
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "category_name",
            name="uq_department_category"
        ),
        CheckConstraint(
            "default_priority IN ('Low', 'Medium', 'High', 'Critical')",
            name="chk_category_priority"
        ),
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "departments.department_id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    default_priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Medium",
        server_default="Medium"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1"
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
