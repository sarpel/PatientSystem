# Copilot Instructions for Clinical AI Assistant

## Repository Overview

**Project**: Clinical AI Assistant - AI-powered family medicine decision support system
**Size**: Medium (~50 source files, dual database architecture)
**Languages**: Python (Backend), TypeScript/React (Frontend)
**Purpose**: Patient search, AI-assisted diagnosis, treatment planning, drug interaction checking, and lab result tracking

### Tech Stack
- **Backend**: Python 3.10.11+, FastAPI, SQLAlchemy, Loguru
- **Frontend**: React 18, TypeScript, Vite, Zustand (state), Tailwind CSS
- **Database**: MS SQL Server 2014/2022 (READ-ONLY patient data) + SQLite (app data, ICD codes)
- **AI Integration**: Ollama (local/free), Claude Sonnet, GPT-5, Gemini
- **Ports**: Backend API on 8080, Frontend dev on 5173

## Critical Build & Setup Instructions

### Prerequisites Verification (ALWAYS RUN FIRST)
```bash
# Check installed versions
python3 --version  # Need 3.10.11+
node --version     # Need 18+
npm --version      # Comes with Node.js

# CRITICAL: Check ODBC drivers (Windows only, skip on Linux/Mac)
python3 -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"
# Example output: ['SQL Server', 'ODBC Driver 11 for SQL Server']
# Note the exact driver name - you'll need it for .env
```

### Backend Setup (Python)

**Step 1: Virtual Environment**
```bash
# Always create venv in project root
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate.bat
```

**Step 2: Install Dependencies**
```bash
# ALWAYS upgrade pip first
pip install --upgrade pip

# Install requirements (takes ~2-3 minutes)
pip install -r requirements.txt

# Expected result: ~50 packages installed including:
# - fastapi, uvicorn (web framework)
# - sqlalchemy, pyodbc (database)
# - anthropic, openai, google-generativeai (AI)
# - loguru (logging)
# - pytest (testing)
```

**Step 3: Configure Environment**
```bash
# Copy example config
cp .env.example .env

# CRITICAL: Edit .env with your ACTUAL ODBC driver
# Use the driver name from prerequisites check
# Example for ODBC Driver 11:
# DATABASE_URL=mssql+pyodbc://localhost\INSTANCE/DBName?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes

# For ODBC Driver 18 (newer), add TrustServerCertificate:
# DATABASE_URL=...driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
```

**Step 4: Initialize App Database**
```bash
# REQUIRED: Migrate ICD-10 codes to SQLite (creates data/app.db)
python scripts/migrate_icd_codes.py

# Expected output: "Migration completed successfully"
# This creates: data/app.db (SQLite database)
```

**Step 5: Test Database Connection (OPTIONAL but RECOMMENDED)**
```bash
# Test SQL Server connection before starting app
python test_db_connection.py

# If this fails, fix .env before proceeding
# Common issue: Wrong ODBC driver specified
```

### Frontend Setup (React/TypeScript)

**Step 1: Install Dependencies**
```bash
cd frontend

# Install npm packages (takes ~30-60 seconds)
npm install

# Expected warnings (IGNORE THESE - they are harmless):
# - deprecated rimraf, inflight, glob, eslint
# - 2 moderate severity vulnerabilities (don't fix unless required)
```

**Step 2: Build Production Bundle (OPTIONAL)**
```bash
# Still in frontend/ directory
npm run build

# Known issue: TypeScript errors about unused variables
# These are lint warnings, not build blockers
# The build will complete despite TS6133 warnings

# Output: frontend/dist/ directory with production files
```

**Step 3: Lint Check (OPTIONAL)**
```bash
# Check code quality
npm run lint

# Known issues (as of Nov 2025):
# - PatientSearch.tsx: unused 'Patient' import, 'calculateAge' var
# - Several 'any' type warnings (technical debt, not blockers)
# - 10 errors, 1 warning total - existing issues, not your fault
```

### Running the Application

**Method 1: Quick Start (Windows, RECOMMENDED)**
```bash
# From project root
scripts\quickstart.bat

# This script:
# 1. Checks prerequisites
# 2. Starts backend in new window (port 8080)
# 3. Starts frontend in new window (port 5173)
# 4. Opens browser to http://localhost:5173
# 5. Waits 5 seconds for backend, 8 seconds for frontend
```

**Method 2: Manual Start (All Platforms)**
```bash
# Terminal 1 - Backend
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
uvicorn src.api.fastapi_app:app --reload --host localhost --port 8080

# Terminal 2 - Frontend
cd frontend
npm run dev

# Access:
# - Frontend UI: http://localhost:5173
# - Backend API Docs: http://localhost:8080/docs
# - Backend Alternative Docs: http://localhost:8080/redoc
```

**Method 3: Using Scripts**
```bash
# Windows batch scripts available:
scripts\install.bat          # Full backend setup
scripts\setup-frontend.bat   # Full frontend setup
scripts\run_web.bat          # Start backend only
scripts\run_tests.bat        # Run pytest suite
```

### Testing

**Backend Tests**
```bash
# Activate venv first
source venv/bin/activate

# Run pytest with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Note: No tests/ directory exists yet (as of Nov 2025)
# If you create tests, follow this pattern
# Coverage report: htmlcov/index.html
```

**Database Connection Test**
```bash
# Specific test for database connectivity
python test_db_connection.py

# Tests both localhost and computer name connections
# Shows SQL Server version, database name, user
```

**Frontend Tests**
```bash
cd frontend

# No test framework configured yet
# If adding tests, use: npm install --save-dev vitest @testing-library/react
```

### Linting & Code Quality

**Python (Backend)**
```bash
# Black formatter (if needed)
black src/

# isort (import sorting)
isort src/

# Ruff (fast linter, installed but no config)
ruff src/
```

**TypeScript (Frontend)**
```bash
cd frontend

# ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# TypeScript check (part of build)
npx tsc --noEmit
```

## Project Layout & Architecture

### Directory Structure
```
PatientSystem/
├── .github/                    # GitHub configuration (this file)
├── config/                     # Configuration templates
│   └── ai_models.yaml.example  # AI provider configuration
├── data/                       # SQLite app database (created by migration)
│   └── app.db                 # ICD codes, logs, sessions
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/        # UI components (Layout, LabCharts, etc.)
│   │   ├── pages/            # Route pages (PatientSearch, Dashboard, etc.)
│   │   ├── services/         # API client (api.ts with axios)
│   │   ├── stores/           # Zustand state management
│   │   └── utils/            # Logger and helpers
│   ├── dist/                 # Production build output
│   ├── vite.config.ts        # Vite bundler config
│   ├── tsconfig.json         # TypeScript compiler config
│   ├── tailwind.config.js    # Tailwind CSS config
│   └── package.json          # Frontend dependencies
├── scripts/                   # Setup and utility scripts
│   ├── install.bat           # Backend setup (Windows)
│   ├── quickstart.bat        # Start both services (Windows)
│   ├── setup-frontend.bat    # Frontend setup (Windows)
│   ├── migrate_icd_codes.py  # ICD-10 migration script
│   └── *.sh                  # Linux/Mac equivalents
├── src/                      # Python backend source
│   ├── api/                  # FastAPI application
│   │   ├── fastapi_app.py   # Main app, CORS, middleware, exception handlers
│   │   └── routes/          # API endpoints (patient, diagnosis, treatment, etc.)
│   ├── clinical/            # Clinical logic modules
│   │   ├── diagnosis_engine.py     # AI-powered diagnosis
│   │   ├── treatment_engine.py     # Treatment planning
│   │   ├── drug_interaction.py     # Drug safety checks
│   │   ├── lab_analyzer.py        # Lab result analysis
│   │   └── prompt_builder.py      # AI prompt templates
│   ├── database/            # Database layers
│   │   ├── connection.py    # MSSQL connection (READ-ONLY)
│   │   ├── app_database.py  # SQLite app database
│   │   └── dependencies.py  # FastAPI dependency injection
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── patient.py       # Patient, demographics
│   │   ├── visit.py         # Visits, diagnoses
│   │   └── clinical.py      # Labs, medications
│   ├── ai/                  # AI provider integrations
│   │   ├── router.py        # Smart routing by complexity
│   │   └── *_client.py      # Provider-specific clients
│   ├── config/              # Settings and configuration
│   └── utils/               # Shared utilities
├── requirements.txt         # Python dependencies
├── package.json            # Root npm config (minimal)
├── .env.example            # Environment template
├── .gitignore              # Git exclusions
└── Documentation files:
    ├── README.md           # User guide (Turkish)
    ├── AGENTS.md           # AI agent guidelines (481 lines)
    ├── CLAUDE.md           # Project patterns (387 lines)
    ├── TROUBLESHOOTING.md  # Issue solutions (522 lines)
    ├── IMPLEMENTATION_SUMMARY.md  # Recent changes
    └── API_CHANGELOG.md    # API version history
```

### Key Configuration Files

**Backend Configuration:**
- `.env` - Environment variables (NEVER commit this)
- `.env.example` - Template with default values
- `requirements.txt` - Python dependencies (~35 packages)
- `src/config/settings.py` - Application settings (loaded from .env)

**Frontend Configuration:**
- `frontend/package.json` - Dependencies and scripts
- `frontend/vite.config.ts` - Dev server, proxy to backend (/api → localhost:8080)
- `frontend/tsconfig.json` - TypeScript: strict mode, ES2020, path aliases (@/*)
- `frontend/tailwind.config.js` - CSS framework configuration
- `frontend/.eslintrc.cjs` - ESLint rules

**Database Configuration:**
- Main DB: MS SQL Server (READ-ONLY, patient clinical data)
- App DB: SQLite at data/app.db (READ-WRITE, ICD codes, logs)
- Connection: Windows Authentication (trusted_connection=yes)
- Pool: 10 connections, 20 max overflow

### API Endpoints (FastAPI)

**Base URL:** http://localhost:8080

**Health Check:**
- GET `/health` - API health status

**Patient APIs:**
- GET `/api/v1/patients/search?q={query}` - Search patients by name/TCKN
- GET `/api/v1/patients/{tckn}` - Get patient details
- GET `/api/v1/patients/{tckn}/visits` - Patient visit history

**Diagnosis APIs:**
- POST `/api/v1/analyze/diagnosis` - AI-powered differential diagnosis
  - Body: `{tckn, chief_complaint, model: 'claude'|'gpt'|'ollama'}`

**Treatment APIs:**
- POST `/api/v1/analyze/treatment` - Generate treatment plan
  - Body: `{tckn, diagnosis, model}`

**Lab APIs:**
- GET `/api/v1/labs/{tckn}` - Lab results for patient
- GET `/api/v1/labs/{tckn}?test=Hemoglobin` - Filter by test name

**Drug APIs:**
- POST `/api/v1/drugs/interactions` - Check drug interactions
  - Body: `{medications: [{name, dosage}]}`

**Documentation:**
- GET `/docs` - Swagger UI (interactive API docs)
- GET `/redoc` - ReDoc (alternative API docs)

### Naming Conventions (CRITICAL - Must Follow)

| Layer | Convention | Example |
|-------|-----------|---------|
| SQL Server Columns | UPPERCASE_SNAKE_CASE | `HASTA_KIMLIK_NO`, `DOGUM_TARIHI` |
| Python Variables | lowercase_snake_case | `patient_id`, `birth_date` |
| API JSON Keys | lowercase (no underscores) | `tckn`, `name`, `age`, `gender` |
| TypeScript Variables | camelCase | `patientId`, `birthDate` |
| React Components | PascalCase | `PatientSearch`, `DiagnosisPanel` |
| Database Tables | PascalCase | `Patient`, `Visit`, `LabResult` |

**Example: Patient Data Flow**
```
Database:     HASTA_KIMLIK_NO
   ↓
Python:       patient.tckn (or patient_id)
   ↓
API JSON:     {"tckn": "12345678901"}
   ↓
TypeScript:   patient.tckn (matches API)
```

## Common Issues & Solutions

### Issue 1: "Data source name not found" Error

**Symptoms:** Backend starts but crashes on database query, 500 errors on patient search

**Root Cause:** .env specifies ODBC driver not installed on system

**Solution:**
```bash
# 1. Check installed drivers
python3 -c "import pyodbc; print(pyodbc.drivers())"

# 2. Update .env to match installed driver
# If you see 'ODBC Driver 11 for SQL Server':
DATABASE_URL=mssql+pyodbc://localhost\INSTANCE/DB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes

# If you see 'ODBC Driver 17 for SQL Server':
DATABASE_URL=...driver=ODBC+Driver+17+for+SQL+Server&...

# 3. Restart backend (uvicorn auto-reloads on .env change)
```

**Prevention:** Always run driver check before configuring database

### Issue 2: Port Already in Use

**Symptoms:** "Address already in use" error on startup

**Solution:**
```bash
# Check what's using the port (Linux/Mac)
lsof -i :8080  # Backend
lsof -i :5173  # Frontend

# Windows
netstat -ano | findstr "8080"
netstat -ano | findstr "5173"

# Kill the process or use different port:
uvicorn src.api.fastapi_app:app --reload --port 8081
```

### Issue 3: Frontend Blank Screen After API Change

**Symptoms:** Frontend loads but shows blank page, console errors about undefined properties

**Root Cause:** API response format changed (e.g., field names) but frontend not updated

**Solution:**
```bash
# 1. Check browser console for errors (F12)
# 2. Verify API response format:
curl http://localhost:8080/api/v1/patients/search?q=test

# 3. Update TypeScript interfaces in frontend/src/services/api.ts
# 4. Update component code to match new field names
# 5. Test end-to-end before committing
```

**Prevention:** When changing API contracts:
1. Document change in API_CHANGELOG.md
2. Search frontend for old field names: `grep -r "OLD_FIELD" frontend/src/`
3. Update TypeScript interfaces first
4. Update components second
5. Test both backend API and frontend UI

### Issue 4: Frontend Build Fails with TypeScript Errors

**Symptoms:** `npm run build` shows TS6133 errors (unused variables)

**Current State:** Known issues exist (as of Nov 2025):
- PatientSearch.tsx: unused 'Patient' import, unused 'calculateAge' function
- Multiple files: 'any' type usage

**Solution:**
```bash
# These are warnings, build still completes
# If blocking your change, fix them:

# Remove unused imports
# Change 'any' to proper types
# Or suppress with: // @ts-ignore (last resort)

# Re-run build
npm run build
```

### Issue 5: Missing data/app.db File

**Symptoms:** "No such table: icd_codes" error, diagnosis fails

**Root Cause:** ICD migration script not run

**Solution:**
```bash
# Run migration (creates data/ dir and app.db)
python scripts/migrate_icd_codes.py

# Verify
ls -la data/app.db

# Should see: data/app.db (SQLite database)
```

### Issue 6: SQL Server Connection Timeout

**Symptoms:** "Login timeout expired", "Could not open connection"

**Solution:**
```bash
# 1. Check SQL Server service running (Windows)
services.msc  # Look for 'SQL Server (INSTANCE_NAME)'

# 2. Check SQL Server accepting connections
# SQL Server Configuration Manager → Network Configuration → TCP/IP (should be Enabled)

# 3. Increase timeout in .env
DB_TIMEOUT=60  # Default is 30 seconds

# 4. Test with different server names
# Try: localhost\INSTANCE, COMPUTERNAME\INSTANCE, or just COMPUTERNAME
```

### Issue 7: Ollama Model Not Found

**Symptoms:** "Model not found" error when using Ollama AI

**Solution:**
```bash
# 1. Check Ollama service running
# Windows: Check system tray for Ollama icon
# Linux/Mac: ollama serve

# 2. List installed models
ollama list

# 3. Pull required model
ollama pull medgemma:4b
# OR the model specified in .env:
ollama pull hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL

# 4. Verify OLLAMA_BASE_URL in .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b
```

## Important Rules for Code Changes

### Rule 1: Database is READ-ONLY
- Main SQL Server database is READ-ONLY (patient clinical data)
- NEVER attempt INSERT, UPDATE, DELETE on MSSQL tables
- Use SQLite app.db for application data (ICD codes, logs, sessions)
- All queries use `db.query()` with SELECT statements

### Rule 2: API Contract Synchronization
- When changing API response format, update BOTH backend and frontend
- Update TypeScript interfaces immediately after backend changes
- Document in API_CHANGELOG.md if breaking change
- Test end-to-end before committing

### Rule 3: Environment Variables
- Never commit .env file (in .gitignore)
- Always update .env.example when adding new variables
- Use src/config/settings.py to load environment variables
- Provide sensible defaults where possible

### Rule 4: FastAPI Dependency Injection
- Use `Depends(get_db)` for database sessions (auto-cleanup)
- Don't manually create SQLAlchemy sessions
- Example:
```python
from src.database.dependencies import get_db

@router.get("/patients/search")
async def search_patients(q: str, db: Session = Depends(get_db)):
    # db session automatically managed
    results = db.query(Patient).filter(...).all()
    return results
```

### Rule 5: Frontend State Management
- Use Zustand store (stores/useAppStore.ts) for global state
- Don't use multiple state management libraries
- Keep local state in components when appropriate (useState)

### Rule 6: Error Handling
- Backend: Let FastAPI global exception handler catch errors
- Log errors with Loguru: `logger.error(f"Message: {e}", exc_info=True)`
- Frontend: Use try/catch, log with logger utility
- Show user-friendly messages in UI

### Rule 7: Port Configuration
- Backend: Port 8080 (not 8000) - Check .env API_PORT
- Frontend Dev: Port 5173 (Vite default)
- Ollama: Port 11434 (default)
- Don't hardcode ports, use environment variables

## Validation & Testing Checklist

Before committing changes, verify:

**Backend Changes:**
- [ ] Virtual environment activated
- [ ] Code follows lowercase_snake_case convention
- [ ] API endpoints tested with curl or /docs
- [ ] Database queries are READ-ONLY (no INSERT/UPDATE/DELETE on MSSQL)
- [ ] Error handling present with logging
- [ ] Environment variables used (no hardcoded values)

**Frontend Changes:**
- [ ] npm install run (if dependencies changed)
- [ ] TypeScript types match API responses
- [ ] Browser console checked (F12) for errors
- [ ] Network tab verified API calls successful
- [ ] Component follows PascalCase convention
- [ ] State management uses Zustand store

**Database Changes:**
- [ ] NEVER modify MSSQL schema (read-only)
- [ ] SQLite migrations documented if added
- [ ] Connection tested with test_db_connection.py
- [ ] ODBC driver specified in .env matches installed driver

**Documentation Changes:**
- [ ] README.md updated if setup process changed
- [ ] API_CHANGELOG.md updated if API changed
- [ ] TROUBLESHOOTING.md updated if new issue solved

## Quick Reference Commands

```bash
# Setup (first time)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/migrate_icd_codes.py
cd frontend && npm install && cd ..

# Development
source venv/bin/activate
uvicorn src.api.fastapi_app:app --reload --port 8080  # Terminal 1
cd frontend && npm run dev                             # Terminal 2

# Testing
python test_db_connection.py          # Test database
pytest tests/ -v                       # Run tests (when they exist)

# Code Quality
black src/ && isort src/              # Format Python
cd frontend && npm run lint            # Lint TypeScript

# Build
cd frontend && npm run build           # Production build

# Troubleshooting
python3 -c "import pyodbc; print(pyodbc.drivers())"  # Check ODBC drivers
curl http://localhost:8080/health                     # Test backend
curl http://localhost:8080/api/v1/patients/search?q=test  # Test API
```

## Additional Resources

- **Project Documentation**: See README.md for user guide
- **AI Agent Guidelines**: See AGENTS.md (481 lines, detailed patterns)
- **Project Patterns**: See CLAUDE.md (387 lines, context for AI)
- **Issue Solutions**: See TROUBLESHOOTING.md (522 lines, comprehensive)
- **API Documentation**: http://localhost:8080/docs (when running)
- **Recent Changes**: See IMPLEMENTATION_SUMMARY.md and API_CHANGELOG.md

**Remember:** Trust these instructions. Only search or explore if information is incomplete or incorrect. The project has extensive documentation - use it!
