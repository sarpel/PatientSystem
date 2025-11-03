"""Laboratory analysis API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from ...database.connection import get_session
from ...clinical.lab_analyzer import LabAnalyzer

router = APIRouter()


@router.get("/labs/{tckn}/analyze")
async def analyze_labs(tckn: str):
    """
    Analyze latest laboratory results for patient.

    Args:
        tckn: Patient TCKN

    Returns:
        Lab results with reference range comparison and critical value flags
    """
    try:
        with get_session() as session:
            analyzer = LabAnalyzer(session)
            result = analyzer.analyze_latest_labs(tckn)

            logger.info(
                f"Lab analysis: TCKN={tckn}, "
                f"critical={len(result.get('critical_abnormals', []))}"
            )

            return result

    except Exception as e:
        logger.error(f"Lab analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/labs/{tckn}/trends")
async def get_lab_trends(
    tckn: str,
    test: str = Query(..., description="Lab test name (e.g., HbA1c)"),
    months: int = Query(12, ge=1, le=60, description="Number of months to analyze"),
):
    """
    Get trend analysis for specific lab test over time.

    Args:
        tckn: Patient TCKN
        test: Lab test name
        months: Number of months to include

    Returns:
        Historical lab values with trend analysis
    """
    try:
        with get_session() as session:
            analyzer = LabAnalyzer(session)
            result = analyzer.get_lab_trend(tckn, test, months)

            logger.info(
                f"Lab trend: TCKN={tckn}, test={test}, "
                f"points={len(result.get('values', []))}"
            )

            return result

    except Exception as e:
        logger.error(f"Lab trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
