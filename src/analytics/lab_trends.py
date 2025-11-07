"""Laboratory trend analytics for longitudinal patient monitoring.

WARNING: This module uses placeholder table names in raw SQL queries that do not match
the actual database schema. The following table name mappings should be used:
- TETKIK -> HRC_DTY_LAB_SONUC or HRC_DTY_LAB_SONUCLARI
- HASTA -> GP_HASTA_KAYIT
- Patient columns: TCKN should be HASTA_KIMLIK_NO, ADI -> AD, SOYADI -> SOYAD

TODO: Update all raw SQL queries to use actual table names from table_names.csv
and verify column names match the actual schema.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.connection import get_session


class LabTrendAnalyzer:
    """Analyzes laboratory test trends and provides clinical insights."""

    def __init__(self, session: Session):
        self.session = session

    def get_common_labs_trend_analysis(self, months: int = 12) -> Dict:
        """Analyze trends for common laboratory tests."""
        common_labs = [
            "Hemoglobin",
            "Hematocrit",
            "White Blood Cell",
            "Platelet Count",
            "Glucose",
            "HbA1c",
            "Creatinine",
            "ALT",
            "AST",
            "Total Cholesterol",
            "LDL Cholesterol",
            "HDL Cholesterol",
            "Triglycerides",
        ]

        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        results = {}

        for lab_name in common_labs:
            query = text(
                """
                SELECT
                    t.TEST_ADI,
                    t.SONUC,
                    t.BIRIM,
                    t.TEST_TARIHI,
                    t.NORMAL_MIN,
                    t.NORMAL_MAX,
                    h.TCKN,
                    h.ADI as patient_name,
                    h.SOYADI as patient_surname
                FROM TETKIK t
                JOIN HASTA h ON t.TCKN = h.TCKN
                WHERE t.TEST_ADI LIKE :lab_name
                AND t.TEST_TARIHI BETWEEN :start_date AND :end_date
                AND t.SONUC IS NOT NULL
                AND TRY_CAST(t.SONUC AS FLOAT) IS NOT NULL
                ORDER BY t.TEST_TARIHI DESC
            """
            )

            lab_data = self.session.execute(
                query, {"lab_name": f"%{lab_name}%", "start_date": start_date, "end_date": end_date}
            ).fetchall()

            if lab_data:
                results[lab_name] = self._analyze_lab_trends(lab_data, lab_name)

        return {
            "analysis_period_months": months,
            "lab_trends": results,
            "total_labs_analyzed": len(results),
        }

    def _analyze_lab_trends(self, lab_data: List, lab_name: str) -> Dict:
        """Analyze trends for a specific laboratory test."""
        try:
            # Extract numeric values
            numeric_values = []
            for row in lab_data:
                try:
                    value = float(str(row.SONUC).replace(",", "."))
                    numeric_values.append(value)
                except (ValueError, TypeError):
                    continue

            if not numeric_values:
                return {"error": "No valid numeric values found"}

            # Calculate statistics
            latest_value = numeric_values[0]
            oldest_value = numeric_values[-1]
            mean_value = statistics.mean(numeric_values)
            median_value = statistics.median(numeric_values)

            # Trend analysis
            if len(numeric_values) >= 3:
                # Simple linear regression for trend
                x_values = list(range(len(numeric_values)))
                n = len(numeric_values)
                sum_x = sum(x_values)
                sum_y = sum(numeric_values)
                sum_xy = sum(x * y for x, y in zip(x_values, numeric_values))
                sum_x2 = sum(x * x for x in x_values)

                if (n * sum_x2 - sum_x**2) != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                    trend_direction = (
                        "improving" if slope < 0 else "worsening" if slope > 0 else "stable"
                    )
                else:
                    slope = 0
                    trend_direction = "stable"
            else:
                slope = 0
                trend_direction = "insufficient_data"

            # Abnormal value analysis
            sample_row = lab_data[0]
            normal_min = (
                float(str(sample_row.NORMAL_MIN).replace(",", "."))
                if sample_row.NORMAL_MIN
                else None
            )
            normal_max = (
                float(str(sample_row.NORMAL_MAX).replace(",", "."))
                if sample_row.NORMAL_MAX
                else None
            )

            abnormal_count = 0
            for i, row in enumerate(lab_data):
                try:
                    value = float(str(row.SONUC).replace(",", "."))
                    if normal_min is not None and normal_max is not None:
                        if value < normal_min or value > normal_max:
                            abnormal_count += 1
                except (ValueError, TypeError):
                    continue

            abnormal_percentage = (
                (abnormal_count / len(numeric_values)) * 100 if numeric_values else 0
            )

            # Patient analysis
            unique_patients = len(set(row.TCKN for row in lab_data))

            return {
                "test_name": lab_name,
                "unit": sample_row.BIRIM,
                "statistics": {
                    "latest_value": round(latest_value, 2),
                    "oldest_value": round(oldest_value, 2),
                    "mean_value": round(mean_value, 2),
                    "median_value": round(median_value, 2),
                    "change_from_oldest": round(latest_value - oldest_value, 2),
                    "percent_change": (
                        round(((latest_value - oldest_value) / oldest_value) * 100, 1)
                        if oldest_value != 0
                        else 0
                    ),
                },
                "trend_analysis": {
                    "direction": trend_direction,
                    "slope": round(slope, 4),
                    "sample_size": len(numeric_values),
                },
                "normal_range": (
                    {"min": normal_min, "max": normal_max}
                    if normal_min is not None and normal_max is not None
                    else None
                ),
                "abnormal_rate": {
                    "abnormal_count": abnormal_count,
                    "total_tests": len(numeric_values),
                    "abnormal_percentage": round(abnormal_percentage, 1),
                },
                "patient_data": {
                    "unique_patients": unique_patients,
                    "total_measurements": len(numeric_values),
                },
            }

        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def get_patient_lab_trends(self, tckn: str, months: int = 12) -> Dict:
        """Get detailed lab trend analysis for a specific patient."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        query = text(
            """
            SELECT
                t.TEST_ADI,
                t.SONUC,
                t.BIRIM,
                t.TEST_TARIHI,
                t.NORMAL_MIN,
                t.NORMAL_MAX
            FROM TETKIK t
            WHERE t.TCKN = :tckn
            AND t.TEST_TARIHI BETWEEN :start_date AND :end_date
            AND t.SONUC IS NOT NULL
            AND TRY_CAST(t.SONUC AS FLOAT) IS NOT NULL
            ORDER BY t.TEST_ADI, t.TEST_TARIHI
        """
        )

        result = self.session.execute(
            query, {"tckn": tckn, "start_date": start_date, "end_date": end_date}
        ).fetchall()

        # Group by test name
        lab_tests = {}
        for row in result:
            test_name = row.TEST_ADI
            if test_name not in lab_tests:
                lab_tests[test_name] = []
            lab_tests[test_name].append(row)

        # Analyze each test
        analysis = {}
        for test_name, test_data in lab_tests.items():
            if len(test_data) >= 2:  # Only analyze tests with multiple measurements
                analysis[test_name] = self._analyze_lab_trends(test_data, test_name)

        return {
            "patient_tckn": tckn,
            "analysis_period_months": months,
            "lab_trends": analysis,
            "total_tests_analyzed": len(analysis),
        }

    def get_critical_lab_values_alert(self, hours: int = 24) -> Dict:
        """Identify critical laboratory values from recent tests."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Define critical value thresholds (simplified)
        critical_thresholds = {
            "Glucose": {"low": 40, "high": 500, "unit": "mg/dL"},
            "Creatinine": {"high": 3.0, "unit": "mg/dL"},
            "Hemoglobin": {"low": 7.0, "unit": "g/dL"},
            "Platelet Count": {"low": 20000, "high": 1000000, "unit": "K/uL"},
            "White Blood Cell": {"low": 1000, "high": 100000, "unit": "K/uL"},
            "Potassium": {"low": 2.5, "high": 7.0, "unit": "mmol/L"},
            "Sodium": {"low": 120, "high": 160, "unit": "mmol/L"},
        }

        query = text(
            """
            SELECT
                t.TEST_ADI,
                t.SONUC,
                t.BIRIM,
                t.TEST_TARIHI,
                t.NORMAL_MIN,
                t.NORMAL_MAX,
                h.TCKN,
                h.ADI as patient_name,
                h.SOYADI as patient_surname,
                h.TELEFON
            FROM TETKIK t
            JOIN HASTA h ON t.TCKN = h.TCKN
            WHERE t.TEST_TARIHI >= :cutoff_time
            AND t.SONUC IS NOT NULL
            AND TRY_CAST(t.SONUC AS FLOAT) IS NOT NULL
            ORDER BY t.TEST_TARIHI DESC
        """
        )

        result = self.session.execute(query, {"cutoff_time": cutoff_time}).fetchall()

        critical_values = []

        for row in result:
            try:
                lab_name = row.TEST_ADI
                value = float(str(row.SONUC).replace(",", "."))

                # Check against critical thresholds
                for critical_test, thresholds in critical_thresholds.items():
                    if critical_test.lower() in lab_name.lower():
                        is_critical = False
                        severity = "moderate"
                        reason = ""

                        if "low" in thresholds and value < thresholds["low"]:
                            is_critical = True
                            severity = "critical" if value < thresholds["low"] * 0.5 else "high"
                            reason = f"Value {value} is below critical threshold {thresholds['low']} {thresholds['unit']}"

                        elif "high" in thresholds and value > thresholds["high"]:
                            is_critical = True
                            severity = "critical" if value > thresholds["high"] * 2 else "high"
                            reason = f"Value {value} is above critical threshold {thresholds['high']} {thresholds['unit']}"

                        if is_critical:
                            critical_values.append(
                                {
                                    "patient_tckn": row.TCKN,
                                    "patient_name": f"{row.patient_name} {row.patient_surname}",
                                    "patient_phone": row.TELEFON,
                                    "test_name": lab_name,
                                    "value": value,
                                    "unit": row.BIRIM,
                                    "critical_threshold": thresholds,
                                    "severity": severity,
                                    "reason": reason,
                                    "test_date": row.TEST_TARIHI.isoformat(),
                                    "hours_ago": int(
                                        (datetime.now() - row.TEST_TARIHI).total_seconds() / 3600
                                    ),
                                }
                            )
                            break

            except (ValueError, TypeError):
                continue

        return {
            "analysis_period_hours": hours,
            "critical_values": critical_values,
            "total_critical_values": len(critical_values),
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def get_lab_utilization_patterns(self) -> Dict:
        """Analyze laboratory test utilization patterns."""
        query = text(
            """
            SELECT
                t.TEST_ADI,
                COUNT(*) as test_count,
                COUNT(DISTINCT t.TCKN) as unique_patients,
                AVG(CAST(t.SONUC AS FLOAT)) as avg_value,
                MIN(t.TEST_TARIHI) as first_test_date,
                MAX(t.TEST_TARIHI) as last_test_date
            FROM TETKIK t
            WHERE t.TEST_TARIHI >= DATEADD(YEAR, -1, GETDATE())
            AND t.SONUC IS NOT NULL
            AND TRY_CAST(t.SONUC AS FLOAT) IS NOT NULL
            GROUP BY t.TEST_ADI
            HAVING COUNT(*) >= 10  -- Only include tests with sufficient data
            ORDER BY test_count DESC
        """
        )

        result = self.session.execute(query).fetchall()

        utilization_patterns = []
        for row in result:
            utilization_patterns.append(
                {
                    "test_name": row.TEST_ADI,
                    "total_tests": row.test_count,
                    "unique_patients": row.unique_patients,
                    "tests_per_patient": round(row.test_count / row.unique_patients, 1),
                    "average_value": round(row.avg_value or 0, 2),
                    "first_test_date": (
                        row.first_test_date.isoformat() if row.first_test_date else None
                    ),
                    "last_test_date": (
                        row.last_test_date.isoformat() if row.last_test_date else None
                    ),
                }
            )

        return {
            "analysis_period": "1 year",
            "utilization_patterns": utilization_patterns,
            "total_different_tests": len(utilization_patterns),
        }

    def generate_comprehensive_lab_report(self) -> Dict:
        """Generate comprehensive laboratory analysis report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "common_labs_trends": self.get_common_labs_trend_analysis(),
            "critical_value_alerts": self.get_critical_lab_values_alert(),
            "lab_utilization_patterns": self.get_lab_utilization_patterns(),
        }


def get_lab_trends_analysis(tckn: Optional[str] = None) -> Dict:
    """Convenience function to get laboratory trends analysis."""
    with get_session() as session:
        analyzer = LabTrendAnalyzer(session)
        if tckn:
            return analyzer.get_patient_lab_trends(tckn)
        else:
            return analyzer.generate_comprehensive_lab_report()


if __name__ == "__main__":
    # Example usage
    trends = get_lab_trends_analysis()
    print("Laboratory Trends Analysis Report")
    print("=" * 40)
    print(f"Generated: {trends['generated_at']}")
    print(f"Critical Values: {trends['critical_value_alerts']['total_critical_values']}")
    print(f"Labs Analyzed: {trends['common_labs_trends']['total_labs_analyzed']}")
