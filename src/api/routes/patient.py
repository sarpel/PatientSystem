"""Patient-related API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from sqlalchemy import bindparam

from ...clinical.patient_summarizer import PatientSummarizer
from ...database.connection import get_session
from ...models.patient import Patient, PatientDemographics

router = APIRouter()


@router.get("/patients/search")
async def search_patients(
    q: str = Query(..., min_length=2, description="Search query (name or TCKN)"),
    limit: int = Query(20, le=100, description="Maximum results to return"),
):
    """
    Search for patients by name or TCKN.

    Args:
        q: Search query string (minimum 2 characters)
        limit: Maximum number of results (default 20, max 100)

    Returns:
        List of matching patients with basic information
    """
    try:
        with get_session() as session:
            # Search by TCKN or name
            query = session.query(Patient)

            # If query looks like TCKN (numeric), search TCKN
            if q.isdigit():
                search_pattern = f"{q}%"
                query = query.filter(Patient.HASTA_KIMLIK_NO.like(bindparam('pattern'))).params(pattern=search_pattern)
            else:
                # Search by name
                search_pattern = f"%{q}%"
                query = query.filter(
                    (Patient.AD.ilike(bindparam('pattern'))) |
                    (Patient.SOYAD.ilike(bindparam('pattern')))
                ).params(pattern=search_pattern)

            patients = query.limit(limit).all()

            # Format results
            results = []
            for patient in patients:
                results.append(
                    {
                        "tckn": str(patient.HASTA_KIMLIK_NO) if patient.HASTA_KIMLIK_NO else None,
                        "name": patient.full_name,
                        "age": patient.age,
                        "gender": patient.CINSIYET,
                        "last_visit": None,  # Would need to query visits
                    }
                )

            logger.info(f"Patient search: query='{q}', results={len(results)}")
            return {"query": q, "count": len(results), "patients": results}

    except Exception as e:
        logger.error(f"Patient search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/patients/{tckn}")
async def get_patient(tckn: str):
    """
    Get comprehensive patient information by TCKN.

    Args:
        tckn: Patient's Turkish ID number

    Returns:
        Complete patient summary with demographics, visits, diagnoses, medications
    """
    try:
        with get_session() as session:
            summarizer = PatientSummarizer(session)
            summary = summarizer.get_patient_summary(tckn)

            if not summary:
                raise HTTPException(status_code=404, detail=f"Patient not found: {tckn}")

            logger.info(f"Patient retrieved: TCKN={tckn}")
            return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patient failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
