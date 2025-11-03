"""Unit tests for API endpoints."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.fastapi_app import app


@pytest.mark.unit
class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_basic(self, test_client: TestClient):
        """Test basic health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    def test_health_check_database(self, test_client: TestClient, mock_session):
        """Test database health check endpoint."""
        with patch("src.api.health.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_connection = Mock()
            mock_connection.execute.return_value.scalar.return_value = 1
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            response = test_client.get("/health/database")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "healthy"
            assert "pool" in data

    def test_health_check_database_error(self, test_client: TestClient):
        """Test database health check with error."""
        with patch("src.api.health.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Database connection failed")

            response = test_client.get("/health/database")
            assert response.status_code == 500

            data = response.json()
            assert data["status"] == "unhealthy"


@pytest.mark.unit
class TestPatientEndpoints:
    """Test patient management endpoints."""

    def test_search_patients_success(self, test_client: TestClient, mock_session, sample_patient):
        """Test successful patient search."""
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.limit.return_value.all.return_value = [sample_patient]
        mock_session.query.return_value = mock_query

        response = test_client.get("/patients/search?q=Test&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["TCKN"] == "12345678901"
        assert data[0]["ADI"] == "Test"

    def test_search_patients_short_query(self, test_client: TestClient):
        """Test patient search with too short query."""
        response = test_client.get("/patients/search?q=T")
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_get_patient_success(self, test_client: TestClient, mock_session, sample_patient):
        """Test successful patient retrieval."""
        mock_session.query.return_value.filter.return_value.first.return_value = sample_patient

        response = test_client.get("/patients/12345678901")
        assert response.status_code == 200

        data = response.json()
        assert data["TCKN"] == "12345678901"
        assert data["ADI"] == "Test"

    def test_get_patient_not_found(self, test_client: TestClient, mock_session):
        """Test patient retrieval with non-existent patient."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        response = test_client.get("/patients/99999999999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data


@pytest.mark.unit
@pytest.mark.ai
class TestDiagnosisEndpoints:
    """Test diagnosis generation endpoints."""

    @pytest.mark.asyncio
    async def test_generate_diagnosis_success(self, test_client: TestClient, mock_ai_response):
        """Test successful diagnosis generation."""
        request_data = {
            "tckn": "12345678901",
            "chief_complaint": "Patient reports headache and fever for 3 days",
            "model": "claude",
        }

        with patch(
            "src.api.diagnosis.generate_differential_diagnosis_ai",
            new_callable=AsyncMock,
            return_value=mock_ai_response,
        ):

            response = test_client.post("/analyze/diagnosis", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "differential_diagnosis" in data
            assert len(data["differential_diagnosis"]) == 2
            assert "red_flags" in data
            assert "recommended_tests" in data

    def test_generate_diagnosis_invalid_data(self, test_client: TestClient):
        """Test diagnosis generation with invalid data."""
        request_data = {"tckn": "", "chief_complaint": ""}  # Empty TCKN  # Empty complaint

        response = test_client.post("/analyze/diagnosis", json=request_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_diagnosis_ai_error(self, test_client: TestClient):
        """Test diagnosis generation when AI service fails."""
        request_data = {"tckn": "12345678901", "chief_complaint": "Test complaint"}

        with patch(
            "src.api.diagnosis.generate_differential_diagnosis_ai",
            new_callable=AsyncMock,
            side_effect=Exception("AI service unavailable"),
        ):

            response = test_client.post("/analyze/diagnosis", json=request_data)
            assert response.status_code == 500


@pytest.mark.unit
@pytest.mark.ai
class TestTreatmentEndpoints:
    """Test treatment recommendation endpoints."""

    @pytest.mark.asyncio
    async def test_generate_treatment_success(
        self, test_client: TestClient, mock_treatment_response
    ):
        """Test successful treatment generation."""
        request_data = {
            "tckn": "12345678901",
            "diagnosis": "Essential Hypertension",
            "model": "claude",
        }

        with patch(
            "src.api.treatment.suggest_treatment_ai",
            new_callable=AsyncMock,
            return_value=mock_treatment_response,
        ):

            response = test_client.post("/analyze/treatment", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "medications" in data
            assert len(data["medications"]) == 2
            assert "clinical_guidelines" in data
            assert "followup_plan" in data

    def test_generate_treatment_invalid_diagnosis(self, test_client: TestClient):
        """Test treatment generation with invalid diagnosis."""
        request_data = {"tckn": "12345678901", "diagnosis": ""}  # Empty diagnosis

        response = test_client.post("/analyze/treatment", json=request_data)
        assert response.status_code == 422


@pytest.mark.unit
class TestDrugEndpoints:
    """Test drug interaction endpoints."""

    @pytest.mark.asyncio
    async def test_check_drug_interactions_success(self, test_client: TestClient):
        """Test successful drug interaction checking."""
        mock_response = {
            "interactions": [
                {
                    "type": "Pharmacodynamic",
                    "severity": "major",
                    "drug1": "Lisinopril",
                    "drug2": "Potassium Supplement",
                    "effect": "Increased risk of hyperkalemia",
                }
            ],
            "safety_recommendations": [
                "Monitor potassium levels",
                "Consider alternative medications",
            ],
        }

        request_data = {"tckn": "12345678901", "proposed_drug": "Lisinopril", "severity": "all"}

        with patch(
            "src.api.drugs.check_interactions", new_callable=AsyncMock, return_value=mock_response
        ):

            response = test_client.post("/drugs/interactions", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "interactions" in data
            assert "safety_recommendations" in data
            assert len(data["interactions"]) == 1

    def test_check_drug_interactions_missing_data(self, test_client: TestClient):
        """Test drug interaction checking with missing data."""
        request_data = {
            "tckn": "12345678901"
            # Missing proposed_drug
        }

        response = test_client.post("/drugs/interactions", json=request_data)
        assert response.status_code == 422


@pytest.mark.unit
class TestLabEndpoints:
    """Test laboratory endpoints."""

    def test_get_lab_tests_success(self, test_client: TestClient, mock_lab_data):
        """Test successful lab test retrieval."""
        with patch("src.api.labs.get_lab_tests", return_value=mock_lab_data):
            response = test_client.get("/labs/12345678901")
            assert response.status_code == 200

            data = response.json()
            assert len(data) == 2
            assert data[0]["TEST_ADI"] == "Hemoglobin"
            assert data[1]["TEST_ADI"] == "Glucose"

    def test_get_lab_trends_success(self, test_client: TestClient):
        """Test successful lab trends retrieval."""
        mock_trends = {
            "test_name": "Hemoglobin",
            "trend_data": [
                {"date": "2024-01-01", "value": 14.0},
                {"date": "2024-02-01", "value": 14.2},
            ],
            "trend_direction": "stable",
        }

        with patch("src.api.labs.get_lab_trends", return_value=mock_trends):
            response = test_client.get("/labs/12345678901/trends?test=Hemoglobin&months=6")
            assert response.status_code == 200

            data = response.json()
            assert "trend_data" in data
            assert "trend_direction" in data

    def test_get_lab_trends_invalid_params(self, test_client: TestClient):
        """Test lab trends with invalid parameters."""
        response = test_client.get("/labs/12345678901/trends?test=")  # Empty test
        assert response.status_code == 422


@pytest.mark.unit
class TestAPIErrorHandling:
    """Test API error handling and validation."""

    def test_404_not_found(self, test_client: TestClient):
        """Test 404 error handling."""
        response = test_client.get("/nonexistent-endpoint")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_method_not_allowed(self, test_client: TestClient):
        """Test method not allowed error."""
        response = test_client.delete("/patients/search")  # GET endpoint with DELETE
        assert response.status_code == 405

    def test_invalid_json(self, test_client: TestClient):
        """Test invalid JSON in request body."""
        response = test_client.post(
            "/analyze/diagnosis", data="invalid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_content_type_validation(self, test_client: TestClient):
        """Test content type validation."""
        response = test_client.post(
            "/analyze/diagnosis",
            data="{}",
            headers={"Content-Type": "text/plain"},  # Wrong content type
        )
        # FastAPI may still handle this, but it's good to test
        assert response.status_code in [200, 422]
