
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    __table_args__ = (
        CheckConstraint(
            "file_size > 0",
            name="chk_attachment_file_size"
        ),
        CheckConstraint(
            "attachment_type IN "
            "('complaint_photo', 'resolution_evidence')",
            name="chk_attachment_type"
        ),
        Index("fk_attachments_request", "request_id"),
        Index("fk_attachments_user", "uploaded_by"),
    )

    attachment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("service_requests.request_id"),
        nullable=False
    )

    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    attachment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
