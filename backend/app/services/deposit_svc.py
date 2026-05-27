"""Hard deposits after training: new/updated SOPs, standards, skills, rules
(feature 4). Each deposit increments the version and is tagged source=deposited.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import llm, models


def _next_version(db: Session, model, employee_id: int) -> int:
    cur = (
        db.query(func.max(model.version))
        .filter(model.employee_id == employee_id)
        .scalar()
    )
    return (cur or 0) + 1


def _mock_deposits(summary: str) -> dict:
    return {
        "skills": [
            {"name": "语料应用", "description": "运用培训语料中的知识解决问题", "category": "trained", "proficiency": 3}
        ],
        "standards": [
            {
                "name": "培训后质量标准",
                "metrics": [{"name": "知识覆盖", "target": ">=85%"}],
                "rubric": {"pass": "正确引用培训语料的关键结论"},
            }
        ],
        "sops": [
            {"title": "培训知识应用流程", "steps": ["检索相关语料", "比对工作标准", "产出并自检"]}
        ],
        "rules": [
            {"name": "关键字段非空", "rule_expr": "required_fields != null", "severity": "high"}
        ],
    }


def deposit_from_training(db: Session, employee_id: int, summary: str, corpus_text: str) -> dict:
    prompt = (
        "A digital employee just finished training on the corpus below. "
        "Produce NEW or UPDATED hard artifacts it learned. Return JSON with keys: "
        "skills[{name,description,category,proficiency(1-5)}], "
        "standards[{name,metrics[{name,target}],rubric}], "
        "sops[{title,steps[]}], rules[{name,rule_expr,severity}]. "
        "Reply in the corpus's language.\n\n"
        f"Training summary: {summary}\n\nCorpus excerpt: {corpus_text[:4000]}"
    )
    data = llm.complete_json(prompt, _mock_deposits(summary))

    created = {"skills": 0, "standards": 0, "sops": 0, "rules": 0}

    for s in data.get("skills", []):
        db.add(
            models.Skill(
                employee_id=employee_id,
                name=s.get("name", "技能"),
                description=s.get("description", ""),
                category=s.get("category", "trained"),
                proficiency=int(s.get("proficiency", 2)),
                source="deposited",
                version=_next_version(db, models.Skill, employee_id),
            )
        )
        created["skills"] += 1
    for st in data.get("standards", []):
        db.add(
            models.WorkStandard(
                employee_id=employee_id,
                name=st.get("name", "标准"),
                metrics=st.get("metrics", []),
                rubric=st.get("rubric", {}),
                source="deposited",
                version=_next_version(db, models.WorkStandard, employee_id),
            )
        )
        created["standards"] += 1
    for sop in data.get("sops", []):
        db.add(
            models.SOP(
                employee_id=employee_id,
                title=sop.get("title", "SOP"),
                steps=sop.get("steps", []),
                source="deposited",
                version=_next_version(db, models.SOP, employee_id),
            )
        )
        created["sops"] += 1
    for r in data.get("rules", []):
        db.add(
            models.DataQualityRule(
                employee_id=employee_id,
                name=r.get("name", "规则"),
                rule_expr=r.get("rule_expr", ""),
                severity=r.get("severity", "medium"),
                source="deposited",
                version=_next_version(db, models.DataQualityRule, employee_id),
            )
        )
        created["rules"] += 1

    db.commit()
    return created
