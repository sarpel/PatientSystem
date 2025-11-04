"""
Lab Analyzer Module.

Analyzes laboratory results with features:
- Reference range abnormality detection
- Critical value flagging
- Trend analysis (6 months)
- Z-score calculation for outliers
"""

import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class AlertLevel(Enum):
    """Alert severity levels for abnormal lab values."""

    NORMAL = "normal"
    MILD = "mild"  # Slightly abnormal
    MODERATE = "moderate"  # Moderately abnormal
    CRITICAL = "critical"  # Critically abnormal


@dataclass
class LabResult:
    """Individual lab result with metadata."""

    test_name: str
    value: float
    unit: str
    reference_range: str
    date: datetime
    alert_level: AlertLevel


@dataclass
class LabTrend:
    """Trend analysis for a specific lab test."""

    test_name: str
    values: List[float]
    dates: List[datetime]
    trend: str  # "increasing", "decreasing", "stable"
    slope: float  # Rate of change per day
    z_score: float  # Statistical significance


class LabAnalyzer:
    """
    Laboratory results analyzer with reference range checking and trend analysis.

    Provides comprehensive lab result interpretation for clinical decision support.
    """

    def __init__(self, session: Session):
        """
        Initialize LabAnalyzer.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self._reference_ranges = self._load_reference_ranges()

    def analyze_patient_labs(self, patient_id: int, months_back: int = 6) -> Dict[str, Any]:
        """
        Analyze all laboratory results for a patient.

        Args:
            patient_id: Patient registration ID
            months_back: Number of months to analyze (default: 6)

        Returns:
            Dictionary containing:
            - latest_results: Most recent lab values with alerts
            - abnormal_results: List of abnormal values
            - critical_alerts: List of critical abnormalities
            - trends: Trend analysis for key labs
            - summary: Analysis summary
        """
        # Get lab results from database
        # Note: This is a placeholder - actual implementation would query lab tables
        # For now, we'll simulate with common lab values

        # Simulated lab results for demonstration
        lab_results = self._get_sample_lab_results(patient_id, months_back)

        # Analyze results
        analysis = {
            "latest_results": self._get_latest_results(lab_results),
            "abnormal_results": self._find_abnormal_results(lab_results),
            "critical_alerts": self._find_critical_alerts(lab_results),
            "trends": self._analyze_trends(lab_results),
            "summary": self._generate_analysis_summary(lab_results),
        }

        return analysis

    def _load_reference_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Load standard reference ranges for common lab tests."""
        return {
            "HbA1c": {
                "normal_range": (4.8, 5.6),
                "unit": "%",
                "mild_range": (5.6, 6.5),
                "moderate_range": (6.5, 8.0),
                "critical_threshold": 8.0,
            },
            "Fasting Glucose": {
                "normal_range": (70, 99),
                "unit": "mg/dL",
                "mild_range": (100, 125),
                "moderate_range": (126, 180),
                "critical_threshold": 180,
            },
            "Creatinine": {
                "normal_range": (0.6, 1.3),
                "unit": "mg/dL",
                "mild_range": (1.3, 2.0),
                "moderate_range": (2.0, 3.0),
                "critical_threshold": 3.0,
            },
            "Potassium": {
                "normal_range": (3.5, 5.1),
                "unit": "mmol/L",
                "low_critical": 2.5,
                "high_critical": 6.5,
                "mild_low_range": (2.5, 3.5),
                "mild_high_range": (5.1, 6.5),
            },
            "CRP": {
                "normal_range": (0, 3.0),
                "unit": "mg/L",
                "mild_range": (3.0, 10.0),
                "moderate_range": (10.0, 50.0),
                "critical_threshold": 50.0,
            },
            "WBC": {
                "normal_range": (4.5, 11.0),
                "unit": "x10^9/L",
                "mild_low_range": (3.0, 4.5),
                "mild_high_range": (11.0, 15.0),
                "moderate_low_range": (1.0, 3.0),
                "moderate_high_range": (15.0, 25.0),
                "low_critical": 1.0,
                "high_critical": 25.0,
            },
            "LDL Cholesterol": {
                "normal_range": (0, 100),
                "unit": "mg/dL",
                "mild_range": (100, 130),
                "moderate_range": (130, 160),
                "critical_threshold": 160,
            },
            "eGFR": {
                "normal_range": (90, 120),
                "unit": "mL/min/1.73m²",
                "mild_range": (60, 90),
                "moderate_range": (30, 60),
                "critical_threshold": 30,
            },
            "ALT (SGPT)": {
                "normal_range": (7, 55),
                "unit": "U/L",
                "mild_range": (55, 100),
                "moderate_range": (100, 250),
                "critical_threshold": 250,
            },
            "AST (SGOT)": {
                "normal_range": (8, 48),
                "unit": "U/L",
                "mild_range": (48, 100),
                "moderate_range": (100, 250),
                "critical_threshold": 250,
            },
        }

    def _get_sample_lab_results(self, patient_id: int, months_back: int) -> List[LabResult]:
        """Generate sample lab results for demonstration."""
        # In real implementation, this would query actual lab tables
        base_date = datetime.now() - timedelta(days=months_back * 30)

        # Simulated lab values showing various abnormalities
        sample_data = [
            # Recent values (last visit)
            LabResult("HbA1c", 8.4, "%", "4.8-5.6", base_date + timedelta(days=150)),
            LabResult("Fasting Glucose", 165, "mg/dL", "70-99", base_date + timedelta(days=150)),
            LabResult("Creatinine", 2.1, "mg/dL", "0.6-1.3", base_date + timedelta(days=150)),
            LabResult("Potassium", 5.9, "mmol/L", "3.5-5.1", base_date + timedelta(days=150)),
            LabResult("CRP", 45, "mg/L", "0-3.0", base_date + timedelta(days=150)),
            LabResult("WBC", 14.2, "x10^9/L", "4.5-11.0", base_date + timedelta(days=150)),
            # Previous visit (showing trends)
            LabResult("HbA1c", 7.8, "%", "4.8-5.6", base_date + timedelta(days=120)),
            LabResult("Fasting Glucose", 145, "mg/dL", "70-99", base_date + timedelta(days=120)),
            LabResult("Creatinine", 1.8, "mg/dL", "0.6-1.3", base_date + timedelta(days=120)),
            LabResult("Potassium", 5.4, "mmol/L", "3.5-5.1", base_date + timedelta(days=120)),
            LabResult("CRP", 25, "mg/L", "0-3.0", base_date + timedelta(days=120)),
            # Earlier visit
            LabResult("HbA1c", 7.2, "%", "4.8-5.6", base_date + timedelta(days=90)),
            LabResult("Fasting Glucose", 125, "mg/dL", "70-99", base_date + timedelta(days=90)),
            LabResult("Creatinine", 1.5, "mg/dL", "0.6-1.3", base_date + timedelta(days=90)),
            LabResult("LDL Cholesterol", 145, "mg/dL", "0-100", base_date + timedelta(days=90)),
            LabResult("eGFR", 65, "mL/min/1.73m²", "90-120", base_date + timedelta(days=90)),
            LabResult("ALT (SGPT)", 280, "U/L", "7-55", base_date + timedelta(days=90)),
            LabResult("AST (SGOT)", 260, "U/L", "8-48", base_date + timedelta(days=90)),
        ]

        return sample_data

    def _get_latest_results(self, lab_results: List[LabResult]) -> Dict[str, LabResult]:
        """Get the most recent result for each lab test."""
        latest_results = {}

        # Sort by date and get latest for each test
        sorted_results = sorted(lab_results, key=lambda x: x.date, reverse=True)

        for result in sorted_results:
            if result.test_name not in latest_results:
                latest_results[result.test_name] = result

        return latest_results

    def _find_abnormal_results(self, lab_results: List[LabResult]) -> List[LabResult]:
        """Identify abnormal lab results based on reference ranges."""
        abnormal_results = []

        for result in lab_results:
            alert_level = self._assess_abnormality(result)
            if alert_level != AlertLevel.NORMAL:
                result.alert_level = alert_level
                abnormal_results.append(result)

        return abnormal_results

    def _find_critical_alerts(self, lab_results: List[LabResult]) -> List[LabResult]:
        """Identify critically abnormal lab values requiring immediate attention."""
        critical_alerts = []

        for result in lab_results:
            alert_level = self._assess_abnormality(result)
            if alert_level == AlertLevel.CRITICAL:
                result.alert_level = alert_level
                critical_alerts.append(result)

        return critical_alerts

    def _assess_abnormality(self, result: LabResult) -> AlertLevel:
        """Assess the severity of abnormality for a lab result."""
        test_info = self._reference_ranges.get(result.test_name)
        if not test_info:
            return AlertLevel.NORMAL

        normal_range = test_info.get("normal_range")
        if not normal_range:
            return AlertLevel.NORMAL

        normal_min, normal_max = normal_range
        value = result.value

        # Check if within normal range
        if normal_min <= value <= normal_max:
            return AlertLevel.NORMAL

        # Check severity levels
        mild_range = test_info.get("mild_range")
        moderate_range = test_info.get("moderate_range")
        critical_threshold = test_info.get("critical_threshold")

        # Handle high values
        if value > normal_max:
            if critical_threshold and value >= critical_threshold:
                return AlertLevel.CRITICAL
            elif moderate_range and moderate_range[1] >= value > moderate_range[0]:
                return AlertLevel.MODERATE
            elif mild_range and mild_range[1] >= value > mild_range[0]:
                return AlertLevel.MILD
            else:
                return AlertLevel.CRITICAL  # Default to critical for very high values

        # Handle low values
        low_critical = test_info.get("low_critical")
        mild_low_range = test_info.get("mild_low_range")
        moderate_low_range = test_info.get("moderate_low_range")

        if value < normal_min:
            if low_critical and value <= low_critical:
                return AlertLevel.CRITICAL
            elif moderate_low_range and moderate_low_range[0] <= value < moderate_low_range[1]:
                return AlertLevel.MODERATE
            elif mild_low_range and mild_low_range[0] <= value < mild_low_range[1]:
                return AlertLevel.MILD
            else:
                return AlertLevel.CRITICAL  # Default to critical for very low values

        return AlertLevel.NORMAL

    def _analyze_trends(self, lab_results: List[LabResult]) -> List[LabTrend]:
        """Analyze trends for lab tests with multiple measurements."""
        # Group results by test name
        test_groups = {}
        for result in lab_results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)

        trends = []

        for test_name, results in test_groups.items():
            if len(results) >= 2:  # Need at least 2 points for trend analysis
                # Sort by date
                results.sort(key=lambda x: x.date)

                values = [r.value for r in results]
                dates = [r.date for r in results]

                # Calculate trend
                trend = self._calculate_trend(values, dates)
                trends.append(trend)

        return trends

    def _calculate_trend(self, values: List[float], dates: List[datetime]) -> LabTrend:
        """Calculate statistical trend for a series of lab values."""
        if len(values) < 2:
            return None

        test_name = ""  # Will be set by caller
        values_array = values

        # Calculate days from first measurement
        start_date = dates[0]
        days = [(date - start_date).days for date in dates]

        # Simple linear regression to find trend
        n = len(days)
        sum_x = sum(days)
        sum_y = sum(values_array)
        sum_xy = sum(x * y for x, y in zip(days, values_array))
        sum_x2 = sum(x * x for x in days)

        # Calculate slope (rate of change per day)
        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            if n * sum_x2 - sum_x * sum_x != 0
            else 0
        )

        # Determine trend direction
        if abs(slope) < 0.001:  # Very small slope = stable
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        # Calculate z-score for statistical significance
        if len(values_array) >= 3:
            mean = statistics.mean(values_array)
            stdev = statistics.stdev(values_array) if len(values_array) > 1 else 0
            latest_value = values_array[-1]
            z_score = (latest_value - mean) / stdev if stdev > 0 else 0
        else:
            z_score = 0

        return LabTrend(
            test_name=test_name,
            values=values_array,
            dates=dates,
            trend=trend,
            slope=slope,
            z_score=z_score,
        )

    def _generate_analysis_summary(self, lab_results: List[LabResult]) -> Dict[str, Any]:
        """Generate a summary of the lab analysis."""
        total_tests = len(set(r.test_name for r in lab_results))
        abnormal_count = len(self._find_abnormal_results(lab_results))
        critical_count = len(self._find_critical_alerts(lab_results))

        latest_results = self._get_latest_results(lab_results)
        critical_tests = [
            test_name
            for test_name, result in latest_results.items()
            if self._assess_abnormality(result) == AlertLevel.CRITICAL
        ]

        return {
            "total_unique_tests": total_tests,
            "abnormal_result_count": abnormal_count,
            "critical_alert_count": critical_count,
            "critical_tests": critical_tests,
            "analysis_date": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations(latest_results, critical_tests),
        }

    def _generate_recommendations(
        self, latest_results: Dict[str, LabResult], critical_tests: List[str]
    ) -> List[str]:
        """Generate clinical recommendations based on lab results."""
        recommendations = []

        # Check for critical values
        if any(test in critical_tests for test in ["HbA1c", "Fasting Glucose"]):
            recommendations.append("Immediate diabetes management review required")

        if "Creatinine" in critical_tests:
            recommendations.append("Urgent nephrology consultation recommended")

        if "Potassium" in critical_tests:
            recommendations.append(
                "Critical potassium level - requires immediate medical attention"
            )

        if "CRP" in critical_tests:
            recommendations.append(
                "Severe inflammation - investigate source and consider treatment"
            )

        if "WBC" in critical_tests:
            recommendations.append(
                "Abnormal white blood cell count - infection or hematological disorder evaluation needed"
            )

        # Check for multiple abnormalities
        lab_count = len(latest_results)
        if lab_count >= 10:
            recommendations.append("Comprehensive metabolic panel recommended for full evaluation")

        return recommendations

    def get_lab_analysis_report(self, patient_id: int) -> str:
        """
        Get formatted lab analysis report.

        Args:
            patient_id: Patient registration ID

        Returns:
            Human-readable formatted lab analysis report
        """
        analysis = self.analyze_patient_labs(patient_id)

        lines = []
        lines.append("=" * 60)
        lines.append("LABORATORY ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Analysis Date: {analysis['summary']['analysis_date']}")
        lines.append("")

        # Critical Alerts
        if analysis["critical_alerts"]:
            lines.append("🚨 CRITICAL ALERTS 🚨")
            for alert in analysis["critical_alerts"]:
                lines.append(
                    f"  {alert.test_name}: {alert.value} {alert.unit} (Normal: {alert.reference_range})"
                )
            lines.append("")

        # Latest Results
        lines.append("LATEST LAB RESULTS")
        lines.append("-" * 40)
        latest = analysis["latest_results"]
        for test_name, result in latest.items():
            status = "✅ Normal"
            if result.alert_level == AlertLevel.MILD:
                status = "⚠️  Mildly abnormal"
            elif result.alert_level == AlertLevel.MODERATE:
                status = "🔶 Moderately abnormal"
            elif result.alert_level == AlertLevel.CRITICAL:
                status = "🚨 Critical"

            lines.append(f"  {test_name}: {result.value} {result.unit} {status}")

        lines.append("")

        # Trends
        if analysis["trends"]:
            lines.append("TREND ANALYSIS")
            lines.append("-" * 40)
            for trend in analysis["trends"]:
                if abs(trend.z_score) > 1.96:  # Statistically significant (p < 0.05)
                    significance = " (significant)"
                else:
                    significance = " (not significant)"

                lines.append(f"  {trend.test_name}: {trend.trend}{significance}")

        lines.append("")

        # Recommendations
        if analysis["summary"]["recommendations"]:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for rec in analysis["summary"]["recommendations"]:
                lines.append(f"  • {rec}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
