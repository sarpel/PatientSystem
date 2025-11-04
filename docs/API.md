# API Documentation

REST API reference for the Clinical AI Assistant.

## Base URL

**Development**: `http://localhost:8000`

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs (recommended - interactive testing)
- **ReDoc**: http://localhost:8000/redoc (cleaner reading experience)

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT, PATCH, DELETE) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## Health Check

### GET /api/health

Check API server status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "database": "connected",
  "ai_providers": {
    "ollama": "available",
    "anthropic": "available"
  }
}
```

---

## Patient Management

### List Patients

**GET** `/api/patients?limit=50&offset=0&search=John`

**Query Parameters**:
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Skip results (default: 0)
- `search` (optional): Search by name

**Response**:
```json
{
  "patients": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1990-01-15",
      "gender": "M",
      "contact_info": { }
    }
  ],
  "total": 1
}
```

### Get Patient

**GET** `/api/patients/{patient_id}`

**Response**:
```json
{
  "id": 123,
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "M",
  "contact_info": {
    "phone": "555-0123",
    "email": "john@example.com"
  }
}
```

### Create Patient

**POST** `/api/patients`

**Request Body**:
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-03-20",
  "gender": "F",
  "contact_info": {
    "phone": "555-0456",
    "email": "jane@example.com"
  }
}
```

**Response** (201 Created):
```json
{
  "id": 124,
  "first_name": "Jane",
  "last_name": "Smith",
  ...
}
```

### Update Patient

**PUT** `/api/patients/{patient_id}`

**Request Body**: Same as Create Patient

**Response**: Updated patient object

### Delete Patient

**DELETE** `/api/patients/{patient_id}`

**Response**: 204 No Content

---

## Visit Management

### Get Patient Visits

**GET** `/api/patients/{patient_id}/visits?limit=20`

**Response**:
```json
{
  "visits": [
    {
      "id": 456,
      "patient_id": 123,
      "visit_date": "2024-01-15",
      "chief_complaint": "Persistent cough",
      "diagnosis": "Acute bronchitis",
      "treatment_plan": "Rest, fluids",
      "medications": [ ],
      "lab_results": [ ]
    }
  ]
}
```

### Create Visit

**POST** `/api/patients/{patient_id}/visits`

**Request Body**:
```json
{
  "visit_date": "2024-01-16",
  "chief_complaint": "Headache and fever",
  "symptoms": ["headache", "fever (101.5°F)", "fatigue"],
  "vital_signs": {
    "temperature": "101.5",
    "blood_pressure": "120/80"
  }
}
```

**Response** (201 Created): Visit object with ID

---

## AI-Powered Features

### Diagnosis Assistance

**POST** `/api/ai/diagnose`

Get AI-powered diagnosis suggestions based on symptoms.

**Request Body**:
```json
{
  "patient_id": 123,
  "chief_complaint": "Severe chest pain",
  "symptoms": [
    "chest pain (8/10 severity)",
    "shortness of breath",
    "radiating pain to left arm"
  ],
  "duration": "30 minutes",
  "medical_history": ["hypertension"],
  "vital_signs": {
    "blood_pressure": "160/95",
    "heart_rate": "110"
  }
}
```

**Response**:
```json
{
  "diagnosis_suggestions": [
    {
      "condition": "Acute Myocardial Infarction",
      "confidence": "high",
      "icd10_code": "I21.9",
      "urgency": "critical",
      "reasoning": "Classic signs of acute MI...",
      "recommended_actions": [
        "Call 911 immediately",
        "Administer aspirin if available"
      ]
    }
  ],
  "red_flags": [
    "Chest pain with arm radiation - cardiac event likely"
  ],
  "ai_provider": "claude-sonnet-4.5"
}
```

### Treatment Recommendations

**POST** `/api/ai/treatment`

Get AI-powered treatment recommendations.

**Request Body**:
```json
{
  "patient_id": 123,
  "diagnosis": "Type 2 Diabetes Mellitus",
  "icd10_code": "E11.9",
  "current_medications": [
    {
      "name": "Lisinopril",
      "dosage": "10mg",
      "frequency": "daily"
    }
  ],
  "allergies": ["sulfa drugs"],
  "comorbidities": ["hypertension"],
  "lab_results": {
    "hba1c": "8.2"
  }
}
```

**Response**:
```json
{
  "treatment_plan": {
    "medications": [
      {
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "twice daily with meals",
        "reasoning": "First-line therapy for Type 2 DM"
      }
    ],
    "lifestyle_modifications": [
      "Low glycemic index diet",
      "30 minutes exercise 5 days/week"
    ],
    "monitoring": [
      "Self-monitor blood glucose daily",
      "HbA1c recheck in 3 months"
    ]
  },
  "drug_interactions": [],
  "ai_provider": "medgemma:4b"
}
```

---

## Medication Management

### Search Drugs

**GET** `/api/drugs/search?query=aspirin&limit=10`

**Response**:
```json
{
  "drugs": [
    {
      "name": "Aspirin",
      "generic_name": "Acetylsalicylic Acid",
      "drug_class": "NSAID",
      "common_dosages": ["81mg", "325mg"],
      "indications": ["Pain relief", "Fever reduction"]
    }
  ]
}
```

### Check Drug Interactions

**POST** `/api/drugs/interactions`

**Request Body**:
```json
{
  "medications": ["Warfarin", "Aspirin", "Ibuprofen"]
}
```

**Response**:
```json
{
  "interactions": [
    {
      "drugs": ["Warfarin", "Aspirin"],
      "severity": "major",
      "description": "Increased bleeding risk",
      "recommendation": "Avoid combination or monitor INR"
    }
  ]
}
```

---

## Laboratory Results

### Get Lab Results

**GET** `/api/patients/{patient_id}/labs?start_date=2024-01-01`

**Response**:
```json
{
  "lab_results": [
    {
      "id": 789,
      "test_date": "2024-01-15",
      "test_name": "Complete Blood Count",
      "results": {
        "wbc": {
          "value": 7.5,
          "unit": "K/uL",
          "reference_range": "4.5-11.0",
          "status": "normal"
        }
      }
    }
  ]
}
```

### Add Lab Results

**POST** `/api/patients/{patient_id}/labs`

**Request Body**:
```json
{
  "test_date": "2024-01-16",
  "test_name": "Lipid Panel",
  "results": {
    "total_cholesterol": {
      "value": 220,
      "unit": "mg/dL",
      "reference_range": "<200"
    }
  }
}
```

**Response** (201 Created): Lab result object

---

## Analytics

### Lab Trends

**GET** `/api/analytics/lab-trends?patient_id=123&test_name=HbA1c&period=6months`

**Response**:
```json
{
  "test_name": "HbA1c",
  "data_points": [
    {"date": "2023-07-15", "value": 9.2},
    {"date": "2023-10-15", "value": 8.5},
    {"date": "2024-01-15", "value": 7.8}
  ],
  "trend": "improving",
  "latest_value": 7.8,
  "target_range": "< 7.0"
}
```

### Medication Adherence

**GET** `/api/analytics/medication-adherence?patient_id=123&medication=Metformin`

**Response**:
```json
{
  "medication": "Metformin",
  "adherence_rate": 0.85,
  "period": "90 days",
  "doses_prescribed": 180,
  "doses_taken": 153
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| PATIENT_NOT_FOUND | Patient ID doesn't exist |
| VISIT_NOT_FOUND | Visit ID doesn't exist |
| VALIDATION_ERROR | Request data validation failed |
| DATABASE_ERROR | Database operation failed |
| AI_PROVIDER_ERROR | AI service unavailable |

---

## Testing the API

### Using Swagger UI

1. Start the server: `uvicorn src.api.fastapi_app:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click on any endpoint
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"

### Using curl

```bash
# Get health status
curl http://localhost:8000/api/health

# List patients
curl http://localhost:8000/api/patients

# Create patient
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "M"
  }'
```

### Using Python

```python
import requests

# Get patients
response = requests.get("http://localhost:8000/api/patients")
patients = response.json()

# Create patient
patient_data = {
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1985-03-20",
    "gender": "F"
}
response = requests.post(
    "http://localhost:8000/api/patients",
    json=patient_data
)
new_patient = response.json()
```

---

## Support

- Interactive docs: http://localhost:8000/docs
- Check logs in `logs/` directory for detailed error information
- Review [Configuration Guide](CONFIGURATION.md) for setup issues
