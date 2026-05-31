"""Judgment service — Triston reads a transcript and predicts pass/fail.

When the employee has learned from labeled training corpora (deposited pass
standards + fail rules), it can score a new transcript against those criteria
and produce a prediction with reasoning and matched evidence. The same engine
powers held-out evaluation (predict on the test split, score against truth).
"""
import re

from sqlalchemy.orm import Session

from .. import llm, models


def _tokens(text: str) -> set[str]:
    # Mix Latin words and Chinese char bigrams — works for both languages without external deps.
    text = text.lower()
    out = set(re.findall(r"[a-z0-9]+", text))
    cjk = re.findall(r"[一-鿿]+", text)
    for run in cjk:
        for i in range(len(run) - 1):
            out.add(run[i : i + 2])
    return out


def _signal_match(transcript_tokens: set[str], signal_text: str) -> bool:
    sig = _tokens(signal_text)
    if not sig:
        return False
    overlap = len(transcript_tokens & sig)
    return overlap >= max(2, int(len(sig) * 0.25))


def _heuristic_judge(emp: models.Employee, transcript: str) -> dict:
    """Mock-mode prediction: tally deposited pass-standards vs fail-rules against
    the transcript using token overlap. Provides a believable proxy when no LLM
    is available, and stays deterministic for tests.
    """
    tokens = _tokens(transcript)
    pass_std = [s for s in emp.standards if s.source == "deposited"]
    fail_rules = [r for r in emp.rules if r.source == "deposited"]

    pass_hits, fail_hits = [], []
    for s in pass_std:
        # Match against the rubric "pass" text + standard name.
        body = (s.name or "") + " " + str((s.rubric or {}).get("pass", ""))
        if _signal_match(tokens, body):
            pass_hits.append({"type": "pass_criterion", "name": s.name})
    for r in fail_rules:
        if _signal_match(tokens, (r.name or "") + " " + (r.rule_expr or "")):
            fail_hits.append({"type": "fail_signal", "name": r.name, "severity": r.severity})

    # Fallback when nothing matches (no deposited criteria yet, or no overlap):
    # use coarse positive/negative keyword lists so first-time judgments still vary.
    pos_kw = ["成功", "上线", "解决", "提升", "量化", "system design", "ownership", "led"]
    neg_kw = ["不清楚", "回避", "记不得", "没参与", "vague", "i dont know", "unable"]
    if not pass_hits:
        for kw in pos_kw:
            if kw in transcript.lower():
                pass_hits.append({"type": "keyword", "name": kw})
    if not fail_hits:
        for kw in neg_kw:
            if kw in transcript.lower():
                fail_hits.append({"type": "keyword", "name": kw, "severity": "low"})

    p, f = len(pass_hits), len(fail_hits)
    score = (p + 0.5) / (p + f + 1)  # smoothed
    prediction = "pass" if score >= 0.5 else "fail"
    confidence = round(abs(score - 0.5) * 2, 2)  # 0..1
    reasoning = (
        f"命中 {p} 条通过标准、{f} 条拒绝信号 → "
        f"{'倾向通过' if prediction == 'pass' else '倾向不通过'}（信心 {int(confidence * 100)}%）。"
    )
    return {
        "prediction": prediction,
        "confidence": confidence,
        "reasoning": reasoning,
        "matched_criteria": pass_hits + fail_hits,
    }


def judge(
    db: Session,
    emp: models.Employee,
    transcript: str,
    ground_truth: str | None = None,
    corpus_id: int | None = None,
) -> models.Judgment:
    if llm.is_live():
        pass_std = "; ".join(s.name for s in emp.standards if s.source == "deposited") or "无"
        fail_rules = "; ".join(r.name for r in emp.rules if r.source == "deposited") or "无"
        prompt = (
            f"You are {emp.name}, an interviewer. Persona: {emp.persona}. "
            f"Pass criteria you have learned: {pass_std}. "
            f"Fail signals you have learned: {fail_rules}. "
            "Read this transcript and decide PASS or FAIL. Cite specific evidence. "
            'Return JSON: {"prediction":"pass"|"fail","confidence":0-1,"reasoning":"...",'
            '"matched_criteria":[{"type":"pass_criterion"|"fail_signal","name":"..."}]}.'
            f"\n\nTranscript:\n{transcript[:6000]}"
        )
        result = llm.complete_json(prompt, _heuristic_judge(emp, transcript))
        if result.get("prediction") not in ("pass", "fail"):
            result = _heuristic_judge(emp, transcript)
    else:
        result = _heuristic_judge(emp, transcript)

    correct = None
    if ground_truth in ("pass", "fail"):
        correct = 1 if result["prediction"] == ground_truth else 0

    j = models.Judgment(
        employee_id=emp.id,
        corpus_id=corpus_id,
        transcript_preview=transcript[:300],
        prediction=result["prediction"],
        confidence=float(result.get("confidence", 0.5)),
        reasoning=result.get("reasoning", ""),
        matched_criteria=result.get("matched_criteria", []),
        ground_truth=ground_truth,
        correct=correct,
    )
    db.add(j)
    db.commit()
    db.refresh(j)
    return j


def evaluate_on_testset(db: Session, emp: models.Employee) -> dict:
    train_size = (
        db.query(models.TrainingCorpus)
        .filter(
            models.TrainingCorpus.employee_id == emp.id,
            models.TrainingCorpus.split == "train",
        )
        .count()
    )
    test_corpora = (
        db.query(models.TrainingCorpus)
        .filter(
            models.TrainingCorpus.employee_id == emp.id,
            models.TrainingCorpus.split == "test",
            models.TrainingCorpus.label.in_(("pass", "fail")),
        )
        .all()
    )

    judgments: list[models.Judgment] = []
    for c in test_corpora:
        j = judge(db, emp, c.raw_text, ground_truth=c.label, corpus_id=c.id)
        judgments.append(j)

    tp = sum(1 for j in judgments if j.prediction == "pass" and j.ground_truth == "pass")
    fp = sum(1 for j in judgments if j.prediction == "pass" and j.ground_truth == "fail")
    tn = sum(1 for j in judgments if j.prediction == "fail" and j.ground_truth == "fail")
    fn = sum(1 for j in judgments if j.prediction == "fail" and j.ground_truth == "pass")

    total = tp + fp + tn + fn
    accuracy = round((tp + tn) / total, 3) if total else None
    precision_pass = round(tp / (tp + fp), 3) if (tp + fp) else None
    recall_pass = round(tp / (tp + fn), 3) if (tp + fn) else None

    return {
        "train_size": train_size,
        "test_size": len(test_corpora),
        "accuracy": accuracy,
        "precision_pass": precision_pass,
        "recall_pass": recall_pass,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "judgments": judgments,
    }
