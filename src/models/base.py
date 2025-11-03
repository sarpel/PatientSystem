"""
Base model class for all ORM models.
Provides common fields and functionality for all database entities.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Declarative base class for all ORM models.
    Uses SQLAlchemy 2.0 declarative mapping style.
    """
    pass


class TimestampMixin:
    """
    Mixin class providing created_at and updated_at timestamps.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=func.now(),
        nullable=True,
        comment="Timestamp when record was last updated"
    )


class SoftDeleteMixin:
    """
    Mixin class providing soft delete functionality.

    Attributes:
        deleted_at: Timestamp when the record was soft-deleted
        is_deleted: Boolean flag indicating if record is deleted
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Timestamp when record was soft-deleted"
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark the record as deleted with current timestamp."""
        self.deleted_at = func.now()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
