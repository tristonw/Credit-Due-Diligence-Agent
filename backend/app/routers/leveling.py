from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import leveling_svc

router = APIRouter(prefix="/api", tags=["leveling"])


@router.get("/employees/{employee_id}/leveling", response_model=schemas.LevelingOut)
def get_leveling(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    return leveling_svc.leveling_state(emp)


@router.get("/employees/{employee_id}/experience-log", response_model=list[schemas.ExperienceLogOut])
def experience_log(employee_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.ExperienceLog)
        .filter(models.ExperienceLog.employee_id == employee_id)
        .order_by(models.ExperienceLog.created_at.asc(), models.ExperienceLog.id.asc())
        .all()
    )


@router.get("/leveling-curve", response_model=list[schemas.CurvePoint])
def leveling_curve(max_level: int = 10):
    points = []
    for lvl in range(1, max_level + 1):
        cumulative = leveling_svc.exp_needed(lvl)
        step = leveling_svc.exp_needed(lvl + 1) - cumulative
        points.append({"level": lvl, "cumulative_exp": cumulative, "step_exp": step})
    return points


@router.get("/stats", response_model=schemas.StatsOut)
def stats(db: Session = Depends(get_db)):
    emp_count = db.query(func.count(models.Employee.id)).scalar() or 0
    avg_level = db.query(func.avg(models.Employee.level)).scalar() or 0
    total_exp = db.query(func.sum(models.Employee.experience)).scalar() or 0
    tasks = db.query(func.count(models.WorkTask.id)).scalar() or 0
    good = db.query(func.count(models.TaskLabel.id)).filter(models.TaskLabel.rating == "good").scalar() or 0
    bad = db.query(func.count(models.TaskLabel.id)).filter(models.TaskLabel.rating == "bad").scalar() or 0
    deposits = sum(
        db.query(func.count(m.id)).filter(m.source == "deposited").scalar() or 0
        for m in (models.Skill, models.WorkStandard, models.SOP, models.DataQualityRule)
    )
    pending = db.query(func.count(models.PromotionRequest.id)).filter(
        models.PromotionRequest.status == "pending"
    ).scalar() or 0
    return {
        "employees": emp_count,
        "avg_level": round(float(avg_level), 2),
        "total_experience": int(total_exp),
        "tasks": tasks,
        "labels_good": good,
        "labels_bad": bad,
        "deposits": deposits,
        "pending_promotions": pending,
    }


@router.get("/promotions", response_model=list[schemas.PromotionOut])
def list_promotions(status: str = "pending", db: Session = Depends(get_db)):
    return (
        db.query(models.PromotionRequest)
        .filter(models.PromotionRequest.status == status)
        .order_by(models.PromotionRequest.created_at.desc())
        .all()
    )


@router.post("/promotions/{promotion_id}/decide", response_model=schemas.PromotionOut)
def decide_promotion(promotion_id: int, req: schemas.PromotionDecision, db: Session = Depends(get_db)):
    promo = db.get(models.PromotionRequest, promotion_id)
    if not promo:
        raise HTTPException(404, "promotion request not found")
    if promo.status != "pending":
        raise HTTPException(400, "promotion already decided")
    return leveling_svc.decide_promotion(db, promo, req.approve, req.expert, req.comment)
