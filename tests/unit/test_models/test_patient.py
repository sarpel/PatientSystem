"""
Unit tests for Patient models.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock

from src.models.patient import Patient, PatientDemographics


class TestPatient:
    """Test suite for Patient model."""

    def test_patient_creation(self):
        """Test creating a Patient instance."""
        patient = Patient(
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            AD="Test",
            SOYAD="User",
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.AD == "Test"
        assert patient.SOYAD == "User"
        assert patient.HASTA_TIPI == 1

    def test_patient_full_name_property(self):
        """Test full_name property."""
        patient = Patient(
            AD="Ahmet",
            SOYAD="Yılmaz",
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.full_name == "Ahmet Yılmaz"

    def test_patient_age_calculation(self):
        """Test age calculation from birth date."""
        patient = Patient(
            AD="Test",
            SOYAD="User",
            DOGUM_TARIHI=date(1990, 1, 1),
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        age = patient.age
        assert age is not None
        assert age >= 30  # Should be at least 30 years old

    def test_patient_age_none_when_no_birth_date(self):
        """Test age returns None when no birth date."""
        patient = Patient(
            AD="Test",
            SOYAD="User",
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.age is None

    def test_patient_is_deceased_false(self):
        """Test is_deceased property returns False when no death date."""
        patient = Patient(
            AD="Test",
            SOYAD="User",
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.is_deceased is False

    def test_patient_is_deceased_true(self):
        """Test is_deceased property returns True when death date exists."""
        patient = Patient(
            AD="Test",
            SOYAD="User",
            OLUM_TARIHI=date(2023, 1, 1),
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.is_deceased is True

    def test_patient_repr(self):
        """Test string representation."""
        patient = Patient(
            HASTA_KAYIT_ID=123,
            AD="Test",
            SOYAD="User",
            HASTA_KIMLIK_NO=12345678901,
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        repr_str = repr(patient)
        assert "Patient" in repr_str
        assert "123" in repr_str
        assert "Test" in repr_str

    def test_patient_with_foreign_nationality(self):
        """Test patient with foreign nationality."""
        patient = Patient(
            AD="John",
            SOYAD="Doe",
            UYRUK="US",
            YABANCI_HASTA_TURU=1,
            PASAPORT_NO="AB123456",
            HASTA_TIPI=1,
            HASTA_KAYIT_TURU=1,
            CINSIYET=1,
            CINSIYET_RESMI=1
        )

        assert patient.UYRUK == "US"
        assert patient.PASAPORT_NO == "AB123456"


class TestPatientDemographics:
    """Test suite for PatientDemographics model."""

    def test_patient_demographics_creation(self):
        """Test creating a PatientDemographics instance."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,  # 70kg in grams
            BOY=175  # 175cm
        )

        assert demographics.HASTA_KAYIT == 1
        assert demographics.AGIRLIK == 70000
        assert demographics.BOY == 175

    def test_bmi_calculation(self):
        """Test BMI calculation."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,  # 70kg
            BOY=175  # 175cm = 1.75m
        )

        bmi = demographics.bmi
        assert bmi is not None
        # BMI = 70 / (1.75^2) = 22.86
        assert 22 < bmi < 23

    def test_bmi_none_when_no_weight(self):
        """Test BMI returns None when weight is missing."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=0,
            BOY=175
        )

        assert demographics.bmi is None

    def test_bmi_none_when_no_height(self):
        """Test BMI returns None when height is missing."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,
            BOY=0
        )

        assert demographics.bmi is None

    def test_bmi_category_underweight(self):
        """Test BMI category for underweight."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=50000,  # 50kg
            BOY=175  # 175cm
        )

        assert demographics.bmi_category == "Underweight"

    def test_bmi_category_normal(self):
        """Test BMI category for normal weight."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,  # 70kg
            BOY=175  # 175cm
        )

        assert demographics.bmi_category == "Normal"

    def test_bmi_category_overweight(self):
        """Test BMI category for overweight."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=85000,  # 85kg
            BOY=175  # 175cm
        )

        assert demographics.bmi_category == "Overweight"

    def test_bmi_category_obese(self):
        """Test BMI category for obese."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=100000,  # 100kg
            BOY=175  # 175cm
        )

        assert demographics.bmi_category == "Obese"

    def test_bmi_category_none_when_no_bmi(self):
        """Test BMI category returns None when BMI cannot be calculated."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=0,
            BOY=0
        )

        assert demographics.bmi_category is None

    def test_patient_demographics_repr(self):
        """Test string representation."""
        demographics = PatientDemographics(
            HASTA_OZLUK_ID=456,
            HASTA_KAYIT=123,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,
            BOY=175
        )

        repr_str = repr(demographics)
        assert "PatientDemographics" in repr_str
        assert "456" in repr_str
        assert "123" in repr_str

    def test_lifestyle_fields(self):
        """Test lifestyle-related fields."""
        demographics = PatientDemographics(
            HASTA_KAYIT=1,
            SOSYAL_GUVENCE=1,
            AGIRLIK=70000,
            BOY=175,
            SIGARA_KULLANIMI=1,
            SIGARA_ADEDI=10,
            ALKOL_KULLANIMI=2,
            MADDE_KULLANIMI=3
        )

        assert demographics.SIGARA_KULLANIMI == 1
        assert demographics.SIGARA_ADEDI == 10
        assert demographics.ALKOL_KULLANIMI == 2
        assert demographics.MADDE_KULLANIMI == 3
