"""
Patient Summarizer Module.

Provides comprehensive patient summaries including:
- Demographics
- Recent visits (last 12 months)
- Active diagnoses (ICD-10)
- Active medications
- Allergy warnings
- Lab results summary
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.models.clinical import Diagnosis, Prescription
from src.models.patient import Patient, PatientDemographics
from src.models.visit import PatientAdmission, Visit


class PatientSummarizer:
    """
    Generate comprehensive patient summaries for clinical decision support.

    Aggregates patient information from multiple tables to provide
    a complete clinical picture.
    """

    def __init__(self, session: Session):
        """
        Initialize PatientSummarizer.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def get_patient_summary(self, patient_id: int, months_back: int = 12) -> Dict[str, Any]:
        """
        Get comprehensive patient summary.

        Args:
            patient_id: Patient registration ID
            months_back: Number of months to look back for visits (default: 12)

        Returns:
            Dictionary containing patient summary with keys:
            - demographics: Patient demographics
            - recent_visits: List of recent visits
            - active_diagnoses: List of active diagnoses
            - active_prescriptions: List of active prescriptions
            - allergies: List of allergies
            - latest_vitals: Most recent vital signs
            - summary_stats: Summary statistics
        """
        # Get patient
        patient = self._get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=months_back * 30)

        # Gather all components
        summary = {
            "demographics": self._get_demographics(patient),
            "recent_visits": self._get_recent_visits(patient_id, threshold_date),
            "active_diagnoses": self._get_active_diagnoses(patient_id),
            "active_prescriptions": self._get_active_prescriptions(patient_id),
            "allergies": self._get_allergies(patient),
            "latest_vitals": self._get_latest_vitals(patient_id),
            "summary_stats": self._get_summary_stats(patient_id, threshold_date),
        }

        return summary

    def _get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID."""
        stmt = select(Patient).where(Patient.HASTA_KAYIT_ID == patient_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def _get_demographics(self, patient: Patient) -> Dict[str, Any]:
        """Extract patient demographics."""
        demographics = {
            "patient_id": patient.HASTA_KAYIT_ID,
            "full_name": patient.full_name,
            "birth_date": patient.DOGUM_TARIHI.isoformat() if patient.DOGUM_TARIHI else None,
            "age": patient.age,
            "gender": patient.CINSIYET,
            "tc_number": patient.TC_KIMLIK_NO,
            "blood_type": patient.KAN_GRUBU,
            "is_deceased": patient.is_deceased,
        }

        # Add demographics if available
        if patient.demographics:
            demo = patient.demographics
            demographics.update(
                {
                    "weight_kg": demo.AGIRLIK / 1000 if demo.AGIRLIK else None,
                    "height_cm": demo.BOY,
                    "bmi": demo.bmi,
                    "bmi_category": demo.bmi_category,
                    "smoking_status": demo.SIGARA,
                    "alcohol_use": demo.ALKOL_KULLANIMI,
                }
            )

        return demographics

    def _get_recent_visits(self, patient_id: int, threshold_date: datetime) -> List[Dict[str, Any]]:
        """Get recent patient visits."""
        # Get admissions for this patient
        stmt = (
            select(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .where(PatientAdmission.KABUL_TARIHI >= threshold_date)
            .order_by(desc(PatientAdmission.KABUL_TARIHI))
            .limit(10)
        )

        visits = self.session.execute(stmt).scalars().all()

        return [
            {
                "visit_id": visit.MUAYENE_ID,
                "admission_id": visit.HASTA_KABUL,
                "visit_type": visit.MUAYENE_TURU,
                "primary_diagnosis": visit.ANA_TANI,
                "complaint": visit.SIKAYETI,
                "blood_pressure": visit.blood_pressure_str,
                "pulse": visit.NABIZ,
                "temperature": float(visit.VUCUT_ISISI) if visit.VUCUT_ISISI else None,
                "weight_kg": visit.AGIRLIK / 1000 if visit.AGIRLIK else None,
                "bmi": visit.bmi,
            }
            for visit in visits
        ]

    def _get_active_diagnoses(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get active diagnoses for patient."""
        # Get all visits for patient
        stmt = (
            select(Diagnosis)
            .join(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .where(Diagnosis.DURUM == 1)  # Active
            .order_by(desc(Diagnosis.TANI_TARIHI))
        )

        diagnoses = self.session.execute(stmt).scalars().all()

        return [
            {
                "diagnosis_id": dx.MUAYENE_EK_TANI_ID,
                "visit_id": dx.MUAYENE,
                "icd10_code": dx.TANI,
                "diagnosis_type": dx.TANI_TURU,
                "description": dx.TANI_ACIKLAMA,
                "severity": dx.SIDDET,
                "diagnosis_date": dx.TANI_TARIHI.isoformat() if dx.TANI_TARIHI else None,
                "is_active": dx.is_active,
            }
            for dx in diagnoses
        ]

    def _get_active_prescriptions(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get active prescriptions for patient."""
        stmt = (
            select(Prescription)
            .where(Prescription.HASTA_KAYIT == patient_id)
            .where(Prescription.DURUM == 1)  # Active
            .order_by(desc(Prescription.RECETE_TARIHI))
            .limit(20)
        )

        prescriptions = self.session.execute(stmt).scalars().all()

        return [
            {
                "prescription_id": rx.RECETE_ID,
                "visit_id": rx.MUAYENE,
                "prescription_type": rx.RECETE_TURU,
                "prescription_date": rx.RECETE_TARIHI.isoformat(),
                "prescription_number": rx.RECETE_NO,
                "physician_id": rx.HEKIM,
                "diagnosis_code": rx.TANI,
                "notes": rx.ACIKLAMA,
                "esy_number": rx.ESY_RECETE_NO,
            }
            for rx in prescriptions
        ]

    def _get_allergies(self, patient: Patient) -> List[str]:
        """Get patient allergies."""
        allergies = []

        if patient.ILAC_ALERJISI:
            allergies.append(f"Drug allergy: {patient.ILAC_ALERJISI}")

        if patient.demographics:
            demo = patient.demographics
            if demo.ILAC_ALERJISI:
                allergies.append(f"Drug allergy (demographics): {demo.ILAC_ALERJISI}")

        return allergies

    def _get_latest_vitals(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get most recent vital signs."""
        stmt = (
            select(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .order_by(desc(PatientAdmission.KABUL_TARIHI))
            .limit(1)
        )

        visit = self.session.execute(stmt).scalar_one_or_none()

        if not visit:
            return None

        return {
            "blood_pressure_systolic": visit.SISTOLIK_KAN_BASINCI,
            "blood_pressure_diastolic": visit.DIASTOLIK_KAN_BASINCI,
            "blood_pressure_str": visit.blood_pressure_str,
            "pulse": visit.NABIZ,
            "temperature_celsius": float(visit.VUCUT_ISISI) if visit.VUCUT_ISISI else None,
            "weight_kg": visit.AGIRLIK / 1000 if visit.AGIRLIK else None,
            "height_cm": visit.BOY,
            "bmi": visit.bmi,
            "waist_circumference_cm": visit.BEL_CEVRESI,
            "hip_circumference_cm": visit.KALCA_CEVRESI,
            "waist_hip_ratio": visit.waist_hip_ratio,
            "glasgow_coma_scale": visit.GLASGOW_KOMA_SKALASI,
        }

    def _get_summary_stats(self, patient_id: int, threshold_date: datetime) -> Dict[str, Any]:
        """Get summary statistics."""
        # Count visits
        visit_stmt = (
            select(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .where(PatientAdmission.KABUL_TARIHI >= threshold_date)
        )
        visit_count = len(self.session.execute(visit_stmt).scalars().all())

        # Count active diagnoses
        diagnosis_stmt = (
            select(Diagnosis)
            .join(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .where(Diagnosis.DURUM == 1)
        )
        diagnosis_count = len(self.session.execute(diagnosis_stmt).scalars().all())

        # Count active prescriptions
        prescription_stmt = (
            select(Prescription)
            .where(Prescription.HASTA_KAYIT == patient_id)
            .where(Prescription.DURUM == 1)
        )
        prescription_count = len(self.session.execute(prescription_stmt).scalars().all())

        return {
            "recent_visit_count": visit_count,
            "active_diagnosis_count": diagnosis_count,
            "active_prescription_count": prescription_count,
            "period_months": 12,
        }

    def get_formatted_summary(self, patient_id: int) -> str:
        """
        Get patient summary as formatted text.

        Args:
            patient_id: Patient registration ID

        Returns:
            Human-readable formatted summary
        """
        summary = self.get_patient_summary(patient_id)

        lines = []
        lines.append("=" * 60)
        lines.append("PATIENT SUMMARY")
        lines.append("=" * 60)
        lines.append("")

        # Demographics
        demo = summary["demographics"]
        lines.append("DEMOGRAPHICS:")
        lines.append(f"  Name: {demo['full_name']}")
        lines.append(f"  Age: {demo['age']} years")
        lines.append(f"  Gender: {demo['gender']}")
        if demo.get("bmi"):
            lines.append(f"  BMI: {demo['bmi']} ({demo.get('bmi_category', 'N/A')})")
        lines.append("")

        # Allergies
        if summary["allergies"]:
            lines.append("ALLERGIES:")
            for allergy in summary["allergies"]:
                lines.append(f"  ⚠️  {allergy}")
            lines.append("")

        # Latest vitals
        if summary["latest_vitals"]:
            vitals = summary["latest_vitals"]
            lines.append("LATEST VITAL SIGNS:")
            if vitals.get("blood_pressure_str"):
                lines.append(f"  BP: {vitals['blood_pressure_str']} mmHg")
            if vitals.get("pulse"):
                lines.append(f"  Pulse: {vitals['pulse']} bpm")
            if vitals.get("temperature_celsius"):
                lines.append(f"  Temperature: {vitals['temperature_celsius']}°C")
            if vitals.get("bmi"):
                lines.append(f"  BMI: {vitals['bmi']}")
            lines.append("")

        # Summary stats
        stats = summary["summary_stats"]
        lines.append("SUMMARY (Last 12 months):")
        lines.append(f"  Visits: {stats['recent_visit_count']}")
        lines.append(f"  Active Diagnoses: {stats['active_diagnosis_count']}")
        lines.append(f"  Active Prescriptions: {stats['active_prescription_count']}")
        lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
