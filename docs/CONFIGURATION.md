# Konfigürasyon

## .env Dosyası

`.env.example` dosyasını `.env` olarak kopyala ve düzenle:

```env
# Veritabanı (Windows Authentication)
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# AI - Ollama (Lokal, Ücretsiz)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b

# Opsiyonel Cloud AI
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Uygulama
LOG_LEVEL=DEBUG
ENVIRONMENT=development
API_PORT=8080
```

## Veritabanı

**Bağlantı String Yapısı**:

```
mssql+pyodbc://<sunucu>\\<instance>/<veritabanı>?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Örnek**:

```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**ODBC Driver**:

- Windows: [Microsoft'tan indir](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Linux: `apt-get install msodbcsql17`

**Veritabanı Başlatma**:

```bash
python scripts\init_db.py
```

## AI - Ollama

**Kurulum**:

1. https://ollama.ai adresinden indir
2. Kur ve çalıştır
3. Model çek: `ollama pull medgemma:4b`
4. Kontrol: `ollama list`

**Config**:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma:4b
```

## AI Model Routing

`config/ai_models.yaml`:

```yaml
routing:
  simple: [ollama]
  moderate: [ollama]
  complex: [claude-sonnet-4.5, gpt-5, ollama]

models:
  ollama:
    base_url: ${OLLAMA_BASE_URL}
    model: ${OLLAMA_MODEL}
    timeout: 30
```

## Sorun Giderme

**Veritabanı**:

- SQL Server çalışıyor mu? → Servisleri kontrol et
- ODBC Driver kurulu mu? → `odbcinst -q -d`
- Bağlantı string doğru mu? → Sunucu adı ve instance kontrol et

**Ollama**:

- Çalışıyor mu? → `curl http://localhost:11434/api/version`
- Model indirilmiş mi? → `ollama list`
- Servis başlamış mı? → `ollama serve`

**API Keys**:

- Doğru kopyalandı mı? → Boşluk yok, tam key
- Aktif mi? → Provider dashboard'u kontrol et
- Log'lara bak → `logs/error.log`
