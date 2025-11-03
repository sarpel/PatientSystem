"""
Clinical data domain models.
Maps to prescription, diagnosis, and related clinical tables.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Prescription(Base):
    """
    Prescription record.
    Maps to GP_RECETE table.

    Represents a prescription issued during or after a patient visit.
    Contains prescription metadata and links to prescription items.
    """

    __tablename__ = "GP_RECETE"

    # Primary Key
    RECETE_ID: Mapped[int] = mapped_column(
        "RECETE_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Prescription ID (Primary Key)",
    )

    # Foreign Keys
    MUAYENE: Mapped[Optional[int]] = mapped_column(
        "MUAYENE",
        Integer,
        ForeignKey("GP_MUAYENE.MUAYENE_ID"),
        nullable=True,
        comment="Examination ID (FK)",
    )

    HASTA_KAYIT: Mapped[int] = mapped_column(
        "HASTA_KAYIT",
        Integer,
        ForeignKey("GP_HASTA_KAYIT.HASTA_KAYIT_ID"),
        nullable=False,
        comment="Patient ID (FK)",
    )

    # Prescription Information
    RECETE_TURU: Mapped[int] = mapped_column(
        "RECETE_TURU", Integer, nullable=False, comment="Prescription type"
    )

    RECETE_TARIHI: Mapped[datetime] = mapped_column(
        "RECETE_TARIHI", DateTime, nullable=False, comment="Prescription date and time"
    )

    RECETE_NO: Mapped[Optional[str]] = mapped_column(
        "RECETE_NO", String(50), nullable=True, comment="Prescription number"
    )

    # Provider Information
    HEKIM: Mapped[Optional[int]] = mapped_column(
        "HEKIM", Integer, nullable=True, comment="Prescribing physician ID"
    )

    # Diagnosis Link
    TANI: Mapped[Optional[int]] = mapped_column(
        "TANI", SmallInteger, nullable=True, comment="Diagnosis code (ICD-10)"
    )

    # Status and Notes
    DURUM: Mapped[int] = mapped_column(
        "DURUM", Integer, nullable=False, default=1, comment="Status (1=Active, 2=Cancelled, etc.)"
    )

    ACIKLAMA: Mapped[Optional[str]] = mapped_column(
        "ACIKLAMA", Text, nullable=True, comment="Prescription notes/instructions"
    )

    # System Integration
    ESY_RECETE_NO: Mapped[Optional[str]] = mapped_column(
        "ESY_RECETE_NO", String(50), nullable=True, comment="E-Health System prescription number"
    )

    ESKI_RECETE_ID: Mapped[Optional[int]] = mapped_column(
        "ESKI_RECETE_ID", Integer, nullable=True, comment="Old prescription ID (for migration)"
    )

    # Relationships
    visit: Mapped[Optional["Visit"]] = relationship(back_populates="prescriptions")

    patient: Mapped["Patient"] = relationship(back_populates="prescriptions")

    def __repr__(self) -> str:
        return (
            f"Prescription(id={self.RECETE_ID!r}, "
            f"patient_id={self.HASTA_KAYIT!r}, "
            f"date={self.RECETE_TARIHI!r})"
        )


class Diagnosis(Base):
    """
    Additional diagnosis record for examination.
    Maps to DTY_MUAYENE_EK_TANI table.

    Represents additional diagnoses beyond the primary diagnosis.
    Linked to a specific examination/visit.
    """

    __tablename__ = "DTY_MUAYENE_EK_TANI"

    # Primary Key
    MUAYENE_EK_TANI_ID: Mapped[int] = mapped_column(
        "MUAYENE_EK_TANI_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Additional diagnosis ID (Primary Key)",
    )

    # Foreign Key to Visit
    MUAYENE: Mapped[int] = mapped_column(
        "MUAYENE",
        Integer,
        ForeignKey("GP_MUAYENE.MUAYENE_ID"),
        nullable=False,
        comment="Examination ID (FK)",
    )

    # Diagnosis Code
    TANI: Mapped[int] = mapped_column(
        "TANI", SmallInteger, nullable=False, comment="Diagnosis code (ICD-10)"
    )

    # Diagnosis Type
    TANI_TURU: Mapped[Optional[int]] = mapped_column(
        "TANI_TURU", Integer, nullable=True, comment="Diagnosis type (primary/secondary/etc.)"
    )

    # Diagnosis Details
    TANI_ACIKLAMA: Mapped[Optional[str]] = mapped_column(
        "TANI_ACIKLAMA", Text, nullable=True, comment="Diagnosis description/notes"
    )

    # Severity and Status
    SIDDET: Mapped[Optional[int]] = mapped_column(
        "SIDDET", Integer, nullable=True, comment="Severity level"
    )

    DURUM: Mapped[int] = mapped_column(
        "DURUM", Integer, nullable=False, default=1, comment="Status (1=Active, 2=Resolved, etc.)"
    )

    # Timing
    TANI_TARIHI: Mapped[Optional[date]] = mapped_column(
        "TANI_TARIHI", Date, nullable=True, comment="Diagnosis date"
    )

    # Relationships
    visit: Mapped["Visit"] = relationship(back_populates="diagnoses")

    def __repr__(self) -> str:
        return (
            f"Diagnosis(id={self.MUAYENE_EK_TANI_ID!r}, "
            f"visit_id={self.MUAYENE!r}, "
            f"code={self.TANI!r})"
        )

    @property
    def is_active(self) -> bool:
        """Check if diagnosis is currently active."""
        return self.DURUM == 1
