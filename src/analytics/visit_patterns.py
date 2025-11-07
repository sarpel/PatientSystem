"""Patient visit pattern analytics for clinical insights.

WARNING: This module uses placeholder table names in raw SQL queries that do not match
the actual database schema. The following table name mappings should be used:
- MUAYENE -> GP_MUAYENE

TODO: Update all raw SQL queries to use actual table names from table_names.csv
and verify column names match the actual schema.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.connection import get_session


class VisitPatternAnalyzer:
    """Analyzes patient visit patterns and provides clinical insights."""

    def __init__(self, session: Session):
        self.session = session

    def get_visit_frequency_trends(self, months: int = 12) -> Dict:
        """Analyze visit frequency trends over time."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        query = text(
            """
            SELECT
                FORMAT(MUAYENE_TARIHI, 'yyyy-MM') as month,
                COUNT(*) as visit_count,
                COUNT(DISTINCT TCKN) as unique_patients
            FROM MUAYENE
            WHERE MUAYENE_TARIHI BETWEEN :start_date AND :end_date
            GROUP BY FORMAT(MUAYENE_TARIHI, 'yyyy-MM')
            ORDER BY month
        """
        )

        result = self.session.execute(
            query, {"start_date": start_date, "end_date": end_date}
        ).fetchall()

        return {
            "trends": [
                {
                    "month": row.month,
                    "visits": row.visit_count,
                    "unique_patients": row.unique_patients,
                    "avg_visits_per_patient": round(row.visit_count / row.unique_patients, 2),
                }
                for row in result
            ],
            "total_months": len(result),
            "analysis_period": f"{months} months",
        }

    def get_peak_visit_times(self) -> Dict:
        """Analyze peak visit times by hour and day of week."""
        query = text(
            """
            SELECT
                DATEPART(HOUR, MUAYENE_TARIHI) as hour,
                DATEPART(WEEKDAY, MUAYENE_TARIHI) as day_of_week,
                COUNT(*) as visit_count
            FROM MUAYENE
            WHERE MUAYENE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
            GROUP BY
                DATEPART(HOUR, MUAYENE_TARIHI),
                DATEPART(WEEKDAY, MUAYENE_TARIHI)
            ORDER BY visit_count DESC
        """
        )

        result = self.session.execute(query).fetchall()

        # Process results for heatmap
        heatmap_data = {}
        for row in result:
            hour = row.hour
            day = row.day_of_week
            count = row.visit_count

            if day not in heatmap_data:
                heatmap_data[day] = {}
            heatmap_data[day][hour] = count

        # Find peak times
        peak_times = sorted(result, key=lambda x: x.visit_count, reverse=True)[:5]

        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        return {
            "heatmap_data": heatmap_data,
            "peak_times": [
                {
                    "day": day_names[peak.day_of_week],
                    "hour": f"{peak.hour:02d}:00",
                    "visit_count": peak.visit_count,
                }
                for peak in peak_times
            ],
            "busiest_day": day_names[peak_times[0].day_of_week] if peak_times else None,
            "busiest_hour": f"{peak_times[0].hour:02d}:00" if peak_times else None,
        }

    def get_patient_visit_frequency_distribution(self) -> Dict:
        """Analyze distribution of patient visit frequencies."""
        query = text(
            """
            SELECT
                visit_counts.frequency_range,
                COUNT(*) as patient_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM (
                    SELECT COUNT(*) as visit_count FROM MUAYENE
                    GROUP BY TCKN
                ) freq_counts), 2) as percentage
            FROM (
                SELECT
                    CASE
                        WHEN visit_count = 1 THEN '1 visit'
                        WHEN visit_count = 2 THEN '2 visits'
                        WHEN visit_count = 3 THEN '3 visits'
                        WHEN visit_count BETWEEN 4 AND 5 THEN '4-5 visits'
                        WHEN visit_count BETWEEN 6 AND 10 THEN '6-10 visits'
                        WHEN visit_count BETWEEN 11 AND 20 THEN '11-20 visits'
                        ELSE '20+ visits'
                    END as frequency_range
                FROM (
                    SELECT COUNT(*) as visit_count
                    FROM MUAYENE
                    WHERE MUAYENE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
                    GROUP BY TCKN
                ) visit_counts
            ) visit_counts
            GROUP BY visit_counts.frequency_range
            ORDER BY
                CASE
                    WHEN visit_counts.frequency_range = '1 visit' THEN 1
                    WHEN visit_counts.frequency_range = '2 visits' THEN 2
                    WHEN visit_counts.frequency_range = '3 visits' THEN 3
                    WHEN visit_counts.frequency_range = '4-5 visits' THEN 4
                    WHEN visit_counts.frequency_range = '6-10 visits' THEN 5
                    WHEN visit_counts.frequency_range = '11-20 visits' THEN 6
                    ELSE 7
                END
        """
        )

        result = self.session.execute(query).fetchall()

        return {
            "distribution": [
                {
                    "frequency_range": row.frequency_range,
                    "patient_count": row.patient_count,
                    "percentage": row.percentage,
                }
                for row in result
            ],
            "total_patients": sum(row.patient_count for row in result),
        }

    def get_return_patient_analysis(self, days: int = 30) -> Dict:
        """Analyze patient return rates within specified timeframe."""
        query = text(
            """
            WITH PatientVisits AS (
                SELECT
                    TCKN,
                    MUAYENE_TARIHI,
                    LEAD(MUAYENE_TARIHI) OVER (PARTITION BY TCKN ORDER BY MUAYENE_TARIHI) as next_visit
                FROM MUAYENE
                WHERE MUAYENE_TARIHI >= DATEADD(YEAR, -1, GETDATE())
            ),
            ReturnAnalysis AS (
                SELECT
                    TCKN,
                    MUAYENE_TARIHI,
                    next_visit,
                    DATEDIFF(day, MUAYENE_TARIHI, next_visit) as days_until_return,
                    CASE
                        WHEN DATEDIFF(day, MUAYENE_TARIHI, next_visit) <= :days THEN 1 ELSE 0
                    END as returned_within_period
                FROM PatientVisits
                WHERE next_visit IS NOT NULL
            )
            SELECT
                COUNT(*) as total_visits_with_followup,
                SUM(returned_within_period) as returns_within_period,
                ROUND(AVG(CAST(days_until_return AS FLOAT)), 1) as avg_days_until_return,
                ROUND(SUM(returned_within_period) * 100.0 / COUNT(*), 2) as return_rate_percentage
            FROM ReturnAnalysis
        """
        )

        result = self.session.execute(query, {"days": days}).fetchone()

        return {
            "analysis_period_days": days,
            "total_visits_with_followup": result.total_visits_with_followup,
            "returns_within_period": result.returns_within_period,
            "return_rate_percentage": result.return_rate_percentage,
            "average_days_until_return": result.avg_days_until_return,
        }

    def get_seasonal_patterns(self) -> Dict:
        """Analyze seasonal visit patterns."""
        query = text(
            """
            SELECT
                CASE
                    WHEN MONTH(MUAYENE_TARIHI) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(MUAYENE_TARIHI) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(MUAYENE_TARIHI) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(*) as visit_count,
                COUNT(DISTINCT TCKN) as unique_patients,
                ROUND(AVG(CAST(DATEDIFF(day,
                    LAG(MUAYENE_TARIHI) OVER (PARTITION BY TCKN ORDER BY MUAYENE_TARIHI),
                    MUAYENE_TARIHI) AS FLOAT)), 1) as avg_days_between_visits
            FROM MUAYENE
            WHERE MUAYENE_TARIHI >= DATEADD(YEAR, -2, GETDATE())
            GROUP BY
                CASE
                    WHEN MONTH(MUAYENE_TARIHI) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(MUAYENE_TARIHI) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(MUAYENE_TARIHI) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END
            ORDER BY visit_count DESC
        """
        )

        result = self.session.execute(query).fetchall()

        return {
            "seasonal_patterns": [
                {
                    "season": row.season,
                    "visit_count": row.visit_count,
                    "unique_patients": row.unique_patients,
                    "avg_days_between_visits": row.avg_days_between_visits,
                }
                for row in result
            ],
            "busiest_season": max(result, key=lambda x: x.visit_count).season if result else None,
            "analysis_period": "2 years",
        }

    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive visit pattern analysis report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "visit_frequency_trends": self.get_visit_frequency_trends(),
            "peak_visit_times": self.get_peak_visit_times(),
            "patient_frequency_distribution": self.get_patient_visit_frequency_distribution(),
            "return_patient_analysis": self.get_return_patient_analysis(),
            "seasonal_patterns": self.get_seasonal_patterns(),
        }


def get_visit_patterns(tckn: Optional[str] = None) -> Dict:
    """Convenience function to get visit patterns analysis."""
    with get_session() as session:
        analyzer = VisitPatternAnalyzer(session)
        return analyzer.generate_comprehensive_report()


if __name__ == "__main__":
    # Example usage
    patterns = get_visit_patterns()
    print("Visit Pattern Analysis Report")
    print("=" * 40)
    print(f"Generated: {patterns['generated_at']}")
    print(f"Busiest Season: {patterns['seasonal_patterns']['busiest_season']}")
    print(
        f"Return Rate (30 days): {patterns['return_patient_analysis']['return_rate_percentage']}%"
    )
