"""
Unit tests for Clinical Data models.
"""

import pytest
from datetime import datetime, date

from src.models.clinical import Prescription, Diagnosis


class TestPrescription:
    """Test suite for Prescription model."""

    def test_prescription_creation(self):
        """Test creating a Prescription instance."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            DURUM=1
        )

        assert prescription.HASTA_KAYIT == 1
        assert prescription.RECETE_TURU == 1
        assert prescription.RECETE_TARIHI == datetime(2024, 1, 15, 14, 30)
        assert prescription.DURUM == 1

    def test_prescription_with_visit(self):
        """Test prescription linked to a visit."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            MUAYENE=123,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            DURUM=1
        )

        assert prescription.MUAYENE == 123

    def test_prescription_with_prescription_number(self):
        """Test prescription with prescription number."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            RECETE_NO="RX-2024-001",
            DURUM=1
        )

        assert prescription.RECETE_NO == "RX-2024-001"

    def test_prescription_with_physician(self):
        """Test prescription with physician ID."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            HEKIM=456,
            DURUM=1
        )

        assert prescription.HEKIM == 456

    def test_prescription_with_diagnosis(self):
        """Test prescription with diagnosis code."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            TANI=110,  # ICD-10 code
            DURUM=1
        )

        assert prescription.TANI == 110

    def test_prescription_with_notes(self):
        """Test prescription with notes/instructions."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            ACIKLAMA="Take with food, avoid alcohol",
            DURUM=1
        )

        assert prescription.ACIKLAMA == "Take with food, avoid alcohol"

    def test_prescription_with_esy_number(self):
        """Test prescription with E-Health System number."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            ESY_RECETE_NO="ESY-2024-12345",
            DURUM=1
        )

        assert prescription.ESY_RECETE_NO == "ESY-2024-12345"

    def test_prescription_status_active(self):
        """Test prescription with active status."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            DURUM=1  # Active
        )

        assert prescription.DURUM == 1

    def test_prescription_status_cancelled(self):
        """Test prescription with cancelled status."""
        prescription = Prescription(
            HASTA_KAYIT=1,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            DURUM=2  # Cancelled
        )

        assert prescription.DURUM == 2

    def test_prescription_repr(self):
        """Test string representation."""
        prescription = Prescription(
            RECETE_ID=789,
            HASTA_KAYIT=456,
            RECETE_TURU=1,
            RECETE_TARIHI=datetime(2024, 1, 15, 14, 30),
            DURUM=1
        )

        repr_str = repr(prescription)
        assert "Prescription" in repr_str
        assert "789" in repr_str
        assert "456" in repr_str


class TestDiagnosis:
    """Test suite for Diagnosis model."""

    def test_diagnosis_creation(self):
        """Test creating a Diagnosis instance."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,  # ICD-10 code
            DURUM=1
        )

        assert diagnosis.MUAYENE == 1
        assert diagnosis.TANI == 110
        assert diagnosis.DURUM == 1

    def test_diagnosis_with_type(self):
        """Test diagnosis with type specified."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            TANI_TURU=2,  # Secondary diagnosis
            DURUM=1
        )

        assert diagnosis.TANI_TURU == 2

    def test_diagnosis_with_description(self):
        """Test diagnosis with description/notes."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            TANI_ACIKLAMA="Chronic hypertension, well controlled",
            DURUM=1
        )

        assert diagnosis.TANI_ACIKLAMA == "Chronic hypertension, well controlled"

    def test_diagnosis_with_severity(self):
        """Test diagnosis with severity level."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            SIDDET=3,  # Severity level 3
            DURUM=1
        )

        assert diagnosis.SIDDET == 3

    def test_diagnosis_with_date(self):
        """Test diagnosis with diagnosis date."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            TANI_TARIHI=date(2024, 1, 15),
            DURUM=1
        )

        assert diagnosis.TANI_TARIHI == date(2024, 1, 15)

    def test_diagnosis_is_active_true(self):
        """Test is_active property returns True for active diagnosis."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            DURUM=1  # Active
        )

        assert diagnosis.is_active is True

    def test_diagnosis_is_active_false(self):
        """Test is_active property returns False for resolved diagnosis."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            DURUM=2  # Resolved
        )

        assert diagnosis.is_active is False

    def test_diagnosis_status_active(self):
        """Test diagnosis with active status."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            DURUM=1  # Active
        )

        assert diagnosis.DURUM == 1

    def test_diagnosis_status_resolved(self):
        """Test diagnosis with resolved status."""
        diagnosis = Diagnosis(
            MUAYENE=1,
            TANI=110,
            DURUM=2  # Resolved
        )

        assert diagnosis.DURUM == 2

    def test_diagnosis_repr(self):
        """Test string representation."""
        diagnosis = Diagnosis(
            MUAYENE_EK_TANI_ID=123,
            MUAYENE=456,
            TANI=110,
            DURUM=1
        )

        repr_str = repr(diagnosis)
        assert "Diagnosis" in repr_str
        assert "123" in repr_str
        assert "456" in repr_str
        assert "110" in repr_str
