"""Test EmailReader service get_email_by_id method."""

import pytest
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.models import Email


class TestEmailReaderGetById:
    """Test suite for EmailReader get_email_by_id method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = MockOutlookAdapter()
        self.email_reader = EmailReader(self.adapter)
    
    def test_get_email_by_id_returns_correct_email(self):
        """Test that EmailReader calls adapter correctly and returns email."""
        # This will fail until we implement get_email_by_id in EmailReader
        email = self.email_reader.get_email_by_id("inbox-001")
        
        assert isinstance(email, Email)
        assert email.id == "inbox-001"
        assert email.subject == "Weekly Team Meeting"
        assert email.folder_path == "Inbox"
    
    def test_get_email_by_id_propagates_adapter_error(self):
        """Test that EmailReader propagates ValueError from adapter."""
        # This will fail until we implement get_email_by_id in EmailReader
        with pytest.raises(ValueError, match="Email 'nonexistent-123' not found"):
            self.email_reader.get_email_by_id("nonexistent-123")
    
    def test_get_email_by_id_works_with_different_folders(self):
        """Test retrieval from sent items and drafts folders."""
        # This will fail until we implement get_email_by_id in EmailReader
        
        # Test sent email
        sent_email = self.email_reader.get_email_by_id("sent-001")
        assert sent_email.id == "sent-001"
        assert sent_email.folder_path == "Sent Items"
        
        # Test draft email
        draft_email = self.email_reader.get_email_by_id("draft-001")
        assert draft_email.id == "draft-001"
        assert draft_email.folder_path == "Drafts"