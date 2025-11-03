"""Lab results visualization with interactive trend charts."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import text

from ...database.connection import get_session


class LabChartsWidget(QWidget):
    """Widget for displaying lab test trend charts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tckn: Optional[str] = None
        self.lab_data: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Test Type:"))

        self.test_combo = QComboBox()
        self.test_combo.addItems(
            [
                "Hemoglobin (HGB)",
                "White Blood Cell (WBC)",
                "Platelet Count (PLT)",
                "Glucose",
                "Creatinine",
                "ALT (SGPT)",
                "AST (SGOT)",
                "Total Cholesterol",
                "LDL Cholesterol",
                "HDL Cholesterol",
                "Triglycerides",
            ]
        )
        self.test_combo.currentIndexChanged.connect(self._update_chart)
        controls_layout.addWidget(self.test_combo)

        controls_layout.addWidget(QLabel("Time Range:"))

        self.range_combo = QComboBox()
        self.range_combo.addItems(["1 Month", "3 Months", "6 Months", "1 Year", "All"])
        self.range_combo.currentIndexChanged.connect(self._update_chart)
        controls_layout.addWidget(self.range_combo)

        controls_layout.addStretch()

        self.export_button = QPushButton("Export Chart")
        self.export_button.clicked.connect(self._export_chart)
        controls_layout.addWidget(self.export_button)

        layout.addLayout(controls_layout)

        # Chart widget
        self.chart_widget = PlotWidget()
        self.chart_widget.setBackground("w")
        self.chart_widget.showGrid(x=True, y=True, alpha=0.3)
        self.chart_widget.setLabel("left", "Value")
        self.chart_widget.setLabel("bottom", "Date")

        # Add legend
        self.chart_widget.addLegend()

        layout.addWidget(self.chart_widget)

        # Status label
        self.status_label = QLabel("No patient selected")
        self.status_label.setStyleSheet("padding: 4px; color: #6b7280;")
        layout.addWidget(self.status_label)

    def load_patient(self, tckn: str):
        """Load patient lab data."""
        self.current_tckn = tckn

        try:
            with get_session() as session:
                # Load lab tests for patient using SQL query
                query = text(
                    """
                    SELECT
                        TEST_ADI,
                        SONUC,
                        BIRIM,
                        TEST_TARIHI,
                        NORMAL_MIN,
                        NORMAL_MAX
                    FROM TETKIK
                    WHERE TCKN = :tckn
                    AND SONUC IS NOT NULL
                    ORDER BY TEST_TARIHI DESC
                """
                )

                result = session.execute(query, {"tckn": tckn}).fetchall()

                # Group by test type
                self.lab_data = {}
                for row in result:
                    test_name = row.TEST_ADI or "Unknown"
                    if test_name not in self.lab_data:
                        self.lab_data[test_name] = []

                    # Convert row to dict
                    test_dict = {
                        "TEST_ADI": row.TEST_ADI,
                        "SONUC": row.SONUC,
                        "BIRIM": row.BIRIM,
                        "TEST_TARIHI": row.TEST_TARIHI,
                        "NORMAL_MIN": row.NORMAL_MIN,
                        "NORMAL_MAX": row.NORMAL_MAX,
                    }
                    self.lab_data[test_name].append(test_dict)

                # Update status
                total_tests = len(result)
                unique_types = len(self.lab_data)
                self.status_label.setText(
                    f"Loaded {total_tests} test results ({unique_types} unique test types)"
                )

                # Update chart
                self._update_chart()

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load lab data:\n{str(e)}")

    def _update_chart(self):
        """Update chart based on selected test and time range."""
        if not self.current_tckn or not self.lab_data:
            return

        self.chart_widget.clear()

        # Get selected test type
        test_type = self.test_combo.currentText()

        # Get matching lab data (simplified - would need proper mapping)
        # For demo, just use any available data
        if not self.lab_data:
            self.status_label.setText("No lab data available")
            return

        # Get first available test type
        available_tests = list(self.lab_data.keys())
        if not available_tests:
            return

        test_data = self.lab_data[available_tests[0]]

        # Filter by time range
        range_text = self.range_combo.currentText()
        range_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365, "All": None}
        days = range_map.get(range_text)

        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            test_data = [
                t for t in test_data if t.get("TEST_TARIHI") and t["TEST_TARIHI"] >= cutoff_date
            ]

        if not test_data:
            self.status_label.setText("No data in selected time range")
            return

        # Prepare data for plotting
        dates = []
        values = []

        for test in sorted(test_data, key=lambda t: t.get("TEST_TARIHI") or datetime.min):
            if test.get("TEST_TARIHI") and test.get("SONUC"):
                try:
                    # Convert date to timestamp
                    timestamp = test["TEST_TARIHI"].timestamp()
                    dates.append(timestamp)

                    # Parse value (handle different formats)
                    value_str = str(test["SONUC"]).replace(",", ".")
                    value = float(value_str)
                    values.append(value)
                except (ValueError, AttributeError):
                    continue

        if not dates:
            self.status_label.setText("No plottable data available")
            return

        # Plot the data
        pen = pg.mkPen(color="b", width=2)
        self.chart_widget.plot(
            dates,
            values,
            pen=pen,
            symbol="o",
            symbolSize=8,
            symbolBrush="b",
            name=available_tests[0],
        )

        # Add reference range shading (example values)
        # Would need to be configurable based on test type
        if available_tests[0].startswith("Hemoglobin"):
            normal_min = 12.0
            normal_max = 16.0

            # Create shaded region
            region = pg.LinearRegionItem(
                values=[normal_min, normal_max],
                orientation="horizontal",
                brush=pg.mkBrush(0, 255, 0, 50),
                movable=False,
            )
            self.chart_widget.addItem(region)

        # Update chart title
        self.chart_widget.setTitle(f"{available_tests[0]} Trend")

        self.status_label.setText(f"Displaying {len(dates)} data points")

    def _export_chart(self):
        """Export chart as image."""
        if not self.current_tckn:
            QMessageBox.warning(self, "No Patient", "Please select a patient first")
            return

        # Export chart (simplified - would use file dialog)
        exporter = pg.exporters.ImageExporter(self.chart_widget.plotItem)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lab_chart_{self.current_tckn}_{timestamp}.png"

        try:
            exporter.export(filename)
            QMessageBox.information(self, "Export Success", f"Chart saved to: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export chart:\n{str(e)}")
