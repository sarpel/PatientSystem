"""
Tests for Lab Analyzer module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.clinical.lab_analyzer import (
    LabAnalyzer, AlertLevel, LabResult, LabTrend
)


class TestLabAnalyzer:
    """Test suite for LabAnalyzer class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session

    @pytest.fixture
    def lab_analyzer(self, mock_session):
        """Create LabAnalyzer instance."""
        return LabAnalyzer(mock_session)

    @pytest.fixture
    def sample_lab_results(self):
        """Create sample lab results."""
        base_date = datetime.now() - timedelta(days=90)
        return [
            # Critical values
            LabResult("Creatinine", 2.1, "mg/dL", "0.6-1.3", base_date + timedelta(days=60)),
            LabResult("Potassium", 5.9, "mmol/L", "3.5-5.1", base_date + timedelta(days=60)),
            LabResult("CRP", 45, "mg/L", "0-3.0", base_date + timedelta(days=60)),

            # Moderately abnormal values
            LabResult("HbA1c", 7.8, "%", "4.8-5.6", base_date + timedelta(days=60)),
            LabResult("Fasting Glucose", 165, "mg/dL", "70-99", base_date + timedelta(days=60)),

            # Normal values
            LabResult("WBC", 8.5, "x10^9/L", "4.5-11.0", base_date + timedelta(days=60)),

            # Previous values for trend analysis
            LabResult("HbA1c", 7.2, "%", "4.8-5.6", base_date + timedelta(days=30)),
            LabResult("HbA1c", 6.8, "%", "4.8-5.6", base_date),
        ]

    def test_init(self, mock_session):
        """Test LabAnalyzer initialization."""
        analyzer = LabAnalyzer(mock_session)
        assert analyzer.session == mock_session
        assert isinstance(analyzer._reference_ranges, dict)
        assert "HbA1c" in analyzer._reference_ranges
        assert "Creatinine" in analyzer._reference_ranges

    def test_analyze_patient_labs(self, lab_analyzer, sample_lab_results):
        """Test comprehensive lab analysis."""
        with patch.object(lab_analyzer, '_get_sample_lab_results', return_value=sample_lab_results):
            result = lab_analyzer.analyze_patient_labs(12345)

            # Verify structure
            assert "latest_results" in result
            assert "abnormal_results" in result
            assert "critical_alerts" in result
            assert "trends" in result
            assert "summary" in result

            # Verify content
            assert len(result["latest_results"]) > 0
            assert len(result["abnormal_results"]) > 0
            assert len(result["critical_alerts"]) > 0
            assert len(result["trends"]) >= 1  # Should have at least HbA1c trend

    def test_assess_abnormality_normal(self, lab_analyzer):
        """Test abnormality assessment for normal values."""
        normal_result = LabResult("HbA1c", 5.0, "%", "4.8-5.6", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(normal_result)
        assert alert_level == AlertLevel.NORMAL

    def test_assess_abnormality_mild(self, lab_analyzer):
        """Test abnormality assessment for mildly abnormal values."""
        mild_result = LabResult("HbA1c", 6.0, "%", "4.8-5.6", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(mild_result)
        assert alert_level == AlertLevel.MILD

    def test_assess_abnormality_moderate(self, lab_analyzer):
        """Test abnormality assessment for moderately abnormal values."""
        moderate_result = LabResult("HbA1c", 7.5, "%", "4.8-5.6", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(moderate_result)
        assert alert_level == AlertLevel.MODERATE

    def test_assess_abnormality_critical(self, lab_analyzer):
        """Test abnormality assessment for critically abnormal values."""
        critical_result = LabResult("HbA1c", 8.5, "%", "4.8-5.6", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(critical_result)
        assert alert_level == AlertLevel.CRITICAL

    def test_assess_abnormality_creatinine_critical(self, lab_analyzer):
        """Test critical creatinine assessment."""
        critical_creatinine = LabResult("Creatinine", 3.5, "mg/dL", "0.6-1.3", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(critical_creatinine)
        assert alert_level == AlertLevel.CRITICAL

    def test_assess_abnormality_potassium_high_critical(self, lab_analyzer):
        """Test critical high potassium assessment."""
        high_k = LabResult("Potassium", 6.8, "mmol/L", "3.5-5.1", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(high_k)
        assert alert_level == AlertLevel.CRITICAL

    def test_assess_abnormality_potassium_low_critical(self, lab_analyzer):
        """Test critical low potassium assessment."""
        low_k = LabResult("Potassium", 2.3, "mmol/L", "3.5-5.1", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(low_k)
        assert alert_level == AlertLevel.CRITICAL

    def test_assess_abnormality_unknown_test(self, lab_analyzer):
        """Test abnormality assessment for unknown test."""
        unknown_result = LabResult("Unknown Test", 100, "units", "10-20", datetime.now())
        alert_level = lab_analyzer._assess_abnormality(unknown_result)
        assert alert_level == AlertLevel.NORMAL

    def test_get_latest_results(self, lab_analyzer, sample_lab_results):
        """Test getting latest results for each test."""
        latest = lab_analyzer._get_latest_results(sample_lab_results)

        # Should have unique tests
        assert len(latest) == len(set(r.test_name for r in sample_lab_results))

        # Should have latest values
        assert latest["HbA1c"].value == 7.8  # Latest HbA1c value
        assert latest["Creatinine"].value == 2.1  # Latest Creatinine value

    def test_find_abnormal_results(self, lab_analyzer, sample_lab_results):
        """Test finding abnormal results."""
        abnormal = lab_analyzer._find_abnormal_results(sample_lab_results)

        assert len(abnormal) > 0
        assert all(result.alert_level != AlertLevel.NORMAL for result in abnormal)

        # Check for specific abnormal results
        abnormal_test_names = [r.test_name for r in abnormal]
        assert "Creatinine" in abnormal_test_names
        assert "HbA1c" in abnormal_test_names

    def test_find_critical_alerts(self, lab_analyzer, sample_lab_results):
        """Test finding critical alerts."""
        critical = lab_analyzer._find_critical_alerts(sample_lab_results)

        assert len(critical) > 0
        assert all(result.alert_level == AlertLevel.CRITICAL for result in critical)

        # Should include the critical values we set up
        critical_test_names = [r.test_name for r in critical]
        assert "Creatinine" in critical_test_names
        assert "Potassium" in critical_test_names

    def test_analyze_trends(self, lab_analyzer, sample_lab_results):
        """Test trend analysis."""
        trends = lab_analyzer._analyze_trends(sample_lab_results)

        # Should have trend for HbA1c (has multiple measurements)
        hba1c_trends = [t for t in trends if t.test_name == "HbA1c"]
        assert len(hba1c_trends) == 1

        trend = hba1c_trends[0]
        assert len(trend.values) == 3  # Three HbA1c measurements
        assert len(trend.dates) == 3
        assert trend.trend in ["increasing", "decreasing", "stable"]
        assert isinstance(trend.slope, float)
        assert isinstance(trend.z_score, float)

    def test_analyze_trends_insufficient_data(self, lab_analyzer):
        """Test trend analysis with insufficient data."""
        single_result = [LabResult("HbA1c", 7.0, "%", "4.8-5.6", datetime.now())]
        trends = lab_analyzer._analyze_trends(single_result)

        # Should not have trends with only one data point
        assert len(trends) == 0

    def test_calculate_trend_increasing(self, lab_analyzer):
        """Test trend calculation for increasing values."""
        values = [6.5, 7.0, 7.5, 8.0]
        base_date = datetime.now()
        dates = [base_date + timedelta(days=i * 30) for i in range(4)]

        trend = lab_analyzer._calculate_trend(values, dates)

        assert trend.trend == "increasing"
        assert trend.slope > 0

    def test_calculate_trend_decreasing(self, lab_analyzer):
        """Test trend calculation for decreasing values."""
        values = [8.0, 7.5, 7.0, 6.5]
        base_date = datetime.now()
        dates = [base_date + timedelta(days=i * 30) for i in range(4)]

        trend = lab_analyzer._calculate_trend(values, dates)

        assert trend.trend == "decreasing"
        assert trend.slope < 0

    def test_calculate_trend_stable(self, lab_analyzer):
        """Test trend calculation for stable values."""
        values = [7.0, 7.1, 7.0, 7.1]
        base_date = datetime.now()
        dates = [base_date + timedelta(days=i * 30) for i in range(4)]

        trend = lab_analyzer._calculate_trend(values, dates)

        assert trend.trend == "stable"
        assert abs(trend.slope) < 0.001

    def test_generate_analysis_summary(self, lab_analyzer, sample_lab_results):
        """Test analysis summary generation."""
        with patch.object(lab_analyzer, '_get_latest_results', return_value={}):
            with patch.object(lab_analyzer, '_find_abnormal_results', return_value=sample_lab_results):
                with patch.object(lab_analyzer, '_find_critical_alerts', return_value=sample_lab_results[:2]):
                    with patch.object(lab_analyzer, '_generate_recommendations', return_value=["Test recommendation"]):
                        summary = lab_analyzer._generate_analysis_summary(sample_lab_results)

                        assert "total_unique_tests" in summary
                        assert "abnormal_result_count" in summary
                        assert "critical_alert_count" in summary
                        assert "critical_tests" in summary
                        assert "analysis_date" in summary
                        assert "recommendations" in summary

    def test_generate_recommendations_critical_glucose(self, lab_analyzer):
        """Test recommendations for critical glucose values."""
        latest_results = {
            "HbA1c": LabResult("HbA1c", 8.4, "%", "4.8-5.6", datetime.now()),
            "Fasting Glucose": LabResult("Fasting Glucose", 200, "mg/dL", "70-99", datetime.now())
        }

        recommendations = lab_analyzer._generate_recommendations(latest_results, ["HbA1c", "Fasting Glucose"])

        assert "diabetes management review" in " ".join(recommendations).lower()

    def test_generate_recommendations_critical_creatinine(self, lab_analyzer):
        """Test recommendations for critical creatinine."""
        latest_results = {
            "Creatinine": LabResult("Creatinine", 3.0, "mg/dL", "0.6-1.3", datetime.now())
        }

        recommendations = lab_analyzer._generate_recommendations(latest_results, ["Creatinine"])

        assert "nephrology" in " ".join(recommendations).lower()

    def test_generate_recommendations_critical_potassium(self, lab_analyzer):
        """Test recommendations for critical potassium."""
        latest_results = {
            "Potassium": LabResult("Potassium", 6.5, "mmol/L", "3.5-5.1", datetime.now())
        }

        recommendations = lab_analyzer._generate_recommendations(latest_results, ["Potassium"])

        assert "medical attention" in " ".join(recommendations).lower()

    def test_generate_recommendations_critical_crp(self, lab_analyzer):
        """Test recommendations for critical CRP."""
        latest_results = {
            "CRP": LabResult("CRP", 60, "mg/L", "0-3.0", datetime.now())
        }

        recommendations = lab_analyzer._generate_recommendations(latest_results, ["CRP"])

        assert "inflammation" in " ".join(recommendations).lower()

    def test_generate_recommendations_critical_wbc(self, lab_analyzer):
        """Test recommendations for critical WBC."""
        latest_results = {
            "WBC": LabResult("WBC", 30.0, "x10^9/L", "4.5-11.0", datetime.now())
        }

        recommendations = lab_analyzer._generate_recommendations(latest_results, ["WBC"])

        assert "infection" in " ".join(recommendations).lower()

    def test_get_lab_analysis_report(self, lab_analyzer):
        """Test formatted lab analysis report generation."""
        mock_analysis = {
            "latest_results": {
                "HbA1c": LabResult("HbA1c", 8.4, "%", "4.8-5.6", datetime.now()),
                "Creatinine": LabResult("Creatinine", 2.1, "mg/dL", "0.6-1.3", datetime.now())
            },
            "critical_alerts": [
                LabResult("Creatinine", 2.1, "mg/dL", "0.6-1.3", datetime.now())
            ],
            "abnormal_results": [],
            "trends": [],
            "summary": {
                "analysis_date": datetime.now().isoformat(),
                "critical_alert_count": 1,
                "abnormal_result_count": 2,
                "recommendations": ["Monitor kidney function"]
            }
        }

        with patch.object(lab_analyzer, 'analyze_patient_labs', return_value=mock_analysis):
            report = lab_analyzer.get_lab_analysis_report(12345)

            assert "LABORATORY ANALYSIS REPORT" in report
            assert "🚨 CRITICAL ALERTS 🚨" in report
            assert "LATEST LAB RESULTS" in report
            assert "Creatinine: 2.1 mg/dL" in report
            assert "RECOMMENDATIONS" in report
            assert "Monitor kidney function" in report

    def test_get_lab_analysis_report_no_criticals(self, lab_analyzer):
        """Test lab analysis report without critical alerts."""
        mock_analysis = {
            "latest_results": {
                "HbA1c": LabResult("HbA1c", 5.5, "%", "4.8-5.6", datetime.now()),
                "WBC": LabResult("WBC", 7.5, "x10^9/L", "4.5-11.0", datetime.now())
            },
            "critical_alerts": [],
            "abnormal_results": [],
            "trends": [],
            "summary": {
                "analysis_date": datetime.now().isoformat(),
                "critical_alert_count": 0,
                "abnormal_result_count": 0,
                "recommendations": []
            }
        }

        with patch.object(lab_analyzer, 'analyze_patient_labs', return_value=mock_analysis):
            report = lab_analyzer.get_lab_analysis_report(12345)

            assert "LABORATORY ANALYSIS REPORT" in report
            assert "🚨 CRITICAL ALERTS 🚨" not in report
            assert "HbA1c: 5.5 % ✅ Normal" in report
            assert "WBC: 7.5 x10^9/L ✅ Normal" in report

    def test_reference_ranges_completeness(self, lab_analyzer):
        """Test that reference ranges are properly loaded."""
        ranges = lab_analyzer._reference_ranges

        # Check that key tests have reference ranges
        required_tests = [
            "HbA1c", "Fasting Glucose", "Creatinine", "Potassium",
            "CRP", "WBC", "LDL Cholesterol", "eGFR",
            "ALT (SGPT)", "AST (SGOT)"
        ]

        for test in required_tests:
            assert test in ranges, f"Missing reference range for {test}"
            assert "normal_range" in ranges[test], f"Missing normal range for {test}"

    def test_edge_case_empty_lab_results(self, lab_analyzer):
        """Test analysis with empty lab results."""
        with patch.object(lab_analyzer, '_get_sample_lab_results', return_value=[]):
            result = lab_analyzer.analyze_patient_labs(12345)

            assert result["latest_results"] == {}
            assert result["abnormal_results"] == []
            assert result["critical_alerts"] == []
            assert result["trends"] == []

    def test_edge_case_single_lab_result(self, lab_analyzer):
        """Test analysis with single lab result."""
        single_result = [LabResult("HbA1c", 7.5, "%", "4.8-5.6", datetime.now())]

        with patch.object(lab_analyzer, '_get_sample_lab_results', return_value=single_result):
            result = lab_analyzer.analyze_patient_labs(12345)

            assert len(result["latest_results"]) == 1
            assert len(result["abnormal_results"]) == 1
            assert len(result["trends"]) == 0  # No trend with single data point