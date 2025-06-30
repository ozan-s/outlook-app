"""
Tests for CLI streaming integration functionality.

TDD Implementation: Tests for --all flag detection and streaming integration.
"""

import unittest
from unittest.mock import patch
from io import StringIO


class TestCLIStreamingIntegration(unittest.TestCase):
    """Test CLI integration with streaming functionality."""

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--all'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_command_with_all_flag_uses_streaming(self, mock_stdout):
        """Test that find command with --all flag uses streaming instead of pagination."""
        # Import and run CLI with built-in MockOutlookAdapter data
        from outlook_cli.cli import main
        
        # This should detect --all flag and use streaming
        # Currently this test WILL FAIL because streaming is not implemented yet
        try:
            main()
        except SystemExit:
            pass  # Normal CLI exit
        
        output = mock_stdout.getvalue()
        
        # Should NOT contain pagination headers like "Page 1 of X"
        self.assertNotIn("Page ", output)
        # Should contain search results
        self.assertIn("inbox-001", output)  # Built-in test email ID

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--limit', '1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_command_with_limit_flag_uses_pagination(self, mock_stdout):
        """Test that find command with --limit flag still uses pagination (backward compatibility)."""
        # Import and run CLI with built-in MockOutlookAdapter data
        from outlook_cli.cli import main
        
        try:
            main()
        except SystemExit:
            pass  # Normal CLI exit
        
        output = mock_stdout.getvalue()
        
        # Should contain pagination headers like "Page 1 of X, showing Y-Z of W emails"
        self.assertIn("Page ", output)
        self.assertIn("showing ", output)

    @patch('sys.argv', ['outlook-cli', 'find', '--folder', 'Inbox', '--keyword', 'meeting', '--all'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('outlook_cli.services.streaming_display.StreamingResultDisplay.show_large_result_warning')
    def test_find_command_detects_streaming_vs_pagination(self, mock_warning, mock_stdout):
        """Test that find command properly detects --all flag for streaming behavior."""
        # Import and run CLI
        from outlook_cli.cli import main
        
        try:
            main()
        except SystemExit:
            pass  # Normal CLI exit
        
        output = mock_stdout.getvalue()
        
        # Key test: --all flag should NOT use pagination format
        # This is the critical difference between streaming and pagination
        self.assertNotIn("Page ", output)
        self.assertNotIn("showing ", output)


if __name__ == '__main__':
    unittest.main()