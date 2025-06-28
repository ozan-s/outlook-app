"""
Tests for centralized logging configuration.
"""
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from outlook_cli.utils.logging_config import setup_logging, get_logger


class TestLoggingConfig:
    """Test centralized logging configuration."""

    def test_setup_logging_creates_console_and_file_handlers(self):
        """Test that setup_logging configures both console and file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup logging with custom log file
            setup_logging(log_file=str(log_file))
            
            # Get the root logger
            root_logger = logging.getLogger()
            
            # Should have 1 handler (file only - console removed for CLI polish)
            assert len(root_logger.handlers) == 1
            
            # Check that file handler was created
            file_handlers = [h for h in root_logger.handlers if hasattr(h, 'baseFilename')]
            assert len(file_handlers) == 1
            assert file_handlers[0].baseFilename == str(log_file)
            
            # Console handler should NOT exist (removed for CLI polish)
            console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')]
            assert len(console_handlers) == 0

    def test_setup_logging_creates_log_file(self):
        """Test that setup_logging creates the log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "outlook_cli.log"
            
            # Setup logging
            setup_logging(log_file=str(log_file))
            
            # Write a log message
            logger = get_logger("test")
            logger.info("Test message")
            
            # Log file should exist and contain our message
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_get_logger_returns_configured_logger(self):
        """Test that get_logger returns properly configured logger."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=str(log_file))
            
            # Get logger for specific component
            logger = get_logger("outlook_cli.services.email_reader")
            
            # Should be a Logger instance
            assert isinstance(logger, logging.Logger)
            assert logger.name == "outlook_cli.services.email_reader"
            
            # Should inherit from root logger configuration
            assert logger.level <= logging.INFO

    def test_logging_format_includes_timestamp_and_component(self):
        """Test that log messages include timestamp and component name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=str(log_file))
            
            # Write test message
            logger = get_logger("test_component")
            logger.info("Test message for formatting")
            
            # Check log file format
            content = log_file.read_text()
            assert "test_component" in content
            assert "INFO" in content
            assert "Test message for formatting" in content
            # Should contain timestamp (basic check for date format)
            assert any(char.isdigit() for char in content)

    def test_setup_logging_configurable_log_level(self):
        """Test that logging level can be configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "debug.log"
            
            # Setup with DEBUG level
            setup_logging(log_file=str(log_file), level=logging.DEBUG)
            
            logger = get_logger("debug_test")
            logger.debug("Debug message")
            logger.info("Info message")
            
            # Both messages should appear in debug mode
            content = log_file.read_text()
            assert "Debug message" in content
            assert "Info message" in content

    def test_setup_logging_with_info_level_filters_debug(self):
        """Test that INFO level filters out DEBUG messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "info.log"
            
            # Setup with INFO level (default)
            setup_logging(log_file=str(log_file), level=logging.INFO)
            
            logger = get_logger("info_test")
            logger.debug("Debug message should not appear")
            logger.info("Info message should appear")
            
            # Only info message should appear
            content = log_file.read_text()
            assert "Debug message should not appear" not in content
            assert "Info message should appear" in content

    def test_setup_logging_handles_missing_log_directory(self):
        """Test that setup_logging creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use nested directory that doesn't exist
            log_file = Path(temp_dir) / "logs" / "outlook_cli.log"
            
            # Should not raise exception
            setup_logging(log_file=str(log_file))
            
            # Directory should be created
            assert log_file.parent.exists()
            
            # Should be able to write to log
            logger = get_logger("test")
            logger.info("Test message")
            assert log_file.exists()