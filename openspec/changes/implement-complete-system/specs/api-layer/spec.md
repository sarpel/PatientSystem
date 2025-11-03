# API Layer Capability Specification

## ADDED Requirements

### Requirement: FastAPI Application Structure
The system SHALL provide a RESTful API built with FastAPI for programmatic access to clinical services.

#### Scenario: API server startup
- **WHEN** developer runs `uvicorn src.api.fastapi_app:app --reload --port 8080`
- **THEN** FastAPI server starts and displays available endpoints at http://localhost:8080

#### Scenario: Interactive API documentation
- **WHEN** user navigates to http://localhost:8080/docs
- **THEN** Swagger UI displays all endpoints with request/response schemas and "Try it out" functionality

#### Scenario: Alternative documentation format
- **WHEN** user navigates to http://localhost:8080/redoc
- **THEN** ReDoc displays comprehensive API documentation with examples

### Requirement: Health Check Endpoint
The system SHALL provide health check endpoint for monitoring and load balancer integration.

#### Scenario: Basic health check
- **WHEN** client sends GET to /health
- **THEN** API returns 200 OK with {status: "healthy", timestamp: "2024-01-15T10:30:00Z"}

#### Scenario: Database connectivity check
- **WHEN** client sends GET to /health/database
- **THEN** API tests database connection and returns status with connection pool metrics

#### Scenario: AI services health check
- **WHEN** client sends GET to /health/ai
- **THEN** API tests each enabled AI provider and returns availability status for Ollama, Claude, GPT, Gemini

### Requirement: Patient Search and Retrieval Endpoints
The system SHALL provide endpoints for querying patient information.

#### Scenario: Search patients by query string
- **WHEN** client sends GET to /api/v1/patients/search?q=AHMET
- **THEN** API returns list of patients matching "AHMET" in name or TCKN fields

#### Scenario: Get patient by TCKN
- **WHEN** client sends GET to /api/v1/patients/12345678901
- **THEN** API returns complete patient demographics, recent visits, active diagnoses, medications, and allergies

#### Scenario: Patient not found error
- **WHEN** client sends GET to /api/v1/patients/99999999999
- **THEN** API returns 404 Not Found with error message "Patient not found"

### Requirement: Diagnosis Analysis Endpoints
The system SHALL provide endpoints for AI-powered diagnosis generation.

#### Scenario: Generate differential diagnosis
- **WHEN** client sends POST to /api/v1/analyze/diagnosis with {tckn, chief_complaint, vitals, lab_results}
- **THEN** API performs AI analysis and returns differential diagnoses with ICD-10 codes, probabilities, and supporting findings

#### Scenario: Diagnosis request validation
- **WHEN** client sends POST to /api/v1/analyze/diagnosis with missing required field (e.g., tckn)
- **THEN** API returns 422 Unprocessable Entity with validation error details

#### Scenario: AI timeout handling
- **WHEN** AI provider takes longer than 120 seconds to respond
- **THEN** API returns 504 Gateway Timeout with message "AI analysis timeout, please try again"

### Requirement: Treatment Recommendation Endpoints
The system SHALL provide endpoints for evidence-based treatment suggestions.

#### Scenario: Generate treatment recommendations
- **WHEN** client sends POST to /api/v1/analyze/treatment with {tckn, diagnosis, patient_profile}
- **THEN** API returns pharmacological, lifestyle, follow-up, and consultation recommendations

#### Scenario: Include contraindication checking
- **WHEN** treatment recommendations include medications
- **THEN** API automatically checks for drug-drug interactions and contraindications based on patient allergies

#### Scenario: Treatment prioritization
- **WHEN** API returns treatment recommendations
- **THEN** recommendations are sorted by priority (1=highest, 3=lowest) within each category

### Requirement: Drug Interaction Check Endpoints
The system SHALL provide endpoints for medication safety verification.

#### Scenario: Check drug interactions
- **WHEN** client sends POST to /api/v1/drugs/interactions with {tckn, proposed_drug}
- **THEN** API analyzes patient's current medications and returns interaction warnings with severity levels

#### Scenario: Allergy cross-reactivity check
- **WHEN** client sends POST to /api/v1/drugs/check-allergy with {tckn, drug_name}
- **THEN** API checks patient allergies for cross-reactivity (e.g., Penicillin allergy vs Amoxicillin)

#### Scenario: Alternative drug suggestions
- **WHEN** major drug interaction is detected
- **THEN** API includes safe_alternatives array with medication names that don't interact

### Requirement: Lab Analysis Endpoints
The system SHALL provide endpoints for laboratory result interpretation and trending.

#### Scenario: Analyze latest lab results
- **WHEN** client sends GET to /api/v1/labs/12345678901/analyze
- **THEN** API returns latest lab results with reference range comparison, critical value flags, and clinical interpretation

#### Scenario: Get lab trends over time
- **WHEN** client sends GET to /api/v1/labs/12345678901/trends?test=HbA1c&months=12
- **THEN** API returns HbA1c values for last 12 months with trend analysis (increasing/decreasing/stable)

#### Scenario: Critical value alerting
- **WHEN** API analyzes lab results with critical values (e.g., Potassium >6.5)
- **THEN** response includes critical_alerts array with immediate action recommendations

### Requirement: CORS and Security Configuration
The system SHALL configure CORS and security headers appropriate for local deployment.

#### Scenario: CORS for localhost frontend
- **WHEN** React frontend at http://localhost:5173 sends request to API
- **THEN** API includes Access-Control-Allow-Origin: http://localhost:5173 header in response

#### Scenario: Reject requests from external origins
- **WHEN** client from https://external-site.com sends request to API
- **THEN** API returns CORS error and blocks the request

#### Scenario: Security headers
- **WHEN** API returns any response
- **THEN** response includes X-Content-Type-Options: nosniff and X-Frame-Options: DENY headers

### Requirement: Request Validation with Pydantic
The system SHALL validate all request bodies using Pydantic schemas.

#### Scenario: Valid request schema
- **WHEN** client sends POST with valid JSON matching Pydantic schema
- **THEN** API accepts request and processes it successfully

#### Scenario: Type validation error
- **WHEN** client sends POST with string value for integer field
- **THEN** API returns 422 with detailed validation error showing expected type vs received type

#### Scenario: Missing required field
- **WHEN** client sends POST without required field
- **THEN** API returns 422 with error message listing all missing required fields

### Requirement: Error Handling and Logging
The system SHALL provide consistent error responses and comprehensive logging.

#### Scenario: Database connection error
- **WHEN** database becomes unavailable during request processing
- **THEN** API returns 503 Service Unavailable with message "Database connection error" and logs full stack trace

#### Scenario: Unexpected exception handling
- **WHEN** unhandled exception occurs in business logic
- **THEN** API returns 500 Internal Server Error without exposing implementation details and logs exception with request ID

#### Scenario: Request/response logging
- **WHEN** API receives any request
- **THEN** system logs request method, path, client IP, response status, and processing time in structured format
