"""GUI widgets package."""

from .clinical_dashboard import ClinicalDashboardWidget
from .diagnosis_panel import DiagnosisPanelWidget
from .lab_charts import LabChartsWidget
from .patient_search import PatientSearchWidget
from .treatment_panel import TreatmentPanelWidget

__all__ = [
    "PatientSearchWidget",
    "ClinicalDashboardWidget",
    "DiagnosisPanelWidget",
    "TreatmentPanelWidget",
    "LabChartsWidget",
]
