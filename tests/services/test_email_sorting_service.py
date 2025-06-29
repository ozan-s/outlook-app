"""Tests for EmailSortingService."""

from typing import List
from datetime import datetime, timezone, timedelta
from outlook_cli.services.email_sorting_service import EmailSortingService
from outlook_cli.models.email import Email


class TestEmailSortingService:
    """Test EmailSortingService functionality."""
    
    def _create_test_emails(self) -> List[Email]:
        """Create test emails with different field values for sorting."""
        now = datetime.now(timezone.utc)
        
        emails = [
            Email(
                id="email-001",
                subject="Beta Project Update",
                sender_email="charlie@company.com",  # Changed to make unsorted order different
                sender_name="Charlie Brown",
                recipient_emails=["user@test.com"],
                received_date=now - timedelta(hours=2),  # 2 hours ago
                body_text="Beta project status update",
                folder_path="Inbox",
                has_attachments=False,
                is_read=False,
                importance="Normal"
            ),
            Email(
                id="email-002", 
                subject="Alpha Release Notes",
                sender_email="alice@company.com",  # Changed to make unsorted order different
                sender_name="Alice Johnson",
                recipient_emails=["user@test.com"],
                received_date=now - timedelta(hours=1),  # 1 hour ago (most recent)
                body_text="Alpha release documentation",
                folder_path="Inbox",
                has_attachments=True,
                is_read=True,
                importance="High"
            ),
            Email(
                id="email-003",
                subject="Gamma Testing Results", 
                sender_email="bob@company.com",  # Changed to make unsorted order different
                sender_name="Bob Smith",
                recipient_emails=["user@test.com"],
                received_date=now - timedelta(hours=3),  # 3 hours ago (oldest)
                body_text="Gamma testing completed",
                folder_path="Inbox",
                has_attachments=False,
                is_read=True,
                importance="Low"
            )
        ]
        return emails
    
    def test_sort_by_received_date_descending_default(self):
        """Test that EmailSortingService sorts by received_date in descending order by default."""
        # Arrange
        emails = self._create_test_emails()
        sorter = EmailSortingService()
        
        # Act
        sorted_emails = sorter.sort_emails(emails, "received_date", "desc")
        
        # Assert
        assert len(sorted_emails) == 3
        assert sorted_emails[0].id == "email-002"  # Most recent (1 hour ago)
        assert sorted_emails[1].id == "email-001"  # 2 hours ago
        assert sorted_emails[2].id == "email-003"  # Oldest (3 hours ago)
    
    def test_sort_by_subject_ascending(self):
        """Test that EmailSortingService sorts by subject in ascending order."""
        # Arrange
        emails = self._create_test_emails()
        sorter = EmailSortingService()
        
        # Act
        sorted_emails = sorter.sort_emails(emails, "subject", "asc")
        
        # Assert
        assert len(sorted_emails) == 3
        assert sorted_emails[0].subject == "Alpha Release Notes"  # First alphabetically
        assert sorted_emails[1].subject == "Beta Project Update"  # Second alphabetically
        assert sorted_emails[2].subject == "Gamma Testing Results"  # Last alphabetically
    
    def test_sort_by_sender_ascending(self):
        """Test that EmailSortingService sorts by sender_email in ascending order."""
        # Arrange
        emails = self._create_test_emails()
        sorter = EmailSortingService()
        
        # Act
        sorted_emails = sorter.sort_emails(emails, "sender", "asc")
        
        # Assert
        assert len(sorted_emails) == 3
        assert sorted_emails[0].sender_email == "alice@company.com"  # First alphabetically
        assert sorted_emails[1].sender_email == "bob@company.com"    # Second alphabetically  
        assert sorted_emails[2].sender_email == "charlie@company.com"  # Last alphabetically
    
    def test_sort_by_importance_descending(self):
        """Test that EmailSortingService sorts by importance (High→Normal→Low)."""
        # Arrange
        emails = self._create_test_emails()
        sorter = EmailSortingService()
        
        # Act
        sorted_emails = sorter.sort_emails(emails, "importance", "desc")
        
        # Assert
        assert len(sorted_emails) == 3
        assert sorted_emails[0].importance == "High"    # email-002 (Alice)
        assert sorted_emails[1].importance == "Normal"  # email-001 (Charlie)
        assert sorted_emails[2].importance == "Low"     # email-003 (Bob)