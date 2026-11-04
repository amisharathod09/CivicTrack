from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attachment


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)


@router.get("")
def get_attachments(db: Session = Depends(get_db)):

    statement = select(Attachment)

    attachment_records = db.execute(statement).scalars().all()

    return [
        {
            "attachment_id": attachment.attachment_id,
            "request_id": attachment.request_id,
            "uploaded_by": attachment.uploaded_by,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "file_size": attachment.file_size,
            "attachment_type": attachment.attachment_type,
            "uploaded_at": attachment.uploaded_at
        }
        for attachment in attachment_records
    ]