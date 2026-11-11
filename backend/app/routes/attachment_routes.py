from pathlib import Path

from fastapi.responses import FileResponse
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attachment, User
from app.services.attachment_service import upload_attachment
from app.utils.auth_dependencies import (
    get_current_user,
    require_roles
)

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)

# Attachment storage directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = (BASE_DIR / "uploads").resolve()


# Download an attachment with role-based authorization
@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find the attachment
    attachment = db.scalar(
        select(Attachment).where(
            Attachment.attachment_id == attachment_id
        )
    )

    if attachment is None:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found."
        )

    # 2. Find the complaint associated with the attachment
    from app.models import ServiceRequest, Assignment

    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == attachment.request_id
        )
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found."
        )

    # 3. Check access permissions
    if current_user.role == "citizen":

        if complaint.citizen_id != current_user.user_id:
            raise HTTPException(
                status_code=404,
                detail="Attachment not found."
            )

    elif current_user.role == "staff":

        current_assignment = db.scalar(
            select(Assignment).where(
                Assignment.request_id == attachment.request_id,
                Assignment.staff_id == current_user.user_id,
                Assignment.is_current.is_(True)
            )
        )

        if current_assignment is None:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned to this complaint."
            )

    elif current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to download this attachment."
        )

    # 4. Resolve and validate the stored file path
    file_path = (BASE_DIR / attachment.file_path).resolve()

    if not file_path.is_relative_to(UPLOAD_DIR):
        raise HTTPException(
            status_code=400,
            detail="Invalid attachment storage path."
        )

    # 5. Check whether the physical file exists
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Attachment file not found."
        )

    # 6. Return the file
    return FileResponse(
        path=file_path,
        media_type=attachment.mime_type,
        filename=attachment.file_name
    )

# Get all attachments (Admin only)
@router.get("")
def get_attachments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    statement = select(Attachment).order_by(
        Attachment.uploaded_at.desc()
    )

    attachment_records = db.scalars(statement).all()

    return [
        {
            "attachment_id": attachment.attachment_id,
            "request_id": attachment.request_id,
            "uploaded_by": attachment.uploaded_by,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "mime_type": attachment.mime_type,
            "file_size": attachment.file_size,
            "attachment_type": attachment.attachment_type,
            "uploaded_at": attachment.uploaded_at
        }
        for attachment in attachment_records
    ]


# Get attachments uploaded by the logged-in citizen or staff member
@router.get("/my-attachments")
def get_my_attachments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("citizen", "staff")
    )
):
    statement = (
        select(Attachment)
        .where(Attachment.uploaded_by == current_user.user_id)
        .order_by(Attachment.uploaded_at.desc())
    )

    attachment_records = db.scalars(statement).all()

    return [
        {
            "attachment_id": attachment.attachment_id,
            "request_id": attachment.request_id,
            "file_name": attachment.file_name,
            "mime_type": attachment.mime_type,
            "file_size": attachment.file_size,
            "attachment_type": attachment.attachment_type,
            "uploaded_at": attachment.uploaded_at
        }
        for attachment in attachment_records
    ]


# Upload a complaint photo or resolution evidence
@router.post("/upload/{request_id}", status_code=status.HTTP_201_CREATED)
async def create_attachment(
    request_id: int,
    file: UploadFile = File(...),
    attachment_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Read at most 5 MB + 1 byte to detect oversized uploads
    file_content = await file.read(5 * 1024 * 1024 + 1)

    attachment, error = upload_attachment(
        request_id=request_id,
        attachment_type=attachment_type,
        original_filename=file.filename or "",
        file_content=file_content,
        current_user=current_user,
        db=db
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Attachment uploaded successfully.",
        "attachment_id": attachment.attachment_id,
        "request_id": attachment.request_id,
        "file_name": attachment.file_name,
        "mime_type": attachment.mime_type,
        "file_size": attachment.file_size,
        "attachment_type": attachment.attachment_type,
        "uploaded_at": attachment.uploaded_at
    }
