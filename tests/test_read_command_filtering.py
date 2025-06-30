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
    
    This test should fail initially and pass after implementation.
    """
    with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Set up mock adapter
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            # Mock EmailSearcher (what we want to use after implementation)
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                
                # Only return emails from last 7 days (email1 and email3, not email2 from June 1)
                recent_emails = [email for email in mock_emails if email.received_date.day >= 27]
                mock_searcher.search_emails.return_value = recent_emails
                
                # Mock Paginator
                with patch('outlook_cli.cli.Paginator') as mock_paginator_class:
                    mock_paginator = MagicMock()
                    mock_paginator_class.return_value = mock_paginator
                    mock_paginator.get_current_page.return_value = recent_emails
                    
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
                    
                    # This assertion will fail initially because current implementation uses EmailReader
                    # and will pass after we implement EmailSearcher with date filtering
                    mock_searcher_class.assert_called_once()
                    mock_searcher.search_emails.assert_called_once()
                    
                    # Verify that search_emails was called with since parameter
                    call_args = mock_searcher.search_emails.call_args
                    assert call_args is not None
                    assert 'since' in call_args.kwargs
                    assert call_args.kwargs['since'] is not None


def test_read_command_with_is_unread_filter_should_filter_by_read_status(mock_emails):
    """Test that read command with --is-unread filter returns only unread emails."""
    with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
        with patch('sys.stdout', new_callable=StringIO):
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            # Mock EmailSearcher 
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                
                # Only return unread emails (just email1 which has is_read=False)
                unread_emails = [email for email in mock_emails if not email.is_read]
                mock_searcher.search_emails.return_value = unread_emails
                
                with patch('outlook_cli.cli.Paginator') as mock_paginator_class:
                    mock_paginator = MagicMock()
                    mock_paginator_class.return_value = mock_paginator
                    mock_paginator.get_current_page.return_value = unread_emails
                    
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
                    
                    # Verify EmailSearcher was called with is_unread=True
                    mock_searcher.search_emails.assert_called_once()
                    call_args = mock_searcher.search_emails.call_args
                    assert call_args.kwargs['is_unread'] is True
                    assert call_args.kwargs['is_read'] is None


def test_read_command_with_has_attachment_filter_should_filter_by_attachments(mock_emails):
    """Test that read command with --has-attachment filter returns only emails with attachments."""
    with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
        with patch('sys.stdout', new_callable=StringIO):
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                
                # Only return emails with attachments (email1 and email3)
                attachment_emails = [email for email in mock_emails if email.has_attachments]
                mock_searcher.search_emails.return_value = attachment_emails
                
                with patch('outlook_cli.cli.Paginator') as mock_paginator_class:
                    mock_paginator = MagicMock()
                    mock_paginator_class.return_value = mock_paginator
                    mock_paginator.get_current_page.return_value = attachment_emails
                    
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
                    
                    # Verify EmailSearcher was called with has_attachment=True
                    mock_searcher.search_emails.assert_called_once()
                    call_args = mock_searcher.search_emails.call_args
                    assert call_args.kwargs['has_attachment'] is True
                    assert call_args.kwargs['no_attachment'] is None


def test_read_command_with_combined_filters_should_apply_all_filters(mock_emails):
    """Test that read command with multiple filters applies all filters correctly."""
    with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
        with patch('sys.stdout', new_callable=StringIO):
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                
                # Only return emails that are both recent AND unread (just email1)
                filtered_emails = [
                    email for email in mock_emails 
                    if email.received_date.day >= 27 and not email.is_read
                ]
                mock_searcher.search_emails.return_value = filtered_emails
                
                with patch('outlook_cli.cli.Paginator') as mock_paginator_class:
                    mock_paginator = MagicMock()
                    mock_paginator_class.return_value = mock_paginator
                    mock_paginator.get_current_page.return_value = filtered_emails
                    
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
                    
                    # Verify EmailSearcher was called with both filters
                    mock_searcher.search_emails.assert_called_once()
                    call_args = mock_searcher.search_emails.call_args
                    assert call_args.kwargs['since'] is not None
                    assert call_args.kwargs['is_unread'] is True


def test_read_command_with_sorting_and_filtering_integration(mock_emails):
    """Test that read command applies both filtering and sorting correctly."""
    with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
        with patch('sys.stdout', new_callable=StringIO):
            mock_adapter = MagicMock()
            mock_create_adapter.return_value = mock_adapter
            
            with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                mock_searcher = MagicMock()
                mock_searcher_class.return_value = mock_searcher
                
                # Return filtered emails
                filtered_emails = [email for email in mock_emails if email.has_attachments]
                mock_searcher.search_emails.return_value = filtered_emails
                
                with patch('outlook_cli.cli.EmailSortingService') as mock_sorting_class:
                    mock_sorting_service = MagicMock()
                    mock_sorting_class.return_value = mock_sorting_service
                    mock_sorting_service.sort_emails.return_value = filtered_emails  # sorted
                    
                    with patch('outlook_cli.cli.Paginator') as mock_paginator_class:
                        mock_paginator = MagicMock()
                        mock_paginator_class.return_value = mock_paginator
                        mock_paginator.get_current_page.return_value = filtered_emails
                        
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
                        
                        # Verify both filtering and sorting were applied
                        mock_searcher.search_emails.assert_called_once()
                        mock_sorting_service.sort_emails.assert_called_once_with(
                            filtered_emails, 'received_date', 'asc'
                        )