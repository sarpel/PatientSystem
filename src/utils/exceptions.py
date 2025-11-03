"""
Custom exception classes for the PatientSystem application.

Provides standardized exception handling with proper categorization
and context information for better error reporting and debugging.
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better error classification."""

    DATABASE = "database"
    AI_SERVICE = "ai_service"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"


class BasePatientSystemError(Exception):
    """
    Base exception class for all PatientSystem errors.

    Provides structured error information with context, severity, and category.
    """

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class DatabaseError(BasePatientSystemError):
    """Database-related errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=severity,
            context=context,
            cause=cause,
        )


class AIServiceError(BasePatientSystemError):
    """AI service provider errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if provider:
            context["provider"] = provider

        super().__init__(
            message=message,
            category=ErrorCategory.AI_SERVICE,
            severity=severity,
            context=context,
            cause=cause,
        )


class ValidationError(BasePatientSystemError):
    """Data validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=severity,
            context=context,
            cause=cause,
        )


class APIError(BasePatientSystemError):
    """API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if status_code:
            context["status_code"] = status_code
        if endpoint:
            context["endpoint"] = endpoint

        super().__init__(
            message=message,
            category=ErrorCategory.API,
            severity=severity,
            context=context,
            cause=cause,
        )


class BusinessLogicError(BasePatientSystemError):
    """Business logic validation errors."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if operation:
            context["operation"] = operation

        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=severity,
            context=context,
            cause=cause,
        )


class ExternalServiceError(BasePatientSystemError):
    """External service integration errors."""

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if service:
            context["service"] = service

        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=severity,
            context=context,
            cause=cause,
        )


class ConfigurationError(BasePatientSystemError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        context = context or {}
        if config_key:
            context["config_key"] = config_key

        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            severity=severity,
            context=context,
            cause=cause,
        )
