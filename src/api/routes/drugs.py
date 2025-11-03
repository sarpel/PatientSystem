"""Drug interaction checking API endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from ...clinical.drug_interaction import DrugInteractionChecker
from ...database.connection import get_session

router = APIRouter()


class DrugCheckRequest(BaseModel):
    """Request model for drug interaction check."""

    tckn: str = Field(..., description="Patient TCKN")
    proposed_drug: str = Field(..., description="New drug to check")
    use_ai: bool = Field(False, description="Use AI for interaction check")


@router.post("/drugs/interactions")
async def check_drug_interactions(request: DrugCheckRequest):
    """
    Check for drug-drug and drug-allergy interactions.

    Args:
        request: Drug check request with patient and proposed drug

    Returns:
        Interaction warnings and safe alternatives
    """
    try:
        with get_session() as session:
            checker = DrugInteractionChecker(session)

            result = await checker.check_interactions(
                tckn=request.tckn,
                proposed_drug=request.proposed_drug,
                use_ai=request.use_ai,
            )

            logger.info(
                f"Drug interaction check: TCKN={request.tckn}, "
                f"drug={request.proposed_drug}, "
                f"safe={result.get('safe_to_prescribe')}"
            )

            return result

    except Exception as e:
        logger.error(f"Drug interaction check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Check error: {str(e)}")


@router.get("/drugs/{tckn}/check-allergy")
async def check_drug_allergy(tckn: str, drug_name: str):
    """
    Check if drug conflicts with patient allergies.

    Args:
        tckn: Patient TCKN
        drug_name: Drug name to check

    Returns:
        Allergy cross-reactivity warnings
    """
    try:
        with get_session() as session:
            checker = DrugInteractionChecker(session)
            result = checker.check_allergy_cross_reactivity(tckn, drug_name)

            logger.info(
                f"Allergy check: TCKN={tckn}, drug={drug_name}, " f"safe={result.get('safe')}"
            )

            return result

    except Exception as e:
        logger.error(f"Allergy check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Check error: {str(e)}")
