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


class TestEmailSearcherFiltering:
    """Test new filtering capabilities added in Milestone 006."""
    
    def test_filter_by_read_status_is_read_returns_only_read_emails(self):
        """Test that filter_by_read_status with is_read=True returns only read emails."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox (mixed read/unread)
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_read_status(inbox_emails, is_read=True)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) > 0  # Should have at least some read emails
        assert all(email.is_read for email in results)
        # Should not include unread emails
        unread_emails = [email for email in inbox_emails if not email.is_read]
        for unread_email in unread_emails:
            assert unread_email not in results
    
    def test_filter_by_read_status_is_unread_returns_only_unread_emails(self):
        """Test that filter_by_read_status with is_unread=True returns only unread emails."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox (mixed read/unread) 
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_read_status(inbox_emails, is_unread=True)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) > 0  # Should have at least some unread emails
        assert all(not email.is_read for email in results)
        # Should not include read emails
        read_emails = [email for email in inbox_emails if email.is_read]
        for read_email in read_emails:
            assert read_email not in results
    
    def test_filter_by_read_status_no_filter_returns_all_emails(self):
        """Test that filter_by_read_status with no flags returns all emails unchanged."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_read_status(inbox_emails)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == len(inbox_emails)
        assert results == inbox_emails
    
    def test_filter_by_attachments_has_attachment_returns_only_emails_with_attachments(self):
        """Test that filter_by_attachments with has_attachment=True returns only emails with attachments."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox (mixed attachment status)
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_attachments(inbox_emails, has_attachment=True)
        
        # Assert - this will fail initially as method doesn't exist
        assert isinstance(results, list)
        assert len(results) > 0  # Should have at least some emails with attachments
        assert all(email.has_attachments for email in results)
        # Should not include emails without attachments
        no_attachment_emails = [email for email in inbox_emails if not email.has_attachments]
        for no_attachment_email in no_attachment_emails:
            assert no_attachment_email not in results
    
    def test_filter_by_attachments_no_attachment_returns_only_emails_without_attachments(self):
        """Test that filter_by_attachments with no_attachment=True returns only emails without attachments."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox (mixed attachment status)
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_attachments(inbox_emails, no_attachment=True)
        
        # Assert - this will fail initially as method doesn't exist
        assert isinstance(results, list)
        assert len(results) > 0  # Should have at least some emails without attachments
        assert all(not email.has_attachments for email in results)
        # Should not include emails with attachments
        attachment_emails = [email for email in inbox_emails if email.has_attachments]
        for attachment_email in attachment_emails:
            assert attachment_email not in results
    
    def test_filter_by_attachments_no_filter_returns_all_emails(self):
        """Test that filter_by_attachments with no flags returns all emails unchanged."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_attachments(inbox_emails)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == len(inbox_emails)
        assert results == inbox_emails
    
    def test_filter_by_importance_high_returns_only_high_importance_emails(self):
        """Test that filter_by_importance with importance='high' returns only high importance emails."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox (has high importance email)
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act
        results = searcher.filter_by_importance(inbox_emails, importance="high")
        
        # Assert - this will fail initially as method doesn't exist
        assert isinstance(results, list)
        assert len(results) > 0  # Should have at least one high importance email
        assert all(email.importance == "High" for email in results)
        # Should not include non-high importance emails
        non_high_emails = [email for email in inbox_emails if email.importance != "High"]
        for non_high_email in non_high_emails:
            assert non_high_email not in results
    
    def test_filter_by_exclusions_not_sender_excludes_matching_senders(self):
        """Test that filter_by_exclusions with not_sender excludes emails from specified sender."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act - exclude emails from IT Support
        results = searcher.filter_by_exclusions(inbox_emails, not_sender="it@company.com")
        
        # Assert - this will fail initially as method doesn't exist
        assert isinstance(results, list)
        assert len(results) < len(inbox_emails)  # Should exclude some emails
        # Should not include emails from IT Support
        for email in results:
            assert "it@company.com" not in email.sender_email.lower()
            assert "it support" not in email.sender_name.lower()
    
    def test_filter_by_exclusions_not_subject_excludes_matching_subjects(self):
        """Test that filter_by_exclusions with not_subject excludes emails with matching subject."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get all emails from Inbox
        inbox_emails = adapter.get_emails("Inbox")
        
        # Act - exclude emails with "meeting" in subject
        results = searcher.filter_by_exclusions(inbox_emails, not_subject="meeting")
        
        # Assert - this will fail initially as method doesn't exist
        assert isinstance(results, list)
        assert len(results) < len(inbox_emails)  # Should exclude some emails
        # Should not include emails with "meeting" in subject
        for email in results:
            assert "meeting" not in email.subject.lower()
    
    def test_search_emails_enhanced_with_all_new_filters(self):
        """Test that enhanced search_emails method supports all new filter types."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act - this will fail initially as enhanced method doesn't exist
        results = searcher.search_emails(
            sender=None,
            subject=None,
            folder_path=None,
            since=None,
            until=None,
            is_read=True,
            has_attachment=True,
            importance="high"
        )
        
        # Assert
        assert isinstance(results, list)
        # All returned emails should meet ALL criteria
        for email in results:
            assert email.is_read  # Must be read
            assert email.has_attachments  # Must have attachments
            assert email.importance == "High"  # Must be high importance
    
    def test_search_emails_with_filter_combinations(self):
        """Test that search_emails works with various filter combinations."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act - Filter for unread emails without attachments, excluding meetings
        results = searcher.search_emails(
            is_unread=True,
            no_attachment=True,
            not_subject="meeting"
        )
        
        # Assert
        assert isinstance(results, list)
        for email in results:
            assert not email.is_read  # Must be unread
            assert not email.has_attachments  # Must not have attachments
            assert "meeting" not in email.subject.lower()  # Must not have "meeting" in subject


class TestEmailSearcherCLIIntegration:
    """Test CLI integration for new filtering features."""
    
    def test_cli_integration_with_new_filters_mocked(self):
        """Test that enhanced search_emails integrates with CLI argument patterns."""
        # Arrange - Simulate CLI args structure
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Simulate CLI args for: ocli find --is-read --has-attachment --importance high
        cli_args = type('Args', (), {
            'is_read': True,
            'is_unread': False, 
            'has_attachment': True,
            'no_attachment': False,
            'importance': 'high',
            'not_sender': None,
            'not_subject': None,
            'sender': None,
            'subject': None,
            'folder': None,
            'since': None,
            'until': None
        })()
        
        # Act - Use enhanced search_emails as CLI would
        results = searcher.search_emails(
            sender=cli_args.sender,
            subject=cli_args.subject,
            folder_path=cli_args.folder,
            since=cli_args.since,
            until=cli_args.until,
            is_read=cli_args.is_read,
            is_unread=cli_args.is_unread,
            has_attachment=cli_args.has_attachment,
            no_attachment=cli_args.no_attachment,
            importance=cli_args.importance,
            not_sender=cli_args.not_sender,
            not_subject=cli_args.not_subject
        )
        
        # Assert - Should work like CLI integration
        assert isinstance(results, list)
        for email in results:
            assert email.is_read  # CLI --is-read filter
            assert email.has_attachments  # CLI --has-attachment filter  
            assert email.importance == "High"  # CLI --importance high filter


class TestEmailSearcherPerformance:
    """Test performance of filtering operations with larger datasets."""
    
    def test_filtering_performance_with_large_dataset(self):
        """Test that filtering operations complete quickly with 1000+ emails."""
        import time
        from datetime import timedelta
        
        # Arrange - Create a large dataset  
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get base emails and replicate them to create larger dataset
        base_emails = adapter.get_emails("Inbox")
        
        # Create 1000 synthetic emails with varied properties
        large_email_set = []
        for i in range(1000):
            base_email = base_emails[i % len(base_emails)]
            # Create variations
            email_copy = type(base_email)(
                id=f"synthetic-{i}",
                subject=f"{base_email.subject} #{i}",
                sender_email=base_email.sender_email,
                sender_name=base_email.sender_name,
                recipient_emails=base_email.recipient_emails,
                received_date=base_email.received_date + timedelta(hours=i),
                body_text=base_email.body_text,
                folder_path=base_email.folder_path,
                has_attachments=(i % 3 == 0),  # Every 3rd email has attachments
                is_read=(i % 2 == 0),  # Every other email is read
                importance=["High", "Normal", "Low"][i % 3],  # Cycle importance
                attachment_count=2 if (i % 3 == 0) else 0
            )
            large_email_set.append(email_copy)
        
        # Act & Assert - Test each filter type for performance
        start_time = time.time()
        
        # Test read status filtering
        read_results = searcher.filter_by_read_status(large_email_set, is_read=True)
        read_time = time.time() - start_time
        
        # Test attachment filtering
        start_time = time.time()
        attachment_results = searcher.filter_by_attachments(large_email_set, has_attachment=True)
        attachment_time = time.time() - start_time
        
        # Test importance filtering
        start_time = time.time()
        importance_results = searcher.filter_by_importance(large_email_set, importance="high")
        importance_time = time.time() - start_time
        
        # Test exclusion filtering
        start_time = time.time()
        exclusion_results = searcher.filter_by_exclusions(large_email_set, not_subject="999")
        exclusion_time = time.time() - start_time
        
        # Assert performance requirements (< 1 second per operation)
        assert read_time < 1.0, f"Read status filtering took {read_time:.3f}s, should be < 1.0s"
        assert attachment_time < 1.0, f"Attachment filtering took {attachment_time:.3f}s, should be < 1.0s"
        assert importance_time < 1.0, f"Importance filtering took {importance_time:.3f}s, should be < 1.0s"
        assert exclusion_time < 1.0, f"Exclusion filtering took {exclusion_time:.3f}s, should be < 1.0s"
        
        # Assert functional correctness
        assert len(read_results) == 500  # Half should be read
        assert len(attachment_results) == 334  # Every 3rd (~333) has attachments
        assert len(importance_results) == 334  # Every 3rd has high importance
        assert len(exclusion_results) == 999  # All except one with "999" in subject
        
        print(f"Performance test passed:")
        print(f"  Read status filtering: {read_time:.3f}s")
        print(f"  Attachment filtering: {attachment_time:.3f}s") 
        print(f"  Importance filtering: {importance_time:.3f}s")
        print(f"  Exclusion filtering: {exclusion_time:.3f}s")