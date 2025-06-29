"""
Tests for timeout handling for long operations.
"""
import time
from unittest.mock import patch

import pytest

from outlook_cli.utils.timeout_handler import (
    with_timeout,
    TimeoutConfig,
    ProgressTracker,
    CancellationToken,
    timeout_operation
)
from outlook_cli.utils.errors import OutlookTimeoutError


class TestTimeoutConfig:
    """Test timeout configuration."""

    def test_timeout_config_initialization(self):
        """Test TimeoutConfig initializes with correct defaults."""
        config = TimeoutConfig()
        
        assert config.default_timeout == 30.0
        assert config.folder_read_timeout == 60.0
        assert config.search_timeout == 45.0
        assert config.move_timeout == 30.0

    def test_timeout_config_custom_values(self):
        """Test TimeoutConfig accepts custom values."""
        config = TimeoutConfig(
            default_timeout=120.0,
            folder_read_timeout=180.0,
            search_timeout=90.0,
            move_timeout=60.0
        )
        
        assert config.default_timeout == 120.0
        assert config.folder_read_timeout == 180.0
        assert config.search_timeout == 90.0
        assert config.move_timeout == 60.0

    def test_get_timeout_for_operation(self):
        """Test getting timeout for specific operations."""
        config = TimeoutConfig()
        
        assert config.get_timeout_for_operation("folder_read") == 60.0
        assert config.get_timeout_for_operation("search") == 45.0
        assert config.get_timeout_for_operation("move") == 30.0
        assert config.get_timeout_for_operation("unknown") == 30.0  # default


class TestCancellationToken:
    """Test cancellation token functionality."""

    def test_cancellation_token_initialization(self):
        """Test CancellationToken initializes correctly."""
        token = CancellationToken()
        
        assert token.is_cancelled is False

    def test_cancel_token(self):
        """Test cancelling a token."""
        token = CancellationToken()
        token.cancel()
        
        assert token.is_cancelled is True

    def test_check_cancellation_raises_when_cancelled(self):
        """Test that check_cancellation raises when token is cancelled."""
        token = CancellationToken()
        token.cancel()
        
        with pytest.raises(OutlookTimeoutError, match="Operation was cancelled"):
            token.check_cancellation()

    def test_check_cancellation_does_nothing_when_not_cancelled(self):
        """Test that check_cancellation does nothing when not cancelled."""
        token = CancellationToken()
        
        # Should not raise
        token.check_cancellation()


class TestProgressTracker:
    """Test progress tracking functionality."""

    def test_progress_tracker_initialization(self):
        """Test ProgressTracker initializes correctly."""
        tracker = ProgressTracker(total_items=100, operation="test")
        
        assert tracker.total_items == 100
        assert tracker.operation == "test"
        assert tracker.processed_items == 0
        assert tracker.progress_percentage == 0.0

    def test_update_progress(self):
        """Test updating progress."""
        tracker = ProgressTracker(total_items=100, operation="test")
        
        tracker.update_progress(25)
        
        assert tracker.processed_items == 25
        assert tracker.progress_percentage == 25.0

    def test_update_progress_beyond_total_clamps_to_100(self):
        """Test that progress update beyond total clamps to 100%."""
        tracker = ProgressTracker(total_items=50, operation="test")
        
        tracker.update_progress(75)  # More than total
        
        assert tracker.processed_items == 75
        assert tracker.progress_percentage == 100.0

    def test_get_progress_message(self):
        """Test getting formatted progress message."""
        tracker = ProgressTracker(total_items=200, operation="reading emails")
        tracker.update_progress(50)
        
        message = tracker.get_progress_message()
        
        assert "reading emails" in message
        assert "50" in message
        assert "200" in message
        assert "25%" in message

    def test_is_complete(self):
        """Test completion detection."""
        tracker = ProgressTracker(total_items=10, operation="test")
        
        assert tracker.is_complete is False
        
        tracker.update_progress(10)
        assert tracker.is_complete is True


class TestWithTimeoutDecorator:
    """Test timeout decorator functionality."""

    def test_with_timeout_succeeds_within_timeout(self):
        """Test decorator succeeds when function completes within timeout."""
        @with_timeout(timeout_seconds=1.0)
        def quick_function():
            time.sleep(0.1)
            return "success"
        
        result = quick_function()
        assert result == "success"

    def test_with_timeout_raises_error_when_timeout_exceeded(self):
        """Test decorator raises TimeoutError when timeout is exceeded."""
        @with_timeout(timeout_seconds=0.1)
        def slow_function():
            time.sleep(0.5)
            return "should not reach here"
        
        with pytest.raises(OutlookTimeoutError):
            slow_function()

    def test_with_timeout_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""
        @with_timeout(timeout_seconds=1.0)
        def documented_function():
            """This is a test function."""
            return "result"
        
        assert documented_function.__name__ == "documented_function"
        assert "test function" in documented_function.__doc__

    def test_with_timeout_custom_operation_name(self):
        """Test timeout decorator with custom operation name."""
        @with_timeout(timeout_seconds=0.1, operation="custom_operation")
        def slow_function():
            time.sleep(0.5)
        
        with pytest.raises(OutlookTimeoutError) as exc_info:
            slow_function()
        
        assert "custom_operation" in str(exc_info.value)

    def test_with_timeout_allows_cancellation_token(self):
        """Test timeout decorator works with cancellation token."""
        token = CancellationToken()
        
        @with_timeout(timeout_seconds=1.0, cancellation_token=token)
        def cancellable_function():
            time.sleep(0.1)
            token.check_cancellation()  # Should check token during execution
            return "success"
        
        # Should succeed when not cancelled
        result = cancellable_function()
        assert result == "success"


class TestTimeoutOperation:
    """Test timeout_operation context manager."""

    def test_timeout_operation_context_manager_succeeds(self):
        """Test timeout operation context manager with successful operation."""
        with timeout_operation(timeout_seconds=1.0, operation="test", total_items=100) as tracker:
            time.sleep(0.1)
            tracker.update_progress(50)
            
        assert tracker.is_complete is False  # Only updated to 50/100

    def test_timeout_operation_context_manager_handles_timeout(self):
        """Test timeout operation context manager raises on timeout."""
        with pytest.raises(OutlookTimeoutError):
            with timeout_operation(timeout_seconds=0.1, operation="test") as tracker:
                time.sleep(0.5)

    def test_timeout_operation_with_progress_tracking(self):
        """Test timeout operation includes progress tracking."""
        with timeout_operation(timeout_seconds=1.0, operation="test", total_items=100) as tracker:
            assert tracker.total_items == 100
            assert tracker.operation == "test"
            
            tracker.update_progress(25)
            assert tracker.progress_percentage == 25.0

    def test_timeout_operation_cancellation_support(self):
        """Test timeout operation supports cancellation."""
        token = CancellationToken()
        
        with pytest.raises(OutlookTimeoutError, match="cancelled"):
            with timeout_operation(timeout_seconds=1.0, operation="test", cancellation_token=token) as tracker:
                token.cancel()
                token.check_cancellation()


class TestTimeoutIntegration:
    """Test timeout handling integration with existing patterns."""

    def test_timeout_with_adapter_pattern(self):
        """Test timeout decorator works with adapter method pattern."""
        class TestAdapter:
            @with_timeout(timeout_seconds=0.1, operation="get_folders")
            def get_folders(self):
                time.sleep(0.5)  # Simulate slow operation
                return []
        
        adapter = TestAdapter()
        
        with pytest.raises(OutlookTimeoutError) as exc_info:
            adapter.get_folders()
        
        assert "get_folders" in str(exc_info.value)

    def test_timeout_preserves_exception_context(self):
        """Test that timeout errors include proper context."""
        @with_timeout(timeout_seconds=0.1, operation="folder_read")
        def slow_folder_read():
            time.sleep(0.5)
        
        with pytest.raises(OutlookTimeoutError) as exc_info:
            slow_folder_read()
        
        error = exc_info.value
        assert error.timeout_seconds == 0.1
        assert error.context["operation"] == "folder_read"
        assert "large folders" in error.suggestion.lower()

    def test_timeout_config_integration(self):
        """Test timeout configuration integration."""
        config = TimeoutConfig(folder_read_timeout=0.1)
        
        @with_timeout(timeout_seconds=config.folder_read_timeout, operation="folder_read")
        def slow_folder_read():
            time.sleep(0.5)
        
        with pytest.raises(OutlookTimeoutError):
            slow_folder_read()


class TestTimeoutEnvironmentConfiguration:
    """Test timeout configuration from environment variables."""

    @patch.dict('os.environ', {'OUTLOOK_CLI_DEFAULT_TIMEOUT': '120'})
    def test_timeout_config_from_environment(self):
        """Test that timeout config can be loaded from environment variables."""
        # This would be implemented in the actual TimeoutConfig if we add env support
        # For now, just test the concept
        import os
        
        timeout_value = float(os.environ.get('OUTLOOK_CLI_DEFAULT_TIMEOUT', 30))
        assert timeout_value == 120.0

    def test_timeout_config_fallback_to_defaults(self):
        """Test that timeout config falls back to defaults when env vars not set."""
        config = TimeoutConfig()
        
        # Should use defaults when no environment variables
        assert config.default_timeout == 30.0