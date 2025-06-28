"""Tests for EmailReader service."""

import pytest
from typing import List, Dict
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.models.email import Email


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
    
    def test_get_emails_from_folder_returns_list_of_emails(self):
        """Test that get_emails_from_folder returns List[Email] for valid folder."""
        # Arrange
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Act
        emails = reader.get_emails_from_folder("Inbox")
        
        # Assert
        assert isinstance(emails, list)
        assert len(emails) == 3  # MockAdapter has 3 inbox emails
        assert all(isinstance(email, Email) for email in emails)
        assert emails[0].folder_path == "Inbox"
    
    def test_get_emails_from_folder_raises_error_for_nonexistent_folder(self):
        """Test that get_emails_from_folder raises ValueError for invalid folder."""
        # Arrange
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Folder 'NonExistentFolder' not found"):
            reader.get_emails_from_folder("NonExistentFolder")
    
    def test_get_all_emails_returns_dict_of_folder_emails(self):
        """Test that get_all_emails returns Dict[str, List[Email]] for all folders."""
        # Arrange
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Act
        all_emails = reader.get_all_emails()
        
        # Assert
        assert isinstance(all_emails, dict)
        assert "Inbox" in all_emails
        assert "Sent Items" in all_emails
        assert "Drafts" in all_emails
        assert len(all_emails["Inbox"]) == 3
        assert len(all_emails["Sent Items"]) == 2
        assert len(all_emails["Drafts"]) == 1
        assert all(isinstance(email, Email) for emails in all_emails.values() for email in emails)


class TestEmailReaderIntegration:
    """Integration tests for EmailReader with MockOutlookAdapter."""
    
    def test_email_reader_integration_with_mock_adapter(self):
        """Test complete EmailReader functionality with MockOutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Act & Assert: Test all methods work together
        # 1. Can get specific folder emails
        inbox_emails = reader.get_emails_from_folder("Inbox")
        assert len(inbox_emails) == 3
        assert inbox_emails[0].subject == "Weekly Team Meeting"
        
        # 2. Can get all emails
        all_emails = reader.get_all_emails()
        assert len(all_emails) == 6  # All folder paths from MockAdapter
        
        # 3. Error handling works
        with pytest.raises(ValueError):
            reader.get_emails_from_folder("DoesNotExist")
        
        # 4. Empty folders work (folders with no emails)
        deleted_emails = reader.get_emails_from_folder("Deleted Items")
        assert deleted_emails == []