"""Diagnosis panel with AI-powered analysis interface."""

import asyncio
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...clinical.diagnosis_engine import DiagnosisEngine
from ...database.connection import get_session


class DiagnosisWorker(QThread):
    """Background worker for AI diagnosis generation."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, tckn: str, complaint: str, model: Optional[str] = None):
        super().__init__()
        self.tckn = tckn
        self.complaint = complaint
        self.model = model

    def run(self):
        """Run diagnosis generation in background thread."""
        try:
            with get_session() as session:
                engine = DiagnosisEngine(session)
                result = asyncio.run(
                    engine.generate_differential_diagnosis_ai(
                        tckn=self.tckn,
                        chief_complaint=self.complaint,
                        preferred_provider=self.model,
                    )
                )
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class DiagnosisPanelWidget(QWidget):
    """Panel for AI-powered differential diagnosis generation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tckn: Optional[str] = None
        self.worker: Optional[DiagnosisWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Chief complaint input
        input_group = QGroupBox("Chief Complaint")
        input_layout = QVBoxLayout(input_group)

        self.complaint_input = QTextEdit()
        self.complaint_input.setPlaceholderText(
            "Enter patient's chief complaint and symptoms...\n"
            "Example: Chest pain for 2 hours, shortness of breath"
        )
        self.complaint_input.setMaximumHeight(100)
        input_layout.addWidget(self.complaint_input)

        # Model selection and analyze button
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("AI Model:"))

        self.model_combo = QComboBox()
        self.model_combo.addItems(
            ["Auto (Smart Routing)", "Claude", "GPT-4o", "Gemini", "Ollama"]
        )
        controls_layout.addWidget(self.model_combo)

        controls_layout.addStretch()

        self.analyze_button = QPushButton("Generate Diagnosis")
        self.analyze_button.clicked.connect(self._generate_diagnosis)
        controls_layout.addWidget(self.analyze_button)

        input_layout.addLayout(controls_layout)
        layout.addWidget(input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results table
        results_group = QGroupBox("Differential Diagnosis")
        results_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(
            ["Diagnosis", "ICD-10", "Probability", "Urgency"]
        )
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        results_layout.addWidget(self.results_table)

        layout.addWidget(results_group)

        # Red flags
        self.red_flags_group = QGroupBox("⚠️ Red Flags")
        self.red_flags_group.setVisible(False)
        red_flags_layout = QVBoxLayout(self.red_flags_group)

        self.red_flags_text = QTextEdit()
        self.red_flags_text.setReadOnly(True)
        self.red_flags_text.setMaximumHeight(80)
        self.red_flags_text.setStyleSheet("background-color: #fef2f2; color: #991b1b;")
        red_flags_layout.addWidget(self.red_flags_text)

        layout.addWidget(self.red_flags_group)

        # Recommended tests
        self.tests_group = QGroupBox("Recommended Tests")
        self.tests_group.setVisible(False)
        tests_layout = QVBoxLayout(self.tests_group)

        self.tests_text = QTextEdit()
        self.tests_text.setReadOnly(True)
        self.tests_text.setMaximumHeight(80)
        tests_layout.addWidget(self.tests_text)

        layout.addWidget(self.tests_group)

    def load_patient(self, tckn: str):
        """Load patient context."""
        self.current_tckn = tckn
        self.complaint_input.clear()
        self.results_table.setRowCount(0)
        self.red_flags_group.setVisible(False)
        self.tests_group.setVisible(False)

    def _generate_diagnosis(self):
        """Generate differential diagnosis using AI."""
        if not self.current_tckn:
            QMessageBox.warning(self, "No Patient", "Please select a patient first")
            return

        complaint = self.complaint_input.toPlainText().strip()
        if not complaint:
            QMessageBox.warning(self, "No Complaint", "Please enter chief complaint")
            return

        # Get selected model
        model_text = self.model_combo.currentText()
        model_map = {
            "Claude": "claude",
            "GPT-5": "gpt-5",
            "Gemini": "gemini",
            "Ollama": "ollama",
        }
        model = model_map.get(model_text)

        # Show progress
        self.progress_bar.setVisible(True)
        self.analyze_button.setEnabled(False)

        # Start worker thread
        self.worker = DiagnosisWorker(self.current_tckn, complaint, model)
        self.worker.finished.connect(self._on_diagnosis_complete)
        self.worker.error.connect(self._on_diagnosis_error)
        self.worker.start()

    def _on_diagnosis_complete(self, result: Dict[str, Any]):
        """Handle diagnosis completion."""
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)

        # Display differential diagnosis
        diagnoses = result.get("differential_diagnosis", [])
        self.results_table.setRowCount(len(diagnoses))

        for row, dx in enumerate(diagnoses):
            self.results_table.setItem(
                row, 0, QTableWidgetItem(dx.get("diagnosis", ""))
            )
            self.results_table.setItem(row, 1, QTableWidgetItem(dx.get("icd10", "")))

            prob = dx.get("probability", 0)
            prob_item = QTableWidgetItem(f"{prob * 100:.1f}%")
            self.results_table.setItem(row, 2, prob_item)

            urgency = dx.get("urgency", "moderate")
            urgency_item = QTableWidgetItem(urgency)

            # Color-code urgency
            if urgency == "critical":
                urgency_item.setBackground(Qt.red)
                urgency_item.setForeground(Qt.white)
            elif urgency == "high":
                urgency_item.setBackground(Qt.yellow)

            self.results_table.setItem(row, 3, urgency_item)

        self.results_table.resizeColumnsToContents()

        # Display red flags
        red_flags = result.get("red_flags", [])
        if red_flags:
            self.red_flags_text.setPlainText("• " + "\n• ".join(red_flags))
            self.red_flags_group.setVisible(True)
        else:
            self.red_flags_group.setVisible(False)

        # Display recommended tests
        tests = result.get("recommended_tests", [])
        if tests:
            self.tests_text.setPlainText("• " + "\n• ".join(tests))
            self.tests_group.setVisible(True)
        else:
            self.tests_group.setVisible(False)

    def _on_diagnosis_error(self, error_msg: str):
        """Handle diagnosis error."""
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        QMessageBox.critical(
            self, "Diagnosis Error", f"Failed to generate diagnosis:\n{error_msg}"
        )
