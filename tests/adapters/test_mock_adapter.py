"""Tests for MockOutlookAdapter implementation."""

import pytest
from outlook_cli.adapters import MockOutlookAdapter
from outlook_cli.models import Folder, Email


def test_mock_adapter_can_be_instantiated():
    """Test that MockOutlookAdapter can be instantiated."""
    adapter = MockOutlookAdapter()
    assert adapter is not None
    assert isinstance(adapter, MockOutlookAdapter)


def test_get_folders_returns_realistic_folder_list():
    """Test that get_folders() returns a realistic list of folders."""
    adapter = MockOutlookAdapter()
    folders = adapter.get_folders()
    
    # Should return multiple folders
    assert len(folders) >= 4
    
    # Should include standard Outlook folders
    folder_paths = [folder.path for folder in folders]
    assert "Inbox" in folder_paths
    assert "Sent Items" in folder_paths
    assert "Drafts" in folder_paths
    
    # Should include at least one subfolder
    assert any("/" in path for path in folder_paths)
    
    # All items should be Folder instances
    assert all(isinstance(folder, Folder) for folder in folders)
    
    # Folders should have realistic data
    for folder in folders:
        assert folder.path
        assert folder.name
        assert folder.email_count >= 0
        assert folder.unread_count >= 0
        assert folder.unread_count <= folder.email_count


def test_get_emails_returns_emails_for_valid_folder():
    """Test that get_emails() returns emails for a valid folder."""
    adapter = MockOutlookAdapter()
    
    # Test with Inbox folder
    emails = adapter.get_emails("Inbox")
    
    # Should return some emails
    assert len(emails) > 0
    
    # All items should be Email instances
    assert all(isinstance(email, Email) for email in emails)
    
    # Emails should have realistic data and belong to the folder
    for email in emails:
        assert email.id
        assert email.subject
        assert email.sender_email
        assert email.sender_name
        assert email.recipient_emails
        assert email.received_date
        assert email.body_text
        assert email.folder_path == "Inbox"


def test_get_emails_returns_different_emails_for_different_folders():
    """Test that get_emails() returns different emails for different folders."""
    adapter = MockOutlookAdapter()
    
    inbox_emails = adapter.get_emails("Inbox")
    sent_emails = adapter.get_emails("Sent Items")
    
    # Should have emails in both folders
    assert len(inbox_emails) > 0
    assert len(sent_emails) > 0
    
    # Email IDs should be different between folders
    inbox_ids = {email.id for email in inbox_emails}
    sent_ids = {email.id for email in sent_emails}
    assert inbox_ids.isdisjoint(sent_ids)
    
    # Folder paths should match
    assert all(email.folder_path == "Inbox" for email in inbox_emails)
    assert all(email.folder_path == "Sent Items" for email in sent_emails)


def test_get_folder_info_returns_correct_folder():
    """Test that get_folder_info() returns correct folder information."""
    adapter = MockOutlookAdapter()
    
    # Test with existing folder
    folder = adapter.get_folder_info("Inbox")
    
    assert isinstance(folder, Folder)
    assert folder.path == "Inbox"
    assert folder.name == "Inbox"
    assert folder.email_count == 25
    assert folder.unread_count == 5


def test_get_folder_info_raises_error_for_invalid_folder():
    """Test that get_folder_info() raises ValueError for non-existent folder."""
    adapter = MockOutlookAdapter()
    
    with pytest.raises(ValueError) as exc_info:
        adapter.get_folder_info("NonExistentFolder")
    
    assert "not found" in str(exc_info.value)


def test_move_email_successfully_moves_between_folders():
    """Test that move_email() successfully moves an email between folders."""
    adapter = MockOutlookAdapter()
    
    # Get initial state
    inbox_emails = adapter.get_emails("Inbox")
    drafts_emails = adapter.get_emails("Drafts")
    
    initial_inbox_count = len(inbox_emails)
    initial_drafts_count = len(drafts_emails)
    
    # Move first inbox email to drafts
    email_to_move = inbox_emails[0]
    original_id = email_to_move.id
    
    result = adapter.move_email(original_id, "Drafts")
    
    # Operation should succeed
    assert result is True
    
    # Check email was removed from Inbox
    new_inbox_emails = adapter.get_emails("Inbox")
    assert len(new_inbox_emails) == initial_inbox_count - 1
    assert not any(email.id == original_id for email in new_inbox_emails)
    
    # Check email was added to Drafts
    new_drafts_emails = adapter.get_emails("Drafts")
    assert len(new_drafts_emails) == initial_drafts_count + 1
    
    # Find the moved email and verify its folder_path was updated
    moved_email = next(email for email in new_drafts_emails if email.id == original_id)
    assert moved_email.folder_path == "Drafts"
    assert moved_email.subject == email_to_move.subject  # Other fields unchanged


def test_move_email_raises_error_for_invalid_email_id():
    """Test that move_email() raises ValueError for non-existent email."""
    adapter = MockOutlookAdapter()
    
    with pytest.raises(ValueError) as exc_info:
        adapter.move_email("invalid-email-id", "Drafts")
    
    assert "not found" in str(exc_info.value)


def test_move_email_raises_error_for_invalid_target_folder():
    """Test that move_email() raises ValueError for non-existent target folder."""
    adapter = MockOutlookAdapter()
    
    # Get a valid email ID
    inbox_emails = adapter.get_emails("Inbox")
    valid_email_id = inbox_emails[0].id
    
    with pytest.raises(ValueError) as exc_info:
        adapter.move_email(valid_email_id, "NonExistentFolder")
    
    assert "not found" in str(exc_info.value)