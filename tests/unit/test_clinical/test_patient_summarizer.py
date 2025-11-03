"""
Tests for Patient Summarizer module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from src.clinical.patient_summarizer import PatientSummarizer
from src.models.patient import Patient, PatientDemographics
from src.models.visit import Visit, PatientAdmission
from src.models.clinical import Prescription, Diagnosis


class TestPatientSummarizer:
    """Test suite for PatientSummarizer class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def patient_summarizer(self, mock_session):
        """Create PatientSummarizer instance."""
        return PatientSummarizer(mock_session)

    @pytest.fixture
    def sample_patient(self):
        """Create sample patient object."""
        patient = Mock(spec=Patient)
        patient.HASTA_KAYIT_ID = 12345
        patient.full_name = "Test Patient"
        patient.DOGUM_TARIHI = datetime(1980, 1, 1)
        patient.age = 44
        patient.CINSIYET = 1
        patient.TC_KIMLIK_NO = "12345678901"
        patient.KAN_GRUBU = "A+"
        patient.is_deceased = False
        patient.ILAC_ALERJISI = None
        return patient

    @pytest.fixture
    def sample_demographics(self):
        """Create sample patient demographics."""
        demographics = Mock(spec=PatientDemographics)
        demographics.AGIRLIK = 75000  # 75 kg
        demographics.BOY = 175  # 175 cm
        demographics.bmi = 24.5
        demographics.bmi_category = "Normal"
        demographics.SIGARA = 0  # Non-smoker
        demographics.ALKOL_KULLANIMI = 0  # No alcohol
        demographics.ILAC_ALERJISI = None
        return demographics

    @pytest.fixture
    def sample_visits(self):
        """Create sample visit data."""
        visits = []
        for i in range(3):
            visit = Mock(spec=Visit)
            visit.MUAYENE_ID = 1000 + i
            visit.HASTA_KABUL = 500 + i
            visit.MUAYENE_TURU = "Routine"
            visit.ANA_TANI = f"Diagnosis {i+1}"
            visit.SIKAYETI = f"Complaint {i+1}"
            visit.SISTOLIK_KAN_BASINCI = 120 + i * 5
            visit.DIASTOLIK_KAN_BASINCI = 80 + i * 3
            visit.NABIZ = 70 + i * 2
            visit.VUCUT_ISISI = 36.5 + i * 0.2
            visit.AGIRLIK = 73000 + i * 500
            visit.BOY = 175
            visit.blood_pressure_str = f"{120 + i * 5}/{80 + i * 3}"
            visit.bmi = (73000 + i * 500) / 1000 / ((175 / 100) ** 2)
            visit.BEL_CEVRESI = 85 + i
            visit.KALCA_CEVRESI = 95 + i
            visit.waist_hip_ratio = (85 + i) / (95 + i)
            visit.GLASGOW_KOMA_SKALASI = 15
            visits.append(visit)
        return visits

    @pytest.fixture
    def sample_prescriptions(self):
        """Create sample prescription data."""
        prescriptions = []
        drug_names = ["Metformin", "Lisinopril", "Atorvastatin"]
        for i, drug in enumerate(drug_names):
            rx = Mock(spec=Prescription)
            rx.RECETE_ID = 2000 + i
            rx.MUAYENE = 1000 + i
            rx.RECETE_TURU = "Chronic"
            rx.RECETE_TARIHI = datetime.now() - timedelta(days=i * 30)
            rx.RECETE_NO = f"RX-{2000 + i}"
            rx.HEKIM = 100
            rx.TANI = "Type 2 Diabetes"
            rx.ACIKLAMA = drug
            rx.ESY_RECETE_NO = f"ESY-{i}"
            rx.DURUM = 1  # Active
            prescriptions.append(rx)
        return prescriptions

    @pytest.fixture
    def sample_diagnoses(self):
        """Create sample diagnosis data."""
        diagnoses = []
        diagnosis_names = ["Type 2 Diabetes", "Hypertension", "Hyperlipidemia"]
        for i, name in enumerate(diagnosis_names):
            dx = Mock(spec=Diagnosis)
            dx.MUAYENE_EK_TANI_ID = 3000 + i
            dx.MUAYENE = 1000 + i
            dx.TANI = i + 1
            dx.TANI_TURU = "Primary"
            dx.TANI_ACIKLAMA = name
            dx.SIDDET = 1
            dx.TANI_TARIHI = datetime.now() - timedelta(days=i * 90)
            dx.DURUM = 1  # Active
            dx.is_active = True
            diagnoses.append(dx)
        return diagnoses

    def test_init(self, mock_session):
        """Test PatientSummarizer initialization."""
        summarizer = PatientSummarizer(mock_session)
        assert summarizer.session == mock_session

    def test_get_patient_summary_success(
        self,
        patient_summarizer,
        mock_session,
        sample_patient,
        sample_demographics,
        sample_visits,
        sample_prescriptions,
        sample_diagnoses
    ):
        """Test successful patient summary generation."""
        # Setup mocks
        sample_patient.demographics = sample_demographics

        # Mock _get_patient
        with patch.object(patient_summarizer, '_get_patient', return_value=sample_patient):
            # Mock other methods
            with patch.object(patient_summarizer, '_get_demographics') as mock_demo:
                with patch.object(patient_summarizer, '_get_recent_visits') as mock_visits:
                    with patch.object(patient_summarizer, '_get_active_diagnoses') as mock_dx:
                        with patch.object(patient_summarizer, '_get_active_prescriptions') as mock_rx:
                            with patch.object(patient_summarizer, '_get_allergies') as mock_allergies:
                                with patch.object(patient_summarizer, '_get_latest_vitals') as mock_vitals:
                                    with patch.object(patient_summarizer, '_get_summary_stats') as mock_stats:
                                        # Setup return values
                                        mock_demo.return_value = {"test": "demographics"}
                                        mock_visits.return_value = [{"test": "visit"}]
                                        mock_dx.return_value = [{"test": "diagnosis"}]
                                        mock_rx.return_value = [{"test": "prescription"}]
                                        mock_allergies.return_value = []
                                        mock_vitals.return_value = {"test": "vitals"}
                                        mock_stats.return_value = {"test": "stats"}

                                        # Call method
                                        result = patient_summarizer.get_patient_summary(12345)

                                        # Assertions
                                        assert result["demographics"] == {"test": "demographics"}
                                        assert result["recent_visits"] == [{"test": "visit"}]
                                        assert result["active_diagnoses"] == [{"test": "diagnosis"}]
                                        assert result["active_prescriptions"] == [{"test": "prescription"}]
                                        assert result["allergies"] == []
                                        assert result["latest_vitals"] == {"test": "vitals"}
                                        assert result["summary_stats"] == {"test": "stats"}

    def test_get_patient_summary_patient_not_found(self, patient_summarizer):
        """Test patient summary when patient not found."""
        with patch.object(patient_summarizer, '_get_patient', return_value=None):
            with pytest.raises(ValueError, match="Patient 12345 not found"):
                patient_summarizer.get_patient_summary(12345)

    def test_get_patient(self, patient_summarizer, mock_session, sample_patient):
        """Test _get_patient method."""
        # Setup mock
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_patient

        # Call method
        result = patient_summarizer._get_patient(12345)

        # Assertions
        assert result == sample_patient
        mock_session.execute.assert_called_once()

    def test_get_demographics(self, patient_summarizer, sample_patient, sample_demographics):
        """Test _get_demographics method."""
        # Setup patient with and without demographics
        sample_patient.demographics = sample_demographics

        # Call method
        result = patient_summarizer._get_demographics(sample_patient)

        # Assertions
        assert result["patient_id"] == 12345
        assert result["full_name"] == "Test Patient"
        assert result["age"] == 44
        assert result["gender"] == 1
        assert result["weight_kg"] == 75.0
        assert result["height_cm"] == 175
        assert result["bmi"] == 24.5
        assert result["smoking_status"] == 0

    def test_get_demographics_no_demographics(self, patient_summarizer, sample_patient):
        """Test _get_demographics without demographics."""
        sample_patient.demographics = None

        result = patient_summarizer._get_demographics(sample_patient)

        assert result["patient_id"] == 12345
        assert result["weight_kg"] is None
        assert result["height_cm"] is None
        assert result["bmi"] is None
        assert result["smoking_status"] is None

    def test_get_allergies_with_drug_allergy(self, patient_summarizer, sample_patient):
        """Test _get_allergies with drug allergy."""
        sample_patient.ILAC_ALERJISI = "Penicillin"
        sample_patient.demographics = None

        result = patient_summarizer._get_allergies(sample_patient)

        assert len(result) == 1
        assert "Drug allergy: Penicillin" in result

    def test_get_allergies_with_demographics_allergy(
        self,
        patient_summarizer,
        sample_patient,
        sample_demographics
    ):
        """Test _get_allergies with demographics allergy."""
        sample_patient.ILAC_ALERJISI = None
        sample_patient.demographics = sample_demographics
        sample_demographics.ILAC_ALERJISI = "Sulfa"

        result = patient_summarizer._get_allergies(sample_patient)

        assert len(result) == 1
        assert "Drug allergy (demographics): Sulfa" in result

    def test_get_allergies_no_allergies(self, patient_summarizer, sample_patient):
        """Test _get_allergies with no allergies."""
        sample_patient.ILAC_ALERJISI = None
        sample_patient.demographics = None

        result = patient_summarizer._get_allergies(sample_patient)

        assert len(result) == 0

    def test_get_latest_vitals(self, patient_summarizer, mock_session, sample_visits):
        """Test _get_latest_vitals method."""
        # Setup mock to return a single visit
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_visits[0]

        # Call method
        result = patient_summarizer._get_latest_vitals(12345)

        # Assertions
        assert result is not None
        assert result["blood_pressure_systolic"] == 120
        assert result["blood_pressure_diastolic"] == 80
        assert result["pulse"] == 70
        assert result["temperature_celsius"] == 36.5
        assert result["bmi"] is not None

    def test_get_latest_vitals_no_visits(self, patient_summarizer, mock_session):
        """Test _get_latest_vitals with no visits."""
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        result = patient_summarizer._get_latest_vitals(12345)

        assert result is None

    def test_get_formatted_summary(self, patient_summarizer):
        """Test formatted summary generation."""
        # Mock the summary data
        mock_summary = {
            "demographics": {
                "full_name": "Test Patient",
                "age": 44,
                "gender": 1,
                "bmi": 24.5,
                "bmi_category": "Normal"
            },
            "allergies": ["Drug allergy: Penicillin"],
            "latest_vitals": {
                "blood_pressure_str": "120/80",
                "pulse": 70,
                "temperature_celsius": 36.5,
                "bmi": 24.5
            },
            "summary_stats": {
                "recent_visit_count": 3,
                "active_diagnosis_count": 2,
                "active_prescription_count": 3
            }
        }

        with patch.object(patient_summarizer, 'get_patient_summary', return_value=mock_summary):
            # Call method
            result = patient_summarizer.get_formatted_summary(12345)

            # Assertions
            assert "PATIENT SUMMARY" in result
            assert "Test Patient" in result
            assert "44 years" in result
            assert "BMI: 24.5 (Normal)" in result
            assert "ALLERGIES:" in result
            assert "Drug allergy: Penicillin" in result
            assert "LATEST VITAL SIGNS:" in result
            assert "BP: 120/80 mmHg" in result
            assert "Pulse: 70 bpm" in result
            assert "SUMMARY (Last 12 months):" in result
            assert "Visits: 3" in result
            assert "Active Diagnoses: 2" in result
            assert "Active Prescriptions: 3" in result

    def test_get_formatted_summary_no_data(self, patient_summarizer):
        """Test formatted summary with minimal data."""
        mock_summary = {
            "demographics": {
                "full_name": "Test Patient",
                "age": 44,
                "gender": 1
            },
            "allergies": [],
            "latest_vitals": None,
            "summary_stats": {
                "recent_visit_count": 0,
                "active_diagnosis_count": 0,
                "active_prescription_count": 0
            }
        }

        with patch.object(patient_summarizer, 'get_patient_summary', return_value=mock_summary):
            result = patient_summarizer.get_formatted_summary(12345)

            assert "PATIENT SUMMARY" in result
            assert "Test Patient" in result
            assert "ALLERGIES:" not in result
            assert "LATEST VITAL SIGNS:" not in result
            assert "SUMMARY (Last 12 months):" in result

    def test_calculate_date_threshold(self, patient_summarizer):
        """Test internal date threshold calculation."""
        # This is tested indirectly through get_patient_summary
        with patch.object(patient_summarizer, '_get_patient') as mock_get_patient:
            mock_get_patient.return_value = Mock(spec=Patient)

            with patch.object(patient_summarizer, '_get_demographics') as mock_demo:
                with patch.object(patient_summarizer, '_get_recent_visits') as mock_visits:
                    with patch.object(patient_summarizer, '_get_active_diagnoses') as mock_dx:
                        with patch.object(patient_summarizer, '_get_active_prescriptions') as mock_rx:
                            with patch.object(patient_summarizer, '_get_allergies') as mock_allergies:
                                with patch.object(patient_summarizer, '_get_latest_vitals') as mock_vitals:
                                    with patch.object(patient_summarizer, '_get_summary_stats') as mock_stats:
                                        # Setup all mocks to return empty data
                                        mock_demo.return_value = {}
                                        mock_visits.return_value = []
                                        mock_dx.return_value = []
                                        mock_rx.return_value = []
                                        mock_allergies.return_value = []
                                        mock_vitals.return_value = None
                                        mock_stats.return_value = {}

                                        # Test with 6 months
                                        patient_summarizer.get_patient_summary(12345, months_back=6)

                                        # The threshold date should be used in _get_recent_visits and _get_summary_stats
                                        assert mock_visits.called
                                        assert mock_stats.called

    def test_edge_case_patient_with_no_data(self, patient_summarizer):
        """Test handling of patient with minimal data."""
        # Create a minimal patient object
        minimal_patient = Mock(spec=Patient)
        minimal_patient.HASTA_KAYIT_ID = 12345
        minimal_patient.full_name = "Minimal Patient"
        minimal_patient.DOGUM_TARIHI = None
        minimal_patient.age = None
        minimal_patient.CINSIYET = None
        minimal_patient.ILAC_ALERJISI = None

        with patch.object(patient_summarizer, '_get_patient', return_value=minimal_patient):
            result = patient_summarizer.get_patient_summary(12345)

            assert "demographics" in result
            assert result["demographics"]["full_name"] == "Minimal Patient"
            assert result["demographics"]["age"] is None
            assert result["allergies"] == []