"""Turkish medical prompt templates for clinical AI tasks."""

from typing import Dict, Any, List, Optional
import json


class TurkishMedicalPrompts:
    """Turkish-language prompt templates for clinical decision support."""

    @staticmethod
    def diagnosis_prompt(
        chief_complaint: str,
        vitals: Optional[Dict[str, Any]] = None,
        lab_results: Optional[List[Dict[str, Any]]] = None,
        medical_history: Optional[List[str]] = None,
        demographics: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate Turkish prompt for differential diagnosis.

        Args:
            chief_complaint: Patient's main symptoms
            vitals: Vital signs dictionary
            lab_results: Laboratory test results
            medical_history: Past medical conditions
            demographics: Age, gender, etc.

        Returns:
            Formatted prompt string
        """
        prompt_parts = ["# Hasta Bilgileri\n"]

        # Demographics
        if demographics:
            age = demographics.get("age", "Bilinmiyor")
            gender = demographics.get("gender", "Bilinmiyor")
            prompt_parts.append(f"**Yaş:** {age}")
            prompt_parts.append(f"**Cinsiyet:** {gender}\n")

        # Chief complaint
        prompt_parts.append(f"**Şikayet:** {chief_complaint}\n")

        # Vital signs
        if vitals:
            prompt_parts.append("**Vital Bulgular:**")
            for key, value in vitals.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")

        # Lab results
        if lab_results and lab_results:
            prompt_parts.append("**Lab Sonuçları:**")
            for lab in lab_results:
                test_name = lab.get("test_name", "Bilinmiyor")
                value = lab.get("value", "N/A")
                unit = lab.get("unit", "")
                ref_range = lab.get("reference_range", "")
                prompt_parts.append(f"- {test_name}: {value} {unit} (Normal: {ref_range})")
            prompt_parts.append("")

        # Medical history
        if medical_history:
            prompt_parts.append("**Geçmiş Hastalıklar:**")
            for condition in medical_history:
                prompt_parts.append(f"- {condition}")
            prompt_parts.append("")

        # Instructions
        prompt_parts.extend(
            [
                "\n# Görev",
                "Lütfen yukarıdaki hasta bilgilerine dayanarak diferansiyel tanı listesi oluştur.",
                "",
                "Her tanı için şunları belirt:",
                "1. **Tanı Adı** (Türkçe)",
                "2. **ICD-10 Kodu**",
                "3. **Olasılık Skoru** (0.0-1.0 arası)",
                "4. **Destekleyen Bulgular** (liste halinde)",
                "5. **Kısa Açıklama** (1-2 cümle)",
                "6. **Aciliyet Derecesi** (düşük/orta/yüksek/kritik)",
                "",
                "# Önemli",
                "- Acil durumları mutlaka belirt (kırmızı bayrak bulguları)",
                "- En olası tanıları önce sırala",
                "- Önerilen tetkikleri ekle",
                "",
                "# Çıktı Formatı",
                "JSON formatında dön:",
                "```json",
                "{",
                '  "differential_diagnosis": [',
                "    {",
                '      "diagnosis": "Tanı adı",',
                '      "icd10": "E11.9",',
                '      "probability": 0.75,',
                '      "supporting_findings": ["Bulgu 1", "Bulgu 2"],',
                '      "reasoning": "Açıklama",',
                '      "urgency": "orta"',
                "    }",
                "  ],",
                '  "red_flags": ["Acil durum uyarıları"],',
                '  "recommended_tests": ["Önerilen tetkikler"],',
                '  "confidence_score": 0.85',
                "}",
                "```",
            ]
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def treatment_prompt(
        diagnosis: str,
        patient_profile: Dict[str, Any],
        current_medications: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
    ) -> str:
        """
        Generate Turkish prompt for treatment recommendations.

        Args:
            diagnosis: Confirmed diagnosis
            patient_profile: Patient demographics and risk factors
            current_medications: List of current medications
            allergies: List of known allergies

        Returns:
            Formatted prompt string
        """
        prompt_parts = ["# Hasta Profili\n"]

        # Diagnosis
        prompt_parts.append(f"**Tanı:** {diagnosis}\n")

        # Patient info
        age = patient_profile.get("age", "Bilinmiyor")
        gender = patient_profile.get("gender", "Bilinmiyor")
        comorbidities = patient_profile.get("comorbidities", [])

        prompt_parts.append(f"**Yaş:** {age}")
        prompt_parts.append(f"**Cinsiyet:** {gender}")

        if comorbidities:
            prompt_parts.append("\n**Ek Hastalıklar:**")
            for condition in comorbidities:
                prompt_parts.append(f"- {condition}")

        # Current medications
        if current_medications:
            prompt_parts.append("\n**Mevcut İlaçlar:**")
            for med in current_medications:
                prompt_parts.append(f"- {med}")

        # Allergies
        if allergies:
            prompt_parts.append("\n**Alerjiler:**")
            for allergy in allergies:
                prompt_parts.append(f"- {allergy}")

        # Instructions
        prompt_parts.extend(
            [
                "\n\n# Görev",
                "Lütfen bu hasta için kanıta dayalı tedavi önerileri sun.",
                "",
                "Şu kategorilerde önerilerde bulun:",
                "1. **Farmakolojik Tedavi** (ilaçlar, dozlar, süre)",
                "2. **Yaşam Tarzı Önerileri** (diyet, egzersiz, alışkanlıklar)",
                "3. **Lab Takip Planı** (hangi testler, ne sıklıkta)",
                "4. **Konsültasyon** (hangi uzmanlığa, ne zaman)",
                "",
                "Her ilaç önerisi için:",
                "- İlaç adı ve generic adı",
                "- Doz ve sıklık",
                "- Süre",
                "- Kontrendikasyonlar",
                "- İzleme gereksinimleri",
                "- Maliyet (düşük/orta/yüksek)",
                "- Öncelik (1=en önemli, 2=önemli, 3=opsiyonel)",
                "",
                "# Önemli",
                "- İlaç-ilaç etkileşimlerini kontrol et",
                "- Alerji kontrendikasyonlarını dikkate al",
                "- Yaş ve böbrek/karaciğer fonksiyonuna göre doz ayarla",
                "",
                "# Çıktı Formatı",
                "JSON formatında dön:",
                "```json",
                "{",
                '  "pharmacological": [',
                "    {",
                '      "drug_name": "Metformin",',
                '      "generic_name": "Metformin HCl",',
                '      "dosage": "500 mg",',
                '      "frequency": "2x1",',
                '      "duration": "Sürekli",',
                '      "route": "Oral",',
                '      "rationale": "Açıklama",',
                '      "contraindications": ["Kontrendikasyonlar"],',
                '      "monitoring": ["İzleme gereksinimleri"],',
                '      "cost": "Düşük",',
                '      "priority": 1',
                "    }",
                "  ],",
                '  "lifestyle": [',
                "    {",
                '      "recommendation": "Karbonhidrat kısıtlaması",',
                '      "details": "Detaylı açıklama",',
                '      "priority": 1',
                "    }",
                "  ],",
                '  "laboratory_followup": [',
                "    {",
                '      "test": "HbA1c",',
                '      "frequency": "3 ayda bir",',
                '      "target": "<7%"',
                "    }",
                "  ],",
                '  "consultations": [',
                "    {",
                '      "specialty": "Endokrinoloji",',
                '      "urgency": "rutin",',
                '      "reason": "Açıklama"',
                "    }",
                "  ]",
                "}",
                "```",
            ]
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def drug_interaction_prompt(
        current_medications: List[str],
        proposed_drug: str,
        patient_allergies: Optional[List[str]] = None,
    ) -> str:
        """
        Generate Turkish prompt for drug interaction checking.

        Args:
            current_medications: List of current medications
            proposed_drug: New drug to check
            patient_allergies: Known allergies

        Returns:
            Formatted prompt string
        """
        prompt_parts = ["# İlaç Etkileşimi Kontrolü\n"]

        # Current medications
        prompt_parts.append("**Mevcut İlaçlar:**")
        for med in current_medications:
            prompt_parts.append(f"- {med}")

        # Proposed drug
        prompt_parts.append(f"\n**Yeni İlaç:** {proposed_drug}\n")

        # Allergies
        if patient_allergies:
            prompt_parts.append("**Hasta Alerjileri:**")
            for allergy in patient_allergies:
                prompt_parts.append(f"- {allergy}")
            prompt_parts.append("")

        # Instructions
        prompt_parts.extend(
            [
                "# Görev",
                "Lütfen yeni ilacın mevcut ilaçlarla ve hasta alerjileriyle etkileşimlerini kontrol et.",
                "",
                "Şunları belirt:",
                "1. **İlaç-İlaç Etkileşimleri** (hangi ilaçlar, nasıl etkilenir)",
                "2. **İlaç-Alerji Çapraz Reaksiyonları** (varsa)",
                "3. **Ciddiyet Derecesi** (minimal/minor/moderate/major/critical)",
                "4. **Yönetim Önerileri** (nasıl kullanılmalı)",
                "5. **Alternatif İlaçlar** (etkileşim yoksa)",
                "",
                "# Önemli",
                "- Kritik etkileşimleri mutlaka vurgula",
                "- Çapraz alerji risklerini belirt (örn: Penisilin → Amoksisilin)",
                "- Güvenli alternatifleri öner",
                "",
                "# Çıktı Formatı",
                "JSON formatında dön:",
                "```json",
                "{",
                '  "interactions": [',
                "    {",
                '      "type": "drug-drug",',
                '      "severity": "major",',
                '      "drug1": "Warfarin",',
                '      "drug2": "NSAİİ",',
                '      "effect": "Kanama riski artışı",',
                '      "recommendation": "Kombinasyondan kaçının",',
                '      "management": "Yönetim önerileri"',
                "    }",
                "  ],",
                '  "safe_to_prescribe": false,',
                '  "alternative_drugs": ["Alternatif ilaçlar"]',
                "}",
                "```",
            ]
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON from AI response text.

        Args:
            response_text: Raw AI response that may contain JSON

        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        try:
            # Try direct JSON parse first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code blocks
        import re

        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in text
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(response_text[start_idx:end_idx])
            except json.JSONDecodeError:
                pass

        return None
