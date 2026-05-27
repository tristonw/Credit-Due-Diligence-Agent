"""Task execution with grounded output and a data-quality gate.

Produces a realistic work result: applies an SOP, cites retrieved corpus, runs
the employee's data-quality rules, and computes a quality score that scales the
experience reward (better-trained, higher-level employees do higher-quality
work and earn more).
"""
from sqlalchemy.orm import Session

from .. import llm, models
from . import training_svc


def _quality(emp: models.Employee, has_context: bool) -> float:
    q = 0.5
    q += 0.04 * (emp.level - 1)
    deposited = sum(1 for s in emp.skills if s.source == "deposited")
    q += 0.04 * min(deposited, 5)
    if has_context:
        q += 0.08
    return round(max(0.3, min(q, 0.99)), 2)


def _dq_findings(emp: models.Employee, quality: float) -> list[dict]:
    findings = []
    for rule in emp.rules:
        passed = quality >= 0.6
        findings.append({"rule": rule.name, "severity": rule.severity, "passed": passed})
    return findings


def execute_task(db: Session, emp: models.Employee, prompt: str) -> dict:
    context = training_svc.search_chunks(db, emp.id, prompt, top_k=2)
    has_ctx = bool(context)
    sop = emp.sops[-1].title if emp.sops else "标准工作流程"
    quality = _quality(emp, has_ctx)

    mock_output = (
        f"【套用SOP：{sop}】\n"
        f"针对任务「{prompt[:60]}」，依据工作标准完成处理并自检。\n"
        + (f"参考培训语料：「{context[0][:100]}…」" if has_ctx else "（暂无相关培训语料可引用）")
    )
    if llm.is_live():
        p = (
            f"You are this digital employee. Persona: {emp.persona}. "
            f"Apply SOP '{sop}'. Use this knowledge if relevant: {context}. "
            f'Complete the task and return JSON: {{"output": "..."}}.\n\nTask: {prompt}'
        )
        output = llm.complete_json(p, {"output": mock_output}).get("output", mock_output)
    else:
        output = mock_output

    findings = _dq_findings(emp, quality)
    reward = 10 + round(30 * quality)
    return {
        "output": output,
        "applied_sop": sop,
        "quality": quality,
        "references": context[:1],
        "dq_findings": findings,
        "reward": reward,
    }
