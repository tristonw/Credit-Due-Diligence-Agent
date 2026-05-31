from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import judgment_svc, leveling_svc

router = APIRouter(prefix="/api/employees", tags=["judgment"])

CORRECT_EXP = 30
WRONG_EXP = -20
NEUTRAL_EXP = 8  # one-off judge with no ground truth


@router.post("/{employee_id}/judge")
def judge(employee_id: int, req: schemas.JudgmentRequest, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    if not req.transcript.strip():
        raise HTTPException(400, "transcript is required")
    if req.ground_truth not in (None, "pass", "fail"):
        raise HTTPException(400, "ground_truth must be pass, fail or null")

    j = judgment_svc.judge(db, emp, req.transcript, req.ground_truth)
    if j.correct == 1:
        delta = CORRECT_EXP
    elif j.correct == 0:
        delta = WRONG_EXP
    else:
        delta = NEUTRAL_EXP
    emp, promo = leveling_svc.add_experience(
        db, emp, delta, f"判定 #{j.id}（{'正确' if j.correct == 1 else '错误' if j.correct == 0 else '无真值'}）"
    )
    return {
        "judgment": schemas.JudgmentOut.model_validate(j).model_dump(),
        "exp_gained": delta,
        "experience": emp.experience,
        "level": emp.level,
        "promotion_request_id": promo.id if promo else None,
    }


@router.post("/{employee_id}/evaluate-judgment", response_model=schemas.AccuracyOut)
def evaluate_judgment(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    return judgment_svc.evaluate_on_testset(db, emp)


@router.get("/{employee_id}/judgments", response_model=list[schemas.JudgmentOut])
def list_judgments(employee_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Judgment)
        .filter(models.Judgment.employee_id == employee_id)
        .order_by(models.Judgment.created_at.desc())
        .limit(50)
        .all()
    )
