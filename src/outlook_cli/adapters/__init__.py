"""Adapter layer for Outlook integration.

This package provides the abstraction layer for Outlook operations,
enabling dependency injection and cross-platform development.

The OutlookAdapter abstract base class defines the contract that all
adapters must implement. MockOutlookAdapter provides a test implementation
with realistic test data for development and testing.
"""

from .outlook_adapter import OutlookAdapter
from .mock_adapter import MockOutlookAdapter

__all__ = ["OutlookAdapter", "MockOutlookAdapter"]