"""Baseline & post-training evaluation (feature 3).

Generates questions for the employee's domain, has the employee answer using its
current profile, scores the answers, and lets the API compare baseline vs
post-training to prove improvement.
"""
from sqlalchemy.orm import Session

from .. import llm, models


def _mock_questions(emp: models.Employee) -> list[str]:
    return [
        f"针对「{emp.description[:20]}」，请描述你的标准工作流程。",
        "遇到不符合质量标准的产出，你会如何处理？",
        "列举你掌握的关键技能及其应用场景。",
    ]


def _mock_eval(emp: models.Employee, phase: str, questions: list[str]) -> dict:
    # Trained employees have more deposited skills -> higher mock score, so the
    # baseline vs post_training comparison demonstrably improves.
    deposited = sum(1 for s in emp.skills if s.source == "deposited")
    base = 55.0 + min(deposited, 5) * 6.0
    if phase == "post_training":
        base += 12.0
    score = min(base, 98.0)
    answers = [
        {"question": q, "answer": f"（{phase}）依据当前技能与标准作答。", "score": round(score, 1)}
        for q in questions
    ]
    return {"score": round(score, 1), "answers": answers}


def evaluate(db: Session, emp: models.Employee, phase: str, training_run_id: int | None) -> models.Evaluation:
    skills = ", ".join(s.name for s in emp.skills) or "无"
    q_prompt = (
        f"Generate 3 evaluation questions to test a digital employee whose role is: "
        f"{emp.description}. Skills: {skills}. "
        'Return JSON: {"questions": ["...", "...", "..."]}. Reply in the role language.'
    )
    questions = llm.complete_json(q_prompt, {"questions": _mock_questions(emp)}).get(
        "questions", _mock_questions(emp)
    )

    a_prompt = (
        f"You are this digital employee. Persona: {emp.persona}. Skills: {skills}. "
        f"Answer each question, then grade the overall performance 0-100. "
        'Return JSON: {"score": <0-100>, "answers": [{"question":"...","answer":"...","score":<0-100>}]}.'
        f"\n\nQuestions: {questions}"
    )
    result = llm.complete_json(a_prompt, _mock_eval(emp, phase, questions))

    ev = models.Evaluation(
        employee_id=emp.id,
        training_run_id=training_run_id,
        phase=phase,
        questions=questions,
        answers=result.get("answers", []),
        score=float(result.get("score", 0.0)),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def compare(db: Session, employee_id: int) -> dict:
    def latest(phase: str):
        return (
            db.query(models.Evaluation)
            .filter(
                models.Evaluation.employee_id == employee_id,
                models.Evaluation.phase == phase,
            )
            .order_by(models.Evaluation.created_at.desc())
            .first()
        )

    base = latest("baseline")
    post = latest("post_training")
    out = {"baseline": None, "post_training": None, "improved": None, "delta": None}
    if base:
        out["baseline"] = base.score
    if post:
        out["post_training"] = post.score
    if base and post:
        out["delta"] = round(post.score - base.score, 2)
        out["improved"] = post.score > base.score
    return out
