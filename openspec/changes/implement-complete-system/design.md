# Complete Clinical AI Assistant System - Design Document

## Context

The Clinical AI Assistant project has successfully completed foundational phases (1-3), implementing database infrastructure, domain models, and clinical decision support modules. This design document covers the architectural decisions for implementing the remaining system components: AI integration, user interfaces (Desktop/Web/CLI), API layer, and production deployment.

### Background
- **Domain**: Family medicine clinical decision support
- **Database**: SQL Server 2014/2022 with 641 tables (~350MB, 7 years, 6-7k patients)
- **Users**: Single doctor, local deployment, no KVKK/GDPR constraints
- **Platform**: Windows 11, Python 3.11+, Local + Remote AI services

### Constraints
- **No Authentication Required**: Single-user, local deployment
- **No Encryption Required**: Secure local environment
- **Full Debug Logging**: Acceptable for personal use
- **Windows-Only Deployment**: No cross-platform requirements
- **Turkish Language Support**: UI and prompts must support Turkish medical terminology

### Stakeholders
- **Primary User**: Family medicine practitioner
- **Technical Owner**: Solo developer
- **End Goal**: Production-ready multi-interface clinical assistant

## Goals / Non-Goals

### Goals
1. **Multi-Interface Access**: Provide Desktop GUI, Web UI, and CLI interfaces for flexible access
2. **Intelligent AI Routing**: Optimize cost/performance by routing simple tasks to local models, complex tasks to premium cloud models
3. **Clinical Safety**: Implement drug interaction checking, allergy alerts, and red flag detection
4. **Production Quality**: >80% test coverage, comprehensive documentation, deployment scripts
5. **Turkish Medical Context**: Support Turkish language prompts and medical terminology
6. **Offline Capability**: Basic functionality with Ollama when internet unavailable

### Non-Goals
1. **Multi-User Support**: No user management, authentication, or authorization
2. **Mobile Applications**: Desktop/Web/CLI only, no native mobile apps
3. **Real-Time Collaboration**: No concurrent multi-user editing
4. **Electronic Health Record Integration**: Standalone system, no HL7/FHIR integration
5. **Production-Grade Security**: KVKK/GDPR compliance not required per project constraints
6. **Cross-Platform Deployment**: Windows 11 only

## Decisions

### Decision 1: Hybrid AI Architecture (Senaryo A)

**Choice**: Implement smart routing between local (Ollama) and remote (Claude/GPT/Gemini) AI models based on task complexity.

**Rationale**:
- **Cost Optimization**: Use free local Ollama for simple tasks (patient summaries, basic stats)
- **Quality for Critical Tasks**: Use Claude 3.5 Sonnet for complex clinical decisions (diagnosis, treatment planning)
- **Fallback Reliability**: Chain Claude → GPT-4o → Gemini Pro → Ollama for high availability
- **Offline Capability**: Ollama provides basic functionality when internet unavailable

**Implementation**:
```python
class AIRouter:
    TASK_COMPLEXITY = {
        'simple': ['patient_summary', 'basic_stats'],
        'moderate': ['lab_trend_analysis', 'medication_adherence'],
        'complex': ['differential_diagnosis', 'treatment_planning', 'drug_interactions']
    }

    MODEL_PRIORITY = {
        'simple': ['ollama'],
        'moderate': ['ollama', 'gpt-4o-mini'],
        'complex': ['claude-3.5-sonnet', 'gpt-4o', 'gemini-pro', 'ollama']
    }
```

**Alternatives Considered**:
- **Senaryo B (Single Premium Model)**: Claude-only would be simpler but expensive and lacks offline capability
- **Senaryo C (Ensemble Voting)**: Multiple models voting would be most accurate but slow and costly
- **Local-Only**: Ollama-only would be free but insufficient quality for critical clinical decisions

**Trade-offs**:
- ✅ **Pro**: Cost-effective ($10-20/month vs $100+/month for Claude-only)
- ✅ **Pro**: Offline fallback capability
- ✅ **Pro**: Performance optimization (Ollama <2s vs Claude ~10s for simple tasks)
- ❌ **Con**: More complex routing logic to maintain
- ❌ **Con**: Inconsistent response quality across models

### Decision 2: PySide6 for Desktop GUI

**Choice**: Use PySide6 (Qt6 official Python bindings) for desktop application.

**Rationale**:
- **Official Support**: PySide6 is Qt's official Python binding, better maintained than PyQt6
- **Medical-Grade UI**: Qt provides professional widgets suitable for medical applications
- **Native Performance**: True native Windows application, not Electron-based
- **Rich Ecosystem**: pyqtgraph for charts, QWebEngine for embedded charts
- **PyInstaller Compatible**: Easy to build standalone .exe

**Implementation**:
- Main window with QTabWidget for organized clinical views
- Custom widgets for patient search, diagnosis panel, treatment recommendations
- Qt stylesheet for medical-themed blue/green color scheme
- Signal/slot architecture for reactive UI updates

**Alternatives Considered**:
- **Tkinter**: Standard library but limited widgets and dated appearance
- **PyQt6**: Similar to PySide6 but licensing concerns (GPL vs LGPL)
- **Electron + Python backend**: Would reuse React frontend but heavy (~200MB) and non-native
- **Kivy**: Cross-platform but poor Windows native integration

**Trade-offs**:
- ✅ **Pro**: Professional appearance suitable for medical use
- ✅ **Pro**: Native Windows performance and integration
- ✅ **Pro**: Extensive documentation and examples
- ❌ **Con**: Learning curve for Qt framework
- ❌ **Con**: Separate codebase from Web UI (can't share React components)

### Decision 3: React + FastAPI for Web Interface

**Choice**: Build modern web UI with React 18 + Vite frontend and FastAPI backend.

**Rationale**:
- **Modern Developer Experience**: Vite provides instant HMR, fast builds
- **Component Reusability**: React components can be shared across views
- **Rich Ecosystem**: Tailwind CSS, shadcn/ui, Chart.js for polished UI
- **API-First Design**: FastAPI backend can serve Desktop, Web, CLI, and future integrations
- **Type Safety**: TypeScript frontend + Pydantic backend for end-to-end type safety

**Architecture**:
```
Frontend (React + Vite)          Backend (FastAPI)
├── Patient Search               ├── /api/v1/patients
├── Clinical Dashboard    <-->   ├── /api/v1/analyze/diagnosis
├── Diagnosis Panel              ├── /api/v1/analyze/treatment
├── Treatment Panel              ├── /api/v1/drugs/interactions
└── Lab Charts                   └── /api/v1/labs/trends
```

**Alternatives Considered**:
- **Django + Jinja Templates**: Traditional server-side rendering but dated UX
- **Vue.js + Flask**: Lighter weight but smaller ecosystem than React + FastAPI
- **Blazor**: Would require C# backend, not aligned with Python stack

**Trade-offs**:
- ✅ **Pro**: Best-in-class developer experience and tooling
- ✅ **Pro**: API backend enables future mobile apps or integrations
- ✅ **Pro**: Real-time updates with React state management
- ❌ **Con**: Two separate servers in development (Vite + FastAPI)
- ❌ **Con**: Deployment complexity (static files + API server)

### Decision 4: Typer + Rich for CLI

**Choice**: Use Typer for command structure and Rich for beautiful terminal output.

**Rationale**:
- **Modern CLI Experience**: Typer provides clean argparse-based CLI with type hints
- **Beautiful Output**: Rich enables tables, progress bars, syntax highlighting
- **Batch Processing Support**: CLI ideal for scripting and automation workflows
- **JSON Export**: Enables integration with external systems (e.g., Java/.NET app)
- **Professional Appearance**: Color-coded severity indicators, formatted tables

**Commands**:
```bash
clinical-ai analyze --tckn 12345678901           # Patient analysis
clinical-ai diagnose --complaint "ateş, öksürük"  # Diagnosis
clinical-ai drug-check --add "Amoksisilin"        # Interaction check
clinical-ai inspect database                      # Schema exploration
clinical-ai batch analyze --input patients.csv    # Batch processing
```

**Alternatives Considered**:
- **Click**: Popular but Typer provides better type safety and modern API
- **argparse**: Standard library but verbose and dated compared to Typer
- **Plain print statements**: Would work but unprofessional appearance

**Trade-offs**:
- ✅ **Pro**: Scriptable for automation workflows
- ✅ **Pro**: Professional appearance with minimal code
- ✅ **Pro**: JSON export for programmatic integration
- ❌ **Con**: Less intuitive than GUI for non-technical users
- ❌ **Con**: Limited interactivity compared to full TUI

### Decision 5: Connection Pooling Strategy

**Choice**: Implement database connection pooling with SQLAlchemy's QueuePool (default).

**Rationale**:
- **Concurrent Access**: Desktop GUI, Web API, CLI may access database simultaneously
- **Performance**: Reusing connections avoids ~100ms overhead per query
- **Resource Management**: Pool limits prevent exhausting database connections
- **SQLAlchemy Default**: QueuePool is battle-tested and requires minimal configuration

**Configuration**:
```python
engine = create_engine(
    connection_string,
    pool_size=5,          # Desktop + Web + CLI simultaneous users
    max_overflow=10,      # Burst capacity
    pool_timeout=30,      # Wait up to 30s for connection
    pool_recycle=3600,    # Recycle connections every hour
)
```

**Alternatives Considered**:
- **NullPool**: No pooling, simplest but poor performance for multiple interfaces
- **StaticPool**: Single connection, insufficient for concurrent access
- **AsyncIO Engine**: Would require rewriting all models for async/await

**Trade-offs**:
- ✅ **Pro**: Good performance with minimal configuration
- ✅ **Pro**: Handles concurrent access from multiple interfaces
- ✅ **Pro**: Automatic connection health checks with pool_recycle
- ❌ **Con**: Consumes more database server resources (5+ connections)
- ❌ **Con**: Potential deadlocks if not properly managed

### Decision 6: Error Handling and Retry Strategy

**Choice**: Use `tenacity` library for retry logic with exponential backoff.

**Rationale**:
- **Transient Failures**: Network glitches, API rate limits are common with cloud AI services
- **User Experience**: Automatic retry avoids showing errors for temporary issues
- **Backpressure**: Exponential backoff prevents overwhelming failing services
- **Declarative**: `@retry` decorator keeps business logic clean

**Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
def call_ai_service(prompt: str) -> dict:
    # Will retry up to 3 times with 1s, 2s, 4s delays
    return ai_client.complete(prompt)
```

**Alternatives Considered**:
- **Manual try/except**: More control but boilerplate code scattered everywhere
- **Circuit Breaker**: Good for preventing cascade failures but overkill for single-user app
- **No Retry**: Simplest but poor UX when transient errors occur

**Trade-offs**:
- ✅ **Pro**: Clean code with declarative retry policies
- ✅ **Pro**: Handles transient failures gracefully
- ✅ **Pro**: Configurable per operation (DB vs AI have different retry needs)
- ❌ **Con**: May hide real issues if configured too aggressively
- ❌ **Con**: Adds latency when service is genuinely down

### Decision 7: Turkish Prompt Engineering Strategy

**Choice**: Create structured prompt templates with Turkish medical terminology embedded.

**Rationale**:
- **Medical Context**: Turkish medical terms (e.g., "diferansiyel tanı", "ilaç etkileşimi") improve AI understanding
- **Consistency**: Templates ensure consistent prompt structure across all clinical tasks
- **Maintainability**: Centralized prompts easier to update than scattered strings
- **JSON Output**: Structured prompts yield structured responses easier to parse

**Template Example**:
```python
DIAGNOSIS_PROMPT = """
Hasta bilgileri:
- Şikayet: {chief_complaint}
- Vital bulgular: {vitals}
- Lab sonuçları: {labs}
- Geçmiş hastalıklar: {medical_history}

Lütfen diferansiyel tanı listesi ver. Her tanı için:
1. Tanı adı (Türkçe)
2. ICD-10 kodu
3. Olasılık (0-1)
4. Destekleyen bulgular
5. Kısa açıklama

JSON formatında dön:
{{"differential_diagnosis": [...]}}
"""
```

**Alternatives Considered**:
- **English-Only Prompts**: Simpler but AI may miss Turkish medical nuances
- **Bilingual Prompts**: More robust but verbose and confusing
- **User-Editable Prompts**: Flexible but risky for non-technical users

**Trade-offs**:
- ✅ **Pro**: Better AI understanding of Turkish medical context
- ✅ **Pro**: Structured JSON responses easier to parse
- ✅ **Pro**: Centralized templates for easy updates
- ❌ **Con**: Requires careful Turkish prompt engineering
- ❌ **Con**: Some AI models (especially older ones) weaker in Turkish

## Risks / Trade-offs

### Risk 1: AI Provider API Changes

**Risk**: OpenAI, Anthropic, Google may change API pricing or deprecate models.

**Mitigation**:
- Abstraction layer (`src/ai/base_client.py`) isolates provider-specific code
- Smart router allows seamless fallback to alternative providers
- Ollama local model ensures offline capability

**Likelihood**: Medium | **Impact**: Medium | **Mitigation Status**: ✅ Addressed

### Risk 2: Database Performance with Large Queries

**Risk**: Complex patient analysis queries may timeout on large datasets (6-7k patients).

**Mitigation**:
- Connection pooling reduces per-query overhead
- Database indexes on frequently queried columns (TCKN, HASTA_ID)
- Query optimization using SQLAlchemy explain() for slow queries
- Pagination for large result sets in API endpoints

**Likelihood**: Medium | **Impact**: Medium | **Mitigation Status**: ✅ Addressed

### Risk 3: PyInstaller Executable Size

**Risk**: Desktop GUI bundled with PySide6, AI SDKs, and dependencies may exceed 500MB.

**Mitigation**:
- Exclude unnecessary packages (e.g., unused AI providers can be optional)
- Use `--exclude-module` for development-only dependencies
- Consider UPX compression (reduces size ~30%)
- If still too large, distribute as Python + requirements instead of .exe

**Likelihood**: High | **Impact**: Low | **Mitigation Status**: ⚠️ Monitor

### Risk 4: AI Response Parsing Failures

**Risk**: AI models may return non-JSON or malformed responses.

**Mitigation**:
- Retry with more explicit JSON formatting instructions
- Graceful degradation: show raw AI response if JSON parsing fails
- Fallback to rule-based logic for critical safety checks (e.g., allergy detection)

**Likelihood**: Medium | **Impact**: Medium | **Mitigation Status**: ✅ Addressed

### Risk 5: Turkish Language Support Gaps

**Risk**: AI models trained primarily on English may produce lower quality Turkish responses.

**Mitigation**:
- Use Claude 3.5 Sonnet (best multilingual support) for complex tasks
- Provide context-rich prompts with medical terminology
- Hybrid approach: AI for analysis, pre-built Turkish templates for output formatting
- User feedback mechanism to improve prompts over time

**Likelihood**: Medium | **Impact**: Medium | **Mitigation Status**: ✅ Addressed

## Migration Plan

**N/A**: This is additive functionality on top of existing clinical modules. No data migration required.

### Rollout Strategy

**Phase 4 (Week 1-2)**: AI Integration + Desktop GUI
1. Implement AI clients and router
2. Build Desktop GUI skeleton and core widgets
3. Test AI integration with real clinical modules
4. User acceptance testing with Desktop GUI

**Phase 5 (Week 3)**: Web Interface + API
1. Set up FastAPI backend with all endpoints
2. Build React frontend components
3. Connect frontend to API and test workflows
4. Deploy web app to localhost

**Phase 6 (Week 3-4)**: CLI + Testing
1. Implement CLI commands
2. Write comprehensive test suites
3. Run performance benchmarks
4. Fix any identified issues

**Phase 7 (Week 4)**: Documentation + Deployment
1. Write user documentation
2. Create deployment scripts
3. Build PyInstaller executable
4. Final system testing and handoff

### Rollback Plan

If critical issues arise during implementation:
1. **AI Integration Issues**: Fall back to rule-based clinical logic (already implemented in Phase 3)
2. **GUI Issues**: Use CLI or Web interface as interim solution
3. **Database Issues**: Restore from backup, revert ORM changes
4. **Complete Rollback**: Git revert to last stable commit (6471680 - Phase 3 complete)

## Performance Targets

### Response Time Targets

| Operation | Target | Acceptable | Unacceptable |
|-----------|--------|------------|--------------|
| Patient Summary | <2s | <5s | >10s |
| Diagnosis (Ollama) | <5s | <10s | >15s |
| Diagnosis (Claude/GPT) | <30s | <60s | >90s |
| Treatment Recommendations | <30s | <60s | >90s |
| Lab Analysis | <5s | <10s | >15s |
| Drug Interaction Check | <1s | <3s | >5s |
| API Endpoint (Patient) | <500ms | <1s | >2s |
| Desktop GUI Launch | <5s | <10s | >15s |
| Web Frontend Load | <3s | <5s | >10s |

### Scalability Targets

- **Concurrent Users**: 1 primary (design allows up to 5-10 simultaneous API requests)
- **Database Size**: 350MB current, design supports up to 10GB
- **Patient Records**: 6-7k current, design supports up to 50k
- **API Throughput**: 10 req/s (far exceeds single-user needs)

## Open Questions

### Question 1: Desktop GUI Distribution Method

**Question**: Should we distribute as PyInstaller .exe or Python + requirements?

**Options**:
- **Option A (PyInstaller .exe)**: Single-file distribution, easier for non-technical user
- **Option B (Python + requirements)**: Smaller download, easier to update dependencies

**Status**: ⏳ **To be decided during Phase 7 based on .exe size**

### Question 2: Web Interface Deployment

**Question**: Should web interface run permanently or on-demand?

**Options**:
- **Option A (Systemd/Windows Service)**: Always running, instant access but consumes resources
- **Option B (On-Demand)**: Start via script when needed, saves resources

**Status**: ⏳ **To be decided based on user preference**

### Question 3: AI Model Preference

**Question**: Should we default to Ollama or Claude for moderate-complexity tasks?

**Options**:
- **Option A (Ollama First)**: Cost-free, faster, but lower quality
- **Option B (Claude First)**: Higher quality, but costs $0.01-0.05 per request

**Status**: ⏳ **To be decided after testing quality differences in Turkish medical context**

## Acceptance Criteria

This implementation is complete when:

1. ✅ All 4 AI providers integrate successfully (Ollama, Claude, GPT, Gemini)
2. ✅ Smart routing selects appropriate model based on task complexity
3. ✅ Desktop GUI launches and displays patient clinical data
4. ✅ Web interface accessible at http://localhost:5173 with functional API
5. ✅ CLI commands execute and produce correct output
6. ✅ Test coverage >80% across all new modules
7. ✅ Performance targets met for patient summary (<2s) and diagnosis (<30s)
8. ✅ All documentation complete (8 user guides + README + API reference)
9. ✅ Deployment scripts work on clean Windows 11 system
10. ✅ User can successfully: search patient → view dashboard → generate diagnosis → view treatment recommendations

## References

- **Implementation Plan**: `Implementation_plan.md` (original 1622-line project specification)
- **Database Schema**: `docs/critical_tables_schema.txt` (641 tables analyzed)
- **Phase 3 Summary**: `.serena/memories/phase_3_completion_summary.md` (clinical modules complete)
- **OpenSpec Project**: `openspec/project.md` (conventions and tech stack)
- **Original Prompt**: Turkish medical AI assistant requirements

## Approval

This design document requires approval before implementation begins.

**Pending**: User review and approval of architectural decisions.

Upon approval, proceed with `tasks.md` implementation checklist.
