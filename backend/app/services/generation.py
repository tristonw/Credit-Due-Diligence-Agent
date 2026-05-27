"""Digital employee generation from a natural-language brief (feature 1)."""
from sqlalchemy.orm import Session

from .. import llm, models


def _mock_profile(description: str, name: str) -> dict:
    return {
        "name": name or "数字员工",
        "persona": f"一名专注于「{description[:30]}」领域的数字员工，严谨、可培养。",
        "avatar": {"style": "professional", "color": "#4f46e5", "emoji": "🧑‍💼", "image_url": ""},
        "outline": {
            "responsibilities": ["理解并执行相关领域的工作任务", "持续学习语料并沉淀标准"],
            "goals": ["保证产出质量达到工作标准基线", "通过培训不断提升能力"],
            "scope": description,
        },
        "skills": [
            {"name": "领域分析", "description": "对相关领域信息进行分析", "category": "analysis", "proficiency": 2},
            {"name": "报告撰写", "description": "产出结构化工作成果", "category": "output", "proficiency": 1},
        ],
        "standards": [
            {
                "name": "基础质量标准",
                "metrics": [{"name": "准确性", "target": ">=80%"}, {"name": "完整性", "target": ">=80%"}],
                "rubric": {"pass": "覆盖关键要点且无重大错误"},
            }
        ],
        "sops": [
            {
                "title": "标准工作流程",
                "steps": ["收集输入", "依据标准处理", "自检质量", "产出结果"],
            }
        ],
    }


def generate_employee(db: Session, description: str, name: str | None) -> models.Employee:
    prompt = (
        "Create a digital employee from this natural-language brief. "
        "Return JSON with keys: name, persona, avatar{style,color,emoji,image_url}, "
        "outline{responsibilities[],goals[],scope}, "
        "skills[{name,description,category,proficiency(1-5)}], "
        "standards[{name,metrics[{name,target}],rubric}], "
        "sops[{title,steps[]}]. Reply in the brief's language.\n\n"
        f"Brief: {description}"
    )
    data = llm.complete_json(prompt, _mock_profile(description, name or ""))

    emp = models.Employee(
        name=data.get("name") or name or "数字员工",
        persona=data.get("persona", ""),
        description=description,
        avatar=data.get("avatar", {}),
        level=1,
        experience=0,
    )
    db.add(emp)
    db.flush()

    db.add(models.WorkOutline(employee_id=emp.id, content=data.get("outline", {})))
    for s in data.get("skills", []):
        db.add(
            models.Skill(
                employee_id=emp.id,
                name=s.get("name", "技能"),
                description=s.get("description", ""),
                category=s.get("category", "general"),
                proficiency=int(s.get("proficiency", 1)),
                source="generated",
            )
        )
    for st in data.get("standards", []):
        db.add(
            models.WorkStandard(
                employee_id=emp.id,
                name=st.get("name", "标准"),
                metrics=st.get("metrics", []),
                rubric=st.get("rubric", {}),
                source="generated",
            )
        )
    for sop in data.get("sops", []):
        db.add(
            models.SOP(
                employee_id=emp.id,
                title=sop.get("title", "SOP"),
                steps=sop.get("steps", []),
                source="generated",
            )
        )
    db.commit()
    db.refresh(emp)
    return emp
