"""Tests for Paginator service."""

import pytest
from typing import List
from datetime import datetime, timezone, timedelta
from outlook_cli.services.paginator import Paginator
from outlook_cli.models.email import Email


class TestPaginator:
    """Test Paginator service functionality."""
    
    def _create_test_emails(self, count: int) -> List[Email]:
        """Create test emails for pagination testing."""
        emails = []
        for i in range(count):
            email = Email(
                id=f"email-{i:03d}",
                subject=f"Test Email {i+1}",
                sender_email=f"sender{i}@test.com",
                sender_name=f"Sender {i+1}",
                recipient_emails=["user@test.com"],
                received_date=datetime.now(timezone.utc) - timedelta(hours=i),
                body_text=f"This is test email number {i+1}",
                folder_path="Inbox",
                has_attachments=False,
                is_read=False
            )
            emails.append(email)
        return emails
    
    def test_paginator_creation_with_25_emails_creates_3_pages(self):
        """Test that Paginator with 25 emails creates 3 pages."""
        # Arrange
        emails = self._create_test_emails(25)
        
        # Act
        paginator = Paginator(emails)
        page_info = paginator.get_page_info()
        
        # Assert
        assert page_info["total_pages"] == 3
        assert page_info["total_items"] == 25
        assert page_info["current_page"] == 1
        assert page_info["items_per_page"] == 10
    
    def test_get_current_page_returns_first_10_emails(self):
        """Test that get_current_page returns first 10 emails."""
        # Arrange
        emails = self._create_test_emails(25)
        paginator = Paginator(emails)
        
        # Act
        current_page = paginator.get_current_page()
        
        # Assert
        assert len(current_page) == 10
        assert current_page[0].id == "email-000"
        assert current_page[9].id == "email-009"
        assert all(isinstance(email, Email) for email in current_page)
    
    def test_next_page_moves_to_page_2_returns_emails_11_to_20(self):
        """Test that next_page moves to page 2 and returns emails 11-20."""
        # Arrange
        emails = self._create_test_emails(25)
        paginator = Paginator(emails)
        
        # Act
        success = paginator.next_page()
        current_page = paginator.get_current_page()
        page_info = paginator.get_page_info()
        
        # Assert
        assert success is True
        assert page_info["current_page"] == 2
        assert len(current_page) == 10
        assert current_page[0].id == "email-010"
        assert current_page[9].id == "email-019"
    
    def test_prev_page_from_page_2_returns_to_page_1(self):
        """Test that prev_page from page 2 returns to page 1."""
        # Arrange
        emails = self._create_test_emails(25)
        paginator = Paginator(emails)
        paginator.next_page()  # Move to page 2
        
        # Act
        success = paginator.prev_page()
        current_page = paginator.get_current_page()
        page_info = paginator.get_page_info()
        
        # Assert
        assert success is True
        assert page_info["current_page"] == 1
        assert len(current_page) == 10
        assert current_page[0].id == "email-000"
        assert current_page[9].id == "email-009"
    
    def test_next_page_from_last_page_does_nothing(self):
        """Test that next_page from last page does nothing."""
        # Arrange
        emails = self._create_test_emails(25)
        paginator = Paginator(emails)
        paginator.next_page()  # Page 2
        paginator.next_page()  # Page 3 (last page)
        
        # Act
        success = paginator.next_page()  # Should fail
        page_info = paginator.get_page_info()
        
        # Assert
        assert success is False
        assert page_info["current_page"] == 3  # Still on page 3
    
    def test_prev_page_from_first_page_does_nothing(self):
        """Test that prev_page from first page does nothing."""
        # Arrange
        emails = self._create_test_emails(25)
        paginator = Paginator(emails)
        
        # Act
        success = paginator.prev_page()  # Should fail
        page_info = paginator.get_page_info()
        
        # Assert
        assert success is False
        assert page_info["current_page"] == 1  # Still on page 1
    
    def test_empty_list_handling(self):
        """Test that empty list is handled correctly."""
        # Arrange
        emails = []
        
        # Act
        paginator = Paginator(emails)
        page_info = paginator.get_page_info()
        current_page = paginator.get_current_page()
        
        # Assert
        assert page_info["total_pages"] == 0
        assert page_info["total_items"] == 0
        assert page_info["current_page"] == 0
        assert current_page == []
    
    def test_single_page_with_10_or_fewer_items(self):
        """Test that list with 10 or fewer items creates single page."""
        # Arrange
        emails = self._create_test_emails(7)
        
        # Act
        paginator = Paginator(emails)
        page_info = paginator.get_page_info()
        current_page = paginator.get_current_page()
        
        # Assert
        assert page_info["total_pages"] == 1
        assert page_info["total_items"] == 7
        assert page_info["current_page"] == 1
        assert len(current_page) == 7
        assert current_page[0].id == "email-000"
        assert current_page[6].id == "email-006"


class TestPaginatorIntegration:
    """Integration tests for Paginator with other services."""
    
    def test_paginator_integration_with_email_reader(self):
        """Test that Paginator works with EmailReader results."""
        # Arrange
        from outlook_cli.services.email_reader import EmailReader
        from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
        
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Act
        emails = reader.get_emails_from_folder("Inbox")
        paginator = Paginator(emails)
        
        # Assert
        page_info = paginator.get_page_info()
        assert page_info["total_items"] == 3  # MockAdapter has 3 inbox emails
        assert page_info["total_pages"] == 1  # 3 emails = 1 page
        assert page_info["current_page"] == 1
        
        current_page = paginator.get_current_page()
        assert len(current_page) == 3
        assert current_page[0].subject == "Weekly Team Meeting"
    
    def test_paginator_integration_with_email_searcher(self):
        """Test that Paginator works with EmailSearcher results."""
        # Arrange
        from outlook_cli.services.email_searcher import EmailSearcher
        from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
        
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Act
        search_results = searcher.search_emails(sender="manager@company.com")
        paginator = Paginator(search_results)
        
        # Assert
        page_info = paginator.get_page_info()
        assert page_info["total_items"] == 1  # Only one email from manager
        assert page_info["total_pages"] == 1
        assert page_info["current_page"] == 1
        
        current_page = paginator.get_current_page()
        assert len(current_page) == 1
        assert current_page[0].sender_email == "manager@company.com"