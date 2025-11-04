# 🏥 HASTA KLİNİK KARAR DESTEK SİSTEMİ - FİNAL PROJE PROMPTU

## 🎯 EXECUTIVE SUMMARY

Aile hekimliği pratiği için **SQL Server 2014/2022** tabanlı, **350MB/7 yıllık/~6-7k hasta** verisi içeren AHBS veritabanını analiz eden, **tam klinik karar desteği** (tanı önerisi, tedavi önerisi, ilaç etkileşimi) sunan, **multi-AI destekli** (Local Ollama + OpenAI + Claude + Gemini), **modern hybrid** (Desktop GUI + Web GUI + CLI) Python uygulaması.

---

## 🔐 KRİTİK PROJE PARAMETRELERİ

```yaml
ORTAM:
  Platform: Windows 11 Only
  Python: 3.11+ (stable latest)
  Database: SQL Server 2014/2022 Express
  Auth: Windows Authentication
  User: Single user (doctor)

GÜVENLIK:
  KVKK: ❌ DISABLED (personal use, secure environment)
  Authentication: ❌ NOT REQUIRED
  Encryption: ❌ NOT REQUIRED
  Remote Data: ✅ ALLOWED (AI services)
  Logging: ✅ FULL DEBUG MODE

KLİNİK KAPASITE:
  Tanı Önerisi: ✅ ENABLED (with probability scores)
  Tedavi Önerisi: ✅ ENABLED (drugs, tests, consultations, lifestyle)
  İlaç Etkileşimi: ✅ ENABLED (API-based if available)
  Lab Analizi: ✅ ENABLED (abnormal detection, trends)
  Risk Stratifikasyonu: ✅ ENABLED

AI STACK:
  Local: Ollama (Gemma/Qwen) - Fast general tasks
  Remote Primary: Anthropic Claude 3.5 Sonnet - Critical analysis
  Remote Secondary: OpenAI GPT-4/4o - Backup
  Remote Tertiary: Google Gemini Pro - Alternative
  Strategy: Configurable (default: Senaryo A)

INTERFACE:
  Primary: Desktop GUI (PySide6/Qt6)
  Secondary: Web GUI (React/Vite + FastAPI backend)
  Tertiary: CLI (Typer + Rich)

ENTEGRASYON:
  Method: Multiple (CLI call, REST API, Database trigger)
  Existing App: Java/.NET Framework mixed
  Detection: Database connection monitoring
```

---

## 📁 PROJE MİMARİSİ

```
clinical-ai-assistant/
├── 🔧 Core Backend
│   ├── src/
│   │   ├── main.py                          # Application entry
│   │   ├── config/
│   │   │   ├── settings.py                  # Pydantic settings
│   │   │   ├── ai_models.py                 # AI model configurations
│   │   │   └── database_schema.yaml         # Auto-discovered schema
│   │   ├── database/
│   │   │   ├── connection.py                # SQLAlchemy engine
│   │   │   ├── inspector.py                 # Schema inspector (from GP_*/DTY_*/LST_* tables)
│   │   │   ├── query_builder.py             # Dynamic query constructor
│   │   │   └── models.py                    # ORM models
│   │   ├── ai/
│   │   │   ├── router.py                    # AI service router (Senaryo A logic)
│   │   │   ├── ollama_client.py             # Local Ollama integration
│   │   │   ├── openai_client.py             # OpenAI API
│   │   │   ├── anthropic_client.py          # Claude API
│   │   │   ├── google_client.py             # Gemini API
│   │   │   └── prompt_templates.py          # Turkish clinical prompts
│   │   ├── clinical/
│   │   │   ├── diagnosis_engine.py          # Diagnosis suggestions with probabilities
│   │   │   ├── treatment_engine.py          # Treatment recommendations
│   │   │   ├── drug_interaction.py          # Drug-drug interaction checker
│   │   │   ├── lab_analyzer.py              # Lab result interpretation
│   │   │   ├── risk_calculator.py           # CVD, DM, CKD risk scores
│   │   │   └── patient_summarizer.py        # Comprehensive patient summary
│   │   ├── analytics/
│   │   │   ├── visit_patterns.py            # Visit frequency analysis
│   │   │   ├── medication_adherence.py      # Medication compliance
│   │   │   ├── lab_trends.py                # Longitudinal lab trends
│   │   │   └── comorbidity_detector.py      # Comorbidity patterns
│   │   ├── api/
│   │   │   ├── fastapi_app.py               # REST API server
│   │   │   ├── routes/
│   │   │   │   ├── patient.py               # Patient endpoints
│   │   │   │   ├── diagnosis.py             # Diagnosis endpoints
│   │   │   │   ├── treatment.py             # Treatment endpoints
│   │   │   │   └── analytics.py             # Analytics endpoints
│   │   │   └── schemas.py                   # Pydantic request/response models
│   │   ├── cli/
│   │   │   ├── app.py                       # Typer CLI application
│   │   │   └── commands/
│   │   │       ├── analyze.py               # Analysis commands
│   │   │       ├── inspect.py               # Database inspection
│   │   │       └── config.py                # Configuration management
│   │   └── utils/
│   │       ├── logger.py                    # Structured logging
│   │       ├── turkish_nlp.py               # Turkish text processing
│   │       └── validators.py                # Data validation
│
├── 🖥️ Desktop GUI (PySide6)
│   └── src/gui/
│       ├── main_window.py                   # Main application window
│       ├── widgets/
│       │   ├── patient_search.py            # Patient search widget
│       │   ├── clinical_dashboard.py        # Dashboard with tabs
│       │   ├── diagnosis_panel.py           # Diagnosis suggestions
│       │   ├── treatment_panel.py           # Treatment recommendations
│       │   ├── lab_charts.py                # Lab trend charts
│       │   └── drug_interaction_alert.py    # Drug interaction warnings
│       ├── dialogs/
│       │   ├── ai_config_dialog.py          # AI model configuration
│       │   └── database_inspector_dialog.py # DB schema viewer
│       └── resources/
│           ├── styles.qss                   # Qt stylesheet
│           └── icons/                       # Application icons
│
├── 🌐 Web GUI (React + Vite)
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx                      # Main React component
│       │   ├── components/
│       │   │   ├── PatientSearch.tsx        # Patient search
│       │   │   ├── ClinicalDashboard.tsx    # Main dashboard
│       │   │   ├── DiagnosisPanel.tsx       # Diagnosis view
│       │   │   ├── TreatmentPanel.tsx       # Treatment view
│       │   │   ├── LabCharts.tsx            # Charts (Chart.js/Recharts)
│       │   │   └── DrugInteractionAlert.tsx # Warnings
│       │   ├── services/
│       │   │   └── api.ts                   # API client
│       │   ├── stores/
│       │   │   └── useAppStore.ts           # Zustand state management
│       │   └── styles/
│       │       └── globals.css              # Tailwind CSS
│       ├── package.json
│       └── vite.config.ts
│
├── 🧪 Tests
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_database/
│   │   │   ├── test_ai/
│   │   │   ├── test_clinical/
│   │   │   └── test_analytics/
│   │   ├── integration/
│   │   │   ├── test_api_endpoints.py
│   │   │   ├── test_ai_integration.py
│   │   │   └── test_database_queries.py
│   │   └── e2e/
│   │       └── test_full_workflow.py
│   ├── conftest.py                          # Pytest fixtures
│   └── synthetic_data_generator.py          # Test data creator
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── 01_KURULUM.md                    # Installation guide
│   │   ├── 02_VERITABANI_BAGLANTI.md        # Database connection
│   │   ├── 03_AI_KONFIGURASYONU.md          # AI setup
│   │   ├── 04_KULLANIM_GUI.md               # GUI usage
│   │   ├── 05_KULLANIM_CLI.md               # CLI usage
│   │   ├── 06_API_DOKUMANTASYON.md          # API reference
│   │   ├── 07_ENTEGRASYON.md                # Integration guide
│   │   └── 08_SORUN_GIDERME.md              # Troubleshooting
│   └── README.md
│
├── ⚙️ Configuration
│   ├── .env.example                         # Environment template
│   ├── config/
│   │   ├── ai_models.yaml                   # AI model configs
│   │   └── database_schema.yaml             # Discovered schema
│   ├── requirements.txt                     # Python dependencies
│   ├── requirements-dev.txt                 # Dev dependencies
│   ├── pyproject.toml                       # Poetry/setup config
│   └── setup.py                             # Installation script
│
└── 🚀 Deployment
    ├── scripts/
    │   ├── install.bat                      # Windows installer
    │   ├── run_desktop.bat                  # Launch desktop GUI
    │   ├── run_web.bat                      # Launch web server
    │   └── run_cli.bat                      # CLI launcher
    ├── build/
    │   └── pyinstaller.spec                 # PyInstaller config
    └── docker/
        └── Dockerfile                       # Optional Docker image
```

---

## 📦 DEPENDENCY STACK (RELIABILITY FOCUSED)

### Core Backend

```toml
[tool.poetry.dependencies]
python = "^3.11"

# Database - Industry Standard
sqlalchemy = "^2.0.23"             # ORM/Query builder
pyodbc = "^5.0.1"                  # SQL Server driver
alembic = "^1.13.0"                # Database migrations

# Data Processing - Battle Tested
pandas = "^2.1.4"                  # Data analysis
numpy = "^1.26.2"                  # Numerical computing
scipy = "^1.11.4"                  # Statistical functions

# AI Integration - Official SDKs
openai = "^1.6.1"                  # OpenAI GPT-4/4o
anthropic = "^0.8.1"               # Claude 3.5 Sonnet
google-generativeai = "^0.3.1"     # Gemini Pro
ollama = "^0.1.6"                  # Local Ollama client

# API Server - Production Grade
fastapi = "^0.108.0"               # Modern async framework
uvicorn = {extras = ["standard"], version = "^0.25.0"}
pydantic = "^2.5.3"                # Data validation
pydantic-settings = "^2.1.0"       # Settings management

# Desktop GUI - Qt Official
PySide6 = "^6.6.1"                 # Qt6 Python bindings
pyqtgraph = "^0.13.3"              # Scientific plotting
matplotlib = "^3.8.2"              # Additional charts

# CLI - Modern Stack
typer = {extras = ["all"], version = "^0.9.0"}
rich = "^13.7.0"                   # Beautiful terminal output
questionary = "^2.0.1"             # Interactive prompts

# Utilities - Proven Libraries
python-dotenv = "^1.0.0"           # Environment management
pyyaml = "^6.0.1"                  # YAML parsing
requests = "^2.31.0"               # HTTP client
httpx = "^0.26.0"                  # Async HTTP
aiofiles = "^23.2.1"               # Async file I/O
tenacity = "^8.2.3"                # Retry logic

# Turkish NLP (if needed)
zemberek-python = "^0.1.3"         # Turkish language processing

# Logging & Monitoring
loguru = "^0.7.2"                  # Advanced logging
sentry-sdk = "^1.40.0"             # Error tracking (optional)

[tool.poetry.dev-dependencies]
pytest = "^7.4.3"                  # Testing framework
pytest-cov = "^4.1.0"              # Coverage
pytest-asyncio = "^0.21.1"         # Async tests
pytest-mock = "^3.12.0"            # Mocking
faker = "^22.0.0"                  # Fake data generation
black = "^23.12.1"                 # Code formatting
ruff = "^0.1.9"                    # Linting
mypy = "^1.8.0"                    # Type checking
pyinstaller = "^6.3.0"             # Executable building
```

### Web Frontend

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.5",
    "chart.js": "^4.4.1",
    "react-chartjs-2": "^5.2.0",
    "recharts": "^2.10.3",
    "lucide-react": "^0.303.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "tailwindcss": "^3.4.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.0.6"
  },
  "devDependencies": {
    "@types/react": "^18.2.47",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.10",
    "typescript": "^5.3.3",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

---

## 🗄️ VERİTABANI TABLO HARİTASI

Verilen **361 tablo** isimlerinden kritik tablo kategorileri:

### Hasta Demografik & Kayıt

```sql
GP_HASTA_KAYIT, GP_HASTA_OZLUK, DTY_HASTA_OZLUK_*
HRC_AILE, HRC_KULLANICILAR, LST_CINSIYET, LST_KAN_GRUBU
```

### Muayene & Vizit

```sql
GP_MUAYENE, GP_HASTA_KABUL, GP_HASTA_CIKIS
HRC_MUAYENE_SABLON*, DTY_MUAYENE_*
LST_MUAYENE_TURU, LST_BASVURU_TURU
```

### Tanı & ICD Kodları

```sql
HRC_MUAYENE_SABLON_TANI, DTY_MUAYENE_EK_TANI
LST_ICD10, LST_ICD10_MSVS_ILISKISI
DTY_*_KOMPLIKASYON_TANILARI
```

### Reçete & İlaç

```sql
GP_RECETE, DTY_RECETE_ILAC, DTY_RECETE_EK_TANI
HRC_ILAC_*, HRC_SGK_ILAC_LISTESI
LST_ILAC_*, HRC_BENIM_LISTEM_ILAC
```

### Lab & Tetkik

```sql
GP_HASTANE_TETKIK_ISTEM, DTY_HASTANE_ISTEM
HRC_DTY_LAB_SONUC*, GP_TETKIK_TALEP
LST_HASTANE_TETKIK, DTY_*_TETKIK_*
```

### Alerji & Uyarılar

```sql
DTY_HASTA_OZLUK_ALERJI*, HRC_LST_UYARI_SABLONLARI
LST_ASI_OZEL_DURUMU_NEDENI
```

### Gebe & Lohusa İzlem

```sql
GP_GEBE_IZLEM, DTY_GEBE_IZLEM_*
GP_LOHUSA_IZLEM, DTY_LOHUSA_IZLEM_*
GP_GEBELIK_BILDIRIM, GP_GEBELIK_SONUCU
```

### Bebek & Çocuk İzlem

```sql
GP_BC_IZLEM, DTY_BC_IZLEM_*
HRC_COCUK_ERGEN_IZLEM, GP_BC_BESLENME
LST_BEBEK_*, DTY_BC_PSIKO_SOSYAL_*
```

### Aşı Takibi

```sql
GP_ASI, HRC_ASI_TAKVIMI, HRC_IZLEM_ASI_TAKVIMI
GP_ASI_ERTELEME_IPTAL, GP_ASI_SONRASI_ISTENMEYEN_ETKI
LST_ASI*, DTY_ASI_*
```

### Kronik Hastalıklar

```sql
GP_DIYABET, GP_KRONIK_HASTALIKLAR, GP_HYP_*
GP_KANSER, GP_KANSER_IZLEM, GP_OBEZITE
DTY_DIYABET_*, DTY_OBEZITE_*
```

### Bulaşıcı Hastalıklar

```sql
GP_BULASICI_HASTALIK_*, GP_VEREM, GP_SITMA
GP_KUDUZ_*, GP_ZEHIRLENME
DTY_BULASICI_HASTALIK_*
```

### Vital & Ölçümler

```sql
LST_AGRI, LST_SPIROMETRI
DTY_*_VITAL*, GP_*_VITAL
```

### Referans & Liste Tabloları (LST\_\*)

```sql
LST_TANI_YONTEMI, LST_TEDAVI_YONTEMI, LST_TEDAVI_SEKLI
LST_TARAMA_SONUCU, LST_HASTALIK, LST_HASTALIK_TIPI
LST_MESLEKLER, LST_MESLEK_VE_KANSER
... (100+ referans tablosu)
```

---

## 🤖 AI SERVİS MİMARİSİ

### Senaryo A: Hybrid Smart Routing

```python
class AIRouter:
    """
    Smart routing:
    - Basit özetleme → Ollama (hızlı)
    - Karmaşık tanı/tedavi → Claude 3.5 Sonnet (en akıllı)
    - Fallback → GPT-4o → Gemini Pro
    """

    TASK_COMPLEXITY = {
        'simple': ['patient_summary', 'basic_stats', 'recent_visits'],
        'moderate': ['lab_trend_analysis', 'medication_adherence'],
        'complex': ['differential_diagnosis', 'treatment_planning',
                   'drug_interactions', 'risk_stratification']
    }

    MODEL_PRIORITY = {
        'simple': ['ollama'],
        'moderate': ['ollama', 'gpt-4o-mini', 'claude-3.5-sonnet'],
        'complex': ['claude-3.5-sonnet', 'gpt-4o', 'gemini-pro']
    }
```

### AI Model Konfigürasyonu

```yaml
# config/ai_models.yaml

models:
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    model_name: "gemma:7b" # veya qwen2.5:7b
    timeout: 60
    temperature: 0.3
    max_tokens: 2048

  anthropic:
    enabled: true
    model_name: "claude-3-5-sonnet-20241022"
    api_key_env: "ANTHROPIC_API_KEY"
    temperature: 0.5
    max_tokens: 4096
    timeout: 120

  openai:
    enabled: true
    model_name: "gpt-4o" # fallback: gpt-4o-mini
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.5
    max_tokens: 4096
    timeout: 120

  google:
    enabled: true
    model_name: "gemini-pro"
    api_key_env: "GOOGLE_API_KEY"
    temperature: 0.5
    max_output_tokens: 2048
    timeout: 120

routing:
  strategy: "smart" # Options: smart, manual, round_robin
  retry_on_failure: true
  max_retries: 3
  fallback_enabled: true
```

---

## 🏥 KLİNİK KARAR DESTEĞİ MODÜLLERİ

### 1. Diagnosis Engine

```python
class DiagnosisEngine:
    """
    Hasta bilgilerine göre diferansiyel tanı önerileri.

    Input:
    - Şikayetler (chief complaints)
    - Vital bulgular
    - Fizik muayene
    - Lab sonuçları
    - Geçmiş tanılar
    - Demografik risk faktörleri

    Output:
    {
      "differential_diagnosis": [
        {
          "diagnosis": "Tip 2 Diabetes Mellitus",
          "icd10": "E11",
          "probability": 0.75,
          "reasoning": "HbA1c: 8.2%, açlık glukozu yüksek...",
          "supporting_findings": ["HbA1c elevated", "polyuria", "polydipsia"],
          "red_flags": []
        },
        {
          "diagnosis": "Prediabetes",
          "icd10": "R73.03",
          "probability": 0.20,
          "reasoning": "...",
          ...
        }
      ],
      "urgent_conditions": [],
      "recommended_tests": ["OGTT", "Lipid panel", "Microalbumin"],
      "confidence_score": 0.82
    }
    """
```

### 2. Treatment Engine

```python
class TreatmentEngine:
    """
    Tanıya ve hasta durumuna göre tedavi önerileri.

    Output:
    {
      "pharmacological": [
        {
          "drug_name": "Metformin",
          "generic_name": "Metformin HCl",
          "dosage": "500 mg",
          "frequency": "2x1",
          "duration": "sürekli",
          "route": "oral",
          "rationale": "First-line for T2DM...",
          "contraindications": ["eGFR <30", "lactic acidosis history"],
          "monitoring": ["Renal function q3mo", "B12 yearly"],
          "cost": "Low",
          "priority": 1
        }
      ],
      "lifestyle": [
        {
          "recommendation": "Karbonhidrat kısıtlaması",
          "details": "Günlük CHO <150g, kompleks CHO tercih",
          "priority": 1
        },
        {
          "recommendation": "Aerobik egzersiz",
          "details": "Haftada 5 gün, 30 dk orta-yoğunluk",
          "priority": 1
        }
      ],
      "laboratory_followup": [
        {
          "test": "HbA1c",
          "frequency": "3 ayda bir",
          "target": "<7%"
        }
      ],
      "consultations": [
        {
          "specialty": "Endokrinoloji",
          "urgency": "routine",
          "reason": "Diyabet yönetimi optimizasyonu"
        },
        {
          "specialty": "Diyetisyen",
          "urgency": "urgent",
          "reason": "Medikal beslenme tedavisi"
        }
      ]
    }
    """
```

### 3. Drug Interaction Checker

```python
class DrugInteractionChecker:
    """
    İlaç-ilaç, ilaç-alerji, ilaç-hastalık etkileşimi kontrolü.

    Kaynak:
    - Türkiye İlaç Kılavuzu (offline database)
    - RxNorm/Drugs.com API (if available)
    - Lokal referans tabloları

    Output:
    {
      "interactions": [
        {
          "type": "drug-drug",
          "severity": "major",
          "drug1": "Warfarin",
          "drug2": "NSAİİ (Diklofenak)",
          "effect": "Kanama riski artışı",
          "recommendation": "Kombinasyondan kaçının veya sıkı INR takibi",
          "management": "PPI ekleyin, INR haftalık kontrol"
        },
        {
          "type": "drug-allergy",
          "severity": "critical",
          "drug": "Amoksisilin",
          "allergen": "Penisilin",
          "reaction": "Anafilaksi",
          "recommendation": "KESİNLİKLE KULLANMAYıN! Alternatif: Makrolid"
        }
      ],
      "safe_to_prescribe": false,
      "alternative_drugs": ["Azitromisin", "Levofloksasin"]
    }
    """
```

### 4. Lab Analyzer

```python
class LabAnalyzer:
    """
    Tahlil sonuçlarını yorumlama ve trend analizi.

    Features:
    - Referans aralığı dışı değerler
    - Kritik değer alarmları
    - Trend analizi (son 6-12 ay)
    - Klinik korelasyon

    Output:
    {
      "critical_abnormals": [
        {
          "test_name": "Potasyum",
          "value": 5.9,
          "unit": "mmol/L",
          "reference_range": "3.5-5.0",
          "deviation": "+18%",
          "severity": "critical",
          "clinical_significance": "Hiperkalemi - kardiyak aritmi riski",
          "immediate_action": "EKG çek, tekrar et, neden araştır",
          "date": "2024-01-15"
        }
      ],
      "trending_abnormals": [
        {
          "test_name": "HbA1c",
          "trend": "increasing",
          "values": [
            {"date": "2023-07-15", "value": 7.2},
            {"date": "2023-10-15", "value": 7.8},
            {"date": "2024-01-15", "value": 8.4}
          ],
          "interpretation": "Diyabet kontrolü bozulmuş, tedavi revizyonu gerekli"
        }
      ],
      "normal_results": [...],
      "recommended_followup": [...]
    }
    """
```

### 5. Risk Calculator

```python
class RiskCalculator:
    """
    Klinik risk skorlamaları.

    Hesaplanan Skorlar:
    - Framingham/SCORE2 (KVH riski)
    - FINDRISC (Diyabet riski)
    - CHA2DS2-VASc (AF'de stroke riski)
    - HAS-BLED (Kanama riski)
    - CKD-EPI eGFR
    - BMI & Obezite sınıflandırması
    - ASCVD 10-year risk

    Output:
    {
      "cardiovascular_risk": {
        "score_type": "SCORE2",
        "10_year_risk": 8.5,
        "risk_category": "orta",  # düşük/orta/yüksek/çok yüksek
        "factors": {
          "age": 55,
          "gender": "M",
          "smoking": true,
          "systolic_bp": 145,
          "total_cholesterol": 240,
          "hdl": 35
        },
        "recommendations": [
          "Statin başlangıcı düşünülmeli",
          "Kan basıncı hedefi <130/80",
          "Sigara bırakma programı"
        ]
      },
      ...
    }
    """
```

---

## 🖥️ KULLANICI ARAYÜZLERİ

### A. Desktop GUI (PySide6)

```python
# Ana Pencere Bileşenleri:

[Üst Menü]
Dosya | Hasta | Analiz | Ayarlar | Yardım

[Arama Çubuğu]
🔍 Hasta Ara (TCKN, Ad, Protokol No...)  [Ara] [Temizle]

[Ana Panel - Tabs]
┌─────────────────────────────────────────────────────────┐
│ 📋 Özet | 🩺 Tanı | 💊 Tedavi | 🧪 Lab | 📊 Grafikler │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [ÖZETPanel]                                           │
│  ┌─────────────────────────────────────────┐          │
│  │ 👤 AHMET YILMAZ, E, 55 yaş              │          │
│  │ TCKN: 12345678901                       │          │
│  │ Son vizit: 15.01.2024                   │          │
│  │ Son lab: 12.01.2024                     │          │
│  │ Aktif ilaç: 5                           │          │
│  │                                          │          │
│  │ ⚠️ UYARILAR:                             │          │
│  │ • Penisilin alerjisi                    │          │
│  │ • INR takibi gerekli (Warfarin)         │          │
│  │ • HbA1c yükselme trendi                 │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
│  [İÇGÖRÜ BUTONU]                                      │
│  ┌─────────────────────────────────────────┐          │
│  │  🤖 AI Analiz Başlat                    │          │
│  │  [Hızlı Özet] [Detaylı Analiz] [Tanı   │          │
│  │               Öner]                     │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘

[Durum Çubuğu]
Hazır | AI Model: Claude 3.5 Sonnet | DB: ✓ Bağlı | Son güncelleme: 15.01.2024 14:30
```

**Tanı Paneli:**

```
┌─────────────────────────────────────────────────────────┐
│ 🩺 DİFERANSİYEL TANI ÖNERİLERİ                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ℹ️ Son şikayet: Poliüri, polidipsi, halsizlik         │
│ ℹ️ Son bulgular: Kilo kaybı, kan şekeri: 245 mg/dL    │
│                                                         │
│ [AI TANI HESAPLA] butonuna basıldıktan sonra:         │
│                                                         │
│ 🎯 Olası Tanılar (Olasılık Sıralı):                   │
│                                                         │
│ 1️⃣ Tip 2 Diabetes Mellitus [E11]         📊 75%      │
│    └─ HbA1c 8.4%, açlık glukozu 245 mg/dL             │
│    └─ Klasik semptomlar mevcut                         │
│    └─ Risk faktörleri: Yaş, obezite, aile öyküsü     │
│                                                         │
│ 2️⃣ Prediabetes [R73.03]                  📊 20%      │
│    └─ Alternatif olarak düşünülebilir                 │
│                                                         │
│ 3️⃣ Tip 1 DM (LADA)                       📊 5%       │
│    └─ Düşük olasılık (yaş, kilo kaybı az)            │
│                                                         │
│ ⚠️ Acil durumlar: DKA riski düşük                      │
│                                                         │
│ 🔬 Önerilen Testler:                                   │
│    • HbA1c (kontrol)                                   │
│    • Lipid profili                                     │
│    • Mikroalbumin/kreatinin oranı                      │
│    • TSH (komorbidite taraması)                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### B. Web GUI (React)

```typescript
// Modern, responsive, medical-grade UI
// Tailwind CSS + shadcn/ui components

<ClinicalDashboard>
  <PatientHeader />
  <Tabs>
    <TabPanel id="summary">
      <PatientSummaryCard />
      <AlertsPanel />
      <QuickActions />
    </TabPanel>

    <TabPanel id="diagnosis">
      <ChiefComplaintInput />
      <VitalsInput />
      <AIAnalysisButton onClick={runDiagnosis} />
      <DiagnosisResultsPanel />
    </TabPanel>

    <TabPanel id="treatment">
      <SelectedDiagnosisDropdown />
      <TreatmentRecommendations />
      <DrugInteractionAlerts />
      <PrescriptionGenerator />
    </TabPanel>

    <TabPanel id="labs">
      <LabResultsTable />
      <TrendCharts />
      <CriticalValueAlerts />
    </TabPanel>
  </Tabs>
</ClinicalDashboard>
```

### C. CLI Interface

```bash
# Hasta analizi
$ clinical-ai analyze --tckn 12345678901

🔍 Hasta analizi başlatılıyor...
✓ Veritabanı bağlantısı başarılı
✓ Hasta kaydı bulundu: AHMET YILMAZ, E, 55
✓ Veriler çekiliyor... (vizit: 45, lab: 23, ilaç: 5)
🤖 AI analizi (Claude 3.5 Sonnet)...

📋 HASTA ÖZETİ
──────────────────────────────────────
Kimlik: AHMET YILMAZ, 55 yaş, Erkek
Son vizit: 15.01.2024
Aktif tanılar: Tip 2 DM, Hipertansiyon, Hiperlipidemi

⚠️  UYARILAR
──────────────────────────────────────
• Penisilin alerjisi kayıtlı
• HbA1c yükseliş trendi (7.2 → 8.4)
• Warfarin kullanımı - INR takibi

🩺 DİFERANSİYEL TANILAR
──────────────────────────────────────
1. Diyabet kontrolsüzlüğü (75%)
   • HbA1c 8.4% (hedef <7%)
   • Tedavi revizyonu gerekli

💊 TEDAVİ ÖNERİLERİ
──────────────────────────────────────
1. Metformin doz artırımı (1000 mg → 1500 mg 2x1)
2. SGLT2 inhibitörü eklenmesi değerlendirilmeli
3. Yaşam tarzı müdahalesi güçlendirilmeli

🧪 ÖNERİLEN TESTLER
──────────────────────────────────────
• HbA1c (3 ay sonra kontrol)
• Lipid profili
• Mikroalbumin/kreatinin
• Göz dibi muayenesi

📊 JSON çıktı için: --output json
📁 Dosyaya kaydet: --save patient_12345.json

# Hızlı tanı önerisi
$ clinical-ai diagnose --tckn 12345678901 --complaint "ateş, öksürük, boğaz ağrısı"

# Veritabanı şeması görüntüleme
$ clinical-ai inspect database

# AI model değiştirme
$ clinical-ai config set-model gpt-4o

# İlaç etkileşimi kontrolü
$ clinical-ai drug-check --tckn 12345678901 --add "Amoksisilin 1000mg"
```

---

## 🔌 ENTEGRASYON STRATEJİLERİ

### Mevcut Java/.NET Uygulaması ile Entegrasyon

**Opsıyon 1: REST API Çağrısı (Önerilen)**

```java
// Java/.NET tarafında - Hasta açıldığında
String tckn = getSelectedPatientTCKN();

// HTTP GET request
String url = "http://localhost:8080/api/v1/patient/analyze?tckn=" + tckn;
HttpResponse response = httpClient.get(url);

JSONObject insights = new JSONObject(response.body());

// Sonuçları göster
showAIInsightsDialog(insights);
```

**Opsıyon 2: CLI Subprocess**

```csharp
// C# örneği
string tckn = GetSelectedPatientTCKN();

var process = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = "clinical-ai.exe",
        Arguments = $"analyze --tckn {tckn} --output json",
        RedirectStandardOutput = true,
        UseShellExecute = false,
        CreateNoWindow = true
    }
};

process.Start();
string jsonOutput = process.StandardOutput.ReadToEnd();
process.WaitForExit();

var insights = JsonConvert.DeserializeObject<PatientInsights>(jsonOutput);
DisplayInsights(insights);
```

**Opsıyon 3: Database Trigger (En Düşük Etkileşim)**

```sql
-- Hasta seçildiğinde tetiklenen trigger
CREATE TRIGGER trg_PatientSelected
ON dbo.LastAccessedPatient
AFTER INSERT, UPDATE
AS
BEGIN
    DECLARE @TCKN VARCHAR(11)
    SELECT @TCKN = TCKN FROM inserted

    -- Harici script çağır
    EXEC xp_cmdshell 'clinical-ai.exe analyze --tckn ' + @TCKN + ' --background'
END
```

**Opsıyon 4: Named Pipe / IPC**

```python
# Python tarafında - Named pipe server
import win32pipe, win32file

pipe = win32pipe.CreateNamedPipe(
    r'\\.\pipe\ClinicalAIPipe',
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
    1, 65536, 65536,
    0,
    None
)

while True:
    win32pipe.ConnectNamedPipe(pipe, None)
    data = win32file.ReadFile(pipe, 64*1024)
    tckn = data[1].decode()

    # Analiz yap
    insights = analyze_patient(tckn)

    # Geri gönder
    win32file.WriteFile(pipe, json.dumps(insights).encode())
```

---

## 🚀 AŞAMA AŞAMA UYGULAMA PLANI

### PHASE 1: Foundation (Gün 1-2)

**Checkpoint 1.1: Project Setup**

```bash
ACTIONS:
✅ Proje klasör yapısını oluştur
✅ Git init, .gitignore
✅ Python venv + requirements.txt
✅ .env.example + config/ dizini

VERIFICATION:
- [ ] Tüm klasörler mevcut
- [ ] Git clean working tree
- [ ] Venv aktif
- [ ] Dependencies yüklü

TOOLS:
- bash_tool: mkdir, git init
- create_file: requirements.txt, .gitignore
- view: Doğrulama için
```

**Checkpoint 1.2: Database Connection**

```python
MODULES:
✅ src/config/settings.py (Pydantic settings)
✅ src/database/connection.py (SQLAlchemy engine)
✅ tests/test_database/test_connection.py

VERIFICATION:
- [ ] Config yükleniyor
- [ ] DB connection başarılı
- [ ] Test geçiyor

TOOLS:
- Context7: SQLAlchemy docs
- Serena: Symbol management
- view: Her dosya oluşumu sonrası
```

**Checkpoint 1.3: Database Inspector**

```python
MODULES:
✅ src/database/inspector.py
   - discover_all_tables()
   - get_table_schema(table_name)
   - export_schema_yaml()

TEST:
✅ 361 tablo keşfedildi mi?
✅ GP_*, DTY_*, LST_*, HRC_* kategorileri

VERIFICATION:
- [ ] Tüm tablolar listelendi
- [ ] Schema YAML dosyası oluştu
- [ ] Primary key'ler tespit edildi

TOOLS:
- Sequential-Thinking: Karmaşık query planlama
- view + bash_tool: Test çalıştırma
```

### PHASE 2: AI Integration (Gün 3-4)

**Checkpoint 2.1: Ollama Client**

```python
MODULES:
✅ src/ai/ollama_client.py
✅ tests/test_ai/test_ollama.py

FEATURES:
- Ollama health check
- Model list
- Completion with retry
- Stream support

TEST:
$ ollama list
$ python -c "from src.ai.ollama_client import OllamaClient; print(OllamaClient().complete('Merhaba'))"

TOOLS:
- Context7: Ollama Python SDK
- Tavily: "ollama python client best practices 2025"
```

**Checkpoint 2.2: Remote AI Clients**

```python
MODULES:
✅ src/ai/anthropic_client.py
✅ src/ai/openai_client.py
✅ src/ai/google_client.py
✅ tests/test_ai/test_remote_clients.py

TEST ENV VARS:
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

VERIFICATION:
- [ ] Her client test edildi
- [ ] Timeout handling çalışıyor
- [ ] Retry logic aktif

TOOLS:
- Context7: anthropic, openai, google-generativeai official docs
```

**Checkpoint 2.3: AI Router (Senaryo A)**

```python
MODULES:
✅ src/ai/router.py
✅ src/ai/prompt_templates.py (Türkçe medical prompts)
✅ tests/test_ai/test_router.py

LOGIC:
def route_request(task_complexity):
    if complexity == 'simple':
        return ollama_client
    elif complexity == 'complex':
        return claude_client  # fallback: openai, gemini
    ...

VERIFICATION:
- [ ] Simple tasks → Ollama
- [ ] Complex tasks → Claude
- [ ] Fallback çalışıyor
- [ ] Config'den değiştirilebilir

TOOLS:
- Sequential-Thinking: Routing algoritması tasarımı
```

### PHASE 3: Clinical Modules (Gün 5-8)

**Checkpoint 3.1: Patient Summarizer**

```python
MODULE: src/clinical/patient_summarizer.py

FEATURES:
- Hasta demografik bilgileri
- Son vizitler (son 12 ay)
- Aktif tanılar (ICD-10)
- Aktif ilaçlar
- Alerji uyarıları
- Lab soncuları özeti

TEST DATA:
- Sentetik hasta: TCKN 12345678901
- Mock data: 10 vizit, 3 tanı, 5 ilaç

TOOLS:
- Serena: find_symbol("GP_HASTA_OZLUK")
- view: Query sonuçları
```

**Checkpoint 3.2: Lab Analyzer**

```python
MODULE: src/clinical/lab_analyzer.py

FEATURES:
- Referans aralığı çıkış tespiti
- Kritik değer flagleme
- Trend analizi (6 ay)
- Z-score hesaplama

TEST CASES:
- HbA1c: 8.4% (yüksek, trend: ↑)
- Kreatinin: 2.1 mg/dL (kritik)
- Potasyum: 5.9 mmol/L (acil)

VERIFICATION:
- [ ] Tüm abnormal değerler tespit edildi
- [ ] Trendler doğru hesaplandı
- [ ] Kritik alarmlar çalışıyor
```

**Checkpoint 3.3: Diagnosis Engine**

```python
MODULE: src/clinical/diagnosis_engine.py

INPUT:
- Şikayetler: "ateş, öksürük, balgam"
- Vitals: Ateş 38.5°C, SpO2 94%
- Lab: CRP 45 mg/L, Lökosit 14000
- Geçmiş: KOAH var

AI PROMPT (Turkish):
"""
Hasta bilgileri:
- Şikayet: {complaints}
- Vital bulgular: {vitals}
- Lab: {labs}
- Geçmiş hastalıklar: {history}

Lütfen diferansiyel tanı listesi ver. Her tanı için:
1. Tanı adı (Türkçe)
2. ICD-10 kodu
3. Olasılık (%)
4. Destekleyen bulgular
5. Kısa açıklama

Format: JSON
"""

OUTPUT EXAMPLE:
{
  "differential_diagnosis": [
    {
      "diagnosis": "Akut Bronşit",
      "icd10": "J20.9",
      "probability": 0.65,
      "supporting": ["öksürük", "balgam", "CRP yüksek"],
      "reasoning": "KOAH zeminine akut enfeksiyon eklenmiş..."
    }
  ]
}

TOOLS:
- ai/router: Complex task → Claude
- Sequential-Thinking: Prompt engineering
```

**Checkpoint 3.4: Treatment Engine**

```python
MODULE: src/clinical/treatment_engine.py

INPUT:
- Confirmed diagnosis: "Tip 2 DM, kontrolsüz"
- Patient factors: Yaş 55, eGFR 70, alerjiler: []
- Current meds: Metformin 1000mg 2x1

AI PROMPT:
"""
Tanı: {diagnosis}
Hasta özellikleri: {patient_profile}
Mevcut tedavi: {current_treatment}

Aşağıdaki kategorilerde önerilerde bulun:
1. İlaç tedavisi (başlangıç, doz değişikliği, ekleme)
2. Yaşam tarzı önerileri
3. Lab takip planı
4. Konsültasyon gerekliliği

Her öneri için priorite (1-3) belirt.
Kontrendikasyonları not et.
JSON formatında dön.
"""

VERIFICATION:
- [ ] Farmakolojik tedavi uygun
- [ ] Kontrendikasyonlar check edildi
- [ ] Follow-up planı net
```

**Checkpoint 3.5: Drug Interaction Checker**

```python
MODULE: src/clinical/drug_interaction.py

APPROACH 1: Local Database
- Türkiye İlaç Kılavuzu offline DB
- Pre-built interaction matrix

APPROACH 2: External API (if available)
- Drugs.com API
- RxNorm API

FALLBACK: AI-based
- Prompt: "Warfarin ve NSAİİ kombinasyonu etkileşimi?"
- Source: Medical literature knowledge

TEST CASES:
- Warfarin + NSAİİ → Major interaction
- Alerji: Penisilin, İlaç: Amoksisilin → Critical
- Metformin + İyotlu kontrast → Warning

TOOLS:
- Tavily: "drug interaction API free 2025"
- Context7: Requests library
```

### PHASE 4: GUI Development (Gün 9-12)

**Checkpoint 4.1: Desktop GUI Skeleton**

```python
MODULE: src/gui/main_window.py

FEATURES:
- QMainWindow
- MenuBar
- StatusBar
- Central widget with tabs

RUN:
$ python src/gui/main_window.py

VERIFICATION:
- [ ] Pencere açılıyor
- [ ] Menüler çalışıyor
- [ ] Tabs görünüyor

TOOLS:
- Context7: PySide6 official docs
- view: UI dosyaları
```

**Checkpoint 4.2: Patient Search Widget**

```python
MODULE: src/gui/widgets/patient_search.py

FEATURES:
- Search by TCKN
- Search by name
- Autocomplete
- Results table

INTEGRATION:
- Database query
- Signal: patient_selected(tckn)

TOOLS:
- Serena: PySide6 signal/slot verification
```

**Checkpoint 4.3: Clinical Dashboard**

```python
MODULES:
✅ src/gui/widgets/clinical_dashboard.py
✅ src/gui/widgets/diagnosis_panel.py
✅ src/gui/widgets/treatment_panel.py
✅ src/gui/widgets/lab_charts.py

FEATURES:
- Tab-based interface
- Real-time AI analysis
- Chart.js integration (via QWebEngine)
- Drug interaction alerts

VERIFICATION:
- [ ] Tüm paneller render oluyor
- [ ] AI butonu tetikleniyor
- [ ] Sonuçlar görüntüleniyor
```

**Checkpoint 4.4: Web GUI Setup**

```bash
ACTIONS:
$ cd frontend
$ npm create vite@latest . -- --template react-ts
$ npm install

COMPONENTS:
✅ src/components/PatientSearch.tsx
✅ src/components/ClinicalDashboard.tsx
✅ src/components/DiagnosisPanel.tsx
✅ src/components/TreatmentPanel.tsx

API CLIENT:
✅ src/services/api.ts (axios)

RUN:
$ npm run dev
# http://localhost:5173

VERIFICATION:
- [ ] Dev server başlıyor
- [ ] API calls çalışıyor (mock)
- [ ] UI responsive

TOOLS:
- Context7: React, Vite docs
- bash_tool: npm commands
```

### PHASE 5: API Layer (Gün 13-14)

**Checkpoint 5.1: FastAPI Setup**

```python
MODULE: src/api/fastapi_app.py

ENDPOINTS:
- GET /health
- GET /api/v1/patients/search?q={query}
- GET /api/v1/patients/{tckn}
- POST /api/v1/analyze/diagnosis
- POST /api/v1/analyze/treatment
- GET /api/v1/labs/{tckn}/trends

RUN:
$ uvicorn src.api.fastapi_app:app --reload --port 8080

TEST:
$ curl http://localhost:8080/health
$ curl http://localhost:8080/api/v1/patients/12345678901

VERIFICATION:
- [ ] API başlıyor
- [ ] Endpoints yanıt veriyor
- [ ] CORS configured (localhost only)

TOOLS:
- Context7: FastAPI official docs
- bash_tool: curl testing
```

**Checkpoint 5.2: CLI Commands**

```python
MODULE: src/cli/app.py

COMMANDS:
- clinical-ai analyze --tckn {tckn}
- clinical-ai diagnose --tckn {tckn} --complaint "{text}"
- clinical-ai inspect database
- clinical-ai config set-model {model_name}

INSTALL:
$ pip install -e .
$ clinical-ai --help

VERIFICATION:
- [ ] CLI yüklü
- [ ] Komutlar çalışıyor
- [ ] Output formatları doğru

TOOLS:
- Context7: Typer, Rich docs
```

### PHASE 6: Testing & Refinement (Gün 15-16)

**Checkpoint 6.1: Unit Tests**

```bash
$ pytest tests/unit/ -v --cov=src

TARGET: >80% coverage

CRITICAL TESTS:
- Database connection
- AI routing logic
- Clinical engines
- Drug interaction

TOOLS:
- bash_tool: pytest
- view: Coverage report
```

**Checkpoint 6.2: Integration Tests**

```python
TESTS:
✅ test_full_patient_workflow.py
✅ test_diagnosis_to_treatment_pipeline.py
✅ test_api_endpoints.py

RUN:
$ pytest tests/integration/ -v

TOOLS:
- faker: Synthetic patient data
- pytest-asyncio: Async testing
```

**Checkpoint 6.3: Performance Testing**

```python
TEST SCENARIOS:
- 1000 hasta ile database query speed
- AI response time (Ollama vs Claude)
- Concurrent API requests (10 users)

BENCHMARK:
- Patient summary: <2s
- Diagnosis generation: <30s
- Lab analysis: <5s

TOOLS:
- Sequential-Thinking: Performance bottleneck analysis
```

### PHASE 7: Documentation & Deployment (Gün 17-18)

**Checkpoint 7.1: Documentation**

```markdown
DOCS TO CREATE:
✅ docs/01_KURULUM.md
✅ docs/02_VERITABANI_BAGLANTI.md
✅ docs/03_AI_KONFIGURASYONU.md
✅ docs/04_KULLANIM_GUI.md
✅ docs/05_KULLANIM_CLI.md
✅ docs/06_API_DOKUMANTASYON.md
✅ docs/07_ENTEGRASYON.md
✅ docs/08_SORUN_GIDERME.md
✅ README.md (comprehensive)

TOOLS:

- create_file: Her doküman
- view: Verification
```

**Checkpoint 7.2: Deployment Scripts**

```bash
SCRIPTS:
✅ scripts/install.bat
✅ scripts/run_desktop.bat
✅ scripts/run_web.bat
✅ scripts/run_cli.bat

OPTIONAL:
✅ build/pyinstaller.spec
✅ PyInstaller build test

RUN:
$ pyinstaller build/pyinstaller.spec
$ dist/ClinicalAI.exe

VERIFICATION:
- [ ] Exe çalışıyor
- [ ] Dependencies bundled
- [ ] Size reasonable (<500MB)
```

---

## ✅ FINAL DELIVERY CHECKLIST

```yaml
✅ CODE:
  - [ ] All modules complete
  - [ ] Type hints full coverage
  - [ ] Docstrings comprehensive
  - [ ] No linter errors (ruff)
  - [ ] Test coverage >80%
  - [ ] Turkish language support verified

✅ AI INTEGRATION:
  - [ ] Ollama connected
  - [ ] Claude API working
  - [ ] OpenAI API working
  - [ ] Gemini API working
  - [ ] Router logic tested
  - [ ] Fallback mechanism works

✅ CLINICAL FEATURES:
  - [ ] Diagnosis suggestions functional
  - [ ] Treatment recommendations accurate
  - [ ] Drug interactions checked
  - [ ] Lab analysis complete
  - [ ] Risk calculations verified

✅ DATABASE:
  - [ ] All 361 tables discovered
  - [ ] Critical tables mapped
  - [ ] Queries optimized
  - [ ] Connection pooling active

✅ UI:
  - [ ] Desktop GUI polished
  - [ ] Web GUI responsive
  - [ ] CLI commands complete
  - [ ] Turkish text correct

✅ API:
  - [ ] All endpoints working
  - [ ] Authentication (none required)
  - [ ] Error handling robust
  - [ ] CORS configured

✅ INTEGRATION:
  - [ ] REST API method documented
  - [ ] CLI subprocess method documented
  - [ ] Database trigger example provided
  - [ ] IPC method (optional) included

✅ DOCUMENTATION:
  - [ ] Installation guide complete
  - [ ] User manual comprehensive
  - [ ] API reference clear
  - [ ] Troubleshooting section

✅ DEPLOYMENT:
  - [ ] requirements.txt accurate
  - [ ] .env.example provided
  - [ ] Install scripts working
  - [ ] PyInstaller build successful (optional)

✅ TESTING:
  - [ ] Unit tests pass
  - [ ] Integration tests pass
  - [ ] Performance acceptable
  - [ ] No critical bugs
```

---

## 🎯 EXECUTION START

### Pre-Flight Checklist

```bash
BEFORE STARTING:
1. ✅ Python 3.11 installed
2. ✅ SQL Server 2014/2022 accessible
3. ✅ ODBC Driver 18 installed
4. ✅ Ollama installed and running (ollama serve)
5. ✅ API keys ready:
   - ANTHROPIC_API_KEY
   - OPENAI_API_KEY
   - GOOGLE_API_KEY
6. ✅ Git configured
7. ✅ VS Code / PyCharm ready

INITIAL COMMANDS:
$ ollama pull gemma:7b  # or qwen2.5:7b
$ ollama serve  # Keep running in background
```

### Start Command

```
CLAUDE CODE, PROJE ŞU ADIMLARLA BAŞLASIN:

1. Tool Setup
   - Context7 ready for library docs
   - Tavily ready for best practices
   - Serena ready for code navigation
   - Sequential-Thinking for complex decisions

2. Project Creation
   - Create folder structure
   - Initialize Git
   - Setup Python venv
   - Install dependencies

3. Phase 1: Foundation
   - Database connection
   - Schema inspector
   - Initial tests

4. Proceed step-by-step with verification checkpoints

HER CHECKPOINT SONRASI:
- Çalışan kodu göster
- Test sonuçlarını göster
- Bir sonraki adımı açıkla
- Onay iste

BAŞLA! 🚀
```

---

**🎯 HEDEF: Production-ready, AI-powered, multi-interface clinical decision support system with full Turkish support, no security constraints, complete diagnosis and treatment capabilities!**

**📊 PROJE KAPSAMASI: ~18 gün (profesyonel hız), tek developer, modüler yaklaşım, test-first methodology, reliable tech stack only!**
