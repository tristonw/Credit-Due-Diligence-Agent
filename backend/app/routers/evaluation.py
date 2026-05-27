from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import evaluation_svc

router = APIRouter(prefix="/api/employees", tags=["evaluation"])


@router.post("/{employee_id}/evaluate", response_model=schemas.EvaluationOut)
def evaluate(employee_id: int, req: schemas.EvaluateRequest, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    if req.phase not in ("baseline", "post_training"):
        raise HTTPException(400, "phase must be baseline or post_training")
    return evaluation_svc.evaluate(db, emp, req.phase, req.training_run_id)


@router.get("/{employee_id}/evaluations", response_model=list[schemas.EvaluationOut])
def list_evaluations(employee_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Evaluation)
        .filter(models.Evaluation.employee_id == employee_id)
        .order_by(models.Evaluation.created_at.desc())
        .all()
    )


@router.get("/{employee_id}/evaluations/compare", response_model=schemas.EvaluationCompareOut)
def compare(employee_id: int, db: Session = Depends(get_db)):
    return evaluation_svc.compare(db, employee_id)
