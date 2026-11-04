
from datetime import datetime

from sqlalchemy import (
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


class StatusHistory(Base):
    __tablename__ = "status_history"

    __table_args__ = (
        CheckConstraint(
            "new_status IN ('Submitted', 'Assigned', 'In Progress', "
            "'Resolved', 'Closed', 'Cancelled')",
            name="chk_new_status"
        ),
        CheckConstraint(
            "old_status IS NULL OR old_status IN "
            "('Submitted', 'Assigned', 'In Progress', "
            "'Resolved', 'Closed', 'Cancelled')",
            name="chk_old_status"
        ),
        Index("fk_history_user", "changed_by"),
        Index("idx_history_request_changed", "request_id", "changed_at"),
    )

    history_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("service_requests.request_id"),
        nullable=False
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    changed_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    change_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

