# Troubleshooting Guide

This document provides comprehensive solutions for common issues encountered in the Clinical AI Assistant project.

## 📋 Table of Contents

- [Database Connection Issues](#database-connection-issues)
- [Frontend Issues](#frontend-issues)
- [Backend API Issues](#backend-api-issues)
- [AI Provider Issues](#ai-provider-issues)
- [Build and Deployment Issues](#build-and-deployment-issues)

---

## Database Connection Issues

### Issue: "Data source name not found"

**Full Error Message**:
```
(pyodbc.InterfaceError) ('IM002', '[IM002] [Microsoft][ODBC Driver Manager]
Data source name not found and no default driver specified (0) (SQLDriverConnect)')
```

**Symptoms**:
- Backend starts successfully but crashes when accessing database
- Patient search returns 500 Internal Server Error
- Error appears in backend terminal/logs

**Root Cause**:
The `.env` file specifies an ODBC driver that is not installed on your system.

**Solution**:

1. **Check installed ODBC drivers**:
   ```bash
   python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"
   ```

   Expected output (example):
   ```
   ['SQL Server', 'SQL Server Native Client 11.0', 'ODBC Driver 11 for SQL Server']
   ```

2. **Update `.env` file** to match an installed driver:

   If you see `ODBC Driver 11 for SQL Server`:
   ```env
   DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes
   ```

   If you see `ODBC Driver 17 for SQL Server`:
   ```env
   DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
   ```

   If you see `ODBC Driver 18 for SQL Server`:
   ```env
   DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
   ```

3. **Restart backend server** (uvicorn will auto-reload):
   - If using `--reload` flag, save `.env` and it will restart automatically
   - Otherwise, stop (Ctrl+C) and restart: `uvicorn src.api.fastapi_app:app --reload --port 8080`

4. **Test connection**:
   ```bash
   python test_db_connection.py
   ```

**Prevention**:
Always run the connection test script before modifying database configuration.

---

### Issue: SQL Server Not Accessible

**Error Messages**:
- `Cannot connect to SQL Server`
- `Login timeout expired`
- `Named Pipes Provider: Could not open a connection to SQL Server`

**Common Causes & Solutions**:

1. **SQL Server Service Not Running**

   **Check**:
   ```bash
   # Open Services Manager
   services.msc
   ```
   Look for `SQL Server (HIZIR)` or `SQL Server (MSSQLSERVER)`

   **Fix**: Right-click → Start

2. **SQL Server Not Configured for TCP/IP**

   **Check**: SQL Server Configuration Manager → SQL Server Network Configuration → Protocols

   **Fix**: Enable TCP/IP protocol and restart SQL Server

3. **Firewall Blocking Connection**

   **Fix**: Add exception for SQL Server port (default 1433)
   ```bash
   # PowerShell (as Administrator)
   New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
   ```

4. **Instance Name Incorrect**

   **Check**: Verify SQL Server instance name in SQL Server Configuration Manager

   **Fix**: Update `.env` DB_SERVER to match actual instance (e.g., `localhost\HIZIR`)

---

### Issue: Authentication Failed

**Error**: `Login failed for user`

**Solutions**:

1. **Windows Authentication** (Recommended):
   ```env
   DATABASE_URL=mssql+pyodbc://localhost\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes
   ```

2. **SQL Server Authentication**:
   ```env
   DATABASE_URL=mssql+pyodbc://username:password@localhost\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server
   ```

   **Security Note**: Never commit `.env` file with credentials to git!

---

## Frontend Issues

### Issue: Blank White Screen After Search

**Symptoms**:
- Patient search input works
- Backend logs show 200 OK responses
- Frontend page goes completely blank when results should display
- Browser console shows no errors (page freezes)

**Root Cause**:
Frontend component tries to access undefined fields from API response. This happens when:
- Backend API response format changes
- Frontend component not updated to match new format
- TypeScript interfaces don't match actual API

**Solution**:

1. **Check API Response Format**:

   Open browser DevTools → Network tab → Find the `/api/v1/patients/search` request → Preview the response

   Expected format (current):
   ```json
   {
     "patients": [
       {
         "tckn": "12345678901",
         "name": "Ahmet Yılmaz",
         "age": 45,
         "gender": "E"
       }
     ]
   }
   ```

2. **Check Frontend Component**:

   File: `frontend/src/pages/PatientSearch.tsx`

   Ensure fields match API response:
   ```typescript
   // ✅ Correct
   <h3>{patient.name}</h3>
   <span>{patient.tckn}</span>
   <span>{patient.age} years</span>

   // ❌ Incorrect (old format)
   <h3>{patient.ADI} {patient.SOYAD}</h3>
   <span>{patient.TCKN}</span>
   ```

3. **Update TypeScript Interface**:

   File: `frontend/src/services/api.ts`
   ```typescript
   export interface PatientSearchResult {
     tckn: string;
     name: string;
     age: number | null;
     gender: "E" | "K" | null;
     last_visit: null;
   }
   ```

4. **Test Fix**:
   - Save files (Vite will auto-reload)
   - Refresh browser
   - Try search again

**Prevention**:
- When changing API response format, update frontend immediately
- Use TypeScript interfaces to catch mismatches
- Test API contract changes end-to-end

---

### Issue: Frontend Not Loading at All

**Symptoms**:
- Browser shows "This site can't be reached"
- Terminal shows no frontend server running

**Solutions**:

1. **Start Frontend Server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Check Port Conflicts**:

   If Vite says port 5173 is in use, it will automatically use 5174
   ```
   Local:   http://localhost:5174/
   ```
   This is normal - use the port shown in terminal

3. **Kill Previous Processes**:
   ```bash
   # Windows
   netstat -ano | findstr "5173"
   taskkill /PID <pid> /F
   ```

4. **Reinstall Dependencies**:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   npm run dev
   ```

---

### Issue: API Calls Failing with 404

**Symptoms**:
- Frontend loads but API calls return 404
- Browser console shows: `GET http://localhost:5173/api/v1/patients/search 404`

**Root Cause**:
Backend is not running or running on wrong port

**Solutions**:

1. **Check Backend Status**:
   ```bash
   # Should see:
   # INFO:     Uvicorn running on http://127.0.0.1:8080
   ```

2. **Start Backend** (if not running):
   ```bash
   # From project root
   ./venv/Scripts/python.exe -m uvicorn src.api.fastapi_app:app --host 127.0.0.1 --port 8080 --reload
   ```

3. **Verify Port Configuration**:
   - `.env`: `API_PORT=8080`
   - `frontend/vite.config.ts`: proxy target should be `http://localhost:8080`

---

## Backend API Issues

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### Issue: Database Query Errors

**Error**: `SQL type -150 is not supported`

**Root Cause**:
Querying all columns includes unsupported ODBC types

**Solution**:
Select only specific columns you need:

```python
# ❌ Bad - queries all columns
patients = session.query(Patient).all()

# ✅ Good - select specific columns
patients = session.query(
    Patient.HASTA_KIMLIK_NO,
    Patient.AD,
    Patient.SOYAD,
    Patient.DOGUM_TARIHI,
    Patient.CINSIYET
).all()
```

See: `src/api/routes/patient.py` for working example

---

### Issue: Slow API Responses

**Symptoms**:
- API responses taking >2 seconds
- High database CPU usage

**Solutions**:

1. **Add Database Indexes** (if you have write access):
   ```sql
   CREATE INDEX idx_patient_name ON HASTA_BILGI(AD, SOYAD);
   CREATE INDEX idx_patient_tckn ON HASTA_BILGI(HASTA_KIMLIK_NO);
   ```

2. **Limit Query Results**:
   ```python
   # Always include .limit()
   query.limit(20).all()
   ```

3. **Use Query Optimization**:
   - Only select needed columns
   - Avoid N+1 queries
   - Use SQLAlchemy's `joinedload()` for relationships

---

## AI Provider Issues

### Issue: Ollama Not Responding

**Error**: `Connection refused to localhost:11434`

**Solutions**:

1. **Check Ollama Service**:
   ```bash
   # Check if running
   curl http://localhost:11434/api/version
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Verify Model Downloaded**:
   ```bash
   ollama list
   # Should see: hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL
   ```

4. **Pull Model** (if not downloaded):
   ```bash
   ollama pull hf.co/unsloth/medgemma-4b-it-GGUF:Q8_K_XL
   ```

---

### Issue: Cloud AI API Errors

**Error**: `Invalid API key` or `Rate limit exceeded`

**Solutions**:

1. **Verify API Keys** in `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-...
   OPENAI_API_KEY=sk-proj-...
   GOOGLE_API_KEY=AIza...
   ```

2. **Check API Key Validity**:
   - Anthropic: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys
   - Google: https://makersuite.google.com/app/apikey

3. **Switch to Ollama** (free, local):
   ```python
   # In your request
   { "model": "ollama" }  # Uses local Ollama
   ```

---

## Build and Deployment Issues

### Issue: Frontend Build Fails

**Error**: `Error: Build failed with X errors`

**Solutions**:

1. **Check TypeScript Errors**:
   ```bash
   cd frontend
   npm run build
   # Fix any type errors shown
   ```

2. **Clean and Rebuild**:
   ```bash
   cd frontend
   rm -rf node_modules dist
   npm install
   npm run build
   ```

3. **Check Node Version**:
   ```bash
   node --version  # Should be 18+
   ```

---

### Issue: Backend Won't Start

**Error**: `Address already in use`

**Solution**:

1. **Find Process Using Port**:
   ```bash
   # Windows
   netstat -ano | findstr "8080"
   ```

2. **Kill Process**:
   ```bash
   taskkill /PID <pid> /F
   ```

3. **Use Different Port**:
   ```bash
   uvicorn src.api.fastapi_app:app --port 8081
   ```

---

## Quick Diagnostic Commands

```bash
# System Check
python --version          # Should be 3.10.11+
node --version           # Should be 18+

# Database Check
python -c "import pyodbc; print(pyodbc.drivers())"
python test_db_connection.py

# Backend Check
curl http://localhost:8080/health

# Frontend Check
curl http://localhost:5173

# Ollama Check
curl http://localhost:11434/api/version

# Port Check
netstat -ano | findstr "8080"   # Backend
netstat -ano | findstr "5173"   # Frontend
netstat -ano | findstr "11434"  # Ollama
```

---

## Getting More Help

1. **Check Logs**:
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser DevTools Console
   - Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging

2. **API Documentation**:
   - Swagger UI: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

3. **Test Individual Components**:
   - Test database: `python test_db_connection.py`
   - Test API: Use `/docs` interactive API
   - Test frontend: Check Network tab in DevTools

4. **Read Project Documentation**:
   - `README.md` - Setup and overview
   - `CLAUDE.md` - AI agent guidelines and patterns
   - `IMPLEMENTATION_SUMMARY.md` - Recent changes

---

**Last Updated**: 2025-11-06
**Maintained By**: Keep this updated when new issues are discovered and solved
