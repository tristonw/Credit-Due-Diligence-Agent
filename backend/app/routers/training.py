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
    if req.label not in (None, "pass", "fail"):
        raise HTTPException(400, "label must be pass, fail, or null")
    if req.split not in ("train", "test"):
        raise HTTPException(400, "split must be train or test")
    corpus = training_svc.add_corpus(
        db, employee_id, req.title, req.text, req.label, req.feedback, req.split
    )
    return {
        "corpus_id": corpus.id,
        "title": corpus.title,
        "label": corpus.label,
        "split": corpus.split,
    }


@router.get("/{employee_id}/corpus", response_model=list[schemas.CorpusOut])
def list_corpus(employee_id: int, db: Session = Depends(get_db)):
    _get_emp(db, employee_id)
    return (
        db.query(models.TrainingCorpus)
        .filter(models.TrainingCorpus.employee_id == employee_id)
        .order_by(models.TrainingCorpus.created_at.desc())
        .all()
    )


@router.patch("/{employee_id}/corpus/{corpus_id}", response_model=schemas.CorpusOut)
def update_corpus(employee_id: int, corpus_id: int, req: schemas.CorpusUpdate, db: Session = Depends(get_db)):
    c = db.get(models.TrainingCorpus, corpus_id)
    if not c or c.employee_id != employee_id:
        raise HTTPException(404, "corpus not found")
    if req.label is not None:
        if req.label not in ("pass", "fail", ""):
            raise HTTPException(400, "label must be pass, fail, or empty")
        c.label = req.label or None
    if req.feedback is not None:
        c.feedback = req.feedback
    if req.split is not None:
        if req.split not in ("train", "test"):
            raise HTTPException(400, "split must be train or test")
        c.split = req.split
    db.commit()
    db.refresh(c)
    return c


@router.post("/{employee_id}/train")
def train(employee_id: int, db: Session = Depends(get_db)):
    _get_emp(db, employee_id)
    try:
        return training_svc.train(db, employee_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
