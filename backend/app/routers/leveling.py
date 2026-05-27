from fastapi import APIRouter, Depends, HTTPException
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
