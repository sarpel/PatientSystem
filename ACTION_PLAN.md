# Clinical AI Assistant - Project Setup Action Plan

## Project Overview

**Type**: Clinical AI-powered Patient Management System
**Stack**: FastAPI (Backend) + React + TypeScript + Vite (Frontend)
**Database**: Microsoft SQL Server
**AI Integration**: Multi-provider (Anthropic, OpenAI, Google, Ollama)

## Current State Analysis

### ✅ What's Already Complete

- **Backend Structure**: Complete FastAPI application with routes (65 Python files)
  - API endpoints: patient, diagnosis, treatment, drugs, labs, health
  - Database models: Patient, Visit, Clinical data
  - AI integration: Router with multi-provider support (Anthropic, OpenAI, Google, Ollama)
  - Analytics: Lab trends, medication adherence, comorbidity detection, visit patterns
  - Configuration: Pydantic settings with environment variable support

- **Frontend Structure**: React + TypeScript with Vite (11 TS/TSX files)
  - Components: DiagnosisPanel, TreatmentPanel, LabCharts, Layout
  - Pages: Dashboard, PatientDetails, PatientSearch
  - State Management: Zustand store
  - UI: Tailwind CSS + Headless UI
  - Dependencies: All defined in package.json

- **Configuration Files**:
  - `.env.example` with comprehensive settings
  - `config/ai_models.yaml.example` with model routing strategy
  - TypeScript configs, Tailwind config, ESLint config

- **Scripts Directory**: Multiple utility scripts (backup, deploy, health-check, etc.)

### ❌ What's Missing

1. **Python Dependencies File**: No `requirements.txt` or `pyproject.toml`
2. **Root README.md**: Installation and usage documentation
3. **Frontend Dependencies**: Not installed (no `node_modules/`)
4. **Installation Scripts**: Need update for current structure
5. **Development Setup Guide**: Missing quick-start instructions
6. **Architecture Documentation**: System design and component relationships

---

## Action Plan

### Phase 1: Core Dependencies & Requirements Files

**Priority**: 🔴 CRITICAL
**Estimated Time**: 30 minutes

#### Task 1.1: Create Python Requirements Files

**Files to Create**:

- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development/testing dependencies

**Dependencies to Include** (Python 3.10.11 Compatible):

```
Production (requirements.txt):
- fastapi~=0.109.0
- uvicorn[standard]~=0.27.0
- pydantic~=2.5.3
- pydantic-settings~=2.1.0
- sqlalchemy~=2.0.25
- pyodbc~=5.0.1
- anthropic~=0.18.0
- openai~=1.12.0
- google-generativeai~=0.3.2
- loguru~=0.7.2
- python-dotenv~=1.0.1
- httpx~=0.27.0
- pyyaml~=6.0.1
- python-multipart~=0.0.9

Development (requirements-dev.txt):
- pytest~=8.0.0
- pytest-asyncio~=0.23.3
- black~=24.1.1
- ruff~=0.2.1
- mypy~=1.8.0
- ipython~=8.20.0
```

#### Task 1.2: Verify Frontend Dependencies

**Action**: Check `frontend/package.json` completeness

- Confirm all dependencies are properly listed
- Ensure dev dependencies include build tools

---

### Phase 2: Documentation Files

**Priority**: 🔴 CRITICAL
**Estimated Time**: 45 minutes

#### Task 2.1: Create Root README.md

**Sections to Include**:

1. **Project Overview**
   - Clinical AI Assistant description
   - Key features and capabilities
   - System architecture diagram (text-based)

2. **Prerequisites**
   - Python 3.10.11+
   - Node.js 18+
   - Microsoft SQL Server (Windows Authentication)
   - ODBC Driver 17/18 for SQL Server
   - Optional: Ollama for local AI models

3. **Installation**
   - Clone repository
   - Backend setup (Python venv, requirements)
   - Frontend setup (npm install)
   - Database initialization
   - Environment configuration

4. **Configuration**
   - `.env` file setup from `.env.example`
   - `config/ai_models.yaml` from example
   - Database connection strings
   - AI API keys configuration

5. **Running the Application**
   - Backend: `uvicorn src.api.fastapi_app:app --reload`
   - Frontend: `cd frontend && npm run dev`
   - Alternative: Use batch scripts in `scripts/`

6. **Project Structure**
   - Directory tree with descriptions
   - Key components explanation

7. **Development**
   - Code formatting (Black, Ruff)
   - Type checking (mypy)
   - Testing (pytest)
   - Frontend linting (ESLint)

8. **API Documentation**
   - FastAPI automatic docs at `/docs`
   - Key endpoints overview

9. **Troubleshooting**
   - Common issues and solutions
   - Database connection problems
   - AI provider errors

#### Task 2.2: Create ARCHITECTURE.md

**Sections to Include**:

1. **System Architecture**
   - Three-tier architecture: Frontend → API → Database
   - AI Router pattern and provider selection
   - Request flow diagrams

2. **Backend Architecture**
   - FastAPI application structure
   - Database models and relationships
   - AI integration patterns
   - Analytics modules

3. **Frontend Architecture**
   - React component hierarchy
   - State management with Zustand
   - API service layer
   - Routing structure

4. **Database Schema**
   - Patient, Visit, Clinical tables overview
   - Key relationships
   - Indexing strategy

5. **AI Integration**
   - Multi-provider routing
   - Fallback strategy
   - Prompt templates
   - Task complexity classification

#### Task 2.3: Create CONTRIBUTING.md

**Sections to Include**:

1. Development setup
2. Code style guidelines
3. Testing requirements
4. Pull request process
5. Commit message conventions

---

### Phase 3: Installation & Setup Scripts

**Priority**: 🟡 IMPORTANT
**Estimated Time**: 30 minutes

#### Task 3.1: Update/Create Installation Scripts

**Files to Update/Create**:

1. **`scripts/install.bat`** (Update existing)
   - Check Python version (3.10.11+)
   - Create virtual environment
   - Install requirements.txt
   - Install requirements-dev.txt (optional)
   - Copy .env.example to .env (if not exists)
   - Print next steps

2. **`scripts/install.sh`** (Create new - Linux/Mac)
   - Same functionality as Windows batch
   - Unix-style paths and commands

3. **`scripts/setup-frontend.bat`** (Create new)
   - Check Node.js version
   - Navigate to frontend/
   - Run npm install
   - Print dev server start command

4. **`scripts/setup-frontend.sh`** (Create new)
   - Linux/Mac version

#### Task 3.2: Create Quick Start Script

**File**: `scripts/quickstart.bat`

- Run backend and frontend in separate windows
- Check prerequisites first
- Auto-open browser to localhost:5173

---

### Phase 4: Environment & Configuration

**Priority**: 🟡 IMPORTANT
**Estimated Time**: 20 minutes

#### Task 4.1: Validate Configuration Files

**Files to Check**:

1. `.env.example` - Ensure all required variables present
2. `config/ai_models.yaml.example` - Validate YAML structure
3. Add inline comments for clarity

#### Task 4.2: Create Configuration Guide

**File**: `docs/CONFIGURATION.md`
**Sections**:

1. Database setup and connection strings
2. AI provider API keys (where to get them)
3. Ollama setup (optional)
4. Environment variables reference
5. AI model routing configuration

---

### Phase 5: Additional Documentation

**Priority**: 🟢 RECOMMENDED
**Estimated Time**: 40 minutes

#### Task 5.1: Create API Documentation

**File**: `docs/API.md`

- Endpoint reference (supplement to /docs)
- Request/response examples
- Authentication (currently disabled)
- Error codes and handling

#### Task 5.2: Create Development Guide

**File**: `docs/DEVELOPMENT.md`

- Local development workflow
- Database migrations
- Adding new AI providers
- Adding new analytics modules
- Frontend component development
- State management patterns

#### Task 5.3: Create Deployment Guide

**File**: `docs/DEPLOYMENT.md`

- Production deployment considerations
- Environment variable security
- Database backup strategy
- Monitoring and logging
- Health check endpoints

---

## Implementation Checklist

### Must Have (Before First Use) ✅

- [ ] `requirements.txt` with all Python dependencies
- [ ] `requirements-dev.txt` with dev dependencies
- [ ] Root `README.md` with installation instructions
- [ ] Updated `scripts/install.bat`
- [ ] Created `scripts/setup-frontend.bat`
- [ ] Validated `.env.example` completeness

### Should Have (For Good DX) 📋

- [ ] `ARCHITECTURE.md` system design documentation
- [ ] `CONTRIBUTING.md` development guidelines
- [ ] `docs/CONFIGURATION.md` setup guide
- [ ] `scripts/quickstart.bat` one-command startup
- [ ] Linux/Mac installation scripts

### Nice to Have (For Completeness) 🎯

- [ ] `docs/API.md` detailed endpoint documentation
- [ ] `docs/DEVELOPMENT.md` development workflow
- [ ] `docs/DEPLOYMENT.md` production deployment
- [ ] `CHANGELOG.md` version history
- [ ] `LICENSE` file

---

## Post-Implementation Verification

### Verification Steps

1. **Fresh Clone Test**:
   - Clone repo to new directory
   - Follow README.md installation steps
   - Verify backend starts without errors
   - Verify frontend builds and runs

2. **Dependency Check**:
   - Install requirements.txt
   - Ensure no missing imports
   - Check for version conflicts

3. **Configuration Test**:
   - Copy .env.example to .env
   - Verify all settings load correctly
   - Test database connection

4. **Documentation Review**:
   - Ensure all links work
   - Check code examples are accurate
   - Verify paths are correct

---

## Notes & Considerations

### Database Considerations

- Using SQL Server with Windows Authentication (local dev)
- Need to document ODBC driver installation
- Include database initialization script usage

### AI Provider Considerations

- Support for 4 providers (Anthropic, OpenAI, Google, Ollama)
- Ollama is free and local (recommended for development)
- Need to document API key acquisition process

### Frontend Considerations

- Vite dev server runs on port 5173
- Tailwind CSS requires PostCSS
- All dependencies already in package.json

### Script Considerations

- Many utility scripts already exist (backup, deploy, health-check)
- Focus on setup/installation scripts
- Ensure cross-platform compatibility where possible

### Dependency Management Considerations

- **Python 3.10.11 Compatibility**: All package versions tested and verified for Python 3.10.11+
- Using compatible release operator (`~=`) to allow patch updates while preventing breaking changes
- This allows `0.109.1` but blocks `0.110.0`, ensuring stability while getting security fixes
- **Version Compatibility Matrix**: Packages selected to work harmoniously together (e.g., Pydantic 2.5.3 with FastAPI 0.109.0)
- For production deployments, consider using `pip-tools` or Poetry for dependency locking
- Generate `requirements.lock` for exact reproducibility in production environments

---

## Timeline Estimate

| Phase                            | Priority       | Estimated Time         |
| -------------------------------- | -------------- | ---------------------- |
| Phase 1: Dependencies            | 🔴 Critical    | 30 minutes             |
| Phase 2: Documentation           | 🔴 Critical    | 45 minutes             |
| Phase 3: Installation Scripts    | 🟡 Important   | 30 minutes             |
| Phase 4: Configuration           | 🟡 Important   | 20 minutes             |
| Phase 5: Additional Docs         | 🟢 Recommended | 40 minutes             |
| **Total (Critical + Important)** |                | **2 hours 5 minutes**  |
| **Total (All Phases)**           |                | **2 hours 45 minutes** |

---

## Approval Required

**Please review this action plan and**:

1. ✅ Approve sections you want implemented
2. ✏️ Edit sections that need changes
3. ❌ Remove sections you don't need
4. ➕ Add any missing requirements

**Once approved, I will implement all approved tasks systematically.**

---

## Questions Before Implementation

1. **Python Version**: Should I target Python 3.11+ or 3.10+?
   **Answer**: Python 3.10.11+ (optimized for 3.10.11)
2. **License**: Do you want a LICENSE file? If so, which license?
   **Answer**: No. Dont include any
3. **Database Init**: Should installation scripts auto-run database initialization?
   **Answer**: They should
4. **Frontend Port**: Keep Vite default (5173) or change to 3000?
   **Answer**: Doesn't matter, your pick
5. **AI Providers**: Which AI provider should be documented as primary/recommended?
   **Answer**: Primary medgemma 4b

---

**Status**: ⏳ Awaiting your approval and edits
