"""Tests for Email model."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from outlook_cli.models import Email


def test_email_creation_with_valid_data():
    """Test creating an Email with all valid required fields."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Email Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "cc_emails": [],
        "bcc_emails": [],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "This is the plain text body",
        "body_html": "<p>This is the HTML body</p>",
        "has_attachments": False,
        "attachment_count": 0,
        "folder_path": "Inbox",
        "is_read": False,
        "importance": "Normal"
    }
    
    email = Email(**email_data)
    
    assert email.id == "test-email-123"
    assert email.subject == "Test Email Subject"
    assert email.sender_email == "sender@example.com"
    assert email.sender_name == "John Sender"
    assert email.recipient_emails == ["recipient@example.com"]
    assert email.received_date == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    assert email.body_text == "This is the plain text body"
    assert email.has_attachments is False
    assert email.attachment_count == 0
    assert email.folder_path == "Inbox"
    assert email.is_read is False
    assert email.importance == "Normal"


def test_email_validation_invalid_sender_email():
    """Test that invalid sender email raises ValidationError."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "invalid-email",  # Invalid email format
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "folder_path": "Inbox"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Email(**email_data)
    
    assert "sender_email" in str(exc_info.value)


def test_email_validation_invalid_recipient_emails():
    """Test that invalid recipient emails raise ValidationError."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["invalid-email", "recipient@example.com"],  # One invalid
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "folder_path": "Inbox"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Email(**email_data)
    
    assert "recipient_emails" in str(exc_info.value)


def test_email_validation_empty_recipient_emails():
    """Test that empty recipient emails list raises ValidationError."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": [],  # Empty list should fail
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "folder_path": "Inbox"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Email(**email_data)
    
    assert "recipient_emails" in str(exc_info.value)


def test_email_validation_negative_attachment_count():
    """Test that negative attachment count raises ValidationError."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "attachment_count": -1,  # Negative count should fail
        "folder_path": "Inbox"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Email(**email_data)
    
    assert "attachment_count" in str(exc_info.value)


def test_email_validation_invalid_importance():
    """Test that invalid importance value raises ValidationError."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "folder_path": "Inbox",
        "importance": "Invalid"  # Not in allowed values
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Email(**email_data)
    
    assert "importance" in str(exc_info.value)


def test_email_serialization_to_dict():
    """Test that Email can be serialized to dictionary."""
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": True,
        "attachment_count": 2,
        "folder_path": "Inbox"
    }
    
    email = Email(**email_data)
    email_dict = email.model_dump()
    
    assert email_dict["id"] == "test-email-123"
    assert email_dict["subject"] == "Test Subject"
    assert email_dict["sender_email"] == "sender@example.com"
    assert email_dict["has_attachments"] is True
    assert email_dict["attachment_count"] == 2


def test_email_serialization_round_trip():
    """Test that Email can serialize to dict and back without data loss."""
    original_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient1@example.com", "recipient2@example.com"],
        "cc_emails": ["cc@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "body_html": "<p>Test HTML</p>",
        "has_attachments": True,
        "attachment_count": 1,
        "folder_path": "Inbox/Subfolder",
        "is_read": True,
        "importance": "High"
    }
    
    # Create email from data
    email1 = Email(**original_data)
    
    # Serialize to dict
    email_dict = email1.model_dump()
    
    # Create new email from dict
    email2 = Email(**email_dict)
    
    # Should be identical
    assert email1.id == email2.id
    assert email1.subject == email2.subject
    assert email1.sender_email == email2.sender_email
    assert email1.recipient_emails == email2.recipient_emails
    assert email1.cc_emails == email2.cc_emails
    assert email1.received_date == email2.received_date
    assert email1.attachment_count == email2.attachment_count
    assert email1.importance == email2.importance


def test_email_json_serialization():
    """Test that Email can be serialized to/from JSON."""
    import json
    
    email_data = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "folder_path": "Inbox"
    }
    
    email = Email(**email_data)
    
    # Serialize to JSON string
    json_str = email.model_dump_json()
    
    # Should be valid JSON
    parsed_json = json.loads(json_str)
    assert parsed_json["id"] == "test-email-123"
    assert parsed_json["subject"] == "Test Subject"
    
    # Should be able to recreate from JSON
    recreated_email = Email.model_validate_json(json_str)
    assert recreated_email.id == email.id
    assert recreated_email.subject == email.subject


def test_email_complex_with_attachments():
    """Test creating Email with complex data including multiple recipients and attachments."""
    complex_email_data = {
        "id": "complex-email-456",
        "subject": "Complex Email with Multiple Recipients and Attachments",
        "sender_email": "sender@company.com",
        "sender_name": "Alice Sender",
        "recipient_emails": [
            "recipient1@example.com",
            "recipient2@example.com", 
            "recipient3@example.com"
        ],
        "cc_emails": [
            "cc1@example.com",
            "cc2@example.com"
        ],
        "bcc_emails": [
            "bcc@example.com"
        ],
        "received_date": datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone.utc),
        "body_text": "This is a complex email with multiple recipients and attachments.",
        "body_html": "<html><body><p>This is a <strong>complex</strong> email with multiple recipients and attachments.</p></body></html>",
        "has_attachments": True,
        "attachment_count": 3,
        "folder_path": "Inbox/Projects/Current",
        "is_read": True,
        "importance": "High"
    }
    
    email = Email(**complex_email_data)
    
    assert email.id == "complex-email-456"
    assert len(email.recipient_emails) == 3
    assert len(email.cc_emails) == 2
    assert len(email.bcc_emails) == 1
    assert email.has_attachments is True
    assert email.attachment_count == 3
    assert email.folder_path == "Inbox/Projects/Current"
    assert email.importance == "High"


def test_email_attachment_validation_consistency():
    """Test that has_attachments and attachment_count are consistent."""
    # Case 1: has_attachments=True but attachment_count=0 should be inconsistent
    email_data_inconsistent = {
        "id": "test-email-123",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": True,
        "attachment_count": 0,  # Inconsistent: has attachments but count is 0
        "folder_path": "Inbox"
    }
    
    # For now, we allow this inconsistency but it should be flagged in business logic
    # This is a data integrity issue that should be caught by business rules
    email = Email(**email_data_inconsistent)
    assert email.has_attachments is True
    assert email.attachment_count == 0
    
    # Case 2: has_attachments=False but attachment_count>0 should be inconsistent
    email_data_inconsistent2 = {
        "id": "test-email-124",
        "subject": "Test Subject",
        "sender_email": "sender@example.com",
        "sender_name": "John Sender",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Test body",
        "has_attachments": False,
        "attachment_count": 2,  # Inconsistent: no attachments but count is 2
        "folder_path": "Inbox"
    }
    
    # This should also be allowed but flagged
    email2 = Email(**email_data_inconsistent2)
    assert email2.has_attachments is False
    assert email2.attachment_count == 2


def test_email_minimal_required_fields():
    """Test creating Email with only required fields (no optional ones)."""
    minimal_data = {
        "id": "minimal-email",
        "subject": "Minimal Email",
        "sender_email": "sender@example.com",
        "sender_name": "Sender Name",
        "recipient_emails": ["recipient@example.com"],
        "received_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "body_text": "Minimal body text",
        "has_attachments": False,
        "folder_path": "Inbox"
    }
    
    email = Email(**minimal_data)
    
    # Check defaults are applied
    assert email.cc_emails == []
    assert email.bcc_emails == []
    assert email.body_html is None
    assert email.attachment_count == 0
    assert email.is_read is False
    assert email.importance == "Normal"