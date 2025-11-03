"""Pytest configuration and shared fixtures."""

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.fastapi_app import app
from src.config.settings import settings
from src.database.connection import get_engine, get_session
from src.models.patient import Patient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session() -> Generator[Session, None, None]:
    """Create a mock database session for testing."""
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    from src.models.base import Base

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client(mock_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with mocked database session."""

    def override_get_session():
        try:
            yield mock_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patient() -> Patient:
    """Create a sample patient for testing."""
    return Patient(
        TCKN="12345678901",
        ADI="Test",
        SOYADI="Patient",
        DOGUM_TARIHI=datetime(1980, 1, 1),
        CINSIYET="E",
        TELEFON="5551234567",
        ADRES="123 Test Street",
    )


@pytest.fixture
def mock_ai_response():
    """Create a mock AI response for testing."""
    return {
        "differential_diagnosis": [
            {
                "diagnosis": "Hypertension",
                "icd10": "I10",
                "probability": 0.75,
                "urgency": "moderate",
            },
            {"diagnosis": "Anxiety", "icd10": "F41.1", "probability": 0.45, "urgency": "minor"},
        ],
        "red_flags": ["Blood pressure reading above 180/120 mmHg", "Chest pain reported"],
        "recommended_tests": ["CBC", "Comprehensive metabolic panel", "Lipid panel", "Urinalysis"],
    }


@pytest.fixture
def mock_treatment_response():
    """Create a mock treatment response for testing."""
    return {
        "medications": [
            {"name": "Lisinopril", "dosage": "10mg daily", "duration": "ongoing"},
            {"name": "Hydrochlorothiazide", "dosage": "25mg daily", "duration": "ongoing"},
        ],
        "clinical_guidelines": "Start ACE inhibitor therapy for hypertension. Monitor blood pressure and renal function.",
        "followup_plan": "Follow up in 4 weeks to assess blood pressure control and medication tolerance.",
    }


@pytest.fixture
def mock_lab_data():
    """Create mock laboratory data for testing."""
    return [
        {
            "TEST_ADI": "Hemoglobin",
            "SONUC": "14.2",
            "BIRIM": "g/dL",
            "TEST_TARIHI": datetime(2024, 1, 15),
            "NORMAL_MIN": "12.0",
            "NORMAL_MAX": "16.0",
        },
        {
            "TEST_ADI": "Glucose",
            "SONUC": "95",
            "BIRIM": "mg/dL",
            "TEST_TARIHI": datetime(2024, 1, 15),
            "NORMAL_MIN": "70",
            "NORMAL_MAX": "100",
        },
    ]


@pytest.fixture
def mock_ollama_client():
    """Create a mock Ollama client for testing."""
    client = Mock()
    client.complete = AsyncMock(
        return_value={"text": "Mock diagnosis response", "model": "gemma:7b", "provider": "ollama"}
    )
    client.health_check = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_claude_client():
    """Create a mock Claude client for testing."""
    client = Mock()
    client.complete = AsyncMock(
        return_value={
            "text": "Mock Claude diagnosis response",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "claude",
        }
    )
    client.health_check = AsyncMock(return_value=True)
    return client


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for testing."""
    return {
        "patient_summary_seconds": 2.0,
        "diagnosis_generation_seconds": 30.0,
        "lab_analysis_seconds": 5.0,
        "api_response_ms": 1000,
        "database_query_ms": 500,
    }


@pytest.fixture
def mock_environment(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")


# Markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
pytest.mark.ai = pytest.mark.ai
pytest.mark.database = pytest.mark.database
pytest.mark.gui = pytest.mark.gui
pytest.mark.performance = pytest.mark.performance
