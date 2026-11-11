
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Assignment, Attachment, ServiceRequest, User


# Storage directory: E:\CivicTrack\backend\uploads
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

# Maximum file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed image formats and their file signatures
ALLOWED_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png"
}


def validate_image(file_content: bytes, extension: str):
    """Validate image extension, content and file signature."""

    if not file_content:
        return False, "Uploaded file is empty."

    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only JPG, JPEG and PNG files are allowed."

    if extension in [".jpg", ".jpeg"]:
        if not file_content.startswith(b"\xff\xd8\xff"):
            return False, "Invalid JPEG image."

        mime_type = "image/jpeg"

    else:
        if not file_content.startswith(b"\x89PNG\r\n\x1a\n"):
            return False, "Invalid PNG image."

        mime_type = "image/png"

    return True, mime_type


def upload_attachment(
    request_id: int,
    attachment_type: str,
    original_filename: str,
    file_content: bytes,
    current_user: User,
    db: Session
):
    # 1. Validate attachment type
    if attachment_type not in [
        "complaint_photo",
        "resolution_evidence"
    ]:
        return None, "Invalid attachment type."

    # 2. Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        return None, "File size must not exceed 5 MB."

    # 3. Validate file extension
    extension = Path(original_filename.replace("\\", "/")).suffix.lower()

    is_valid, validation_result = validate_image(
        file_content,
        extension
    )

    if not is_valid:
        return None, validation_result

    mime_type = validation_result

    # 4. Find the complaint
    complaint = db.scalar(
        select(ServiceRequest).where(
            ServiceRequest.request_id == request_id
        )
    )

    if complaint is None:
        return None, "Complaint not found."

    # 5. Check citizen and staff permissions
    if current_user.role == "citizen":

        if attachment_type != "complaint_photo":
            return None, "Citizens can upload complaint photos only."

        if complaint.citizen_id != current_user.user_id:
            return None, "Complaint not found."

        if complaint.status in ["Resolved", "Closed", "Cancelled"]:
            return None, "Photos cannot be uploaded for completed or cancelled complaints."

    elif current_user.role == "staff":

        if attachment_type != "resolution_evidence":
            return None, "Staff can upload resolution evidence only."

        current_assignment = db.scalar(
            select(Assignment).where(
                Assignment.request_id == request_id,
                Assignment.staff_id == current_user.user_id,
                Assignment.is_current.is_(True)
            )
        )

        if current_assignment is None:
            return None, "You are not assigned to this complaint."

        if complaint.status not in ["In Progress", "Resolved"]:
            return None, "Resolution evidence can only be uploaded for complaints in progress or resolved."

    else:
        return None, "You do not have permission to upload attachments."

    # 6. Generate a unique server-side filename
    unique_filename = f"{uuid4().hex}{extension}"

    # 7. Create a complaint-specific storage folder
    complaint_folder = UPLOAD_DIR / str(request_id)
    complaint_folder.mkdir(parents=True, exist_ok=True)

    file_location = complaint_folder / unique_filename

    # Store a relative path in MySQL
    relative_path = (
        Path("uploads") / str(request_id) / unique_filename
    ).as_posix()

    # 8. Save file and metadata
    try:
        file_location.write_bytes(file_content)

        safe_original_filename = (
            original_filename.replace("\\", "/").split("/")[-1]
        )[:255]

        new_attachment = Attachment(
            request_id=request_id,
            uploaded_by=current_user.user_id,
            file_name=safe_original_filename,
            file_path=relative_path,
            mime_type=mime_type,
            file_size=len(file_content),
            attachment_type=attachment_type
        )

        db.add(new_attachment)
        db.commit()
        db.refresh(new_attachment)

        return new_attachment, None

    except Exception:
        db.rollback()

        if file_location.exists():
            file_location.unlink()

        raise
