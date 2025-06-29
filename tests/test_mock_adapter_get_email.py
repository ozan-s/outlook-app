"""Test MockOutlookAdapter get_email_by_id implementation."""

import pytest
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.models import Email


class TestMockAdapterGetEmailById:
    """Test suite for MockOutlookAdapter get_email_by_id method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = MockOutlookAdapter()
    
    def test_get_email_by_id_returns_correct_inbox_email(self):
        """Test retrieving an existing inbox email by ID."""
        # This will fail until we implement get_email_by_id
        email = self.adapter.get_email_by_id("inbox-001")
        
        assert isinstance(email, Email)
        assert email.id == "inbox-001"
        assert email.subject == "Weekly Team Meeting"
        assert email.sender_email == "manager@company.com"
        assert email.folder_path == "Inbox"
    
    def test_get_email_by_id_returns_correct_sent_email(self):
        """Test retrieving an existing sent email by ID."""
        # This will fail until we implement get_email_by_id
        email = self.adapter.get_email_by_id("sent-001")
        
        assert isinstance(email, Email)
        assert email.id == "sent-001"
        assert email.subject == "Re: Project Update Required"
        assert email.sender_email == "user@company.com"
        assert email.folder_path == "Sent Items"
    
    def test_get_email_by_id_returns_correct_draft_email(self):
        """Test retrieving an existing draft email by ID."""
        # This will fail until we implement get_email_by_id
        email = self.adapter.get_email_by_id("draft-001")
        
        assert isinstance(email, Email)
        assert email.id == "draft-001"
        assert email.subject == "Vacation Request"
        assert email.folder_path == "Drafts"
    
    def test_get_email_by_id_raises_value_error_for_nonexistent_email(self):
        """Test that get_email_by_id raises ValueError for non-existent email."""
        # This will fail until we implement get_email_by_id
        with pytest.raises(ValueError, match="Email 'nonexistent-123' not found"):
            self.adapter.get_email_by_id("nonexistent-123")
    
    def test_get_email_by_id_raises_value_error_for_empty_string(self):
        """Test that get_email_by_id raises ValueError for empty email ID."""
        # This will fail until we implement get_email_by_id
        with pytest.raises(ValueError, match="Email '' not found"):
            self.adapter.get_email_by_id("")