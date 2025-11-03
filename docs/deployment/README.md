# Deployment Guide

## 🚀 Overview

This guide covers deployment options for the Clinical AI Assistant system, including local development, production deployment, and containerized setups.

## 📋 Prerequisites

### System Requirements

**Minimum Requirements:**
- **Operating System**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+
- **Python**: 3.11+ (with pip)
- **Database**: SQL Server 2014/2022
- **Memory**: 4GB RAM minimum
- **Storage**: 10GB free space

**Optional Requirements:**
- **Docker**: 20.10+ (for containerized deployment)
- **Node.js**: 18+ (for web frontend)
- **PySide6**: For desktop GUI application
- **Ollama**: For local AI model hosting

### Software Dependencies

**Python Packages:**
```bash
# Core dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
python-multipart>=0.0.6

# Database drivers
pyodbc>=5.0.1
pymssql>=2.2.9

# AI Integration
anthropic>=0.8.1
openai>=1.6.2
google-generativeai>=0.3.2

# CLI Tools
typer>=0.9.0
rich>=13.7.0
tenacity>=8.2.3

# Web Frontend (if using)
# See frontend/package.json for dependencies
```

## 🏠 Development Deployment

### Local Development Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd PatientSystem
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (if using web interface)
cd frontend
npm install
cd ..
```

#### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Database connection
# For Windows with named instance and Windows Authentication
DATABASE_URL=mssql+pyodbc://localhost\\INSTANCE_NAME/database?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# For SQL Server Authentication
# DATABASE_URL=mssql+pyodbc://server\\instance/database?driver=ODBC+Driver+17+for+SQL+Server&UID=username&PWD=password

DATABASE_POOL_SIZE=20

# AI API keys (optional, Ollama works locally)
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Application settings
LOG_LEVEL=INFO
DEBUG=false
```

#### 5. Initialize Database

```bash
# Run database initialization (first time only)
python -m src.database.migrations.init_database
```

#### 6. Start Services

```bash
# Terminal 1: Start API server
python -m src.api.fastapi_app

# Terminal 2: Start web frontend (if using)
cd frontend
npm run dev

# Terminal 3: Start desktop GUI (optional)
python -m src.gui.main_window

# Terminal 4: Run CLI commands (optional)
python -m src.cli.app --help
```

### Development URLs

- **API Server**: http://localhost:8000
- **Web Interface**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Production Deployment

### Option 1: Direct Server Deployment

#### System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-pip

# Install SQL Server (Ubuntu)
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/prod.list)"
sudo apt update
sudo ACCEPT_EULA=Y apt install -y mssql-server
```

#### Application Deployment

```bash
# Create application user
sudo useradd -m -d /opt/clinical-ai clinicalai
sudo usermod -aG clinicalai

# Deploy application files
sudo cp -r /path/to/PatientSystem /opt/clinical-ai/
sudo chown -R clinicalai:clinicalai /opt/clinical-ai/
cd /opt/clinicalai

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure production environment
cp .env.example .env
# Edit .env with production settings

# Create systemd service
sudo tee /etc/systemd/systems/clinical-ai.service > /dev/null <<EOF
[Unit]
Description=Clinical AI Assistant API
After=network.target

[Service]
Type=simple
User=clinicalai
WorkingDirectory=/opt/clinical-ai
Environment=PATH=/opt/clinicalai/venv/bin
ExecStart=/opt/clinicalai/venv/bin/python -m src.api.fastapi_app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable clinical-ai.service
sudo systemctl start clinical-health.service
```

#### Database Configuration

```bash
# Create database user if needed
sqlcmd -S localhost -E
CREATE LOGIN clinicalai_user WITH PASSWORD='secure_password';
GO;

# Configure application database connection
# Edit .env with production database settings
DATABASE_URL=mssql+pyodbc://localhost/ClinicalAI;UID=clinicalai_user;PWD=secure_password
```

#### Reverse Proxy (Optional)

**Nginx Configuration:**
```bash
sudo apt install nginx

sudo tee /etc/nginx/sites-available/clinical-ai > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
        root /path/to/frontend/dist;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/clinical-ai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### Docker Compose Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: clinical-ai-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_KEY}
    depends_on:
      - db
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: clinical-ai-frontend
    ports:
      - "5173:5173"
    depends_on:
      - api
    environment:
      - VITE_API_URL=http://api:8000

  db:
    image: mcr.microsoft.com/mssql/server:2019-latest
    container_name: clinical-ai-db
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=51028894
      - MSSQL_PID=/var/opt/mssql/data/sqlservr.pid
    ports:
      - "1433:1433"
    volumes:
      - sqlserver_data:/var/opt/mssql/data
      - sqlserver_logs:/var/opt/mssql/logs
    restart: always

  ollama:
    image: ollama/ollama:latest
    container_name: clinical-ai-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_ORIGINS= "*"
    restart: always
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc \
    curl

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./

# Create non-root user
RUN useradd -m -u clinicalai

USER clinicalai

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "src.api.fastapi_app"]
```

**Docker Commands:**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down

# Update containers
docker-compose build
docker-compose up -d --force-recreate
```

### Option 3: Cloud Deployment

#### AWS EC2 Deployment

**Instance Setup:**
```bash
# Launch EC2 instance
aws ec2 run \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.medium \
  --key-name clinical-ai-key \
  --security-group-ids sg-1234567890 \
  --user-data file://./cloud-init.sh \
  --tag Name=Clinical-AI-Assistant
```

**cloud-init.sh:**
```bash
#!/bin/bash
# Update system
apt-get update -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh | sh
sudo usermod -aG docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Pull and start application
git clone https://github.com/your-org/PatientSystem.git /opt/clinical-ai
cd /opt/clinical-ai
docker-compose up -d
```

#### Azure App Service

**app-service.json:**
```json
{
  "version": "2.0",
  "provisioningState": {
    "name": "clinical-ai-assistant",
    "runtime": "python:3.11",
    "startupCommand": "pip install -r requirements.txt && python -m src.api.fastapi_app",
    "alwaysOn": true
  },
  "siteConfig": {
    "alwaysOn": true,
    "appCommandLine": "python -m src.api.fastai_app",
    "appSettings": {
      "WEBSITE_SITE_NAME": "clinical-ai-assistant.azurewebsites.net"
    }
  },
  "connectionStrings": {
    "DATABASE_URL": "mssql+pyodbc://localhost\\HIZIR/TestDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
  },
  "properties": {
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${OPENAI_API_KEY}"
  }
}
```

**Deployment:**
```bash
# Configure Azure CLI
az login
az webapp up --plan ./app-service.json

# Deploy application
az webapp up --name clinical-ai-assistant
```

### Option 4: Kubernetes Deployment

**kubernetes Manifests:**

**api-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clinical-ai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: clinical-ai-api
  template:
    metadata:
      labels:
        app: clinical-ai-api
    spec:
      containers:
      - name: clinical-ai-api
        image: clinical-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "mssql+pyodbc://localhost\\HIZIR/TestDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-api-key
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port:8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: clinical-ai-api-service
spec:
  selector:
    matchLabels:
      app: clinical-api-api
  ports:
  - port: 8000
    targetPort: 8000
    type: LoadBalancer
---
apiVersion: v1
kind: Ingress
metadata:
  name: clinical-ai-ingress
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        backend:
          service: clinical-ai-api-service
          port: 8000
```

**Secrets Configuration:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: anthropic-api-key
type: Opaque
data:
  ANTHROPIC_API_KEY: your-claude-key
---
apiVersion: v1
kind: Secret
metadata:
  name: openai-api-key
type: Opaque
data:
  OPENAI_API_KEY: your-openai-key
---
```

## 🔧 Configuration Management

### Environment Variables

**Development (.env.development):**
```bash
# Database
DATABASE_URL=mssql+pyodbc://localhost/ClinicalAI_DEV
DATABASE_POOL_SIZE=10

# Logging
LOG_LEVEL=DEBUG
DEBUG=true

# AI Services
ANTHROPIC_API_KEY=dev_claude_key
OPENAI_API_KEY=dev_openai_key
GOOGLE_API_KEY=dev_google_key
OLLAMA_BASE_URL=http://localhost:11434

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

**Production (.env.production):**
```bash
# Database
DATABASE_URL=mssql+pyodbc://prod-server/ClinicalAI_PROD
DATABASE_POOL_SIZE=50

# Logging
LOG_LEVEL=INFO
DEBUG=false

# AI Services
ANTHROPIC_API_KEY=prod_claude_key
OPENAI_API_KEY=prod_openai_key
GOOGLE_API_KEY=prod_google_key

# Security
CORS_ORIGINS=["https://your-domain.com"]

# Performance
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4
```

### Configuration File (config/settings.py)

```python
# Database Configuration
DATABASE_URL = Field(
    default="mssql+pyodbc://localhost/ClinicalAI",
    description="Database connection string"
)
DATABASE_POOL_SIZE = Field(
    default=20,
    description="Database connection pool size"
)

# AI Configuration
CLAUDE_MODEL = Field(
    default="claude-3-5-sonnet-20241022",
    description="Claude model to use"
)
OPENAI_MODEL = Field(
    default="gpt-4o",
    description="OpenAI model to use"
)
GEMINI_MODEL = Field(
    default="gemini-pro",
    description="Gemini model to use"
)
OLLAMA_MODEL = Field(
    default="gemma:7b",
    description="Ollama model to use"
)

# Routing Strategy
AI_ROUTING_STRATEGY = Field(
    default="smart",
    description="AI routing strategy (smart/cost_optimized/quality_first)"
)
AI_ENABLE_FALLBACK = Field(
    default=True,
    description="Enable AI provider fallback"
)

# Performance Settings
AI_TIMEOUT = Field(
    default=30,
    description="AI request timeout in seconds"
)
AI_TEMPERATURE = Field(
    default=0.7,
    description="AI sampling temperature"
)
AI_MAX_TOKENS = Field(
    default=2000,
    description="Maximum tokens for AI responses"
)
```

## 🔍 Monitoring and Logging

### Application Logging

**Logging Configuration:**
```python
import logging
from loguru import logger

# Configure logging
logger.add(
    "src/",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

logger.info("Clinical AI Assistant started")
```

### Health Monitoring

**Health Check Implementation:**
```python
from fastapi import FastAPI
from prometheus_client import Counter, Histogram
import time

# Metrics
REQUEST_COUNT = Counter("api_requests_total", "API requests total", ["method", "endpoint"])
REQUEST_DURATION = Histogram("api_request_duration_seconds", "API request duration", buckets=[0.1, 0.5, 1, 2, 5, 10])

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    REQUEST_COUNT.labels["method"] = request.method
    REQUEST_COUNT.labels["endpoint"] = request.url.path
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    return response
```

### Performance Monitoring

**Performance Metrics:**
- Request response times
- Database query performance
- AI model response times
- Memory usage
- CPU utilization
- Error rates

**Monitoring Stack Options:**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Datadog**: APM and error tracking

## 🔒 Security Considerations

### Network Security

**SSL/TLS Configuration:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/clinical-ai.crt;
    ssl_certificate_key /etc/ssl/certs/clinical-ai.key;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;
    ssl_session_cache_timeout 1d;
}
```

**Firewall Configuration:**
```bash
# Open necessary ports
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp     # API
sudo ufw allow 5173/tcp     # Web development
```

### Application Security

**Input Validation:**
- All API endpoints use Pydantic models
- Request/response validation
- SQL injection prevention
- XSS protection

**Data Protection:**
- No sensitive data in logs
- Encrypted data transmission
- Regular security updates
- Audit logging for access attempts

## 📦 Backup and Recovery

### Database Backup Strategy

**SQL Server Backup Script:**
```sql
-- Create backup job
USE msdb;
GO

-- Backup database
BACKUP DATABASE ClinicalAI
TO DISK = 'D:\Backups\ClinicalAI_backup.bak'
WITH FORMAT INIT,
    NAME = 'ClinicalAI_Backup',
    DESCRIPTION = 'Daily backup of Clinical AI database',
    STATS = STATS,
    COMPRESSION = ON
    INIT,
    SKIP,
    NOFORMAT;
GO

-- Backup transaction logs
BACKUP LOG ClinicalAI
FROM DISK = 'D:\Backups\ClinicalAI_log_backup.bak'
TO DISK = 'D:\Backups\ClinicalAI_log_backup.bak'
WITH NOFORMAT, INIT;
GO
```

**Automated Backup:**
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)
DATABASE_NAME="ClinicalAI"

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Database backup
sqlcmd -S localhost -S "
BACKUP DATABASE $DATABASE_NAME
TO DISK = '$BACKUP_DIR/$DATE/database_backup.bak'
WITH COMPRESSION, INIT,
STATS"
GO

# Application files backup
tar -czf "$BACKUP_DIR/$DATE/application_backup.tar.gz" \
    /opt/clinical-ai/src \
    /opt/clinical_ai/requirements.txt \
    /opt/clinicalai/.env \
    /opt/clinicalai/docs

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore from backup
sqlcmd -S localhost -S "
RESTORE DATABASE ClinicalAI
FROM DISK = 'D:\Backups\20241102\database_backup.bak'
WITH REPLACE, RECOVERY,
STATS,
    STOPATATMARK = 0;
GO
```

## 📊 Scaling Considerations

### Horizontal Scaling

**Load Balancer Configuration:**
```nginx
upstream api_servers {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Scaling

**Connection Pooling:**
```python
# In settings.py
DATABASE_POOL_SIZE = 50  # Increased for production
DATABASE_MAX_OVERFLOW = 20  # Additional connections under load
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

### Caching Strategy

**Redis Integration:**
```python
# Cache frequently accessed data
REDIS_URL = "redis://localhost:6379/0"

# Cache patient searches
@cache(expire=300)  # 5 minutes
def get_patient_summary(tckn: str):
    cache_key = f"patient_summary:{tckn}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # Generate patient summary
    summary = generate_patient_summary(tckn)

    # Cache for 5 minutes
    redis_client.setex(cache_key, json.dumps(summary), ex=300)
    return summary
```

## 🚀 Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check database status
sqlcmd -S localhost -Q "SELECT @@VERSION"

# Test connectivity from application
python -c "from src.database.connection import get_engine; print(get_engine().execute('SELECT 1').scalar())"

# Check connection pool
python -c "
from src.database.connection import get_session
with get_session() as session:
    result = session.execute('SELECT COUNT(*) FROM HASTA').scalar()
    print(f'Total patients: {result}')
```

**AI Service Issues:**
```bash
# Test AI provider connectivity
python -c "
from src.ai import create_ai_router
router = create_ai_router()
results = asyncio.run(router.health_check_all())
for provider, status in results.items():
    print(f'{provider}: {'✓' if status else '✗'}')
```

**Performance Issues:**
```bash
# Monitor system resources
htop
df -h

# Check memory usage
free -h

# Monitor disk usage
df -h

# Check running processes
ps aux | grep python
```

### Log Analysis

**Common Log Patterns:**
```bash
# Error patterns
grep "ERROR" logs/app.log
grep "CRITICAL" logs/app.log
grep "timeout" logs/app.log

# Performance patterns
grep "slow" logs/app.log
grep "timeout" logs/app.log

# Database query patterns
grep "query took" logs/app.log
grep "connection" logs/app.log
```

---

**Last Updated:** November 2024
**Version:** 0.1.0
**Deployment Status:** Production Ready ✅

For additional help, see the [installation guide](installation.md) or [user guides](../user-guides/README.md).