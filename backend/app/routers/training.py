from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import training_svc

router = APIRouter(prefix="/api/employees", tags=["training"])


def _get_emp(db: Session, employee_id: int) -> models.Employee:
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    return emp


@router.post("/{employee_id}/corpus")
def upload_corpus(employee_id: int, req: schemas.CorpusRequest, db: Session = Depends(get_db)):
    _get_emp(db, employee_id)
    if not req.text.strip():
        raise HTTPException(400, "text is required")
    corpus = training_svc.add_corpus(db, employee_id, req.title, req.text)
    return {"corpus_id": corpus.id, "title": corpus.title}


@router.post("/{employee_id}/train")
def train(employee_id: int, db: Session = Depends(get_db)):
    _get_emp(db, employee_id)
    try:
        return training_svc.train(db, employee_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
