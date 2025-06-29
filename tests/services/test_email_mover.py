"""Tests for EmailMover service."""

import pytest
from outlook_cli.services.email_mover import EmailMover
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.adapters.outlook_adapter import OutlookAdapter


class TestEmailMover:
    """Test EmailMover service functionality."""
    
    def test_email_mover_constructor_takes_adapter_parameter(self):
        """Test that EmailMover can be constructed with an OutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        
        # Act
        mover = EmailMover(adapter)
        
        # Assert
        assert isinstance(mover, EmailMover)
        assert isinstance(mover._adapter, OutlookAdapter)
    
    def test_move_email_to_folder_returns_boolean_success(self):
        """Test that move_email_to_folder returns True for successful move."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Act
        result = mover.move_email_to_folder("inbox-001", "Drafts")
        
        # Assert
        assert isinstance(result, bool)
        assert result is True
    
    def test_move_email_to_folder_raises_error_for_invalid_email_id(self):
        """Test that move_email_to_folder raises ValueError for invalid email ID."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email 'nonexistent' not found"):
            mover.move_email_to_folder("nonexistent", "Drafts")
    
    def test_move_email_to_folder_raises_error_for_invalid_target_folder(self):
        """Test that move_email_to_folder raises ValueError for invalid target folder."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Target folder 'BadFolder' not found"):
            mover.move_email_to_folder("inbox-001", "BadFolder")
    
    def test_move_multiple_emails_returns_dict_with_status(self):
        """Test that move_multiple_emails returns Dict[str, bool] with status for each email."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        email_ids = ["inbox-001", "inbox-002"]
        
        # Act
        results = mover.move_multiple_emails(email_ids, "Drafts")
        
        # Assert
        assert isinstance(results, dict)
        assert len(results) == 2
        assert results["inbox-001"] is True
        assert results["inbox-002"] is True
        assert all(isinstance(success, bool) for success in results.values())
    
    def test_move_multiple_emails_handles_mixed_success_failure(self):
        """Test that move_multiple_emails handles partial failures gracefully."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        email_ids = ["inbox-001", "nonexistent", "inbox-002"]
        
        # Act
        results = mover.move_multiple_emails(email_ids, "Drafts")
        
        # Assert
        assert isinstance(results, dict)
        assert len(results) == 3
        assert results["inbox-001"] is True
        assert results["nonexistent"] is False  # Failed gracefully
        assert results["inbox-002"] is True
    
    def test_move_multiple_emails_with_invalid_target_folder(self):
        """Test that move_multiple_emails handles invalid target folder."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        email_ids = ["inbox-001", "inbox-002"]
        
        # Act
        results = mover.move_multiple_emails(email_ids, "BadFolder")
        
        # Assert
        assert isinstance(results, dict)
        assert len(results) == 2
        assert results["inbox-001"] is False  # Failed due to bad folder
        assert results["inbox-002"] is False  # Failed due to bad folder
    
    def test_move_multiple_emails_with_empty_list(self):
        """Test that move_multiple_emails handles empty email list."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Act
        results = mover.move_multiple_emails([], "Drafts")
        
        # Assert
        assert isinstance(results, dict)
        assert len(results) == 0


class TestEmailMoverIntegration:
    """Integration tests for EmailMover with MockOutlookAdapter."""
    
    def test_email_mover_integration_with_mock_adapter(self):
        """Test complete EmailMover functionality with MockOutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Act & Assert: Test all methods work together
        # 1. Can move single email
        result = mover.move_email_to_folder("inbox-001", "Custom/Archive")
        assert result is True
        
        # 2. Can verify email was actually moved
        archive_emails = adapter.get_emails("Custom/Archive")
        moved_email = next((email for email in archive_emails if email.id == "inbox-001"), None)
        assert moved_email is not None
        assert moved_email.folder_path == "Custom/Archive"
        
        # 3. Can move multiple emails
        batch_results = mover.move_multiple_emails(["inbox-002", "inbox-003"], "Drafts")
        assert batch_results["inbox-002"] is True
        assert batch_results["inbox-003"] is True
        
        # 4. Can verify batch move worked
        drafts_emails = adapter.get_emails("Drafts")
        moved_email_ids = {email.id for email in drafts_emails}
        assert "inbox-002" in moved_email_ids
        assert "inbox-003" in moved_email_ids
        
        # 5. Error handling works for invalid operations
        with pytest.raises(ValueError):
            mover.move_email_to_folder("nonexistent", "Drafts")
        
        # 6. Batch operation handles mixed scenarios
        mixed_results = mover.move_multiple_emails(["sent-001", "badid"], "Custom/Archive")
        assert mixed_results["sent-001"] is True
        assert mixed_results["badid"] is False