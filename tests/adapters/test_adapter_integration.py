"""Integration tests for adapter layer."""

from outlook_cli.adapters import OutlookAdapter, MockOutlookAdapter
from outlook_cli.models import Email, Folder


def test_mock_adapter_implements_outlook_adapter_interface():
    """Test that MockOutlookAdapter properly implements OutlookAdapter interface."""
    adapter = MockOutlookAdapter()
    
    # Should be instance of both MockOutlookAdapter and OutlookAdapter
    assert isinstance(adapter, MockOutlookAdapter)
    assert isinstance(adapter, OutlookAdapter)


def test_adapter_integration_with_pydantic_models():
    """Test that adapter works seamlessly with Pydantic Email and Folder models."""
    adapter = MockOutlookAdapter()
    
    # Test folder model integration
    folders = adapter.get_folders()
    assert all(isinstance(folder, Folder) for folder in folders)
    
    # Test folder serialization/deserialization
    folder_dict = folders[0].model_dump()
    recreated_folder = Folder.model_validate(folder_dict)
    assert recreated_folder.path == folders[0].path
    
    # Test email model integration
    emails = adapter.get_emails("Inbox")
    assert all(isinstance(email, Email) for email in emails)
    
    # Test email serialization/deserialization
    email_dict = emails[0].model_dump()
    recreated_email = Email.model_validate(email_dict)
    assert recreated_email.id == emails[0].id


def test_dependency_injection_pattern():
    """Test that adapter can be used in dependency injection pattern."""
    def email_service_function(adapter: OutlookAdapter) -> int:
        """Example service function that accepts any OutlookAdapter."""
        folders = adapter.get_folders()
        total_emails = 0
        for folder in folders:
            emails = adapter.get_emails(folder.path)
            total_emails += len(emails)
        return total_emails
    
    # Should work with MockOutlookAdapter
    mock_adapter = MockOutlookAdapter()
    total_count = email_service_function(mock_adapter)
    
    # Should return reasonable count based on our test data
    assert total_count > 0
    assert isinstance(total_count, int)


def test_adapter_data_consistency():
    """Test that adapter maintains data consistency across operations."""
    adapter = MockOutlookAdapter()
    
    # Get folder info and compare with email counts
    inbox_folder = adapter.get_folder_info("Inbox")
    inbox_emails = adapter.get_emails("Inbox")
    
    # Folder email count should match actual emails (our test data is consistent)
    assert len(inbox_emails) <= inbox_folder.email_count  # Can be <= due to pagination in future
    
    # Test that unread count is reasonable
    unread_emails = [email for email in inbox_emails if not email.is_read]
    assert len(unread_emails) <= inbox_folder.unread_count


def test_adapter_cross_folder_operations():
    """Test adapter operations across multiple folders."""
    adapter = MockOutlookAdapter()
    
    # Get all folders and emails
    folders = adapter.get_folders()
    all_email_ids = set()
    
    for folder in folders:
        emails = adapter.get_emails(folder.path)
        folder_email_ids = {email.id for email in emails}
        
        # Email IDs should be unique across all folders
        assert all_email_ids.isdisjoint(folder_email_ids)
        all_email_ids.update(folder_email_ids)
        
        # All emails should have correct folder_path
        assert all(email.folder_path == folder.path for email in emails)
    
    # Should have found some emails across folders
    assert len(all_email_ids) > 0


def test_adapter_error_handling_consistency():
    """Test that adapter handles errors consistently across methods."""
    adapter = MockOutlookAdapter()
    
    # All methods should raise ValueError for invalid inputs
    try:
        adapter.get_folder_info("InvalidFolder")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
    
    try:
        adapter.move_email("invalid-id", "Inbox")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
    
    try:
        valid_email_id = adapter.get_emails("Inbox")[0].id
        adapter.move_email(valid_email_id, "InvalidFolder")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)