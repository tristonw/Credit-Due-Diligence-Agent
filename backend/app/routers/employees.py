from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import generation

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=schemas.EmployeeDetailOut)
def create_employee(req: schemas.CreateEmployeeRequest, db: Session = Depends(get_db)):
    if not req.description.strip():
        raise HTTPException(400, "description is required")
    emp = generation.generate_employee(db, req.description, req.name)
    return emp


@router.get("", response_model=list[schemas.EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).order_by(models.Employee.created_at.desc()).all()


@router.get("/{employee_id}", response_model=schemas.EmployeeDetailOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "employee not found")
    return emp
