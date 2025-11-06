# Clinical AI Assistant 🏥

AI destekli aile hekimliği karar destek sistemi. Hasta kayıtları, diferansiyel tanı önerileri, tedavi planları ve ilaç etkileşim kontrolü sağlar.

## 🎯 Özellikler

- 📋 **Hasta Yönetimi**: TCKN bazlı hasta arama ve kayıt görüntüleme
- 🧠 **AI Destekli Tanı**: GPT-4o, Claude, Gemini veya Ollama ile diferansiyel tanı
- 💊 **Tedavi Planlama**: Evidence-based tedavi önerileri ve kılavuzlar
- ⚠️ **İlaç Etkileşimleri**: Otomatik etkileşim kontrolü ve uyarılar
- 📊 **Lab Takibi**: Laboratuvar sonuçları trend analizi ve görselleştirme
- 🔍 **ICD-10 Kodlama**: Otomatik ICD-10 kod eşleştirme

## 🚀 Hızlı Başlangıç

### Gereksinimler

- **Python**: 3.10.11+
- **Node.js**: 18+
- **SQL Server**: 2014+ (Windows Authentication)
- **ODBC Driver**: 17 veya 18
- **Ollama** (opsiyonel): Ücretsiz lokal AI

### 1. Backend Kurulumu

```bash
# Virtual environment oluştur ve bağımlılıkları yükle
scripts\install.bat

# .env dosyasını yapılandır
copy .env.example .env
# .env dosyasını editörde aç ve veritabanı ayarlarını düzenle
```

### 2. Veritabanı Yapılandırması

`.env` dosyasını düzenleyin:

```env
# Ana veritabanı (READ-ONLY)
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/HastaDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# AI Ayarları (Ollama - Ücretsiz)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b

# Opsiyonel Cloud AI
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
```

**ICD-10 Kodlarını Migrate Et**:

```bash
# App veritabanını oluştur ve ICD kodlarını yükle
python scripts\migrate_icd_codes.py
```

### 3. Frontend Kurulumu

```bash
# Node.js bağımlılıklarını yükle ve build et
scripts\setup-frontend.bat
```

### 4. Ollama Kurulumu (Opsiyonel)

Ücretsiz lokal AI için:

```bash
# 1. https://ollama.ai adresinden indir ve kur
# 2. Medical model'i çek
ollama pull medgemma:4b

# 3. Ollama servisini başlat
ollama serve
```

### 5. Uygulamayı Başlat

```bash
# Otomatik başlatma (önerilen)
scripts\quickstart.bat

# Manuel başlatma
# Terminal 1 - Backend
venv\Scripts\activate
uvicorn src.api.fastapi_app:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🌐 Erişim

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## 📁 Proje Yapısı

```
PatientSystem/
├── src/                      # Backend (Python/FastAPI)
│   ├── api/                  # API routes ve endpoints
│   │   └── routes/           # Patient, diagnosis, treatment routes
│   ├── clinical/             # Klinik modüller
│   │   ├── diagnosis_engine.py    # Tanı motoru
│   │   ├── treatment_engine.py    # Tedavi planlama
│   │   └── prompt_builder.py      # Template-based promptlar
│   ├── database/             # Veritabanı yönetimi
│   │   ├── connection.py     # MSSQL bağlantısı (READ-ONLY)
│   │   ├── app_database.py   # SQLite (ICD, logs, sessions)
│   │   └── dependencies.py   # FastAPI dependency injection
│   ├── ai/                   # AI entegrasyonları
│   │   ├── router.py         # Smart AI routing
│   │   └── *_client.py       # Provider clients
│   └── models/               # SQLAlchemy modelleri
│
├── frontend/                 # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/       # UI bileşenleri
│   │   ├── pages/           # Sayfa bileşenleri
│   │   ├── services/        # API client (axios)
│   │   ├── stores/          # State management (Zustand)
│   │   └── utils/           # Logger ve yardımcılar
│   └── dist/                # Production build
│
├── scripts/                  # Kurulum ve yardımcı scriptler
│   ├── migrate_icd_codes.py # ICD-10 migrasyon
│   └── *.bat                # Windows batch scriptleri
│
└── data/                     # Uygulama veritabanı
    └── app.db               # SQLite (ICD codes, logs, sessions)
```

## 🏗️ Mimari

### Dual Database Architecture

1. **Ana Veritabanı (MSSQL)**
   - READ-ONLY mod
   - Hasta klinik verileri
   - Lab sonuçları, ziyaretler, tanılar
   - SQL Server 2014/2022 uyumlu

2. **Uygulama Veritabanı (SQLite)**
   - READ-WRITE mod
   - ICD-10 kod eşleştirmeleri
   - Uygulama logları
   - Session yönetimi

### Tech Stack

**Backend**:
- FastAPI (async web framework)
- SQLAlchemy (ORM)
- Loguru (logging)
- Pydantic (validation)

**Frontend**:
- React 18 + TypeScript
- Vite (build tool)
- Zustand (state management)
- Axios + axios-retry (HTTP client)
- Tailwind CSS

**AI Integration**:
- Ollama (local, free)
- Claude-Sonnet-4.5
- GPT-5
- Gemini-2.5-flash

## 🔧 Yapılandırma

### Ortam Değişkenleri

```env
# Database (Main - READ ONLY)
DATABASE_URL=mssql+pyodbc://...

# AI Providers
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
API_PORT=8000
```

### FastAPI Dependency Injection

```python
from src.database.dependencies import get_db
from sqlalchemy.orm import Session

@router.get("/patients/search")
async def search_patients(
    q: str,
    db: Session = Depends(get_db)  # Otomatik session yönetimi
):
    results = db.query(Patient).filter(...).all()
    return results
```

## 📊 Performans

### Optimizasyonlar

- ✅ **N+1 Query Elimination**: 75% daha hızlı sorgu performansı
- ✅ **Connection Pooling**: 100+ eşzamanlı bağlantı desteği
- ✅ **Frontend Logging**: Production'da 0 overhead
- ✅ **Template-based Prompts**: Bakım kolaylığı ve test edilebilirlik

### Beklenen Performans

- **API Response Time**: P95 < 500ms
- **Query Latency**: ~50ms (avg)
- **Frontend Bundle**: 252KB (gzipped: 80KB)
- **Retry Success Rate**: >80%

## 🐛 Sorun Giderme

### Veritabanı Bağlantı Hatası

```bash
# SQL Server çalışıyor mu?
services.msc  # SQL Server servisini kontrol et

# ODBC Driver kurulu mu?
odbcad32.exe  # ODBC Data Source Administrator

# Connection string doğru mu?
# .env dosyasını kontrol et
```

### Ollama Çalışmıyor

```bash
# Model indirilmiş mi?
ollama list

# Servis çalışıyor mu?
ollama serve

# Port doğru mu?
# Default: http://localhost:11434
```

### Frontend Build Hatası

```bash
# Node modules temizle ve yeniden yükle
cd frontend
rm -rf node_modules
npm install

# Build tekrar dene
npm run build
```

### ICD Kodları Yüklenmiyor

```bash
# Migration scriptini çalıştır
python scripts\migrate_icd_codes.py

# App database'i kontrol et
ls -la data/app.db  # Dosya var mı?
```

## 📚 API Kullanımı

### Hasta Arama

```bash
curl -X GET "http://localhost:8000/api/patients/search?q=ahmet&limit=10"
```

### Tanı Oluşturma

```bash
curl -X POST "http://localhost:8000/api/analyze/diagnosis" \
  -H "Content-Type: application/json" \
  -d '{
    "tckn": "12345678901",
    "chief_complaint": "Baş ağrısı ve ateş",
    "model": "claude"
  }'
```

### Lab Sonuçları

```bash
curl -X GET "http://localhost:8000/api/labs/12345678901?test=Hemoglobin"
```

## 🚦 Geliştirme

### Development Mode

```bash
# Backend hot-reload
uvicorn src.api.fastapi_app:app --reload

# Frontend hot-reload
cd frontend && npm run dev
```

### Production Build

```bash
# Frontend build
cd frontend && npm run build

# Backend production
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Code Quality

```bash
# Python linting
black src/
isort src/

# Frontend linting
cd frontend
npm run lint
```

## 📝 Önemli Notlar

### Güvenlik

- Ana veritabanı **READ-ONLY** modda çalışır
- SQL injection koruması mevcut (parametreli sorgular)
- Input validation aktif (Pydantic)
- CORS yapılandırması gerekli

### Veritabanı

- **MSSQL 2014/2022** uyumlu
- Windows Authentication önerilen
- Connection pooling etkin (10 pool size, 20 max overflow)
- READ-ONLY mode otomatik (değiştirilebilir)

### Deployment

- Multi-process deployment için dependency injection kullanın
- SQLite app.db dosyasını yedekleyin
- `.env` dosyasını versiyonlamayın
- Production'da LOG_LEVEL=INFO kullanın

## 📖 Dokümantasyon

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API Redoc**: http://localhost:8000/redoc (Alternative API docs)
- **IMPLEMENTATION_SUMMARY.md**: Son implementasyon detayları ve değişiklikler

## 🤝 Katkı

Bu proje kişisel kullanım için geliştirilmiştir. Katkı yapmak isterseniz:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yenilik`)
3. Commit yapın (`git commit -m 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yenilik`)
5. Pull Request açın

## 📄 Lisans

Bu proje kişisel kullanım içindir. Ticari kullanım için izin gereklidir.

## 🆘 Destek

Sorun yaşarsanız:

1. GitHub Issues'a bakın
2. API dokümantasyonunu kontrol edin: `/docs`
3. Log dosyalarını inceleyin: `LOG_LEVEL=DEBUG`

---

**Not**: Bu sistem yardımcı bir araçtır. Tıbbi kararlar hekimin bilgi ve deneyimi ile alınmalıdır. AI önerileri referans amaçlıdır.
