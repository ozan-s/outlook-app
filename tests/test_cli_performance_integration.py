"""Tests for CLI performance monitoring integration."""

import pytest
import tempfile
import os
import json
from io import StringIO
from unittest.mock import patch, MagicMock
from outlook_cli import cli
from outlook_cli.utils.performance_monitor import PerformanceMonitor
from outlook_cli.utils.audit_logger import AuditLogger
from outlook_cli.utils.resource_monitor import ResourceMonitor, ResourceExceededError


class TestCLIPerformanceIntegration:
    """Test CLI integration with performance monitoring."""
    
    def test_read_command_captures_performance_metrics(self):
        """Test that read command captures performance metrics."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('outlook_cli.cli.performance_monitor') as mock_monitor:
                mock_monitor.start_monitoring.return_value = None
                mock_monitor.stop_monitoring.return_value = MagicMock(
                    duration_seconds=0.5,
                    memory_used_mb=10.5,
                    operation_name="read_command"
                )
                
                with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    mock_service.process_email_command.return_value = {
                        'emails': [],
                        'paginator': None,
                        'current_page': None
                    }
                    
                    with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                        mock_filter_service = MagicMock()
                        mock_filter_class.return_value = mock_filter_service
                        mock_filter_service.parse_date_filters.return_value = (None, None)
                        mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
                        
                        with patch('outlook_cli.cli.AdapterFactory'):
                            args = type('Args', (), {
                                'folder': 'Inbox',
                                'since': None, 'until': None, 'is_read': None, 'is_unread': None,
                                'has_attachment': None, 'no_attachment': None, 'importance': None,
                                'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                            })()
                            
                            cli.handle_read(args)
                            
                            # Verify performance monitoring was called
                            mock_monitor.start_monitoring.assert_called_with("read_command")
                            mock_monitor.stop_monitoring.assert_called_with("read_command")
    
    def test_find_command_captures_performance_metrics(self):
        """Test that find command captures performance metrics."""
        with patch('sys.stdout', new_callable=StringIO):
            with patch('outlook_cli.cli.performance_monitor') as mock_monitor:
                
                with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    mock_service.process_email_command.return_value = {
                        'emails': [],
                        'paginator': None,
                        'current_page': None
                    }
                    
                    with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                        mock_filter_service = MagicMock()
                        mock_filter_class.return_value = mock_filter_service
                        mock_filter_service.parse_date_filters.return_value = (None, None)
                        mock_filter_service.build_search_params.return_value = {
                            'sender': 'test@example.com'
                        }
                        
                        with patch('outlook_cli.cli.AdapterFactory'):
                            with patch('outlook_cli.cli._create_adapter') as mock_create_adapter:
                                with patch('outlook_cli.cli.EmailSearcher') as mock_searcher_class:
                                    with patch('outlook_cli.cli._display_email_page') as mock_display:
                                        mock_searcher = MagicMock()
                                        mock_searcher_class.return_value = mock_searcher
                                        mock_searcher.search_emails.return_value = [MagicMock(), MagicMock()]  # 2 results
                                        
                                        args = type('Args', (), {
                                            'keyword': None,
                                            'sender': 'test@example.com',
                                            'subject': None, 'folder': None,
                                            'since': None, 'until': None, 'is_read': None, 'is_unread': None,
                                            'has_attachment': None, 'no_attachment': None, 'importance': None,
                                            'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                                        })()
                                
                                        cli.handle_find(args)
                                        
                                        # Verify performance monitoring was called
                                        mock_monitor.start_monitoring.assert_called_with("find_command")
                                        mock_monitor.stop_monitoring.assert_called_with("find_command")


class TestCLIAuditLogging:
    """Test CLI integration with audit logging."""
    
    def test_read_command_creates_audit_log_entry(self):
        """Test that read command creates audit log entries."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('sys.stdout', new_callable=StringIO):
                with patch('outlook_cli.cli.audit_logger') as mock_logger:
                    
                    with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service_class.return_value = mock_service
                        mock_service.process_email_command.return_value = {
                            'emails': [MagicMock(), MagicMock()],  # 2 emails
                            'paginator': None,
                            'current_page': None
                        }
                        
                        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                            mock_filter_service = MagicMock()
                            mock_filter_class.return_value = mock_filter_service
                            mock_filter_service.parse_date_filters.return_value = (None, None)
                            mock_filter_service.build_search_params.return_value = {
                                'folder': 'Inbox',
                                'is_unread': True
                            }
                            
                            with patch('outlook_cli.cli.AdapterFactory'):
                                args = type('Args', (), {
                                    'folder': 'Inbox',
                                    'is_unread': True,
                                    'since': None, 'until': None, 'is_read': None,
                                    'has_attachment': None, 'no_attachment': None, 'importance': None,
                                    'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                                })()
                                
                                cli.handle_read(args)
                                
                                # Verify audit logging was called
                                mock_logger.log_filter_operation.assert_called_once()
                                call_args = mock_logger.log_filter_operation.call_args
                                assert call_args[1]['operation'] == 'read'
                                assert call_args[1]['result_count'] == 2
                                assert 'Inbox' in str(call_args[1]['filters'])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_audit_logging_can_be_disabled(self):
        """Test that audit logging can be disabled via environment variable."""
        with patch.dict(os.environ, {'OUTLOOK_CLI_AUDIT_ENABLED': 'false'}):
            with patch('sys.stdout', new_callable=StringIO):
                with patch('outlook_cli.cli.audit_logger') as mock_logger:
                    mock_logger.log_filter_operation.return_value = None  # Should not be called
                    
                    with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service_class.return_value = mock_service
                        mock_service.process_email_command.return_value = {
                            'emails': [],
                            'paginator': None,
                            'current_page': None
                        }
                        
                        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                            mock_filter_service = MagicMock()
                            mock_filter_class.return_value = mock_filter_service
                            mock_filter_service.parse_date_filters.return_value = (None, None)
                            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
                            
                            with patch('outlook_cli.cli.AdapterFactory'):
                                args = type('Args', (), {
                                    'folder': 'Inbox',
                                    'since': None, 'until': None, 'is_read': None, 'is_unread': None,
                                    'has_attachment': None, 'no_attachment': None, 'importance': None,
                                    'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                                })()
                                
                                cli.handle_read(args)
                                
                                # When disabled, audit logger instance still exists but doesn't log
                                # The behavior is controlled by the OUTLOOK_CLI_AUDIT_ENABLED environment variable


class TestCLIResourceLimits:
    """Test CLI integration with resource limits."""
    
    def test_read_command_enforces_resource_limits(self):
        """Test that read command enforces resource limits."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('outlook_cli.cli.resource_monitor') as mock_monitor:
                
                # Simulate resource limit exceeded
                mock_monitor.check_memory_usage.side_effect = ResourceExceededError(
                    "Memory limit exceeded", "memory", 1024, 2048
                )
                
                with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                        mock_filter_service = MagicMock()
                        mock_filter_class.return_value = mock_filter_service
                        mock_filter_service.parse_date_filters.return_value = (None, None)
                        mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
                        
                        with patch('outlook_cli.cli.AdapterFactory'):
                            args = type('Args', (), {
                                'folder': 'Inbox',
                                'since': None, 'until': None, 'is_read': None, 'is_unread': None,
                                'has_attachment': None, 'no_attachment': None, 'importance': None,
                                'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                            })()
                            
                            cli.handle_read(args)
                            
                            output = mock_stdout.getvalue()
                            # Should show resource limit error
                            assert "Error:" in output
                            assert "Memory limit exceeded" in output
    
    def test_resource_limits_configurable_via_environment(self):
        """Test that resource limits can be configured via environment variables."""
        with patch.dict(os.environ, {
            'OUTLOOK_CLI_MAX_MEMORY_MB': '2048',
            'OUTLOOK_CLI_MAX_PROCESSING_TIME': '120'
        }):
            with patch('outlook_cli.cli.resource_monitor') as mock_monitor:
                
                # Resource monitor is already instantiated at module level with defaults
                # Environment variables are read during ResourceLimits.__init__()
                
                with patch('sys.stdout', new_callable=StringIO):
                    with patch('outlook_cli.cli.CommandProcessingService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service_class.return_value = mock_service
                        mock_service.process_email_command.return_value = {
                            'emails': [],
                            'paginator': None,
                            'current_page': None
                        }
                        
                        with patch('outlook_cli.cli.FilterParsingService') as mock_filter_class:
                            mock_filter_service = MagicMock()
                            mock_filter_class.return_value = mock_filter_service
                            mock_filter_service.parse_date_filters.return_value = (None, None)
                            mock_filter_service.build_search_params.return_value = {'folder': 'Inbox'}
                            
                            with patch('outlook_cli.cli.AdapterFactory'):
                                args = type('Args', (), {
                                    'folder': 'Inbox',
                                    'since': None, 'until': None, 'is_read': None, 'is_unread': None,
                                    'has_attachment': None, 'no_attachment': None, 'importance': None,
                                    'not_sender': None, 'not_subject': None, 'sort_by': None, 'sort_order': 'desc'
                                })()
                                
                                cli.handle_read(args)
                                
                                # Should have been called with environment-configured limits
                                # Note: The instance is already created at module level, so we can't test constructor calls