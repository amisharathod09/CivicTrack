from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Department


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.get("")
def get_departments(db: Session = Depends(get_db)):

    departments = db.scalars(
        select(Department)
    ).all()

    return [
        {
            "department_id": department.department_id,
            "department_name": department.department_name,
            "description": department.description,
            "is_active": department.is_active
        }
        for department in departments
    ]