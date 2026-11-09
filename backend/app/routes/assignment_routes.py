from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assignment, ServiceRequest, User
from app.schemas.assignment_schema import AssignmentCreate
from app.services.assignment_service import assign_complaint
from app.utils.auth_dependencies import require_roles


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


# Only admins can view all assignment records
@router.get("")
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

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


# Staff can view only their own current assignments
@router.get("/my-assignments")
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("staff"))
):

    results = db.execute(
        select(Assignment, ServiceRequest)
        .join(
            ServiceRequest,
            Assignment.request_id == ServiceRequest.request_id
        )
        .where(
            Assignment.staff_id == current_user.user_id,
            Assignment.is_current.is_(True)
        )
        .order_by(Assignment.assigned_at.desc())
    ).all()

    return [
        {
            "assignment_id": assignment.assignment_id,
            "request_id": complaint.request_id,
            "title": complaint.title,
            "description": complaint.description,
            "category_id": complaint.category_id,
            "location_id": complaint.location_id,
            "priority": complaint.priority,
            "status": complaint.status,
            "assigned_at": assignment.assigned_at,
            "assignment_notes": assignment.notes,
            "created_at": complaint.created_at,
            "sla_due_at": complaint.sla_due_at
        }
        for assignment, complaint in results
    ]

# Admin assigns a complaint to a staff member
@router.post("", status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    new_assignment, error_message = assign_complaint(
        request_id=assignment_data.request_id,
        staff_id=assignment_data.staff_id,
        assigned_by=current_user,
        notes=assignment_data.notes,
        db=db
    )

    if error_message:

        if error_message == "Complaint not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        if error_message in [
            "Staff member not found or inactive.",
            "Complaint category not found."
        ]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    return {
        "message": "Complaint assigned successfully.",
        "assignment_id": new_assignment.assignment_id,
        "request_id": new_assignment.request_id,
        "staff_id": new_assignment.staff_id,
        "assigned_by": new_assignment.assigned_by,
        "is_current": new_assignment.is_current
    }