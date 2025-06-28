"""Tests for CLI polish features (Milestone 015+016)."""

import io
import sys
from unittest.mock import patch, MagicMock
import pytest
from outlook_cli.cli import main
import logging


class TestCLIPolish:
    """Test suite for CLI polish features."""
    
    def test_console_output_clean_no_log_messages(self):
        """Test that CLI operations produce clean console output with no log messages."""
        # Capture both stdout and stderr
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.stderr', captured_error), \
             patch('sys.argv', ['outlook-cli', 'read', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass  # Expected for CLI commands
            
            stdout_content = captured_output.getvalue()
            stderr_content = captured_error.getvalue()
            
            # Console output should contain email data but NO log messages
            # Log messages have format: "YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message"
            log_pattern_indicators = [
                " - outlook_cli",
                " - INFO -",
                " - ERROR -", 
                " - DEBUG -",
                " - WARNING -"
            ]
            
            for indicator in log_pattern_indicators:
                assert indicator not in stdout_content, f"Found log message in stdout: {stdout_content}"
                assert indicator not in stderr_content, f"Found log message in stderr: {stderr_content}"
            
            # Should still contain actual email data
            assert "emails" in stdout_content or "Page" in stdout_content
    
    def test_email_list_displays_email_ids(self):
        """Test that email list view displays email IDs alongside numbered items."""
        captured_output = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', 'read', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass
            
            output = captured_output.getvalue()
            
            # Should display format: "1. [inbox-001] [UNREAD] Subject..."
            # Look for pattern: number. [email-id] [status] 
            import re
            email_id_pattern = r'\d+\.\s+\[[\w-]+\]\s+\[(UNREAD|READ)\]'
            
            assert re.search(email_id_pattern, output), \
                f"Email ID pattern not found in output: {output}"
    
    def test_error_messages_use_red_color(self):
        """Test that error messages appear in red color."""
        captured_output = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', 'read', 'NonexistentFolder']):
            
            try:
                main()
            except SystemExit:
                pass
            
            output = captured_output.getvalue()
            
            # Should contain ANSI red color codes for errors
            # Red color code is \033[31m or \033[91m
            assert '\033[31m' in output or '\033[91m' in output, \
                f"Red color code not found in error output: {output}"
    
    def test_success_messages_use_green_color(self):
        """Test that success messages appear in green color."""
        # Test move command success message
        captured_output = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', 'move', 'inbox-001', 'Sent Items']):
            
            try:
                main()
            except SystemExit:
                pass
            
            output = captured_output.getvalue()
            
            # Should contain ANSI green color codes for success
            # Green color code is \033[32m or \033[92m
            assert '\033[32m' in output or '\033[92m' in output, \
                f"Green color code not found in success output: {output}"
    
    def test_help_text_includes_usage_examples(self):
        """Test that help text includes practical usage examples for all commands."""
        captured_output = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', '--help']):
            
            try:
                main()
            except SystemExit:
                pass
            
            help_output = captured_output.getvalue()
            
            # Should contain practical examples for all 4 commands
            expected_examples = [
                'outlook-cli read Inbox',
                'outlook-cli find "meeting"',
                'outlook-cli move inbox-001 "Sent Items"',
                'outlook-cli open inbox-001'
            ]
            
            for example in expected_examples:
                assert example in help_output, \
                    f"Example '{example}' not found in help output: {help_output}"