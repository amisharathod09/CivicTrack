from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assignment


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


@router.get("")
def get_assignments(db: Session = Depends(get_db)):

    assignments = db.scalars(
        select(Assignment)
    ).all()

    return [
        {
            "assignment_id": assignment.assignment_id,
            "request_id": assignment.request_id,
            "staff_id": assignment.staff_id,
            "assigned_by": assignment.assigned_by,
            "assigned_at": assignment.assigned_at,
            "notes": assignment.notes,
            "is_current": assignment.is_current,
            "current_request_id": assignment.current_request_id
        }
        for assignment in assignments
    ]