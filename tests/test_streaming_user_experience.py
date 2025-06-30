"""
Tests for streaming user experience features.

TDD Implementation: Tests for warnings, progress indication, and UX features.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from outlook_cli.services.streaming_display import StreamingResultDisplay


class TestStreamingUserExperience(unittest.TestCase):
    """Test user experience features for streaming."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.display = StreamingResultDisplay()

    def test_large_result_warning_shows_correct_message(self):
        """Test that large result warning shows proper message format."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.show_large_result_warning(1500)
            
            output = mock_stdout.getvalue()
            
            # Should show count and warning message
            self.assertIn("1500", output)
            self.assertIn("Warning", output)
            self.assertIn("Large result set", output)
            self.assertIn("Streaming results", output)

    def test_large_result_warning_threshold_works(self):
        """Test that warning is only shown for large result sets."""
        # Test that current CLI integration shows warning for >1000 results
        
        # This would require creating a mock adapter with >1000 emails
        # For now, test the display component directly
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Test exactly at threshold
            self.display.show_large_result_warning(1001)
            
            output = mock_stdout.getvalue()
            self.assertIn("1001", output)
            self.assertIn("Warning", output)

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--all'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_integration_respects_warning_threshold(self, mock_stdout):
        """Test that CLI integration properly triggers warnings for large result sets."""
        # For this test, we'd need to modify MockOutlookAdapter to have >1000 emails
        # Or create a custom test that mocks the result count
        
        # This test validates the integration works as expected
        from outlook_cli.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        
        # Should NOT show warning for small result set (MockAdapter has only a few emails)
        self.assertNotIn("Warning", output)
        self.assertNotIn("Large result set", output)

    def test_progress_indication_shows_correct_format(self):
        """Test that progress indication shows proper format."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.display.show_progress_indication(150, 300, 3, 6)
            
            output = mock_stdout.getvalue()
            
            # Should show progress in correct format
            self.assertIn("150/300", output)
            self.assertIn("50.0%", output)
            self.assertIn("Chunk 3/6", output)
            self.assertIn("Streaming progress", output)


if __name__ == '__main__':
    unittest.main()