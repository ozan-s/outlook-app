"""Test CLI date integration functionality."""
import pytest
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from outlook_cli.cli import main, handle_find
from outlook_cli.models.email import Email


class TestCLIDateIntegration:
    """Test CLI date argument processing and integration."""

    def test_handle_find_processes_relative_dates(self):
        """Test that handle_find processes relative date arguments."""
        # Create mock arguments
        mock_args = MagicMock()
        mock_args.keyword = "test"
        mock_args.sender = None
        mock_args.subject = None
        mock_args.folder = "Inbox"
        mock_args.since = "7d"  # 7 days ago
        mock_args.until = "2d"  # 2 days ago
        
        # Mock the adapter and searcher
        with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search_emails.return_value = []
                
                with patch('outlook_cli.cli.Paginator'):
                    # Call handle_find
                    handle_find(mock_args)
                    
                    # Verify EmailSearcher was created
                    mock_searcher_class.assert_called_once_with(mock_adapter)
                    
                    # Verify search_emails was called twice (for keyword search: sender and subject)
                    assert mock_searcher.search_emails.call_count == 2
                    
                    # Check calls contain datetime objects for relative dates
                    calls = mock_searcher.search_emails.call_args_list
                    assert any('sender' in str(call) for call in calls)
                    assert any('subject' in str(call) for call in calls)

    def test_handle_find_processes_absolute_dates(self):
        """Test that handle_find processes absolute date arguments."""
        # Create mock arguments
        mock_args = MagicMock()
        mock_args.keyword = None
        mock_args.sender = "test@example.com"
        mock_args.subject = None
        mock_args.folder = "Inbox"
        mock_args.since = "2025-06-01"
        mock_args.until = "2025-06-30"
        
        # Mock the adapter and searcher
        with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search_emails.return_value = []
                
                with patch('outlook_cli.cli.Paginator'):
                    # Call handle_find
                    handle_find(mock_args)
                    
                    # Verify search_emails was called with parsed dates
                    mock_searcher.search_emails.assert_called_once()
                    call_args = mock_searcher.search_emails.call_args
                    
                    # Should have been called with sender and datetime objects
                    assert call_args[1]['sender'] == "test@example.com"
                    assert call_args[1]['folder_path'] == "Inbox"
                    assert isinstance(call_args[1]['since'], datetime)
                    assert isinstance(call_args[1]['until'], datetime)

    def test_handle_find_shows_error_for_invalid_date(self):
        """Test that handle_find shows user-friendly error for invalid dates."""
        # Create mock arguments with invalid date
        mock_args = MagicMock()
        mock_args.keyword = "test"
        mock_args.sender = None
        mock_args.subject = None
        mock_args.folder = "Inbox"
        mock_args.since = "invalid_date"
        mock_args.until = None
        
        # Mock the adapter
        with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher'):
                with patch('builtins.print') as mock_print:
                    # Call handle_find - should handle ValueError gracefully
                    handle_find(mock_args)
                    
                    # Should print error message
                    mock_print.assert_called()
                    error_message = str(mock_print.call_args[0][0])
                    assert "Error" in error_message
                    assert "date" in error_message.lower()

    def test_handle_find_shows_error_for_invalid_date_range(self):
        """Test that handle_find shows error when since > until."""
        # Create mock arguments with invalid date range
        mock_args = MagicMock()
        mock_args.keyword = "test"
        mock_args.sender = None
        mock_args.subject = None
        mock_args.folder = "Inbox"
        mock_args.since = "2025-06-30"  # After until date
        mock_args.until = "2025-06-01"  # Before since date
        
        # Mock the adapter
        with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher'):
                with patch('builtins.print') as mock_print:
                    # Call handle_find - should handle ValueError gracefully
                    handle_find(mock_args)
                    
                    # Should print error message
                    mock_print.assert_called()
                    error_message = str(mock_print.call_args[0][0])
                    assert "Error" in error_message
                    assert "range" in error_message.lower()

    def test_handle_find_works_without_date_arguments(self):
        """Test that handle_find still works when no date arguments provided."""
        # Create mock arguments without dates
        mock_args = MagicMock()
        mock_args.keyword = "test"
        mock_args.sender = None
        mock_args.subject = None
        mock_args.folder = "Inbox"
        mock_args.since = None
        mock_args.until = None
        
        # Mock the adapter and searcher
        with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search_emails.return_value = []
                
                with patch('outlook_cli.cli.Paginator'):
                    # Call handle_find - should work normally
                    handle_find(mock_args)
                    
                    # Verify search_emails was called twice (keyword search: sender and subject)
                    assert mock_searcher.search_emails.call_count == 2
                    
                    # Check that since and until parameters are None
                    calls = mock_searcher.search_emails.call_args_list
                    for call in calls:
                        assert call[1]['since'] is None
                        assert call[1]['until'] is None