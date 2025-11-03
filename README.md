# 🏥 Clinical AI Assistant - Hasta Klinik Karar Destek Sistemi

## 📋 Proje Özeti

Aile hekimliği pratiği için **SQL Server** tabanlı, **multi-AI destekli** (Local Ollama + Anthropic Claude + OpenAI + Google Gemini), **hybrid interface** (Desktop GUI + Web GUI + CLI) klinik karar destek sistemi.

### Ana Özellikler

- ✅ **Tanı Önerisi**: Diferansiyel tanı önerileri ile olasılık skorları
- ✅ **Tedavi Önerisi**: İlaç, test, konsültasyon ve yaşam tarzı önerileri
- ✅ **İlaç Etkileşimi**: İlaç-ilaç, ilaç-alerji kontrolleri
- ✅ **Lab Analizi**: Anormal değer tespiti ve trend analizi
- ✅ **Risk Stratifikasyonu**: KVH, diyabet, CKD risk hesaplamaları

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- SQL Server 2014/2022
- Windows 11
- Ollama (opsiyonel, lokal AI için)

### Adım 1: Repository Klonlama

```bash
git clone <repository-url>
cd PatientSystem
```

### Adım 2: Virtual Environment Oluşturma

```bash
python -m venv venv
venv\Scripts\activate
```

### Adım 3: Dependencies Yükleme

```bash
pip install -r requirements.txt
```

### Adım 4: Konfigürasyon

`.env` dosyası oluşturun (`.env.example` dosyasından):

```bash
cp .env.example .env
```

API anahtarlarını `.env` dosyasına ekleyin:

```env
DB_SERVER=Sarpel-PC\HIZIR
DB_NAME=TestDB

ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
```

## 📖 Kullanım

### Desktop GUI

```bash
python src/gui/main_window.py
```

### Web Interface

```bash
# Backend başlatma
uvicorn src.api.fastapi_app:app --reload --port 8080

# Frontend (ayrı terminalde)
cd frontend
npm install
npm run dev
```

### CLI

```bash
# Hasta analizi
python -m src.cli.app analyze --tckn 12345678901

# Tanı önerisi
python -m src.cli.app diagnose --tckn 12345678901 --complaint "ateş, öksürük"

# Veritabanı inspeksiyon
python -m src.cli.app inspect database
```

## 🏗️ Proje Yapısı

```
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
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage raporu
pytest --cov=src --cov-report=html

# Specific test
pytest tests/unit/test_database/
```

## 📚 Dokümantasyon

Detaylı dokümantasyon için `docs/` klasörüne bakınız:

- [Kurulum Rehberi](docs/01_KURULUM.md)
- [Veritabanı Bağlantısı](docs/02_VERITABANI_BAGLANTI.md)
- [AI Konfigürasyonu](docs/03_AI_KONFIGURASYONU.md)
- [GUI Kullanımı](docs/04_KULLANIM_GUI.md)
- [CLI Kullanımı](docs/05_KULLANIM_CLI.md)
- [API Dokümantasyonu](docs/06_API_DOKUMANTASYON.md)

## 🔧 Geliştirme

```bash
# Dev dependencies yükle
pip install -r requirements-dev.txt

# Code formatting
black src/

# Linting
ruff check src/

# Type checking
mypy src/
```

## 📊 Veritabanı

Sistem 361 SQL Server tablosunu analiz eder:

- GP*HASTA*\*: Hasta demografik bilgileri
- GP_MUAYENE\*: Muayene ve vizit kayıtları
- GP_RECETE\*: Reçete ve ilaç bilgileri
- GP_HASTANE_TETKIK\*: Lab sonuçları
- LST\_\*: Referans tabloları
- DTY\_\*: Detay tabloları

## 🤖 AI Entegrasyonu

**Senaryo A: Hybrid Smart Routing**

- **Basit görevler** → Ollama (hızlı, lokal)
- **Karmaşık klinik kararlar** → Claude 3.5 Sonnet (en akıllı)
- **Fallback** → GPT-4o → Gemini Pro

## 📄 Lisans

Bu proje kişisel kullanım içindir. KVKK ve güvenlik gereksinimleri devre dışıdır (kişisel, güvenli ortam).

## 🛠️ Teknoloji Stack

**Backend:**

- Python 3.11
- SQLAlchemy 2.0
- FastAPI
- Pydantic

**Frontend:**

- React 18
- Vite
- Tailwind CSS

**Desktop:**

- PySide6 (Qt6)

**AI:**

- Anthropic Claude
- OpenAI GPT-4
- Google Gemini
- Ollama (local)

---

**Sürüm:** 0.1.0 (Phase 1 - Foundation)
**Durum:** Development
