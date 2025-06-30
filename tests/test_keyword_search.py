"""Tests for keyword search functionality (TDD approach)."""

import io
from unittest.mock import patch, MagicMock
from datetime import datetime
from outlook_cli.cli import main
from outlook_cli.models.email import Email


class TestKeywordSearch:
    """Test suite for --keyword search functionality."""
    
    def test_keyword_search_finds_emails_with_keyword_in_subject(self):
        """Test that --keyword finds emails when keyword is in subject."""
        # Create test emails - one with keyword in subject, one without
        test_emails_subject = [
            Email(
                id="test-id-1",
                subject="Meeting notes for project",
                sender_email="alice@example.com",
                sender_name="Alice Smith",
                recipient_emails=["user@example.com"],
                received_date=datetime.now(),
                body_text="Test body",
                has_attachments=False,
                folder_path="Inbox",
            )
        ]
        
        test_emails_sender = []  # No matches in sender for this test
        
        # Mock the services used by find command
        mock_adapter = MagicMock()
        mock_searcher = MagicMock()
        
        with patch('outlook_cli.cli._create_adapter', return_value=mock_adapter), \
             patch('outlook_cli.cli.EmailSearcher', return_value=mock_searcher), \
             patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
             patch('sys.argv', ['ocli', 'find', '--keyword', 'notes']):
            
            # Mock FilterParsingService 
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
            
            # Setup the searcher to return our test data based on search_emails calls
            def mock_search_emails(**kwargs):
                if 'subject' in kwargs and kwargs['subject'] == 'notes':
                    return test_emails_subject
                elif 'sender' in kwargs and kwargs['sender'] == 'notes':
                    return test_emails_sender
                return []
            
            mock_searcher.search_emails.side_effect = mock_search_emails
            
            main()
            
            output = mock_stdout.getvalue()
            
            # Verify the keyword search was called correctly with new method
            assert mock_searcher.search_emails.call_count == 2  # One for sender, one for subject
            
            # Verify the correct parameters were passed
            calls = mock_searcher.search_emails.call_args_list
            sender_call = calls[0]
            subject_call = calls[1]
            
            # First call should be for sender search
            assert sender_call.kwargs['sender'] == 'notes'
            assert sender_call.kwargs['folder'] == 'Inbox'
            
            # Second call should be for subject search
            assert subject_call.kwargs['subject'] == 'notes'
            assert subject_call.kwargs['folder'] == 'Inbox'
            
            # Verify output shows the found email
            assert "Meeting notes for project" in output
            assert "Page 1 of 1, showing 1-1 of 1" in output

    def test_keyword_search_finds_emails_with_keyword_in_sender(self):
        """Test that --keyword finds emails when keyword is in sender."""
        # Create test emails - one with keyword in sender name, none in subject
        test_emails_subject = []  # No matches in subject for this test
        test_emails_sender = [
            Email(
                id="test-id-2", 
                subject="Project update",
                sender_email="john.notes@example.com",
                sender_name="John Notes",
                recipient_emails=["user@example.com"],
                received_date=datetime.now(),
                body_text="Test body",
                has_attachments=False,
                folder_path="Inbox",
            )
        ]
        
        # Mock the services used by find command
        mock_adapter = MagicMock()
        mock_searcher = MagicMock()
        
        with patch('outlook_cli.cli._create_adapter', return_value=mock_adapter), \
             patch('outlook_cli.cli.EmailSearcher', return_value=mock_searcher), \
             patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
             patch('sys.argv', ['ocli', 'find', '--keyword', 'notes']):
            
            # Mock FilterParsingService 
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
            
            # Setup the searcher to return our test data based on search_emails calls
            def mock_search_emails(**kwargs):
                if 'subject' in kwargs and kwargs['subject'] == 'notes':
                    return test_emails_subject
                elif 'sender' in kwargs and kwargs['sender'] == 'notes':
                    return test_emails_sender
                return []
            
            mock_searcher.search_emails.side_effect = mock_search_emails
            
            main()
            
            output = mock_stdout.getvalue()
            
            # Verify the keyword search was called correctly with new method
            assert mock_searcher.search_emails.call_count == 2  # One for sender, one for subject
            
            # Verify output shows the found email
            assert "John Notes" in output
            assert "Project update" in output

    def test_keyword_search_combines_results_and_removes_duplicates(self):
        """Test that --keyword combines subject and sender results, removing duplicates."""
        # Create the same email that would be found by both searches
        duplicate_email = Email(
            id="duplicate-id",
            subject="Meeting notes discussion", 
            sender_email="notes.keeper@example.com",
            sender_name="Notes Keeper",
            recipient_emails=["user@example.com"],
            received_date=datetime.now(),
            body_text="Test body",
            has_attachments=False,
            folder_path="Inbox",
        )
        
        # Both searches return the same email (simulating duplicate)
        test_emails_subject = [duplicate_email]
        test_emails_sender = [duplicate_email]
        
        # Mock the services used by find command
        mock_adapter = MagicMock()
        mock_searcher = MagicMock()
        
        with patch('outlook_cli.cli._create_adapter', return_value=mock_adapter), \
             patch('outlook_cli.cli.EmailSearcher', return_value=mock_searcher), \
             patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
             patch('sys.argv', ['ocli', 'find', '--keyword', 'notes']):
            
            # Mock FilterParsingService 
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
            
            # Setup the searcher to return our test data based on search_emails calls (same email from both)
            def mock_search_emails(**kwargs):
                if 'subject' in kwargs and kwargs['subject'] == 'notes':
                    return test_emails_subject
                elif 'sender' in kwargs and kwargs['sender'] == 'notes':
                    return test_emails_sender
                return []
            
            mock_searcher.search_emails.side_effect = mock_search_emails
            
            main()
            
            output = mock_stdout.getvalue()
            
            # Verify output shows only one result (duplicate removed)
            assert "Page 1 of 1, showing 1-1 of 1" in output
            assert "Meeting notes discussion" in output
            
            # Count occurrences of the email ID to ensure no duplicates in display
            id_count = output.count("duplicate-id")
            assert id_count == 1, f"Email ID should appear only once, but appeared {id_count} times"

    def test_keyword_search_shows_correct_search_summary(self):
        """Test that keyword search displays the correct search summary."""
        mock_adapter = MagicMock()
        mock_searcher = MagicMock()
        
        with patch('outlook_cli.cli._create_adapter', return_value=mock_adapter), \
             patch('outlook_cli.cli.EmailSearcher', return_value=mock_searcher), \
             patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
             patch('sys.argv', ['ocli', 'find', '--keyword', 'meeting']):
            
            # Mock FilterParsingService 
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
            
            # Setup empty results for this test (focusing on search summary)
            mock_searcher.search_emails.return_value = []
            
            main()
            
            output = mock_stdout.getvalue()
            
            # Verify search summary shows keyword search description
            assert "Searching for emails with keyword 'meeting' in subject and sender in folder 'Inbox'" in output

    def test_keyword_search_requires_keyword_argument(self):
        """Test that find command requires at least one search criteria."""
        mock_adapter = MagicMock()
        
        with patch('outlook_cli.cli._create_adapter', return_value=mock_adapter), \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
             patch('sys.argv', ['ocli', 'find']):  # No search criteria
            
            main()
            
            output = mock_stdout.getvalue()
            
            # Verify error message for missing search criteria
            assert "Error: Please specify at least one search criteria (--keyword, --sender, --subject, date filters, or other filters)" in output