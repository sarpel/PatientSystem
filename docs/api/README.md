# Clinical AI Assistant API Reference

## 🔌 API Overview

The Clinical AI Assistant REST API provides comprehensive endpoints for clinical decision support, patient management, and AI-powered analysis. This reference covers all available endpoints, request/response formats, and usage examples.

## 🚀 Getting Started

### Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

### Authentication

Currently, the API does not require authentication (single-user deployment). This may change in future versions.

### CORS Configuration

```json
{
  "allowed_origins": ["http://localhost:5173"],
  "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
  "allowed_headers": ["*"]
}
```

## 📋 API Endpoints

### Health Check Endpoints

#### System Health

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-11-02T10:30:45.123456",
  "version": "0.1.0",
  "uptime": 86400
}
```

#### Database Health

```http
GET /health/database
```

**Response:**

```json
{
  "status": "healthy",
  "connection_pool": {
    "size": 20,
    "checked_in": 5,
    "checked_out": 2,
    "overflow": 0,
    "invalid": 0
  },
  "query_time_ms": 15
}
```

### Patient Management Endpoints

#### Search Patients

```http
GET /patients/search?q={query}&limit={limit}
```

**Parameters:**

- `q` (required): Search query (min 2 characters)
- `limit` (optional): Maximum results (default: 20)

**Response:**

```json
[
  {
    "TCKN": "12345678901",
    "ADI": "Test",
    "SOYADI": "Patient",
    "DOGUM_TARIHI": "1980-01-01",
    "CINSIYET": "E",
    "TELEFON": "5551234567",
    "ADRES": "123 Test Street"
  }
]
```

#### Get Patient Details

```http
GET /patients/{tckn}
```

**Path Parameters:**

- `tckn` (required): Patient TCKN

**Response:**

```json
{
  "TCKN": "12345678901",
  "ADI": "Test",
  "SOYADI": "Patient",
  "DOGUM_TARIHI": "1980-01-01",
  "CINSIYET": "E",
  "TELEFON": "5551234567",
  "ADRES": "123 Test Street"
}
```

### AI Analysis Endpoints

#### Generate Differential Diagnosis

```http
POST /analyze/diagnosis
```

**Request Body:**

```json
{
  "tckn": "12345678901",
  "chief_complaint": "65-year-old male presents with chest pain radiating to left arm",
  "model": "claude"
}
```

**Response:**

```json
{
  "differential_diagnosis": [
    {
      "diagnosis": "Acute Coronary Syndrome",
      "icd10": "I21.9",
      "probability": 0.75,
      "urgency": "critical"
    },
    {
      "diagnosis": "Aortic Dissection",
      "icd10": "I71.0",
      "probability": 0.15,
      "urgency": "critical"
    }
  ],
  "red_flags": [
    "Age > 60 with chest pain requires urgent evaluation",
    "Pain radiating to arm suggests cardiac origin",
    "Multiple cardiovascular risk factors present"
  ],
  "recommended_tests": [
    "12-lead ECG",
    "Cardiac enzymes (Troponin, CK-MB)",
    "Chest X-ray",
    "Complete blood count",
    "Basic metabolic panel"
  ]
}
```

#### Generate Treatment Recommendations

```http
POST /analyze/treatment
```

**Request Body:**

```json
{
  "tckn": "12345678901",
  "diagnosis": "Acute Coronary Syndrome",
  "model": "claude"
}
```

**Response:**

```json
{
  "medications": [
    {
      "name": "Aspirin",
      "dosage": "325mg immediately, then 81mg daily",
      "duration": "lifelong"
    },
    {
      "name": "Nitroglycerin",
      "dosage": "0.4mg sublingual every 5 minutes PRN chest pain",
      "duration": "as needed"
    }
  ],
  "clinical_guidelines": "Immediate antiplatelet therapy with aspirin. Consider beta-blocker therapy. Urgent cardiology consultation recommended.",
  "followup_plan": "Admit to cardiac monitoring unit. Serial ECGs and cardiac enzymes. Cardiology consultation within 24 hours."
}
```

### Drug Interaction Endpoints

#### Check Drug Interactions

```http
POST /drugs/interactions
```

**Request Body:**

```json
{
  "tckn": "12345678901",
  "proposed_drug": "Aspirin",
  "severity": "all"
}
```

**Response:**

```json
{
  "interactions": [
    {
      "type": "Pharmacodynamic",
      "severity": "major",
      "drug1": "Aspirin",
      "drug2": "Warfarin",
      "effect": "Increased risk of bleeding",
      "alternative_drugs": ["Acetaminophen", "Ibuprofen"]
    }
  ],
  "safety_recommendations": [
    "Monitor INR/PT levels frequently",
    "Consider gastroprotection with PPI",
    "Educate patient about bleeding signs"
  ]
}
```

### Laboratory Endpoints

#### Get Laboratory Results

```http
GET /labs/{tckn}?test={test}
```

**Parameters:**

- `tckn` (required): Patient TCKN
- `test` (optional): Specific test name

**Response:**

```json
[
  {
    "TEST_ADI": "Hemoglobin",
    "SONUC": "14.2",
    "BIRIM": "g/dL",
    "TEST_TARIHI": "2024-11-01T10:30:00",
    "NORMAL_MIN": "12.0",
    "NORMAL_MAX": "16.0"
  },
  {
    "TEST_ADI": "Glucose",
    "SONUC": "95",
    "BIRIM": "mg/dL",
    "TEST_TARIHI": "2024-11-01T10:30:00",
    "NORMAL_MIN": "70",
    "NORMAL_MAX": "100"
  }
]
```

#### Get Laboratory Trends

```http
GET /labs/{tckn}/trends?test={test}&months={months}
```

**Parameters:**

- `tckn` (required): Patient TCKN
- `test` (required): Test name
- `months` (optional): Analysis period in months (default: 12)

**Response:**

```json
{
  "test_name": "Hemoglobin",
  "trend_data": [
    { "date": "2024-01-01", "value": 14.0 },
    { "date": "2024-02-01", "value": 14.2 },
    { "date": "2024-03-01", "value": 13.8 }
  ],
  "trend_direction": "stable",
  "reference_range": {
    "min": 12.0,
    "max": 16.0
  }
}
```

## 📊 Response Formats

### Success Responses

**HTTP Status Codes:**

- `200 OK`: Request successful
- `201 Created`: Resource created
- `202 Accepted`: Request accepted for processing

**Content-Type:**

- `application/json`: Standard JSON responses
- `text/plain`: Error messages

### Error Responses

**Common Error Codes:**

- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Error Response Format:**

```json
{
  "detail": "Validation error: Chief complaint is required",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-11-02T10:30:45.123456"
}
```

## 🔧 Request/Response Schemas

### Patient Schema

```json
{
  "TCKN": "string (required, 11 digits)",
  "ADI": "string (required)",
  "SOYADI": "string (required)",
  "DOGUM_TARIHI": "string (date format: YYYY-MM-DD)",
  "CINSIYET": "string (E|K)",
  "TELEFON": "string (optional)",
  "ADRES": "string (optional)"
}
```

### Diagnosis Request Schema

```json
{
  "tckn": "string (required, 11 digits)",
  "chief_complaint": "string (required, min 10 chars)",
  "model": "string (optional, auto|claude|gpt-4o|gemini|ollama)"
}
```

### Diagnosis Response Schema

```json
{
  "differential_diagnosis": [
    {
      "diagnosis": "string (required)",
      "icd10": "string (required)",
      "probability": "number (required, 0-1)",
      "urgency": "string (required, critical|major|moderate|minor)"
    }
  ],
  "red_flags": ["string"],
  "recommended_tests": ["string"]
}
```

### Treatment Request Schema

```json
{
  "tckn": "string (required, 11 digits)",
  "diagnosis": "string (required, min 5 chars)",
  "model": "string (optional, auto|claude|gpt-4o|gemini|ollama)"
}
```

### Treatment Response Schema

```json
{
  "medications": [
    {
      "name": "string (required)",
      "dosage": "string (required)",
      "duration": "string (required)"
    }
  ],
  "clinical_guidelines": "string",
  "followup_plan": "string"
}
```

### Drug Interaction Request Schema

```json
{
  "tckn": "string (required, 11 digits)",
  "proposed_drug": "string (required)",
  "severity": "string (optional, all|critical|major|moderate|minor)"
}
```

### Drug Interaction Response Schema

```json
{
  "interactions": [
    {
      "type": "string",
      "severity": "string (critical|major|moderate|minor)",
      "drug1": "string",
      "drug2": "string",
      "effect": "string",
      "alternative_drugs": ["string"]
    }
  ],
  "safety_recommendations": ["string"]
}
```

## 🧪 Usage Examples

### Patient Analysis Workflow

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Search for patients
search_response = requests.get(
    f"{BASE_URL}/patients/search",
    params={"q": "Test", "limit": 10}
)
patients = search_response.json()

if patients:
    tckn = patients[0]["TCKN"]

    # 2. Get patient details
    patient_response = requests.get(f"{BASE_URL}/patients/{tckn}")
    patient = patient_response.json()

    # 3. Generate diagnosis
    diagnosis_request = {
        "tckn": tckn,
        "chief_complaint": "Patient reports chest pain",
        "model": "claude"
    }
    diagnosis_response = requests.post(
        f"{BASE_URL}/analyze/diagnosis",
        json=diagnosis_request
    )
    diagnosis = diagnosis_response.json()

    # 4. Generate treatment
    if diagnosis["differential_diagnosis"]:
        primary_diagnosis = diagnosis["differential_diagnosis"][0]["diagnosis"]
        treatment_request = {
            "tckn": tckn,
            "diagnosis": primary_diagnosis,
            "model": "claude"
        }
        treatment_response = requests.post(
            f"{BASE_URL}/analyze/treatment",
            json=treatment_request
        )
        treatment = treatment_response.json()

        print(f"Patient: {patient['ADI']} {patient['SOYADI']}")
        print(f"Diagnosis: {primary_diagnosis}")
        print(f"Treatment: {len(treatment['medications'])} medications")
```

### Drug Interaction Checking

```python
import requests

# Check for drug interactions
interaction_request = {
    "tckn": "12345678901",
    "proposed_drug": "Aspirin",
    "severity": "all"
}

response = requests.post(
    "http://localhost:8000/drugs/interactions",
    json=interaction_request
)

interactions = response.json()

if interactions["interactions"]:
    print(f"Found {len(interactions['interactions'])} interactions:")
    for interaction in interactions["interactions"]:
        severity_emoji = {
            "critical": "🔴",
            "major": "🟠",
            "moderate": "🟡",
            "minor": "🟢"
        }

        print(f"  {severity_emoji[interaction['severity']]} "
              f"{interaction['drug1']} + {interaction['drug2']}: "
              f"{interaction['effect']}")

        if interaction.get("alternative_drugs"):
            print(f"    Alternatives: {', '.join(interaction['alternative_drugs'])}")
else:
    print("No drug interactions found")

# Display safety recommendations
if interactions.get("safety_recommendations"):
    print("\nSafety Recommendations:")
    for rec in interactions["safety_recommendations"]:
        print(f"• {rec}")
```

### Laboratory Data Analysis

```python
import requests
import matplotlib.pyplot as plt
import pandas as pd

# Get laboratory results for a patient
tckn = "12345678901"
response = requests.get(f"http://localhost:8000/labs/{tckn}")
lab_data = response.json()

# Convert to DataFrame
df = pd.DataFrame(lab_data)

# Parse numeric values
df['numeric_value'] = pd.to_numeric(df['SONUC'], errors='coerce')
df['test_date'] = pd.to_datetime(df['TEST_TARIHI'])

# Filter for specific test
hemoglobin_data = df[df['TEST_ADI'].str.contains('Hemoglobin', case=False)]

if not hemoglobin_data.empty:
    # Plot trend chart
    plt.figure(figsize=(12, 6))
    plt.plot(hemoglobin_data['test_date'], hemoglobin_data['numeric_value'],
             marker='o', linewidth=2, markersize=8)
    plt.title(f"Hemoglobin Trends for TCKN {tckn}")
    plt.xlabel('Date')
    plt.ylabel('Hemoglobin (g/dL)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print(f"Hemoglobin Analysis for Patient {tckn}:")
    print(f"Average: {hemoglobin_data['numeric_value'].mean():.1f} g/dL")
    print(f"Range: {hemoglobin_data['numeric_value'].min():.1f}-{hemoglobin_data['numeric_value'].max():.1f} g/dL")
else:
    print(f"No hemoglobin data found for patient {tckn}")
```

## 🔧 Error Handling

### HTTP Status Codes

**Client Errors (4xx):**

```python
import requests
from requests.exceptions import HTTPError

try:
    response = requests.get("http://localhost:8000/patients/invalid")
    response.raise_for_status()
except HTTPError as e:
    if e.response.status_code == 404:
        print("Patient not found")
    elif e.response.status_code == 422:
        print("Invalid request parameters")
    else:
        print(f"HTTP Error: {e.response.status_code}")
```

### Timeout Handling

```python
import requests
from requests.exceptions import Timeout

try:
    # Set timeout to 30 seconds
    response = requests.post(
        "http://localhost:8000/analyze/diagnosis",
        json={
            "tckn": "12345678901",
            "chief_complaint": "Test complaint"
        },
        timeout=30
    )
    print("Diagnosis generated successfully")
except Timeout:
    print("Request timed out - please try again")
```

### Connection Errors

```python
import requests
from requests.exceptions import ConnectionError

try:
    response = requests.get("http://localhost:8000/health")
    print("API is accessible")
except ConnectionError:
    print("Cannot connect to API - check if server is running")
```

## ⚡ Performance Considerations

### Request Optimization

**Batch Operations:**

- Use single requests for multiple items when possible
- Implement client-side caching for frequently accessed data
- Use pagination for large datasets

**Efficient Data Loading:**

```python
# Good: Load specific patient data
response = requests.get(f"http://localhost:8000/patients/{tckn}")

# Avoid: Loading all patients
response = requests.get("http://localhost:8000/patients")  # May be slow
```

### Rate Limiting

**Recommendations:**

- Implement request throttling for bulk operations
- Add delays between AI model calls
- Cache AI responses when appropriate

```python
import time
import requests

# Add delay between AI requests
diagnosis_requests = [
    {"tckn": "12345678901", "complaint": "Headache"},
    {"tckn": "12345678902", "complaint": "Chest pain"}
]

for request in diagnosis_requests:
    response = requests.post(
        "http://localhost:8000/analyze/diagnosis",
        json=request
    )
    print(f"Diagnosis generated for {request['tckn']}")

    # Add delay between requests
    time.sleep(1)
```

## 📝 Monitoring and Logging

### Request Logging

The API logs all requests with:

- HTTP method and endpoint
- Response status codes
- Processing time
- Error details

### Health Monitoring

Regular health checks should monitor:

- Database connectivity
- AI service availability
- Response times
- Error rates

```python
import requests
import time

def monitor_api_health():
    """Monitor API health over time"""
    while True:
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=5)
            response_time = time.time() - start_time

            status = response.json().get("status", "unknown")
            print(f"API Status: {status}, Response Time: {response_time:.3f}s")

        except Exception as e:
            print(f"Health check failed: {e}")

        time.sleep(60)  # Check every minute
```

## 🔒 Security Considerations

### Data Validation

**Input Sanitization:**

- All inputs validated using Pydantic models
- SQL injection prevention through parameterized queries
- XSS protection through response encoding

### Error Information

**Security Best Practices:**

- Never expose sensitive information in error messages
- Log errors without including PHI
- Implement proper error handling without information disclosure

## 📞 Getting Support

### Troubleshooting

**Common Issues:**

1. **Connection Refused**: Check if API server is running
2. **Timeouts**: Increase timeout values for long operations
3. **Validation Errors**: Check request format and required fields
4. **500 Errors**: Check server logs for detailed error information

### Testing Tools

**Command Line Testing:**

```bash
# Test basic connectivity
curl -X GET http://localhost:8000/health

# Test patient search
curl -X GET "http://localhost:8000/patients/search?q=Test"

# Test AI diagnosis
curl -X POST http://localhost:8000/analyze/diagnosis \
  -H "Content-Type: application/json" \
  -d '{"tckn":"12345678901","chief_complaint":"Test"}'
```

**Python Testing:**

```python
import requests

def test_api_connectivity():
    """Test basic API connectivity"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        print("✅ API is accessible")
        return True
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_diagnosis_endpoint():
    """Test diagnosis generation endpoint"""
    request_data = {
        "tckn": "12345678901",
        "chief_complaint": "Test complaint for API testing"
    }

    try:
        response = requests.post(
            "http://localhost:8000/analyze/diagnosis",
            json=request_data,
            timeout=60  # Allow more time for AI processing
        )
        assert response.status_code == 200
        data = response.json()
        assert "differential_diagnosis" in data
        print("✅ Diagnosis endpoint working")
        return data
    except Exception as e:
        print(f"❌ Diagnosis endpoint failed: {e}")
        return None
```

---

**Last Updated:** November 2024
**Version:** 0.1.0
**API Version:** v1

For additional help, see the [user guides](../user-guides/README.md) or [deployment documentation](../deployment/README.md).
