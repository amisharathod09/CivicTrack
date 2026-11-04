from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StatusHistory


router = APIRouter(
    prefix="/status-history",
    tags=["Status History"]
)


@router.get("")
def get_status_history(db: Session = Depends(get_db)):

    history_records = db.scalars(
        select(StatusHistory).order_by(
            StatusHistory.changed_at.desc(),
            StatusHistory.history_id.desc()
        )
    ).all()

    return [
        {
            "history_id": history.history_id,
            "request_id": history.request_id,
            "old_status": history.old_status,
            "new_status": history.new_status,
            "changed_by": history.changed_by,
            "change_note": history.change_note,
            "changed_at": history.changed_at
        }
        for history in history_records
    ]