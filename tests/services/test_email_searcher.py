"""Tests for EmailSearcher service."""

import pytest
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.models.email import Email


class TestEmailSearcher:
    """Test EmailSearcher service functionality."""
    
    def test_email_searcher_constructor_takes_adapter_parameter(self):
        """Test that EmailSearcher can be constructed with an OutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        
        # Act
        searcher = EmailSearcher(adapter)
        
        # Assert
        assert isinstance(searcher, EmailSearcher)
        assert isinstance(searcher._adapter, OutlookAdapter)
    
    def test_search_by_sender_email_returns_matching_emails(self):
        """Test that search_by_sender returns emails matching sender email address."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("manager@company.com")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 1
        assert all(isinstance(email, Email) for email in results)
        assert results[0].subject == "Weekly Team Meeting"
        assert results[0].sender_email == "manager@company.com"
    
    def test_search_by_sender_name_returns_matching_emails(self):
        """Test that search_by_sender returns emails matching sender display name."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("Alice Manager")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].sender_name == "Alice Manager"
        assert results[0].subject == "Weekly Team Meeting"
    
    def test_search_by_sender_case_insensitive(self):
        """Test that search_by_sender is case-insensitive."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("MANAGER@COMPANY.COM")
        
        # Assert
        assert len(results) == 1
        assert results[0].sender_email == "manager@company.com"
    
    def test_search_by_subject_partial_match_returns_matching_emails(self):
        """Test that search_by_subject returns emails with partial subject match."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_subject("Project")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 2  # "Project Update Required" + "Re: Project Update Required"
        assert all("project" in email.subject.lower() for email in results)
    
    def test_search_by_subject_case_insensitive(self):
        """Test that search_by_subject is case-insensitive."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_subject("MEETING")
        
        # Assert
        assert len(results) >= 1
        assert any("meeting" in email.subject.lower() for email in results)
    
    def test_search_emails_with_multiple_criteria_applies_and_logic(self):
        """Test that search_emails applies AND logic for multiple criteria."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_emails(sender="pm@company.com", subject="Project")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].subject == "Project Update Required"
        assert results[0].sender_email == "pm@company.com"
    
    def test_search_by_sender_with_folder_path_limits_scope(self):
        """Test that folder_path parameter limits search to specific folder."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("user@company.com", folder_path="Sent Items")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 2  # Only Sent Items emails
        assert all(email.folder_path == "Sent Items" for email in results)
        assert all(email.sender_email == "user@company.com" for email in results)
    
    def test_search_by_sender_with_no_folder_searches_all_folders(self):
        """Test that folder_path=None searches all folders."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("user@company.com")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 3  # 2 from Sent Items + 1 from Drafts
        folder_paths = {email.folder_path for email in results}
        assert "Sent Items" in folder_paths
        assert "Drafts" in folder_paths
    
    def test_search_returns_empty_list_for_no_matches(self):
        """Test that search methods return empty list when no emails match."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        results = searcher.search_by_sender("nonexistent@email.com")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_raises_error_for_invalid_folder_path(self):
        """Test that search methods raise ValueError for invalid folder path."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Folder 'NonExistentFolder' not found"):
            searcher.search_by_sender("user@company.com", folder_path="NonExistentFolder")


class TestEmailSearcherIntegration:
    """Integration tests for EmailSearcher with MockOutlookAdapter."""
    
    def test_email_searcher_integration_with_mock_adapter(self):
        """Test complete EmailSearcher functionality with MockOutlookAdapter."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act & Assert: Test all search methods work together
        # 1. Can search by sender email
        manager_emails = searcher.search_by_sender("manager@company.com")
        assert len(manager_emails) == 1
        assert manager_emails[0].subject == "Weekly Team Meeting"
        
        # 2. Can search by subject
        project_emails = searcher.search_by_subject("Project")
        assert len(project_emails) == 2
        
        # 3. Can combine search criteria
        combined_results = searcher.search_emails(sender="pm@company.com", subject="Project")
        assert len(combined_results) == 1
        assert combined_results[0].subject == "Project Update Required"
        
        # 4. Can limit search to specific folder
        sent_user_emails = searcher.search_by_sender("user@company.com", folder_path="Sent Items")
        assert len(sent_user_emails) == 2
        assert all(email.folder_path == "Sent Items" for email in sent_user_emails)
        
        # 5. Empty results work
        no_results = searcher.search_by_sender("nobody@nowhere.com")
        assert no_results == []
        
        # 6. Error handling works
        with pytest.raises(ValueError):
            searcher.search_by_sender("user@company.com", folder_path="DoesNotExist")