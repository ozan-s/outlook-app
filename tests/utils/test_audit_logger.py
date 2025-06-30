"""Tests for AuditLogger utility."""

import pytest
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from outlook_cli.utils.audit_logger import AuditLogger, AuditEntry


class TestAuditLogger:
    """Test AuditLogger functionality."""
    
    def test_audit_logger_initialization(self):
        """Test that AuditLogger initializes correctly."""
        logger = AuditLogger()
        
        assert logger is not None
        assert hasattr(logger, 'log_filter_operation')
        assert hasattr(logger, 'log_performance_metrics')
        assert hasattr(logger, 'get_audit_entries')
    
    def test_audit_logger_with_custom_file(self):
        """Test AuditLogger with custom log file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            logger = AuditLogger(log_file=temp_path)
            assert logger._log_file == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_log_filter_operation_creates_audit_entry(self):
        """Test that filter operations are logged."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            logger = AuditLogger(log_file=temp_path)
            
            # Log a filter operation
            logger.log_filter_operation(
                operation="read",
                filters={"folder": "Inbox", "is_unread": True},
                user="test_user",
                result_count=5
            )
            
            # Verify entry was written
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert "read" in content
            assert "Inbox" in content
            assert "is_unread" in content
            assert "test_user" in content
            assert "5" in content
        finally:
            os.unlink(temp_path)
    
    def test_log_performance_metrics_creates_audit_entry(self):
        """Test that performance metrics are logged."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            logger = AuditLogger(log_file=temp_path)
            
            # Log performance metrics
            logger.log_performance_metrics(
                operation="search",
                duration_seconds=1.23,
                memory_used_mb=45.6,
                result_count=100
            )
            
            # Verify entry was written
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert "search" in content
            assert "1.23" in content
            assert "45.6" in content
            assert "100" in content
        finally:
            os.unlink(temp_path)
    
    def test_audit_logger_disabled_by_environment(self):
        """Test that audit logging can be disabled via environment variable."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Disable audit logging
            os.environ['OUTLOOK_CLI_AUDIT_ENABLED'] = 'false'
            
            logger = AuditLogger(log_file=temp_path)
            
            # Log something
            logger.log_filter_operation(
                operation="read",
                filters={"folder": "Inbox"},
                user="test_user",
                result_count=5
            )
            
            # File should be empty or not exist
            if os.path.exists(temp_path):
                with open(temp_path, 'r') as f:
                    content = f.read().strip()
                assert content == ""
        finally:
            # Clean up
            if 'OUTLOOK_CLI_AUDIT_ENABLED' in os.environ:
                del os.environ['OUTLOOK_CLI_AUDIT_ENABLED']
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_audit_entries_returns_parsed_logs(self):
        """Test that audit entries can be retrieved and parsed."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name
        
        try:
            logger = AuditLogger(log_file=temp_path)
            
            # Log multiple operations
            logger.log_filter_operation(
                operation="read",
                filters={"folder": "Inbox"},
                user="user1",
                result_count=5
            )
            logger.log_filter_operation(
                operation="find",
                filters={"sender": "test@example.com"},
                user="user2",
                result_count=3
            )
            
            # Get entries
            entries = logger.get_audit_entries(limit=10)
            
            assert len(entries) == 2
            assert all(isinstance(entry, AuditEntry) for entry in entries)
            assert entries[0].operation in ["read", "find"]
            assert entries[1].operation in ["read", "find"]
        finally:
            os.unlink(temp_path)


class TestAuditEntry:
    """Test AuditEntry data class."""
    
    def test_audit_entry_initialization(self):
        """Test AuditEntry initialization."""
        timestamp = datetime.now()
        entry = AuditEntry(
            timestamp=timestamp,
            operation="test_op",
            user="test_user",
            details={"key": "value"},
            result_count=42
        )
        
        assert entry.timestamp == timestamp
        assert entry.operation == "test_op"
        assert entry.user == "test_user"
        assert entry.details == {"key": "value"}
        assert entry.result_count == 42
    
    def test_audit_entry_to_dict(self):
        """Test AuditEntry dictionary conversion."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        entry = AuditEntry(
            timestamp=timestamp,
            operation="test_op",
            user="test_user",
            details={"key": "value"},
            result_count=42
        )
        
        result = entry.to_dict()
        
        expected = {
            "timestamp": timestamp.isoformat(),
            "operation": "test_op",
            "user": "test_user",
            "details": {"key": "value"},
            "result_count": 42
        }
        assert result == expected
    
    def test_audit_entry_from_dict(self):
        """Test creating AuditEntry from dictionary."""
        data = {
            "timestamp": "2023-01-01T12:00:00",
            "operation": "test_op",
            "user": "test_user",
            "details": {"key": "value"},
            "result_count": 42
        }
        
        entry = AuditEntry.from_dict(data)
        
        assert entry.operation == "test_op"
        assert entry.user == "test_user"
        assert entry.details == {"key": "value"}
        assert entry.result_count == 42
        assert isinstance(entry.timestamp, datetime)