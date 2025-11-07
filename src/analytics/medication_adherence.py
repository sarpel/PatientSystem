"""Medication adherence analytics for tracking patient compliance.

WARNING: This module uses placeholder table names in raw SQL queries that do not match
the actual database schema. The following table name mappings should be used:
- RECETE -> GP_RECETE
- ILACLAR -> DTY_RECETE_ILAC
- HASTA -> GP_HASTA_KAYIT

TODO: Update all raw SQL queries to use actual table names from table_names.csv
and verify column names match the actual schema.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.connection import get_session


class MedicationAdherenceAnalyzer:
    """Analyzes medication adherence patterns and compliance rates."""

    def __init__(self, session: Session):
        self.session = session

    def get_prescription_adherence_rate(self, months: int = 6) -> Dict:
        """Calculate overall prescription adherence rates."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        query = text(
            """
            WITH Prescriptions AS (
                SELECT
                    r.TCKN,
                    r.RECETE_TARIHI,
                    i.ILAC_ADI,
                    i.KULLANIM_DOZU,
                    i.KULLANIM_SURESI,
                    DATEDIFF(day, r.RECETE_TARIHI, GETDATE()) as days_since_prescription
                FROM RECETE r
                JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
                WHERE r.RECETE_TARIHI BETWEEN :start_date AND :end_date
            ),
            RefillAnalysis AS (
                SELECT
                    TCKN,
                    ILAC_ADI,
                    COUNT(*) as prescription_count,
                    AVG(DATEDIFF(day, RECETE_TARIHI,
                        LEAD(RECETE_TARIHI) OVER (PARTITION BY TCKN, ILAC_ADI ORDER BY RECETE_TARIHI)
                    )) as avg_days_between_prescriptions
                FROM Prescriptions
                GROUP BY TCKN, ILAC_ADI
                HAVING COUNT(*) > 1
            )
            SELECT
                COUNT(*) as total_prescriptions,
                COUNT(DISTINCT TCKN) as unique_patients,
                COUNT(DISTINCT ILAC_ADI) as unique_medications,
                AVG(CAST(avg_days_between_prescriptions AS FLOAT)) as avg_refill_interval_days
            FROM RefillAnalysis
        """
        )

        result = self.session.execute(
            query, {"start_date": start_date, "end_date": end_date}
        ).fetchone()

        return {
            "analysis_period_months": months,
            "total_prescriptions": result.total_prescriptions or 0,
            "unique_patients": result.unique_patients or 0,
            "unique_medications": result.unique_medications or 0,
            "average_refill_interval_days": round(result.avg_refill_interval_days or 0, 1),
        }

    def get_chronic_medication_adherence(self) -> Dict:
        """Analyze adherence for chronic medications (antihypertensives, diabetes, etc.)."""
        # Define chronic medication categories (simplified)
        chronic_medications = [
            "METFORMIN",
            "INSULIN",
            "GLICLAZIDE",
            "AMLODIPINE",
            "LISINOPRIL",
            "ATENOLOL",
            "SIMVASTATIN",
            "ATORVASTATIN",
        ]

        chronic_conditions = {
            "Diabetes": ["METFORMIN", "INSULIN", "GLICLAZIDE"],
            "Hypertension": ["AMLODIPINE", "LISINOPRIL", "ATENOLOL"],
            "Hyperlipidemia": ["SIMVASTATIN", "ATORVASTATIN"],
        }

        results = {}

        for condition, medications in chronic_conditions.items():
            query = text(
                """
                SELECT
                    COUNT(DISTINCT r.TCKN) as patients_on_medication,
                    COUNT(*) as total_prescriptions,
                    AVG(CAST(DATEDIFF(day,
                        r.RECETE_TARIHI,
                        LEAD(r.RECETE_TARIHI) OVER (PARTITION BY r.TCKN ORDER BY r.RECETE_TARIHI)
                    ) AS FLOAT)) as avg_days_between_prescriptions
                FROM RECETE r
                JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
                WHERE r.RECETE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
                AND UPPER(i.ILAC_ADI) IN :medications
            """
            )

            result = self.session.execute(query, {"medications": medications}).fetchone()

            results[condition] = {
                "patients_on_medication": result.patients_on_medication or 0,
                "total_prescriptions": result.total_prescriptions or 0,
                "average_days_between_prescriptions": round(
                    result.avg_days_between_prescriptions or 0, 1
                ),
                "medications_tracked": medications,
            }

        return results

    def get_medication_persistence_analysis(self) -> Dict:
        """Analyze how long patients stay on their medications."""
        query = text(
            """
            WITH PatientMedicationPeriods AS (
                SELECT
                    r.TCKN,
                    i.ILAC_ADI,
                    r.RECETE_TARIHI as start_date,
                    LEAD(r.RECETE_TARIHI) OVER (
                        PARTITION BY r.TCKN, i.ILAC_ADI
                        ORDER BY r.RECETE_TARIHI
                    ) as next_prescription,
                    ROW_NUMBER() OVER (
                        PARTITION BY r.TCKN, i.ILAC_ADI
                        ORDER BY r.RECETE_TARIHI
                    ) as prescription_number
                FROM RECETE r
                JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
                WHERE r.RECETE_TARIHI >= DATEADD(YEAR, -2, GETDATE())
            ),
            MedicationCourses AS (
                SELECT
                    TCKN,
                    ILAC_ADI,
                    MIN(start_date) as first_prescription,
                    MAX(start_date) as last_prescription,
                    COUNT(*) as total_prescriptions,
                    DATEDIFF(day, MIN(start_date), MAX(start_date)) as persistence_days
                FROM PatientMedicationPeriods
                GROUP BY TCKN, ILAC_ADI
            )
            SELECT
                COUNT(*) as total_medication_courses,
                COUNT(DISTINCT TCKN) as unique_patients,
                COUNT(DISTINCT ILAC_ADI) as unique_medications,
                AVG(CAST(total_prescriptions AS FLOAT)) as avg_prescriptions_per_course,
                AVG(CAST(persistence_days AS FLOAT)) as avg_persistence_days
            FROM MedicationCourses
        """
        )

        result = self.session.execute(query).fetchone()

        # Categorize persistence duration
        persistence_query = text(
            """
            WITH MedicationCourses AS (
                SELECT
                    TCKN,
                    ILAC_ADI,
                    COUNT(*) as total_prescriptions,
                    DATEDIFF(day, MIN(start_date), MAX(start_date)) as persistence_days
                FROM (
                    SELECT
                        r.TCKN,
                        i.ILAC_ADI,
                        r.RECETE_TARIHI as start_date
                    FROM RECETE r
                    JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
                    WHERE r.RECETE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
                ) base_data
                GROUP BY TCKN, ILAC_ADI
            )
            SELECT
                CASE
                    WHEN persistence_days < 30 THEN 'Less than 1 month'
                    WHEN persistence_days < 90 THEN '1-3 months'
                    WHEN persistence_days < 180 THEN '3-6 months'
                    WHEN persistence_days < 365 THEN '6-12 months'
                    ELSE 'More than 1 year'
                END as persistence_category,
                COUNT(*) as course_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM MedicationCourses), 2) as percentage
            FROM MedicationCourses
            GROUP BY
                CASE
                    WHEN persistence_days < 30 THEN 'Less than 1 month'
                    WHEN persistence_days < 90 THEN '1-3 months'
                    WHEN persistence_days < 180 THEN '3-6 months'
                    WHEN persistence_days < 365 THEN '6-12 months'
                    ELSE 'More than 1 year'
                END
            ORDER BY
                CASE
                    WHEN persistence_days < 30 THEN 1
                    WHEN persistence_days < 90 THEN 2
                    WHEN persistence_days < 180 THEN 3
                    WHEN persistence_days < 365 THEN 4
                    ELSE 5
                END
        """
        )

        persistence_result = self.session.execute(persistence_query).fetchall()

        return {
            "summary": {
                "total_medication_courses": result.total_medication_courses or 0,
                "unique_patients": result.unique_patients or 0,
                "unique_medications": result.unique_medications or 0,
                "avg_prescriptions_per_course": round(result.avg_prescriptions_per_course or 0, 1),
                "avg_persistence_days": round(result.avg_persistence_days or 0, 1),
            },
            "persistence_distribution": [
                {
                    "category": row.persistence_category,
                    "course_count": row.course_count,
                    "percentage": row.percentage,
                }
                for row in persistence_result
            ],
        }

    def get_high_risk_non_adherence_patients(self) -> Dict:
        """Identify patients with potential non-adherence issues."""
        query = text(
            """
            WITH PatientMedicationGaps AS (
                SELECT
                    r.TCKN,
                    i.ILAC_ADI,
                    r.RECETE_TARIHI,
                    LEAD(r.RECETE_TARIHI) OVER (
                        PARTITION BY r.TCKN, i.ILAC_ADI
                        ORDER BY r.RECETE_TARIHI
                    ) as next_prescription,
                    DATEDIFF(day, r.RECETE_TARIHI,
                        LEAD(r.RECETE_TARIHI) OVER (
                            PARTITION BY r.TCKN, i.ILAC_ADI
                            ORDER BY r.RECETE_TARIHI
                        )
                    ) as days_between_prescriptions
                FROM RECETE r
                JOIN ILACLAR i ON r.RECETE_ID = i.RECETE_ID
                WHERE r.RECETE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
            ),
            RiskAnalysis AS (
                SELECT
                    TCKN,
                    ILAC_ADI,
                    COUNT(*) as total_prescriptions,
                    AVG(CAST(days_between_prescriptions AS FLOAT)) as avg_gap_days,
                    MAX(days_between_prescriptions) as max_gap_days,
                    COUNT(*) FILTER (WHERE days_between_prescriptions > 90) as long_gaps_count
                FROM PatientMedicationGaps
                WHERE days_between_prescriptions IS NOT NULL
                GROUP BY TCKN, ILAC_ADI
                HAVING COUNT(*) >= 2  -- At least 2 prescriptions
            )
            SELECT TOP 20
                TCKN,
                ILAC_ADI,
                total_prescriptions,
                avg_gap_days,
                max_gap_days,
                long_gaps_count
            FROM RiskAnalysis
            WHERE avg_gap_days > 60 OR long_gaps_count > 0
            ORDER BY avg_gap_days DESC, long_gaps_count DESC
        """
        )

        result = self.session.execute(query).fetchall()

        # Get patient names
        if result:
            tckns = [row.TCKN for row in result]
            patient_query = text(
                """
                SELECT TCKN, ADI, SOYADI
                FROM HASTA
                WHERE TCKN IN :tckns
            """
            )

            patients = {
                row.TCKN: f"{row.ADI} {row.SOYADI}"
                for row in self.session.execute(patient_query, {"tckns": tckns}).fetchall()
            }
        else:
            patients = {}

        return {
            "high_risk_patients": [
                {
                    "tckn": row.TCKN,
                    "patient_name": patients.get(row.TCKN, "Unknown"),
                    "medication": row.ILAC_ADI,
                    "total_prescriptions": row.total_prescriptions,
                    "average_gap_days": round(row.avg_gap_days or 0, 1),
                    "maximum_gap_days": row.max_gap_days or 0,
                    "long_gaps_count": row.long_gaps_count or 0,
                }
                for row in result
            ],
            "total_high_risk_patients": len(result),
            "analysis_date": datetime.now().isoformat(),
        }

    def generate_comprehensive_adherence_report(self) -> Dict:
        """Generate comprehensive medication adherence report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "prescription_adherence": self.get_prescription_adherence_rate(),
            "chronic_medication_adherence": self.get_chronic_medication_adherence(),
            "medication_persistence": self.get_medication_persistence_analysis(),
            "high_risk_patients": self.get_high_risk_non_adherence_patients(),
        }


def get_medication_adherence_analysis(tckn: Optional[str] = None) -> Dict:
    """Convenience function to get medication adherence analysis."""
    with get_session() as session:
        analyzer = MedicationAdherenceAnalyzer(session)
        return analyzer.generate_comprehensive_adherence_report()


if __name__ == "__main__":
    # Example usage
    adherence = get_medication_adherence_analysis()
    print("Medication Adherence Analysis Report")
    print("=" * 45)
    print(f"Generated: {adherence['generated_at']}")
    print(f"Total Prescriptions: {adherence['prescription_adherence']['total_prescriptions']}")
    print(f"High Risk Patients: {adherence['high_risk_patients']['total_high_risk_patients']}")
