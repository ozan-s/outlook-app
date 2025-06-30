"""Tests for read command filtering functionality."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from io import StringIO
from outlook_cli import cli
from outlook_cli.models.email import Email


@pytest.fixture
def mock_emails():
    """Create mock emails for testing filtering."""
    emails = []
    
    # Email 1: Recent, unread, with attachment
    emails.append(Email(
        id='email1',
        subject='Recent Project Update',
        sender_name='Alice Smith',
        sender_email='alice@company.com',
        recipient_emails=['user@company.com'],
        cc_emails=[],
        bcc_emails=[],
        body_text='Project status update with attachment',
        body_html='<p>Project status update with attachment</p>',
        received_date=datetime(2025, 6, 28, 10, 0, tzinfo=timezone.utc),
        is_read=False,
        has_attachments=True,
        attachment_count=1,
        importance='Normal',
        folder_path='Inbox'
    ))
    
    # Email 2: Old, read, no attachment  
    emails.append(Email(
        id='email2',
        subject='Old Meeting Notes',
        sender_name='Bob Jones',
        sender_email='bob@company.com',
        recipient_emails=['user@company.com'],
        cc_emails=[],
        bcc_emails=[],
        body_text='Meeting notes from last month',
        body_html='<p>Meeting notes from last month</p>',
        received_date=datetime(2025, 6, 1, 14, 0, tzinfo=timezone.utc),
        is_read=True,
        has_attachments=False,
        attachment_count=0,
        importance='Low',
        folder_path='Inbox'
    ))
    
    # Email 3: Recent, read, with attachment
    emails.append(Email(
        id='email3',
        subject='Important Report',
        sender_name='Carol Davis',
        sender_email='carol@company.com',
        recipient_emails=['user@company.com'],
        cc_emails=[],
        bcc_emails=[],
        body_text='Quarterly report attached',
        body_html='<p>Quarterly report attached</p>',
        received_date=datetime(2025, 6, 27, 16, 0, tzinfo=timezone.utc),
        is_read=True,
        has_attachments=True,
        attachment_count=2,
        importance='High',
        folder_path='Inbox'
    ))
    
    return emails


def test_read_command_with_since_filter_should_filter_by_date(mock_emails):
    """Test that read command with --since filter returns only emails from last 7 days.
    
    This test validates the new service architecture with FilterParsingService + CommandProcessingService.
    """
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        # Mock FilterParsingService
        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class:
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            
            # Mock date parsing results
            from datetime import datetime, timezone
            since_date = datetime(2025, 6, 23, tzinfo=timezone.utc)  # 7 days ago
            mock_filter_service.parse_date_filters.return_value = (since_date, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox', 'since': since_date}
            
            # Mock AdapterFactory and CommandProcessingService
            with patch('outlook_cli.cli.AdapterFactory') as mock_adapter_factory_class:
                with patch('outlook_cli.cli.CommandProcessingService') as mock_command_service_class:
                    mock_adapter_factory = MagicMock()
                    mock_adapter_factory_class.return_value = mock_adapter_factory
                    
                    mock_command_service = MagicMock()
                    mock_command_service_class.return_value = mock_command_service
                    
                    # Only return emails from last 7 days (email1 and email3, not email2 from June 1)
                    recent_emails = [email for email in mock_emails if email.received_date.day >= 27]
                    
                    # Mock the result from CommandProcessingService
                    mock_paginator = MagicMock()
                    mock_paginator.get_current_page.return_value = recent_emails
                    mock_command_service.process_email_command.return_value = {
                        'emails': recent_emails,
                        'paginator': mock_paginator,
                        'current_page': recent_emails
                    }
                    
                    # Call handle_read with --since filter
                    args = type('Args', (), {
                        'folder': 'Inbox',
                        'since': '7d',
                        'until': None,
                        'is_read': None,
                        'is_unread': None,
                        'has_attachment': None,
                        'no_attachment': None,
                        'importance': None,
                        'not_sender': None,
                        'not_subject': None,
                        'sort_by': None,
                        'sort_order': 'desc'
                    })()
                    
                    cli.handle_read(args)
                    
                    # Verify the service interactions
                    mock_filter_service.parse_date_filters.assert_called_once_with(args)
                    mock_filter_service.build_search_params.assert_called_once_with(args, since_date, None)
                    mock_command_service.process_email_command.assert_called_once_with(
                        args, {'folder': 'Inbox', 'since': since_date}, "reading emails"
                    )


def test_read_command_with_is_unread_filter_should_filter_by_read_status(mock_emails):
    """Test that read command with --is-unread filter returns only unread emails."""
    with patch('sys.stdout', new_callable=StringIO):
        # Mock FilterParsingService
        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class:
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            
            # Mock filter parsing results
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox', 'is_unread': True}
            
            # Mock AdapterFactory and CommandProcessingService
            with patch('outlook_cli.cli.AdapterFactory') as mock_adapter_factory_class:
                with patch('outlook_cli.cli.CommandProcessingService') as mock_command_service_class:
                    mock_adapter_factory = MagicMock()
                    mock_adapter_factory_class.return_value = mock_adapter_factory
                    
                    mock_command_service = MagicMock()
                    mock_command_service_class.return_value = mock_command_service
                    
                    # Only return unread emails (just email1 which has is_read=False)
                    unread_emails = [email for email in mock_emails if not email.is_read]
                    
                    # Mock the result from CommandProcessingService
                    mock_paginator = MagicMock()
                    mock_command_service.process_email_command.return_value = {
                        'emails': unread_emails,
                        'paginator': mock_paginator,
                        'current_page': unread_emails
                    }
                    
                    args = type('Args', (), {
                        'folder': 'Inbox',
                        'since': None,
                        'until': None,
                        'is_read': None,
                        'is_unread': True,
                        'has_attachment': None,
                        'no_attachment': None,
                        'importance': None,
                        'not_sender': None,
                        'not_subject': None,
                        'sort_by': None,
                        'sort_order': 'desc'
                    })()
                    
                    cli.handle_read(args)
                    
                    # Verify the service interactions
                    mock_filter_service.parse_date_filters.assert_called_once_with(args)
                    mock_filter_service.build_search_params.assert_called_once_with(args, None, None)
                    mock_command_service.process_email_command.assert_called_once_with(
                        args, {'folder': 'Inbox', 'is_unread': True}, "reading emails"
                    )


def test_read_command_with_has_attachment_filter_should_filter_by_attachments(mock_emails):
    """Test that read command with --has-attachment filter returns only emails with attachments."""
    with patch('sys.stdout', new_callable=StringIO):
        # Mock FilterParsingService
        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class:
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            
            # Mock filter parsing results
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox', 'has_attachment': True}
            
            # Mock AdapterFactory and CommandProcessingService
            with patch('outlook_cli.cli.AdapterFactory') as mock_adapter_factory_class:
                with patch('outlook_cli.cli.CommandProcessingService') as mock_command_service_class:
                    mock_adapter_factory = MagicMock()
                    mock_adapter_factory_class.return_value = mock_adapter_factory
                    
                    mock_command_service = MagicMock()
                    mock_command_service_class.return_value = mock_command_service
                    
                    # Only return emails with attachments (email1 and email3)
                    attachment_emails = [email for email in mock_emails if email.has_attachments]
                    
                    # Mock the result from CommandProcessingService
                    mock_paginator = MagicMock()
                    mock_command_service.process_email_command.return_value = {
                        'emails': attachment_emails,
                        'paginator': mock_paginator,
                        'current_page': attachment_emails
                    }
                    
                    args = type('Args', (), {
                        'folder': 'Inbox',
                        'since': None,
                        'until': None,
                        'is_read': None,
                        'is_unread': None,
                        'has_attachment': True,
                        'no_attachment': None,
                        'importance': None,
                        'not_sender': None,
                        'not_subject': None,
                        'sort_by': None,
                        'sort_order': 'desc'
                    })()
                    
                    cli.handle_read(args)
                    
                    # Verify the service interactions
                    mock_filter_service.parse_date_filters.assert_called_once_with(args)
                    mock_filter_service.build_search_params.assert_called_once_with(args, None, None)
                    mock_command_service.process_email_command.assert_called_once_with(
                        args, {'folder': 'Inbox', 'has_attachment': True}, "reading emails"
                    )


def test_read_command_with_combined_filters_should_apply_all_filters(mock_emails):
    """Test that read command with multiple filters applies all filters correctly."""
    with patch('sys.stdout', new_callable=StringIO):
        # Mock FilterParsingService
        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class:
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            
            # Mock filter parsing results
            from datetime import datetime, timezone
            since_date = datetime(2025, 6, 23, tzinfo=timezone.utc)  # 7 days ago
            mock_filter_service.parse_date_filters.return_value = (since_date, None)
            mock_filter_service.build_search_params.return_value = {
                'folder': 'Inbox', 'since': since_date, 'is_unread': True
            }
            
            # Mock AdapterFactory and CommandProcessingService
            with patch('outlook_cli.cli.AdapterFactory') as mock_adapter_factory_class:
                with patch('outlook_cli.cli.CommandProcessingService') as mock_command_service_class:
                    mock_adapter_factory = MagicMock()
                    mock_adapter_factory_class.return_value = mock_adapter_factory
                    
                    mock_command_service = MagicMock()
                    mock_command_service_class.return_value = mock_command_service
                    
                    # Only return emails that are both recent AND unread (just email1)
                    filtered_emails = [
                        email for email in mock_emails 
                        if email.received_date.day >= 27 and not email.is_read
                    ]
                    
                    # Mock the result from CommandProcessingService
                    mock_paginator = MagicMock()
                    mock_command_service.process_email_command.return_value = {
                        'emails': filtered_emails,
                        'paginator': mock_paginator,
                        'current_page': filtered_emails
                    }
                    
                    args = type('Args', (), {
                        'folder': 'Inbox',
                        'since': '7d',
                        'until': None,
                        'is_read': None,
                        'is_unread': True,
                        'has_attachment': None,
                        'no_attachment': None,
                        'importance': None,
                        'not_sender': None,
                        'not_subject': None,
                        'sort_by': None,
                        'sort_order': 'desc'
                    })()
                    
                    cli.handle_read(args)
                    
                    # Verify the service interactions
                    mock_filter_service.parse_date_filters.assert_called_once_with(args)
                    mock_filter_service.build_search_params.assert_called_once_with(args, since_date, None)
                    mock_command_service.process_email_command.assert_called_once_with(
                        args, {'folder': 'Inbox', 'since': since_date, 'is_unread': True}, "reading emails"
                    )


def test_read_command_with_sorting_and_filtering_integration(mock_emails):
    """Test that read command applies both filtering and sorting correctly."""
    with patch('sys.stdout', new_callable=StringIO):
        # Mock FilterParsingService
        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_service_class:
            mock_filter_service = MagicMock()
            mock_filter_service_class.return_value = mock_filter_service
            
            # Mock filter parsing results
            mock_filter_service.parse_date_filters.return_value = (None, None)
            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox', 'has_attachment': True}
            
            # Mock AdapterFactory and CommandProcessingService
            with patch('outlook_cli.cli.AdapterFactory') as mock_adapter_factory_class:
                with patch('outlook_cli.cli.CommandProcessingService') as mock_command_service_class:
                    mock_adapter_factory = MagicMock()
                    mock_adapter_factory_class.return_value = mock_adapter_factory
                    
                    mock_command_service = MagicMock()
                    mock_command_service_class.return_value = mock_command_service
                    
                    # Return filtered emails
                    filtered_emails = [email for email in mock_emails if email.has_attachments]
                    
                    # Mock the result from CommandProcessingService (includes sorting)
                    mock_paginator = MagicMock()
                    mock_command_service.process_email_command.return_value = {
                        'emails': filtered_emails,
                        'paginator': mock_paginator,
                        'current_page': filtered_emails
                    }
                    
                    args = type('Args', (), {
                        'folder': 'Inbox',
                        'since': None,
                        'until': None,
                        'is_read': None,
                        'is_unread': None,
                        'has_attachment': True,
                        'no_attachment': None,
                        'importance': None,
                        'not_sender': None,
                        'not_subject': None,
                        'sort_by': 'received_date',
                        'sort_order': 'asc'
                    })()
                    
                    cli.handle_read(args)
                    
                    # Verify the service interactions (CommandProcessingService handles both filtering and sorting)
                    mock_filter_service.parse_date_filters.assert_called_once_with(args)
                    mock_filter_service.build_search_params.assert_called_once_with(args, None, None)
                    mock_command_service.process_email_command.assert_called_once_with(
                        args, {'folder': 'Inbox', 'has_attachment': True}, "reading emails"
                    )