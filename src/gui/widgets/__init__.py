"""GUI widgets package."""
from .patient_search import PatientSearchWidget
from .clinical_dashboard import ClinicalDashboardWidget
from .diagnosis_panel import DiagnosisPanelWidget
from .treatment_panel import TreatmentPanelWidget
from .lab_charts import LabChartsWidget

__all__ = [
    "PatientSearchWidget",
    "ClinicalDashboardWidget",
    "DiagnosisPanelWidget",
    "TreatmentPanelWidget",
    "LabChartsWidget",
]
