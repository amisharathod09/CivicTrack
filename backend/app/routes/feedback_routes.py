
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback, User
from app.schemas.feedback_schema import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse
)
from app.services.feedback_service import (
    submit_feedback,
    update_feedback
)
from app.utils.auth_dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


# Get all feedback records (Admin only)
@router.get("")
def get_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    statement = select(Feedback).order_by(
        Feedback.created_at.desc()
    )

    feedback_records = db.scalars(statement).all()

    return [
        {
            "feedback_id": feedback.feedback_id,
            "request_id": feedback.request_id,
            "citizen_id": feedback.citizen_id,
            "rating": feedback.rating,
            "comments": feedback.comments,
            "created_at": feedback.created_at,
            "updated_at": feedback.updated_at
        }
        for feedback in feedback_records
    ]


# Get feedback submitted by the logged-in citizen
@router.get("/my-feedback")
def get_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    feedback_records = db.scalars(
        select(Feedback).where(
            Feedback.citizen_id == current_user.user_id
        ).order_by(Feedback.created_at.desc())
    ).all()

    return [
        {
            "feedback_id": feedback.feedback_id,
            "request_id": feedback.request_id,
            "citizen_id": feedback.citizen_id,
            "rating": feedback.rating,
            "comments": feedback.comments,
            "created_at": feedback.created_at,
            "updated_at": feedback.updated_at
        }
        for feedback in feedback_records
    ]


# Submit feedback (Citizen only)
@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED
)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    feedback, error = submit_feedback(
        feedback_data,
        current_user,
        db
    )

    if error:
        if error == "Complaint not found.":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        if "already" in error.lower():
            raise HTTPException(
                status_code=409,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return feedback


# Edit existing feedback (Citizen only)
@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse
)
def edit_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("citizen"))
):

    feedback, error = update_feedback(
        feedback_id,
        feedback_data,
        current_user,
        db
    )

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return feedback
