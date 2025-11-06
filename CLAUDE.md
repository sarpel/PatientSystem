# Claude Code Guidelines for Clinical AI Assistant Project

This document provides AI agents (Claude Code, GitHub Copilot, etc.) with project-specific context, patterns, and critical lessons learned to prevent common mistakes.

## 🎯 Project Context

**Project**: Clinical AI Assistant - Family medicine decision support system
**Tech Stack**:
- Backend: Python 3.10.11, FastAPI, SQLAlchemy
- Frontend: React 18 + TypeScript, Vite, Zustand, Tailwind CSS
- Database: MS SQL Server (READ-ONLY) + SQLite (app data)
- AI: Ollama (local), Claude, GPT, Gemini

## 🚨 Critical Rules - ALWAYS Verify Before Assuming

### Rule 1: Environment Values - NEVER GUESS

**❌ WRONG**: Assuming ODBC Driver 17 is installed because it's "standard"
**✅ RIGHT**: Check installed drivers before configuring

```python
# Always verify what's actually installed:
import pyodbc
print(pyodbc.drivers())  # Lists: SQL Server, SQL Server Native Client 11.0, ODBC Driver 11 for SQL Server
```

**Lesson Learned**: In November 2025, we had a production issue where:
- `.env` file specified `driver=ODBC+Driver+17+for+SQL+Server`
- System only had `ODBC Driver 11 for SQL Server` installed
- Result: "Data source name not found" errors
- Fix: Changed `.env` to use Driver 11

**Action Required**: Before configuring database connections, run:
```bash
python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"
```

### Rule 2: API Contract Synchronization

**❌ WRONG**: Changing backend API response format without updating frontend
**✅ RIGHT**: Coordinate API contract changes across both layers

**Lesson Learned**: Frontend crash issue on 2025-11-06:
- Backend changed from uppercase field names (`TCKN`, `ADI`, `SOYAD`) to lowercase (`tckn`, `name`, `age`)
- Frontend still expected uppercase fields
- Result: Component crashed with undefined field access
- Fix: Updated `PatientSearch.tsx` to match new API format

**Action Required**: When modifying API responses:
1. Document the change in this file
2. Search for all frontend usages: `grep -r "TCKN\|ADI\|SOYAD" frontend/src/`
3. Update TypeScript interfaces in `frontend/src/services/api.ts`
4. Test end-to-end before committing

### Rule 3: Naming Convention Consistency

**Current Conventions**:

| Layer | Convention | Example |
|-------|-----------|---------|
| Database Columns | UPPERCASE_SNAKE_CASE | `HASTA_KIMLIK_NO`, `DOGUM_TARIHI` |
| Python Variables | lowercase_snake_case | `patient_id`, `birth_date` |
| API JSON Keys | lowercase | `tckn`, `name`, `age`, `gender` |
| TypeScript | camelCase | `patientId`, `birthDate` |
| React Components | PascalCase | `PatientSearch`, `DiagnosisPanel` |

**Action Required**: When adding new fields:
1. Check existing patterns in the target layer
2. Follow the established convention
3. Update API documentation if changing contracts

### Rule 4: Port Configuration

**Current Configuration** (as of 2025-11-06):
- Backend API: Port 8080 (not 8000)
- Frontend Dev: Port 5174 (Vite fallback when 5173 is busy)
- Frontend Prod: Static files served by backend
- Ollama: Port 11434

**Action Required**:
- Check `.env` for `API_PORT=8080`
- Frontend proxy configured for `/api` → `http://localhost:8080`
- Update README.md if ports change

## 📁 File Organization

### Where to Create Files

**Documentation** → `docs/` or project root (for important docs like this)
**Test Files** → `tests/` (not scattered next to source files)
**Utility Scripts** → `scripts/` (batch files, Python utilities)
**Frontend Tests** → `frontend/src/__tests__/` or `frontend/tests/`

**❌ NEVER**: Create `test_*.py` next to source files, `debug.sh` in random locations
**✅ ALWAYS**: Organize by purpose and maintain clean structure

## 🔧 Configuration Management

### Environment Variables (.env)

**Current Active Configuration**:
```env
# Database - VERIFIED WORKING as of 2025-11-06
DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes
DB_SERVER=localhost\HIZIR
DB_NAME=TestDB
DB_DRIVER=ODBC Driver 11 for SQL Server

# AI Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL
ANTHROPIC_API_KEY=<redacted>
OPENAI_API_KEY=<redacted>
GOOGLE_API_KEY=<redacted>

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
API_PORT=8080
```

### Database Connection Testing

**Before making changes**, test connection:
```bash
python test_db_connection.py
```

This script tests multiple connection string formats and reports which ones work.

## 🔄 API Response Formats

### Patient Search API

**Endpoint**: `GET /api/v1/patients/search?q={query}&limit={limit}`

**Response Format** (Current as of 2025-11-06):
```json
{
  "query": "search_term",
  "count": 2,
  "patients": [
    {
      "tckn": "12345678901",
      "name": "Ahmet Yılmaz",  // Combined first + last name
      "age": 45,               // Calculated from birth_date
      "gender": "E",           // E=Male, K=Female
      "last_visit": null       // Placeholder for future feature
    }
  ]
}
```

**Frontend Usage**:
```typescript
// File: frontend/src/pages/PatientSearch.tsx
// Access fields as: patient.tckn, patient.name, patient.age, patient.gender
```

### Patient Details API

**Endpoint**: `GET /api/v1/patients/{tckn}`

**Response Format**: See `src/clinical/patient_summarizer.py` for full schema

## 🧪 Testing Patterns

### Backend Testing

```bash
# Test database connection
python test_db_connection.py

# Test API endpoints (when implemented)
pytest tests/ -v

# Check ODBC drivers
python -c "import pyodbc; print(pyodbc.drivers())"
```

### Frontend Testing

```bash
cd frontend

# Run dev server (auto-reload)
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check  # When implemented
```

## 🐛 Common Issues and Solutions

### Issue 1: "Data source name not found"

**Symptoms**: Backend fails to connect to database, error message:
```
(pyodbc.InterfaceError) ('IM002', '[IM002] [Microsoft][ODBC Driver Manager]
Data source name not found and no default driver specified (0) (SQLDriverConnect)')
```

**Root Cause**: `.env` specifies ODBC driver that's not installed

**Solution**:
1. Check installed drivers: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Update `.env` DATABASE_URL to use installed driver
3. Restart backend server (uvicorn auto-reloads)

### Issue 2: Frontend Blank White Screen

**Symptoms**:
- Patient search works in backend logs (200 OK responses)
- Frontend page goes completely blank when results load
- Browser console shows no errors (page freezes before errors can display)

**Root Cause**: Component tries to access undefined fields from API response

**Solution**:
1. Check backend API response format (logs or `/docs` endpoint)
2. Check frontend component field access (`patient.TCKN` vs `patient.tckn`)
3. Update TypeScript interfaces to match API
4. Test with browser DevTools Network tab

**Prevention**: When changing API response format, update:
- Backend route handler (`src/api/routes/patient.py`)
- Frontend TypeScript interface (`frontend/src/services/api.ts`)
- Frontend component usage (search for old field names)

### Issue 3: Frontend Running on Unexpected Port

**Symptoms**: Vite dev server starts on 5174 instead of 5173

**Root Cause**: Port 5173 is already in use (previous dev server, another app)

**Solution**:
- Check Vite output for actual port: `Local:   http://localhost:5174/`
- Frontend automatically handles this via proxy config
- No action needed unless port conflict persists

## 📝 Documentation Standards

### Code Comments

**Python**:
```python
def search_patients(q: str, limit: int = 20):
    """
    Search for patients by name or TCKN.

    Args:
        q: Search query (minimum 2 characters)
        limit: Maximum number of results (default 20, max 100)

    Returns:
        List of matching patients with basic information
        Format: {tckn, name, age, gender, last_visit}

    Raises:
        HTTPException: 500 if database error occurs
    """
```

**TypeScript**:
```typescript
/**
 * Search for patients by name or TCKN
 * @param query - Search term (minimum 2 characters)
 * @param limit - Maximum results to return (default 20)
 * @returns Promise resolving to array of patient objects
 */
async searchPatients(query: string, limit: number = 20): Promise<Patient[]>
```

### Git Commit Messages

**Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, refactor, test, chore

**Example**:
```
fix: update frontend to use new API response format

- Changed patient field access from uppercase to lowercase
- Updated PatientSearch.tsx to use combined name field
- Fixed age display to use pre-calculated age from backend

Fixes blank white screen issue when displaying search results
```

## 🚀 Deployment Checklist

Before deploying changes:

- [ ] Test database connection with `test_db_connection.py`
- [ ] Verify ODBC driver matches `.env` configuration
- [ ] Run backend: `uvicorn src.api.fastapi_app:app --reload`
- [ ] Run frontend: `cd frontend && npm run dev`
- [ ] Test patient search end-to-end
- [ ] Check browser console for errors
- [ ] Verify API responses in Network tab
- [ ] Run linting (if configured)
- [ ] Update documentation if API changed
- [ ] Commit with descriptive message
- [ ] Test after deployment

## 🔍 Debugging Commands

### Quick Diagnostics

```bash
# Check Python version
python --version  # Should be 3.10.11+

# Check Node version
node --version  # Should be 18+

# Check installed Python packages
pip list | grep -E "fastapi|sqlalchemy|pyodbc"

# Check ODBC drivers
python -c "import pyodbc; print('\n'.join(pyodbc.drivers()))"

# Test database connection
python test_db_connection.py

# Check if ports are in use
netstat -ano | findstr "8080"  # Backend
netstat -ano | findstr "5173"  # Frontend

# View backend logs
# Check terminal where uvicorn is running

# View frontend logs
# Check browser DevTools Console tab
```

### Backend Debugging

```python
# Add to any route for detailed logging
from loguru import logger

logger.debug(f"Request params: {request.query_params}")
logger.debug(f"Response data: {response_data}")
```

### Frontend Debugging

```typescript
// Add to any component
import { logger } from "../utils/logger";

logger.debug("Component rendered with props:", props);
logger.debug("API response:", data);
```

## 📚 Further Reading

- **API Documentation**: http://localhost:8080/docs (when backend running)
- **React Query Docs**: https://tanstack.com/query/latest (if implemented)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

## 🔄 Changelog

### 2025-11-06
- Fixed ODBC driver mismatch (Driver 17 → Driver 11)
- Fixed frontend crash by updating API field names
- Updated API response format documentation
- Created this CLAUDE.md file for future reference

---

**Last Updated**: 2025-11-06
**Maintained By**: AI agents assisting with this project should update this file when discovering new patterns or issues.
