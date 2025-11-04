# Desktop GUI User Guide

## 🖥️ Overview

The Clinical AI Assistant Desktop GUI is a native PySide6 application providing a professional interface for clinical decision support. This guide covers all features and workflows available in the desktop application.

## 🚀 Getting Started

### Launching the Application

1. **From Command Line:**

   ```bash
   python -m src.gui.main_window
   ```

2. **From Python:**
   ```python
   from src.gui.main_window import main
   main()
   ```

### First Launch

When you first launch the application, you'll see:

1. **Main Window** with patient search and clinical dashboard
2. **Status Bar** showing database and AI service connectivity
3. **Menu Bar** with File, Tools, and Help options

The application will automatically:

- ✅ Check database connectivity
- ✅ Verify AI service availability
- ✅ Load patient interface components
- ✅ Display system status indicators

## 🏠 Main Interface

### Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Clinical AI Assistant                                    [_][□][×] │
├─────────────────────────────────────────────────────────────────┤
│ File  Tools  Help                                             │
├─────────────────────────────────────────────────────────────────┤
│ Database: Connected ✓    AI: Ready ✓                           │
├─────────────────────────────────────────────────────────────────┤
│ [Patient Search Box...................] [Search]              │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌───────────────────────────────────────┐ │
│ │   Patient Info  │ │           Clinical Dashboard             │ │
│ │                 │ │ [Diagnosis] [Treatment] [Labs] [Meds] [History] │ │
│ │ Name: Test      │ │                                         │ │
│ │ Age: 45          │ │         [Selected Content Area]           │ │
│ │ Gender: Male    │ │                                         │ │
│ │ TCKN: 123456789 │ │                                         │ │
│ └─────────────────┘ └───────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Status: Ready | Clinical AI Assistant v0.1.0                     │
└─────────────────────────────────────────────────────────────────┘
```

### Status Indicators

**Database Status:**

- 🟢 **Connected** - Database connection healthy
- 🔴 **Disconnected** - Database connection failed
- 🟡 **Checking** - Verifying database connectivity

**AI Service Status:**

- 🟢 **Ready** - AI services available
- 🔴 **Unavailable** - No AI services accessible
- 🟡 **Checking** - Verifying AI service status

## 🔍 Patient Search

### Searching for Patients

1. **Enter Search Criteria:**
   - Type patient name (partial names work: "Ahm" for "Ahmet")
   - Enter TCKN (Turkish ID number)
   - Minimum 2 characters required

2. **Search Methods:**
   - **Press Enter** in search box
   - **Click Search button**
   - **Real-time search** (starts after 2 characters)

3. **Search Results:**
   - Table shows TCKN, Full Name, Birth Date, Gender, Last Visit
   - **Double-click** on any row to load patient
   - Results limited to 20 patients for performance

### Search Tips

- ✅ **Use partial names**: "Ali" finds "Ali", "Alper", "Halil"
- ✅ **TCKN search**: "1234" finds patients starting with 1234
- ✅ **Quick access**: Recently searched patients remembered
- ❌ **Too short**: Single character searches not allowed

## 📋 Clinical Dashboard

### Tab Navigation

The clinical dashboard provides 5 main tabs:

#### 1. 🧠 Diagnosis

AI-powered differential diagnosis generation

**Features:**

- **Chief Complaint Input**: Describe symptoms and duration
- **AI Model Selection**: Choose optimal AI provider
- **Progress Indicators**: Real-time AI analysis progress
- **Results Display**: Diagnosis table with probability scoring
- **Red Flags**: Urgent condition warnings
- **Recommended Tests**: Suggested laboratory studies

**Workflow:**

1. Enter chief complaint in text area
2. Select AI model (Auto recommended)
3. Click "Generate Diagnosis"
4. Review differential diagnosis with probabilities
5. Check red flags and recommended tests

#### 2. 💊 Treatment

Evidence-based treatment recommendations

**Features:**

- **Diagnosis Input**: Confirmed diagnosis for treatment planning
- **Medication Recommendations**: Drug, dosage, and duration
- **Clinical Guidelines**: Evidence-based protocols
- **Follow-up Plan**: Ongoing care recommendations
- **AI Provider Selection**: Choose model for treatment suggestions

**Workflow:**

1. Enter confirmed diagnosis from diagnosis panel
2. Select AI model preference
3. Click "Generate Treatment Plan"
4. Review medication recommendations
5. Check clinical guidelines and follow-up plan

#### 3. 🧪 Lab Results

Laboratory test analysis and trending

**Features:**

- **Test Selection**: Choose from common laboratory tests
- **Time Range Filtering**: 1 month to all available data
- **Results Table**: All values with reference ranges
- **Abnormal Value Highlighting**: Color-coded normal/abnormal indicators
- **Export Functionality**: Save charts as images
- **Trend Visualization**: Interactive plots (placeholder)

**Workflow:**

1. Select test type from dropdown
2. Choose time range for analysis
3. View results in table format
4. Check abnormal values (highlighted in red)
5. Export charts if needed

#### 4. 💊 Medications

Patient medication history and management

**Features:**

- **Current Medications**: Active prescriptions
- **Medication History**: Past prescriptions
- **Dosage Information**: Strength and frequency
- **Duration Tracking**: Start and end dates
- **Prescriber Information**: Healthcare provider details

_Note: This tab shows patient's medication history from the database_

#### 5. 📅 History

Patient visit and encounter history

**Features:**

- **Visit Timeline**: Chronological encounter list
- **Encounter Types**: Visit classifications
- **Date Filtering**: Range-based history viewing
- **Encounter Details**: Chief complaints and diagnoses
- **Provider Information**: Healthcare professional details

_Note: This tab shows patient's complete visit history_

## ⚙️ Tools and Configuration

### Database Inspector

**Access:** Tools → Database Inspector

**Features:**

- **Schema Explorer**: Browse all database tables
- **Table Categories**: Filter by table type (Patient, Visit, Diagnosis, etc.)
- **Column Information**: Field names, types, and nullability
- **Record Counts**: Table row statistics
- **SQL Query Preview**: See underlying queries

**Categories:**

- **Patient Tables**: HASTA, GP_BC
- **Visit Tables**: MUAYENE, KABUL
- **Diagnosis Tables**: TANI, ICD
- **Prescription Tables**: RECETE, ILAC
- **Lab Tables**: TETKIK, LAB
- **Reference Tables**: LST\_\* (lookup tables)

### AI Configuration

**Access:** Tools → AI Configuration

**Features:**

- **Model Selection**: Choose AI models for each provider
- **Health Checks**: Test AI service connectivity
- **Routing Strategy**: Configure smart routing behavior
- **Performance Settings**: Timeouts and temperature
- **Provider Status**: Real-time availability monitoring

**Model Options:**

- **Claude**: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Gemini**: gemini-pro, gemini-1.5-pro, gemini-1.5-flash
- **Ollama**: gemma:7b, llama2:7b, mistral:7b

**Health Check Process:**

1. Click "Check Provider Health"
2. Monitor progress bars
3. Review status results (✓ Available or ✗ Unavailable)
4. Update settings if needed

## 🚨 Alerts and Notifications

### Drug Interaction Alerts

**When triggered:** When prescribing medications that may interact

**Alert Features:**

- **Severity Coding:** Color-coded by interaction severity
  - 🔴 **Critical**: Life-threatening interactions
  - 🟠 **Major**: Significant clinical effects
  - 🟡 **Moderate**: Monitor for adverse effects
  - 🟢 **Minor**: Minor interactions
- **Interaction Details:** Drugs involved and effects
- **Alternative Medications:** Safer options when available
- **Safety Recommendations:** Monitoring and management advice

### Red Flag Warnings

**When triggered:** During AI diagnosis generation

**Red Flag Examples:**

- Chest pain with cardiac risk factors
- Fever with neurological symptoms
- Difficulty breathing with vital sign abnormalities
- Trauma with potential internal injuries

**Display Features:**

- ⚠️ **Warning Icon:** Prominent alert indication
- **Red Box Background:** High-visibility warning styling
- **Specific Warnings:** Detailed description of urgent findings
- **Action Recommendations:** Immediate steps to take

## 📊 System Performance

### Performance Indicators

**Loading States:**

- **Progress Bars:** Visual feedback for long operations
- **Status Messages**: Real-time operation updates
- **Cancel Options:** Stop long-running operations
- **Timeout Handling**: Graceful failure management

**Response Times:**

- **Patient Search:** <1 second
- **Diagnosis Generation:** 5-30 seconds (depending on complexity)
- **Lab Analysis:** <2 seconds
- **Database Queries:** <500ms

### Memory Management

**Features:**

- **Automatic Cleanup:** Release memory when not needed
- **Data Caching:** Cache recent queries for faster access
- **Background Processing:** Non-blocking operations
- **Resource Monitoring:** Track memory usage

## ⌨️ Keyboard Shortcuts

### Global Shortcuts

- **Ctrl+Q**: Exit application
- **F1**: Show help dialog
- **Alt+F4**: Close window

### Navigation Shortcuts

- **Tab**: Navigate between form fields
- **Enter**: Confirm actions (search, generate)
- **Escape**: Cancel operations, close dialogs
- **Ctrl+F**: Focus search box

### Dialog Shortcuts

- **Enter**: Confirm dialog action
- **Escape**: Cancel/close dialog

## 🔧 Troubleshooting

### Common Issues

**Database Connection Issues:**

```
Problem: Database shows "Disconnected"
Solution:
1. Check SQL Server service is running
2. Verify connection string in settings
3. Ensure firewall allows database access
4. Restart application
```

**AI Service Unavailable:**

```
Problem: AI status shows "Unavailable"
Solution:
1. Check internet connection
2. Verify API keys in configuration
3. Test individual AI providers
4. Use local Ollama as fallback
```

**Slow Performance:**

```
Problem: Interface responds slowly
Solution:
1. Check database performance
2. Close unused applications
3. Restart application
4. Check system resources
```

**Patient Search Fails:**

```
Problem: No search results returned
Solution:
1. Verify search criteria spelling
2. Check database connection
3. Ensure patient exists in database
4. Try broader search terms
```

### Error Messages

**Database Errors:**

- "Failed to connect to database" → Check SQL Server connection
- "Query execution failed" → Verify database schema
- "Timeout occurred" → Check database performance

**AI Service Errors:**

- "AI service unavailable" → Check API keys and internet
- "Request timeout" → Try again or use different model
- "Rate limit exceeded" -> Wait and retry later

**GUI Errors:**

- "Widget not responding" → Restart application
- "Failed to load data" → Check connection and permissions
- "Invalid input format" → Follow input guidelines

## 📞 Getting Help

### Resources

**Documentation:**

- [Installation Guide](../deployment/installation.md)
- [Configuration Guide](../deployment/configuration.md)
- [Clinical Workflows](clinical-workflows.md)
- [Troubleshooting Guide](../deployment/troubleshooting.md)

**Support:**

- Check status indicators in bottom status bar
- Review error messages in dialog boxes
- Consult logs for detailed error information
- Contact system administrator for database issues

### Clinical Support

**Best Practices:**

- Always verify critical findings with clinical judgment
- Use AI recommendations as decision support, not replacement
- Document reasoning for clinical decisions
- Follow standard clinical protocols and guidelines
- Consult specialists for complex cases

---

**Last Updated:** November 2024
**Version:** 0.1.0
**Application:** Clinical AI Assistant Desktop GUI

For additional help, see the [complete user guide](README.md) or [technical documentation](../api/README.md).
