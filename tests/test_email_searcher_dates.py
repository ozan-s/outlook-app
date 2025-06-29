"""Test EmailSearcher date filtering functionality."""
from datetime import datetime, timezone, timedelta
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.models.email import Email


class TestEmailSearcherDates:
    """Test EmailSearcher date filtering functionality."""

    def setup_method(self):
        """Set up test data with known dates."""
        self.adapter = MockOutlookAdapter()
        self.searcher = EmailSearcher(self.adapter)
        
        # Create test emails with specific dates
        self.base_date = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        
        # Email from 7 days ago
        self.email_7d_ago = Email(
            id="email_7d",
            subject="Email from 7 days ago",
            sender_email="sender1@example.com",
            sender_name="Sender One",
            recipient_emails=["user@example.com"],
            received_date=self.base_date - timedelta(days=7),
            body_text="Test email content",
            has_attachments=False,
            folder_path="Inbox"
        )
        
        # Email from 3 days ago
        self.email_3d_ago = Email(
            id="email_3d",
            subject="Email from 3 days ago",
            sender_email="sender2@example.com", 
            sender_name="Sender Two",
            recipient_emails=["user@example.com"],
            received_date=self.base_date - timedelta(days=3),
            body_text="Test email content",
            has_attachments=False,
            folder_path="Inbox"
        )
        
        # Email from 1 day ago
        self.email_1d_ago = Email(
            id="email_1d",
            subject="Email from 1 day ago",
            sender_email="sender3@example.com",
            sender_name="Sender Three", 
            recipient_emails=["user@example.com"],
            received_date=self.base_date - timedelta(days=1),
            body_text="Test email content",
            has_attachments=False,
            folder_path="Inbox"
        )

    def test_search_emails_with_since_date(self):
        """Test searching emails with since date filter."""
        # Mock the adapter to return our test emails
        self.adapter._emails = {
            "Inbox": [self.email_7d_ago, self.email_3d_ago, self.email_1d_ago]
        }
        
        # Search for emails since 5 days ago
        since_date = self.base_date - timedelta(days=5)
        results = self.searcher.search_emails(since=since_date, folder_path="Inbox")
        
        # Should only return emails from 3 days and 1 day ago
        assert len(results) == 2
        assert self.email_3d_ago in results
        assert self.email_1d_ago in results
        assert self.email_7d_ago not in results

    def test_search_emails_with_until_date(self):
        """Test searching emails with until date filter."""
        # Mock the adapter to return our test emails
        self.adapter._emails = {
            "Inbox": [self.email_7d_ago, self.email_3d_ago, self.email_1d_ago]
        }
        
        # Search for emails until 2 days ago
        until_date = self.base_date - timedelta(days=2)
        results = self.searcher.search_emails(until=until_date, folder_path="Inbox")
        
        # Should only return emails from 7 days and 3 days ago
        assert len(results) == 2
        assert self.email_7d_ago in results
        assert self.email_3d_ago in results
        assert self.email_1d_ago not in results

    def test_search_emails_with_date_range(self):
        """Test searching emails with both since and until dates."""
        # Mock the adapter to return our test emails
        self.adapter._emails = {
            "Inbox": [self.email_7d_ago, self.email_3d_ago, self.email_1d_ago]
        }
        
        # Search for emails between 5 days ago and 2 days ago
        since_date = self.base_date - timedelta(days=5)
        until_date = self.base_date - timedelta(days=2)
        results = self.searcher.search_emails(since=since_date, until=until_date, folder_path="Inbox")
        
        # Should only return email from 3 days ago
        assert len(results) == 1
        assert self.email_3d_ago in results
        assert self.email_7d_ago not in results
        assert self.email_1d_ago not in results

    def test_search_emails_date_filters_with_other_criteria(self):
        """Test date filters combined with sender/subject criteria."""
        # Mock the adapter to return our test emails
        self.adapter._emails = {
            "Inbox": [self.email_7d_ago, self.email_3d_ago, self.email_1d_ago]
        }
        
        # Search for emails from sender2 since 5 days ago
        since_date = self.base_date - timedelta(days=5)
        results = self.searcher.search_emails(
            sender="sender2@example.com",
            since=since_date,
            folder_path="Inbox"
        )
        
        # Should only return email from sender2 that's within date range
        assert len(results) == 1
        assert self.email_3d_ago in results
        assert self.email_7d_ago not in results  # Wrong date range
        assert self.email_1d_ago not in results  # Wrong sender

    def test_search_emails_no_date_filters(self):
        """Test that search works normally when no date filters provided."""
        # Mock the adapter to return our test emails
        self.adapter._emails = {
            "Inbox": [self.email_7d_ago, self.email_3d_ago, self.email_1d_ago]
        }
        
        # Search without date filters
        results = self.searcher.search_emails(folder_path="Inbox")
        
        # Should return all emails
        assert len(results) == 3
        assert self.email_7d_ago in results
        assert self.email_3d_ago in results
        assert self.email_1d_ago in results