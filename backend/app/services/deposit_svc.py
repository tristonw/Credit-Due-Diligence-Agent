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


def _mock_labeled_deposits(pos_texts: list[str], neg_texts: list[str]) -> dict:
    """Produce a believable supervised distillation in keyless mode.

    The structure mirrors what an interviewer's playbook would contain:
    skills the employee now has, *pass criteria* as WorkStandards, *fail signals*
    as DataQualityRules, plus an evaluation SOP.
    """
    return {
        "skills": [
            {
                "name": "面试判定",
                "description": f"基于 {len(pos_texts)} 份通过 / {len(neg_texts)} 份不通过样本，"
                "判断候选人是否符合录用标准",
                "category": "judgment",
                "proficiency": 3,
            }
        ],
        "standards": [
            {
                "name": "通过标准：技术深度",
                "metrics": [{"name": "能讲出系统设计权衡", "target": "至少 2 个具体例子"}],
                "rubric": {"pass": "候选人能落地到代码/架构细节，并解释取舍"},
            },
            {
                "name": "通过标准：沟通表达",
                "metrics": [{"name": "回答结构化（STAR/分点）", "target": "全程保持"}],
                "rubric": {"pass": "答案有主线、有量化结果"},
            },
        ],
        "sops": [
            {
                "title": "面试评估流程",
                "steps": [
                    "通读面试记录，定位关键问答",
                    "对照通过标准逐条打勾",
                    "扫描拒绝信号",
                    "综合给出 通过/不通过 结论，并附理由与高亮证据",
                ],
            }
        ],
        "rules": [
            {"name": "拒绝信号：回避具体细节", "rule_expr": "candidate avoids concrete examples", "severity": "high"},
            {"name": "拒绝信号：无法量化成果", "rule_expr": "no measurable outcome mentioned", "severity": "medium"},
            {"name": "拒绝信号：与岗位不匹配", "rule_expr": "skill set diverges from role", "severity": "high"},
        ],
    }


def deposit_from_labeled(
    db: Session,
    employee_id: int,
    pos: list[models.TrainingCorpus],
    neg: list[models.TrainingCorpus],
) -> dict:
    pos_texts = [c.raw_text for c in pos]
    neg_texts = [c.raw_text for c in neg]
    prompt = (
        "You are distilling an interviewer's judgment from labeled transcripts. "
        f"PASS examples ({len(pos)}):\n"
        + "\n---\n".join(t[:1500] for t in pos_texts)
        + f"\n\nFAIL examples ({len(neg)}):\n"
        + "\n---\n".join(t[:1500] for t in neg_texts)
        + "\n\nReturn JSON with keys: "
        "skills[{name,description,category,proficiency(1-5)}], "
        "standards[{name,metrics[{name,target}],rubric}] (= what passing candidates demonstrate), "
        "sops[{title,steps[]}], "
        "rules[{name,rule_expr,severity}] (= rejection signals seen in failing transcripts). "
        "Use the transcripts' language."
    )
    data = llm.complete_json(prompt, _mock_labeled_deposits(pos_texts, neg_texts))

    created = {"skills": 0, "standards": 0, "sops": 0, "rules": 0}

    for s in data.get("skills", []):
        db.add(
            models.Skill(
                employee_id=employee_id,
                name=s.get("name", "技能"),
                description=s.get("description", ""),
                category=s.get("category", "judgment"),
                proficiency=int(s.get("proficiency", 3)),
                source="deposited",
                version=_next_version(db, models.Skill, employee_id),
            )
        )
        created["skills"] += 1
    for st in data.get("standards", []):
        db.add(
            models.WorkStandard(
                employee_id=employee_id,
                name=st.get("name", "通过标准"),
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
                title=sop.get("title", "面试评估SOP"),
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
                name=r.get("name", "拒绝信号"),
                rule_expr=r.get("rule_expr", ""),
                severity=r.get("severity", "medium"),
                source="deposited",
                version=_next_version(db, models.DataQualityRule, employee_id),
            )
        )
        created["rules"] += 1

    db.commit()
    return created


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
