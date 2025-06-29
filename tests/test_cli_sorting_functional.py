"""Functional tests for CLI sorting integration."""

import subprocess
import tempfile
import os
from typing import List


class TestCLISortingFunctional:
    """Functional tests for CLI sorting with mock adapter."""
    
    def test_find_command_with_sort_by_subject_uses_mock_adapter(self):
        """Test that find command with sorting works with mock adapter."""
        # Arrange
        env = os.environ.copy()
        env['OUTLOOK_ADAPTER'] = 'mock'  # Use mock adapter for testing
        
        # Act - run find command with sorting
        result = subprocess.run([
            'uv', 'run', 'outlook-cli', 'find',
            '--keyword', 'meeting',
            '--sort-by', 'subject',
            '--sort-order', 'asc'
        ], capture_output=True, text=True, env=env, timeout=10)
        
        # Assert - command should not crash and should complete successfully
        assert result.returncode == 0
        assert "Error:" not in result.stdout
        # The command should process the sort flags without error
        
    def test_read_command_with_sort_by_sender_uses_mock_adapter(self):
        """Test that read command with sorting works with mock adapter."""
        # Arrange  
        env = os.environ.copy()
        env['OUTLOOK_ADAPTER'] = 'mock'  # Use mock adapter for testing
        
        # Act - run read command with sorting
        result = subprocess.run([
            'uv', 'run', 'outlook-cli', 'read',
            '--sort-by', 'sender',
            '--sort-order', 'asc'
        ], capture_output=True, text=True, env=env, timeout=10)
        
        # Assert - command should not crash and should complete successfully
        assert result.returncode == 0
        assert "Error:" not in result.stdout
        # The command should process the sort flags without error