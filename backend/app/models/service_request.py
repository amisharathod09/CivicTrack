
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


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('Low', 'Medium', 'High', 'Critical')",
            name="chk_request_priority"
        ),
        CheckConstraint(
            "status IN ('Submitted', 'Assigned', 'In Progress', "
            "'Resolved', 'Closed', 'Cancelled')",
            name="chk_request_status"
        ),
        Index("idx_requests_status", "status"),
        Index("idx_requests_created_at", "created_at"),
        Index("idx_requests_status_created", "status", "created_at"),
        Index("fk_requests_citizen", "citizen_id"),
        Index("fk_requests_category", "category_id"),
        Index("fk_requests_location", "location_id"),
    )

    request_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    citizen_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "categories.category_id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    location_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "locations.location_id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Medium",
        server_default="Medium"
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Submitted",
        server_default="Submitted"
    )

    sla_due_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
