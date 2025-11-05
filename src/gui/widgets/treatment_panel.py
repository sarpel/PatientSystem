"""Treatment recommendation panel with AI-powered suggestions."""

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

from ...clinical.treatment_engine import TreatmentEngine
from ...database.connection import get_session


class TreatmentWorker(QThread):
    """Background worker for AI treatment recommendation."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, tckn: str, diagnosis: str, model: Optional[str] = None):
        super().__init__()
        self.tckn = tckn
        self.diagnosis = diagnosis
        self.model = model

    def run(self):
        """Run treatment generation in background thread."""
        try:
            with get_session() as session:
                engine = TreatmentEngine(session)
                result = asyncio.run(
                    engine.suggest_treatment_ai(
                        tckn=self.tckn,
                        diagnosis=self.diagnosis,
                        preferred_provider=self.model,
                    )
                )
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TreatmentPanelWidget(QWidget):
    """Panel for AI-powered treatment recommendations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tckn: Optional[str] = None
        self.worker: Optional[TreatmentWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Diagnosis input
        input_group = QGroupBox("Diagnosis")
        input_layout = QVBoxLayout(input_group)

        self.diagnosis_input = QTextEdit()
        self.diagnosis_input.setPlaceholderText(
            "Enter confirmed diagnosis or differential diagnosis...\n"
            "Example: Acute Coronary Syndrome (ACS)"
        )
        self.diagnosis_input.setMaximumHeight(80)
        input_layout.addWidget(self.diagnosis_input)

        # Model selection and generate button
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("AI Model:"))

        self.model_combo = QComboBox()
        self.model_combo.addItems(
            ["Auto (Smart Routing)", "Claude", "GPT-4o", "Gemini", "Ollama"]
        )
        controls_layout.addWidget(self.model_combo)

        controls_layout.addStretch()

        self.generate_button = QPushButton("Generate Treatment Plan")
        self.generate_button.clicked.connect(self._generate_treatment)
        controls_layout.addWidget(self.generate_button)

        input_layout.addLayout(controls_layout)
        layout.addWidget(input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Treatment recommendations
        recommendations_group = QGroupBox("Treatment Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)

        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(3)
        self.recommendations_table.setHorizontalHeaderLabels(
            ["Medication", "Dosage", "Duration"]
        )
        self.recommendations_table.setEditTriggers(QTableWidget.NoEditTriggers)
        recommendations_layout.addWidget(self.recommendations_table)

        layout.addWidget(recommendations_group)

        # Clinical guidelines
        guidelines_group = QGroupBox("Clinical Guidelines")
        guidelines_layout = QVBoxLayout(guidelines_group)

        self.guidelines_text = QTextEdit()
        self.guidelines_text.setReadOnly(True)
        self.guidelines_text.setMaximumHeight(100)
        guidelines_layout.addWidget(self.guidelines_text)

        layout.addWidget(guidelines_group)

        # Follow-up recommendations
        followup_group = QGroupBox("Follow-up Plan")
        followup_layout = QVBoxLayout(followup_group)

        self.followup_text = QTextEdit()
        self.followup_text.setReadOnly(True)
        self.followup_text.setMaximumHeight(80)
        followup_layout.addWidget(self.followup_text)

        layout.addWidget(followup_group)

    def load_patient(self, tckn: str):
        """Load patient context."""
        self.current_tckn = tckn
        self.diagnosis_input.clear()
        self.recommendations_table.setRowCount(0)
        self.guidelines_text.clear()
        self.followup_text.clear()

    def _generate_treatment(self):
        """Generate treatment recommendations using AI."""
        if not self.current_tckn:
            QMessageBox.warning(self, "No Patient", "Please select a patient first")
            return

        diagnosis = self.diagnosis_input.toPlainText().strip()
        if not diagnosis:
            QMessageBox.warning(self, "No Diagnosis", "Please enter diagnosis")
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
        self.generate_button.setEnabled(False)

        # Start worker thread
        self.worker = TreatmentWorker(self.current_tckn, diagnosis, model)
        self.worker.finished.connect(self._on_treatment_complete)
        self.worker.error.connect(self._on_treatment_error)
        self.worker.start()

    def _on_treatment_complete(self, result: Dict[str, Any]):
        """Handle treatment generation completion."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)

        # Display medication recommendations
        medications = result.get("medications", [])
        self.recommendations_table.setRowCount(len(medications))

        for row, med in enumerate(medications):
            self.recommendations_table.setItem(
                row, 0, QTableWidgetItem(med.get("name", ""))
            )
            self.recommendations_table.setItem(
                row, 1, QTableWidgetItem(med.get("dosage", ""))
            )
            self.recommendations_table.setItem(
                row, 2, QTableWidgetItem(med.get("duration", ""))
            )

        self.recommendations_table.resizeColumnsToContents()

        # Display clinical guidelines
        guidelines = result.get("clinical_guidelines", "")
        self.guidelines_text.setPlainText(guidelines)

        # Display follow-up plan
        followup = result.get("followup_plan", "")
        self.followup_text.setPlainText(followup)

    def _on_treatment_error(self, error_msg: str):
        """Handle treatment generation error."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        QMessageBox.critical(
            self, "Treatment Error", f"Failed to generate treatment plan:\n{error_msg}"
        )
