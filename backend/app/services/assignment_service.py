
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Assignment,
    Category,
    ServiceRequest,
    StatusHistory,
    User
)


def assign_complaint(
    request_id: int,
    staff_id: int,
    assigned_by: User,
    notes: str | None,
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

    # 2. Check whether the complaint can be assigned
    if complaint.status not in ["Submitted", "Assigned"]:
        return None, "Only Submitted or Assigned complaints can be assigned."

    # 3. Find the selected staff member
    staff = db.scalar(
        select(User).where(
            User.user_id == staff_id
        )
    )

    if staff is None or not staff.is_active:
        return None, "Staff member not found or inactive."

    # 4. Verify the selected user is staff
    if staff.role != "staff":
        return None, "Selected user is not a staff member."

    # 5. Find the complaint category
    category = db.scalar(
        select(Category).where(
            Category.category_id == complaint.category_id
        )
    )

    if category is None:
        return None, "Complaint category not found."

    # 6. Verify department matching
    if staff.department_id != category.department_id:
        return None, "Staff member does not belong to the complaint department."

    try:
        # 7. Find the previous current assignment
        previous_assignment = db.scalar(
            select(Assignment)
            .where(
                Assignment.request_id == request_id,
                Assignment.is_current.is_(True)
            )
            .with_for_update()
        )

        # 8. Preserve the previous assignment as history
        if previous_assignment is not None:
            previous_assignment.is_current = False

        # 9. Create the new assignment
        new_assignment = Assignment(
            request_id=request_id,
            staff_id=staff_id,
            assigned_by=assigned_by.user_id,
            notes=notes,
            is_current=True
        )

        db.add(new_assignment)

        # 10. Update complaint status when first assigned
        if complaint.status == "Submitted":
            old_status = complaint.status
            complaint.status = "Assigned"

            history_record = StatusHistory(
                request_id=request_id,
                old_status=old_status,
                new_status="Assigned",
                changed_by=assigned_by.user_id,
                change_note="Complaint assigned to department staff."
            )

            db.add(history_record)

        # 11. Save all changes together
        db.commit()
        db.refresh(new_assignment)

        return new_assignment, None

    except Exception:
        db.rollback()
        raise
