"""
Patient domain models.
Maps to GP_HASTA_KAYIT and related patient tables.
"""

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, BigInteger, Date, DateTime, LargeBinary, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.config.settings import settings


class Patient(Base):
    """
    Patient registration record.
    Maps to GP_HASTA_KAYIT table.

    Core entity representing a registered patient in the system.
    Contains demographic information, identification, and registration details.
    """

    __tablename__ = "GP_HASTA_KAYIT"

    # Primary Key
    HASTA_KAYIT_ID: Mapped[int] = mapped_column(
        "HASTA_KAYIT_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Patient registration ID (Primary Key)"
    )

    # Patient Type and Registration
    HASTA_TIPI: Mapped[int] = mapped_column(
        "HASTA_TIPI",
        Integer,
        ForeignKey("LST_HASTA_TIPI.KODU"),
        nullable=False,
        default=1,
        comment="Patient type (FK to LST_HASTA_TIPI)"
    )

    HASTA_KAYIT_TURU: Mapped[int] = mapped_column(
        "HASTA_KAYIT_TURU",
        Integer,
        ForeignKey("LST_HASTA_KAYIT_TURU.KODU"),
        nullable=False,
        default=1,
        comment="Registration type (FK to LST_HASTA_KAYIT_TURU)"
    )

    # Identification
    HASTA_KIMLIK_NO: Mapped[Optional[int]] = mapped_column(
        "HASTA_KIMLIK_NO",
        BigInteger,
        nullable=True,
        comment="National ID number (TC Kimlik No)"
    )

    HASTA_KODU: Mapped[Optional[str]] = mapped_column(
        "HASTA_KODU",
        String(9),
        nullable=True,
        comment="Patient code (internal identifier)"
    )

    # Personal Information
    AD: Mapped[str] = mapped_column(
        "AD",
        String(100),
        nullable=False,
        comment="First name"
    )

    SOYAD: Mapped[str] = mapped_column(
        "SOYAD",
        String(100),
        nullable=False,
        comment="Last name"
    )

    # Gender
    CINSIYET: Mapped[int] = mapped_column(
        "CINSIYET",
        Integer,
        ForeignKey("LST_CINSIYET.KODU"),
        nullable=False,
        comment="Gender (FK to LST_CINSIYET)"
    )

    CINSIYET_RESMI: Mapped[int] = mapped_column(
        "CINSIYET_RESMI",
        Integer,
        ForeignKey("LST_CINSIYET_RESMI.KODU"),
        nullable=False,
        comment="Official gender (FK to LST_CINSIYET_RESMI)"
    )

    # Birth Information
    DOGUM_TARIHI: Mapped[Optional[date]] = mapped_column(
        "DOGUM_TARIHI",
        Date,
        nullable=True,
        comment="Date of birth"
    )

    DOGUM_TARIHI_RESMI: Mapped[Optional[date]] = mapped_column(
        "DOGUM_TARIHI_RESMI",
        Date,
        nullable=True,
        comment="Official date of birth"
    )

    DOGUM_YERI: Mapped[Optional[str]] = mapped_column(
        "DOGUM_YERI",
        String(50),
        nullable=True,
        comment="Place of birth"
    )

    DOGUM_SIRASI: Mapped[Optional[int]] = mapped_column(
        "DOGUM_SIRASI",
        Integer,
        ForeignKey("LST_DOGUM_SIRASI.KODU"),
        nullable=True,
        comment="Birth order (FK to LST_DOGUM_SIRASI)"
    )

    # Parental Information
    ANNE_ADI: Mapped[Optional[str]] = mapped_column(
        "ANNE_ADI",
        String(100),
        nullable=True,
        comment="Mother's name"
    )

    ANNE_KIMLIK_NO: Mapped[Optional[int]] = mapped_column(
        "ANNE_KIMLIK_NO",
        BigInteger,
        nullable=True,
        comment="Mother's national ID number"
    )

    ANNE_PASAPORT_NO: Mapped[Optional[str]] = mapped_column(
        "ANNE_PASAPORT_NO",
        String(50),
        nullable=True,
        comment="Mother's passport number"
    )

    BABA_ADI: Mapped[Optional[str]] = mapped_column(
        "BABA_ADI",
        String(100),
        nullable=True,
        comment="Father's name"
    )

    BABA_KIMLIK_NO: Mapped[Optional[int]] = mapped_column(
        "BABA_KIMLIK_NO",
        BigInteger,
        nullable=True,
        comment="Father's national ID number"
    )

    BABA_PASAPORT_NO: Mapped[Optional[str]] = mapped_column(
        "BABA_PASAPORT_NO",
        String(50),
        nullable=True,
        comment="Father's passport number"
    )

    # Nationality and Foreign Patient Information
    UYRUK: Mapped[str] = mapped_column(
        "UYRUK",
        String(10),
        ForeignKey("LST_ULKE_KODLARI.KODU"),
        nullable=True,
        default='TR',
        comment="Nationality (FK to LST_ULKE_KODLARI)"
    )

    YABANCI_HASTA_TURU: Mapped[Optional[int]] = mapped_column(
        "YABANCI_HASTA_TURU",
        Integer,
        ForeignKey("LST_YABANCI_HASTA_TURU.KODU"),
        nullable=True,
        comment="Foreign patient type (FK to LST_YABANCI_HASTA_TURU)"
    )

    PASAPORT_NO: Mapped[Optional[str]] = mapped_column(
        "PASAPORT_NO",
        String(50),
        nullable=True,
        comment="Passport number"
    )

    YUPASS_NO: Mapped[Optional[int]] = mapped_column(
        "YUPASS_NO",
        Integer,
        nullable=True,
        comment="YUPASS number (foreign patient ID)"
    )

    # Family Doctor Information
    MEVCUT_AH: Mapped[Optional[str]] = mapped_column(
        "MEVCUT_AH",
        String(100),
        nullable=True,
        comment="Current family physician"
    )

    MEVCUT_AHB: Mapped[Optional[str]] = mapped_column(
        "MEVCUT_AHB",
        String(100),
        nullable=True,
        comment="Current family health center"
    )

    AH_KAYIT_TARIHI: Mapped[Optional[datetime]] = mapped_column(
        "AH_KAYIT_TARIHI",
        DateTime,
        nullable=True,
        comment="Family physician registration date"
    )

    AH_GUNCELLEME: Mapped[date] = mapped_column(
        "AH_GUNCELLEME",
        Date,
        nullable=False,
        default=date(2000, 1, 1),
        comment="Family physician last update date"
    )

    # Photo and Medical Information
    KISI_FOTOGRAF: Mapped[Optional[bytes]] = mapped_column(
        "KISI_FOTOGRAF",
        LargeBinary,
        nullable=True,
        comment="Patient photograph"
    )

    KADIN_IZLEM_SAYISI: Mapped[Optional[int]] = mapped_column(
        "KADIN_IZLEM_SAYISI",
        Integer,
        nullable=True,
        comment="Women's health monitoring count"
    )

    # Death Information
    OLUM_TARIHI: Mapped[Optional[date]] = mapped_column(
        "OLUM_TARIHI",
        Date,
        nullable=True,
        comment="Date of death"
    )

    OLUM_BILDIRIM: Mapped[Optional[str]] = mapped_column(
        "OLUM_BILDIRIM",
        nullable=True,
        comment="Death notification (SQL_VARIANT)"
    )

    # System and Integration Fields
    OZEL_NOT: Mapped[Optional[str]] = mapped_column(
        "OZEL_NOT",
        String,
        nullable=True,
        comment="Special notes"
    )

    ESKI_HASTA_KAYIT_ID: Mapped[Optional[int]] = mapped_column(
        "ESKI_HASTA_KAYIT_ID",
        Integer,
        nullable=True,
        comment="Old patient registration ID (for migration)"
    )

    SGK_SMS_NO: Mapped[Optional[int]] = mapped_column(
        "SGK_SMS_NO",
        BigInteger,
        nullable=True,
        comment="Social Security (SGK) SMS number"
    )

    ESY_HASTA_ID: Mapped[Optional[str]] = mapped_column(
        "ESY_HASTA_ID",
        String(40),
        nullable=True,
        comment="E-Health System (ESY) patient ID"
    )

    MERNIS_GUNCELLE: Mapped[date] = mapped_column(
        "MERNIS_GUNCELLE",
        Date,
        nullable=False,
        default=date(2000, 1, 1),
        comment="MERNIS (civil registry) last update date"
    )

    ASI_TAKVIMI_GUNCELLEME_TARIHI: Mapped[Optional[datetime]] = mapped_column(
        "ASI_TAKVIMI_GUNCELLEME_TARIHI",
        DateTime,
        nullable=True,
        comment="Vaccination schedule last update date"
    )

    # COVID-19 Related Fields
    PLAZMA_NOTU: Mapped[Optional[str]] = mapped_column(
        "PLAZMA_NOTU",
        String(100),
        nullable=True,
        comment="Plasma donation note"
    )

    GRIP_ASI_NOTU: Mapped[Optional[str]] = mapped_column(
        "GRIP_ASI_NOTU",
        String(100),
        nullable=True,
        comment="Flu vaccination note"
    )

    # Relationships
    demographics: Mapped[Optional["PatientDemographics"]] = relationship(
        back_populates="patient",
        uselist=False
    )

    admissions: Mapped[list["PatientAdmission"]] = relationship(
        back_populates="patient"
    )

    prescriptions: Mapped[list["Prescription"]] = relationship(
        back_populates="patient"
    )

    def __repr__(self) -> str:
        return (
            f"Patient(id={self.HASTA_KAYIT_ID!r}, "
            f"name={self.AD!r} {self.SOYAD!r}, "
            f"tc={self.HASTA_KIMLIK_NO!r})"
        )

    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        return f"{self.AD} {self.SOYAD}"

    @property
    def age(self) -> Optional[int]:
        """Calculate patient's age from birth date."""
        if self.DOGUM_TARIHI:
            today = date.today()
            return today.year - self.DOGUM_TARIHI.year - (
                (today.month, today.day) < (self.DOGUM_TARIHI.month, self.DOGUM_TARIHI.day)
            )
        return None

    @property
    def is_deceased(self) -> bool:
        """Check if patient is deceased."""
        return self.OLUM_TARIHI is not None


class PatientDemographics(Base):
    """
    Patient demographics and lifestyle information.
    Maps to GP_HASTA_OZLUK table.

    Contains detailed demographic, lifestyle, and social information about patients.
    One-to-one relationship with Patient.
    """

    __tablename__ = "GP_HASTA_OZLUK"

    # Primary Key
    HASTA_OZLUK_ID: Mapped[int] = mapped_column(
        "HASTA_OZLUK_ID",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Patient demographics ID (Primary Key)"
    )

    # Foreign Key to Patient
    HASTA_KAYIT: Mapped[int] = mapped_column(
        "HASTA_KAYIT",
        Integer,
        ForeignKey("GP_HASTA_KAYIT.HASTA_KAYIT_ID"),
        nullable=False,
        comment="Patient registration ID (FK)"
    )

    # Demographic Information
    MEDENI_HALI: Mapped[Optional[int]] = mapped_column(
        "MEDENI_HALI",
        Integer,
        ForeignKey("LST_MEDENI_HALI.KODU"),
        nullable=True,
        comment="Marital status"
    )

    EVLENME_YASI: Mapped[Optional[int]] = mapped_column(
        "EVLENME_YASI",
        Integer,
        nullable=True,
        comment="Marriage age"
    )

    OGRENIM_DURUMU: Mapped[Optional[int]] = mapped_column(
        "OGRENIM_DURUMU",
        Integer,
        ForeignKey("LST_OGRENIM_DURUMU.KODU"),
        nullable=True,
        comment="Education level"
    )

    OGRENCININ_SINIFI: Mapped[Optional[int]] = mapped_column(
        "OGRENCININ_SINIFI",
        Integer,
        ForeignKey("LST_OGRENCININ_SINIFI.KODU"),
        nullable=True,
        comment="Student's grade level"
    )

    # Employment and Income
    IS_DURUMU: Mapped[Optional[int]] = mapped_column(
        "IS_DURUMU",
        Integer,
        ForeignKey("LST_IS_DURUMU.KODU"),
        nullable=True,
        comment="Employment status"
    )

    MESLEK: Mapped[Optional[int]] = mapped_column(
        "MESLEK",
        SmallInteger,
        ForeignKey("LST_MESLEKLER.KODU"),
        nullable=True,
        comment="Occupation"
    )

    GELIR_DURUMU: Mapped[Optional[int]] = mapped_column(
        "GELIR_DURUMU",
        Integer,
        ForeignKey("LST_GELIR_DURUMU.KODU"),
        nullable=True,
        comment="Income level"
    )

    # Social Security
    SOSYAL_GUVENCE: Mapped[int] = mapped_column(
        "SOSYAL_GUVENCE",
        Integer,
        ForeignKey("LST_SOSYAL_GUVENCE_DURUMU.KODU"),
        nullable=False,
        comment="Social security status"
    )

    # Medical Information
    KAN_GRUBU: Mapped[Optional[int]] = mapped_column(
        "KAN_GRUBU",
        Integer,
        ForeignKey("LST_KAN_GRUBU.KODU"),
        nullable=True,
        comment="Blood type"
    )

    AMELIYAT_GECMISI: Mapped[int] = mapped_column(
        "AMELIYAT_GECMISI",
        Integer,
        ForeignKey("LST_AMELIYAT_GECMISI.KODU"),
        nullable=False,
        default=99,
        comment="Surgery history"
    )

    YARALANMA_GECMISI: Mapped[int] = mapped_column(
        "YARALANMA_GECMISI",
        Integer,
        ForeignKey("LST_YARALANMA_GECMISI.KODU"),
        nullable=False,
        default=99,
        comment="Injury history"
    )

    OZURLULUK_DURUMU: Mapped[int] = mapped_column(
        "OZURLULUK_DURUMU",
        Integer,
        ForeignKey("LST_OZURLULUK_DURUMU.KODU"),
        nullable=False,
        default=99,
        comment="Disability status"
    )

    # Physical Measurements
    AGIRLIK: Mapped[int] = mapped_column(
        "AGIRLIK",
        Integer,
        nullable=False,
        comment="Weight (grams)"
    )

    BOY: Mapped[int] = mapped_column(
        "BOY",
        Integer,
        nullable=False,
        comment="Height (cm)"
    )

    # Lifestyle - Substance Use
    ALKOL_KULLANIMI: Mapped[Optional[int]] = mapped_column(
        "ALKOL_KULLANIMI",
        Integer,
        ForeignKey("LST_ALKOL_KULLANIMI.KODU"),
        nullable=True,
        comment="Alcohol use"
    )

    MADDE_KULLANIMI: Mapped[Optional[int]] = mapped_column(
        "MADDE_KULLANIMI",
        Integer,
        ForeignKey("LST_MADDE_KULLANIMI.KODU"),
        nullable=True,
        comment="Substance use"
    )

    SIGARA_KULLANIMI: Mapped[Optional[int]] = mapped_column(
        "SIGARA_KULLANIMI",
        Integer,
        ForeignKey("LST_SIGARA_KULLANIMI.KODU"),
        nullable=True,
        comment="Smoking status"
    )

    SIGARA_ADEDI: Mapped[Optional[int]] = mapped_column(
        "SIGARA_ADEDI",
        Integer,
        nullable=True,
        comment="Number of cigarettes per day"
    )

    SIGARA_KULLANIMI_TEYIT_TARIHI: Mapped[Optional[datetime]] = mapped_column(
        "SIGARA_KULLANIMI_TEYIT_TARIHI",
        DateTime,
        nullable=True,
        comment="Smoking status confirmation date"
    )

    # Location and Living Situation
    KIR_KENT: Mapped[Optional[int]] = mapped_column(
        "KIR_KENT",
        Integer,
        ForeignKey("LST_KIR_KENT.KODU"),
        nullable=True,
        comment="Rural/Urban location"
    )

    GEZICI: Mapped[Optional[bool]] = mapped_column(
        "GEZICI",
        nullable=True,
        comment="Mobile/nomadic status"
    )

    # Family and Household
    AILE_KODU: Mapped[Optional[int]] = mapped_column(
        "AILE_KODU",
        SmallInteger,
        ForeignKey("HRC_AILE.AILE_KODU"),
        nullable=True,
        comment="Family code"
    )

    AILE_SIRA_NO: Mapped[Optional[str]] = mapped_column(
        "AILE_SIRA_NO",
        String(50),
        nullable=True,
        comment="Family sequence number"
    )

    BIREY_SIRA_NO: Mapped[Optional[str]] = mapped_column(
        "BIREY_SIRA_NO",
        String(50),
        nullable=True,
        comment="Individual sequence number"
    )

    CILT_AD: Mapped[Optional[str]] = mapped_column(
        "CILT_AD",
        String(50),
        nullable=True,
        comment="Civil registry volume name"
    )

    CILT_KOD: Mapped[Optional[str]] = mapped_column(
        "CILT_KOD",
        String(50),
        nullable=True,
        comment="Civil registry volume code"
    )

    # Health Services
    EVDE_SAGLIK_HIZMETI_ALMA_DURUMU: Mapped[Optional[bool]] = mapped_column(
        "EVDE_SAGLIK_HIZMETI_ALMA_DURUMU",
        nullable=True,
        comment="Home health service status"
    )

    YERINDE_SAGLIK_HIZMETI_ALMA_DURUMU: Mapped[Optional[bool]] = mapped_column(
        "YERINDE_SAGLIK_HIZMETI_ALMA_DURUMU",
        nullable=True,
        default=False,
        comment="On-site health service status"
    )

    HASTA_KABUL_ONCELIK: Mapped[Optional[bool]] = mapped_column(
        "HASTA_KABUL_ONCELIK",
        nullable=True,
        comment="Patient admission priority flag"
    )

    # Prison-related Information
    HUKUMLULUK_DURUMU: Mapped[Optional[int]] = mapped_column(
        "HUKUMLULUK_DURUMU",
        Integer,
        ForeignKey("LST_HUKUMLULUK_DURUMU.KODU"),
        nullable=True,
        comment="Conviction status"
    )

    CEZA_EVI_TIPI: Mapped[Optional[int]] = mapped_column(
        "CEZA_EVI_TIPI",
        Integer,
        ForeignKey("LST_CEZAEVI_TIPI.KODU"),
        nullable=True,
        comment="Prison type"
    )

    # Contact Information
    EPOSTA: Mapped[Optional[str]] = mapped_column(
        "EPOSTA",
        String(100),
        nullable=True,
        comment="Email address"
    )

    # System Fields
    GUNCELLEME_TARIHI: Mapped[Optional[datetime]] = mapped_column(
        "GUNCELLEME_TARIHI",
        nullable=True,
        comment="Last update timestamp"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(
        back_populates="demographics"
    )

    def __repr__(self) -> str:
        return (
            f"PatientDemographics(id={self.HASTA_OZLUK_ID!r}, "
            f"patient_id={self.HASTA_KAYIT!r})"
        )

    @property
    def bmi(self) -> Optional[float]:
        """Calculate Body Mass Index (BMI)."""
        if self.AGIRLIK and self.BOY and self.BOY > 0:
            # Convert weight from grams to kg and height from cm to meters
            weight_kg = self.AGIRLIK / 1000
            height_m = self.BOY / 100
            return round(weight_kg / (height_m ** 2), 2)
        return None

    @property
    def bmi_category(self) -> Optional[str]:
        """Get BMI category using configured thresholds."""
        bmi = self.bmi
        if bmi is None:
            return None
        if bmi < settings.underweight_bmi_threshold:
            return "Underweight"
        elif bmi < settings.overweight_bmi_threshold:
            return "Normal"
        elif bmi < settings.obesity_bmi_threshold:
            return "Overweight"
        else:
            return "Obese"