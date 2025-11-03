# Web Interface User Guide

## 🌐 Overview

The Clinical AI Assistant Web Interface is a modern React-based application providing comprehensive clinical decision support through your web browser. This guide covers all features and workflows available in the web interface.

## 🚀 Getting Started

### Accessing the Web Interface

1. **Start the API Server:**
   ```bash
   python -m src.api.fastapi_app
   ```

2. **Start the Web Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser:**
   Navigate to `http://localhost:5173`

### First Visit

When you first access the web interface, you'll see:

1. **Dashboard Overview** with system status
2. **Navigation Menu** for different sections
3. **Status Indicators** for database and AI services
4. **Feature Cards** showcasing system capabilities

The application will automatically:
- ✅ Initialize application state
- ✅ Check database connectivity
- ✅ Verify AI service availability
- ✅ Load user interface components

## 🏠 Interface Layout

### Main Navigation

```
┌─────────────────────────────────────────────────────────────────┐
│ Clinical AI Assistant                            Database: ✓  AI: ✓  │
├─────────────────────────────────────────────────────────────────┤
│ Dashboard  Patient Search                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                             │
│                    [Main Content Area]                     │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation Menu

**Dashboard (Default):**
- System overview and statistics
- Quick access to common functions
- System status monitoring
- Feature highlights

**Patient Search:**
- Smart patient lookup functionality
- Advanced search options
- Patient selection and navigation

### Status Indicators

**Database Connection:**
- 🟢 **Connected** - Database accessible
- 🔴 **Disconnected** - Database connection failed
- 🟡 **Unknown** - Status checking

**AI Services:**
- 🟢 **Ready** - AI models available
- 🔴 **Unavailable** - No AI services accessible
- 🟡 **Unknown** - Status checking

## 🏠 Dashboard Overview

### System Information

**Key Metrics:**
- **Database Years**: 7 years of patient data
- **Total Patients**: 6,000+ patients in database
- **Database Tables**: 641 tables available

**System Features:**
- **Patient Records**: Search and comprehensive profiles
- **AI Diagnosis**: Differential diagnosis with probability scoring
- **Treatment Plans**: Evidence-based recommendations
- **Drug Interactions**: Safety checking and warnings
- **Lab Analysis**: Results with trend monitoring

### Quick Actions

**Primary Functions:**
- **Search Patient**: Navigate to patient search
- **AI Analysis**: Quick access to AI tools (when available)

### Feature Cards

**Patient Management:**
- Smart patient search capabilities
- Complete medical history access
- Laboratory result integration
- Medication tracking

**AI Intelligence:**
- Differential diagnosis generation
- Treatment recommendations
- Clinical guideline integration
- Evidence-based decision support

**Safety Features:**
- Drug interaction checking
- Allergy alert system
- Red flag detection
- Reference range validation

## 🔍 Patient Search

### Search Interface

**Search Options:**
- **Name Search**: Patient first or last name (partial matches supported)
- **TCKN Search**: Turkish ID number (partial matches supported)
- **Real-time Search**: Starts after 2 characters, 300ms debounce
- **Quick Results**: Limited to 20 results for performance

### Search Process

1. **Enter Search Criteria:**
   - Type patient name (e.g., "Ahmet" finds "Ahmet", "Ahm...")
   - Enter TCKN (e.g., "123456" finds matching patients)
   - Minimum 2 characters required

2. **View Results:**
   - **Patient Name**: Full name display
   - **TCKN**: Turkish ID number
   - **Age**: Calculated from birth date
   - **Gender**: Male/Female/Unknown
   - **Phone**: Contact information (if available)

3. **Select Patient:**
   - Click anywhere on patient row
   - Navigate to patient details page
   - Load comprehensive patient profile

### Search Results Display

**Table Columns:**
- **TCKN**: Turkish identification number
- **Full Name**: Patient first and last name
- **Age**: Current age in years
- **Gender**: Male/Female/Unknown
- **Last Visit**: Most recent encounter date

**Visual Features:**
- **Hover Effects**: Row highlighting on mouse hover
- **Loading States**: Search progress indicators
- **Empty States**: Helpful messages when no results found
- **Error Handling**: User-friendly error messages

### Search Tips

✅ **Best Practices:**
- Use partial names for flexible matching
- Search by TCKN for exact patient identification
- Check spelling for common variations
- Use unique identifiers when possible

❌ **Limitations:**
- Single character searches not allowed
- Results limited to 20 patients
- Requires 2+ characters for search initiation

## 👤 Patient Details Page

### Patient Header

**Patient Information Display:**
- **Full Name**: Patient complete name
- **TCKN**: Turkish ID number
- **Age**: Current calculated age
- **Gender**: Male/Female/Unknown
- **Birth Date**: Date of birth
- **Phone**: Contact number (if available)
- **Address**: Residential address (if available)

### Tabbed Interface

**Available Tabs:**
1. **AI Diagnosis**: Generate differential diagnosis
2. **Treatment Plan**: Get treatment recommendations
3. **Lab Results**: View laboratory data and trends
4. **Medications**: Medication history (coming soon)
5. **Visit History**: Encounter timeline (coming soon)

### Tab Navigation

**Active Tab Indicators:**
- **Blue Border**: Currently active tab
- **Hover Effects**: Visual feedback on tab hover
- **Disabled State**: Grayed out for unavailable features
- **Badge Indicators**: "Coming Soon" for future features

## 🧠 AI Diagnosis Tab

### Diagnosis Generation

**Input Fields:**
- **Chief Complaint & Symptoms**: Detailed symptom description
- **AI Model Selection**: Choose AI provider for analysis
- **Generate Button**: Start AI-powered diagnosis

**Chief Complaint Guidelines:**
- Be specific about symptoms
- Include duration and severity
- Mention aggravating/alleviating factors
- Describe associated symptoms

### AI Model Selection

**Available Models:**
- **Auto (Smart Routing)**: System selects optimal model
- **Claude**: Best for complex cases
- **GPT-4o**: High-quality general analysis
- **Gemini**: Alternative premium model
- **Ollama**: Local model (fast, private)

**Model Characteristics:**
- **Claude**: Best for complex clinical reasoning
- **GPT-4o**: Fast, high-quality responses
- **Gemini**: Alternative perspective
- **Ollama**: Local processing, no internet required

### Results Display

**Differential Diagnosis Table:**
- **Diagnosis**: Identified condition
- **ICD-10 Code**: Standard diagnosis code
- **Probability**: Likelihood percentage
- **Urgency**: Severity level (Critical/Major/Moderate/Minor)

**Urgency Color Coding:**
- 🔴 **Critical**: Immediate attention required
- 🟠 **Major**: Urgent evaluation needed
- 🟡 **Moderate**: Timely follow-up recommended
- 🟢 **Minor**: Routine care appropriate

**Red Flags Section:**
- ⚠️ **Warning Display**: Prominent red box styling
- **Critical Findings**: Urgent condition indicators
- **Action Recommendations**: Immediate steps to take
- **Risk Assessment**: Danger level evaluation

**Recommended Tests:**
- **Lab Studies**: Suggested blood work
- **Imaging**: Radiology recommendations
- **Specialist Referrals**: When to refer patients
- **Follow-up Timeline**: Recommended review schedule

## 💊 Treatment Plan Tab

### Treatment Generation

**Input Fields:**
- **Confirmed Diagnosis**: Primary diagnosis for treatment
- **AI Model Selection**: Choose AI provider
- **Generate Button**: Start treatment recommendation

**Diagnosis Guidelines:**
- Enter confirmed or working diagnosis
- Use specific clinical terminology
- Include severity when relevant
- Consider comorbid conditions

### Treatment Results

**Medication Recommendations:**
- **Medication Name**: Drug name and formulation
- **Dosage**: Strength and frequency
- **Duration**: Treatment course length

**Clinical Guidelines:**
- **Evidence-Based Protocols**: Current medical standards
- **Treatment Algorithms**: Step-by-step approaches
- **Monitoring Requirements**: Follow-up parameters
- **Contraindications**: When to avoid treatment

**Follow-up Plan:**
- **Timeline**: Recommended review schedule
- **Monitoring**: What to watch for
- **Adjustments**: When to modify treatment
- **Referral Criteria**: Specialist consultation needs

## 🧪 Lab Results Tab

### Laboratory Data

**Test Selection:**
- **Common Tests**: Frequently ordered studies
- **Time Range**: Filter results by date range
- **Refresh Button**: Update lab data

**Available Tests:**
- Hemoglobin, White Blood Cell, Platelet Count
- Glucose, HbA1c, Creatinine
- ALT, AST, Total Cholesterol
- LDL, HDL, Triglycerides

### Results Display

**Data Table:**
- **Date**: Test collection date
- **Result**: Laboratory value
- **Reference Range**: Normal values
- **Status**: Normal/Abnormal indicator

**Status Indicators:**
- 🟢 **Normal**: Within reference range
- 🔴 **Abnormal**: Outside reference range
- **Gray**: Insufficient data

**Visual Features:**
- **Abnormal Highlighting**: Red background for out-of-range values
- **Normal Range Display**: Reference intervals shown
- **Unit Information**: Measurement units included
- **Sort Options**: Date-based ordering

### Trend Analysis

**Chart Visualization:**
- **Interactive Plots**: Time-based value trends
- **Reference Ranges**: Normal value shading
- **Data Points**: Individual measurement markers
- **Export Options**: Save charts as images

*Note: Chart functionality displays placeholder for development*

## ⚡ System Features

### Real-Time Updates

**Status Monitoring:**
- **Database Connection**: Live connectivity status
- **AI Services**: Provider availability status
- **Error Handling**: User-friendly error messages
- **Loading States**: Progress indicators for operations

### Responsive Design

**Device Support:**
- **Desktop**: Full feature set, optimal layout
- **Tablet**: Adapted interface, touch-friendly
- **Mobile**: Essential features, simplified navigation

**Responsive Features:**
- **Adaptive Layout**: Content reorganization
- **Touch Gestures**: Mobile-friendly interactions
- **Readable Text**: Optimized font sizes
- **Efficient Navigation**: Mobile-optimized menus

### Performance Optimizations

**Speed Enhancements:**
- **Debounced Search**: Prevents excessive API calls
- **Data Caching**: Store frequently accessed data
- **Lazy Loading**: Load content on demand
- **Error Recovery**: Graceful failure handling

## 🔧 Configuration

### Environment Setup

**Development Environment:**
```bash
# Frontend development server
npm run dev

# Backend API server
python -m src.api.fastapi_app

# Environment variables
VITE_API_URL=http://localhost:8000
```

**Production Environment:**
```bash
# Build frontend
npm run build

# Serve built files
npm run preview

# Production API
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000
```

### Customization Options

**Theme Colors:**
- **Medical Blue**: Primary color scheme
- **Status Colors**: Red/green/yellow indicators
- **Typography**: Medical-appropriate fonts
- **Spacing**: Clinical interface layout

**Feature Flags:**
- **AI Integration**: Enable/disable AI features
- **Advanced Analytics**: Show/hide advanced features
- **Experimental UI**: Preview new interface elements

## 📱 Browser Compatibility

### Supported Browsers

**Desktop Browsers:**
- ✅ **Chrome 88+** (Recommended)
- ✅ **Firefox 85+**
- ✅ **Safari 14+**
- ✅ **Edge 88+**

**Mobile Browsers:**
- ✅ **Chrome Mobile** (Android)
- ✅ **Safari Mobile** (iOS)

### Required Features

**JavaScript Requirements:**
- ES2020 support
- Async/await functionality
- Modern DOM APIs
- Local storage support

**CSS Requirements:**
- Flexbox layout
- CSS Grid support
- Modern color functions
- Responsive media queries

## 🔒 Security Considerations

### Data Protection

**Local Storage:**
- No sensitive PHI stored in browser
- Session data only
- Automatic cleanup on logout
- Secure cookie handling

**API Security:**
- HTTPS required in production
- CORS configuration
- Request validation
- Error message sanitization

### Clinical Safety

**AI Recommendations:**
- Decision support, not replacement
- Clinical judgment required
- Verification of critical findings
- Professional oversight maintained

## 📞 Getting Help

### Common Issues

**Connection Problems:**
```
Problem: "Failed to connect to API"
Solution:
1. Check API server is running
2. Verify API URL in environment
3. Check network connectivity
4. Try refreshing page
```

**Search Issues:**
```
Problem: "No patients found"
Solution:
1. Verify search spelling
2. Try broader search terms
3. Check database connection
4. Confirm patient exists
```

**AI Service Issues:**
```
Problem: "AI services unavailable"
Solution:
1. Check API key configuration
2. Verify internet connection
3. Try different AI model
4. Use local Ollama as fallback
```

### Performance Issues

**Slow Loading:**
- Check internet connection speed
- Verify API server performance
- Clear browser cache
- Restart application

**Memory Issues:**
- Close unused browser tabs
- Restart browser
- Check system resources
- Contact system administrator

### Support Resources

**Documentation:**
- [Installation Guide](../deployment/installation.md)
- [Configuration Guide](../deployment/configuration.md)
- [Troubleshooting Guide](../deployment/troubleshooting.md)
- [API Reference](../api/README.md)

**Help Features:**
- Tooltips on hover for all buttons
- Contextual help in dialogs
- Status indicators for system health
- Error messages with guidance

---

**Last Updated:** November 2024
**Version:** 0.1.0
**Application:** Clinical AI Assistant Web Interface

For additional help, see the [desktop GUI guide](desktop-gui.md) or [CLI reference](cli-reference.md).