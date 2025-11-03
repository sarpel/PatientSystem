"""Diagnosis analysis API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from loguru import logger

from ...ai import create_ai_router, AIRequest, TurkishMedicalPrompts
from ...database.connection import get_session
from ...clinical.diagnosis_engine import DiagnosisEngine

router = APIRouter()


class DiagnosisRequest(BaseModel):
    """Request model for diagnosis analysis."""

    tckn: str = Field(..., description="Patient TCKN")
    chief_complaint: str = Field(..., min_length=10, description="Patient symptoms")
    vitals: Optional[Dict[str, Any]] = Field(None, description="Vital signs")
    use_ai: bool = Field(True, description="Use AI for analysis")
    preferred_provider: Optional[str] = Field(None, description="Preferred AI provider")


@router.post("/analyze/diagnosis")
async def analyze_diagnosis(request: DiagnosisRequest):
    """
    Generate differential diagnosis using AI or rule-based engine.

    Args:
        request: Diagnosis request with patient info and symptoms

    Returns:
        Differential diagnoses with probabilities and recommendations
    """
    try:
        with get_session() as session:
            engine = DiagnosisEngine(session)

            if request.use_ai:
                # Use AI-powered diagnosis
                result = await engine.generate_differential_diagnosis_ai(
                    tckn=request.tckn,
                    chief_complaint=request.chief_complaint,
                    vitals=request.vitals,
                    preferred_provider=request.preferred_provider,
                )
            else:
                # Use rule-based diagnosis
                result = engine.generate_differential_diagnosis_rules(
                    tckn=request.tckn,
                    chief_complaint=request.chief_complaint,
                    vitals=request.vitals,
                )

            logger.info(
                f"Diagnosis generated: TCKN={request.tckn}, "
                f"AI={request.use_ai}, "
                f"results={len(result.get('differential_diagnosis', []))}"
            )

            return result

    except Exception as e:
        logger.error(f"Diagnosis analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
