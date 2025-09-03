"""
Custom exceptions for Truth and Dare API.

This module defines all custom exceptions used throughout the application
with proper HTTP status codes and error messages.
"""

from typing import Any


class TruthDareAPIException(Exception):
    """Base exception class for Truth and Dare API."""

    def __init__(self, message: str, status_code: int = 500, details: dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DataLoadError(TruthDareAPIException):
    """Raised when data files cannot be loaded."""

    def __init__(self, file_path: str, details: dict[str, Any] | None = None):
        message = f"Failed to load data file: {file_path}"
        super().__init__(message, status_code=500, details=details)


class CategoryNotFoundError(TruthDareAPIException):
    """Raised when a requested category is not found."""

    def __init__(self, category: str, available_categories: list):
        message = f"Category '{category}' not found. Available categories: {', '.join(available_categories)}"
        details = {"requested_category": category, "available_categories": available_categories}
        super().__init__(message, status_code=404, details=details)


class DifficultyNotFoundError(TruthDareAPIException):
    """Raised when a requested difficulty level is not found."""

    def __init__(self, difficulty: str, available_difficulties: list):
        message = f"Difficulty '{difficulty}' not found. Available difficulties: {', '.join(available_difficulties)}"
        details = {
            "requested_difficulty": difficulty,
            "available_difficulties": available_difficulties,
        }
        super().__init__(message, status_code=404, details=details)


class NoDataAvailableError(TruthDareAPIException):
    """Raised when no data is available for the requested filter."""

    def __init__(self, filter_type: str, filter_value: str):
        message = f"No data available for {filter_type}: '{filter_value}'"
        details = {"filter_type": filter_type, "filter_value": filter_value}
        super().__init__(message, status_code=404, details=details)


class ValidationError(TruthDareAPIException):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation error for field '{field}' with value '{value}': {reason}"
        details = {"field": field, "value": value, "reason": reason}
        super().__init__(message, status_code=422, details=details)
