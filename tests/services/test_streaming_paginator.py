"""
Tests for StreamingPaginator functionality.

TDD Implementation: Start with failing tests, then implement to make them pass.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# This will fail initially - classes don't exist yet
try:
    from outlook_cli.services.streaming_paginator import StreamingPaginator
except ImportError:
    StreamingPaginator = None

try:
    from outlook_cli.utils.resource_monitor import ResourceMonitor
except ImportError:
    ResourceMonitor = MagicMock

from outlook_cli.models.email import Email


class TestStreamingPaginator(unittest.TestCase):
    """Test streaming paginator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Skip tests if classes not implemented yet
        if StreamingPaginator is None:
            self.skipTest("StreamingPaginator not implemented yet")
            
        self.paginator = StreamingPaginator()
        
        # Create test emails
        self.test_emails = [
            Email(
                id=f"email-{i:03d}",
                subject=f"Test Email {i}", 
                sender_email=f"sender{i}@test.com",
                sender_name=f"Sender {i}",
                recipient_emails=["user@test.com"],
                received_date=datetime(2025, 6, 30, 10, i % 60),
                body_text=f"Test body {i}",
                is_read=(i % 2 == 0),
                has_attachments=(i % 3 == 0),
                folder_path="Inbox"
            ) for i in range(1, 101)  # 100 test emails
        ]

    def test_stream_all_results_returns_iterator(self):
        """Test that stream_all_results returns an iterator of chunks."""
        chunk_iterator = self.paginator.stream_all_results(self.test_emails)
        
        # Should be an iterator
        self.assertTrue(hasattr(chunk_iterator, '__iter__'))
        self.assertTrue(hasattr(chunk_iterator, '__next__'))

    def test_stream_all_results_yields_correct_chunk_sizes(self):
        """Test that chunks are correct size (default 50)."""
        chunks = list(self.paginator.stream_all_results(self.test_emails))
        
        # Should have 2 chunks (100 emails / 50 per chunk)
        self.assertEqual(len(chunks), 2)
        # First chunk should be 50 emails
        self.assertEqual(len(chunks[0]), 50)
        # Second chunk should be 50 emails  
        self.assertEqual(len(chunks[1]), 50)

    def test_stream_all_results_custom_chunk_size(self):
        """Test streaming with custom chunk size."""
        # Use smaller test set for custom chunk testing
        small_emails = self.test_emails[:25]
        chunks = list(self.paginator.stream_all_results(small_emails, chunk_size=10))
        
        # Should have 3 chunks (25 emails / 10 per chunk = 2.5 -> 3)
        self.assertEqual(len(chunks), 3)
        # First two chunks should be 10 emails
        self.assertEqual(len(chunks[0]), 10)
        self.assertEqual(len(chunks[1]), 10)
        # Last chunk should be 5 emails
        self.assertEqual(len(chunks[2]), 5)

    def test_get_chunk_size_returns_default(self):
        """Test that get_chunk_size returns reasonable default."""
        chunk_size = self.paginator.get_chunk_size()
        
        # Should be a reasonable chunk size (between 10 and 100)
        self.assertGreaterEqual(chunk_size, 10)
        self.assertLessEqual(chunk_size, 100)

    def test_stream_respects_memory_limits(self):
        """Test that streaming respects memory monitoring."""
        # Mock resource monitor to simulate memory limit exceeded after first chunk
        with patch.object(self.paginator, 'resource_monitor') as mock_monitor:
            mock_monitor.check_memory_usage.side_effect = [None, Exception("Memory exceeded")]
            
            chunks = []
            with self.assertRaises(Exception) as context:
                for chunk in self.paginator.stream_all_results(self.test_emails):
                    chunks.append(chunk)
            
            # Should have error message about memory
            self.assertIn("Memory", str(context.exception))
            # Should have processed exactly 1 chunk before stopping
            self.assertEqual(len(chunks), 1)


if __name__ == '__main__':
    unittest.main()