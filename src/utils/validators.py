"""
Input validation utilities for the PatientSystem application.

Provides comprehensive validation functions for clinical data, patient information,
and API inputs with proper error handling and user feedback.
"""

import re
from typing import Any, List, Optional, Dict, Union
from datetime import datetime, date
from decimal import Decimal

from .exceptions import ValidationError


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, field_name: str, required: bool = True):
        self.field_name = field_name
        self.required = required

    def validate(self, value: Any) -> bool:
        """Validate the input value."""
        raise NotImplementedError

    def get_error_message(self, value: Any) -> str:
        """Get appropriate error message for failed validation."""
        raise NotImplementedError


class LengthRule(ValidationRule):
    """Validates string length."""

    def __init__(
        self,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True
    ):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        if not isinstance(value, str):
            return False

        length = len(value)
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False

        return True

    def get_error_message(self, value: Any) -> str:
        if value is None and self.required:
            return f"{self.field_name} is required"

        if not isinstance(value, str):
            return f"{self.field_name} must be a string"

        length = len(value) if isinstance(value, str) else 0
        errors = []
        if self.min_length is not None and length < self.min_length:
            errors.append(f"minimum {self.min_length} characters")
        if self.max_length is not None and length > self.max_length:
            errors.append(f"maximum {self.max_length} characters")

        return f"{self.field_name} must be between {', '.join(errors)}"


class NumericRule(ValidationRule):
    """Validates numeric values with ranges."""

    def __init__(
        self,
        field_name: str,
        min_value: Optional[Union[int, float, Decimal]] = None,
        max_value: Optional[Union[int, float, Decimal]] = None,
        required: bool = True
    ):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return False

        if self.min_value is not None and numeric_value < float(self.min_value):
            return False
        if self.max_value is not None and numeric_value > float(self.max_value):
            return False

        return True

    def get_error_message(self, value: Any) -> str:
        if value is None and self.required:
            return f"{self.field_name} is required"

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return f"{self.field_name} must be a valid number"

        errors = []
        if self.min_value is not None and numeric_value < float(self.min_value):
            errors.append(f"minimum {self.min_value}")
        if self.max_value is not None and numeric_value > float(self.max_value):
            errors.append(f"maximum {self.max_value}")

        return f"{self.field_name} must be between {', '.join(errors)}"


class RegexRule(ValidationRule):
    """Validates string patterns using regular expressions."""

    def __init__(
        self,
        field_name: str,
        pattern: str,
        description: str,
        required: bool = True
    ):
        super().__init__(field_name, required)
        self.pattern = re.compile(pattern)
        self.description = description

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        if not isinstance(value, str):
            return False

        return bool(self.pattern.match(value))

    def get_error_message(self, value: Any) -> str:
        if value is None and self.required:
            return f"{self.field_name} is required"

        if not isinstance(value, str):
            return f"{self.field_name} must be a string"

        return f"{self.field_name} must match {self.description}"


class DateRule(ValidationRule):
    """Validates date values."""

    def __init__(
        self,
        field_name: str,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        required: bool = True
    ):
        super().__init__(field_name, required)
        self.min_date = min_date
        self.max_date = max_date

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    return False
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            return False

        if self.min_date is not None and value < self.min_date:
            return False
        if self.max_date is not None and value > self.max_date:
            return False

        return True

    def get_error_message(self, value: Any) -> str:
        if value is None and self.required:
            return f"{self.field_name} is required"

        return f"{self.field_name} must be a valid date"


class EnumRule(ValidationRule):
    """Validates values against an allowed set."""

    def __init__(
        self,
        field_name: str,
        allowed_values: List[Any],
        required: bool = True
    ):
        super().__init__(field_name, required)
        self.allowed_values = allowed_values

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        return value in self.allowed_values

    def get_error_message(self, value: Any) -> str:
        if value is None and self.required:
            return f"{self.field_name} is required"

        return f"{self.field_name} must be one of: {', '.join(map(str, self.allowed_values))}"


class Validator:
    """
    Main validator class that orchestrates multiple validation rules.
    """

    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, field_name: str, rule: ValidationRule) -> 'Validator':
        """Add a validation rule for a field."""
        if field_name not in self.rules:
            self.rules[field_name] = []
        self.rules[field_name].append(rule)
        return self

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate all fields against their rules.

        Args:
            data: Dictionary containing field values

        Returns:
            Dictionary mapping field names to lists of error messages
        """
        errors = {}

        for field_name, field_rules in self.rules.items():
            field_value = data.get(field_name)
            field_errors = []

            for rule in field_rules:
                if not rule.validate(field_value):
                    field_errors.append(rule.get_error_message(field_value))

            if field_errors:
                errors[field_name] = field_errors

        return errors

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """Check if data is valid (no errors)."""
        return not self.validate(data)


# Predefined validation rules for common clinical data

class ClinicalValidators:
    """Predefined validators for clinical data."""

    @staticmethod
    def turkish_tckn_validator(field_name: str = "TCKN") -> ValidationRule:
        """Validate Turkish ID number (11 digits, specific algorithm)."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^\d{11}$',
            description="11-digit Turkish ID number"
        )

    @staticmethod
    def name_validator(field_name: str = "name") -> ValidationRule:
        """Validate person names (Turkish characters allowed)."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^[a-zA-ZçğıöşüÇĞİÖŞÜ\s\-\.]+$',
            description="valid name (letters, spaces, hyphens, dots)"
        )

    @staticmethod
    def blood_pressure_validator(field_name: str = "blood_pressure") -> ValidationRule:
        """Validate blood pressure format (120/80)."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^\d{1,3}\/\d{1,3}$',
            description="blood pressure in format '120/80'"
        )

    @staticmethod
    def icd10_code_validator(field_name: str = "icd10_code") -> ValidationRule:
        """Validate ICD-10 code format."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^[A-Z]\d{2}(\.\d{1,2})?$',
            description="ICD-10 code format (e.g., 'I10', 'E11.9')"
        )

    @staticmethod
    def email_validator(field_name: str = "email") -> ValidationRule:
        """Validate email addresses."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            description="valid email address"
        )

    @staticmethod
    def phone_validator(field_name: str = "phone") -> ValidationRule:
        """Validate phone numbers (Turkish format)."""
        return RegexRule(
            field_name=field_name,
            pattern=r'^(\+90|0)?\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}$',
            description="valid Turkish phone number"
        )


# Convenience functions for common validation scenarios

def validate_patient_demographics(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate patient demographic data."""
    validator = Validator()

    # Name validations
    validator.add_rule("first_name", ClinicalValidators.name_validator("first_name"))
    validator.add_rule("last_name", ClinicalValidators.name_validator("last_name"))

    # ID validation
    validator.add_rule("tckn", ClinicalValidators.turkish_tckn_validator())

    # Birth date
    validator.add_rule("birth_date", DateRule("birth_date"))

    # Contact information
    validator.add_rule("email", ClinicalValidators.email_validator("email").__class__(
        "email", required=False
    ))
    validator.add_rule("phone", ClinicalValidators.phone_validator("phone").__class__(
        "phone", required=False
    ))

    return validator.validate(data)


def validate_vital_signs(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate vital signs data."""
    validator = Validator()

    # Blood pressure
    validator.add_rule("systolic", NumericRule("systolic", min_value=60, max_value=250))
    validator.add_rule("diastolic", NumericRule("diastolic", min_value=30, max_value=150))

    # Temperature
    validator.add_rule("temperature", NumericRule("temperature", min_value=35.0, max_value=42.0))

    # Heart rate
    validator.add_rule("heart_rate", NumericRule("heart_rate", min_value=30, max_value=200))

    # Oxygen saturation
    validator.add_rule("oxygen_sat", NumericRule("oxygen_sat", min_value=70, max_value=100))

    # Respiratory rate
    validator.add_rule("respiratory_rate", NumericRule("respiratory_rate", min_value=8, max_value=40))

    return validator.validate(data)


def validate_lab_results(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate laboratory results."""
    validator = Validator()

    # Common lab tests
    if "HbA1c" in data:
        validator.add_rule("HbA1c", NumericRule("HbA1c", min_value=3.0, max_value=15.0))

    if "CRP" in data:
        validator.add_rule("CRP", NumericRule("CRP", min_value=0.1, max_value=500.0))

    if "glucose" in data:
        validator.add_rule("glucose", NumericRule("glucose", min_value=20, max_value=500))

    if "cholesterol_ldl" in data:
        validator.add_rule("cholesterol_ldl", NumericRule("cholesterol_ldl", min_value=20, max_value=400))

    if "cholesterol_hdl" in data:
        validator.add_rule("cholesterol_hdl", NumericRule("cholesterol_hdl", min_value=10, max_value=200))

    if "creatinine" in data:
        validator.add_rule("creatinine", NumericRule("creatinine", min_value=0.1, max_value=20.0))

    return validator.validate(data)