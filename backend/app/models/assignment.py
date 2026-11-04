
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    __table_args__ = (
        Index("request_id", "request_id"),
        Index("assigned_by", "assigned_by"),
        Index("idx_assignments_staff_current", "staff_id", "is_current"),
    )

    assignment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("service_requests.request_id"),
        nullable=False
    )

    staff_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1"
    )

    current_request_id: Mapped[int | None] = mapped_column(
        Integer,
        Computed(
            "CASE WHEN is_current = TRUE THEN request_id ELSE NULL END",
            persisted=True
        ),
        nullable=True,
        unique=True
    )
