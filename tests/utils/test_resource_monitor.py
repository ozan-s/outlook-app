"""Tests for ResourceMonitor utility."""

import pytest
import time
import os
from unittest.mock import patch, MagicMock
from outlook_cli.utils.resource_monitor import ResourceMonitor, ResourceLimits, ResourceExceededError


class TestResourceLimits:
    """Test ResourceLimits configuration."""
    
    def test_resource_limits_initialization(self):
        """Test ResourceLimits initialization with defaults."""
        limits = ResourceLimits()
        
        assert limits.max_memory_mb > 0
        assert limits.max_processing_time_seconds > 0
        assert limits.max_result_count > 0
    
    def test_resource_limits_custom_values(self):
        """Test ResourceLimits with custom values."""
        limits = ResourceLimits(
            max_memory_mb=1024,
            max_processing_time_seconds=60,
            max_result_count=5000
        )
        
        assert limits.max_memory_mb == 1024
        assert limits.max_processing_time_seconds == 60
        assert limits.max_result_count == 5000
    
    def test_resource_limits_from_environment(self):
        """Test ResourceLimits reads from environment variables."""
        with patch.dict(os.environ, {
            'OUTLOOK_CLI_MAX_MEMORY_MB': '2048',
            'OUTLOOK_CLI_MAX_PROCESSING_TIME': '120',
            'OUTLOOK_CLI_MAX_RESULT_COUNT': '10000'
        }):
            limits = ResourceLimits()
            
            assert limits.max_memory_mb == 2048
            assert limits.max_processing_time_seconds == 120
            assert limits.max_result_count == 10000


class TestResourceMonitor:
    """Test ResourceMonitor functionality."""
    
    def test_resource_monitor_initialization(self):
        """Test ResourceMonitor initialization."""
        monitor = ResourceMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'check_memory_usage')
        assert hasattr(monitor, 'check_processing_time')
        assert hasattr(monitor, 'check_result_count')
        assert hasattr(monitor, 'monitor_operation')
    
    def test_resource_monitor_with_custom_limits(self):
        """Test ResourceMonitor with custom limits."""
        limits = ResourceLimits(max_memory_mb=512)
        monitor = ResourceMonitor(limits)
        
        assert monitor._limits.max_memory_mb == 512
    
    def test_check_memory_usage_passes_within_limit(self):
        """Test memory check passes when within limits."""
        limits = ResourceLimits(max_memory_mb=10000)  # Very high limit
        monitor = ResourceMonitor(limits)
        
        # Should not raise exception
        monitor.check_memory_usage()
    
    def test_check_memory_usage_raises_when_exceeded(self):
        """Test memory check raises exception when limit exceeded."""
        limits = ResourceLimits(max_memory_mb=1)  # Very low limit
        monitor = ResourceMonitor(limits)
        
        with pytest.raises(ResourceExceededError) as exc_info:
            monitor.check_memory_usage()
        
        assert "memory limit exceeded" in str(exc_info.value).lower()
    
    def test_check_processing_time_passes_within_limit(self):
        """Test processing time check passes when within limits."""
        limits = ResourceLimits(max_processing_time_seconds=10)
        monitor = ResourceMonitor(limits)
        
        start_time = time.time()
        
        # Should not raise exception (within 10 seconds)
        monitor.check_processing_time(start_time)
    
    def test_check_processing_time_raises_when_exceeded(self):
        """Test processing time check raises exception when exceeded."""
        limits = ResourceLimits(max_processing_time_seconds=0.1)
        monitor = ResourceMonitor(limits)
        
        start_time = time.time() - 1  # Started 1 second ago
        
        with pytest.raises(ResourceExceededError) as exc_info:
            monitor.check_processing_time(start_time)
        
        assert "processing time limit exceeded" in str(exc_info.value).lower()
    
    def test_check_result_count_passes_within_limit(self):
        """Test result count check passes when within limits."""
        limits = ResourceLimits(max_result_count=1000)
        monitor = ResourceMonitor(limits)
        
        # Should not raise exception
        monitor.check_result_count(500)
    
    def test_check_result_count_raises_when_exceeded(self):
        """Test result count check raises exception when exceeded."""
        limits = ResourceLimits(max_result_count=100)
        monitor = ResourceMonitor(limits)
        
        with pytest.raises(ResourceExceededError) as exc_info:
            monitor.check_result_count(500)
        
        assert "result count limit exceeded" in str(exc_info.value).lower()
    
    def test_monitor_operation_context_manager(self):
        """Test monitor_operation context manager."""
        limits = ResourceLimits(
            max_memory_mb=10000,  # High limits for test
            max_processing_time_seconds=10,
            max_result_count=1000
        )
        monitor = ResourceMonitor(limits)
        
        with monitor.monitor_operation() as operation_monitor:
            # Should provide methods for checking limits
            assert hasattr(operation_monitor, 'check_memory')
            assert hasattr(operation_monitor, 'check_time')
            assert hasattr(operation_monitor, 'check_result_count')
            
            # Should not raise exceptions within limits
            operation_monitor.check_memory()
            operation_monitor.check_time()
            operation_monitor.check_result_count(100)
    
    def test_monitor_operation_enforces_limits(self):
        """Test monitor_operation enforces resource limits."""
        limits = ResourceLimits(max_result_count=10)
        monitor = ResourceMonitor(limits)
        
        with pytest.raises(ResourceExceededError):
            with monitor.monitor_operation() as operation_monitor:
                operation_monitor.check_result_count(50)  # Exceeds limit


class TestResourceExceededError:
    """Test ResourceExceededError exception."""
    
    def test_resource_exceeded_error_initialization(self):
        """Test ResourceExceededError initialization."""
        error = ResourceExceededError("Test message", "memory", 1024, 512)
        
        assert str(error) == "Test message"
        assert error.resource_type == "memory"
        assert error.limit_value == 1024
        assert error.actual_value == 512
    
    def test_resource_exceeded_error_formatting(self):
        """Test ResourceExceededError provides helpful error messages."""
        error = ResourceExceededError(
            "Memory limit exceeded",
            "memory",
            limit_value=1024,
            actual_value=2048
        )
        
        error_str = str(error)
        assert "Memory limit exceeded" in error_str
        assert error.resource_type == "memory"
        assert error.limit_value == 1024
        assert error.actual_value == 2048