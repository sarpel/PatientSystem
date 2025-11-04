"""
Error handling utilities for standardized error management.

Provides centralized error handling, logging, and error reporting
functionality across the application.
"""

import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type

from loguru import logger

from .exceptions import BasePatientSystemError, ErrorCategory, ErrorSeverity


class ErrorHandler:
    """
    Centralized error handling utility.

    Provides consistent error logging, reporting, and transformation
    across all application modules.
    """

    @staticmethod
    def log_error(
        error: Exception, operation: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error with appropriate severity level.

        Args:
            error: The exception to log
            operation: Operation context where error occurred
            context: Additional context information
        """
        if isinstance(error, BasePatientSystemError):
            error_info = error.to_dict()
            if operation:
                error_info["operation"] = operation
            if context:
                error_info["additional_context"] = context

            # Log based on severity
            if error.severity == ErrorSeverity.CRITICAL:
                logger.critical(f"Critical error in {operation}: {error.message}", extra=error_info)
            elif error.severity == ErrorSeverity.HIGH:
                logger.error(
                    f"High severity error in {operation}: {error.message}", extra=error_info
                )
            elif error.severity == ErrorSeverity.MEDIUM:
                logger.warning(
                    f"Medium severity error in {operation}: {error.message}", extra=error_info
                )
            else:
                logger.info(f"Low severity error in {operation}: {error.message}", extra=error_info)
        else:
            # Generic exception
            logger.error(
                f"Unhandled exception in {operation}: {str(error)}",
                extra={
                    "error_type": type(error).__name__,
                    "operation": operation,
                    "context": context or {},
                    "traceback": traceback.format_exc(),
                },
            )

    @staticmethod
    def wrap_error(
        error: Exception,
        operation: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ) -> BasePatientSystemError:
        """
        Wrap generic exceptions in appropriate PatientSystem exceptions.

        Args:
            error: Original exception
            operation: Operation where error occurred
            category: Error category for the wrapped exception
            severity: Error severity level
            context: Additional context information

        Returns:
            Appropriate PatientSystem exception
        """
        from .exceptions import (
            AIServiceError,
            APIError,
            BusinessLogicError,
            ConfigurationError,
            DatabaseError,
            ExternalServiceError,
            ValidationError,
        )

        # Determine appropriate exception type based on category or error type
        if category == ErrorCategory.DATABASE:
            return DatabaseError(
                message=f"Database operation failed in {operation}: {str(error)}",
                cause=error,
                context=context,
            )
        elif category == ErrorCategory.AI_SERVICE:
            return AIServiceError(
                message=f"AI service error in {operation}: {str(error)}",
                cause=error,
                context=context,
            )
        elif category == ErrorCategory.VALIDATION:
            return ValidationError(
                message=f"Validation error in {operation}: {str(error)}",
                cause=error,
                context=context,
            )
        elif category == ErrorCategory.API:
            return APIError(
                message=f"API error in {operation}: {str(error)}", cause=error, context=context
            )
        elif category == ErrorCategory.BUSINESS_LOGIC:
            return BusinessLogicError(
                message=f"Business logic error in {operation}: {str(error)}",
                operation=operation,
                cause=error,
                context=context,
            )
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return ExternalServiceError(
                message=f"External service error in {operation}: {str(error)}",
                cause=error,
                context=context,
            )
        else:
            return BasePatientSystemError(
                message=f"System error in {operation}: {str(error)}",
                category=category,
                severity=severity,
                context={"original_error_type": type(error).__name__, **(context or {})},
                cause=error,
            )

    @staticmethod
    def safe_execute(
        func: Callable,
        *args,
        operation: Optional[str] = None,
        default_return: Any = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Safely execute a function with standardized error handling.

        Args:
            func: Function to execute
            *args: Function arguments
            operation: Operation description for error context
            default_return: Default return value if function fails
            category: Error category for wrapped exceptions
            severity: Error severity level
            context: Additional context information
            **kwargs: Function keyword arguments

        Returns:
            Function result or default_return if error occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            op_name = operation or f"{func.__name__} execution"
            wrapped_error = ErrorHandler.wrap_error(e, op_name, category, severity, context)
            ErrorHandler.log_error(wrapped_error, op_name, context)

            # If original error was already a PatientSystem error, re-raise it
            if isinstance(e, BasePatientSystemError):
                raise e
            # Otherwise raise the wrapped error
            raise wrapped_error from e


def handle_errors(
    operation: Optional[str] = None,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    default_return: Any = None,
    re_raise: bool = True,
):
    """
    Decorator for standardized error handling in functions.

    Args:
        operation: Operation description
        category: Error category for wrapped exceptions
        severity: Error severity level
        context: Additional context information
        default_return: Default return value if error occurs and re_raise=False
        re_raise: Whether to re-raise exceptions or return default_return
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or f"{func.__module__}.{func.__name__}"

            try:
                return func(*args, **kwargs)
            except Exception as e:
                wrapped_error = ErrorHandler.wrap_error(e, op_name, category, severity, context)
                ErrorHandler.log_error(wrapped_error, op_name, context)

                if re_raise:
                    # If original error was already a PatientSystem error, re-raise it
                    if isinstance(e, BasePatientSystemError):
                        raise e
                    # Otherwise raise the wrapped error
                    raise wrapped_error from e
                else:
                    return default_return

        return wrapper

    return decorator


@contextmanager
def error_context(
    operation: str,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for standardized error handling.

    Args:
        operation: Operation description
        category: Error category for wrapped exceptions
        severity: Error severity level
        context: Additional context information
    """
    try:
        yield
    except Exception as e:
        wrapped_error = ErrorHandler.wrap_error(e, operation, category, severity, context)
        ErrorHandler.log_error(wrapped_error, operation, context)

        # If original error was already a PatientSystem error, re-raise it
        if isinstance(e, BasePatientSystemError):
            raise e
        # Otherwise raise the wrapped error
        raise wrapped_error from e
