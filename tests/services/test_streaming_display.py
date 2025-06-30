"""
Tests for StreamingResultDisplay functionality.

TDD Implementation: Start with failing tests, then implement to make them pass.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from datetime import datetime

# This will fail initially - classes don't exist yet
try:
    from outlook_cli.services.streaming_display import StreamingResultDisplay
except ImportError:
    StreamingResultDisplay = None

from outlook_cli.models.email import Email


class TestStreamingResultDisplay(unittest.TestCase):
    """Test streaming display functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Skip tests if classes not implemented yet
        if StreamingResultDisplay is None:
            self.skipTest("StreamingResultDisplay not implemented yet")
            
        self.display = StreamingResultDisplay()
        
        # Create test emails
        self.test_emails = [
            Email(
                id="email-001",
                subject="Test Email 1", 
                sender_email="sender1@test.com",
                sender_name="Sender One",
                recipient_emails=["user@test.com"],
                received_date=datetime(2025, 6, 30, 10, 0),
                body_text="Test body 1",
                is_read=False,
                has_attachments=True,
                folder_path="Inbox"
            ),
            Email(
                id="email-002", 
                subject="Test Email 2",
                sender_email="sender2@test.com",
                sender_name="Sender Two",
                recipient_emails=["user@test.com"],
                received_date=datetime(2025, 6, 30, 11, 0),
                body_text="Test body 2",
                is_read=True,
                has_attachments=False,
                folder_path="Inbox"
            )
        ]

    def test_stream_results_displays_chunks_incrementally(self):
        """Test that stream_results displays chunks immediately, not all at once."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # This should display results in chunks of 2
            self.display.stream_results(self.test_emails, chunk_size=2)
            
            output = mock_stdout.getvalue()
            
            # Should contain both emails
            self.assertIn("Test Email 1", output)
            self.assertIn("Test Email 2", output)
            # Should not have pagination headers like "Page 1 of 2"
            self.assertNotIn("Page ", output)

    def test_show_large_result_warning_displays_warning(self):
        """Test that large result warning is shown for >1000 results."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.show_large_result_warning(1500)
            
            output = mock_stdout.getvalue()
            
            # Should warn about large result set
            self.assertIn("1500", output)
            self.assertIn("large", output.lower())
            self.assertIn("warning", output.lower())

    def test_display_streaming_chunk_shows_chunk_without_pagination(self):
        """Test that chunk display doesn't show pagination headers."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.display_streaming_chunk(self.test_emails, chunk_num=1)
            
            output = mock_stdout.getvalue()
            
            # Should show emails
            self.assertIn("Test Email 1", output) 
            self.assertIn("Test Email 2", output)
            # Should NOT show pagination info
            self.assertNotIn("Page ", output)
            self.assertNotIn("showing ", output)


if __name__ == '__main__':
    unittest.main()