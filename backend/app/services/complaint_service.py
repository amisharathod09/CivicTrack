from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.location import Location
from app.models.service_request import ServiceRequest
from app.models.status_history import StatusHistory
from app.models.user import User
from app.schemas.complaint_schema import (
    ComplaintCreate,
    StaffStatusUpdate
)
from datetime import datetime

from app.models.assignment import Assignment

def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: User,
    db: Session
):
    # 1. Check whether the category exists and is active
    category = db.scalar(
        select(Category).where(
            Category.category_id == complaint_data.category_id,
            Category.is_active.is_(True)
        )
    )

    if category is None:
        return None, "Invalid or inactive complaint category."

    # 2. Check whether the location exists
    location = db.scalar(
        select(Location).where(
            Location.location_id == complaint_data.location_id
        )
    )

    if location is None:
        return None, "Invalid complaint location."

    try:
        # 3. Create the complaint
        new_complaint = ServiceRequest(
            citizen_id=current_user.user_id,
            category_id=complaint_data.category_id,
            location_id=complaint_data.location_id,
            title=complaint_data.title,
            description=complaint_data.description,
            priority=category.default_priority,
            status="Submitted"
        )

        db.add(new_complaint)

        # Generate request_id before creating status history
        db.flush()

        # 4. Create initial status history
        initial_history = StatusHistory(
            request_id=new_complaint.request_id,
            old_status=None,
            new_status="Submitted",
            changed_by=current_user.user_id,
            change_note="Complaint submitted by citizen."
        )

        db.add(initial_history)

        # 5. Save both records together
        db.commit()

        db.refresh(new_complaint)

        return new_complaint, None

    except Exception:
        db.rollback()
        raise


# Cancel a complaint submitted by the logged-in citizen
def cancel_complaint(
    request_id: int,
    current_user: User,
    db: Session
):
    # 1. Find the complaint
    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == request_id
        )
    )

    if complaint is None:
        return None, "Complaint not found."

    # 2. Verify complaint ownership
    if complaint.citizen_id != current_user.user_id:
        return None, "Complaint not found."

    # 3. Allow cancellation only before In Progress
    if complaint.status not in ["Submitted", "Assigned"]:
        return None, "This complaint cannot be cancelled at its current status."

    try:
        old_status = complaint.status

        # 4. Update complaint status
        complaint.status = "Cancelled"

        # Mark any current assignment as historical
        current_assignment = db.scalar(
            select(Assignment).where(
                Assignment.request_id == request_id,
                Assignment.is_current.is_(True)
            )
        )
        if current_assignment is not None:
            current_assignment.is_current = False

        # 5. Create status history record
        cancellation_history = StatusHistory(
            request_id=complaint.request_id,
            old_status=old_status,
            new_status="Cancelled",
            changed_by=current_user.user_id,
            change_note="Complaint cancelled by citizen."
        )

        db.add(cancellation_history)

        # 6. Save both changes together
        db.commit()

        db.refresh(complaint)

        return complaint, None

    except Exception:
        db.rollback()
        raise

# Update complaint status by the currently assigned staff member
def update_staff_complaint_status(
    request_id: int,
    status_data: StaffStatusUpdate,
    current_user: User,
    db: Session
):
    # 1. Find the complaint
    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == request_id
        )
    )

    if complaint is None:
        return None, "Complaint not found."

    # 2. Verify that this complaint is currently assigned to this staff member
    current_assignment = db.scalar(
        select(Assignment).where(
            Assignment.request_id == request_id,
            Assignment.staff_id == current_user.user_id,
            Assignment.is_current.is_(True)
        )
    )

    if current_assignment is None:
        return None, "You are not assigned to this complaint."

    # 3. Validate the status transition
    allowed_transitions = {
        "Assigned": "In Progress",
        "In Progress": "Resolved"
    }

    expected_status = allowed_transitions.get(complaint.status)

    if expected_status != status_data.status:
        return None, (
            f"Invalid status transition. "
            f"Current status is {complaint.status}."
        )

    try:
        old_status = complaint.status

        # 4. Update complaint status
        complaint.status = status_data.status

        # 5. Record resolution time and close current assignment
        if status_data.status == "Resolved":
            complaint.resolved_at = datetime.now()
            current_assignment.is_current = False

        # 6. Create status history
        history_record = StatusHistory(
            request_id=complaint.request_id,
            old_status=old_status,
            new_status=status_data.status,
            changed_by=current_user.user_id,
            change_note=status_data.change_note
        )

        db.add(history_record)

        # 7. Save both changes together
        db.commit()

        db.refresh(complaint)

        return complaint, None

    except Exception:
        db.rollback()
        raise
