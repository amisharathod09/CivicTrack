from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


@router.get("")
def get_feedback(db: Session = Depends(get_db)):

    statement = select(Feedback)

    feedback_records = db.execute(statement).scalars().all()

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