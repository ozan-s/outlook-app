"""Tests for PerformanceMonitor utility."""

import pytest
import time
import psutil
from unittest.mock import patch, MagicMock
from outlook_cli.utils.performance_monitor import PerformanceMonitor, PerformanceMetrics


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    def test_performance_monitor_initialization(self):
        """Test that PerformanceMonitor initializes correctly."""
        monitor = PerformanceMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'stop_monitoring')
        assert hasattr(monitor, 'get_metrics')
    
    def test_performance_metrics_captures_timing_data(self):
        """Test that performance monitoring captures timing data."""
        monitor = PerformanceMonitor()
        
        # Start monitoring
        monitor.start_monitoring("test_operation")
        
        # Simulate some work
        time.sleep(0.1)
        
        # Stop monitoring
        metrics = monitor.stop_monitoring("test_operation")
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.operation_name == "test_operation"
        assert metrics.duration_seconds >= 0.1
        assert metrics.duration_seconds < 0.2  # Should be close to 0.1
    
    def test_performance_metrics_captures_memory_usage(self):
        """Test that performance monitoring captures memory usage."""
        monitor = PerformanceMonitor()
        
        # Start monitoring
        monitor.start_monitoring("memory_test")
        
        # Allocate some memory
        large_list = [i for i in range(10000)]
        
        # Stop monitoring
        metrics = monitor.stop_monitoring("memory_test")
        
        assert metrics.memory_used_mb > 0
        assert metrics.peak_memory_mb >= metrics.memory_used_mb
        assert large_list  # Keep reference to prevent optimization
    
    def test_performance_monitor_decorator_captures_metrics(self):
        """Test that the performance monitoring decorator works."""
        monitor = PerformanceMonitor()
        
        @monitor.monitor_performance("decorated_function")
        def test_function():
            time.sleep(0.05)
            return "result"
        
        result = test_function()
        
        assert result == "result"
        # Metrics should be stored internally
        metrics = monitor.get_metrics("decorated_function")
        assert metrics is not None
        assert metrics.operation_name == "decorated_function"
        assert metrics.duration_seconds >= 0.05
    
    def test_performance_monitor_handles_multiple_operations(self):
        """Test that monitor can handle multiple concurrent operations."""
        monitor = PerformanceMonitor()
        
        # Start multiple operations
        monitor.start_monitoring("op1")
        monitor.start_monitoring("op2")
        
        time.sleep(0.05)
        
        # Stop in different order
        metrics2 = monitor.stop_monitoring("op2")
        metrics1 = monitor.stop_monitoring("op1")
        
        assert metrics1.operation_name == "op1"
        assert metrics2.operation_name == "op2"
        assert metrics1.duration_seconds >= 0.05
        assert metrics2.duration_seconds >= 0.05


class TestPerformanceMetrics:
    """Test PerformanceMetrics data class."""
    
    def test_performance_metrics_initialization(self):
        """Test PerformanceMetrics initialization."""
        metrics = PerformanceMetrics(
            operation_name="test",
            duration_seconds=1.5,
            memory_used_mb=10.0,
            peak_memory_mb=15.0
        )
        
        assert metrics.operation_name == "test"
        assert metrics.duration_seconds == 1.5
        assert metrics.memory_used_mb == 10.0
        assert metrics.peak_memory_mb == 15.0
    
    def test_performance_metrics_to_dict(self):
        """Test that PerformanceMetrics can be converted to dictionary."""
        metrics = PerformanceMetrics(
            operation_name="test",
            duration_seconds=1.5,
            memory_used_mb=10.0,
            peak_memory_mb=15.0
        )
        
        result = metrics.to_dict()
        
        expected = {
            "operation_name": "test",
            "duration_seconds": 1.5,
            "memory_used_mb": 10.0,
            "peak_memory_mb": 15.0
        }
        assert result == expected
    
    def test_performance_metrics_string_representation(self):
        """Test string representation of PerformanceMetrics."""
        metrics = PerformanceMetrics(
            operation_name="test_op",
            duration_seconds=2.34,
            memory_used_mb=25.6,
            peak_memory_mb=30.1
        )
        
        result = str(metrics)
        
        assert "test_op" in result
        assert "2.34" in result
        assert "25.6" in result
        assert "30.1" in result