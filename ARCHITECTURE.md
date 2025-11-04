# Sistem Mimarisi

## Genel Yapı

```
Frontend (React) → API (FastAPI) → Database (SQL Server 2014)
                        ↓
                   AI Router
                   (Ollama/Cloud)
```

## Backend (src/)

```
src/
├── api/
│   ├── fastapi_app.py        # Ana uygulama
│   └── routes/               # Endpoint'ler
│       ├── patient.py        # Hasta işlemleri
│       ├── diagnosis.py      # AI tanı
│       ├── treatment.py      # Tedavi önerileri
│       └── ...
│
├── database/
│   ├── models.py             # Veritabanı modelleri
│   └── connection.py         # Bağlantı
│
├── ai/
│   ├── router.py             # AI sağlayıcı seçimi
│   └── providers/            # AI entegrasyonları
│
└── analytics/                # Analiz modülleri
```

## Frontend (frontend/)

```
frontend/src/
├── components/               # Bileşenler
├── pages/                    # Sayfalar
│   ├── Dashboard.tsx
│   ├── PatientSearch.tsx
│   └── PatientDetails.tsx
├── services/                 # API çağrıları
└── store/                    # State yönetimi (Zustand)
```

## Veritabanı

**Ana Tablolar**:
- `Patient` - Hasta bilgileri
- `Visit` - Ziyaret kayıtları
- `Diagnosis` - Tanılar
- `Treatment` - Tedaviler
- `Laboratory` - Lab sonuçları

**İlişkiler**:
```
Patient (1) → (N) Visit
Visit (1) → (N) Diagnosis
Visit (1) → (N) Treatment
Visit (1) → (N) Laboratory
```

## AI Entegrasyonu

**Sağlayıcı Önceliği**:
1. **Ollama** (MedGemma 4B) - Lokal, ücretsiz
2. **Anthropic** (Claude) - Yedek
3. **OpenAI** (GPT) - Yedek
4. **Google** (Gemini) - Yedek

**Görev Dağılımı**:
- Basit sorgular → Ollama
- Orta karmaşıklık → Ollama
- Kritik kararlar → Claude/GPT (yoksa Ollama)

## Konfigürasyon

**`.env`**:
```env
DATABASE_URL=mssql+pyodbc://server\\instance/db?...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b
```

**`config/ai_models.yaml`**:
```yaml
routing:
  simple: [ollama]
  moderate: [ollama]
  complex: [claude-sonnet-4.5, gpt-5, ollama]
```

## Teknoloji

- **Backend**: FastAPI + Python 3.10.11 + SQLAlchemy + PyODBC
- **Frontend**: React 18 + TypeScript 5 + Vite 5 + Tailwind CSS
- **Database**: SQL Server 2014+ (Windows Auth)
- **AI**: Ollama + Cloud APIs (optional)

## Çalıştırma

```bash
# Backend
uvicorn src.api.fastapi_app:app --reload

# Frontend
cd frontend && npm run dev
```
