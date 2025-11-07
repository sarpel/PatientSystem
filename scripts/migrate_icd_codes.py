"""
Migration script to move ICD-10 codes from hardcoded dictionary to app database.
This script extracts the hardcoded ICD mappings and populates the SQLite database.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.database.app_database import get_app_db_session, ICDCode


# Hardcoded ICD-10 mappings from diagnosis_engine.py (lines 120-167)
ICD_MAPPINGS = {
    # Cardiovascular
    "Hypertension": "I10",
    "Myocardial Infarction": "I21",
    "Heart Failure": "I50",
    "Atrial Fibrillation": "I48",
    "Angina Pectoris": "I20",

    # Respiratory
    "Pneumonia": "J18",
    "Asthma": "J45",
    "COPD": "J44",
    "Bronchitis": "J40",
    "Pulmonary Embolism": "I26",

    # Gastrointestinal
    "Gastritis": "K29",
    "Peptic Ulcer": "K27",
    "Cholecystitis": "K81",
    "Appendicitis": "K35",
    "Pancreatitis": "K85",

    # Endocrine
    "Diabetes Mellitus Type 2": "E11",
    "Diabetes Mellitus Type 1": "E10",
    "Hyperthyroidism": "E05",
    "Hypothyroidism": "E03",

    # Neurological
    "Stroke": "I64",
    "Migraine": "G43",
    "Epilepsy": "G40",
    "Parkinson's Disease": "G20",
    "Multiple Sclerosis": "G35",

    # Renal
    "Chronic Kidney Disease": "N18",
    "Acute Kidney Injury": "N17",
    "Urinary Tract Infection": "N39.0",
    "Nephrolithiasis": "N20",

    # Musculoskeletal
    "Osteoarthritis": "M19",
    "Rheumatoid Arthritis": "M06",
    "Osteoporosis": "M81",
    "Gout": "M10",

    # Infectious
    "Sepsis": "A41",
    "Tuberculosis": "A15",
    "HIV Disease": "B20",
    "Influenza": "J11",

    # Hematological
    "Anemia": "D64",
    "Iron Deficiency Anemia": "D50",
    "Thrombocytopenia": "D69.6",
    "Leukemia": "C95",

    # Psychiatric
    "Major Depression": "F32",
    "Anxiety Disorder": "F41",
    "Bipolar Disorder": "F31",
    "Schizophrenia": "F20",

    # Dermatological
    "Psoriasis": "L40",
    "Eczema": "L30",
    "Cellulitis": "L03",

    # Oncological
    "Lung Cancer": "C34",
    "Breast Cancer": "C50",
    "Colorectal Cancer": "C18",
    "Prostate Cancer": "C61",

    # Other Common
    "Obesity": "E66",
    "Dyslipidemia": "E78",
    "Vitamin D Deficiency": "E55",
    "Dehydration": "E86",
    "Fever of Unknown Origin": "R50.9",
}


# Turkish translations for common diagnoses
TURKISH_TRANSLATIONS = {
    "Hypertension": "Hipertansiyon",
    "Diabetes Mellitus Type 2": "Tip 2 Diyabet",
    "Pneumonia": "Zatürre",
    "Gastritis": "Gastrit",
    "Anemia": "Anemi",
    "Migraine": "Migren",
    "Asthma": "Astım",
    "Obesity": "Obezite",
    "Depression": "Depresyon",
    "Anxiety": "Anksiyete",
}


def categorize_diagnosis(diagnosis: str) -> str:
    """Categorize diagnosis based on keywords."""
    diagnosis_lower = diagnosis.lower()

    if any(word in diagnosis_lower for word in ["heart", "cardiac", "hypertension", "angina", "infarction"]):
        return "Cardiovascular"
    elif any(word in diagnosis_lower for word in ["lung", "pneumonia", "asthma", "copd", "respiratory"]):
        return "Respiratory"
    elif any(word in diagnosis_lower for word in ["gastro", "peptic", "cholecyst", "appendic", "pancrea"]):
        return "Gastrointestinal"
    elif any(word in diagnosis_lower for word in ["diabetes", "thyroid", "endocrine"]):
        return "Endocrine"
    elif any(word in diagnosis_lower for word in ["stroke", "neuro", "epilep", "parkinson", "sclerosis"]):
        return "Neurological"
    elif any(word in diagnosis_lower for word in ["kidney", "renal", "urinary", "nephro"]):
        return "Renal"
    elif any(word in diagnosis_lower for word in ["arthritis", "bone", "osteo", "gout", "musculo"]):
        return "Musculoskeletal"
    elif any(word in diagnosis_lower for word in ["sepsis", "infection", "tubercul", "hiv", "flu"]):
        return "Infectious"
    elif any(word in diagnosis_lower for word in ["anemia", "blood", "hematolog", "leukemia", "thrombo"]):
        return "Hematological"
    elif any(word in diagnosis_lower for word in ["depression", "anxiety", "bipolar", "schizo", "psychiatric"]):
        return "Psychiatric"
    elif any(word in diagnosis_lower for word in ["skin", "dermat", "psoriasis", "eczema", "cellulitis"]):
        return "Dermatological"
    elif any(word in diagnosis_lower for word in ["cancer", "oncolog", "tumor", "malign"]):
        return "Oncological"
    else:
        return "Other"


def migrate_icd_codes():
    """Migrate ICD-10 codes to app database."""
    logger.info("Starting ICD-10 code migration")

    try:
        with get_app_db_session() as session:
            # Check if codes already exist
            existing_count = session.query(ICDCode).count()
            if existing_count > 0:
                logger.warning(f"Database already contains {existing_count} ICD codes")
                response = input("Do you want to clear existing codes and re-migrate? (yes/no): ")
                if response.lower() == "yes":
                    session.query(ICDCode).delete()
                    session.commit()
                    logger.info("Cleared existing ICD codes")
                else:
                    logger.info("Migration cancelled")
                    return

            # Insert ICD codes
            codes_added = 0
            for diagnosis, code in ICD_MAPPINGS.items():
                icd_code = ICDCode(
                    code=code,
                    diagnosis_name_en=diagnosis,
                    diagnosis_name_tr=TURKISH_TRANSLATIONS.get(diagnosis),
                    category=categorize_diagnosis(diagnosis),
                    icd_version="ICD-10",
                    is_active=True,
                )
                session.add(icd_code)
                codes_added += 1

            session.commit()
            logger.info(f"Successfully migrated {codes_added} ICD-10 codes to app database")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate_icd_codes()
