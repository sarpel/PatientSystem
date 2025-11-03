"""
Treatment Engine Module.

Provides AI-powered treatment recommendations with:
- Pharmacological treatment suggestions
- Lifestyle recommendations
- Lab monitoring plans
- Consultation recommendations
- Contraindication checking
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.patient import Patient, PatientDemographics
from src.models.visit import Visit
from src.models.clinical import Prescription


@dataclass
class MedicationRecommendation:
    """Individual medication recommendation."""
    drug_name: str
    generic_name: str
    dosage: str
    frequency: str
    duration: str
    route: str
    rationale: str
    contraindications: List[str]
    monitoring: List[str]
    cost: str
    priority: int
    pregnancy_category: Optional[str]


@dataclass
class LifestyleRecommendation:
    """Lifestyle modification recommendation."""
    category: str  # "diet", "exercise", "habits", "other"
    recommendation: str
    details: str
    priority: int
    rationale: str
    expected_outcome: str


@dataclass
class MonitoringPlan:
    """Laboratory and clinical monitoring plan."""
    test_name: str
    frequency: str
    target_range: str
    action_threshold: str
    rationale: str


@dataclass
class ConsultationRecommendation:
    """Specialist consultation recommendation."""
    specialty: str
    urgency: str  # "routine", "soon", "urgent"
    reason: str
    specific_questions: List[str]


class TreatmentEngine:
    """
    AI-powered treatment recommendation engine.

    Generates comprehensive treatment plans based on diagnosis
    and patient characteristics using structured AI prompts.
    """

    def __init__(self, session: Session, ai_router=None):
        """
        Initialize TreatmentEngine.

        Args:
            session: SQLAlchemy database session
            ai_router: AI service router for complex treatment recommendations
        """
        self.session = session
        self.ai_router = ai_router
        self._drug_database = self._load_drug_database()
        self._treatment_guidelines = self._load_treatment_guidelines()

    def generate_treatment_plan(
        self,
        patient_id: int,
        diagnosis: str,
        diagnosis_details: Optional[Dict[str, Any]] = None,
        patient_factors: Optional[Dict[str, Any]] = None,
        current_medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive treatment plan.

        Args:
            patient_id: Patient registration ID
            diagnosis: Primary diagnosis
            diagnosis_details: Additional diagnosis information
            patient_factors: Patient-specific factors (age, comorbidities, etc.)
            current_medications: List of current medications

        Returns:
            Dictionary containing:
            - pharmacological: Medication recommendations
            - lifestyle: Lifestyle modification recommendations
            - monitoring: Laboratory monitoring plan
            - consultations: Specialist consultation recommendations
            - contraindications: Treatment contraindications
            - follow_up: Follow-up schedule
        """
        # Gather patient information
        patient_context = self._build_patient_context(patient_id, current_medications)

        # Generate treatment recommendations
        if self.ai_router:
            # Use AI for complex cases
            treatment_result = self._generate_ai_treatment(
                diagnosis, diagnosis_details, patient_context, patient_factors
            )
        else:
            # Use rule-based approach
            treatment_result = self._generate_rule_based_treatment(
                diagnosis, diagnosis_details, patient_context, patient_factors
            )

        # Check contraindications
        treatment_result = self._check_contraindications(treatment_result, patient_context)

        return treatment_result

    def _load_drug_database(self) -> Dict[str, Dict[str, Any]]:
        """Load drug information database."""
        return {
            # Diabetes medications
            "Metformin": {
                "generic_name": "Metformin HCl",
                "class": "Biguanide",
                "indications": ["Type 2 Diabetes"],
                "dosage_forms": ["500mg", "850mg", "1000mg"],
                "typical_dosage": "500-1000mg 2x1",
                "contraindications": ["eGFR <30 mL/min", "lactic acidosis history", "severe liver disease"],
                "monitoring": ["Renal function q3-6mo", "B12 yearly"],
                "pregnancy_category": "B",
                "cost": "Low",
                "mechanism": "Decreases hepatic glucose production, improves insulin sensitivity",
            },
            "Insulin Glargine": {
                "generic_name": "Insulin Glargine",
                "class": "Long-acting insulin",
                "indications": ["Type 1 Diabetes", "Type 2 Diabetes"],
                "dosage_forms": ["U-100", "U-300"],
                "typical_dosage": "10-20 units daily",
                "contraindications": ["hypoglycemia"],
                "monitoring": ["Blood glucose", "HbA1c q3mo"],
                "pregnancy_category": "B",
                "cost": "High",
                "mechanism": "Long-acting insulin analog",
            },

            # Hypertension medications
            "Lisinopril": {
                "generic_name": "Lisinopril",
                "class": "ACE Inhibitor",
                "indications": ["Hypertension", "Heart Failure"],
                "dosage_forms": ["5mg", "10mg", "20mg", "40mg"],
                "typical_dosage": "10-40mg 1x1",
                "contraindications": ["pregnancy", "angioedema history", "bilateral renal artery stenosis"],
                "monitoring": ["Blood pressure", "Renal function", "Potassium"],
                "pregnancy_category": "D",
                "cost": "Low",
                "mechanism": "ACE inhibition, reduces angiotensin II production",
            },
            "Amlodipine": {
                "generic_name": "Amlodipine Besylate",
                "class": "Calcium Channel Blocker",
                "indications": ["Hypertension", "Angina"],
                "dosage_forms": ["2.5mg", "5mg", "10mg"],
                "typical_dosage": "5-10mg 1x1",
                "contraindications": ["severe aortic stenosis"],
                "monitoring": ["Blood pressure", "Heart rate", "Edema"],
                "pregnancy_category": "C",
                "cost": "Low",
                "mechanism": "L-type calcium channel blocker",
            },

            # Lipid-lowering medications
            "Atorvastatin": {
                "generic_name": "Atorvastatin Calcium",
                "class": "Statin",
                "indications": ["Hyperlipidemia", "Cardiovascular prevention"],
                "dosage_forms": ["10mg", "20mg", "40mg", "80mg"],
                "typical_dosage": "10-80mg 1x1",
                "contraindications": ["active liver disease", "pregnancy"],
                "monitoring": ["Liver enzymes", "CK if symptoms"],
                "pregnancy_category": "X",
                "cost": "Low",
                "mechanism": "HMG-CoA reductase inhibitor",
            },

            # NSAIDs
            "Ibuprofen": {
                "generic_name": "Ibuprofen",
                "class": "NSAID",
                "indications": ["Pain", "Inflammation", "Fever"],
                "dosage_forms": ["200mg", "400mg", "600mg", "800mg"],
                "typical_dosage": "200-800mg 3-4x1",
                "contraindications": ["active ulcer disease", "severe renal impairment", "late pregnancy"],
                "monitoring": ["Renal function if long-term", "GI symptoms"],
                "pregnancy_category": "D (3rd trimester)",
                "cost": "Low",
                "mechanism": "COX inhibition",
            },

            # Antibiotics
            "Amoxicillin": {
                "generic_name": "Amoxicillin",
                "class": "Penicillin",
                "indications": ["Bacterial infections"],
                "dosage_forms": ["250mg", "500mg", "875mg"],
                "typical_dosage": "500mg 3x1",
                "contraindications": ["penicillin allergy"],
                "monitoring": ["Allergic reactions", "Renal function if impaired"],
                "pregnancy_category": "B",
                "cost": "Low",
                "mechanism": "Beta-lactam antibiotic, cell wall synthesis inhibitor",
            },

            # Proton pump inhibitors
            "Omeprazole": {
                "generic_name": "Omeprazole",
                "class": "Proton Pump Inhibitor",
                "indications": ["GERD", "Peptic ulcer", "H. pylori"],
                "dosage_forms": ["10mg", "20mg", "40mg"],
                "typical_dosage": "20-40mg 1x1",
                "contraindications": ["rare PPI allergy"],
                "monitoring": ["Magnesium, B12 if long-term"],
                "pregnancy_category": "C",
                "cost": "Low",
                "mechanism": "H+/K+ ATPase inhibitor",
            },
        }

    def _load_treatment_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load clinical treatment guidelines."""
        return {
            "Type 2 Diabetes": {
                "first_line": ["Metformin"],
                "second_line": ["SGLT2i", "GLP-1 RA", "DPP-4i", "Sulfonylurea", "Insulin"],
                "lifestyle": ["Weight loss", "Regular exercise", "Diet modification"],
                "monitoring": ["HbA1c q3mo", "Renal function q6mo", "Lipids yearly", "Eye exam yearly"],
                "targets": {
                    "HbA1c": "<7.0%",
                    "BP": "<130/80 mmHg",
                    "LDL": "<100 mg/dL",
                },
                "consultations": ["Endocrinology if complex", "Ophthalmology yearly", "Podiatry yearly", "Nephrology if eGFR <60"],
            },
            "Hypertension": {
                "first_line": ["ACEi/ARB", "CCB", "Thiazide diuretic"],
                "second_line": ["Beta blocker", "Mineralocorticoid receptor antagonist"],
                "lifestyle": ["DASH diet", "Sodium restriction", "Exercise", "Weight loss", "Limit alcohol"],
                "monitoring": ["BP q1-3mo", "Renal function", "Electrolytes", "Lipids"],
                "targets": {
                    "BP": "<130/80 mmHg",
                },
                "consultations": ["Cardiology if resistant", "Nephrology if renal involvement"],
            },
            "Hyperlipidemia": {
                "first_line": ["High-intensity statin"],
                "second_line": ["Ezetimibe", "PCSK9 inhibitor", "Bempedoic acid"],
                "lifestyle": ["Heart-healthy diet", "Exercise", "Weight management", "Smoking cessation"],
                "monitoring": ["Lipids q3-12mo", "Liver enzymes", "CK if symptoms"],
                "targets": {
                    "LDL": "Individualized based on risk",
                },
                "consultations": ["Cardiology if high risk", "Lipid specialist if refractory"],
            },
            "Depression": {
                "first_line": ["SSRI", "SNRI", "Bupropion"],
                "second_line": ["TCA", "MAOI", "Augmentation strategies"],
                "lifestyle": ["Regular exercise", "Sleep hygiene", "Stress management", "Social support"],
                "monitoring": ["PHQ-9 regularly", "Suicide risk assessment", "Side effects"],
                "targets": {
                    "PHQ-9": "<5 remission",
                },
                "consultations": ["Psychiatry if severe", "Psychotherapy referral"],
            },
            "COPD": {
                "first_line": ["LABA/LAMA inhaler", "SABA prn"],
                "second_line": ["ICS inhaler", "Roflumilast", "Theophylline"],
                "lifestyle": ["Smoking cessation", "Pulmonary rehab", "Vaccinations", "Exercise"],
                "monitoring": ["Spirometry yearly", "Oxygen saturation", "Exacerbations"],
                "targets": {
                    "FEV1": "Stabilize/slow decline",
                },
                "consultations": ["Pulmonology", "Smoking cessation program"],
            },
        }

    def _build_patient_context(self, patient_id: int, current_medications: List[str]) -> Dict[str, Any]:
        """Build patient context for treatment planning."""
        patient = self.session.execute(
            select(Patient).where(Patient.HASTA_KAYIT_ID == patient_id)
        ).scalar_one_or_none()

        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Get current prescriptions if not provided
        if current_medications is None:
            prescriptions = self.session.execute(
                select(Prescription)
                .where(Prescription.HASTA_KAYIT == patient_id)
                .where(Prescription.DURUM == 1)  # Active
            ).scalars().all()
            current_medications = [rx.ACIKLAMA for rx in prescriptions if rx.ACIKLAMA]

        return {
            "patient_id": patient_id,
            "age": patient.age,
            "gender": patient.CINSIYET,
            "bmi": patient.demographics.bmi if patient.demographics else None,
            "egfr": None,  # Would come from lab data
            "creatinine": None,  # Would come from lab data
            "liver_function": None,  # Would come from lab data
            "allergies": patient.ILAC_ALERJISI,
            "current_medications": current_medications,
            "comorbidities": [],  # Would come from diagnosis data
            "smoking_status": patient.demographics.SIGARA if patient.demographics else None,
            "alcohol_use": patient.demographics.ALKOL_KULLANIMI if patient.demographics else None,
        }

    def _generate_ai_treatment(
        self,
        diagnosis: str,
        diagnosis_details: Optional[Dict[str, Any]],
        patient_context: Dict[str, Any],
        patient_factors: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate treatment plan using AI."""
        prompt = self._create_treatment_prompt(
            diagnosis, diagnosis_details, patient_context, patient_factors
        )

        try:
            ai_response = self.ai_router.process_complex_task(
                task="treatment",
                prompt=prompt,
                context={
                    "complexity": "high",
                    "domain": "medical",
                    "language": "tr"
                }
            )

            return self._parse_ai_treatment_response(ai_response)

        except Exception as e:
            print(f"AI treatment failed, using rule-based: {e}")
            return self._generate_rule_based_treatment(
                diagnosis, diagnosis_details, patient_context, patient_factors
            )

    def _create_treatment_prompt(
        self,
        diagnosis: str,
        diagnosis_details: Optional[Dict[str, Any]],
        patient_context: Dict[str, Any],
        patient_factors: Optional[Dict[str, Any]]
    ) -> str:
        """Create structured prompt for AI treatment generation."""
        prompt = """Tanı: {diagnosis}
Hasta özellikleri:
- Yaş: {age} yıl
- Cinsiyet: {gender}
- BMI: {bmi}
- Sigara: {smoking}
- Mevcut ilaçlar: {medications}
- Alerjiler: {allergies}

Tanı detayları: {diagnosis_details}

Lütfen tedavi planı öner. Aşağıdaki kategorilerde önerilerde bulun:

1. FARMAKOLOJİK TEDAVİ:
   - İlaç adı, doz, sıklık, süre
   - Başlangıç dozu ve doz ayarı
   - Kontrendikasyonlar
   - Takip planı
   - Her öneri için priorite (1-3)

2. YAŞAM TARZI ÖNERİLERİ:
   - Diyet önerileri
   - Egzersiz programı
   - Yaşam tarzı değişiklikleri
   - Her öneri için priorite

3. LABORATUVAR TAKİBİ:
   - Hangi testler, hangi sıklıkla
   - Hedef değerler
   - Aksiyon eşiği

4. KONSÜLTASYON GEREKSİNİMİ:
   - Hangi uzmana
   - Aciliyet durumu
   - Spesifik sorular

Format: JSON olarak dön.
""".format(
            diagnosis=diagnosis,
            age=patient_context.get("age", "Bilinmiyor"),
            gender=patient_context.get("gender", "Bilinmiyor"),
            bmi=str(patient_context.get("bmi", "Bilinmiyor")),
            smoking=patient_context.get("smoking_status", "Bilinmiyor"),
            medications=", ".join(patient_context.get("current_medications", [])) or "Yok",
            allergies=patient_context.get("allergies", "Yok"),
            diagnosis_details=str(diagnosis_details) if diagnosis_details else "Ek detay yok"
        )

        return prompt

    def _parse_ai_treatment_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI treatment response into structured format."""
        try:
            # Try to parse as JSON
            if ai_response.strip().startswith('{'):
                result = json.loads(ai_response)
            else:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fallback to rule-based
                    return self._get_default_treatment_result()

            # Ensure all required keys exist
            result.setdefault("pharmacological", [])
            result.setdefault("lifestyle", [])
            result.setdefault("monitoring", [])
            result.setdefault("consultations", [])
            result.setdefault("contraindications", [])
            result.setdefault("follow_up", {})

            return result

        except Exception as e:
            print(f"Failed to parse AI treatment response: {e}")
            return self._get_default_treatment_result()

    def _get_default_treatment_result(self) -> Dict[str, Any]:
        """Get default treatment result structure."""
        return {
            "pharmacological": [],
            "lifestyle": [],
            "monitoring": [],
            "consultations": [],
            "contraindications": [],
            "follow_up": {},
            "error": "Treatment parsing failed"
        }

    def _generate_rule_based_treatment(
        self,
        diagnosis: str,
        diagnosis_details: Optional[Dict[str, Any]],
        patient_context: Dict[str, Any],
        patient_factors: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate treatment plan using rule-based approach."""
        guidelines = self._treatment_guidelines.get(diagnosis, {})

        # Medication recommendations
        medications = []
        for drug_name in guidelines.get("first_line", []):
            if drug_name in self._drug_database:
                drug_info = self._drug_database[drug_name]
                meds.append(self._create_medication_recommendation(drug_name, drug_info, patient_context))

        # Lifestyle recommendations
        lifestyle = []
        for rec in guidelines.get("lifestyle", []):
            lifestyle.append(LifestyleRecommendation(
                category=self._categorize_lifestyle_recommendation(rec),
                recommendation=rec,
                details=self._get_lifestyle_details(rec),
                priority=1,
                rationale="Evidence-based lifestyle intervention",
                expected_outcome="Improved disease control"
            ))

        # Monitoring plan
        monitoring = []
        for test in guidelines.get("monitoring", []):
            monitoring.append(self._create_monitoring_plan(test))

        # Consultation recommendations
        consultations = []
        for consult in guidelines.get("consultations", []):
            consultations.append(self._create_consultation_recommendation(consult))

        return {
            "pharmacological": [
                {
                    "drug_name": med.drug_name,
                    "generic_name": med.generic_name,
                    "dosage": med.dosage,
                    "frequency": med.frequency,
                    "duration": med.duration,
                    "route": med.route,
                    "rationale": med.rationale,
                    "contraindications": med.contraindications,
                    "monitoring": med.monitoring,
                    "cost": med.cost,
                    "priority": med.priority,
                    "pregnancy_category": med.pregnancy_category,
                }
                for med in medications
            ],
            "lifestyle": [
                {
                    "category": rec.category,
                    "recommendation": rec.recommendation,
                    "details": rec.details,
                    "priority": rec.priority,
                    "rationale": rec.rationale,
                    "expected_outcome": rec.expected_outcome,
                }
                for rec in lifestyle
            ],
            "monitoring": [
                {
                    "test_name": plan.test_name,
                    "frequency": plan.frequency,
                    "target_range": plan.target_range,
                    "action_threshold": plan.action_threshold,
                    "rationale": plan.rationale,
                }
                for plan in monitoring
            ],
            "consultations": [
                {
                    "specialty": consult.specialty,
                    "urgency": consult.urgency,
                    "reason": consult.reason,
                    "specific_questions": consult.specific_questions,
                }
                for consult in consultations
            ],
            "contraindications": [],
            "follow_up": {
                "schedule": "3 months",
                "what_to_monitor": "Symptoms, side effects, lab values",
            },
        }

    def _create_medication_recommendation(
        self,
        drug_name: str,
        drug_info: Dict[str, Any],
        patient_context: Dict[str, Any]
    ) -> MedicationRecommendation:
        """Create medication recommendation object."""
        return MedicationRecommendation(
            drug_name=drug_name,
            generic_name=drug_info["generic_name"],
            dosage=drug_info["typical_dosage"],
            frequency=drug_info["typical_dosage"].split()[-1] if " " in drug_info["typical_dosage"] else "1x1",
            duration="sürekli",
            route="oral",
            rationale=drug_info["mechanism"],
            contraindications=drug_info["contraindications"],
            monitoring=drug_info["monitoring"],
            cost=drug_info["cost"],
            priority=1,
            pregnancy_category=drug_info["pregnancy_category"],
        )

    def _categorize_lifestyle_recommendation(self, recommendation: str) -> str:
        """Categorize lifestyle recommendation."""
        rec_lower = recommendation.lower()
        if any(keyword in rec_lower for keyword in ["diyet", "beslenme", "nutrition", "food"]):
            return "diet"
        elif any(keyword in rec_lower for keyword in ["egzersiz", "spor", "exercise", "active"]):
            return "exercise"
        elif any(keyword in rec_lower for keyword in ["sigara", "alkol", "smoking", "alcohol"]):
            return "habits"
        else:
            return "other"

    def _get_lifestyle_details(self, recommendation: str) -> str:
        """Get detailed description for lifestyle recommendation."""
        details_map = {
            "Weight loss": "Hedef: %5-10 ağırlık kaybı, haftada 0.5-1 kg",
            "Regular exercise": "Haftada 150 dakika orta yoğunluklu aerobik egzersiz",
            "Diet modification": "Düşük karbonhidrat, yüksek lif, doymamış yağlar",
            "Sodium restriction": "Günlük sodyum alımı <2000 mg",
            "DASH diet": "Meyve, sebze, tam tahıllar ağırlıklı beslenme",
            "Smoking cessation": "Kademeli azaltma, nikotin replasman tedavisi",
        }
        return details_map.get(recommendation, "Detaylı bilgi doktor tarafından verilecektir")

    def _create_monitoring_plan(self, test_description: str) -> MonitoringPlan:
        """Create monitoring plan object."""
        # Parse test description
        if "q3mo" in test_description or "3 ay" in test_description:
            frequency = "3 ayda bir"
        elif "q6mo" in test_description or "6 ay" in test_description:
            frequency = "6 ayda bir"
        elif "yearly" in test_description or "yıllık" in test_description:
            frequency = "Yılda bir"
        else:
            frequency = "Düzenli aralıklarla"

        return MonitoringPlan(
            test_name=test_description.split()[0],
            frequency=frequency,
            target_range="Hedef aralık referans değerlerde",
            action_threshold="Hedef dışı değerlerde doktora başvur",
            rationale="Tedavi yanıtını izlemek ve yan etkileri tespit etmek"
        )

    def _create_consultation_recommendation(self, consult_description: str) -> ConsultationRecommendation:
        """Create consultation recommendation object."""
        specialties = {
            "endocrinology": "Endocrinology",
            "cardiology": "Cardiology",
            "pulmonology": "Pulmonology",
            "nephrology": "Nephrology",
            "ophthalmology": "Ophthalmology",
            "psychiatry": "Psychiatry",
        }

        for keyword, specialty in specialties.items():
            if keyword.lower() in consult_description.lower():
                return ConsultationRecommendation(
                    specialty=specialty,
                    urgency="routine",
                    reason=consult_description,
                    specific_questions=["Treatment optimization", "Management recommendations"]
                )

        return ConsultationRecommendation(
            specialty="Specialist",
            urgency="routine",
            reason=consult_description,
            specific_questions=["Management recommendations"]
        )

    def _check_contraindications(
        self,
        treatment_result: Dict[str, Any],
        patient_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for contraindications and adjust treatment plan."""
        contraindications = []

        # Check medication contraindications
        patient_allergies = patient_context.get("allergies", "").lower()
        patient_meds = patient_context.get("current_medications", [])
        patient_age = patient_context.get("age", 0)

        # Filter out contraindicated medications
        filtered_medications = []
        for med in treatment_result.get("pharmacological", []):
            drug_name = med.get("drug_name", "")
            drug_info = self._drug_database.get(drug_name, {})

            # Check allergies
            if drug_name.lower() in patient_allergies:
                contraindications.append(f"Allergy: {drug_name}")
                continue

            # Check medication interactions
            for current_med in patient_meds:
                interaction = self._check_drug_interaction(drug_name, current_med)
                if interaction:
                    contraindications.append(f"Drug interaction: {drug_name} + {current_med}: {interaction}")

            # Check age-related contraindications
            if patient_age > 65 and drug_info.get("caution_elderly"):
                contraindications.append(f"Caution in elderly: {drug_name}")

            filtered_medications.append(med)

        # Update treatment result
        treatment_result["pharmacological"] = filtered_medications
        treatment_result["contraindications"] = contraindications

        return treatment_result

    def _check_drug_interaction(self, drug1: str, drug2: str) -> Optional[str]:
        """Check for drug-drug interactions."""
        # Common drug interactions (simplified)
        interaction_map = {
            ("Lisinopril", "Ibuprofen"): "Reduced antihypertensive effect, increased renal risk",
            ("Lisinopril", "Potassium"): "Hyperkalemia risk",
            ("Warfarin", "Ibuprofen"): "Increased bleeding risk",
            ("Metformin", "Iodinated contrast"): "Lactic acidosis risk",
        }

        for (d1, d2), interaction in interaction_map.items():
            if (d1.lower() in drug1.lower() and d2.lower() in drug2.lower()) or \
               (d1.lower() in drug2.lower() and d2.lower() in drug1.lower()):
                return interaction

        return None

    def get_treatment_report(self, treatment_result: Dict[str, Any]) -> str:
        """
        Generate formatted treatment report.

        Args:
            treatment_result: Result from generate_treatment_plan

        Returns:
            Human-readable formatted treatment report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TREATMENT PLAN")
        lines.append("=" * 60)
        lines.append("")

        # Pharmacological treatment
        medications = treatment_result.get("pharmacological", [])
        if medications:
            lines.append("PHARMACOLOGICAL TREATMENT")
            lines.append("-" * 40)
            for med in sorted(medications, key=lambda x: x.get("priority", 999)):
                lines.append(f"🔹 {med.get('drug_name', 'Unknown')} ({med.get('generic_name', '')})")
                lines.append(f"   Dosage: {med.get('dosage', '')} {med.get('frequency', '')}")
                lines.append(f"   Duration: {med.get('duration', '')}")
                if med.get('rationale'):
                    lines.append(f"   Rationale: {med['rationale']}")
                if med.get('contraindications'):
                    lines.append(f"   Contraindications: {', '.join(med['contraindications'])}")
                lines.append("")

        # Lifestyle recommendations
        lifestyle = treatment_result.get("lifestyle", [])
        if lifestyle:
            lines.append("LIFESTYLE MODIFICATIONS")
            lines.append("-" * 40)
            for rec in sorted(lifestyle, key=lambda x: x.get("priority", 999)):
                lines.append(f"🔹 {rec.get('recommendation', '')}")
                if rec.get("details"):
                    lines.append(f"   Details: {rec['details']}")
                if rec.get("rationale"):
                    lines.append(f"   Reason: {rec['rationale']}")
                lines.append("")

        # Monitoring plan
        monitoring = treatment_result.get("monitoring", [])
        if monitoring:
            lines.append("MONITORING PLAN")
            lines.append("-" * 40)
            for plan in monitoring:
                lines.append(f"🔹 {plan.get('test_name', '')}")
                lines.append(f"   Frequency: {plan.get('frequency', '')}")
                lines.append(f"   Target: {plan.get('target_range', '')}")
                lines.append("")

        # Consultations
        consultations = treatment_result.get("consultations", [])
        if consultations:
            lines.append("CONSULTATIONS")
            lines.append("-" * 40)
            for consult in consultations:
                urgency_icon = "🔴" if consult.get("urgency") == "urgent" else "🟢"
                lines.append(f"{urgency_icon} {consult.get('specialty', '')}")
                lines.append(f"   Reason: {consult.get('reason', '')}")
                lines.append("")

        # Contraindications
        contraindications = treatment_result.get("contraindications", [])
        if contraindications:
            lines.append("⚠️ CONTRAINDICATIONS / WARNINGS")
            lines.append("-" * 40)
            for warning in contraindications:
                lines.append(f"• {warning}")
            lines.append("")

        # Follow-up
        follow_up = treatment_result.get("follow_up", {})
        if follow_up:
            lines.append("FOLLOW-UP")
            lines.append("-" * 40)
            if follow_up.get("schedule"):
                lines.append(f"Schedule: {follow_up['schedule']}")
            if follow_up.get("what_to_monitor"):
                lines.append(f"Monitor: {follow_up['what_to_monitor']}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)