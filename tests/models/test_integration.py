"""Integration tests for models working together."""

from datetime import datetime, timezone
import json
from outlook_cli.models import Email, Folder


def test_models_can_be_imported_together():
    """Test that both models can be imported and used together."""
    # Create a folder
    folder = Folder(
        path="Inbox",
        name="Inbox",
        email_count=2,
        unread_count=1
    )
    
    # Create emails in that folder
    email1 = Email(
        id="email-1",
        subject="First Email",
        sender_email="sender1@example.com",
        sender_name="Sender One",
        recipient_emails=["recipient@example.com"],
        received_date=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        body_text="First email body",
        has_attachments=False,
        folder_path=folder.path,  # Use folder path
        is_read=True
    )
    
    email2 = Email(
        id="email-2",
        subject="Second Email",
        sender_email="sender2@example.com",
        sender_name="Sender Two",
        recipient_emails=["recipient@example.com"],
        received_date=datetime(2024, 1, 15, 11, 30, 0, tzinfo=timezone.utc),
        body_text="Second email body",
        has_attachments=True,
        attachment_count=1,
        folder_path=folder.path,  # Use folder path
        is_read=False
    )
    
    # Verify relationships
    assert email1.folder_path == folder.path == "Inbox"
    assert email2.folder_path == folder.path == "Inbox"
    assert folder.email_count == 2
    assert folder.unread_count == 1  # email2 is unread


def test_models_json_serialization_together():
    """Test that both models can be serialized to JSON and back."""
    folder_data = {
        "path": "Inbox/Important",
        "name": "Important",
        "email_count": 1,
        "unread_count": 0
    }
    
    email_data = {
        "id": "important-email",
        "subject": "Important Message",
        "sender_email": "boss@company.com",
        "sender_name": "The Boss",
        "recipient_emails": ["employee@company.com"],
        "received_date": datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc),
        "body_text": "This is important",
        "has_attachments": False,
        "folder_path": "Inbox/Important",
        "is_read": True,
        "importance": "High"
    }
    
    # Create models
    folder = Folder(**folder_data)
    email = Email(**email_data)
    
    # Serialize both to JSON
    folder_json = folder.model_dump_json()
    email_json = email.model_dump_json()
    
    # Parse JSON to verify it's valid
    json.loads(folder_json)
    json.loads(email_json)
    
    # Recreate from JSON
    folder_recreated = Folder.model_validate_json(folder_json)
    email_recreated = Email.model_validate_json(email_json)
    
    # Verify integrity
    assert folder_recreated.path == folder.path
    assert email_recreated.folder_path == folder.path
    assert email_recreated.importance == "High"


def test_models_validation_works_independently():
    """Test that validation works correctly for both models independently."""
    # Test folder validation
    try:
        Folder(
            path="",  # Invalid empty path
            name="Test",
            email_count=5,
            unread_count=2
        )
        assert False, "Should have raised ValidationError"
    except Exception as e:
        assert "path" in str(e)
    
    # Test email validation
    try:
        Email(
            id="test",
            subject="Test",
            sender_email="invalid-email",  # Invalid email
            sender_name="Test",
            recipient_emails=["valid@example.com"],
            received_date=datetime.now(timezone.utc),
            body_text="Test",
            has_attachments=False,
            folder_path="Inbox"
        )
        assert False, "Should have raised ValidationError"
    except Exception as e:
        assert "sender_email" in str(e)


def test_email_folder_path_consistency():
    """Test that email folder_path values are consistent with Folder paths."""
    folders = [
        Folder(path="Inbox", name="Inbox", email_count=3, unread_count=1),
        Folder(path="Inbox/Archive", name="Archive", email_count=10, unread_count=0),
        Folder(path="Sent Items", name="Sent Items", email_count=5, unread_count=0)
    ]
    
    emails = [
        Email(
            id="email-1",
            subject="Email in Inbox",
            sender_email="sender@example.com",
            sender_name="Sender",
            recipient_emails=["recipient@example.com"],
            received_date=datetime.now(timezone.utc),
            body_text="Body",
            has_attachments=False,
            folder_path="Inbox"
        ),
        Email(
            id="email-2", 
            subject="Email in Archive",
            sender_email="sender@example.com",
            sender_name="Sender",
            recipient_emails=["recipient@example.com"],
            received_date=datetime.now(timezone.utc),
            body_text="Body",
            has_attachments=False,
            folder_path="Inbox/Archive"
        )
    ]
    
    # Verify folder paths exist in folder list
    folder_paths = [f.path for f in folders]
    for email in emails:
        assert email.folder_path in folder_paths, f"Email folder_path '{email.folder_path}' not found in folder list"