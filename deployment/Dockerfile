# Clinical AI Assistant - Production Dockerfile
# Multi-stage build for optimal performance and security

# Build Stage - Python Dependencies
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production Stage - Runtime Container
FROM python:3.11-slim as production

# Set labels for metadata
LABEL maintainer="Clinical AI Assistant Team" \
      org.opencontainers.image.title="Clinical AI Assistant" \
      org.opencontainers.image.description="AI-powered clinical decision support system" \
      org.opencontainers.image.version="${VERSION:-latest}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/your-org/PatientSystem"

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    unixodbc \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r clinicalai && \
    useradd -r -g clinicalai -d /app -s /bin/bash clinicalai

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./
COPY README.md ./

# Create necessary directories
RUN mkdir -p logs data cache && \
    chown -R clinicalai:clinicalai /app

# Switch to non-root user
USER clinicalai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command - start the API server
CMD ["python", "-m", "src.api.fastapi_app"]

# Development Stage - For development with hot reload
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install watchfiles python-dotenv

# Switch back to clinicalai user
USER clinicalai

# Override command for development with auto-reload
CMD ["python", "-m", "uvicorn", "src.api.fastapi_app:app",
     "--host", "0.0.0.0", "--port", "8000", "--reload"]