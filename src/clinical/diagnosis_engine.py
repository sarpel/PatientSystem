"""
Diagnosis Engine Module.

Provides AI-powered differential diagnosis suggestions with:
- Probability scoring
- Supporting evidence analysis
- Red flag detection
- Recommended additional tests
- ICD-10 coding integration
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.clinical.prompt_builder import create_diagnosis_prompt
from src.config.settings import settings
from src.database.app_database import ICDCode, get_app_db_session
from src.models.clinical import Diagnosis
from src.models.patient import Patient, PatientDemographics
from src.models.visit import PatientAdmission, Visit


@dataclass
class DiagnosisSuggestion:
    """Individual diagnosis suggestion with probability and evidence."""

    diagnosis: str
    icd10_code: str
    probability: float
    reasoning: str
    supporting_findings: List[str]
    red_flags: List[str]
    recommended_tests: List[str]
    urgency: str  # "urgent", "soon", "routine"


@dataclass
class DiagnosisContext:
    """Clinical context for diagnosis generation."""

    patient_info: Dict[str, Any]
    chief_complaints: List[str]
    vital_signs: Dict[str, Any]
    physical_exam: Dict[str, Any]
    lab_results: Dict[str, Any]
    past_diagnoses: List[str]
    medications: List[str]
    demographics: Dict[str, Any]


class DiagnosisEngine:
    """
    AI-powered differential diagnosis engine.

    Generates differential diagnosis suggestions based on patient data
    using structured prompts for AI models.
    """

    def __init__(self, session: Session, ai_router=None):
        """
        Initialize DiagnosisEngine.

        Args:
            session: SQLAlchemy database session
            ai_router: AI service router for complex diagnosis requests
        """
        self.session = session
        self.ai_router = ai_router
        self._icd10_mapping = self._load_icd10_mapping()
        self._red_flag_patterns = self._load_red_flag_patterns()

    def generate_differential_diagnosis(
        self,
        patient_id: int,
        chief_complaints: List[str],
        vital_signs: Optional[Dict[str, Any]] = None,
        physical_exam: Optional[Dict[str, Any]] = None,
        lab_results: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate differential diagnosis suggestions.

        Args:
            patient_id: Patient registration ID
            chief_complaints: List of chief complaints
            vital_signs: Current vital signs
            physical_exam: Physical examination findings
            lab_results: Relevant laboratory results

        Returns:
            Dictionary containing:
            - differential_diagnosis: List of diagnosis suggestions
            - urgent_conditions: List requiring immediate attention
            - recommended_tests: Additional recommended tests
            - confidence_score: Overall confidence in analysis
            - red_flags: Identified red flags
        """
        # Gather patient context
        context = self._build_diagnosis_context(
            patient_id, chief_complaints, vital_signs, physical_exam, lab_results
        )

        # Generate differential diagnosis
        if self.ai_router and len(chief_complaints) > 0:
            # Use AI for complex cases
            diagnosis_result = self._generate_ai_diagnosis(context)
        else:
            # Use rule-based approach for simple cases
            diagnosis_result = self._generate_rule_based_diagnosis(context)

        # Enhance with local analysis
        diagnosis_result = self._enhance_with_local_analysis(diagnosis_result, context)

        return diagnosis_result

    def _load_icd10_mapping(self) -> Dict[str, str]:
        """
        Load ICD-10 code mappings from app database.
        Falls back to empty dict if database is not available.
        """
        try:
            with get_app_db_session() as app_session:
                codes = app_session.query(ICDCode).filter(ICDCode.is_active).all()
                return {code.diagnosis_name_en: code.code for code in codes}
        except Exception as e:
            # Fallback to empty dict - ICD codes are optional
            logger.warning(f"Failed to load ICD codes from database: {e}")
            return {}

    def _load_red_flag_patterns(self) -> List[Dict[str, Any]]:
        """Load red flag patterns requiring urgent attention."""
        return [
            {
                "patterns": ["chest pain", "pressure", "tightness", "crushing"],
                "context": ["radiates to arm", "jaw", "neck", "sweating", "nausea"],
                "urgency": "immediate",
                "suggested_conditions": ["Myocardial Infarction", "Angina", "Aortic Dissection"],
            },
            {
                "patterns": ["shortness of breath", "difficulty breathing", "dyspnea"],
                "context": ["chest pain", "wheezing", "cyanosis", "fast heart rate"],
                "urgency": "immediate",
                "suggested_conditions": ["Pulmonary Embolism", "Heart Failure", "Asthma Attack"],
            },
            {
                "patterns": ["severe headache", "worst headache", "thunderclap"],
                "context": ["neck stiffness", "fever", "confusion", "vision changes"],
                "urgency": "immediate",
                "suggested_conditions": ["Subarachnoid Hemorrhage", "Meningitis"],
            },
            {
                "patterns": ["fever", "high temperature", "chills"],
                "context": ["rash", "difficulty breathing", "confusion", "low blood pressure"],
                "urgency": "urgent",
                "suggested_conditions": ["Sepsis", "Severe Infection"],
            },
            {
                "patterns": ["abdominal pain", "stomach pain"],
                "context": ["rigid abdomen", "fever", "vomiting", "shoulder pain"],
                "urgency": "urgent",
                "suggested_conditions": ["Appendicitis", "Pancreatitis", "Perforated Ulcer"],
            },
        ]

    def _build_diagnosis_context(
        self,
        patient_id: int,
        chief_complaints: List[str],
        vital_signs: Optional[Dict[str, Any]],
        physical_exam: Optional[Dict[str, Any]],
        lab_results: Optional[Dict[str, Any]],
    ) -> DiagnosisContext:
        """Build comprehensive diagnosis context from patient data."""
        # Get patient information with demographics in single query to prevent N+1 issues
        from sqlalchemy.orm import joinedload

        patient = self.session.execute(
            select(Patient)
            .options(joinedload(Patient.demographics))
            .where(Patient.HASTA_KAYIT_ID == patient_id)
        ).scalar_one_or_none()

        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Optimized query - directly select only what we need to avoid N+1 and cartesian product
        past_diagnoses_stmt = (
            select(Diagnosis.TANI_ACIKLAMA)
            .join(Visit)
            .join(PatientAdmission)
            .where(PatientAdmission.HASTA_KAYIT == patient_id)
            .where(Diagnosis.TANI_ACIKLAMA.isnot(None))
            .distinct()
        )

        past_diagnoses = list(self.session.execute(past_diagnoses_stmt).scalars())

        # Build demographics
        demographics = {
            "age": patient.age,
            "gender": patient.CINSIYET,
            "bmi": patient.demographics.bmi if patient.demographics else None,
            "smoking_status": patient.demographics.SIGARA_KULLANIMI if patient.demographics else None,
            "comorbidities": past_diagnoses,
        }

        return DiagnosisContext(
            patient_info={
                "id": patient_id,
                "name": patient.full_name,
                "age": patient.age,
                "gender": patient.CINSIYET,
            },
            chief_complaints=chief_complaints,
            vital_signs=vital_signs or {},
            physical_exam=physical_exam or {},
            lab_results=lab_results or {},
            past_diagnoses=past_diagnoses,
            medications=[],  # Would be populated from prescription data
            demographics=demographics,
        )

    def _generate_ai_diagnosis(self, context: DiagnosisContext) -> Dict[str, Any]:
        """Generate differential diagnosis using AI."""
        # Create structured prompt for AI
        prompt = self._create_diagnosis_prompt(context)

        try:
            # Send to AI router for processing
            ai_response = self.ai_router.process_complex_task(
                task="diagnosis",
                prompt=prompt,
                context={"complexity": "high", "domain": "medical", "language": "tr"},
            )

            # Parse AI response
            return self._parse_ai_diagnosis_response(ai_response)

        except Exception as e:
            # Fallback to rule-based approach
            print(f"AI diagnosis failed, using rule-based: {e}")
            return self._generate_rule_based_diagnosis(context)

    def _create_diagnosis_prompt(self, context: DiagnosisContext) -> str:
        """
        Create structured prompt for AI diagnosis generation using templates.
        Delegates to template-based prompt builder for cleaner separation of concerns.
        """
        return create_diagnosis_prompt(context)

    def _parse_ai_diagnosis_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI diagnosis response into structured format."""
        try:
            # Try to parse as JSON
            if ai_response.strip().startswith("["):
                suggestions = json.loads(ai_response)
            else:
                # Extract JSON from response
                json_match = re.search(r"\[.*\]", ai_response, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                else:
                    # Fallback: parse text response
                    suggestions = self._parse_text_diagnosis_response(ai_response)

            # Convert to DiagnosisSuggestion objects
            diagnosis_list = []
            for item in suggestions:
                diagnosis = DiagnosisSuggestion(
                    diagnosis=item.get("diagnosis", "Bilinmeyen"),
                    icd10_code=item.get("icd10", ""),
                    probability=float(item.get("probability", 0)),
                    reasoning=item.get("reasoning", ""),
                    supporting_findings=item.get("supporting_findings", []),
                    red_flags=item.get("red_flags", []),
                    recommended_tests=item.get("recommended_tests", []),
                    urgency=item.get("urgency", "routine"),
                )
                diagnosis_list.append(diagnosis)

            return self._format_diagnosis_result(diagnosis_list)

        except Exception as e:
            print(f"Failed to parse AI response: {e}")
            return {
                "differential_diagnosis": [],
                "urgent_conditions": [],
                "recommended_tests": [],
                "confidence_score": 0.0,
                "red_flags": [],
                "error": "AI response parsing failed",
            }

    def _parse_text_diagnosis_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse text-based AI response into structured format."""
        # Basic text parsing fallback
        suggestions = []

        lines = response.split("\n")
        current_suggestion = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to identify diagnosis line
            if any(
                keyword in line.lower()
                for keyword in ["tanı:", "diagnosis:", "olasılık:", "probability:"]
            ):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}

                # Extract diagnosis name
                diagnosis_match = re.search(
                    r"(?:tanı|diagnosis):\s*(.+?)(?:,|\n|$)", line, re.IGNORECASE
                )
                if diagnosis_match:
                    current_suggestion["diagnosis"] = diagnosis_match.group(1).strip()

                # Extract probability
                prob_match = re.search(
                    r"(?:olasılık|probability):\s*(\d+(?:\.\d+)?)\s*%?", line, re.IGNORECASE
                )
                if prob_match:
                    current_suggestion["probability"] = float(prob_match.group(1)) / 100

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    def _generate_rule_based_diagnosis(self, context: DiagnosisContext) -> Dict[str, Any]:
        """Generate differential diagnosis using rule-based approach."""
        suggestions = []

        # Analyze chief complaints
        for complaint in context.chief_complaints:
            complaint_suggestions = self._analyze_complaint(complaint, context)
            suggestions.extend(complaint_suggestions)

        # Analyze vital signs
        if context.vital_signs:
            vital_suggestions = self._analyze_vital_signs(context.vital_signs, context)
            suggestions.extend(vital_suggestions)

        # Analyze lab results
        if context.lab_results:
            lab_suggestions = self._analyze_lab_results(context.lab_results, context)
            suggestions.extend(lab_suggestions)

        # Remove duplicates and sort by probability
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        unique_suggestions.sort(key=lambda x: x.probability, reverse=True)

        return self._format_diagnosis_result(unique_suggestions)

    def _analyze_complaint(
        self, complaint: str, context: DiagnosisContext
    ) -> List[DiagnosisSuggestion]:
        """Analyze individual chief complaint for possible diagnoses."""
        suggestions = []
        complaint_lower = complaint.lower()

        # Respiratory complaints
        if any(
            keyword in complaint_lower
            for keyword in ["öksür", "cough", "balgam", "sputum", "nefes darlığı", "dyspnea"]
        ):
            suggestions.append(
                DiagnosisSuggestion(
                    diagnosis="Acute Bronchitis",
                    icd10_code="J20.9",
                    probability=0.6,
                    reasoning="Akut öksürük ve balgam şikayeti bronşiti düşündürüyor",
                    supporting_findings=[complaint],
                    red_flags=[],
                    recommended_tests=["Göğüs röntgeni", "Kan sayımı"],
                    urgency="routine",
                )
            )

            if "nefes darlığı" in complaint_lower or "dyspnea" in complaint_lower:
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="COPD Exacerbation",
                        icd10_code="J44.1",
                        probability=0.4,
                        reasoning="Nefes darlığı KOAH alevlenmesini düşündürüyor",
                        supporting_findings=[complaint],
                        red_flags=["Sürekli nefes darlığı"],
                        recommended_tests=["Pulmoner fonksiyon testi", "Arteryal kan gazı"],
                        urgency="soon",
                    )
                )

        # Chest pain complaints
        if any(
            keyword in complaint_lower
            for keyword in ["göğüs ağrısı", "chest pain", "batma", "sıkışma"]
        ):
            suggestions.append(
                DiagnosisSuggestion(
                    diagnosis="Angina Pectoris",
                    icd10_code="I20.9",
                    probability=0.5,
                    reasoning="Göğüs ağrısı koroner iskemi düşündürüyor",
                    supporting_findings=[complaint],
                    red_flags=["Radyasyon", "terleme", "bulantı"],
                    recommended_tests=["EKG", "Troponin", "EKO"],
                    urgency="urgent",
                )
            )

        # Gastrointestinal complaints
        if any(
            keyword in complaint_lower
            for keyword in ["karın ağrısı", "mide", "hazımsızlık", "bulantı"]
        ):
            suggestions.append(
                DiagnosisSuggestion(
                    diagnosis="Gastritis",
                    icd10_code="K29.70",
                    probability=0.5,
                    reasoning="Mide şikayetleri gastriti düşündürüyor",
                    supporting_findings=[complaint],
                    red_flags=["Şiddetli ağrı", "kanama"],
                    recommended_tests=["Üst GIS endoskopi", "Helikobakter testi"],
                    urgency="routine",
                )
            )

        # Headache complaints
        if any(keyword in complaint_lower for keyword in ["baş ağrısı", "headache", "migren"]):
            suggestions.append(
                DiagnosisSuggestion(
                    diagnosis="Tension Headache",
                    icd10_code="G44.2",
                    probability=0.6,
                    reasoning="Gerilim tipi baş ağrısı en sık görülen tiptir",
                    supporting_findings=[complaint],
                    red_flags=["Ani başlangıç", "şiddetli", "boynunda katılık"],
                    recommended_tests=["Nörolojik muayene"],
                    urgency="routine",
                )
            )

            if "şiddetli" in complaint_lower or "en kötü" in complaint_lower:
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Migraine",
                        icd10_code="G43.9",
                        probability=0.4,
                        reasoning="Şiddetli baş ağrısı migreni düşündürüyor",
                        supporting_findings=[complaint],
                        red_flags=["Ani başlangıç", "ateş", "bilinç bulanıklığı"],
                        recommended_tests=["BT/MR"],
                        urgency="urgent",
                    )
                )

        return suggestions

    def _analyze_vital_signs(
        self, vital_signs: Dict[str, Any], context: DiagnosisContext
    ) -> List[DiagnosisSuggestion]:
        """Analyze vital signs for diagnostic clues."""
        suggestions = []

        # Blood pressure analysis
        if "systolic" in vital_signs and "diastolic" in vital_signs:
            sbp = vital_signs["systolic"]
            dbp = vital_signs["diastolic"]

            if (
                sbp >= settings.hypertension_systolic_threshold
                or dbp >= settings.hypertension_diastolic_threshold
            ):
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Hypertension",
                        icd10_code="I10",
                        probability=0.8,
                        reasoning=f"Kan basıncı yüksek: {sbp}/{dbp} mmHg",
                        supporting_findings=[f"BP: {sbp}/{dbp}"],
                        red_flags=[],
                        recommended_tests=["Kan basıncı takibi", "EKO", "Böbrek fonksiyonları"],
                        urgency="soon",
                    )
                )

        # Fever analysis
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"]
            if temp >= settings.fever_temperature_threshold:
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Infection",
                        icd10_code="A49.9",
                        probability=0.7,
                        reasoning=f"Ateş var: {temp}°C",
                        supporting_findings=[f"Temperature: {temp}°C"],
                        red_flags=[],
                        recommended_tests=["Kan sayımı", "CRP", "Ürine bakteri"],
                        urgency="urgent",
                    )
                )

        # Heart rate analysis
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            if hr > settings.tachycardia_threshold:
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Tachycardia",
                        icd10_code="R00.0",
                        probability=0.6,
                        reasoning=f"Taşikardi: {hr} bpm",
                        supporting_findings=[f"Heart rate: {hr} bpm"],
                        red_flags=[],
                        recommended_tests=["EKG"],
                        urgency="soon",
                    )
                )

        return suggestions

    def _analyze_lab_results(
        self, lab_results: Dict[str, Any], context: DiagnosisContext
    ) -> List[DiagnosisSuggestion]:
        """Analyze laboratory results for diagnostic clues."""
        suggestions = []

        # HbA1c analysis
        if "HbA1c" in lab_results:
            hba1c = lab_results["HbA1c"]
            if hba1c >= settings.hba1c_diabetes_threshold:
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Type 2 Diabetes",
                        icd10_code="E11.9",
                        probability=0.8,
                        reasoning=f"HbA1c yüksek: {hba1c}%",
                        supporting_findings=[f"HbA1c: {hba1c}%"],
                        red_flags=[],
                        recommended_tests=["Açlık glukozu", "Lipid paneli"],
                        urgency="soon",
                    )
                )

        # CRP analysis
        if "CRP" in lab_results:
            crp = lab_results["CRP"]
            if crp > 10.0:
                red_flags = (
                    [f"CRP > {settings.crp_severe_threshold} mg/L"]
                    if crp > settings.crp_severe_threshold
                    else []
                )
                suggestions.append(
                    DiagnosisSuggestion(
                        diagnosis="Inflammation",
                        icd10_code="R68.89",
                        probability=0.7,
                        reasoning=f"CRP yüksek: {crp} mg/L",
                        supporting_findings=[f"CRP: {crp} mg/L"],
                        red_flags=red_flags,
                        recommended_tests=["Enfeksiyon odağı araştırması"],
                        urgency="urgent",
                    )
                )

        return suggestions

    def _deduplicate_suggestions(
        self, suggestions: List[DiagnosisSuggestion]
    ) -> List[DiagnosisSuggestion]:
        """Remove duplicate diagnosis suggestions."""
        seen = set()
        unique_suggestions = []

        for suggestion in suggestions:
            key = (suggestion.diagnosis, suggestion.icd10_code)
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
            else:
                # Update existing suggestion if new one has higher probability
                for existing in unique_suggestions:
                    if (
                        existing.diagnosis == suggestion.diagnosis
                        and existing.icd10_code == suggestion.icd10_code
                        and suggestion.probability > existing.probability
                    ):
                        existing.probability = suggestion.probability
                        existing.reasoning = suggestion.reasoning
                        existing.supporting_findings.extend(suggestion.supporting_findings)
                        break

        return unique_suggestions

    def _enhance_with_local_analysis(
        self, diagnosis_result: Dict[str, Any], context: DiagnosisContext
    ) -> Dict[str, Any]:
        """Enhance diagnosis result with local analysis and red flag detection."""
        # Check for red flags
        red_flags = self._detect_red_flags(context)

        # Add to existing red flags
        existing_red_flags = diagnosis_result.get("red_flags", [])
        all_red_flags = list(set(existing_red_flags + red_flags))

        # Identify urgent conditions
        urgent_conditions = [
            dx
            for dx in diagnosis_result.get("differential_diagnosis", [])
            if dx.urgency in ["urgent", "immediate"]
        ]

        # Update result
        diagnosis_result["red_flags"] = all_red_flags
        diagnosis_result["urgent_conditions"] = urgent_conditions

        return diagnosis_result

    def _detect_red_flags(self, context: DiagnosisContext) -> List[str]:
        """Detect red flags in patient presentation."""
        red_flags = []

        all_text = " ".join(
            context.chief_complaints
            + list(context.vital_signs.values())
            + list(context.physical_exam.values())
        ).lower()

        for red_flag_pattern in self._red_flag_patterns:
            for pattern in red_flag_pattern["patterns"]:
                if pattern in all_text:
                    red_flags.append(f"RED FLAG: {pattern}")
                    if red_flag_pattern["urgency"] == "immediate":
                        red_flags.append("EMERGENCY: Requires immediate medical attention")

        return red_flags

    def _format_diagnosis_result(self, suggestions: List[DiagnosisSuggestion]) -> Dict[str, Any]:
        """Format diagnosis suggestions into result structure."""
        differential_diagnosis = [
            {
                "diagnosis": dx.diagnosis,
                "icd10": dx.icd10_code,
                "probability": dx.probability,
                "reasoning": dx.reasoning,
                "supporting_findings": dx.supporting_findings,
                "red_flags": dx.red_flags,
                "recommended_tests": dx.recommended_tests,
                "urgency": dx.urgency,
            }
            for dx in suggestions
        ]

        urgent_conditions = [
            {
                "diagnosis": dx.diagnosis,
                "icd10": dx.icd10_code,
                "reasoning": dx.reasoning,
                "urgency": dx.urgency,
            }
            for dx in suggestions
            if dx.urgency in ["urgent", "immediate"]
        ]

        # Collect all recommended tests
        all_tests = set()
        for dx in suggestions:
            all_tests.update(dx.recommended_tests)

        # Calculate confidence score
        if suggestions:
            confidence_score = max(dx.probability for dx in suggestions)
        else:
            confidence_score = 0.0

        return {
            "differential_diagnosis": differential_diagnosis,
            "urgent_conditions": urgent_conditions,
            "recommended_tests": list(all_tests),
            "confidence_score": confidence_score,
            "red_flags": [],  # Will be added by enhancement step
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def get_diagnosis_report(self, patient_id: int, diagnosis_result: Dict[str, Any]) -> str:
        """
        Generate formatted diagnosis report.

        Args:
            patient_id: Patient registration ID
            diagnosis_result: Result from generate_differential_diagnosis

        Returns:
            Human-readable formatted diagnosis report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("DIFFERENTIAL DIAGNOSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Analysis Time: {diagnosis_result.get('analysis_timestamp', 'Unknown')}")
        lines.append(f"Confidence Score: {diagnosis_result.get('confidence_score', 0):.1%}")
        lines.append("")

        # Urgent conditions first
        urgent = diagnosis_result.get("urgent_conditions", [])
        if urgent:
            lines.append("🚨 URGENT CONDITIONS 🚨")
            for condition in urgent:
                urgency_icon = (
                    "🔴 IMMEDIATE" if condition.get("urgency") == "immediate" else "🟠 URGENT"
                )
                lines.append(
                    f"  {urgency_icon}: {condition['diagnosis']} ({condition.get('icd10', '')})"
                )
                lines.append(f"    Reasoning: {condition.get('reasoning', 'N/A')}")
            lines.append("")

        # Red flags
        red_flags = diagnosis_result.get("red_flags", [])
        if red_flags:
            lines.append("⚠️ RED FLAGS")
            for flag in red_flags:
                lines.append(f"  • {flag}")
            lines.append("")

        # Differential diagnosis
        differential = diagnosis_result.get("differential_diagnosis", [])
        if differential:
            lines.append("DIFFERENTIAL DIAGNOSIS")
            lines.append("-" * 40)
            for i, dx in enumerate(differential[:5], 1):  # Top 5
                prob_pct = dx.get("probability", 0) * 100
                urgency = (
                    f" [{dx.get('urgency', 'routine').upper()}]"
                    if dx.get("urgency") != "routine"
                    else ""
                )
                lines.append(f"{i}. {dx['diagnosis']} ({dx.get('icd10', '')}) {urgency}")
                lines.append(f"   Probability: {prob_pct:.1f}%")
                if dx.get("reasoning"):
                    lines.append(f"   Reasoning: {dx['reasoning']}")
                if dx.get("supporting_findings"):
                    findings = ", ".join(dx["supporting_findings"])
                    lines.append(f"   Supporting: {findings}")
                lines.append("")

        # Recommended tests
        tests = diagnosis_result.get("recommended_tests", [])
        if tests:
            lines.append("RECOMMENDED INVESTIGATIONS")
            lines.append("-" * 40)
            for test in tests:
                lines.append(f"  • {test}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
