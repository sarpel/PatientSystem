"""Health check endpoints for monitoring and status."""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from loguru import logger
from sqlalchemy import text

from ...ai import create_ai_router
from ...database.connection import get_engine

router = APIRouter()


@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Clinical AI Assistant API",
    }


@router.get("/database")
async def database_health() -> Dict[str, Any]:
    """
    Check database connectivity and pool status.

    Returns:
        Database connection status
    """
    try:
        engine = get_engine()

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test")).scalar()

        # Get pool status
        pool = engine.pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }

        return {
            "status": "healthy",
            "connection": "successful",
            "test_query": result == 1,
            "pool": pool_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection error: {str(e)}",
        )


@router.get("/ai")
async def ai_health() -> Dict[str, Any]:
    """
    Check AI provider availability.

    Returns:
        Status of all configured AI providers
    """
    try:
        router = create_ai_router()
        providers_status = await router.health_check_all()

        healthy_count = sum(1 for status in providers_status.values() if status)
        total_count = len(providers_status)

        return {
            "status": "healthy" if healthy_count > 0 else "degraded",
            "providers": providers_status,
            "available": list(router.get_available_providers()),
            "healthy_providers": healthy_count,
            "total_providers": total_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service error: {str(e)}",
        )


@router.get("/full")
async def full_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check of all services.

    Returns:
        Status of database, AI providers, and overall system
    """
    results = {
        "overall_status": "healthy",
        "checks": {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Check database
    try:
        db_health = await database_health()
        results["checks"]["database"] = {
            "status": "healthy",
            "details": db_health,
        }
    except Exception as e:
        results["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        results["overall_status"] = "degraded"

    # Check AI providers
    try:
        ai_health = await ai_health()
        results["checks"]["ai"] = {
            "status": ai_health["status"],
            "details": ai_health,
        }
        if ai_health["status"] != "healthy":
            results["overall_status"] = "degraded"
    except Exception as e:
        results["checks"]["ai"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        results["overall_status"] = "degraded"

    return results
