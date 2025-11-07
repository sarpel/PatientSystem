"""
Template-based prompt builder for clinical AI interactions.
Separates prompt templates from business logic for easier maintenance and localization.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


# Template strings for diagnosis prompts
DIAGNOSIS_PROMPT_TEMPLATE = """Hasta bilgileri:

DEMOGRAFİK BİLGİLER:
{demographics}

ŞİKAYETLER:
{complaints}

VİTAL BULGULAR:
{vitals}

FİZİK MUAYENE:
{exam}

LAB SONUÇLARI:
{labs}

Lütfen diferansiyel tanı listesi ver. Her tanı için:
1. Tanı adı (Türkçe)
2. ICD-10 kodu
3. Olasılık (% olarak)
4. Destekleyen bulgular
5. Kısa gerekçelendirme
6. Acil durumu (urgent/soon/routine)
7. Önerilen ek testler
8. Uyarılar/red flag var mı

Format: JSON dizisi olarak dön.

Örnek format:
[
  {{
    "diagnosis": "Tip 2 Diabetes Mellitus",
    "icd10": "E11.9",
    "probability": 0.75,
    "reasoning": "HbA1c yüksek, açlık glukozu yükselmiş...",
    "supporting_findings": ["HbA1c 8.4%", "açlık glukozu 165 mg/dL"],
    "red_flags": [],
    "recommended_tests": ["Lipid paneli", "Mikroalbüminüri", "Göz muayenesi"],
    "urgency": "soon"
  }}
]"""


DEMOGRAPHIC_TEMPLATE = """- Yaş: {age} yıl
- Cinsiyet: {gender}
- BMI: {bmi}
- Sigara kullanımı: {smoking}
- Geçmiş hastalıklar: {comorbidities}"""


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


class DiagnosisPromptBuilder:
    """Builder for diagnosis prompts using templates."""

    def __init__(self, context: DiagnosisContext):
        """
        Initialize prompt builder with diagnosis context.

        Args:
            context: Clinical context for diagnosis
        """
        self.context = context

    def build_prompt(self) -> str:
        """
        Build complete diagnosis prompt from context.

        Returns:
            Formatted prompt string
        """
        return DIAGNOSIS_PROMPT_TEMPLATE.format(
            demographics=self._format_demographics(),
            complaints=self._format_complaints(),
            vitals=self._format_vitals(),
            exam=self._format_exam(),
            labs=self._format_labs(),
        )

    def _format_demographics(self) -> str:
        """Format demographic information section."""
        demographics = self.context.demographics
        age = demographics.get("age", "Bilinmiyor")
        gender = demographics.get("gender", "Bilinmiyor")
        bmi = demographics.get("bmi", "Bilinmiyor")
        smoking = demographics.get("smoking_status", "Bilinmiyor")
        comorbidities = ", ".join(demographics.get("comorbidities", [])) or "Yok"

        return DEMOGRAPHIC_TEMPLATE.format(
            age=age,
            gender=gender,
            bmi=bmi,
            smoking=smoking,
            comorbidities=comorbidities,
        )

    def _format_complaints(self) -> str:
        """Format chief complaints section."""
        if not self.context.chief_complaints:
            return "Mevcut değil"
        return "\n".join(f"- {complaint}" for complaint in self.context.chief_complaints)

    def _format_vitals(self) -> str:
        """Format vital signs section."""
        if not self.context.vital_signs:
            return "Mevcut değil"
        return "\n".join(f"- {k}: {v}" for k, v in self.context.vital_signs.items())

    def _format_exam(self) -> str:
        """Format physical examination section."""
        if not self.context.physical_exam:
            return "Mevcut değil"
        return "\n".join(f"- {k}: {v}" for k, v in self.context.physical_exam.items())

    def _format_labs(self) -> str:
        """Format laboratory results section."""
        if not self.context.lab_results:
            return "Mevcut değil"
        return "\n".join(f"- {k}: {v}" for k, v in self.context.lab_results.items())


def create_diagnosis_prompt(context: DiagnosisContext) -> str:
    """
    Convenience function to create diagnosis prompt.

    Args:
        context: Clinical context for diagnosis

    Returns:
        Formatted prompt string
    """
    builder = DiagnosisPromptBuilder(context)
    return builder.build_prompt()
