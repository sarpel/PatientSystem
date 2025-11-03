"""Clinical dashboard with tabbed interface for patient data."""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ...database.connection import get_session
from ...models.patient import Patient
from .diagnosis_panel import DiagnosisPanelWidget
from .treatment_panel import TreatmentPanelWidget
from .lab_charts import LabChartsWidget


class ClinicalDashboardWidget(QWidget):
    """Tabbed clinical dashboard for patient information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tckn: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Patient header
        self.patient_header = QLabel("No patient selected")
        self.patient_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background-color: #3b82f6;
            color: white;
            border-radius: 4px;
        """)
        layout.addWidget(self.patient_header)

        # Tab widget
        self.tabs = QTabWidget()

        # Diagnosis tab
        self.diagnosis_panel = DiagnosisPanelWidget()
        self.tabs.addTab(self.diagnosis_panel, "Diagnosis")

        # Treatment tab
        self.treatment_panel = TreatmentPanelWidget()
        self.tabs.addTab(self.treatment_panel, "Treatment")

        # Lab results tab
        self.lab_charts = LabChartsWidget()
        self.tabs.addTab(self.lab_charts, "Lab Results")

        # Medications tab (placeholder)
        medications_placeholder = QLabel("Medication history will be displayed here")
        medications_placeholder.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(medications_placeholder, "Medications")

        # History tab (placeholder)
        history_placeholder = QLabel("Visit history will be displayed here")
        history_placeholder.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(history_placeholder, "History")

        layout.addWidget(self.tabs)

    def load_patient(self, tckn: str):
        """Load patient data into dashboard."""
        self.current_tckn = tckn

        try:
            with get_session() as session:
                # Convert tckn string to integer for comparison
                tckn_int = int(tckn) if tckn.isdigit() else None
                patient = session.query(Patient).filter(
                    Patient.HASTA_KIMLIK_NO == tckn_int
                ).first()

                if not patient:
                    QMessageBox.warning(
                        self,
                        "Patient Not Found",
                        f"No patient found with TCKN: {tckn}"
                    )
                    return

                # Update header
                full_name = f"{patient.AD or ''} {patient.SOYAD or ''}".strip()
                age = patient.age if patient.age else "Unknown"
                gender_map = {1: "Male", 2: "Female"}
                gender = gender_map.get(patient.CINSIYET, "Unknown")

                self.patient_header.setText(
                    f"{full_name} | Age: {age} | Gender: {gender} | TCKN: {tckn}"
                )

                # Load data in each panel
                self.diagnosis_panel.load_patient(tckn)
                self.treatment_panel.load_patient(tckn)
                self.lab_charts.load_patient(tckn)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load patient data:\n{str(e)}"
            )
