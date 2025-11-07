# API Changelog

This document tracks all API contract changes to help maintain frontend-backend synchronization.

## Format

Each entry should include:
- **Date**: When the change was made
- **Endpoint**: Which API endpoint changed
- **Type**: Breaking / Non-breaking / Deprecation
- **Change**: What changed
- **Migration**: How to update client code
- **Reason**: Why the change was necessary

---

## [2025-11-06] Patient Search Response Format Change

### Endpoint
`GET /api/v1/patients/search`

### Type
**BREAKING CHANGE** ⚠️

### Previous Format
```json
{
  "patients": [
    {
      "TCKN": "12345678901",
      "ADI": "Ahmet",
      "SOYADI": "Yılmaz",
      "DOGUM_TARIHI": "1978-05-15",
      "CINSIYET": "E",
      "TELEFON": "5551234567"
    }
  ]
}
```

### New Format
```json
{
  "query": "search_term",
  "count": 1,
  "patients": [
    {
      "tckn": "12345678901",
      "name": "Ahmet Yılmaz",
      "age": 45,
      "gender": "E",
      "last_visit": null
    }
  ]
}
```

### Changes Made

1. **Field Names**: Changed from uppercase to lowercase
   - `TCKN` → `tckn`
   - `CINSIYET` → `gender`

2. **Combined Fields**: Merged separate name fields
   - `ADI` + `SOYADI` → `name` (single combined field)

3. **Calculated Fields**: Age now calculated server-side
   - `DOGUM_TARIHI` (birth date) → `age` (years, calculated)

4. **Removed Fields**:
   - `TELEFON` (phone) - Not included in current version

5. **Added Fields**:
   - `last_visit` - Placeholder for future feature (currently null)
   - `query` - Echo back search query
   - `count` - Number of results returned

### Migration Guide

#### TypeScript Interface Update

**Before**:
```typescript
interface Patient {
  TCKN: string;
  ADI: string;
  SOYADI: string;
  DOGUM_TARIHI?: string;
  CINSIYET?: "E" | "K";
  TELEFON?: string;
}
```

**After**:
```typescript
interface PatientSearchResult {
  tckn: string;
  name: string;
  age: number | null;
  gender: "E" | "K" | null;
  last_visit: null;
}

interface PatientSearchResponse {
  query: string;
  count: number;
  patients: PatientSearchResult[];
}
```

#### Component Update

**Before**:
```typescript
// PatientSearch.tsx
{patients.map((patient) => (
  <div key={patient.TCKN}>
    <h3>{patient.ADI} {patient.SOYADI}</h3>
    <span>TCKN: {patient.TCKN}</span>
    <span>Age: {calculateAge(patient.DOGUM_TARIHI)}</span>
    <span>Gender: {patient.CINSIYET === "E" ? "Male" : "Female"}</span>
    {patient.TELEFON && <span>Phone: {patient.TELEFON}</span>}
  </div>
))}
```

**After**:
```typescript
// PatientSearch.tsx
{patients.map((patient) => (
  <div key={patient.tckn}>
    <h3>{patient.name}</h3>
    <span>TCKN: {patient.tckn}</span>
    {patient.age !== null && <span>Age: {patient.age} years</span>}
    <span>Gender: {patient.gender === "E" ? "Male" : "Female"}</span>
    {/* Phone number removed from API response */}
  </div>
))}
```

### Reason for Change

1. **ODBC Compatibility**: Original query using `SELECT *` caused SQL type -150 errors with certain column types
2. **Performance**: Selecting specific columns improves query performance
3. **API Convention**: Lowercase field names follow REST API best practices
4. **Reduced Computation**: Age calculated once on server instead of on every render
5. **Simplified Frontend**: Combined name field reduces frontend logic

### Affected Files

**Backend**:
- `src/api/routes/patient.py` - Modified query to select specific columns

**Frontend**:
- `frontend/src/pages/PatientSearch.tsx` - Updated component to use new fields
- `frontend/src/services/api.ts` - Should update TypeScript interfaces

### Backend Implementation

```python
# File: src/api/routes/patient.py
# Lines: 34-79

# Select only the columns we need to avoid ODBC type compatibility issues
query = session.query(
    Patient.HASTA_KIMLIK_NO,
    Patient.AD,
    Patient.SOYAD,
    Patient.DOGUM_TARIHI,
    Patient.CINSIYET
)

# ... query filters ...

# Format results with calculated age and combined name
for patient in patients:
    # Calculate age from birth date
    age = None
    if patient.DOGUM_TARIHI:
        from datetime import date
        today = date.today()
        age = today.year - patient.DOGUM_TARIHI.year - (
            (today.month, today.day) < (patient.DOGUM_TARIHI.month, patient.DOGUM_TARIHI.day)
        )

    # Build full name
    full_name = f"{patient.AD or ''} {patient.SOYAD or ''}".strip()

    results.append({
        "tckn": str(patient.HASTA_KIMLIK_NO) if patient.HASTA_KIMLIK_NO else None,
        "name": full_name,
        "age": age,
        "gender": patient.CINSIYET,
        "last_visit": None,
    })
```

### Testing

**Manual Test**:
```bash
# Test API directly
curl "http://localhost:8080/api/v1/patients/search?q=test&limit=5"

# Expected response format:
{
  "query": "test",
  "count": 5,
  "patients": [
    {
      "tckn": "...",
      "name": "Full Name",
      "age": 45,
      "gender": "E",
      "last_visit": null
    }
  ]
}
```

**Frontend Test**:
1. Open http://localhost:5174/search
2. Search for patient name or TCKN
3. Verify results display correctly
4. Check browser console for errors
5. Inspect Network tab for response format

---

## Future API Changes

### Planned Deprecations

None currently planned.

### Upcoming Features

1. **Last Visit Date**: The `last_visit` field is currently a placeholder. Future implementation will include:
   ```json
   {
     "last_visit": {
       "date": "2025-11-01T10:30:00Z",
       "reason": "Routine checkup",
       "doctor": "Dr. Smith"
     }
   }
   ```

2. **Pagination**: Large result sets may require pagination:
   ```json
   {
     "query": "test",
     "count": 100,
     "page": 1,
     "page_size": 20,
     "total_pages": 5,
     "patients": [...]
   }
   ```

---

## API Versioning Strategy

### Current Version
**v1** - `/api/v1/*`

### Version Policy

- **Non-Breaking Changes**: Can be added to current version (v1)
  - New optional fields
  - New endpoints
  - Performance improvements

- **Breaking Changes**: Require new version (v2)
  - Field name changes
  - Field type changes
  - Field removal
  - Response structure changes
  - Endpoint URL changes

### Backward Compatibility

When introducing v2:
- Maintain v1 endpoints for 6 months minimum
- Add deprecation warnings to v1 responses
- Document migration path clearly
- Provide migration tools if complex

---

## Change Request Process

### Before Making API Changes

1. **Document the change** in this file first
2. **Assess impact**:
   - Is it breaking?
   - Who uses this endpoint?
   - What frontend code needs updating?
3. **Plan migration**:
   - Can we make it non-breaking?
   - Do we need a new version?
   - What's the rollout strategy?

### After Making API Changes

1. **Update documentation**:
   - This file (API_CHANGELOG.md)
   - CLAUDE.md (if new patterns)
   - README.md (if setup affected)
2. **Update frontend**:
   - TypeScript interfaces
   - Component usage
   - Test cases
3. **Test thoroughly**:
   - Backend tests
   - Frontend tests
   - End-to-end tests
4. **Deploy coordinated**:
   - Backend first (if backward compatible)
   - Frontend immediately after
   - Monitor for errors

---

## API Documentation

For complete API documentation, see:
- **Interactive Docs**: http://localhost:8080/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8080/redoc (ReDoc)

---

**Last Updated**: 2025-11-06
**Maintained By**: Update this file whenever making API changes
