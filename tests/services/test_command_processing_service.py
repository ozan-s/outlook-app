"""Tests for CommandProcessingService."""

import pytest
from unittest.mock import Mock, patch
from src.outlook_cli.services.command_processing_service import CommandProcessingService


class TestCommandProcessingService:
    """Test CommandProcessingService common command patterns."""
    
    def setup_method(self):
        """Set up test instance."""
        self.adapter_factory = Mock()
        self.service = CommandProcessingService(self.adapter_factory)
    
    @patch('src.outlook_cli.services.command_processing_service.EmailSearcher')
    @patch('src.outlook_cli.services.command_processing_service.EmailSortingService')
    @patch('src.outlook_cli.services.command_processing_service.Paginator')
    def test_process_email_command_with_sorting_and_pagination(self, mock_paginator, mock_sorting_service, mock_searcher):
        """Test the common email command processing pattern with sorting."""
        # Arrange
        args = Mock()
        args.sort_by = "date"
        args.sort_order = "desc"
        args.adapter = None  # Explicitly set adapter to None
        
        search_params = {
            'folder_path': 'Inbox',
            'is_read': True
        }
        
        # Mock the email searcher
        mock_adapter = Mock()
        self.adapter_factory.create_adapter.return_value = mock_adapter
        mock_searcher_instance = Mock()
        mock_searcher.return_value = mock_searcher_instance
        mock_emails = [Mock(), Mock(), Mock()]  # 3 mock emails
        mock_searcher_instance.search_emails.return_value = mock_emails
        
        # Mock the sorting service
        mock_sorting_instance = Mock()
        mock_sorting_service.return_value = mock_sorting_instance
        mock_sorted_emails = [Mock(), Mock(), Mock()]
        mock_sorting_instance.sort_emails.return_value = mock_sorted_emails
        
        # Mock the paginator
        mock_paginator_instance = Mock()
        mock_paginator.return_value = mock_paginator_instance
        mock_current_page = Mock()
        mock_paginator_instance.get_current_page.return_value = mock_current_page
        
        # Act
        result = self.service.process_email_command(args, search_params, "test operation")
        
        # Assert
        # Verify adapter creation (should extract adapter type from args)
        self.adapter_factory.create_adapter.assert_called_once_with(None)  # args.adapter defaults to None
        
        # Verify EmailSearcher usage
        mock_searcher.assert_called_once_with(mock_adapter)
        mock_searcher_instance.search_emails.assert_called_once_with(**search_params)
        
        # Verify sorting
        mock_sorting_service.assert_called_once()
        mock_sorting_instance.sort_emails.assert_called_once_with(mock_emails, "date", "desc")
        
        # Verify pagination
        mock_paginator.assert_called_once_with(mock_sorted_emails, page_size=10)
        mock_paginator_instance.get_current_page.assert_called_once()
        
        # Result should contain paginator and current page
        assert result['paginator'] == mock_paginator_instance
        assert result['current_page'] == mock_current_page
        assert result['emails'] == mock_sorted_emails
    
    @patch('src.outlook_cli.services.command_processing_service.EmailSearcher')
    @patch('src.outlook_cli.services.command_processing_service.Paginator')
    def test_process_email_command_without_sorting(self, mock_paginator, mock_searcher):
        """Test email command processing without sorting."""
        # Arrange
        args = Mock()
        args.sort_by = None
        args.adapter = None  # Explicitly set adapter to None
        
        search_params = {'folder_path': 'Inbox'}
        
        # Mock the email searcher
        mock_adapter = Mock()
        self.adapter_factory.create_adapter.return_value = mock_adapter
        mock_searcher_instance = Mock()
        mock_searcher.return_value = mock_searcher_instance
        mock_emails = [Mock(), Mock()]  # 2 mock emails
        mock_searcher_instance.search_emails.return_value = mock_emails
        
        # Mock the paginator
        mock_paginator_instance = Mock()
        mock_paginator.return_value = mock_paginator_instance
        mock_current_page = Mock()
        mock_paginator_instance.get_current_page.return_value = mock_current_page
        
        # Act
        result = self.service.process_email_command(args, search_params, "test operation")
        
        # Assert
        # Should not attempt sorting
        assert result['emails'] == mock_emails  # Original unsorted emails
        
        # Should still paginate
        mock_paginator.assert_called_once_with(mock_emails, page_size=10)
        assert result['paginator'] == mock_paginator_instance
        assert result['current_page'] == mock_current_page
    
    @patch('src.outlook_cli.services.command_processing_service.EmailSearcher')
    def test_process_email_command_with_empty_results(self, mock_searcher):
        """Test handling of empty search results."""
        # Arrange
        args = Mock()
        args.sort_by = None
        args.adapter = None  # Explicitly set adapter to None
        
        search_params = {'folder_path': 'Empty'}
        
        # Mock the email searcher to return empty list
        mock_adapter = Mock()
        self.adapter_factory.create_adapter.return_value = mock_adapter
        mock_searcher_instance = Mock()
        mock_searcher.return_value = mock_searcher_instance
        mock_searcher_instance.search_emails.return_value = []
        
        # Act
        result = self.service.process_email_command(args, search_params, "test operation")
        
        # Assert
        assert result['emails'] == []
        assert result['paginator'] is None
        assert result['current_page'] is None
    
    @patch('src.outlook_cli.services.command_processing_service.EmailSearcher')
    def test_process_email_command_handles_exceptions(self, mock_searcher):
        """Test that exceptions are properly handled and re-raised."""
        # Arrange
        args = Mock()
        args.adapter = None  # Explicitly set adapter to None
        search_params = {'folder_path': 'Inbox'}
        
        # Mock adapter creation to raise exception
        self.adapter_factory.create_adapter.side_effect = Exception("Adapter creation failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Adapter creation failed"):
            self.service.process_email_command(args, search_params, "test operation")