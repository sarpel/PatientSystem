# AI Agent Guidelines

Guidelines for AI coding assistants (Claude Code, GitHub Copilot, Cursor, etc.) working on the Clinical AI Assistant project.

## 🎯 Purpose

This document provides AI agents with:
1. Context management strategies
2. Project-specific best practices
3. Common pitfalls and how to avoid them
4. Decision-making frameworks

## 🧠 Context Management

### Session Initialization

When starting a new session, **ALWAYS** follow this checklist:

```bash
# 1. Check current branch and status
git status && git branch

# 2. Verify database connectivity
python test_db_connection.py

# 3. Check running services
netstat -ano | findstr "8080"   # Backend
netstat -ano | findstr "5173"   # Frontend

# 4. Review recent changes
git log --oneline -5

# 5. Read critical documentation
# - CLAUDE.md (project patterns)
# - TROUBLESHOOTING.md (known issues)
# - This file (AGENTS.md)
```

### Verification Before Making Changes

**NEVER assume, ALWAYS verify:**

| What to Check | How to Check | Why |
|--------------|--------------|-----|
| ODBC Drivers | `python -c "import pyodbc; print(pyodbc.drivers())"` | Prevent connection errors |
| Port Configuration | Check `.env` and running processes | Prevent conflicts |
| API Contract | Read backend route + frontend component | Prevent mismatches |
| Naming Conventions | Grep for similar patterns | Maintain consistency |
| Existing Tests | `find . -name "*test*"` | Understand test patterns |

### Context Retention Strategies

1. **Document As You Go**
   - Add comments explaining non-obvious decisions
   - Update this file with new patterns discovered
   - Maintain TROUBLESHOOTING.md with solutions

2. **Use Descriptive Commits**
   ```bash
   # ❌ Bad
   git commit -m "fix bug"

   # ✅ Good
   git commit -m "fix: update frontend to match new API response format

   - Changed PatientSearch.tsx to use lowercase field names
   - Updated type interface to match backend schema
   - Resolves blank screen issue on search results"
   ```

3. **Create Decision Records**
   When making architectural decisions, document:
   - What was the problem?
   - What alternatives were considered?
   - Why was this solution chosen?
   - What are the trade-offs?

## ⚠️ Critical Rules - Never Break These

### Rule 1: Verify Environment Configuration

**Before** modifying database connections:

```python
# ALWAYS run this check
import pyodbc
available_drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
print(f"Available drivers: {available_drivers}")

# THEN update .env to match reality, not assumptions
```

**Why**: Assuming "standard" drivers causes production failures. Real systems vary.

**Lesson**: 2025-11-06 - Assumed Driver 17, system had Driver 11, caused 8+ hours of downtime.

### Rule 2: Synchronize API Contracts

**Before** changing backend API response format:

```bash
# 1. Document current format
# 2. Identify all frontend consumers
grep -r "patient.TCKN\|patient.ADI" frontend/src/

# 3. Update backend
# 4. Update frontend immediately
# 5. Update TypeScript interfaces
# 6. Test end-to-end
```

**Why**: Mismatched API contracts cause silent failures that are hard to debug.

**Lesson**: 2025-11-06 - Changed backend to lowercase fields, frontend crashed accessing uppercase fields.

### Rule 3: Follow Naming Conventions

**Check existing patterns BEFORE creating new code:**

```bash
# Check Python patterns
grep -r "def.*patient" src/ | head -5

# Check TypeScript patterns
grep -r "interface.*Patient" frontend/src/ | head -5

# Check database column names
grep -r "HASTA_KIMLIK_NO\|DOGUM_TARIHI" src/models/
```

**Current Conventions** (must follow):
- Database: `UPPERCASE_SNAKE_CASE`
- Python: `lowercase_snake_case`
- API JSON: `lowercase` (no underscores)
- TypeScript: `camelCase`
- React Components: `PascalCase`

### Rule 4: Never Guess - Always Test

**Before** claiming something works:

```bash
# Test database connection
python test_db_connection.py

# Test API endpoint
curl http://localhost:8080/api/v1/patients/search?q=test

# Test frontend
# Open browser, use DevTools Network tab, verify responses
```

**Why**: Manual verification catches issues automated tests miss.

**Lesson**: Visual testing would have caught the field name mismatch immediately.

## 🔧 Decision Framework

### When to Modify Backend API

**Ask these questions:**

1. **Is this a breaking change?**
   - Changing field names = YES
   - Adding optional fields = NO
   - Changing data types = YES

2. **Who consumes this API?**
   - Search for usage: `grep -r "patients/search" frontend/`
   - Check TypeScript interfaces
   - Review API documentation

3. **Can I version instead?**
   - Consider `/api/v2/...` for breaking changes
   - Maintain v1 for backward compatibility

4. **Have I updated:**
   - [ ] Backend route handler
   - [ ] API documentation (`/docs`)
   - [ ] Frontend TypeScript interface
   - [ ] Frontend component usage
   - [ ] This AGENTS.md file
   - [ ] Test cases (if they exist)

### When to Refactor

**Safe to refactor when:**
- No external API contract changes
- Internal implementation only
- Covered by tests (or you add tests)
- Backward compatible

**Requires coordination when:**
- Changes API response format
- Modifies database schema
- Updates environment variables
- Changes port numbers or URLs

### When to Create New Files

**Ask:**
1. **Where do similar files live?**
   - Tests → `tests/` or `frontend/src/__tests__/`
   - Scripts → `scripts/`
   - Docs → project root or `docs/`

2. **Is there an existing pattern?**
   - Check: `find . -name "*test*"` or `find . -name "*util*"`
   - Follow established structure

3. **Will this clutter the project?**
   - Temporary files → Clean up after use
   - Permanent files → Logical organization

## 🚫 Common Mistakes to Avoid

### Mistake 1: Assuming Standard Configuration

```python
# ❌ DON'T
DATABASE_URL = "driver=ODBC+Driver+17"  # Assumed standard

# ✅ DO
import pyodbc
drivers = pyodbc.drivers()
# Use what's actually installed
```

### Mistake 2: Changing One Side of API Contract

```typescript
// Backend changed to:
{ "tckn": "123", "name": "John" }

// ❌ Frontend still uses:
patient.TCKN  // undefined!

// ✅ Update immediately:
patient.tckn  // works!
```

### Mistake 3: Inconsistent Naming

```python
# ❌ Mixing conventions
def getPatientData():  # camelCase in Python?
    return patient_TCKN  # mixed case?

# ✅ Consistent
def get_patient_data():  # snake_case
    return patient_tckn  # snake_case
```

### Mistake 4: Not Testing Changes

```bash
# ❌ Making changes and assuming they work
git commit -m "fix"

# ✅ Test first
python test_db_connection.py
curl http://localhost:8080/api/v1/patients/search?q=test
# Open browser, verify in Network tab
git commit -m "fix: verified working"
```

### Mistake 5: Creating Files in Wrong Locations

```bash
# ❌ Scattered organization
project_root/test_something.py
project_root/debug.sh
src/utils/another_test.py

# ✅ Organized
tests/test_something.py
scripts/debug.sh
tests/utils/test_utils.py
```

## 📝 Code Review Checklist

Before committing changes, verify:

### Backend Changes
- [ ] No hardcoded values (use .env)
- [ ] Error handling present
- [ ] Logging statements added
- [ ] Database queries optimized (select specific columns)
- [ ] API response format documented
- [ ] No breaking changes without version bump

### Frontend Changes
- [ ] TypeScript interfaces match API
- [ ] Error states handled
- [ ] Loading states shown
- [ ] Console errors checked
- [ ] Network tab verified
- [ ] Responsive design maintained

### Database Changes
- [ ] Connection string verified against installed drivers
- [ ] Test connection script run
- [ ] READ-ONLY mode respected (main DB)
- [ ] Query optimization considered
- [ ] Connection pooling not broken

### Documentation Changes
- [ ] CLAUDE.md updated if new patterns added
- [ ] TROUBLESHOOTING.md updated if issues solved
- [ ] This AGENTS.md updated if new guidelines needed
- [ ] README.md updated if setup changed
- [ ] API docs updated if endpoints changed

## 🎓 Learning from Past Issues

### Case Study 1: ODBC Driver Mismatch (2025-11-06)

**What Happened**:
- Backend `.env` configured with `ODBC Driver 17`
- System only had `ODBC Driver 11` installed
- Result: "Data source name not found" error
- 8+ hours of attempted fixes before root cause found

**What We Learned**:
1. Never assume "standard" configurations
2. Always verify what's actually installed
3. Document exact versions that work
4. Create test scripts for environment validation

**Prevention**:
```python
# Add to setup scripts
def verify_odbc_driver():
    import pyodbc
    required_drivers = ['SQL Server', 'ODBC Driver 11 for SQL Server',
                       'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server']
    installed = pyodbc.drivers()
    available = [d for d in required_drivers if d in installed]

    if not available:
        raise EnvironmentError(f"No SQL Server ODBC drivers found. Install one of: {required_drivers}")

    print(f"✅ Available drivers: {available}")
    return available[0]
```

### Case Study 2: API Contract Mismatch (2025-11-06)

**What Happened**:
- Backend changed from `{TCKN, ADI, SOYAD}` to `{tckn, name, age}`
- Frontend not updated, tried to access `patient.ADI`
- Result: Component crashed, blank white screen
- Backend showed 200 OK, making debugging difficult

**What We Learned**:
1. API changes must be coordinated across layers
2. TypeScript interfaces must match backend schema
3. Visual testing catches what logs don't
4. Browser DevTools Network tab shows actual responses

**Prevention**:
```typescript
// Create type guards
function isValidPatient(obj: any): obj is Patient {
  return (
    typeof obj.tckn === 'string' &&
    typeof obj.name === 'string' &&
    (obj.age === null || typeof obj.age === 'number') &&
    (obj.gender === 'E' || obj.gender === 'K' || obj.gender === null)
  );
}

// Use in components
const patients = response.data.patients.filter(isValidPatient);
if (patients.length !== response.data.patients.length) {
  console.error('Some patients have invalid format!');
}
```

## 🔄 Continuous Improvement

### When You Discover a Pattern

1. **Document it immediately** in this file
2. **Create an example** showing correct usage
3. **Add to checklist** if it should be verified
4. **Update TROUBLESHOOTING.md** if it solved an issue

### When You Solve a Novel Issue

1. **Document the solution** in TROUBLESHOOTING.md
2. **Explain the root cause** in CLAUDE.md
3. **Create prevention measures** in this file
4. **Add to test suite** (if applicable)

### When You Make a Mistake

1. **Don't hide it** - document what went wrong
2. **Explain how to detect** it in the future
3. **Add prevention steps** to checklists
4. **Share the learning** in this file

## 📚 Required Reading for New Agents

Before making changes, read:

1. **CLAUDE.md** - Project patterns and context
2. **TROUBLESHOOTING.md** - Known issues and solutions
3. **This file (AGENTS.md)** - Guidelines and best practices
4. **README.md** - Setup and architecture overview

## 🔍 Debugging Workflow

When encountering an issue:

1. **Reproduce the Issue**
   - Get exact error message
   - Identify affected component
   - Note environment (OS, versions)

2. **Gather Context**
   - Check logs (backend terminal, browser console)
   - Review recent changes (`git log`)
   - Read relevant documentation

3. **Form Hypothesis**
   - What could cause this?
   - Has this happened before? (check TROUBLESHOOTING.md)
   - What changed recently?

4. **Test Hypothesis**
   - Isolate the component
   - Test minimal reproduction
   - Verify expected vs actual behavior

5. **Document Solution**
   - Add to TROUBLESHOOTING.md
   - Update CLAUDE.md with patterns
   - Create prevention measures

## 🎯 Success Metrics

You're doing well when:

- ✅ Changes work on first try
- ✅ No assumptions made without verification
- ✅ Documentation updated with changes
- ✅ Future agents can understand your code
- ✅ Issues don't repeat
- ✅ Patterns are followed consistently

## 🆘 When Stuck

1. **Read Documentation**
   - CLAUDE.md for patterns
   - TROUBLESHOOTING.md for solutions
   - README.md for setup

2. **Verify Environment**
   - Run diagnostic commands
   - Check service status
   - Test connections

3. **Ask for Clarification**
   - Don't guess user intent
   - Confirm breaking changes
   - Validate assumptions

4. **Start Small**
   - Test minimal changes
   - Verify each step
   - Build incrementally

---

**Last Updated**: 2025-11-06

**Contribution**: When you discover new patterns or solve novel issues, please update this file to help future AI agents avoid the same pitfalls.

**Remember**: The best code is code that future developers (human or AI) can easily understand, maintain, and build upon.
