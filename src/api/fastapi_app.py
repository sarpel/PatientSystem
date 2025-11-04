"""FastAPI application for Clinical AI Assistant REST API."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from ..config.settings import settings
from .routes import diagnosis, drugs, health, labs, patient, treatment


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("🚀 Clinical AI Assistant API starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.db_server}/{settings.db_name}")
    logger.info(f"AI Providers: {settings.has_ai_keys}")

    yield

    # Shutdown
    logger.info("👋 Clinical AI Assistant API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Clinical AI Assistant API",
    description="REST API for AI-powered clinical decision support system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS middleware configuration (localhost only for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration_ms:.2f}ms - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if settings.environment == "development" else None,
        },
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(patient.router, prefix="/api/v1", tags=["Patients"])
app.include_router(diagnosis.router, prefix="/api/v1", tags=["Diagnosis"])
app.include_router(treatment.router, prefix="/api/v1", tags=["Treatment"])
app.include_router(drugs.router, prefix="/api/v1", tags=["Drugs"])
app.include_router(labs.router, prefix="/api/v1", tags=["Labs"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with basic information."""
    return {
        "name": "Clinical AI Assistant API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.fastapi_app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
