"""Adapter layer for Outlook integration.

This package provides the abstraction layer for Outlook operations,
enabling dependency injection and cross-platform development.

The OutlookAdapter abstract base class defines the contract that all
adapters must implement. MockOutlookAdapter provides a test implementation
with realistic test data for development and testing. PyWin32OutlookAdapter
provides real Windows COM integration for production use.
"""

from .outlook_adapter import OutlookAdapter
from .mock_adapter import MockOutlookAdapter

# Platform-specific adapter - only import on Windows
try:
    from .pywin32_adapter import PyWin32OutlookAdapter
    __all__ = ["OutlookAdapter", "MockOutlookAdapter", "PyWin32OutlookAdapter"]
except ImportError:
    # pywin32 not available (non-Windows platform)
    __all__ = ["OutlookAdapter", "MockOutlookAdapter"]