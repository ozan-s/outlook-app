"""
Tests for connection health monitoring.
"""

import pytest

from outlook_cli.utils.connection_monitor import (
    ConnectionMonitor,
    ConnectionStatus,
    monitor_connection,
    with_connection_retry
)
from outlook_cli.utils.errors import OutlookConnectionError


class TestConnectionStatus:
    """Test connection status enumeration."""

    def test_connection_status_values(self):
        """Test that all expected connection statuses exist."""
        assert ConnectionStatus.CONNECTED.value == "connected"
        assert ConnectionStatus.DISCONNECTED.value == "disconnected"
        assert ConnectionStatus.RECONNECTING.value == "reconnecting"
        assert ConnectionStatus.UNKNOWN.value == "unknown"


class TestConnectionMonitor:
    """Test connection monitoring functionality."""

    def test_connection_monitor_initialization(self):
        """Test ConnectionMonitor initializes with correct defaults."""
        monitor = ConnectionMonitor()
        
        assert monitor.status == ConnectionStatus.UNKNOWN
        assert monitor.max_retries == 3
        assert monitor.retry_delay == 1.0
        assert monitor.last_check_time is None

    def test_connection_monitor_custom_configuration(self):
        """Test ConnectionMonitor accepts custom configuration."""
        monitor = ConnectionMonitor(max_retries=5, retry_delay=2.0)
        
        assert monitor.max_retries == 5
        assert monitor.retry_delay == 2.0

    def test_check_connection_with_healthy_checker(self):
        """Test connection check with healthy connection."""
        def healthy_checker():
            return True
        
        monitor = ConnectionMonitor()
        status = monitor.check_connection(healthy_checker)
        
        assert status == ConnectionStatus.CONNECTED
        assert monitor.status == ConnectionStatus.CONNECTED
        assert monitor.last_check_time is not None

    def test_check_connection_with_unhealthy_checker(self):
        """Test connection check with unhealthy connection."""
        def unhealthy_checker():
            return False
        
        monitor = ConnectionMonitor()
        status = monitor.check_connection(unhealthy_checker)
        
        assert status == ConnectionStatus.DISCONNECTED
        assert monitor.status == ConnectionStatus.DISCONNECTED

    def test_check_connection_with_exception_in_checker(self):
        """Test connection check handles exceptions in checker function."""
        def failing_checker():
            raise Exception("Connection failed")
        
        monitor = ConnectionMonitor()
        status = monitor.check_connection(failing_checker)
        
        assert status == ConnectionStatus.DISCONNECTED
        assert monitor.status == ConnectionStatus.DISCONNECTED

    def test_attempt_reconnection_successful(self):
        """Test successful reconnection attempt."""
        # First call fails, second succeeds (simulating reconnection)
        call_count = 0
        def reconnecting_checker():
            nonlocal call_count
            call_count += 1
            return call_count > 1
        
        monitor = ConnectionMonitor(retry_delay=0.01)  # Fast retry for testing
        success = monitor.attempt_reconnection(reconnecting_checker)
        
        assert success is True
        assert monitor.status == ConnectionStatus.CONNECTED

    def test_attempt_reconnection_max_retries_exceeded(self):
        """Test reconnection fails after max retries."""
        def always_failing_checker():
            return False
        
        monitor = ConnectionMonitor(max_retries=2, retry_delay=0.01)
        success = monitor.attempt_reconnection(always_failing_checker)
        
        assert success is False
        assert monitor.status == ConnectionStatus.DISCONNECTED

    def test_attempt_reconnection_sets_reconnecting_status(self):
        """Test that reconnection process sets RECONNECTING status."""
        status_history = []
        
        def status_tracking_checker():
            status_history.append(monitor.status)
            return False  # Always fail to see status changes
        
        monitor = ConnectionMonitor(max_retries=1, retry_delay=0.01)
        monitor.attempt_reconnection(status_tracking_checker)
        
        # Should have set RECONNECTING status during the process
        assert ConnectionStatus.RECONNECTING in status_history

    def test_is_healthy_reflects_current_status(self):
        """Test is_healthy property reflects connection status."""
        monitor = ConnectionMonitor()
        
        # Initially unknown, should be False
        assert monitor.is_healthy is False
        
        # After successful check
        monitor.check_connection(lambda: True)
        assert monitor.is_healthy is True
        
        # After failed check
        monitor.check_connection(lambda: False)
        assert monitor.is_healthy is False

    def test_get_status_info_includes_timing(self):
        """Test get_status_info includes timing information."""
        monitor = ConnectionMonitor()
        monitor.check_connection(lambda: True)
        
        info = monitor.get_status_info()
        
        assert info["status"] == ConnectionStatus.CONNECTED.value
        assert info["is_healthy"] is True
        assert "last_check_time" in info
        assert info["last_check_time"] is not None


class TestConnectionDecorator:
    """Test connection monitoring decorator."""

    def test_monitor_connection_decorator_with_healthy_connection(self):
        """Test decorator works with healthy connection."""
        checker_calls = []
        
        def mock_checker():
            checker_calls.append("called")
            return True
        
        @monitor_connection(connection_checker=mock_checker)
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert len(checker_calls) == 1

    def test_monitor_connection_decorator_with_unhealthy_connection(self):
        """Test decorator raises error for unhealthy connection."""
        def failing_checker():
            return False
        
        @monitor_connection(connection_checker=failing_checker, max_retries=1, retry_delay=0.01)
        def test_function():
            return "success"
        
        with pytest.raises(OutlookConnectionError):
            test_function()

    def test_monitor_connection_decorator_with_reconnection_success(self):
        """Test decorator succeeds after reconnection."""
        call_count = 0
        
        def reconnecting_checker():
            nonlocal call_count
            call_count += 1
            return call_count > 2  # Fail first 2 times, succeed on 3rd
        
        @monitor_connection(connection_checker=reconnecting_checker, max_retries=3, retry_delay=0.01)
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count >= 3


class TestConnectionRetryDecorator:
    """Test connection retry decorator."""

    def test_with_connection_retry_succeeds_immediately(self):
        """Test retry decorator when function succeeds immediately."""
        call_count = 0
        
        @with_connection_retry(max_retries=3, retry_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert call_count == 1

    def test_with_connection_retry_succeeds_after_retries(self):
        """Test retry decorator when function succeeds after retries."""
        call_count = 0
        
        @with_connection_retry(max_retries=3, retry_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OutlookConnectionError("Connection failed")
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert call_count == 3

    def test_with_connection_retry_fails_after_max_retries(self):
        """Test retry decorator fails after max retries exceeded."""
        call_count = 0
        
        @with_connection_retry(max_retries=2, retry_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise OutlookConnectionError("Connection failed")
        
        with pytest.raises(OutlookConnectionError):
            test_function()
        
        assert call_count == 3  # Initial call + 2 retries

    def test_with_connection_retry_only_retries_connection_errors(self):
        """Test retry decorator only retries connection errors, not other exceptions."""
        call_count = 0
        
        @with_connection_retry(max_retries=3, retry_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not a connection error")
        
        with pytest.raises(ValueError):
            test_function()
        
        assert call_count == 1  # Should not retry non-connection errors


class TestIntegrationWithExistingAdapters:
    """Test integration with existing adapter patterns."""

    def test_connection_monitor_works_with_mock_adapter(self):
        """Test connection monitoring works with MockOutlookAdapter pattern."""
        
        def mock_checker():
            # Mock adapter is always "connected"
            return True
        
        monitor = ConnectionMonitor()
        status = monitor.check_connection(mock_checker)
        
        assert status == ConnectionStatus.CONNECTED

    def test_connection_monitor_interface_compatible_with_adapters(self):
        """Test that connection monitoring interface is compatible with adapter pattern."""
        # This test ensures our connection monitoring can be integrated into adapters
        
        def adapter_health_check():
            """Simulate adapter health check method."""
            try:
                # Simulate checking adapter connection
                return True
            except Exception:
                return False
        
        monitor = ConnectionMonitor()
        
        # Should be able to use adapter's health check method
        status = monitor.check_connection(adapter_health_check)
        assert status == ConnectionStatus.CONNECTED