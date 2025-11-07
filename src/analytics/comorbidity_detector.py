"""Comorbidity detection and pattern analysis for clinical insights.

WARNING: This module uses placeholder table names in raw SQL queries that do not match
the actual database schema. The following table name mappings should be used:
- HASTA -> GP_HASTA_KAYIT
- TANI -> DTY_MUAYENE_EK_TANI
- RECETE -> GP_RECETE
- ILACLAR -> DTY_RECETE_ILAC

TODO: Update all raw SQL queries to use actual table names from table_names.csv
and verify column names match the actual schema.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.connection import get_session


class ComorbidityDetector:
    """Detects and analyzes comorbidity patterns in patient populations."""

    def __init__(self, session: Session):
        self.session = session

    def get_chronic_condition_mapping(self) -> Dict:
        """Define chronic conditions and their associated ICD-10 codes."""
        return {
            "Hypertension": {
                "icd10_codes": ["I10", "I11", "I12", "I13", "I15"],
                "medications": [
                    "AMLODIPINE",
                    "LISINOPRIL",
                    "ATENOLOL",
                    "METOPROLOL",
                    "HYDROCHLOROTHIAZIDE",
                ],
                "lab_markers": ["Blood Pressure"],
                "keywords": ["hipertansiyon", "yüksek tansiyon", "ht"],
            },
            "Diabetes Mellitus": {
                "icd10_codes": ["E10", "E11", "E12", "E13", "E14"],
                "medications": ["METFORMIN", "INSULIN", "GLICLAZIDE", "SITAGLIPTIN"],
                "lab_markers": ["Glucose", "HbA1c"],
                "keywords": ["diyabet", "şeker hastalığı", "dm"],
            },
            "Hyperlipidemia": {
                "icd10_codes": ["E78"],
                "medications": ["ATORVASTATIN", "SIMVASTATIN", "ROSUVASTATIN"],
                "lab_markers": [
                    "Total Cholesterol",
                    "LDL Cholesterol",
                    "HDL Cholesterol",
                    "Triglycerides",
                ],
                "keywords": ["kolesterol", "lipid", "yağ"],
            },
            "Coronary Artery Disease": {
                "icd10_codes": ["I20", "I21", "I22", "I23", "I24", "I25"],
                "medications": ["ASPIRIN", "CLOPIDOGREL", "ATENOLOL", "LISINOPRIL"],
                "lab_markers": ["Troponin", "CK-MB"],
                "keywords": ["kalp", "koroner", "anjina", "mi"],
            },
            "Chronic Kidney Disease": {
                "icd10_codes": ["N18"],
                "medications": ["ATORVASTATIN", "FAMOTIDINE", "CALCIUM CARBONATE"],
                "lab_markers": ["Creatinine", "eGFR", "BUN"],
                "keywords": ["böbrek", "nefropati", "ckd"],
            },
            "Chronic Obstructive Pulmonary Disease": {
                "icd10_codes": ["J44"],
                "medications": ["SALBUTAMOL", "BUDESONIDE", "TIOTROPIUM"],
                "lab_markers": ["SpO2", "FEV1"],
                "keywords": ["astım", "koah", "nefes"],
            },
            "Depression": {
                "icd10_codes": ["F32", "F33"],
                "medications": ["SERTRALINE", "FLUOXETINE", "ESCITALOPRAM"],
                "lab_markers": [],
                "keywords": ["depresyon", "anksiyete", "ruh"],
            },
            "Osteoporosis": {
                "icd10_codes": ["M80", "M81"],
                "medications": ["CALCIUM", "VITAMIN D", "ALENDRONATE"],
                "lab_markers": ["Vitamin D", "Calcium"],
                "keywords": ["kemik erimesi", "osteoporoz"],
            },
        }

    def detect_comorbidities_by_icd10(self) -> Dict:
        """Detect comorbidities using ICD-10 diagnosis codes."""
        condition_mapping = self.get_chronic_condition_mapping()
        reverse_mapping = {}
        for condition, data in condition_mapping.items():
            for code in data["icd10_codes"]:
                reverse_mapping[code] = condition

        query = text(
            """
            SELECT
                h.TCKN,
                t.KOD,
                t.TANI_ADI,
                t.TANI_TARIHI
            FROM HASTA h
            JOIN TANI t ON h.TCKN = t.TCKN
            WHERE t.TANI_TARIHI >= DATEADD(YEAR, -2, GETDATE())
            AND t.KOD IS NOT NULL
        """
        )

        result = self.session.execute(query).fetchall()

        # Build patient condition mapping
        patient_conditions = defaultdict(set)
        for row in result:
            condition = reverse_mapping.get(row.KOD[:3])  # Get first 3 characters of ICD-10
            if condition:
                patient_conditions[row.TCKN].add(condition)

        # Analyze comorbidity patterns
        comorbidity_matrix = defaultdict(lambda: defaultdict(int))
        condition_counts = defaultdict(int)

        for tckn, conditions in patient_conditions.items():
            for condition in conditions:
                condition_counts[condition] += 1
                for other_condition in conditions:
                    if condition != other_condition:
                        comorbidity_matrix[condition][other_condition] += 1

        # Calculate comorbidity rates
        total_patients = len(patient_conditions)
        comorbidity_rates = {}

        for condition1, conditions_dict in comorbidity_matrix.items():
            patients_with_condition1 = condition_counts[condition1]
            comorbidity_rates[condition1] = {}

            for condition2, co_occurrence_count in conditions_dict.items():
                if co_occurrence_count > 0:
                    comorbidity_rate = (co_occurrence_count / patients_with_condition1) * 100
                    comorbidity_rates[condition1][condition2] = round(comorbidity_rate, 1)

        return {
            "total_patients_analyzed": total_patients,
            "condition_prevalence": {
                condition: {
                    "patient_count": count,
                    "prevalence_percentage": round((count / total_patients) * 100, 1),
                }
                for condition, count in condition_counts.items()
            },
            "comorbidity_rates": comorbidity_rates,
            "patient_conditions": dict(patient_conditions),
        }

    def detect_comorbidities_by_medications(self) -> Dict:
        """Detect comorbidities using medication patterns."""
        condition_mapping = self.get_chronic_condition_mapping()
        reverse_mapping = {}
        for condition, data in condition_mapping.items():
            for medication in data["medications"]:
                reverse_mapping[medication.upper()] = condition

        query = text(
            """
            SELECT DISTINCT
                r.TCKN,
                UPPER(i.ILAC_ADI) as medication_name
            FROM RECETE r
            JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
            WHERE r.RECETE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
            AND i.ILAC_ADI IS NOT NULL
        """
        )

        result = self.session.execute(query).fetchall()

        # Build patient condition mapping from medications
        patient_conditions = defaultdict(set)
        medication_conditions = defaultdict(list)

        for row in result:
            medication = row.medication_name

            # Check exact matches
            if medication in reverse_mapping:
                condition = reverse_mapping[medication]
                patient_conditions[row.TCKN].add(condition)
                medication_conditions[medication].append(row.TCKN)
            else:
                # Check partial matches
                for med_key, condition in reverse_mapping.items():
                    if med_key in medication:
                        patient_conditions[row.TCKN].add(condition)
                        medication_conditions[medication].append(row.TCKN)

        return {
            "total_patients_with_medications": len(patient_conditions),
            "medication_patterns": {
                medication: {
                    "condition": reverse_mapping.get(medication, "Unknown"),
                    "patient_count": len(tckns),
                    "patients": tckns[:5],  # First 5 patients for example
                }
                for medication, tckns in medication_conditions.items()
            },
            "detected_conditions": {
                condition: {
                    "patient_count": len(tckns),
                    "medications": [
                        med
                        for med, conds in medication_conditions.items()
                        if reverse_mapping.get(med) == condition
                    ],
                }
                for condition, tckns in patient_conditions.items()
            },
        }

    def analyze_comorbidity_clusters(self) -> Dict:
        """Identify common comorbidity clusters and patterns."""
        # Get patient conditions from both ICD-10 and medications
        icd_data = self.detect_comorbidities_by_icd10()
        med_data = self.detect_comorbidities_by_medications()

        # Combine patient conditions
        all_patient_conditions = defaultdict(set)

        # Add from ICD-10 data
        for tckn, conditions in icd_data["patient_conditions"].items():
            all_patient_conditions[tckn].update(conditions)

        # Add from medication data
        for condition_data in med_data["detected_conditions"].values():
            # This is simplified - in practice you'd need to match patients
            pass

        # Find common condition combinations
        condition_combinations = Counter()
        triple_combinations = Counter()

        for tckn, conditions in all_patient_conditions.items():
            condition_list = sorted(list(conditions))

            # Count pairs
            for i in range(len(condition_list)):
                for j in range(i + 1, len(condition_list)):
                    pair = (condition_list[i], condition_list[j])
                    condition_combinations[pair] += 1

            # Count triples
            for i in range(len(condition_list)):
                for j in range(i + 1, len(condition_list)):
                    for k in range(j + 1, len(condition_list)):
                        triple = (condition_list[i], condition_list[j], condition_list[k])
                        triple_combinations[triple] += 1

        # Get top combinations
        top_pairs = condition_combinations.most_common(10)
        top_triples = triple_combinations.most_common(5)

        return {
            "total_patients_analyzed": len(all_patient_conditions),
            "common_pairs": [
                {
                    "conditions": list(pair),
                    "patient_count": count,
                    "percentage": round((count / len(all_patient_conditions)) * 100, 1),
                }
                for pair, count in top_pairs
            ],
            "common_triples": [
                {
                    "conditions": list(triple),
                    "patient_count": count,
                    "percentage": round((count / len(all_patient_conditions)) * 100, 1),
                }
                for triple, count in top_triples
            ],
            "most_complex_patients": [
                {
                    "tckn": tckn,
                    "condition_count": len(conditions),
                    "conditions": sorted(list(conditions)),
                }
                for tckn, conditions in sorted(
                    all_patient_conditions.items(), key=lambda x: len(x[1]), reverse=True
                )[:10]
            ],
        }

    def get_high_risk_comorbidity_profiles(self) -> Dict:
        """Identify patients with high-risk comorbidity combinations."""
        # Define high-risk combinations
        high_risk_combinations = [
            ("Diabetes Mellitus", "Hypertension", "Hyperlipidemia"),  # Metabolic syndrome
            ("Hypertension", "Coronary Artery Disease", "Hyperlipidemia"),  # Cardiovascular risk
            ("Diabetes Mellitus", "Chronic Kidney Disease"),  # Diabetic nephropathy risk
            ("Coronary Artery Disease", "Depression"),  # Mental health impact
            (
                "Chronic Obstructive Pulmonary Disease",
                "Coronary Artery Disease",
            ),  # Cardiopulmonary risk
        ]

        icd_data = self.detect_comorbidities_by_icd10()
        patient_conditions = icd_data["patient_conditions"]

        high_risk_patients = []

        for tckn, conditions in patient_conditions.items():
            condition_list = set(conditions)

            for risk_combo in high_risk_combinations:
                if set(risk_combo).issubset(condition_list):
                    high_risk_patients.append(
                        {
                            "tckn": tckn,
                            "risk_profile": list(risk_combo),
                            "total_conditions": len(condition_list),
                            "all_conditions": sorted(list(condition_list)),
                        }
                    )
                    break

        # Sort by number of conditions (most complex first)
        high_risk_patients.sort(key=lambda x: x["total_conditions"], reverse=True)

        return {
            "total_high_risk_patients": len(high_risk_patients),
            "high_risk_combinations": [
                {"combination": list(combo), "description": self._get_risk_description(combo)}
                for combo in high_risk_combinations
            ],
            "patients": high_risk_patients[:20],  # Top 20 patients
            "risk_distribution": Counter(
                tuple(sorted(patient["risk_profile"])) for patient in high_risk_patients
            ),
        }

    def _get_risk_description(self, combination: Tuple) -> str:
        """Get description for risk combination."""
        descriptions = {
            (
                "Diabetes Mellitus",
                "Hypertension",
                "Hyperlipidemia",
            ): "Metabolic Syndrome - High cardiovascular risk",
            (
                "Hypertension",
                "Coronary Artery Disease",
                "Hyperlipidemia",
            ): "Established Cardiovascular Disease",
            ("Diabetes Mellitus", "Chronic Kidney Disease"): "Diabetic Nephropathy Risk",
            ("Coronary Artery Disease", "Depression"): "Post-MI Depression Risk",
            (
                "Chronic Obstructive Pulmonary Disease",
                "Coronary Artery Disease",
            ): "Cardiopulmonary Disease",
        }
        return descriptions.get(tuple(sorted(combination)), "Multiple Chronic Conditions")

    def generate_comprehensive_comorbidity_report(self) -> Dict:
        """Generate comprehensive comorbidity analysis report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "icd10_based_analysis": self.detect_comorbidities_by_icd10(),
            "medication_based_analysis": self.detect_comorbidities_by_medications(),
            "comorbidity_clusters": self.analyze_comorbidity_clusters(),
            "high_risk_profiles": self.get_high_risk_comorbidity_profiles(),
        }


def get_comorbidity_analysis() -> Dict:
    """Convenience function to get comorbidity analysis."""
    with get_session() as session:
        detector = ComorbidityDetector(session)
        return detector.generate_comprehensive_comorbidity_report()


if __name__ == "__main__":
    # Example usage
    comorbidity_report = get_comorbidity_analysis()
    print("Comorbidity Analysis Report")
    print("=" * 35)
    print(f"Generated: {comorbidity_report['generated_at']}")
    print(
        f"Total Patients: {comorbidity_report['icd10_based_analysis']['total_patients_analyzed']}"
    )
    print(
        f"High Risk Patients: {comorbidity_report['high_risk_profiles']['total_high_risk_patients']}"
    )
