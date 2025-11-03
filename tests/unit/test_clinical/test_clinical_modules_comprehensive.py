"""
Comprehensive tests for Diagnosis Engine, Treatment Engine, and Drug Interaction Checker modules.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.clinical.diagnosis_engine import (
    DiagnosisEngine, DiagnosisSuggestion, DiagnosisContext
)
from src.clinical.treatment_engine import (
    TreatmentEngine, MedicationRecommendation, InteractionSeverity
)
from src.clinical.drug_interaction import (
    DrugInteractionChecker, DrugInteraction, InteractionSeverity as DrugInteractionSeverity,
    AllergyWarning, InteractionResult
)


class TestDiagnosisEngine:
    """Test suite for DiagnosisEngine class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session

    @pytest.fixture
    def diagnosis_engine(self, mock_session):
        """Create DiagnosisEngine instance."""
        return DiagnosisEngine(mock_session, ai_router=None)

    @pytest.fixture
    def sample_patient_context(self):
        """Create sample patient context."""
        return {
            "patient_id": 12345,
            "age": 55,
            "gender": 1,
            "bmi": 28.5,
            "smoking_status": "former",
            "allergies": None,
            "current_medications": ["Metformin"],
            "comorbidities": ["Hypertension"],
        }

    def test_init(self, mock_session):
        """Test DiagnosisEngine initialization."""
        engine = DiagnosisEngine(mock_session)
        assert engine.session == mock_session
        assert isinstance(engine._icd10_mapping, dict)
        assert isinstance(engine._red_flag_patterns, list)

    def test_generate_differential_diagnosis_rule_based(
        self,
        diagnosis_engine,
        sample_patient_context
    ):
        """Test rule-based differential diagnosis generation."""
        complaints = ["göğüs ağrısı", "nefes darlığı"]

        # Mock patient context building
        with patch.object(diagnosis_engine, '_build_diagnosis_context', return_value=sample_patient_context):
            result = diagnosis_engine.generate_differential_diagnosis(
                patient_id=12345,
                chief_complaints=complaints,
                vital_signs={"BP": "150/90", "HR": 95},
                physical_exam={"chest_clear": True},
                lab_results={"Troponin": 0.5}
            )

            # Verify structure
            assert "differential_diagnosis" in result
            assert "urgent_conditions" in result
            assert "recommended_tests" in result
            assert "confidence_score" in result

            # Should have chest pain and breathing difficulty suggestions
            diagnoses = [d["diagnosis"] for d in result["differential_diagnosis"]]
            assert any("Chest" in d or "Angina" in d for d in diagnoses)

    def test_analyze_complaint_chest_pain(self, diagnosis_engine, sample_patient_context):
        """Test chest pain complaint analysis."""
        suggestions = diagnosis_engine._analyze_complaint("göğüs ağrısı", sample_patient_context)

        assert len(suggestions) > 0
        chest_pain_diagnoses = [s.diagnosis for s in suggestions]
        assert any("Angina" in d or "Chest" in d for d in chest_pain_diagnoses)

    def test_analyze_complaint_headache(self, diagnosis_engine, sample_patient_context):
        """Test headache complaint analysis."""
        suggestions = diagnosis_engine._analyze_complaint("baş ağrısı", sample_patient_context)

        assert len(suggestions) > 0
        headache_diagnoses = [s.diagnosis for s in suggestions]
        assert any("Headache" in d or "Migraine" in d for d in headache_diagnoses)

    def test_analyze_vital_signs_hypertension(self, diagnosis_engine, sample_patient_context):
        """Test vital sign analysis for hypertension."""
        vital_signs = {"systolic": 150, "diastolic": 95, "heart_rate": 80}
        suggestions = diagnosis_engine._analyze_vital_signs(vital_signs, sample_patient_context)

        assert len(suggestions) > 0
        hypertension_diagnoses = [s.diagnosis for s in suggestions]
        assert any("Hypertension" in d for d in hypertension_diagnoses)

    def test_analyze_lab_results_diabetes(self, diagnosis_engine, sample_patient_context):
        """Test lab result analysis for diabetes."""
        lab_results = {"HbA1c": 7.5, "Fasting Glucose": 155}
        suggestions = diagnosis_engine._analyze_lab_results(lab_results, sample_patient_context)

        assert len(suggestions) > 0
        diabetes_diagnoses = [s.diagnosis for s in suggestions]
        assert any("Diabetes" in d for d in diabetes_diagnoses)

    def test_detect_red_flags_chest_pain(self, diagnosis_engine):
        """Test red flag detection for chest pain."""
        context = DiagnosisContext(
            patient_info={},
            chief_complaints=["göğüs ağrısı ve terleme"],
            vital_signs={},
            physical_exam={},
            lab_results={},
            past_diagnoses=[],
            medications=[],
            demographics={}
        )

        red_flags = diagnosis_engine._detect_red_flags(context)
        assert len(red_flags) > 0
        assert any("chest pain" in flag.lower() for flag in red_flags)

    def test_get_diagnosis_report(self, diagnosis_engine):
        """Test formatted diagnosis report generation."""
        mock_result = {
            "differential_diagnosis": [
                {
                    "diagnosis": "Acute Coronary Syndrome",
                    "icd10": "I21.9",
                    "probability": 0.75,
                    "reasoning": "Chest pain with risk factors",
                    "urgency": "urgent"
                }
            ],
            "urgent_conditions": [
                {
                    "diagnosis": "Acute Coronary Syndrome",
                    "icd10": "I21.9",
                    "urgency": "urgent"
                }
            ],
            "red_flags": ["Chest pain requires immediate attention"],
            "recommended_tests": ["EKG", "Troponin", "Chest X-ray"],
            "confidence_score": 0.75,
            "analysis_timestamp": datetime.now().isoformat()
        }

        report = diagnosis_engine.get_diagnosis_report(12345, mock_result)

        assert "DIFFERENTIAL DIAGNOSIS REPORT" in report
        assert "Acute Coronary Syndrome" in report
        assert "I21.9" in report
        assert "Probability: 75.0%" in report
        assert "🚨 URGENT CONDITIONS 🚨" in report
        assert "⚠️ RED FLAGS" in report
        assert "RECOMMENDED INVESTIGATIONS" in report


class TestTreatmentEngine:
    """Test suite for TreatmentEngine class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session

    @pytest.fixture
    def treatment_engine(self, mock_session):
        """Create TreatmentEngine instance."""
        return TreatmentEngine(mock_session, ai_router=None)

    @pytest.fixture
    def sample_patient_context(self):
        """Create sample patient context."""
        return {
            "patient_id": 12345,
            "age": 65,
            "gender": 1,
            "bmi": 32.0,
            "egfr": 45,
            "allergies": None,
            "current_medications": ["Metformin"],
            "comorbidities": ["Hypertension", "Type 2 Diabetes"],
            "smoking_status": "former",
        }

    def test_init(self, mock_session):
        """Test TreatmentEngine initialization."""
        engine = TreatmentEngine(mock_session)
        assert engine.session == mock_session
        assert isinstance(engine._drug_database, dict)
        assert isinstance(engine._treatment_guidelines, dict)

    def test_generate_treatment_plan_diabetes(self, treatment_engine, sample_patient_context):
        """Test treatment plan generation for Type 2 Diabetes."""
        # Mock patient context building
        with patch.object(treatment_engine, '_build_patient_context', return_value=sample_patient_context):
            result = treatment_engine.generate_treatment_plan(
                patient_id=12345,
                diagnosis="Type 2 Diabetes",
                patient_factors={"duration": "5 years", "complications": None}
            )

            # Verify structure
            assert "pharmacological" in result
            assert "lifestyle" in result
            assert "monitoring" in result
            assert "consultations" in result
            assert "contraindications" in result

            # Should include Metformin as first-line
            medications = [m["drug_name"] for m in result["pharmacological"]]
            assert "Metformin" in medications

            # Should include lifestyle recommendations
            lifestyle_categories = [r["category"] for r in result["lifestyle"]]
            assert any("diet" in cat or "exercise" in cat for cat in lifestyle_categories)

    def test_generate_treatment_plan_hypertension(self, treatment_engine, sample_patient_context):
        """Test treatment plan generation for Hypertension."""
        with patch.object(treatment_engine, '_build_patient_context', return_value=sample_patient_context):
            result = treatment_engine.generate_treatment_plan(
                patient_id=12345,
                diagnosis="Hypertension"
            )

            # Should include antihypertensive medications
            medications = [m["drug_name"] for m in result["pharmacological"]]
            assert any(ace in " ".join(medications) for ace in ["ACEi", "ARB", "Lisinopril"])

    def test_check_contraindications_renal_impairment(self, treatment_engine):
        """Test contraindication checking for renal impairment."""
        patient_context = {
            "age": 70,
            "egfr": 25,  # Severe renal impairment
            "allergies": None,
            "current_medications": []
        }

        treatment_result = {
            "pharmacological": [
                {
                    "drug_name": "Metformin",
                    "generic_name": "Metformin HCl",
                    "contraindications": ["eGFR <30 mL/min"]
                }
            ],
            "lifestyle": [],
            "monitoring": [],
            "consultations": [],
            "contraindications": []
        }

        result = treatment_engine._check_contraindications(treatment_result, patient_context)

        # Should identify Metformin contraindication
        assert len(result["contraindications"]) > 0
        assert any("Metformin" in str(contraindication) for contraindication in result["contraindications"])

        # Should filter out contraindicated medications
        filtered_meds = [m["drug_name"] for m in result["pharmacological"]]
        assert "Metformin" not in filtered_meds

    def test_check_drug_interaction_warfarin_nsaid(self, treatment_engine):
        """Test warfarin + NSAID interaction detection."""
        interaction = treatment_engine._check_drug_interaction("Warfarin", "Ibuprofen")
        assert interaction is not None
        assert "bleeding" in interaction.lower()

    def test_create_medication_recommendation(self, treatment_engine, sample_patient_context):
        """Test medication recommendation creation."""
        drug_info = {
            "generic_name": "Metformin HCl",
            "typical_dosage": "500mg 2x1",
            "contraindications": ["eGFR <30", "lactic acidosis"],
            "monitoring": ["Renal function", "B12"],
            "cost": "Low",
            "mechanism": "Decreases hepatic glucose production",
            "pregnancy_category": "B"
        }

        recommendation = treatment_engine._create_medication_recommendation("Metformin", drug_info, sample_patient_context)

        assert recommendation.drug_name == "Metformin"
        assert recommendation.generic_name == "Metformin HCl"
        assert recommendation.dosage == "500mg 2x1"
        assert recommendation.duration == "sürekli"
        assert recommendation.route == "oral"
        assert recommendation.priority == 1

    def test_get_treatment_report(self, treatment_engine):
        """Test formatted treatment report generation."""
        mock_result = {
            "pharmacological": [
                {
                    "drug_name": "Metformin",
                    "generic_name": "Metformin HCl",
                    "dosage": "500mg 2x1",
                    "frequency": "2x1",
                    "duration": "sürekli",
                    "route": "oral",
                    "rationale": "First-line for T2DM",
                    "priority": 1
                }
            ],
            "lifestyle": [
                {
                    "category": "diet",
                    "recommendation": "Weight loss",
                    "details": "5-10% weight loss",
                    "priority": 1
                }
            ],
            "monitoring": [
                {
                    "test_name": "HbA1c",
                    "frequency": "3 ayda bir",
                    "target_range": "<7.0%"
                }
            ],
            "consultations": [],
            "contraindications": [],
            "follow_up": {
                "schedule": "3 months",
                "what_to_monitor": "Symptoms, side effects"
            }
        }

        report = treatment_engine.get_treatment_report(mock_result)

        assert "TREATMENT PLAN" in report
        assert "PHARMACOLOGICAL TREATMENT" in report
        assert "Metformin (Metformin HCl)" in report
        assert "LIFESTYLE MODIFICATIONS" in report
        assert "Weight loss" in report
        assert "MONITORING PLAN" in report
        assert "HbA1c" in report
        assert "FOLLOW-UP" in report


class TestDrugInteractionChecker:
    """Test suite for DrugInteractionChecker class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session

    @pytest.fixture
    def interaction_checker(self, mock_session):
        """Create DrugInteractionChecker instance."""
        return DrugInteractionChecker(mock_session, ai_router=None)

    def test_init(self, mock_session):
        """Test DrugInteractionChecker initialization."""
        checker = DrugInteractionChecker(mock_session)
        assert checker.session == mock_session
        assert isinstance(checker._interaction_database, dict)
        assert isinstance(checker._allergy_database, dict)

    def test_check_drug_interactions_warfarin_nsaid(self, interaction_checker):
        """Test checking warfarin + NSAID interaction."""
        result = interaction_checker.check_drug_interactions(
            patient_id=12345,
            medications=["Warfarin", "Ibuprofen"],
            patient_allergies=[]
        )

        assert result.patient_id == 12345
        assert len(result.interactions) > 0
        assert result.requires_pharmacist_review

        # Should detect major interaction
        warfarin_interaction = [i for i in result.interactions
                               if "Warfarin" in i.drug1 and "Ibuprofen" in i.drug2]
        assert len(warfarin_interaction) > 0
        assert warfarin_interaction[0].severity == DrugInteractionSeverity.MAJOR

    def test_check_drug_interactions_acei_potassium(self, interaction_checker):
        """Test checking ACE inhibitor + potassium interaction."""
        result = interaction_checker.check_drug_interactions(
            patient_id=12345,
            medications=["Lisinopril", "Potassium Chloride"],
            patient_allergies=[]
        )

        # Should detect major interaction
        acei_interaction = [i for i in result.interactions
                           if "Lisinopril" in i.drug1 and "Potassium" in i.drug2]
        assert len(acei_interaction) > 0
        assert acei_interaction[0].severity == DrugInteractionSeverity.MAJOR

    def test_check_allergies_penicillin(self, interaction_checker):
        """Test checking penicillin allergy."""
        result = interaction_checker.check_drug_interactions(
            patient_id=12345,
            medications=["Amoxicillin"],
            patient_allergies=["Penicillin"]
        )

        assert len(result.allergy_warnings) > 0
        assert result.allergy_warnings[0].severity == "CRITICAL"
        assert "Penicillin" in result.allergy_warnings[0].allergen

    def test_check_allergies_cross_reactivity(self, interaction_checker):
        """Test checking allergy cross-reactivity."""
        result = interaction_checker.check_drug_interactions(
            patient_id=12345,
            medications=["Sulfamethoxazole"],  # Bactrim
            patient_allergies=["Sulfa drugs"]
        )

        assert len(result.allergy_warnings) > 0
        assert any("Cross-reactivity" in warning.clinical_significance
                  for warning in result.allergy_warnings)

    def test_normalize_drug_name(self, interaction_checker):
        """Test drug name normalization."""
        # Test synonym mapping
        assert interaction_checker._normalize_drug_name("Advil") == "Ibuprofen"
        assert interaction_checker._normalize_drug_name("Tylenol") == "Acetaminophen"
        assert interaction_checker._normalize_drug_name("Zestril") == "Lisinopril"

        # Test case normalization
        assert interaction_checker._normalize_drug_name("metformin") == "Metformin"
        assert interaction_checker._normalize_drug_name("IBUPROFEN") == "Ibuprofen"

    def test_class_interactions_acei_nsaid(self, interaction_checker):
        """Test class-based ACE inhibitor + NSAID interaction."""
        interactions = interaction_checker._check_class_interactions("Lisinopril", "Ibuprofen")
        assert len(interactions) > 0
        assert interactions[0].severity == DrugInteractionSeverity.MAJOR
        assert "triple whammy" in interactions[0].description.lower()

    def test_generate_recommendations(self, interaction_checker):
        """Test recommendation generation."""
        interactions = [
            DrugInteraction(
                drug1="Warfarin", drug2="Ibuprofen",
                severity=DrugInteractionSeverity.MAJOR,
                description="Increased bleeding risk",
                clinical_effect="Bleeding",
                management="Avoid combination",
                evidence_level="High"
            ),
            DrugInteraction(
                drug1="Metformin", drug2="Contrast",
                severity=DrugInteractionSeverity.CONTRAINDICATED,
                description="Lactic acidosis risk",
                clinical_effect="Lactic acidosis",
                management="Stop before procedure",
                evidence_level="High"
            )
        ]

        recommendations = interaction_checker._generate_recommendations(interactions, [])

        assert len(recommendations) > 0
        assert any("CONTRAINDICATED" in rec for rec in recommendations)
        assert any("Major drug interactions" in rec for rec in recommendations)

    def test_requires_pharmacist_review_true(self, interaction_checker):
        """Test pharmacist review requirement with major interactions."""
        interactions = [
            DrugInteraction("Drug1", "Drug2", DrugInteractionSeverity.MAJOR, "", "", "", "")
        ]

        assert interaction_checker._requires_pharmacist_review(interactions) == True

    def test_requires_pharmacist_review_false(self, interaction_checker):
        """Test pharmacist review requirement with minor interactions."""
        interactions = [
            DrugInteraction("Drug1", "Drug2", DrugInteractionSeverity.MINOR, "", "", "", "")
        ]

        assert interaction_checker._requires_pharmacist_review(interactions) == False

    def test_get_interaction_report(self, interaction_checker):
        """Test formatted interaction report generation."""
        mock_result = InteractionResult(
            patient_id=12345,
            interactions=[
                DrugInteraction(
                    drug1="Warfarin", drug2="Ibuprofen",
                    severity=DrugInteractionSeverity.MAJOR,
                    description="Increased bleeding risk",
                    clinical_effect="Bleeding",
                    management="Avoid combination",
                    evidence_level="High"
                )
            ],
            allergy_warnings=[
                AllergyWarning(
                    drug_name="Amoxicillin",
                    allergen="Penicillin",
                    severity="CRITICAL",
                    clinical_significance="Direct allergy"
                )
            ],
            safe_alternatives=["Acetaminophen"],
            recommendations=["Avoid warfarin + NSAID combination"],
            requires_pharmacist_review=True
        )

        report = interaction_checker.get_interaction_report(mock_result)

        assert "DRUG INTERACTION ANALYSIS REPORT" in report
        assert "Patient ID: 12345" in report
        assert "⚠️ ALLERGY WARNINGS ⚠️" in report
        assert "Amoxicillin" in report
        assert "🔶 MAJOR INTERACTIONS 🔶" in report
        assert "Warfarin + Ibuprofen" in report
        assert "💡 SAFE ALTERNATIVES 💡" in report
        assert "Acetaminophen" in report
        assert "🏥 PHARMACIST REVIEW REQUIRED 🏥" in report

    def test_get_patient_allergies(self, interaction_checker, mock_session):
        """Test getting patient allergies from database."""
        mock_patient = Mock()
        mock_patient.ILAC_ALERJISI = "Penicillin"
        mock_patient.demographics = Mock()
        mock_patient.demographics.ILAC_ALERJISI = None

        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_patient

        allergies = interaction_checker._get_patient_allergies(12345)

        assert len(allergies) == 1
        assert "Penicillin" in allergies

    def test_edge_case_empty_medications(self, interaction_checker):
        """Test interaction checking with empty medication list."""
        result = interaction_checker.check_drug_interactions(
            patient_id=12345,
            medications=[],
            patient_allergies=[]
        )

        assert result.patient_id == 12345
        assert len(result.interactions) == 0
        assert len(result.allergy_warnings) == 0
        assert result.requires_pharmacist_review == False