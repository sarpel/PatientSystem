"""
API input validation decorators for FastAPI endpoints.

Provides decorators for validating request data with proper error responses
and standardized validation across all API endpoints.
"""

from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status

from .validators import Validator
from .exceptions import ValidationError


def validate_request_data(
    validator: Validator,
    error_status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
):
    """
    Decorator for validating request data in FastAPI endpoints.

    Args:
        validator: Validator instance with configured rules
        error_status_code: HTTP status code for validation errors

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request data in kwargs (common FastAPI patterns)
            request_data = None

            # Look for common request data parameter names
            for param_name in ['data', 'request_data', 'body', 'payload']:
                if param_name in kwargs:
                    request_data = kwargs[param_name]
                    break

            # If no explicit data parameter, try to get it from the first argument after self
            if request_data is None and len(args) > 1:
                request_data = args[1]

            if request_data is None:
                raise HTTPException(
                    status_code=error_status_code,
                    detail="No request data provided for validation"
                )

            # Convert request data to dict if it's not already
            if hasattr(request_data, 'dict'):
                request_data = request_data.dict()
            elif hasattr(request_data, 'model_dump'):
                request_data = request_data.model_dump()
            elif not isinstance(request_data, dict):
                raise HTTPException(
                    status_code=error_status_code,
                    detail="Request data must be a dictionary or Pydantic model"
                )

            # Perform validation
            validation_errors = validator.validate(request_data)

            if validation_errors:
                error_details = []
                for field, errors in validation_errors.items():
                    error_details.extend([f"{field}: {error}" for error in errors])

                raise HTTPException(
                    status_code=error_status_code,
                    detail={
                        "error": "Validation failed",
                        "details": error_details,
                        "field_errors": validation_errors
                    }
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def validate_query_params(
    validator: Validator,
    error_status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
):
    """
    Decorator for validating query parameters in FastAPI endpoints.

    Args:
        validator: Validator instance with configured rules
        error_status_code: HTTP status code for validation errors

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Filter query parameters from kwargs
            query_params = {
                k: v for k, v in kwargs.items()
                if k in validator.rules
            }

            # Perform validation
            validation_errors = validator.validate(query_params)

            if validation_errors:
                error_details = []
                for field, errors in validation_errors.items():
                    error_details.extend([f"{field}: {error}" for error in errors])

                raise HTTPException(
                    status_code=error_status_code,
                    detail={
                        "error": "Query parameter validation failed",
                        "details": error_details,
                        "field_errors": validation_errors
                    }
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def validate_path_params(
    validator: Validator,
    error_status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
):
    """
    Decorator for validating path parameters in FastAPI endpoints.

    Args:
        validator: Validator instance with configured rules
        error_status_code: HTTP status code for validation errors

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Filter path parameters from kwargs
            path_params = {
                k: v for k, v in kwargs.items()
                if k in validator.rules
            }

            # Perform validation
            validation_errors = validator.validate(path_params)

            if validation_errors:
                error_details = []
                for field, errors in validation_errors.items():
                    error_details.extend([f"{field}: {error}" for error in errors])

                raise HTTPException(
                    status_code=error_status_code,
                    detail={
                        "error": "Path parameter validation failed",
                        "details": error_details,
                        "field_errors": validation_errors
                    }
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


class ValidationMiddleware:
    """
    Middleware class for adding validation to FastAPI applications.

    Can be used to add global validation rules for specific request patterns.
    """

    def __init__(self):
        self.global_validators = {}

    def add_global_validator(
        self,
        path_pattern: str,
        method: str,
        validator: Validator
    ):
        """
        Add a global validator for specific path patterns and HTTP methods.

        Args:
            path_pattern: URL pattern to match (regex)
            method: HTTP method (GET, POST, etc.)
            validator: Validator instance
        """
        key = f"{method.upper()}:{path_pattern}"
        self.global_validators[key] = validator

    def get_validator_for_request(self, path: str, method: str) -> Optional[Validator]:
        """
        Get validator for a specific request path and method.

        Args:
            path: Request path
            method: HTTP method

        Returns:
            Validator instance if found, None otherwise
        """
        key = f"{method.upper()}:{path}"
        return self.global_validators.get(key)

    def validate_request(
        self,
        path: str,
        method: str,
        data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate request data using global validators.

        Args:
            path: Request path
            method: HTTP method
            data: Request data

        Returns:
            Validation errors dictionary
        """
        validator = self.get_validator_for_request(path, method)
        if validator:
            return validator.validate(data)
        return {}


# Predefined validators for common API scenarios

class APIValidators:
    """Predefined validators for common API endpoints."""

    @staticmethod
    def patient_id_validator() -> Validator:
        """Validator for patient ID parameter."""
        from .validators import ClinicalValidators
        validator = Validator()
        validator.add_rule(
            "patient_id",
            ClinicalValidators.turkish_tckn_validator("patient_id")
        )
        return validator

    @staticmethod
    def diagnosis_request_validator() -> Validator:
        """Validator for diagnosis request data."""
        from .validators import LengthRule, EnumRule

        validator = Validator()

        # Chief complaints
        validator.add_rule(
            "chief_complaints",
            LengthRule("chief_complaints", min_length=1, max_length=1000)
        )

        # Vital signs validation
        validator.add_rule("systolic", validator.__class__(
            "systolic", required=False
        ).__class__("systolic", required=False))
        validator.add_rule("diastolic", validator.__class__(
            "diastolic", required=False
        ).__class__("diastolic", required=False))
        validator.add_rule("temperature", validator.__class__(
            "temperature", required=False
        ).__class__("temperature", required=False))
        validator.add_rule("heart_rate", validator.__class__(
            "heart_rate", required=False
        ).__class__("heart_rate", required=False))

        return validator

    @staticmethod
    def treatment_request_validator() -> Validator:
        """Validator for treatment request data."""
        from .validators import LengthRule

        validator = Validator()

        # Diagnosis
        validator.add_rule(
            "diagnosis",
            LengthRule("diagnosis", min_length=1, max_length=500)
        )

        # Severity level
        validator.add_rule(
            "severity",
            EnumRule("severity", ["mild", "moderate", "severe"], required=False)
        )

        return validator

    @staticmethod
    def drug_interaction_validator() -> Validator:
        """Validator for drug interaction check request."""
        from .validators import LengthRule, EnumRule

        validator = Validator()

        # Proposed drug
        validator.add_rule(
            "proposed_drug",
            LengthRule("proposed_drug", min_length=1, max_length=100)
        )

        # Severity filter
        validator.add_rule(
            "severity",
            EnumRule("severity", ["all", "major", "critical"], required=False)
        )

        return validator

    @staticmethod
    def search_validator() -> Validator:
        """Validator for search parameters."""
        from .validators import LengthRule

        validator = Validator()

        # Search query
        validator.add_rule(
            "query",
            LengthRule("query", min_length=1, max_length=100)
        )

        # Limit
        validator.add_rule(
            "limit",
            validator.__class__("limit", required=False).__class__(
                "limit", min_value=1, max_value=100, required=False
            )
        )

        return validator