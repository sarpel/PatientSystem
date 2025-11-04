# 🏥 KLİNİK KARAR DESTEK SİSTEMİ - SADELEŞTİRİLMİŞ PROJE PLANI

## 🎯 PROJE ÖZETİ

Aile hekimliği için **SQL Server 2014/2022** veritabanı üzerinde çalışan, **AI destekli** (Ollama + OpenAI + Claude + Gemini) klinik karar destek sistemi. Tanı önerisi, tedavi planlaması ve ilaç etkileşimi kontrolü sağlar.

---

## 🔧 TEMEL PARAMETRELERİ

```yaml
ORTAM:
  Platform: Windows 11
  Python: 3.11+
  Database: SQL Server 2014/2022 Express
  User: Tek kullanıcı (hekim)
  
KLİNİK ÖZELLİKLER:
  Tanı Önerisi: ✅ Olasılık skorları ile
  Tedavi Önerisi: ✅ İlaç, test, yaşam tarzı
  İlaç Etkileşimi: ✅ Temel kontrol
  Lab Analizi: ✅ Anormal değer tespiti
  Risk Hesaplama: ✅ Basit risk skorları
  
AI ENTEGRASYONU:
  Local: Ollama (Gemma/Qwen) 
  Remote 1: Claude 3.5 Sonnet
  Remote 2: OpenAI GPT-4
  Remote 3: Google Gemini Pro
  
ARAYÜZLER:
  Desktop: PySide6 (Qt6) GUI
  Web: React + FastAPI 
  CLI: Typer komut satırı
```

---

## 📁 BASİTLEŞTİRİLMİŞ PROJE YAPISI

```
clinical-ai-assistant/
├── src/                              # Ana uygulama kodu
│   ├── main.py                       # Uygulama giriş noktası
│   ├── config/
│   │   └── settings.py               # Temel ayarlar
│   ├── database/
│   │   ├── connection.py             # SQL Server bağlantısı
│   │   ├── models.py                 # Veritabanı modelleri
│   │   └── queries.py                # SQL sorguları
│   ├── ai/
│   │   ├── ollama_client.py          # Lokal AI
│   │   ├── openai_client.py          # OpenAI entegrasyonu
│   │   ├── anthropic_client.py       # Claude entegrasyonu
│   │   └── google_client.py          # Gemini entegrasyonu
│   ├── clinical/
│   │   ├── diagnosis.py              # Tanı önerileri
│   │   ├── treatment.py              # Tedavi önerileri
│   │   ├── drug_check.py             # İlaç etkileşimi
│   │   └── lab_analyzer.py           # Lab sonuç analizi
│   ├── api/
│   │   ├── app.py                    # FastAPI server
│   │   └── endpoints.py              # API endpoint'leri
│   └── utils/
│       ├── logger.py                 # Basit loglama
│       └── helpers.py                # Yardımcı fonksiyonlar
│
├── gui/                              # Desktop arayüzü
│   ├── main_window.py                # Ana pencere
│   ├── patient_widget.py             # Hasta arama/görüntüleme
│   ├── diagnosis_widget.py           # Tanı paneli
│   └── treatment_widget.py           # Tedavi paneli
│
├── web/                              # Web arayüzü  
│   ├── src/
│   │   ├── App.jsx                   # React ana bileşen
│   │   ├── components/               # UI bileşenleri
│   │   └── api.js                    # Backend bağlantısı
│   └── package.json
│
├── cli/                              # Komut satırı
│   └── app.py                        # CLI komutları
│
├── docs/                             # Basit dokümantasyon
│   ├── README.md                     # Kurulum ve kullanım
│   └── API.md                        # API dokümantasyonu
│
├── scripts/                          # Başlatma scriptleri
│   ├── setup.bat                     # Kurulum
│   ├── start_gui.bat                 # GUI başlatma
│   └── start_web.bat                 # Web server başlatma
│
├── .env.example                      # Örnek environment dosyası
└── requirements.txt                  # Python bağımlılıkları
```

---

## 📦 MİNİMAL BAĞIMLILIKLAR

```python
# requirements.txt

# Database
sqlalchemy==2.0.23
pyodbc==5.0.1

# Data Processing
pandas==2.1.4
numpy==1.26.2

# AI SDKs
openai==1.6.1
anthropic==0.8.1
google-generativeai==0.3.1
ollama==0.1.6

# Web API
fastapi==0.108.0
uvicorn==0.25.0
pydantic==2.5.3

# Desktop GUI
PySide6==6.6.1

# CLI
typer==0.9.0
rich==13.7.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
loguru==0.7.2
```

---

## 🚀 HIZLI BAŞLANGIÇ

### 1. Ortam Hazırlığı

```bash
# Python sanal ortamı
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ollama kurulumu (eğer lokal AI istenirse)
# https://ollama.ai adresinden indir ve kur
ollama pull gemma:7b
```

### 2. Yapılandırma

`.env` dosyası oluştur:
```env
# Database
DB_SERVER=localhost
DB_NAME=AHBS_DB
DB_DRIVER=ODBC Driver 18 for SQL Server

# AI API Keys (opsiyonel)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Local AI
OLLAMA_HOST=http://localhost:11434
```

### 3. Veritabanı Bağlantısı Test

```python
# src/database/connection.py
from sqlalchemy import create_engine
import pyodbc

def get_connection():
    conn_str = f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}&trusted_connection=yes"
    engine = create_engine(conn_str)
    return engine

# Test
engine = get_connection()
with engine.connect() as conn:
    result = conn.execute("SELECT TOP 1 * FROM GP_HASTAKAYIT")
    print(result.fetchone())
```

---

## 💻 KULLANIM ÖRNEKLERİ

### Desktop GUI
```bash
python gui/main_window.py
```

### Web Interface
```bash
# Backend
uvicorn src.api.app:app --reload

# Frontend
cd web && npm start
```

### CLI
```bash
# Hasta analizi
python cli/app.py analyze --tckn 12345678901

# Tanı önerisi
python cli/app.py diagnose --complaint "baş ağrısı ve ateş"
```

---

## 🔌 BASİT API KULLANIMI

### Hasta Özeti
```python
GET /api/patient/{tckn}/summary
```

### Tanı Önerisi
```python
POST /api/diagnosis
{
    "tckn": "12345678901",
    "complaint": "Karın ağrısı ve bulantı",
    "symptoms": ["ağrı", "bulantı", "ateş"]
}
```

### Tedavi Önerisi
```python
POST /api/treatment
{
    "tckn": "12345678901", 
    "diagnosis_code": "K29.7"
}
```

---

## 📊 TEMEL KLİNİK FONKSİYONLAR

### 1. Tanı Önerisi
```python
# src/clinical/diagnosis.py
def suggest_diagnosis(symptoms, patient_history):
    # AI modellerini kullanarak tanı öner
    # Olasılık skorları ile döndür
    pass
```

### 2. Tedavi Planı
```python
# src/clinical/treatment.py  
def create_treatment_plan(diagnosis, patient_data):
    # İlaç, test ve yaşam tarzı önerileri
    pass
```

### 3. İlaç Kontrolü
```python
# src/clinical/drug_check.py
def check_drug_interactions(medications):
    # Basit etkileşim kontrolü
    pass
```

### 4. Lab Analizi
```python
# src/clinical/lab_analyzer.py
def analyze_lab_results(lab_data):
    # Anormal değerleri tespit et
    # Trend analizi yap
    pass
```

---

## 🎯 GELİŞTİRME ADIMLARI

### Adım 1: Temel Altyapı (2 gün)
- [ ] Proje klasör yapısını oluştur
- [ ] Veritabanı bağlantısını kur
- [ ] Temel configuration dosyalarını hazırla

### Adım 2: AI Entegrasyonları (2 gün)
- [ ] Ollama bağlantısı
- [ ] OpenAI/Claude/Gemini client'ları
- [ ] Basit router mantığı

### Adım 3: Klinik Modüller (3 gün)
- [ ] Tanı önerisi modülü
- [ ] Tedavi planlama modülü
- [ ] İlaç kontrolü
- [ ] Lab analizi

### Adım 4: API Geliştirme (2 gün)
- [ ] FastAPI server
- [ ] Temel endpoint'ler
- [ ] Basit error handling

### Adım 5: Desktop GUI (3 gün)
- [ ] Ana pencere tasarımı
- [ ] Hasta arama/görüntüleme
- [ ] Tanı ve tedavi panelleri

### Adım 6: Web Arayüzü (2 gün)
- [ ] React setup
- [ ] Temel component'ler
- [ ] API bağlantısı

### Adım 7: CLI (1 gün)
- [ ] Typer komutları
- [ ] Basit output formatları

### Adım 8: Test & Dokümantasyon (2 gün)
- [ ] Temel testler
- [ ] Kullanım dokümantasyonu
- [ ] Örnek scriptler

---

## 📝 NOTLAR

- **Güvenlik:** Development ortamı için güvenlik özellikleri devre dışı
- **Test:** Zorunlu test coverage yok, sadece kritik fonksiyonlar test edilecek  
- **Deployment:** Basit script dosyaları ile çalıştırma
- **Monitoring:** Log dosyaları ile basit takip
- **Dokümantasyon:** Minimal, sadece temel kullanım

---

## ✅ BAŞARILI PROJE KRİTERLERİ

1. **Veritabanı bağlantısı çalışıyor**
2. **En az bir AI modeli entegre**
3. **Tanı önerisi yapabiliyor**
4. **Tedavi planı oluşturabiliyor**
5. **Basit GUI veya Web arayüzü var**
6. **Temel API endpoint'leri çalışıyor**

---

**🎯 ANA HEDEF:** Fonksiyonel, kullanılabilir, sade bir klinik karar destek sistemi. Gereksiz karmaşıklık yok, sadece core özellikler!