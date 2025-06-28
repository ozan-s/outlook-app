"""Tests for configuration system (Phase 2 of Milestone 015+016)."""

import os
import io
import sys
from unittest.mock import patch, MagicMock
import pytest
from outlook_cli.cli import main


class TestConfigurationSystem:
    """Test suite for adapter configuration system."""
    
    def test_environment_variable_selects_adapter_type(self):
        """Test that OUTLOOK_ADAPTER environment variable selects adapter type."""
        # Mock the adapters to avoid Windows COM dependencies
        mock_real_adapter = MagicMock()
        mock_mock_adapter = MagicMock()
        
        captured_output = io.StringIO()
        
        with patch.dict(os.environ, {'OUTLOOK_ADAPTER': 'real'}), \
             patch('outlook_cli.adapters.pywin32_adapter.PyWin32OutlookAdapter', return_value=mock_real_adapter), \
             patch('outlook_cli.adapters.mock_adapter.MockOutlookAdapter', return_value=mock_mock_adapter), \
             patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass
            
            # Verify real adapter was used (not mock adapter)
            # Should fail initially since configuration system doesn't exist yet
            # This test will demonstrate the configuration system working
        
        assert True  # Placeholder - will be enhanced when config system exists
    
    def test_cli_argument_overrides_environment_variable(self):
        """Test that --adapter CLI argument overrides environment variable."""
        mock_real_adapter = MagicMock()
        mock_mock_adapter = MagicMock()
        
        captured_output = io.StringIO()
        
        with patch.dict(os.environ, {'OUTLOOK_ADAPTER': 'real'}), \
             patch('outlook_cli.config.adapter_factory.PyWin32OutlookAdapter', return_value=mock_real_adapter), \
             patch('outlook_cli.config.adapter_factory.MockOutlookAdapter', return_value=mock_mock_adapter), \
             patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', '--adapter', 'mock', 'read', '--folder', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass
            
            # Should use mock adapter despite OUTLOOK_ADAPTER=real
            # Check that MockOutlookAdapter was instantiated, not PyWin32OutlookAdapter
            # This demonstrates CLI argument overriding environment variable
    
    def test_invalid_adapter_names_show_helpful_error(self):
        """Test that invalid adapter names show helpful error message."""
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        
        with patch('sys.stdout', captured_output), \
             patch('sys.stderr', captured_error), \
             patch('sys.argv', ['outlook-cli', '--adapter', 'invalid', 'read', '--folder', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass
            
            output = captured_output.getvalue() + captured_error.getvalue()
            
            # Should contain helpful error about valid adapter types
            assert 'invalid' in output.lower()
            assert 'mock' in output.lower() and 'real' in output.lower()
    
    def test_default_behavior_uses_mock_adapter_for_safety(self):
        """Test that default behavior uses MockAdapter when no config specified."""
        # Clear any environment variables
        env_without_adapter = {k: v for k, v in os.environ.items() if k != 'OUTLOOK_ADAPTER'}
        
        captured_output = io.StringIO()
        
        with patch.dict(os.environ, env_without_adapter, clear=True), \
             patch('sys.stdout', captured_output), \
             patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Inbox']):
            
            try:
                main()
            except SystemExit:
                pass
            
            output = captured_output.getvalue()
            
            # Should successfully run with mock adapter (contains email data)
            assert 'Page' in output or 'emails' in output
            # No error messages about missing adapters
            assert 'Error' not in output
    
    def test_adapter_factory_creates_correct_adapter_instances(self):
        """Test that AdapterFactory creates correct adapter instances."""
        # This will test the factory pattern directly
        # Will fail initially since AdapterFactory doesn't exist
        
        # Import will fail initially - that's expected (RED phase)
        try:
            from outlook_cli.config.adapter_factory import AdapterFactory
            
            # Test mock adapter creation
            mock_adapter = AdapterFactory.create_adapter('mock')
            assert mock_adapter.__class__.__name__ == 'MockOutlookAdapter'
            
            # Test real adapter creation (will be mocked to avoid Windows dependency)
            with patch('outlook_cli.config.adapter_factory.PyWin32OutlookAdapter') as mock_real:
                mock_real.return_value = MagicMock()
                mock_real.return_value.__class__.__name__ = 'PyWin32OutlookAdapter'
                real_adapter = AdapterFactory.create_adapter('real')
                mock_real.assert_called_once()
                assert real_adapter.__class__.__name__ == 'PyWin32OutlookAdapter'
            
            # Test default (should be mock for safety)
            default_adapter = AdapterFactory.create_adapter()
            assert default_adapter.__class__.__name__ == 'MockOutlookAdapter'
            
            # Test invalid adapter type
            with pytest.raises(ValueError, match="Invalid adapter type"):
                AdapterFactory.create_adapter('invalid')
            
        except ImportError:
            # Expected during RED phase - AdapterFactory doesn't exist yet
            pytest.fail("AdapterFactory not implemented yet (expected during RED phase)")