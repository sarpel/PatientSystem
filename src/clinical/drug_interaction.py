"""
Drug Interaction Checker Module.

Provides comprehensive drug interaction analysis with:
- Drug-drug interaction database
- Allergy checking
- Contraindication detection
- AI-based interaction assessment
- Severity classification
- Management recommendations
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.clinical import Prescription
from src.models.patient import Patient


class InteractionSeverity(Enum):
    """Interaction severity levels."""

    UNKNOWN = "unknown"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"


@dataclass
class DrugInteraction:
    """Individual drug interaction information."""

    drug1: str
    drug2: str
    severity: InteractionSeverity
    description: str
    clinical_effect: str
    management: str
    evidence_level: str


@dataclass
class AllergyWarning:
    """Drug allergy warning."""

    drug_name: str
    allergen: str
    severity: str
    clinical_significance: str


@dataclass
class InteractionResult:
    """Complete interaction analysis result."""

    patient_id: int
    interactions: List[DrugInteraction]
    allergy_warnings: List[AllergyWarning]
    safe_alternatives: List[str]
    recommendations: List[str]
    requires_pharmacist_review: bool


class DrugInteractionChecker:
    """
    Comprehensive drug interaction checker.

    Analyzes medication regimens for potential interactions,
    allergies, and contraindications using both local database
    and AI-powered assessment.
    """

    def __init__(self, session: Session, ai_router=None):
        """
        Initialize DrugInteractionChecker.

        Args:
            session: SQLAlchemy database session
            ai_router: AI service router for complex interaction assessment
        """
        self.session = session
        self.ai_router = ai_router
        self._interaction_database = self._load_interaction_database()
        self._allergy_database = self._load_allergy_database()
        self._drug_synonyms = self._load_drug_synonyms()

    def check_drug_interactions(
        self, patient_id: int, medications: List[str], patient_allergies: Optional[List[str]] = None
    ) -> InteractionResult:
        """
        Check for drug interactions in medication regimen.

        Args:
            patient_id: Patient registration ID
            medications: List of medications to check
            patient_allergies: Known patient allergies

        Returns:
            Complete interaction analysis result
        """
        # Get patient allergies if not provided
        if patient_allergies is None:
            patient_allergies = self._get_patient_allergies(patient_id)

        # Normalize medication names
        normalized_meds = [self._normalize_drug_name(med) for med in medications]

        # Check drug-drug interactions
        interactions = self._check_drug_drug_interactions(normalized_meds)

        # Check allergies
        allergy_warnings = self._check_allergies(normalized_meds, patient_allergies)

        # Use AI for complex interaction assessment
        if self.ai_router and len(normalized_meds) >= 3:
            ai_interactions = self._get_ai_interactions(normalized_meds, patient_allergies)
            interactions.extend(ai_interactions)

        # Remove duplicates and sort by severity
        interactions = self._deduplicate_interactions(interactions)
        interactions.sort(key=lambda x: self._severity_rank(x.severity), reverse=True)

        # Generate recommendations
        recommendations = self._generate_recommendations(interactions, allergy_warnings)

        # Identify safe alternatives
        safe_alternatives = self._identify_safe_alternatives(medications, interactions)

        return InteractionResult(
            patient_id=patient_id,
            interactions=interactions,
            allergy_warnings=allergy_warnings,
            safe_alternatives=safe_alternatives,
            recommendations=recommendations,
            requires_pharmacist_review=self._requires_pharmacist_review(interactions),
        )

    def _load_interaction_database(self) -> Dict[Tuple[str, str], DrugInteraction]:
        """Load comprehensive drug interaction database."""
        interactions = {}

        # Major interactions (contraindicated or require monitoring)
        interaction_data = [
            # Cardiovascular interactions
            (
                "Warfarin",
                "Ibuprofen",
                InteractionSeverity.MAJOR,
                "Increased bleeding risk due to antiplatelet effect and GI ulceration",
                "Bleeding, GI ulcer, hematoma",
                "Avoid combination, use acetaminophen for pain",
                "High",
            ),
            (
                "Warfarin",
                "Aspirin",
                InteractionSeverity.MAJOR,
                "Additive anticoagulant effect",
                "Major bleeding",
                "Use with extreme caution, monitor INR closely",
                "High",
            ),
            (
                "Lisinopril",
                "Potassium",
                InteractionSeverity.MAJOR,
                "ACE inhibitors reduce potassium excretion",
                "Hyperkalemia, cardiac arrhythmias",
                "Avoid potassium supplements, monitor serum potassium",
                "High",
            ),
            (
                "Lisinopril",
                "NSAIDs",
                InteractionSeverity.MODERATE,
                "NSAIDs reduce ACE inhibitor effectiveness and increase renal risk",
                "Reduced BP control, acute kidney injury",
                "Monitor renal function, consider acetaminophen",
                "Moderate",
            ),
            (
                "Digoxin",
                "Amiodarone",
                InteractionSeverity.MAJOR,
                "Amiodarone increases digoxin levels",
                "Digoxin toxicity (arrhythmias, vision changes)",
                "Reduce digoxin dose by 50%, monitor levels",
                "High",
            ),
            # Diabetes interactions
            (
                "Metformin",
                "Iodinated contrast",
                InteractionSeverity.CONTRAINDICATED,
                "Increased risk of lactic acidosis",
                "Lactic acidosis (fatal)",
                "Stop metformin 48h before contrast, wait 48h after",
                "High",
            ),
            (
                "Insulin",
                "Beta Blocker",
                InteractionSeverity.MODERATE,
                "Beta blockers mask hypoglycemia symptoms",
                "Unrecognized hypoglycemia",
                "Monitor glucose closely, educate patient",
                "Moderate",
            ),
            # CNS interactions
            (
                "SSRIs",
                "MAOIs",
                InteractionSeverity.CONTRAINDICATED,
                "Serotonin syndrome risk",
                "Serotonin syndrome (hyperthermia, rigidity, seizures)",
                "Do not combine, 2-week washout required",
                "High",
            ),
            (
                "Opioids",
                "Benzodiazepines",
                InteractionSeverity.MAJOR,
                "Additive CNS depression and respiratory depression",
                "Respiratory depression, sedation, death",
                "Use lowest effective doses, monitor closely",
                "High",
            ),
            # Antibiotic interactions
            (
                "Warfarin",
                "Fluoroquinolones",
                InteractionSeverity.MAJOR,
                "Fluoroquinolones potentiate warfarin effect",
                "Elevated INR, bleeding",
                "Monitor INR frequently, reduce warfarin dose",
                "Moderate",
            ),
            (
                "Statins",
                "Clarithromycin",
                InteractionSeverity.MAJOR,
                "Macrolides inhibit statin metabolism",
                "Rhabdomyolysis, myopathy",
                "Stop statin during macrolide therapy",
                "High",
            ),
            # GI interactions
            (
                "PPIs",
                "Clopidogrel",
                InteractionSeverity.MODERATE,
                "PPIs may reduce clopidogrel activation",
                "Reduced antiplatelet effect",
                "Consider pantoprazole or H2 blocker",
                "Moderate",
            ),
            # Psychiatric interactions
            (
                "TCAs",
                "Antihistamines",
                InteractionSeverity.MODERATE,
                "Additive anticholinergic effects",
                "Sedation, dry mouth, urinary retention",
                "Monitor for anticholinergic side effects",
                "Moderate",
            ),
            # Hormonal interactions
            (
                "Oral Contraceptives",
                "Antibiotics",
                InteractionSeverity.MODERATE,
                "Antibiotics may reduce contraceptive efficacy",
                "Unintended pregnancy",
                "Use backup contraception during therapy",
                "Moderate",
            ),
            # Drug-food interactions
            (
                "Warfarin",
                "Vitamin K",
                InteractionSeverity.MAJOR,
                "Vitamin K antagonizes warfarin effect",
                "Reduced anticoagulation, thrombosis risk",
                "Maintain consistent vitamin K intake",
                "High",
            ),
            (
                "MAOIs",
                "Tyramine-rich foods",
                InteractionSeverity.CONTRAINDICATED,
                "Hypertensive crisis",
                "Severe hypertension, headache, stroke",
                "Strict dietary tyramine restriction",
                "High",
            ),
            # NSAID interactions
            (
                "NSAIDs",
                "Corticosteroids",
                InteractionSeverity.MAJOR,
                "Additive GI ulcer risk",
                "GI bleeding, ulceration",
                "Use gastroprotection, avoid if possible",
                "High",
            ),
            (
                "NSAIDs",
                "ACEi/ARBs",
                InteractionSeverity.MAJOR,
                "Triple whammy effect - acute kidney injury",
                "Acute kidney injury, hyperkalemia",
                "Avoid triple therapy, monitor renal function",
                "High",
            ),
        ]

        for drug1, drug2, severity, desc, effect, management, evidence in interaction_data:
            # Add both directions
            interactions[(drug1, drug2)] = DrugInteraction(
                drug1=drug1,
                drug2=drug2,
                severity=severity,
                description=desc,
                clinical_effect=effect,
                management=management,
                evidence_level=evidence,
            )
            interactions[(drug2, drug1)] = DrugInteraction(
                drug1=drug2,
                drug2=drug1,
                severity=severity,
                description=desc,
                clinical_effect=effect,
                management=management,
                evidence_level=evidence,
            )

        return interactions

    def _load_allergy_database(self) -> Dict[str, List[str]]:
        """Load drug allergy cross-reactivity database."""
        return {
            "Penicillin": ["Amoxicillin", "Ampicillin", "Amoxicillin-clavulanate", "Piperacillin"],
            "Sulfonamides": [
                "Sulfamethoxazole",
                "Sulfasalazine",
                "Furosemide",
                "Thiazide diuretics",
            ],
            "NSAIDs": ["Ibuprofen", "Naproxen", "Diclofenac", "Ketorolac", "Aspirin"],
            "Opioids": ["Codeine", "Morphine", "Oxycodone", "Hydromorphone"],
            "Beta Blockers": [
                "Propranolol",
                "Atenolol",
                "Metoprolol",
                "Lisinopril",
            ],  # Note: Lisinopril is ACEi
            "ACE Inhibitors": ["Lisinopril", "Enalapril", "Ramipril", "Captopril"],
            "Statins": ["Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin"],
            "Quinolones": ["Ciprofloxacin", "Levofloxacin", "Moxifloxacin", "Ofloxacin"],
        }

    def _load_drug_synonyms(self) -> Dict[str, List[str]]:
        """Load drug name synonyms for matching."""
        return {
            "Ibuprofen": ["Advil", "Motrin", "Brufen"],
            "Acetaminophen": ["Paracetamol", "Tylenol"],
            "Aspirin": ["Acetylsalicylic acid", "ASA", "Ecotrin"],
            "Lisinopril": ["Zestril", "Prinivil"],
            "Atorvastatin": ["Lipitor"],
            "Metformin": ["Glucophage", "Diaformin"],
            "Metoprolol": ["Lopressor", "Toprol-XL"],
            "Omeprazole": ["Prilosec", "Losec"],
            "Warfarin": ["Coumadin", "Jantoven"],
            "Digoxin": ["Lanoxin"],
        }

    def _get_patient_allergies(self, patient_id: int) -> List[str]:
        """Get patient allergies from database."""
        patient = self.session.execute(
            select(Patient).where(Patient.HASTA_KAYIT_ID == patient_id)
        ).scalar_one_or_none()

        if not patient:
            return []

        allergies = []
        # Note: ILAC_ALERJISI column does not exist in Patient or PatientDemographics models
        # Allergy information would need to be retrieved from DTY_HASTA_OZLUK_ALERJI table
        # For now, return empty list as placeholder
        # TODO: Implement allergy retrieval from DTY_HASTA_OZLUK_ALERJI table

        return allergies

    def _normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name for matching."""
        if not drug_name:
            return drug_name

        # Remove common variations and normalize
        normalized = drug_name.strip().title()

        # Check if it's a synonym
        for canonical, synonyms in self._drug_synonyms.items():
            if normalized in [s.title() for s in synonyms]:
                return canonical

        return normalized

    def _check_drug_drug_interactions(self, medications: List[str]) -> List[DrugInteraction]:
        """Check for drug-drug interactions."""
        interactions = []
        n = len(medications)

        # Check all pairs
        for i in range(n):
            for j in range(i + 1, n):
                drug1, drug2 = medications[i], medications[j]

                # Check direct interaction
                key = (drug1, drug2)
                if key in self._interaction_database:
                    interactions.append(self._interaction_database[key])

                # Check class-based interactions
                class_interactions = self._check_class_interactions(drug1, drug2)
                interactions.extend(class_interactions)

        return interactions

    def _check_class_interactions(self, drug1: str, drug2: str) -> List[DrugInteraction]:
        """Check for interactions based on drug classes."""
        interactions = []

        # Define drug classes and their interactions
        drug_classes = {
            "NSAIDs": ["Ibuprofen", "Naproxen", "Diclofenac", "Ketorolac", "Aspirin"],
            "ACEi": ["Lisinopril", "Enalapril", "Ramipril", "Captopril"],
            "ARBs": ["Losartan", "Valsartan", "Candesartan", "Irbesartan"],
            "Beta Blockers": ["Metoprolol", "Propranolol", "Atenolol", "Carvedilol"],
            "Statins": ["Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin"],
            "SSRIs": ["Fluoxetine", "Sertraline", "Paroxetine", "Citalopram"],
            "Opioids": ["Codeine", "Morphine", "Oxycodone", "Hydrocodone", "Tramadol"],
            "Benzodiazepines": ["Diazepam", "Lorazepam", "Alprazolam", "Clonazepam"],
        }

        # Check class-based interactions
        for class_name, class_drugs in drug_classes.items():
            if drug1 in class_drugs or drug2 in class_drugs:
                # ACEi + NSAID interaction
                if class_name == "ACEi" and any(
                    n in drug2 for n in ["NSAIDs", "Ibuprofen", "Naproxen"]
                ):
                    interactions.append(
                        DrugInteraction(
                            drug1=drug1,
                            drug2=drug2,
                            severity=InteractionSeverity.MAJOR,
                            description="ACE inhibitor + NSAID triple whammy effect",
                            clinical_effect="Acute kidney injury, reduced BP control",
                            management="Avoid combination, monitor renal function closely",
                            evidence_level="High",
                        )
                    )

                # Statin + macrolide antibiotics (if we had antibiotic classes defined)
                if class_name == "Statins" and "Clarithromycin" in drug2:
                    interactions.append(
                        DrugInteraction(
                            drug1=drug1,
                            drug2=drug2,
                            severity=InteractionSeverity.MAJOR,
                            description="Macrolide inhibits statin metabolism",
                            clinical_effect="Rhabdomyolysis, myopathy",
                            management="Stop statin during macrolide therapy",
                            evidence_level="High",
                        )
                    )

        return interactions

    def _check_allergies(
        self, medications: List[str], patient_allergies: List[str]
    ) -> List[AllergyWarning]:
        """Check for drug allergies and cross-reactivity."""
        warnings = []

        # Direct allergy matches
        for med in medications:
            for allergy in patient_allergies:
                allergy_lower = allergy.lower()
                med_lower = med.lower()

                if allergy_lower in med_lower or med_lower in allergy_lower:
                    warnings.append(
                        AllergyWarning(
                            drug_name=med,
                            allergen=allergy,
                            severity="CRITICAL",
                            clinical_significance="Avoid this medication - direct allergy",
                        )
                    )

        # Cross-reactivity checks
        for med in medications:
            for allergen, cross_reactive_drugs in self._allergy_database.items():
                if allergen.lower() in [a.lower() for a in patient_allergies]:
                    if med in cross_reactive_drugs or any(
                        drug in med for drug in cross_reactive_drugs
                    ):
                        warnings.append(
                            AllergyWarning(
                                drug_name=med,
                                allergen=allergen,
                                severity="HIGH",
                                clinical_significance=f"Cross-reactivity with {allergen} allergy",
                            )
                        )

        return warnings

    def _get_ai_interactions(
        self, medications: List[str], patient_allergies: List[str]
    ) -> List[DrugInteraction]:
        """Get AI-powered interaction assessment."""
        prompt = self._create_interaction_prompt(medications, patient_allergies)

        try:
            ai_response = self.ai_router.process_complex_task(
                task="drug_interaction",
                prompt=prompt,
                context={"complexity": "high", "domain": "pharmacology", "language": "en"},
            )

            return self._parse_ai_interaction_response(ai_response, medications)

        except Exception as e:
            logger.warning(f"AI interaction check failed: {e}")
            return []

    def _create_interaction_prompt(self, medications: List[str], allergies: List[str]) -> str:
        """Create structured prompt for AI interaction analysis."""
        med_list = "\n".join(f"- {med}" for med in medications)
        allergy_list = (
            "\n".join(f"- {allergy}" for allergy in allergies)
            if allergies
            else "No known allergies"
        )

        prompt = f"""Medications to analyze:
{med_list}

Patient allergies:
{allergy_list}

Please analyze this medication regimen for:

1. Drug-drug interactions not in standard databases
2. Complex multi-drug interactions
3. Condition-specific considerations
4. Alternative medications if needed

Focus on:
- Novel or rare interactions
- Polypharmacy risks
- Age-specific considerations
- Organ function impacts

Return as JSON with structure:
{{
  "interactions": [
    {{
      "drug1": "Drug1",
      "drug2": "Drug2",
      "severity": "moderate|major|contraindicated",
      "description": "Interaction description",
      "clinical_effect": "Potential outcome",
      "management": "Management strategy"
    }}
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ]
}}"""

        return prompt

    def _parse_ai_interaction_response(
        self, ai_response: str, medications: List[str]
    ) -> List[DrugInteraction]:
        """Parse AI interaction response."""
        try:
            response_data = json.loads(ai_response)
            interactions = []

            for item in response_data.get("interactions", []):
                # Map AI severity to our enum
                severity_map = {
                    "minor": InteractionSeverity.MINOR,
                    "moderate": InteractionSeverity.MODERATE,
                    "major": InteractionSeverity.MAJOR,
                    "contraindicated": InteractionSeverity.CONTRAINDICATED,
                }

                interaction = DrugInteraction(
                    drug1=item.get("drug1", ""),
                    drug2=item.get("drug2", ""),
                    severity=severity_map.get(
                        item.get("severity", ""), InteractionSeverity.UNKNOWN
                    ),
                    description=item.get("description", ""),
                    clinical_effect=item.get("clinical_effect", ""),
                    management=item.get("management", ""),
                    evidence_level="AI-Generated",
                )
                interactions.append(interaction)

            return interactions

        except Exception as e:
            logger.error(f"Failed to parse AI interaction response: {e}")
            return []

    def _deduplicate_interactions(
        self, interactions: List[DrugInteraction]
    ) -> List[DrugInteraction]:
        """Remove duplicate interactions."""
        seen = set()
        unique_interactions = []

        for interaction in interactions:
            # Create a key for deduplication
            key = (interaction.drug1, interaction.drug2)
            if key not in seen:
                seen.add(key)
                unique_interactions.append(interaction)
            else:
                # Keep the more severe interaction
                for existing in unique_interactions:
                    if existing.drug1 == interaction.drug1 and existing.drug2 == interaction.drug2:
                        if self._severity_rank(interaction.severity) > self._severity_rank(
                            existing.severity
                        ):
                            unique_interactions[unique_interactions.index(existing)] = interaction
                        break

        return unique_interactions

    def _severity_rank(self, severity: InteractionSeverity) -> int:
        """Get numeric rank for severity comparison."""
        ranking = {
            InteractionSeverity.UNKNOWN: 0,
            InteractionSeverity.MINOR: 1,
            InteractionSeverity.MODERATE: 2,
            InteractionSeverity.MAJOR: 3,
            InteractionSeverity.CONTRAINDICATED: 4,
        }
        return ranking.get(severity, 0)

    def _generate_recommendations(
        self, interactions: List[DrugInteraction], allergy_warnings: List[AllergyWarning]
    ) -> List[str]:
        """Generate clinical recommendations based on analysis."""
        recommendations = []

        # Critical allergy warnings
        if any(w.severity == "CRITICAL" for w in allergy_warnings):
            recommendations.append(
                "🚨 CRITICAL: Remove medications causing direct allergic reactions"
            )

        # Major interactions
        major_interactions = [i for i in interactions if i.severity == InteractionSeverity.MAJOR]
        if major_interactions:
            recommendations.append(
                "⚠️ Major drug interactions detected - consider alternative therapies"
            )

        # Contraindicated combinations
        contraindicated = [
            i for i in interactions if i.severity == InteractionSeverity.CONTRAINDICATED
        ]
        if contraindicated:
            recommendations.append("❌ CONTRAINDICATED: Immediate medication adjustment required")

        # Moderate interactions
        moderate_interactions = [
            i for i in interactions if i.severity == InteractionSeverity.MODERATE
        ]
        if moderate_interactions:
            recommendations.append("⚠️ Moderate interactions - monitor patient closely")

        # General recommendations
        if len(interactions) > 3:
            recommendations.append("Consider medication therapy optimization due to polypharmacy")

        recommendations.append("Document all interactions in patient chart")
        recommendations.append("Educate patient about interaction symptoms")
        recommendations.append("Schedule follow-up to monitor therapy")

        return recommendations

    def _identify_safe_alternatives(
        self, medications: List[str], interactions: List[DrugInteraction]
    ) -> List[str]:
        """Identify safer medication alternatives."""
        alternatives = []

        # Based on common problematic combinations
        if "Ibuprofen" in medications and any(
            "Lisinopril" in i.drug1 or "Lisinopril" in i.drug2 for i in interactions
        ):
            alternatives.append("Acetaminophen (Paracetamol) for pain management")

        if "Warfarin" in medications and any(
            "Ibuprofen" in i.drug1 or "Ibuprofen" in i.drug2 for i in interactions
        ):
            alternatives.append("Consider alternative analgesics or adjust warfarin monitoring")

        if "Statins" in medications and any(
            "Clarithromycin" in i.drug1 or "Clarithromycin" in i.drug2 for i in interactions
        ):
            alternatives.append("Temporary statin discontinuation during antibiotic therapy")

        if "Metformin" in medications and interactions:
            alternatives.append("Consider diabetes medication adjustment for procedures")

        return alternatives

    def _requires_pharmacist_review(self, interactions: List[DrugInteraction]) -> bool:
        """Determine if pharmacist review is required."""
        return (
            any(
                interaction.severity
                in [InteractionSeverity.MAJOR, InteractionSeverity.CONTRAINDICATED]
                for interaction in interactions
            )
            or len(interactions) > 3
        )

    def get_interaction_report(self, result: InteractionResult) -> str:
        """
        Generate formatted interaction report.

        Args:
            result: Interaction analysis result

        Returns:
            Human-readable formatted interaction report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("DRUG INTERACTION ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Patient ID: {result.patient_id}")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Critical alerts first
        critical_interactions = [
            i for i in result.interactions if i.severity == InteractionSeverity.CONTRAINDICATED
        ]
        if critical_interactions:
            lines.append("🚨 CRITICAL - CONTRAINDICATED COMBINATIONS 🚨")
            for interaction in critical_interactions:
                lines.append(f"  {interaction.drug1} + {interaction.drug2}")
                lines.append(f"  Risk: {interaction.clinical_effect}")
                lines.append(f"  Action: {interaction.management}")
                lines.append("")
            lines.append("")

        # Allergy warnings
        if result.allergy_warnings:
            lines.append("⚠️ ALLERGY WARNINGS ⚠️")
            for warning in result.allergy_warnings:
                severity_icon = "🚨" if warning.severity == "CRITICAL" else "⚠️"
                lines.append(
                    f"  {severity_icon} {warning.drug_name}: {warning.clinical_significance}"
                )
            lines.append("")

        # Major interactions
        major_interactions = [
            i for i in result.interactions if i.severity == InteractionSeverity.MAJOR
        ]
        if major_interactions:
            lines.append("🔶 MAJOR INTERACTIONS 🔶")
            for interaction in major_interactions:
                lines.append(f"  {interaction.drug1} + {interaction.drug2}")
                lines.append(f"  Effect: {interaction.clinical_effect}")
                lines.append(f"  Management: {interaction.management}")
                lines.append("")
            lines.append("")

        # Moderate interactions
        moderate_interactions = [
            i for i in result.interactions if i.severity == InteractionSeverity.MODERATE
        ]
        if moderate_interactions:
            lines.append("🟡 MODERATE INTERACTIONS 🟡")
            for interaction in moderate_interactions[:5]:  # Limit to first 5
                lines.append(f"  {interaction.drug1} + {interaction.drug2}")
                lines.append(f"  Effect: {interaction.clinical_effect}")
                lines.append("")
            lines.append("")

        # Safe alternatives
        if result.safe_alternatives:
            lines.append("💡 SAFE ALTERNATIVES 💡")
            for alternative in result.safe_alternatives:
                lines.append(f"  • {alternative}")
            lines.append("")

        # Recommendations
        if result.recommendations:
            lines.append("📋 RECOMMENDATIONS 📋")
            for rec in result.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")

        # Pharmacist review
        if result.requires_pharmacist_review:
            lines.append("🏥 PHARMACIST REVIEW REQUIRED 🏥")
            lines.append("  Please consult with clinical pharmacist before prescribing")
            lines.append("")

        lines.append("=" * 60)
        lines.append("This report is for clinical reference purposes only.")
        lines.append("Always use clinical judgment and consider individual patient factors.")
        lines.append("=" * 60)

        return "\n".join(lines)
