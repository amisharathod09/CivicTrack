
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Assignment,
    Category,
    ServiceRequest,
    StatusHistory,
    User
)
from app.schemas.complaint_schema import (
    ComplaintCreate,
    ComplaintResponse,
    StaffStatusUpdate
)
from app.services.complaint_service import (
    create_complaint,
    cancel_complaint,
    update_staff_complaint_status
)
from app.utils.auth_dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests"]
)


# Get all complaints with optional filters (Admin only)
@router.get("")
def get_service_requests(
    complaint_status: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    category_id: int | None = Query(default=None, gt=0),
    department_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    query = (
        select(ServiceRequest)
        .join(
            Category,
            ServiceRequest.category_id == Category.category_id
        )
    )

    # Filter by complaint status
    if complaint_status:
        query = query.where(
            ServiceRequest.status == complaint_status
        )

    # Filter by priority
    if priority:
        query = query.where(
            ServiceRequest.priority == priority
        )

    # Filter by category
    if category_id is not None:
        query = query.where(
            ServiceRequest.category_id == category_id
        )

    # Filter by department
    if department_id is not None:
        query = query.where(
            Category.department_id == department_id
        )

    # Search by complaint title
    if search:
        query = query.where(
            ServiceRequest.title.ilike(f"%{search.strip()}%")
        )

    query = query.order_by(
        ServiceRequest.created_at.desc()
    )

    service_requests = db.scalars(query).all()

    return [
        {
            "request_id": request.request_id,
            "citizen_id": request.citizen_id,
            "category_id": request.category_id,
            "location_id": request.location_id,
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "status": request.status,
            "sla_due_at": request.sla_due_at,
            "created_at": request.created_at,
            "updated_at": request.updated_at,
            "resolved_at": request.resolved_at
        }
        for request in service_requests
    ]


# Submit a new complaint (Citizen only)
@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    new_complaint, error_message = create_complaint(
        complaint_data,
        current_user,
        db
    )

    if error_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )

    return new_complaint


# Get complaints belonging to the logged-in citizen
@router.get("/my-complaints")
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    my_complaints = db.scalars(
        select(ServiceRequest)
        .where(ServiceRequest.citizen_id == current_user.user_id)
        .order_by(ServiceRequest.created_at.desc())
    ).all()

    return [
        {
            "request_id": request.request_id,
            "category_id": request.category_id,
            "location_id": request.location_id,
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "status": request.status,
            "sla_due_at": request.sla_due_at,
            "created_at": request.created_at,
            "updated_at": request.updated_at,
            "resolved_at": request.resolved_at
        }
        for request in my_complaints
    ]


# Get complaint details and status history
@router.get("/{request_id}")
def get_complaint_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == request_id
        )
    )

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found."
        )

    # Citizens can access only their own complaints
    if (
        current_user.role == "citizen"
        and complaint.citizen_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found."
        )

   # Staff can access only their currently assigned complaints
    if current_user.role == "staff":

       current_assignment = db.scalar(
        select(Assignment).where(
            Assignment.request_id == request_id,
            Assignment.staff_id == current_user.user_id,
            Assignment.is_current.is_(True)
        )
    )

    if current_assignment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this complaint."
        )

    history_records = db.scalars(
        select(StatusHistory)
        .where(StatusHistory.request_id == request_id)
        .order_by(
            StatusHistory.changed_at.asc(),
            StatusHistory.history_id.asc()
        )
    ).all()

    return {
        "complaint": {
            "request_id": complaint.request_id,
            "citizen_id": complaint.citizen_id,
            "category_id": complaint.category_id,
            "location_id": complaint.location_id,
            "title": complaint.title,
            "description": complaint.description,
            "priority": complaint.priority,
            "status": complaint.status,
            "sla_due_at": complaint.sla_due_at,
            "created_at": complaint.created_at,
            "updated_at": complaint.updated_at,
            "resolved_at": complaint.resolved_at
        },
        "status_history": [
            {
                "history_id": history.history_id,
                "old_status": history.old_status,
                "new_status": history.new_status,
                "changed_by": history.changed_by,
                "change_note": history.change_note,
                "changed_at": history.changed_at
            }
            for history in history_records
        ]
    }


# Cancel a complaint (Citizen only)
@router.patch("/{request_id}/cancel")
def cancel_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    cancelled_complaint, error_message = cancel_complaint(
        request_id,
        current_user,
        db
    )

    if error_message:

        if error_message == "Complaint not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    return {
        "message": "Complaint cancelled successfully.",
        "request_id": cancelled_complaint.request_id,
        "status": cancelled_complaint.status
    }


# Staff updates the status of their assigned complaint
@router.patch("/{request_id}/status")
def update_complaint_status(
    request_id: int,
    status_data: StaffStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("staff"))
):

    updated_complaint, error_message = update_staff_complaint_status(
        request_id,
        status_data,
        current_user,
        db
    )

    if error_message:
        if error_message == "Complaint not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        if error_message == "You are not assigned to this complaint.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    return {
        "message": "Complaint status updated successfully.",
        "request_id": updated_complaint.request_id,
        "new_status": updated_complaint.status,
        "resolved_at": updated_complaint.resolved_at
    }