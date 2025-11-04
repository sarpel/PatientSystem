"""
Unit tests for Visit models.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from src.models.visit import PatientAdmission, Visit


class TestVisit:
    """Test suite for Visit model."""

    def test_visit_creation(self):
        """Test creating a Visit instance."""
        visit = Visit(HASTA_KABUL=1, MUAYENE_TURU=1)

        assert visit.HASTA_KABUL == 1
        assert visit.MUAYENE_TURU == 1

    def test_visit_with_vital_signs(self):
        """Test visit with vital signs."""
        visit = Visit(
            HASTA_KABUL=1,
            MUAYENE_TURU=1,
            AGIRLIK=70000,  # 70kg
            BOY=175,  # 175cm
            SISTOLIK_KAN_BASINCI=120,
            DIASTOLIK_KAN_BASINCI=80,
            NABIZ=72,
            VUCUT_ISISI=Decimal("36.5"),
        )

        assert visit.AGIRLIK == 70000
        assert visit.BOY == 175
        assert visit.SISTOLIK_KAN_BASINCI == 120
        assert visit.DIASTOLIK_KAN_BASINCI == 80
        assert visit.NABIZ == 72
        assert visit.VUCUT_ISISI == Decimal("36.5")

    def test_visit_bmi_calculation(self):
        """Test BMI calculation for visit."""
        visit = Visit(HASTA_KABUL=1, MUAYENE_TURU=1, AGIRLIK=70000, BOY=175)  # 70kg  # 175cm

        bmi = visit.bmi
        assert bmi is not None
        assert 22 < bmi < 23

    def test_visit_bmi_none_when_no_measurements(self):
        """Test BMI returns None when measurements missing."""
        visit = Visit(HASTA_KABUL=1, MUAYENE_TURU=1)

        assert visit.bmi is None

    def test_waist_hip_ratio_calculation(self):
        """Test waist-to-hip ratio calculation."""
        visit = Visit(
            HASTA_KABUL=1,
            MUAYENE_TURU=1,
            BEL_CEVRESI=90,  # 90cm waist
            KALCA_CEVRESI=100,  # 100cm hip
        )

        ratio = visit.waist_hip_ratio
        assert ratio is not None
        assert ratio == 0.9

    def test_waist_hip_ratio_none_when_missing(self):
        """Test waist-to-hip ratio returns None when missing."""
        visit = Visit(HASTA_KABUL=1, MUAYENE_TURU=1)

        assert visit.waist_hip_ratio is None

    def test_blood_pressure_string_format(self):
        """Test blood pressure string formatting."""
        visit = Visit(
            HASTA_KABUL=1, MUAYENE_TURU=1, SISTOLIK_KAN_BASINCI=120, DIASTOLIK_KAN_BASINCI=80
        )

        bp_str = visit.blood_pressure_str
        assert bp_str == "120/80"

    def test_blood_pressure_string_none_when_missing(self):
        """Test blood pressure string returns None when missing."""
        visit = Visit(HASTA_KABUL=1, MUAYENE_TURU=1)

        assert visit.blood_pressure_str is None

    def test_visit_with_clinical_notes(self):
        """Test visit with clinical notes."""
        visit = Visit(
            HASTA_KABUL=1,
            MUAYENE_TURU=1,
            SIKAYETI="Headache and fever",
            HIKAYESI="History of migraines",
            BULGU="Elevated temperature",
            MUAYENE_NOT="Patient advised rest",
        )

        assert visit.SIKAYETI == "Headache and fever"
        assert visit.HIKAYESI == "History of migraines"
        assert visit.BULGU == "Elevated temperature"
        assert visit.MUAYENE_NOT == "Patient advised rest"

    def test_visit_with_emergency_info(self):
        """Test visit with emergency/disaster information."""
        visit = Visit(
            HASTA_KABUL=1,
            MUAYENE_TURU=1,
            OLAY_AFET_BILGISI="Earthquake victim",
            HAYATI_TEHLIKE_DURUMU=2,
            GLASGOW_KOMA_SKALASI=15,
        )

        assert visit.OLAY_AFET_BILGISI == "Earthquake victim"
        assert visit.HAYATI_TEHLIKE_DURUMU == 2
        assert visit.GLASGOW_KOMA_SKALASI == 15

    def test_visit_repr(self):
        """Test string representation."""
        visit = Visit(MUAYENE_ID=123, HASTA_KABUL=456, MUAYENE_TURU=1)

        repr_str = repr(visit)
        assert "Visit" in repr_str
        assert "123" in repr_str
        assert "456" in repr_str


class TestPatientAdmission:
    """Test suite for PatientAdmission model."""

    def test_patient_admission_creation(self):
        """Test creating a PatientAdmission instance."""
        admission = PatientAdmission(
            HASTA_KAYIT=1, KABUL_TARIHI=datetime(2024, 1, 15, 10, 30), KABUL_TURU=1, DURUM=1
        )

        assert admission.HASTA_KAYIT == 1
        assert admission.KABUL_TARIHI == datetime(2024, 1, 15, 10, 30)
        assert admission.KABUL_TURU == 1
        assert admission.DURUM == 1

    def test_patient_admission_with_physician(self):
        """Test admission with physician assigned."""
        admission = PatientAdmission(
            HASTA_KAYIT=1,
            KABUL_TARIHI=datetime(2024, 1, 15, 10, 30),
            KABUL_TURU=1,
            DURUM=1,
            HEKIM=123,
        )

        assert admission.HEKIM == 123

    def test_patient_admission_with_reason(self):
        """Test admission with reason for visit."""
        admission = PatientAdmission(
            HASTA_KAYIT=1,
            KABUL_TARIHI=datetime(2024, 1, 15, 10, 30),
            KABUL_TURU=1,
            DURUM=1,
            BASVURU_NEDENI=5,
        )

        assert admission.BASVURU_NEDENI == 5

    def test_patient_admission_repr(self):
        """Test string representation."""
        admission = PatientAdmission(
            HASTA_KABUL_ID=789,
            HASTA_KAYIT=456,
            KABUL_TARIHI=datetime(2024, 1, 15, 10, 30),
            KABUL_TURU=1,
            DURUM=1,
        )

        repr_str = repr(admission)
        assert "PatientAdmission" in repr_str
        assert "789" in repr_str
        assert "456" in repr_str

    def test_patient_admission_status_active(self):
        """Test admission with active status."""
        admission = PatientAdmission(
            HASTA_KAYIT=1,
            KABUL_TARIHI=datetime(2024, 1, 15, 10, 30),
            KABUL_TURU=1,
            DURUM=1,  # Active
        )

        assert admission.DURUM == 1

    def test_patient_admission_status_completed(self):
        """Test admission with completed status."""
        admission = PatientAdmission(
            HASTA_KAYIT=1,
            KABUL_TARIHI=datetime(2024, 1, 15, 10, 30),
            KABUL_TURU=1,
            DURUM=2,  # Completed
        )

        assert admission.DURUM == 2
