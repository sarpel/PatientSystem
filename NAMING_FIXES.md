# Naming Convention Fixes

## Overview
This document details all naming convention issues found and fixed in the PatientSystem codebase. The issues stemmed from discrepancies between code references and actual database table/column names as defined in `table_names.csv` and SQLAlchemy models.

## Issues Fixed

### 1. Column Name Issues in Clinical Modules

#### TC_KIMLIK_NO → HASTA_KIMLIK_NO
**Location:** `src/clinical/patient_summarizer.py` line 93  
**Issue:** Code referenced `patient.TC_KIMLIK_NO` which doesn't exist  
**Fix:** Changed to `patient.HASTA_KIMLIK_NO` to match Patient model definition  
**Impact:** Prevents AttributeError when accessing patient national ID

#### KAN_GRUBU Access Path
**Location:** `src/clinical/patient_summarizer.py` line 94  
**Issue:** Code referenced `patient.KAN_GRUBU` directly on Patient model  
**Fix:** Changed to `patient.demographics.KAN_GRUBU` as blood type is in PatientDemographics model  
**Impact:** Correct access to blood type information

#### SIGARA → SIGARA_KULLANIMI
**Locations:**
- `src/clinical/patient_summarizer.py` line 107
- `src/clinical/diagnosis_engine.py` line 208
- `src/clinical/treatment_engine.py` line 382

**Issue:** Code referenced `demographics.SIGARA` which doesn't exist  
**Fix:** Changed to `demographics.SIGARA_KULLANIMI` to match PatientDemographics model  
**Impact:** Correct access to smoking status information

### 2. Non-existent Attribute References

#### ILAC_ALERJISI (Drug Allergy)
**Locations:**
- `src/clinical/patient_summarizer.py` lines 199-210
- `src/clinical/drug_interaction.py` lines 385-402
- `src/clinical/treatment_engine.py` line 379

**Issue:** Code referenced `patient.ILAC_ALERJISI` and `demographics.ILAC_ALERJISI` which don't exist in either model  
**Fix:** Removed all references to these non-existent attributes, replaced with empty lists and TODO comments  
**Correct Approach:** Allergy information should be retrieved from `DTY_HASTA_OZLUK_ALERJI` table  
**Impact:** Prevents AttributeError, documents proper implementation path

### 3. Table Name Issues in Database Inspector

#### HRC_ILAC → HRC_ILAC_KULLANIM_VARSAYILANLARI
**Location:** `src/database/inspector.py` line 295  
**Issue:** Code referenced `HRC_ILAC` table which doesn't exist  
**Fix:** Changed to `HRC_ILAC_KULLANIM_VARSAYILANLARI` which exists in database  
**Impact:** Correct table reference in critical tables summary

#### GP_HYP → GP_HYP_FIZIKSEL_BULGULAR
**Location:** `src/database/inspector.py` line 301  
**Issue:** Code referenced `GP_HYP` table which doesn't exist  
**Fix:** Changed to `GP_HYP_FIZIKSEL_BULGULAR` which exists in database  
**Impact:** Correct table reference for chronic disease tracking

### 4. Analytics Module Table Names (Documentation Only)

The following modules use placeholder table names in raw SQL queries that don't match actual schema:

#### src/analytics/lab_trends.py
**Incorrect Table Names:**
- `TETKIK` → Should be `HRC_DTY_LAB_SONUC` or `HRC_DTY_LAB_SONUCLARI`
- `HASTA` → Should be `GP_HASTA_KAYIT`

**Incorrect Column Names:**
- `TCKN` → Should be `HASTA_KIMLIK_NO`
- `ADI` → Should be `AD`
- `SOYADI` → Should be `SOYAD`

#### src/analytics/medication_adherence.py
**Incorrect Table Names:**
- `RECETE` → Should be `GP_RECETE`
- `ILACLAR` → Should be `DTY_RECETE_ILAC`
- `HASTA` → Should be `GP_HASTA_KAYIT`

#### src/analytics/comorbidity_detector.py
**Incorrect Table Names:**
- `HASTA` → Should be `GP_HASTA_KAYIT`
- `TANI` → Should be `DTY_MUAYENE_EK_TANI`
- `RECETE` → Should be `GP_RECETE`
- `ILACLAR` → Should be `DTY_RECETE_ILAC`

#### src/analytics/visit_patterns.py
**Incorrect Table Names:**
- `MUAYENE` → Should be `GP_MUAYENE`

#### src/gui/widgets/lab_charts.py
**Incorrect Table Names:**
- `TETKIK` → Should be `HRC_DTY_LAB_SONUC` or `HRC_DTY_LAB_SONUCLARI`

**Action Taken:** Added WARNING comments in module docstrings with correct table name mappings and TODO items

## Database Schema Reference

### Core Patient Tables
- `GP_HASTA_KAYIT` - Patient registration (main patient record)
- `GP_HASTA_OZLUK` - Patient demographics and lifestyle
- `DTY_HASTA_OZLUK_ALERJI` - Patient allergies

### Clinical Data Tables
- `GP_MUAYENE` - Patient examinations/visits
- `GP_HASTA_KABUL` - Patient admissions
- `DTY_MUAYENE_EK_TANI` - Additional diagnoses

### Prescription Tables
- `GP_RECETE` - Prescriptions
- `DTY_RECETE_ILAC` - Prescription medications

### Laboratory Tables
- `HRC_DTY_LAB_SONUC` - Lab results
- `HRC_DTY_LAB_SONUC_PARAMETRELER` - Lab result parameters
- `HRC_DTY_LAB_SONUCLARI` - Lab results (alternative)

### Chronic Disease Tables
- `GP_HYP_FIZIKSEL_BULGULAR` - Hypertension physical findings
- `GP_DIYABET` - Diabetes tracking
- `GP_KRONIK_HASTALIKLAR` - Chronic diseases

### Reference Tables
- `LST_ICD10` - ICD-10 diagnosis codes
- `LST_KAN_GRUBU` - Blood type codes
- `LST_SIGARA_KULLANIMI` - Smoking status codes

## Column Naming Conventions

### Database (SQL Server)
- Uses `UPPERCASE_SNAKE_CASE` for all column names
- Turkish naming: `HASTA_KIMLIK_NO`, `DOGUM_TARIHI`, `AD`, `SOYAD`

### Python Models (SQLAlchemy)
- Column attributes use same names as database: `HASTA_KIMLIK_NO`, `AD`, `SOYAD`
- Property methods use lowercase_snake_case: `full_name`, `age`, `bmi`

### API JSON Responses
- Uses lowercase with no underscores: `tckn`, `name`, `age`, `gender`
- Camel case not used for consistency with Python naming

### TypeScript Frontend
- Uses camelCase for variables: `patientId`, `birthDate`
- API interfaces match API JSON format: `tckn`, `name`, etc.

## Testing Results

All fixes have been validated:
- ✅ All Python files compile without syntax errors
- ✅ Column references match model definitions
- ✅ Table references match table_names.csv
- ✅ No AttributeError exceptions on fixed attributes

## Future Work

### High Priority
1. Implement proper allergy retrieval from `DTY_HASTA_OZLUK_ALERJI` table
2. Update analytics module SQL queries to use correct table names
3. Verify all column names in analytics SQL queries match actual schema

### Medium Priority
1. Create database schema documentation with all column names
2. Add unit tests to validate model attribute access patterns
3. Create migration guide for updating raw SQL queries

### Low Priority
1. Consider creating database views with simplified names for analytics queries
2. Standardize all raw SQL queries to use SQLAlchemy ORM instead

## References

- `table_names.csv` - Complete list of all database tables (653 tables)
- `src/models/` - SQLAlchemy model definitions with correct column names
- `.github/copilot-instructions.md` - Naming convention guidelines

## Change Log

- **2024-11-07**: Initial fixes for column and table naming issues
  - Fixed 4 column name issues in clinical modules
  - Fixed 2 table name issues in database inspector
  - Added documentation warnings for 5 analytics modules
  - Added documentation warning for 1 GUI module
