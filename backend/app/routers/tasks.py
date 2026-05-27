from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import leveling_svc, work_svc

router = APIRouter(prefix="/api", tags=["tasks"])

LABEL_GOOD_EXP = 40
LABEL_BAD_EXP = -25


@router.post("/employees/{employee_id}/tasks")
def run_task(employee_id: int, req: schemas.TaskRequest, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")

    result = work_svc.execute_task(db, emp, req.prompt)
    task = models.WorkTask(employee_id=employee_id, prompt=req.prompt, output=result["output"])
    db.add(task)
    db.commit()
    db.refresh(task)

    emp, promo = leveling_svc.add_experience(
        db, emp, result["reward"], f"完成任务 #{task.id}（质量{result['quality']}）"
    )
    return {
        "task_id": task.id,
        "output": result["output"],
        "applied_sop": result["applied_sop"],
        "quality": result["quality"],
        "references": result["references"],
        "dq_findings": result["dq_findings"],
        "exp_gained": result["reward"],
        "experience": emp.experience,
        "level": emp.level,
        "promotion_request_id": promo.id if promo else None,
    }


@router.post("/tasks/{task_id}/label")
def label_task(task_id: int, req: schemas.LabelRequest, db: Session = Depends(get_db)):
    task = db.get(models.WorkTask, task_id)
    if not task:
        raise HTTPException(404, "task not found")
    if req.rating not in ("good", "bad"):
        raise HTTPException(400, "rating must be good or bad")

    delta = LABEL_GOOD_EXP if req.rating == "good" else LABEL_BAD_EXP
    db.add(
        models.TaskLabel(
            task_id=task_id,
            rating=req.rating,
            exp_delta=delta,
            labeler=req.labeler,
            comment=req.comment,
        )
    )
    db.commit()

    emp = db.get(models.Employee, task.employee_id)
    emp, promo = leveling_svc.add_experience(db, emp, delta, f"人工打标 {req.rating} 任务 #{task_id}")
    return {
        "rating": req.rating,
        "exp_delta": delta,
        "experience": emp.experience,
        "level": emp.level,
        "promotion_request_id": promo.id if promo else None,
    }
