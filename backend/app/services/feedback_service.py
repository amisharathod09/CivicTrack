from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Feedback, ServiceRequest, User
from app.schemas.feedback_schema import FeedbackCreate, FeedbackUpdate


# Submit feedback for a completed complaint
def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User,
    db: Session
):
    # 1. Find the complaint
    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == feedback_data.request_id
        )
    )

    if complaint is None:
        return None, "Complaint not found."

    # 2. Verify complaint ownership
    if complaint.citizen_id != current_user.user_id:
        return None, "Complaint not found."

    # 3. Allow feedback only after resolution or closure
    if complaint.status not in ["Resolved", "Closed"]:
        return None, "Feedback can only be submitted for resolved or closed complaints."

    # 4. Check whether feedback already exists
    existing_feedback = db.scalar(
        select(Feedback).where(
            Feedback.request_id == feedback_data.request_id
        )
    )

    if existing_feedback is not None:
        return None, "Feedback has already been submitted for this complaint."

    try:
        # 5. Create feedback
        new_feedback = Feedback(
            request_id=feedback_data.request_id,
            citizen_id=current_user.user_id,
            rating=feedback_data.rating,
            comments=feedback_data.comments
        )

        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)

        return new_feedback, None

    except IntegrityError:
        db.rollback()
        return None, "Feedback already exists for this complaint."

    except Exception:
        db.rollback()
        raise


# Edit existing feedback
def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    current_user: User,
    db: Session
):
    # 1. Find feedback
    feedback = db.scalar(
        select(Feedback).where(
            Feedback.feedback_id == feedback_id
        )
    )

    if feedback is None:
        return None, "Feedback not found."

    # 2. Verify feedback ownership
    if feedback.citizen_id != current_user.user_id:
        return None, "Feedback not found."

    try:
        # 3. Update feedback
        feedback.rating = feedback_data.rating
        feedback.comments = feedback_data.comments

        db.commit()
        db.refresh(feedback)

        return feedback, None

    except Exception:
        db.rollback()
        raise