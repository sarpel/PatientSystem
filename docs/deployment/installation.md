# Installation Guide

## 🏥 System Requirements

### Minimum Requirements

**Hardware:**

- **Processor**: Intel i5 or equivalent
- **Memory**: 4GB RAM minimum
- **Storage**: 10GB free disk space
- **Network**: Internet connection for AI services (optional)

**Software:**

- **Operating System**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+
- **Python**: 3.11+ (includes pip)
- **SQL Server**: 2014 or 2022 (for patient data)

**Optional (for full functionality):**

- **Node.js 18+** (for web interface)
- **PySide6** (for desktop GUI)
- **Docker** (for containerized deployment)
- **Ollama** (for local AI model hosting)

## 🚀 Quick Start

### Option 1: Using Installation Script (Recommended)

1. **Download Installation Script:**

   ```bash
   curl -fsSL https://raw.githubusercontent.com/your-org/PatientSystem/main/install.sh | bash
   ```

2. **Run Interactive Installation:**

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Follow On-Screen Instructions**

### Option 2: Manual Installation

#### Step 1: Clone Repository

```bash
git clone <repository-url>
cd PatientSystem
```

#### Step 2: Create Virtual Environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

#### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Example .env Configuration:**

```bash
# Database Configuration
# Windows with named instance and Windows Authentication (RECOMMENDED)
DATABASE_URL=mssql+pyodbc://localhost\\INSTANCE_NAME/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# Windows with default instance
# DATABASE_URL=mssql+pyodbc://localhost/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# SQL Server Authentication
# DATABASE_URL=mssql+pyodbc://localhost\\INSTANCE_NAME/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&UID=username&PWD=password

DATABASE_POOL_SIZE=20

# AI Services (Optional)
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
```

#### Step 6: Initialize Database

```bash
# First time only
python -m src.database.migrations.init_database
```

#### Step 7: Start Services

```bash
# Terminal 1: API Server
python -m src.api.fastapi_app

# Terminal 2: Web Frontend
cd frontend
npm run dev

# Terminal 3: Desktop GUI (optional)
python -m src.gui.main_window

# Terminal 4: CLI Commands
python -m src.cli.app --help
```

## 🔧 Detailed Installation

### Python Installation

#### Windows

**Option 1: Microsoft Store**

1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click "Install"

**Option 2: Python.org**

1. Visit https://www.python.org/downloads/
2. Download Python 3.11 Windows installer
3. Run installer
4. Add Python to PATH

**Option 3: Chocolatey**

```bash
# Install Chocolatey
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process"
Set-ExecutionPolicy All
choco install python
```

#### macOS

**Option 1: Homebrew**

```bash
brew install python@3.11
```

**Option 2: Install from Source**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

**Option 3: Pyenv**

```bash
# Install pyenv
brew install pyenv
pyenv install 3.11.2
```

#### Linux (Ubuntu/Debian)

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install python3.11 python3.11-dev python3.11-venv
```

**CentOS/RHEL:**

```bash
sudo yum install python3 python3-pip
sudo yum install python3.11
```

**Arch Linux:**

```bash
sudo pacman -S python
# Choose Python 3.11 when prompted
```

### SQL Server Installation

#### Windows

**Option 1: SQL Server Express**

1. Download from Microsoft website
2. Run installer with default settings
3. Use Windows Authentication

**Option 2: SQL Server Developer Edition**

1. Download from Microsoft website
2. Run installer with custom settings
3. Configure during installation

**Option 3: SQL Server Evaluation**

1. Download evaluation version (180 days)
2. Use for development and testing

#### Linux (Ubuntu/Debian)

```bash
# Add Microsoft repository
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql.list

# Update package list
sudo apt-get update

# Install SQL Server
sudo ACCEPT_EULA=Y apt-get install -y mssql-server
```

#### Linux (CentOS/RHEL)

```bash
# Install Microsoft repository
sudo curl -fsSL https://packages.microsoft.com/config/rhel/9/mssql/server/ | sudo tee /etc/yum.repos.d/mssql.repo

# Install SQL Server
sudo yum install -y mssql-server
```

#### macOS

**Option 1: Docker**

```bash
docker run -e "ACCEPT_EULA=Y" \
  -p 1433:1433 \
  -e "MSSQL_PID=/var/opt/mssql/data/sqlservr.pid" \
  -v /opt/mssql \
  mcr.microsoft.com/mssql/server:2019-latest
```

**Option 2: Use Virtual Machine**

- Install SQL Server in Windows VM
- Configure port forwarding
- Connect from host machine

### Node.js Installation

#### Windows

**Option 1: Official Installer**

1. Download Node.js from https://nodejs.org/
2. Run installer with default settings
3. Verify installation with `node --version`

**Option 2: Chocolatey**

```bash
choco install nodejs
```

**Option 3: fnm (Recommended)**

```bash
# Install fnm
curl -fsSL https://fnm.vercel.app/install | bash
fnm install 18
```

#### macOS

```bash
brew install node
```

#### Linux (Ubuntu/Debian)\*\*

```bash
sudo apt update
sudo apt install -y nodejs npm
```

#### Linux (CentOS/RHEL)\*\*

```bash
curl -fsSL https://rpm.nodesource.com/setup_nvm.sh | bash
nvm install 18
```

### PySide6 Installation

#### Windows

**Option 1: pip**

```bash
pip install PySide6
```

**Option 2: conda-forge**

```bash
conda install pyside6
```

#### macOS

```bash
brew install pyside6
```

#### Linux (Ubuntu/Debian)\*\*

```bash
sudo apt update
sudo apt install -y python3-pyside6
```

## 🔧 Configuration

### Environment Variables Setup

#### Creating .env File

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

#### Required Variables

```bash
# Database (Required)
# Windows Authentication with named instance (RECOMMENDED for development)
DATABASE_URL=mssql+pyodbc://localhost\\INSTANCE_NAME/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# Or with SQL Authentication
# DATABASE_URL=mssql+pyodbc://localhost\\INSTANCE_NAME/ClinicalAI?driver=ODBC+Driver+17+for+SQL+Server&UID=username&PWD=password

# AI Services (Optional but Recommended)
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Ollama (Local AI)
OLLAMA_BASE_URL=http://localhost:11434
```

### Database Connection Testing

```bash
# Test database connection
python -c "
from src.database.connection import get_engine
try:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute('SELECT 1').scalar()
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### AI Service Testing

```bash
# Test AI services
python -c "
from src.ai import create_ai_router

router = create_ai_router()
results = asyncio.run(router.health_check_all())

for provider, status in results.items():
    status_icon = '✓' if status else '✗'
    print(f'{status_icon} {provider}: {status}')
```

## 🔍 Verification

### Installation Verification

#### Step 1: Check Python Installation

```bash
python --version
# Should show: Python 3.11.x
```

#### Step 2: Check Dependencies

```bash
pip list
pip show fastapi
pip show pydantic
```

#### Step 3: Test Database Connection

```bash
python -m "from src.database.connection import get_engine; print('Database connection OK')"
```

#### Step 4: Test API Server

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

#### Step 5: Test CLI

```bash
python -m src.cli.app --help
# Should show available commands
```

#### Step 6: Test Web Interface

```bash
cd frontend
npm run dev
# Should start development server on http://localhost:5173
```

## 🐛 Troubleshooting

### Common Issues

#### Python Installation Errors

**Issue:** `python: command not found`

```bash
# Solutions:
# 1. Check Python installation
python --version

# 2. Add Python to PATH (Windows)
set PATH=%PATH%;%USERPROFILE%\python

# 3. Restart terminal
# For macOS: source ~/.zshrc
# For Linux: source ~/.bashrc
```

**Issue:** Module not found errors

```bash
# Solutions:
# 1. Verify virtual environment is active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Check Python version compatibility
python -c "import sys; print(sys.version)"
```

#### Database Connection Issues

**Issue:** Database connection failed

```bash
# Check SQL Server service status
# Windows: Services > SQL Server
# Linux: sudo systemctl status mssql

# Test connection string
python -c "
from urllib.parse import urlparse
parsed = urlparse(os.getenv('DATABASE_URL', ''))
print(f'Database type: {parsed.scheme}')
print(f'Server: {parsed.netloc}')
```

\*\*Issue: PyODBC driver errors

```bash
# Install ODBC drivers
# Windows: Install SQL Server Native Client
# Linux: sudo apt-get install python3-pyodbc

# Test ODBC configuration
python -c "
import pyodbc
try:
    conn = pyodbc.connect(your_connection_string)
    print('✅ PyODBC driver working')
except Exception as e:
    print(f'❌ PyODBC error: {e}')
```

#### Port Conflicts

**Issue:** Port 8000 already in use

```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process using port 8000
# Windows: taskkill /F /PID
# Linux: kill -9 PID

# Use different port
export PORT=8001
python -m src.api.fastapi_app
```

#### Frontend Build Issues

**Issue:** npm install fails

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

**Issue:** npm run dev fails

```bash
# Check Node.js version
node --version

# Clear cache and reinstall
npm cache clean
npm install

# Install latest versions
npm install
npm run build
```

#### Dependency Version Conflicts

**Issue:** Version conflicts between packages

```bash
# Check for conflicting packages
pip list --outdated

# Update all packages
pip install --upgrade

# Install specific version
pip install fastapi==0.104.0
```

### Performance Issues

#### Slow Database Queries

```bash
# Check database query performance
python -c "
from src.database.connection import get_session
import time

start_time = time.time()
with get_session() as session:
    result = session.execute('SELECT COUNT(*) FROM HASTA').scalar()
    end_time = time.time()
    print(f'Query time: {end_time - start_time:.3f}s')
```

#### Slow AI Responses

```bash
# Test AI model performance
python -c "
import time
start_time = time.time()
result = await router.complete(
    prompt="Simple test prompt",
    provider="ollama"  # Fast, local model
)
end_time = time.time()
    print(f'Ollama response time: {end_time - start_time:.1f}s')
```

### Memory Issues

#### High Memory Usage

```bash
# Check memory usage
free -h

# Check Python process memory
ps aux | grep python

# Profile memory usage
python -m memory_profiler
```

## 🔒 System Optimization

### Performance Tuning

#### Database Optimization

```sql
-- Optimize SQL Server
EXEC sp_configure 'show advanced options';
EXEC sp_configure 'max server memory' = 4096;
EXEC sp_configure 'max degree of parallelism' = 4;
```

#### Application Optimization

```bash
# Configure connection pooling
DATABASE_POOL_SIZE=50

# Enable query optimization
DATABASE_ECHO=true
```

#### AI Model Configuration

```python
# Use local models for simple tasks
AI_ROUTING_STRATEGY="cost_optimized"

# Optimize for speed
AI_TEMPERATURE=0.5  # More deterministic
AI_MAX_TOKENS=1000  # Shorter responses
```

## 📋 Post-Installation Checklist

### ✅ Verification Checklist

- [ ] Python 3.11+ installed and accessible
- [ ] All required packages installed successfully
- [ ] Database connection working
      -1] Environment variables configured correctly
- [1] API server starts without errors
- [1] Frontend builds and runs locally
- [1] CLI commands work properly
- [ ] Health checks pass
- [ ] Sample data queries work
- [ ] AI services connect (if configured)

### 🎯 Next Steps

1. **Load Test Data:**

   ```bash
   python -m src.database.migrations.load_sample_data
   ```

2. **Run Tests:**

   ```bash
   pytest tests/
   ```

3. **Explore Features:**

   ```bash
   python -m src.cli.app analyze patient 12345678901
   python -m src.gui.main_window
   ```

4. **Review Documentation:**
   - Read [user guides](../docs/user-guides/README.md)
   - Check [API reference](../docs/api/README.md)
   - Review [deployment guide](../deployment/README.md)

5. **Join Community:**
   - Report issues on GitHub
   - Contribute to documentation
   - Share feedback and improvements

---

**Installation Complete!** 🎉

Your Clinical AI Assistant system is now ready for use. The system includes:

- ✅ Multi-interface access (Desktop, Web, CLI)
- ✅ AI-powered clinical analysis
- ✅ Database integration
- ✅ Comprehensive documentation

**Access Points:**

- **API Server**: http://localhost:8000
- **Web Interface**: http://localhost:5173
- **Desktop GUI**: `python -m src.gui.main_window`
- **CLI Tools**: `python -m src.cli.app`

For additional help, see the [user guides](../user-guides/README.md) or [deployment guide](../deployment/README.md).

---

**Installation Script:** `./install.sh` (auto-generated)
**Version:** 0.1.0
**Platform:** Cross-platform (Windows/macOS/Linux)
**Documentation:** [Complete documentation available](docs/)

🤖 **Generated with Claude Code** 🤖
📝 **Co-Authored-By: Claude <noreply@anthropic.com>**
