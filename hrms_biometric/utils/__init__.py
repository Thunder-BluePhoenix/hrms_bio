# hrms_biometric/utils/__init__.py

"""
Utilities module for HRMS Biometric app

This module contains utility functions and helper methods used throughout the application.
"""

__version__ = "0.0.1"

# Import commonly used utilities
from .jinja_methods import (
    get_biometric_status,
    format_attendance_time
)

__all__ = [
    'get_biometric_status',
    'format_attendance_time'
]