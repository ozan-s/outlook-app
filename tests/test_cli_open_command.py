"""Test CLI open command implementation."""

import pytest
from unittest.mock import patch, Mock
import io
from outlook_cli.cli import handle_open
from outlook_cli.models import Email
from datetime import datetime, timezone


class TestCliOpenCommand:
    """Test suite for CLI open command."""
    
    def test_handle_open_displays_email_correctly(self):
        """Test that handle_open retrieves and displays email correctly."""
        # Mock args
        args = Mock()
        args.email_id = "inbox-001"
        args.adapter = None  # Use default adapter
        
        # Capture stdout
        captured_output = io.StringIO()
        
        # This will fail until we implement handle_open properly
        with patch('sys.stdout', captured_output):
            handle_open(args)
        
        output = captured_output.getvalue()
        
        # Should display full email content
        assert "Email ID: inbox-001" in output
        assert "Weekly Team Meeting" in output
        assert "Alice Manager" in output
        assert "manager@company.com" in output
        assert "Hi team, our weekly meeting" in output
        assert "CONTENT:" in output
        assert "=" in output  # Content separator
    
    def test_handle_open_shows_error_for_nonexistent_email(self):
        """Test that handle_open shows friendly error for non-existent email."""
        # Mock args
        args = Mock()
        args.email_id = "nonexistent-123"
        args.adapter = None  # Use default adapter
        
        # Capture stdout
        captured_output = io.StringIO()
        
        # This will fail until we implement handle_open properly
        with patch('sys.stdout', captured_output):
            handle_open(args)
        
        output = captured_output.getvalue()
        
        # Should show user-friendly error
        assert "Error: Email 'nonexistent-123' not found" in output
    
    def test_display_full_email_function_exists(self):
        """Test that _display_full_email function exists and is importable."""
        # This will fail until we create the _display_full_email function
        try:
            from outlook_cli.cli import _display_full_email
            assert callable(_display_full_email), "_display_full_email must be callable"
        except ImportError:
            pytest.fail("_display_full_email function not found in cli module")
    
    def test_display_full_email_formats_correctly(self):
        """Test that _display_full_email formats email content properly."""
        from outlook_cli.cli import _display_full_email
        
        # Create test email
        test_email = Email(
            id="test-001",
            subject="Test Subject",
            sender_email="sender@test.com",
            sender_name="Test Sender",
            recipient_emails=["recipient@test.com", "cc@test.com"],
            cc_emails=["cc@test.com"],
            received_date=datetime(2024, 6, 28, 10, 30, tzinfo=timezone.utc),
            body_text="This is the email body content.",
            folder_path="Inbox",
            has_attachments=True,
            attachment_count=2,
            is_read=False,
            importance="High"
        )
        
        # Capture stdout
        captured_output = io.StringIO()
        
        with patch('sys.stdout', captured_output):
            _display_full_email(test_email)
        
        output = captured_output.getvalue()
        
        # Verify all expected elements are displayed
        assert "Email ID: test-001 [UNREAD]" in output
        assert "Subject: Test Subject" in output
        assert "From: Test Sender <sender@test.com>" in output
        assert "To: recipient@test.com, cc@test.com" in output
        assert "CC: cc@test.com" in output
        assert "Date: 2024-06-28 10:30" in output
        assert "Importance: High" in output
        assert "📎 Attachments: 2" in output
        assert "Folder: Inbox" in output
        assert "CONTENT:" in output
        assert "This is the email body content." in output
        assert "="*50 in output  # Content separator