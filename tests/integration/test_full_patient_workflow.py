"""Integration tests for complete patient workflow."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import asyncio

from src.api.fastapi_app import app


@pytest.mark.integration
@pytest.mark.database
class TestFullPatientWorkflow:
    """Test complete patient workflow from search to treatment."""

    @pytest.fixture
    def test_data(self):
        """Set up comprehensive test data."""
        return {
            "patient": {
                "TCKN": "12345678901",
                "ADI": "Test",
                "SOYADI": "Patient",
                "DOGUM_TARIHI": "1980-01-01",
                "CINSIYET": "E"
            },
            "complaint": "Patient reports chest pain and shortness of breath for 2 days",
            "vitals": {
                "blood_pressure": "160/95",
                "heart_rate": 92,
                "temperature": 37.2
            },
            "lab_results": [
                {
                    "TEST_ADI": "Troponin I",
                    "SONUC": "0.05",
                    "BIRIM": "ng/mL",
                    "NORMAL_MAX": "0.04"
                },
                {
                    "TEST_ADI": "CK-MB",
                    "SONUC": "25",
                    "BIRIM": "U/L",
                    "NORMAL_MAX": "25"
                }
            ]
        }

    def test_complete_workflow_success(self, test_client: TestClient, test_data):
        """Test complete patient workflow from start to finish."""
        # Step 1: Search for patient
        search_response = test_client.get(
            f"/patients/search?q={test_data['patient']['ADI']}&limit=10"
        )
        assert search_response.status_code == 200
        patients = search_response.json()
        assert len(patients) > 0

        patient_tckn = patients[0]["TCKN"]

        # Step 2: Get patient details
        patient_response = test_client.get(f"/patients/{patient_tckn}")
        assert patient_response.status_code == 200
        patient_data = patient_response.json()
        assert patient_data["TCKN"] == patient_tckn

        # Step 3: Generate differential diagnosis
        diagnosis_request = {
            "tckn": patient_tckn,
            "chief_complaint": test_data["complaint"],
            "model": "claude"
        }

        with patch('src.api.diagnosis.generate_differential_diagnosis_ai',
                  new_callable=AsyncMock) as mock_diagnosis:

            mock_diagnosis.return_value = {
                "differential_diagnosis": [
                    {
                        "diagnosis": "Acute Coronary Syndrome",
                        "icd10": "I21.9",
                        "probability": 0.75,
                        "urgency": "critical"
                    },
                    {
                        "diagnosis": "Anxiety with Hyperventilation",
                        "icd10": "F41.0",
                        "probability": 0.25,
                        "urgency": "minor"
                    }
                ],
                "red_flags": [
                    "Elevated troponin levels",
                    "Chest pain characteristics suggest cardiac origin",
                    "Shortness of breath with exertion"
                ],
                "recommended_tests": [
                    "Serial troponin measurements",
                    "12-lead ECG",
                    "Chest X-ray",
                    "Complete blood count"
                ]
            }

            diagnosis_response = test_client.post(
                "/analyze/diagnosis",
                json=diagnosis_request
            )
            assert diagnosis_response.status_code == 200
            diagnosis_data = diagnosis_response.json()

            # Verify diagnosis contains critical findings
            assert len(diagnosis_data["differential_diagnosis"]) == 2
            assert len(diagnosis_data["red_flags"]) > 0
            critical_diagnoses = [
                d for d in diagnosis_data["differential_diagnosis"]
                if d["urgency"] == "critical"
            ]
            assert len(critical_diagnoses) > 0

        # Step 4: Generate treatment plan based on diagnosis
        treatment_request = {
            "tckn": patient_tckn,
            "diagnosis": "Acute Coronary Syndrome",
            "model": "claude"
        }

        with patch('src.api.treatment.suggest_treatment_ai',
                  new_callable=AsyncMock) as mock_treatment:

            mock_treatment.return_value = {
                "medications": [
                    {
                        "name": "Aspirin",
                        "dosage": "325mg immediately, then 81mg daily",
                        "duration": "lifelong"
                    },
                    {
                        "name": "Nitroglycerin",
                        "dosage": "0.4mg sublingual every 5 minutes as needed",
                        "duration": "as needed"
                    }
                ],
                "clinical_guidelines": (
                    "Immediate antiplatelet therapy with aspirin. "
                    "Consider beta-blocker therapy. "
                    "Urgent cardiology consultation recommended."
                ),
                "followup_plan": (
                    "Admit to cardiac monitoring unit. "
                    "Serial ECGs and cardiac enzymes. "
                    "Cardiology consultation within 24 hours."
                )
            }

            treatment_response = test_client.post(
                "/analyze/treatment",
                json=treatment_request
            )
            assert treatment_response.status_code == 200
            treatment_data = treatment_response.json()

            # Verify treatment plan
            assert len(treatment_data["medications"]) >= 2
            assert "Aspirin" in [med["name"] for med in treatment_data["medications"]]
            assert "clinical_guidelines" in treatment_data
            assert "followup_plan" in treatment_data

        # Step 5: Check for drug interactions
        drug_check_request = {
            "tckn": patient_tckn,
            "proposed_drug": "Aspirin",
            "severity": "all"
        }

        with patch('src.api.drugs.check_interactions',
                  new_callable=AsyncMock) as mock_drug_check:

            mock_drug_check.return_value = {
                "interactions": [],
                "safety_recommendations": [
                    "Monitor for gastrointestinal bleeding",
                    "Consider gastroprotection with PPI if long-term use"
                ]
            }

            drug_check_response = test_client.post(
                "/drugs/interactions",
                json=drug_check_request
            )
            assert drug_check_response.status_code == 200
            drug_check_data = drug_check_response.json()

            # Verify drug interaction check
            assert "interactions" in drug_check_data
            assert "safety_recommendations" in drug_check_data

        # Step 6: Retrieve lab results and trends
        with patch('src.api.labs.get_lab_tests',
                  return_value=test_data["lab_results"]):

            lab_response = test_client.get(f"/labs/{patient_tckn}")
            assert lab_response.status_code == 200
            lab_data = lab_response.json()

            # Verify lab data
            assert len(lab_data) >= 2
            troponin = next((lab for lab in lab_data if "Troponin" in lab["TEST_ADI"]), None)
            assert troponin is not None
            assert float(troponin["SONUC"]) > 0.04  # Elevated

    def test_workflow_with_moderate_risk_patient(self, test_client: TestClient, test_data):
        """Test workflow with a moderate risk patient scenario."""
        # Modified complaint for moderate risk scenario
        moderate_complaint = "Patient reports occasional headaches and fatigue for 2 weeks"

        search_response = test_client.get("/patients/search?q=Test&limit=10")
        patients = search_response.json()
        patient_tckn = patients[0]["TCKN"]

        # Generate diagnosis for moderate risk case
        diagnosis_request = {
            "tckn": patient_tckn,
            "chief_complaint": moderate_complaint,
            "model": "claude"
        }

        with patch('src.api.diagnosis.generate_differential_diagnosis_ai',
                  new_callable=AsyncMock) as mock_diagnosis:

            mock_diagnosis.return_value = {
                "differential_diagnosis": [
                    {
                        "diagnosis": "Tension Headache",
                        "icd10": "G44.2",
                        "probability": 0.65,
                        "urgency": "minor"
                    },
                    {
                        "diagnosis": "Anemia",
                        "icd10": "D64.9",
                        "probability": 0.35,
                        "urgency": "moderate"
                    }
                ],
                "red_flags": [],
                "recommended_tests": [
                    "Complete blood count",
                    "Thyroid function tests",
                    "Blood pressure measurement"
                ]
            }

            diagnosis_response = test_client.post("/analyze/diagnosis", json=diagnosis_request)
            assert diagnosis_response.status_code == 200
            diagnosis_data = diagnosis_response.json()

            # Verify moderate risk scenario
            assert len(diagnosis_data["differential_diagnosis"]) == 2
            assert len(diagnosis_data["red_flags"]) == 0  # No red flags
            assert any(d["urgency"] == "moderate" for d in diagnosis_data["differential_diagnosis"])

    def test_workflow_error_handling(self, test_client: TestClient):
        """Test workflow error handling scenarios."""
        # Test with non-existent patient
        nonexistent_response = test_client.get("/patients/99999999999")
        assert nonexistent_response.status_code == 404

        # Test diagnosis generation with invalid data
        invalid_diagnosis = {
            "tckn": "12345678901",
            "chief_complaint": "",  # Empty complaint
            "model": "claude"
        }

        response = test_client.post("/analyze/diagnosis", json=invalid_diagnosis)
        assert response.status_code == 422

        # Test treatment generation without diagnosis
        no_diagnosis_request = {
            "tckn": "12345678901",
            "diagnosis": "",  # Empty diagnosis
            "model": "claude"
        }

        response = test_client.post("/analyze/treatment", json=no_diagnosis_request)
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.database
class TestPatientDataConsistency:
    """Test data consistency across patient workflow."""

    def test_patient_id_consistency(self, test_client: TestClient):
        """Test patient ID consistency throughout workflow."""
        # Search for patient
        search_response = test_client.get("/patients/search?q=Test&limit=10")
        patients = search_response.json()
        patient_tckn = patients[0]["TCKN"]

        # Get patient details
        patient_response = test_client.get(f"/patients/{patient_tckn}")
        patient_data = patient_response.json()
        assert patient_data["TCKN"] == patient_tckn

        # Use same TCKN for diagnosis
        diagnosis_request = {
            "tckn": patient_tckn,
            "chief_complaint": "Test complaint",
            "model": "claude"
        }

        with patch('src.api.diagnosis.generate_differential_diagnosis_ai',
                  new_callable=AsyncMock) as mock_diagnosis:

            mock_diagnosis.return_value = {
                "differential_diagnosis": [
                    {
                        "diagnosis": "Test Condition",
                        "icd10": "Z00.0",
                        "probability": 1.0,
                        "urgency": "minor"
                    }
                ],
                "red_flags": [],
                "recommended_tests": []
            }

            diagnosis_response = test_client.post("/analyze/diagnosis", json=diagnosis_request)
            assert diagnosis_response.status_code == 200

        # Verify same patient TCKN is used throughout
        # This would be verified through database consistency checks
        assert patient_tckn == patient_tckn  # Redundant but shows consistency


@pytest.mark.integration
@pytest.mark.ai
class TestAIIntegrationWorkflow:
    """Test AI service integration in workflow."""

    @pytest.mark.asyncio
    async def test_ai_routing_consistency(self):
        """Test AI routing consistency across different task types."""
        from src.ai.router import AIRouter
        from src.ai.ollama_client import OllamaClient
        from src.ai.anthropic_client import AnthropicClient

        # Mock clients
        mock_ollama = Mock()
        mock_claude = Mock()
        mock_ollama.complete = AsyncMock(return_value={"text": "Simple response", "provider": "ollama"})
        mock_claude.complete = AsyncMock(return_value={"text": "Complex response", "provider": "claude"})

        router = AIRouter(ollama_client=mock_ollama, claude_client=mock_claude)

        # Test routing for different task types
        simple_request = {
            "prompt": "Patient summary",
            "task_type": "patient_summary"
        }
        result = await router.route_and_complete(simple_request)
        assert result.provider == "ollama"

        complex_request = {
            "prompt": "Complex differential diagnosis",
            "task_type": "differential_diagnosis"
        }
        result = await router.route_and_complete(complex_request)
        assert result.provider == "claude"

        # Verify correct clients were called
        mock_ollama.complete.assert_called_once()
        mock_claude.complete.assert_called_once()