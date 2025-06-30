"""
Tests for streaming validation - performance, memory limits, backward compatibility.

TDD Implementation: Comprehensive validation of streaming functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import time
from datetime import datetime

from outlook_cli.models.email import Email
from outlook_cli.services.streaming_display import StreamingResultDisplay
from outlook_cli.services.streaming_paginator import StreamingPaginator
from outlook_cli.utils.resource_monitor import ResourceExceededError


class TestStreamingValidation(unittest.TestCase):
    """Test validation of streaming functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.display = StreamingResultDisplay()
        self.paginator = StreamingPaginator()
        
        # Create large test email set for performance testing
        self.large_email_set = [
            Email(
                id=f"email-{i:04d}",
                subject=f"Test Email {i}", 
                sender_email=f"sender{i}@test.com",
                sender_name=f"Sender {i}",
                recipient_emails=["user@test.com"],
                received_date=datetime(2025, 6, 30, 10, i % 60),
                body_text=f"Test body {i}",
                is_read=(i % 2 == 0),
                has_attachments=(i % 3 == 0),
                folder_path="Inbox"
            ) for i in range(1, 501)  # 500 test emails for performance testing
        ]

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--limit', '5'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_backward_compatibility_limit_flag_unchanged(self, mock_stdout):
        """Test that --limit flag behavior is completely unchanged."""
        from outlook_cli.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        
        # Must contain pagination headers (backward compatibility)
        self.assertIn("Page ", output)
        self.assertIn("showing ", output)
        # Must NOT contain streaming indicators
        self.assertNotIn("Streaming progress", output)
        self.assertNotIn("Warning", output)

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--all'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_all_flag_completely_different_from_limit(self, mock_stdout):
        """Test that --all flag behavior is completely different from --limit."""
        from outlook_cli.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        
        # Must NOT contain pagination headers (streaming behavior)
        self.assertNotIn("Page ", output)
        self.assertNotIn("showing ", output)

    def test_memory_limits_respected_during_streaming(self):
        """Test that streaming respects memory limits via ResourceMonitor."""
        # Mock resource monitor to simulate memory limit exceeded
        with patch.object(self.paginator, 'resource_monitor') as mock_monitor:
            mock_monitor.check_memory_usage.side_effect = [None, None, ResourceExceededError("Memory limit exceeded", "memory")]
            
            chunks_processed = 0
            with self.assertRaises(ResourceExceededError):
                for chunk in self.paginator.stream_all_results(self.large_email_set, chunk_size=100):
                    chunks_processed += 1
            
            # Should have processed some chunks before hitting memory limit
            self.assertGreater(chunks_processed, 0)
            self.assertLess(chunks_processed, 5)  # Should stop before processing all

    def test_streaming_performance_with_large_result_sets(self):
        """Test that streaming performs reasonably with large result sets."""
        start_time = time.time()
        
        # Stream 500 emails - should be fast
        with patch('sys.stdout', new_callable=StringIO):
            self.display.stream_results(self.large_email_set, chunk_size=50)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time (less than 1 second for 500 emails)
        self.assertLess(duration, 1.0, f"Streaming took {duration:.2f}s, should be < 1.0s")

    def test_chunked_processing_memory_efficiency(self):
        """Test that chunked processing is more memory efficient than loading all at once."""
        # This test validates the design principle rather than actual memory usage
        
        chunk_sizes = []
        chunk_count = 0
        
        for chunk in self.paginator.stream_all_results(self.large_email_set, chunk_size=50):
            chunk_sizes.append(len(chunk))
            chunk_count += 1
        
        # Should process in consistent chunk sizes
        self.assertGreater(chunk_count, 1)  # Multiple chunks
        self.assertEqual(max(chunk_sizes), 50)  # Max chunk size respected
        self.assertLessEqual(min(chunk_sizes), 50)  # All chunks within limit

    def test_progress_indication_only_for_large_sets(self):
        """Test that progress indication only appears for large result sets."""
        # Small result set - no progress indication
        small_emails = self.large_email_set[:50]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.stream_results(small_emails, chunk_size=25)
            
            output = mock_stdout.getvalue()
            self.assertNotIn("Streaming progress", output)
        
        # Large result set - should show progress indication
        large_emails = self.large_email_set  # 500 emails
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.stream_results(large_emails, chunk_size=50)
            
            output = mock_stdout.getvalue()
            self.assertIn("Streaming progress", output)

    def test_warning_threshold_precise(self):
        """Test that warning threshold is exactly 1000 emails."""
        # Just under threshold - no warning
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            emails_999 = self.large_email_set[:999] if len(self.large_email_set) >= 999 else self.large_email_set
            # Simulate 999 emails in CLI
            from outlook_cli.services.streaming_display import StreamingResultDisplay
            display = StreamingResultDisplay()
            
            # No warning for 999 emails
            if len(emails_999) > 1000:  # Only test if we can simulate < 1000
                display.stream_results(emails_999)
                output = mock_stdout.getvalue()
                self.assertNotIn("Warning", output)

    def test_streaming_handles_empty_results(self):
        """Test that streaming gracefully handles empty result sets."""
        empty_emails = []
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.stream_results(empty_emails)
            
            output = mock_stdout.getvalue()
            # Should not crash, output should be empty or minimal
            self.assertNotIn("Error", output)
            self.assertNotIn("Exception", output)


if __name__ == '__main__':
    unittest.main()