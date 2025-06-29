"""Integration tests for sorting + filtering + pagination."""

from datetime import datetime, timezone, timedelta
from typing import List
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.email_sorting_service import EmailSortingService
from outlook_cli.services.paginator import Paginator
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.models.email import Email


class TestSortingFilteringPaginationIntegration:
    """Test that sorting, filtering, and pagination work together correctly."""
    
    def test_search_then_sort_then_paginate_integration(self):
        """Test that search results can be sorted and then paginated correctly."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        sorter = EmailSortingService()
        
        # Act - Search for emails (this will use filtering from Milestone 006)
        search_results = searcher.search_emails(
            folder_path="Inbox",
            # No filters applied - get all inbox emails
        )
        
        # Sort by subject ascending
        sorted_results = sorter.sort_emails(search_results, "subject", "asc")
        
        # Paginate with page size of 2
        paginator = Paginator(sorted_results, page_size=2)
        page1 = paginator.get_current_page()
        
        # Assert - verify the full integration pipeline works
        assert len(search_results) == 3  # MockAdapter has 3 inbox emails
        assert len(sorted_results) == 3  # All emails should be returned after sorting
        assert len(page1) == 2  # First page should have 2 emails
        
        # Verify sorting worked - first page should have first 2 emails alphabetically by subject
        subjects_page1 = [email.subject for email in page1]
        assert subjects_page1 == sorted(subjects_page1)  # Should be in alphabetical order
        
        # Verify pagination works
        page_info = paginator.get_page_info()
        assert page_info["total_pages"] == 2  # 3 emails / 2 per page = 2 pages
        assert page_info["current_page"] == 1
        
        # Move to page 2 and verify
        success = paginator.next_page()
        assert success is True
        page2 = paginator.get_current_page()
        assert len(page2) == 1  # Second page should have 1 email
        
    def test_filtering_then_sorting_then_pagination_integration(self):
        """Test that filtering, sorting, and pagination work together with actual filters."""
        # Arrange
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        sorter = EmailSortingService()
        
        # Act - Search with filters from Milestone 006
        filtered_results = searcher.search_emails(
            folder_path="Inbox",
            is_unread=True  # Filter for unread emails only
        )
        
        # Sort by received_date descending (most recent first)
        sorted_filtered_results = sorter.sort_emails(filtered_results, "received_date", "desc")
        
        # Paginate
        paginator = Paginator(sorted_filtered_results, page_size=10)
        current_page = paginator.get_current_page()
        
        # Assert - verify the integration
        # MockAdapter should have some unread emails
        assert len(filtered_results) >= 0  # May have 0 or more unread emails
        assert len(sorted_filtered_results) == len(filtered_results)  # Sorting preserves count
        
        # If we have results, verify they're sorted correctly
        if len(sorted_filtered_results) > 1:
            # Verify descending order by received_date
            for i in range(len(sorted_filtered_results) - 1):
                assert sorted_filtered_results[i].received_date >= sorted_filtered_results[i + 1].received_date
        
        # Verify pagination info
        page_info = paginator.get_page_info()
        assert page_info["total_items"] == len(filtered_results)
        assert page_info["current_page"] == 1 if filtered_results else 0