from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/employees", tags=["deposits"])


@router.get("/{employee_id}/deposits")
def list_deposits(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    return {
        "skills": [schemas.SkillOut.model_validate(s).model_dump() for s in emp.skills],
        "standards": [schemas.StandardOut.model_validate(s).model_dump() for s in emp.standards],
        "sops": [schemas.SOPOut.model_validate(s).model_dump() for s in emp.sops],
        "rules": [schemas.RuleOut.model_validate(r).model_dump() for r in emp.rules],
    }
