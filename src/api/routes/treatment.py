"""Treatment recommendation API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from ...clinical.treatment_engine import TreatmentEngine
from ...database.connection import get_session

router = APIRouter()


class TreatmentRequest(BaseModel):
    """Request model for treatment recommendations."""

    tckn: str = Field(..., description="Patient TCKN")
    diagnosis: str = Field(..., description="Confirmed diagnosis")
    use_ai: bool = Field(True, description="Use AI for recommendations")
    preferred_provider: Optional[str] = Field(None, description="Preferred AI provider")


@router.post("/analyze/treatment")
async def analyze_treatment(request: TreatmentRequest):
    """
    Generate treatment recommendations for confirmed diagnosis.

    Args:
        request: Treatment request with patient and diagnosis

    Returns:
        Treatment recommendations (pharmacological, lifestyle, follow-up)
    """
    try:
        with get_session() as session:
            engine = TreatmentEngine(session)

            if request.use_ai:
                result = await engine.generate_treatment_plan_ai(
                    tckn=request.tckn,
                    diagnosis=request.diagnosis,
                    preferred_provider=request.preferred_provider,
                )
            else:
                result = engine.generate_treatment_plan_rules(
                    tckn=request.tckn,
                    diagnosis=request.diagnosis,
                )

            logger.info(
                f"Treatment plan generated: TCKN={request.tckn}, "
                f"diagnosis={request.diagnosis}, AI={request.use_ai}"
            )

            return result

    except Exception as e:
        logger.error(f"Treatment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
