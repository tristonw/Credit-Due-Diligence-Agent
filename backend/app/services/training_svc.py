"""Text-corpus training (feature 2).

Supports two modes:
- Plain text: summarises the corpus and produces generic deposits.
- Labeled (pass/fail) text: trains only on the `train` split, then distils
  *pass criteria* and *fail signals* separately so the employee can later judge
  new transcripts against ground truth (the "distill Triston" workflow).
"""
import re

from sqlalchemy.orm import Session

from .. import llm, models
from . import deposit_svc


def _chunk(text: str, size: int = 800) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) > size and buf:
            chunks.append(buf.strip())
            buf = p
        else:
            buf = f"{buf}\n{p}" if buf else p
    if buf.strip():
        chunks.append(buf.strip())
    return chunks or [text[:size]]


def add_corpus(
    db: Session,
    employee_id: int,
    title: str,
    text: str,
    label: str | None = None,
    feedback: str = "",
    split: str = "train",
) -> models.TrainingCorpus:
    corpus = models.TrainingCorpus(
        employee_id=employee_id,
        title=title,
        raw_text=text,
        label=label,
        feedback=feedback,
        split=split,
    )
    db.add(corpus)
    db.flush()
    for i, ch in enumerate(_chunk(text)):
        db.add(models.CorpusChunk(corpus_id=corpus.id, text=ch, idx=i))
    db.commit()
    db.refresh(corpus)
    return corpus


def search_chunks(db: Session, employee_id: int, query: str, top_k: int = 3) -> list[str]:
    """Keyword-overlap retrieval over the employee's TRAIN-split corpus chunks
    (test-split kept hidden so it can be used as a held-out set).
    """
    corpus_ids = [
        c.id
        for c in db.query(models.TrainingCorpus)
        .filter(
            models.TrainingCorpus.employee_id == employee_id,
            models.TrainingCorpus.split == "train",
        )
        .all()
    ]
    if not corpus_ids:
        return []
    chunks = (
        db.query(models.CorpusChunk)
        .filter(models.CorpusChunk.corpus_id.in_(corpus_ids))
        .all()
    )
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for ch in chunks:
        words = re.findall(r"\w+", ch.text.lower())
        overlap = sum(1 for w in words if w in terms)
        scored.append((overlap, ch.text))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:top_k]]


def train(db: Session, employee_id: int) -> dict:
    train_corpora = (
        db.query(models.TrainingCorpus)
        .filter(
            models.TrainingCorpus.employee_id == employee_id,
            models.TrainingCorpus.split == "train",
        )
        .all()
    )
    if not train_corpora:
        raise ValueError("No training corpus uploaded for this employee")

    labeled = [c for c in train_corpora if c.label in ("pass", "fail")]
    if labeled:
        # Supervised: distil differential pass/fail criteria.
        pos = [c for c in labeled if c.label == "pass"]
        neg = [c for c in labeled if c.label == "fail"]
        summary = (
            f"已从 {len(pos)} 份通过 / {len(neg)} 份不通过的样本中学习判定模式，"
            "沉淀通过标准与拒绝信号。"
        )
        run = models.TrainingRun(
            employee_id=employee_id,
            corpus_ids=[c.id for c in train_corpora],
            status="completed",
            summary=summary,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        deposits = deposit_svc.deposit_from_labeled(db, employee_id, pos, neg)
        return {
            "training_run_id": run.id,
            "summary": summary,
            "deposits": deposits,
            "mode": "labeled",
            "train_size": len(train_corpora),
            "pass_size": len(pos),
            "fail_size": len(neg),
        }

    # Plain mode: original behavior.
    combined = "\n\n".join(c.raw_text for c in train_corpora)
    prompt = (
        "Summarise what a digital employee should learn from this corpus in 3-5 "
        'bullet points. Return JSON: {"summary": "..."}. Reply in the corpus language.'
        f"\n\nCorpus: {combined[:4000]}"
    )
    summary = llm.complete_json(
        prompt, {"summary": "已从语料中提炼关键知识点，可应用于后续工作并形成沉淀。"}
    ).get("summary", "")

    run = models.TrainingRun(
        employee_id=employee_id,
        corpus_ids=[c.id for c in train_corpora],
        status="completed",
        summary=summary,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    deposits = deposit_svc.deposit_from_training(db, employee_id, summary, combined)
    return {
        "training_run_id": run.id,
        "summary": summary,
        "deposits": deposits,
        "mode": "plain",
        "train_size": len(train_corpora),
    }
