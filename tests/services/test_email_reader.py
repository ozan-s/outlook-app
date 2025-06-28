"""Tests for EmailReader service."""

import pytest
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.adapters.outlook_adapter import OutlookAdapter


class TestEmailReader:
    """Test EmailReader service functionality."""
    
    def test_email_reader_constructor_takes_adapter_parameter(self):
        """Test that EmailReader can be constructed with an OutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        
        # Act
        reader = EmailReader(adapter)
        
        # Assert
        assert isinstance(reader, EmailReader)
        assert isinstance(reader._adapter, OutlookAdapter)