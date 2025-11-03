# OpenSpec Project Overview

## Project Context
Aile hekimliği pratiği için **SQL Server 2014/2022** tabanlı, **350MB/7 yıllık/~6-7k hasta** verisi içeren AHBS veritabanını analiz eden, **tam klinik karar desteği** (tanı önerisi, tedavi önerisi, ilaç etkileşimi) sunan, **multi-AI destekli** (Local Ollama + OpenAI + Claude + Gemini), **modern hybrid** (Desktop GUI + Web GUI + CLI) Python uygulaması.

### Domain Constraints
- **Platform:** Windows 11
- **Python:** 3.11+ (stable latest)
- **Database:** SQL Server 2014/2022 Express
- **Authentication:** Windows Auth, single user (doctor)
- **KVKK/GDPR:** Not enforced (local and secure use)
- **Encryption:** Not required
- **Remote AI Services:** Allowed
- **Logging Level:** Full debug

### Current Project Status
- **Version:** 0.1.0
- **Phase:** Phase 3 Complete (Clinical Decision Support Modules)
- **Production Code:** 3,340+ lines
- **Test Code:** 820+ lines
- **Database Tables:** 361 SQL Server tables analyzed
- **Patient Records:** ~6-7k patients, 7 years of data

---

## Technology Stack

### Backend
- Python 3.11
- SQLAlchemy 2.0
- FastAPI
- Pydantic

### Frontend
- React 18
- Vite
- Tailwind CSS

### Desktop
- PySide6 (Qt6)

### AI
- Anthropic Claude
- OpenAI GPT-4
- Google Gemini
- Local Ollama (Gemma/Qwen models)

### Other Libraries & Tools
- SQL Server Driver: pyodbc
- ORM: SQLAlchemy
- Data Processing: pandas, numpy, scipy
- Logging: loguru, sentry-sdk (optional)
- CLI: Typer, Rich
- Async HTTP: httpx

---

## Project Structure

```plaintext
clinical-ai-assistant/
├── src/
│   ├── config/          # Konfigürasyon dosyaları
│   ├── database/        # Veritabanı bağlantı ve query modülleri
│   ├── ai/              # AI servis entegrasyonları
│   ├── clinical/        # Klinik karar destek modülleri
│   ├── analytics/       # Analitik ve raporlama
│   ├── api/             # REST API (FastAPI)
│   ├── cli/             # CLI uygulaması
│   ├── gui/             # Desktop GUI (PySide6)
│   └── utils/           # Yardımcı fonksiyonlar
├── tests/               # Test dosyaları
├── docs/                # Dokümantasyon
└── frontend/            # Web UI (React + Vite)
````

---

## Conventions

### Coding Conventions

* PEP8 + Black for code formatting (line-length: 100)
* Meaningful English identifiers
* Consistent use of type hints (Python typing/mypy)
* Core configs via `pydantic-settings`
* Turkish comments and docstrings allowed for clinical context

### Architecture

* **Pattern:** Modular + layered architecture with clear separation:

  * Data layer (ORM/models)
  * Service layer (AI, business logic)
  * Presentation layer (GUI, API, CLI)

### Naming Conventions

* **Files:** `snake_case.py` for Python modules
* **Classes:** `PascalCase` for class names
* **Functions/Variables:** `snake_case` for functions and variables
* **Constants:** `UPPER_CASE` for constants
* **Turkish DB Tables:** Respect existing GP_, DTY_, HRC_, LST_ prefixes

---

## Error Handling

* Centralized exception handlers (FastAPI)
* Retry logic using `tenacity` for unstable integrations (AI APIs, DB)
* Graceful fallback between AI providers (Claude → GPT → Gemini → Ollama)

---

## Logging

* Logging: `loguru` with structured logs
* Log sinks:

  * `stdout` for dev
  * Rotating log file in production
* Log Levels:

  * Debug mode enabled by default (configurable)

---

## Testing Strategy

### Unit Tests

```bash
$ pytest tests/unit/ -v --cov=src
```

* Target: **>80% coverage**
* Critical modules to test:

  * DB connection
  * AI routing
  * Clinical rule engines
  * Drug interaction module

### Integration Tests

```bash
$ pytest tests/integration/ -v
```

* Includes:

  * `test_full_patient_workflow.py`
  * `test_diagnosis_to_treatment_pipeline.py`
  * `test_api_endpoints.py`

### Performance Testing

* Benchmarks:

  * Patient summary: <2s
  * Diagnosis generation: <30s
  * Lab analysis: <5s

---

## Development Workflow

### Git Strategy

* `main` branch is stable
* `dev` branch for active feature integration
* Feature branches naming: `feat/<module>`
* Commit style: Small, descriptive, present-tense

### Phase Progression

* **Phase 1:** ✅ Database Foundation & ORM Models
* **Phase 2:** ✅ Domain Models & Data Layer
* **Phase 3:** ✅ Clinical Decision Support Modules
* **Phase 4:** 🔄 GUI Development (In Progress)
* **Phase 5:** 📋 Planned - Web UI & API Endpoints
* **Phase 6:** 📋 Planned - CLI & Deployment

### Tooling

* Virtual environment: `poetry`
* Linting: `ruff`
* Static typing: `mypy`
* Build GUI executable: `pyinstaller`
* Frontend dev: `vite` with HMR

---

## API Documentation

### FastAPI Endpoints

**Base URL:** `http://localhost:8080`

**Key Endpoints:**
* `/api/v1/patients/{tckn}` - Patient summary
* `/api/v1/diagnose` - Diagnosis suggestions
* `/api/v1/treatment` - Treatment recommendations
* `/api/v1/drugs/interactions` - Drug interaction check
* `/api/v1/labs/analyze` - Lab result analysis

**Documentation:**
* Swagger UI: `http://localhost:8080/docs`
* ReDoc: `http://localhost:8080/redoc`

---

## Deployment

### Desktop Application

```bash
# Build executable with PyInstaller
pyinstaller --name ClinicalAI \
            --windowed \
            --onefile \
            --add-data "config:config" \
            src/gui/main_window.py
```

### Web Application

```bash
# Production deployment with uvicorn
uvicorn src.api.fastapi_app:app \
        --host 0.0.0.0 \
        --port 8080 \
        --workers 4
```

### Environment Variables

Required in `.env`:
```env
DB_SERVER=Sarpel-PC\HIZIR
DB_NAME=TestDB
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
```

---

## Clinical Modules

### Core Capabilities

* **Patient Summarizer:** Demographics, recent visits, active diagnoses, medications, allergies
* **Lab Analyzer:** Reference range abnormality detection, critical value alerting, trend analysis
* **Diagnosis Engine:** AI-powered differential diagnosis with red flag detection, ICD-10 coding
* **Treatment Engine:** Evidence-based treatment recommendations, contraindication checking
* **Drug Interaction Checker:** Drug-drug interactions, allergy cross-reactivity, contraindications

### Safety Features

* Red flag detection for medical emergencies
* Critical lab value alerting (Creatinine >3.0, Potassium >6.5, CRP >50)
* Drug allergy checking with cross-reactivity
* Age-specific contraindication checking
* Comprehensive drug interaction database (4 severity levels)

---