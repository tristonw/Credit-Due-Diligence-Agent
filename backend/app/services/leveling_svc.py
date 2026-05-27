"""Experience & leveling logic (features 5 and 7).

- Completing tasks and good/bad human labels move experience.
- The curve gets steeper at higher levels.
- Promotions at/above the expert threshold require human expert approval.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from ..config import settings


def exp_needed(level: int) -> int:
    """Total cumulative experience required to *reach* `level`."""
    if level <= 1:
        return 0
    total = 0
    for lvl in range(1, level):
        total += int(settings.exp_base * (lvl ** settings.exp_exponent))
    return total


def _level_for_exp(exp: int) -> int:
    level = 1
    while exp >= exp_needed(level + 1):
        level += 1
    return level


def leveling_state(emp: models.Employee) -> dict:
    cur = emp.level
    cur_floor = exp_needed(cur)
    next_req = exp_needed(cur + 1)
    span = max(next_req - cur_floor, 1)
    progress = max(0.0, min(1.0, (emp.experience - cur_floor) / span))
    return {
        "level": emp.level,
        "experience": emp.experience,
        "exp_for_current": cur_floor,
        "exp_for_next": next_req,
        "progress": round(progress, 4),
        "needs_expert_approval": (cur + 1) >= settings.expert_approval_level,
    }


def add_experience(db: Session, emp: models.Employee, delta: int, reason: str):
    """Apply an experience change, log it, and trigger level-up handling.

    Returns (employee, promotion_request_or_None).
    """
    emp.experience = max(0, emp.experience + delta)
    db.add(
        models.ExperienceLog(
            employee_id=emp.id,
            delta=delta,
            reason=reason,
            balance_after=emp.experience,
        )
    )

    promotion = None
    target = _level_for_exp(emp.experience)
    if target > emp.level:
        next_level = emp.level + 1
        if next_level >= settings.expert_approval_level:
            # High-level promotion: gate behind a pending expert approval.
            existing = (
                db.query(models.PromotionRequest)
                .filter(
                    models.PromotionRequest.employee_id == emp.id,
                    models.PromotionRequest.status == "pending",
                )
                .first()
            )
            if not existing:
                promotion = models.PromotionRequest(
                    employee_id=emp.id,
                    from_level=emp.level,
                    to_level=next_level,
                )
                db.add(promotion)
        else:
            # Auto-promote one level (re-evaluated on the next exp change).
            emp.level = next_level

    db.commit()
    db.refresh(emp)
    return emp, promotion


def decide_promotion(
    db: Session, promo: models.PromotionRequest, approve: bool, expert: str, comment: str
):
    promo.status = "approved" if approve else "rejected"
    promo.expert = expert
    promo.comment = comment
    promo.decided_at = datetime.utcnow()
    if approve:
        emp = db.get(models.Employee, promo.employee_id)
        emp.level = promo.to_level
        db.add(
            models.ExperienceLog(
                employee_id=emp.id,
                delta=0,
                reason=f"Expert-approved promotion to L{promo.to_level}",
                balance_after=emp.experience,
            )
        )
    db.commit()
    db.refresh(promo)
    return promo
