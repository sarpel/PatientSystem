"""
Visit and examination domain models.
Maps to GP_MUAYENE, GP_HASTA_KABUL and related visit tables.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Visit(Base):
    """
    Patient examination/visit record.
    Maps to GP_MUAYENE table.

    Core entity representing a medical examination during a patient visit.
    Contains vital signs, symptoms, diagnoses, and clinical notes.
    """

    __tablename__ = "GP_MUAYENE"

    # Primary Key
    MUAYENE_ID: Mapped[int] = mapped_column(
        "MUAYENE_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Examination ID (Primary Key)",
    )

    # Foreign Key to PatientAdmission
    HASTA_KABUL: Mapped[int] = mapped_column(
        "HASTA_KABUL",
        Integer,
        ForeignKey("GP_HASTA_KABUL.HASTA_KABUL_ID"),
        nullable=False,
        comment="Patient admission ID (FK)",
    )

    # Examination Type
    MUAYENE_TURU: Mapped[int] = mapped_column(
        "MUAYENE_TURU", Integer, nullable=False, comment="Examination type"
    )

    # Primary Diagnosis
    ANA_TANI: Mapped[Optional[int]] = mapped_column(
        "ANA_TANI", SmallInteger, nullable=True, comment="Primary diagnosis (ICD-10 code)"
    )

    # Vital Signs - Physical Measurements
    AGIRLIK: Mapped[Optional[int]] = mapped_column(
        "AGIRLIK", Integer, nullable=True, comment="Weight (grams)"
    )

    BOY: Mapped[Optional[int]] = mapped_column("BOY", Integer, nullable=True, comment="Height (cm)")

    BEL_CEVRESI: Mapped[Optional[int]] = mapped_column(
        "BEL_CEVRESI", Integer, nullable=True, comment="Waist circumference (cm)"
    )

    KALCA_CEVRESI: Mapped[Optional[int]] = mapped_column(
        "KALCA_CEVRESI", Integer, nullable=True, comment="Hip circumference (cm)"
    )

    # Vital Signs - Cardiovascular
    SISTOLIK_KAN_BASINCI: Mapped[Optional[int]] = mapped_column(
        "SISTOLIK_KAN_BASINCI", Integer, nullable=True, comment="Systolic blood pressure (mmHg)"
    )

    DIASTOLIK_KAN_BASINCI: Mapped[Optional[int]] = mapped_column(
        "DIASTOLIK_KAN_BASINCI", Integer, nullable=True, comment="Diastolic blood pressure (mmHg)"
    )

    NABIZ: Mapped[Optional[int]] = mapped_column(
        "NABIZ", Integer, nullable=True, comment="Pulse rate (bpm)"
    )

    # Vital Signs - Other
    VUCUT_ISISI: Mapped[Optional[Decimal]] = mapped_column(
        "VUCUT_ISISI", Numeric(3, 1), nullable=True, comment="Body temperature (°C)"
    )

    GLASGOW_KOMA_SKALASI: Mapped[Optional[int]] = mapped_column(
        "GLASGOW_KOMA_SKALASI", Integer, nullable=True, comment="Glasgow Coma Scale score"
    )

    # Clinical Notes
    SIKAYETI: Mapped[Optional[str]] = mapped_column(
        "SIKAYETI", String, nullable=True, comment="Patient complaint/symptoms"
    )

    HIKAYESI: Mapped[Optional[str]] = mapped_column(
        "HIKAYESI", String, nullable=True, comment="Medical history"
    )

    BULGU: Mapped[Optional[str]] = mapped_column(
        "BULGU", String, nullable=True, comment="Physical examination findings"
    )

    MUAYENE_NOT: Mapped[Optional[str]] = mapped_column(
        "MUAYENE_NOT", String, nullable=True, comment="Examination notes"
    )

    # Additional Information
    MESLEK: Mapped[Optional[int]] = mapped_column(
        "MESLEK", SmallInteger, nullable=True, comment="Occupation (at time of visit)"
    )

    SIGARA_KULLANIMI: Mapped[Optional[int]] = mapped_column(
        "SIGARA_KULLANIMI", Integer, nullable=True, comment="Smoking status (at time of visit)"
    )

    # Emergency/Disaster Information
    OLAY_AFET_BILGISI: Mapped[Optional[str]] = mapped_column(
        "OLAY_AFET_BILGISI", String(100), nullable=True, comment="Disaster/event information"
    )

    AFET_OLAY_VATANDAS_TIPI: Mapped[Optional[int]] = mapped_column(
        "AFET_OLAY_VATANDAS_TIPI", Integer, nullable=True, comment="Disaster victim type"
    )

    HAYATI_TEHLIKE_DURUMU: Mapped[Optional[int]] = mapped_column(
        "HAYATI_TEHLIKE_DURUMU", Integer, nullable=True, comment="Life-threatening status"
    )

    # System Fields
    ESKI_MUAYENE_ID: Mapped[Optional[int]] = mapped_column(
        "ESKI_MUAYENE_ID", Integer, nullable=True, comment="Old examination ID (for migration)"
    )

    # Relationships
    admission: Mapped["PatientAdmission"] = relationship(back_populates="visits")

    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="visit")

    diagnoses: Mapped[list["Diagnosis"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"Visit(id={self.MUAYENE_ID!r}, "
            f"admission_id={self.HASTA_KABUL!r}, "
            f"type={self.MUAYENE_TURU!r})"
        )

    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI if weight and height are available."""
        if self.AGIRLIK and self.BOY and self.BOY > 0:
            weight_kg = self.AGIRLIK / 1000
            height_m = self.BOY / 100
            return round(weight_kg / (height_m**2), 2)
        return None

    @property
    def waist_hip_ratio(self) -> Optional[float]:
        """Calculate waist-to-hip ratio."""
        if self.BEL_CEVRESI and self.KALCA_CEVRESI and self.KALCA_CEVRESI > 0:
            return round(self.BEL_CEVRESI / self.KALCA_CEVRESI, 2)
        return None

    @property
    def blood_pressure_str(self) -> Optional[str]:
        """Format blood pressure as 'systolic/diastolic'."""
        if self.SISTOLIK_KAN_BASINCI and self.DIASTOLIK_KAN_BASINCI:
            return f"{self.SISTOLIK_KAN_BASINCI}/{self.DIASTOLIK_KAN_BASINCI}"
        return None


class PatientAdmission(Base):
    """
    Patient admission/registration for a visit.
    Maps to GP_HASTA_KABUL table.

    Represents the patient's admission to the facility for treatment.
    Links patient to their visit/examination records.
    """

    __tablename__ = "GP_HASTA_KABUL"

    # Primary Key
    HASTA_KABUL_ID: Mapped[int] = mapped_column(
        "HASTA_KABUL_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Patient admission ID (Primary Key)",
    )

    # Foreign Key to Patient
    HASTA_KAYIT: Mapped[int] = mapped_column(
        "HASTA_KAYIT",
        Integer,
        ForeignKey("GP_HASTA_KAYIT.HASTA_KAYIT_ID"),
        nullable=False,
        comment="Patient registration ID (FK)",
    )

    # Admission DateTime
    KABUL_TARIHI: Mapped[datetime] = mapped_column(
        "KABUL_TARIHI", DateTime, nullable=False, comment="Admission date and time"
    )

    # Admission Type and Reason
    KABUL_TURU: Mapped[int] = mapped_column(
        "KABUL_TURU", Integer, nullable=False, comment="Admission type"
    )

    BASVURU_NEDENI: Mapped[Optional[int]] = mapped_column(
        "BASVURU_NEDENI", Integer, nullable=True, comment="Reason for visit"
    )

    # Provider Information
    HEKIM: Mapped[Optional[int]] = mapped_column(
        "HEKIM", Integer, nullable=True, comment="Physician ID"
    )

    # Status
    DURUM: Mapped[int] = mapped_column(
        "DURUM", Integer, nullable=False, default=1, comment="Status (1=Active, 2=Completed, etc.)"
    )

    # System Fields
    ESKI_HASTA_KABUL_ID: Mapped[Optional[int]] = mapped_column(
        "ESKI_HASTA_KABUL_ID", Integer, nullable=True, comment="Old admission ID (for migration)"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="admissions")

    visits: Mapped[list["Visit"]] = relationship(
        back_populates="admission", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"PatientAdmission(id={self.HASTA_KABUL_ID!r}, "
            f"patient_id={self.HASTA_KAYIT!r}, "
            f"date={self.KABUL_TARIHI!r})"
        )
