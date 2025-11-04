# Clinical AI Assistant

Hasta yönetimi ve AI destekli tıbbi analiz sistemi.

## Ne İşe Yarar

- Hasta kayıtları ve ziyaret geçmişi
- Semptomlara göre AI destekli tanı önerileri
- Tedavi önerileri ve ilaç etkileşim kontrolü
- Laboratuvar sonuçları takibi
- İlaç uyum analizi

## Gereksinimler

- Python 3.10.11+
- Node.js 18+
- SQL Server 2014+ (Windows Authentication)
- ODBC Driver 17 veya 18
- Ollama (ücretsiz, lokal AI için)

## Kurulum

### 1. Backend

```bash
scripts\install.bat
```

### 2. Frontend

```bash
scripts\setup-frontend.bat
```

### 3. Veritabanı

`.env` dosyasını düzenle:

```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

Veritabanını başlat:

```bash
python scripts\init_db.py
```

### 4. AI (Ollama)

1. https://ollama.ai adresinden indir ve kur
2. Medical model'i çek:

```bash
ollama pull medgemma:4b
```

### 5. Başlat

```bash
scripts\quickstart.bat
```

Veya manuel:

```bash
# Backend
venv\Scripts\activate
uvicorn src.api.fastapi_app:app --reload

# Frontend (başka terminal)
cd frontend
npm run dev
```

## Erişim

- **Uygulama**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## Yapı

```
PatientSystem/
├── src/              # Backend (FastAPI)
├── frontend/         # Frontend (React)
├── scripts/          # Kurulum scriptleri
├── config/           # Konfigürasyon
└── docs/             # Dökümanlar
```

## Sorun Giderme

**Veritabanı bağlanamıyor**:

- SQL Server çalışıyor mu kontrol et
- Windows Authentication aktif mi bak
- ODBC Driver kurulu mu kontrol et

**Ollama çalışmıyor**:

- `ollama list` ile model indirilmiş mi bak
- `ollama serve` ile servisi başlat

## Dokümantasyon

- [ARCHITECTURE.md](ARCHITECTURE.md) - Sistem mimarisi
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - Ayarlar
- [docs/API.md](docs/API.md) - API referansı
