"""
Timeout handling for long-running Outlook operations.
"""
import os
import time
import signal
import threading
import functools
from contextlib import contextmanager
from typing import Optional, Any

from .errors import OutlookTimeoutError
from .logging_config import get_logger

logger = get_logger(__name__)


class TimeoutConfig:
    """Configuration for operation timeouts."""
    
    def __init__(
        self,
        default_timeout: float = 30.0,
        folder_read_timeout: float = 60.0,
        search_timeout: float = 45.0,
        move_timeout: float = 30.0
    ):
        """
        Initialize timeout configuration.
        
        Args:
            default_timeout: Default timeout for operations
            folder_read_timeout: Timeout for folder reading operations
            search_timeout: Timeout for search operations
            move_timeout: Timeout for move operations
        """
        # Allow environment variable overrides
        self.default_timeout = float(os.environ.get('OUTLOOK_CLI_DEFAULT_TIMEOUT', default_timeout))
        self.folder_read_timeout = float(os.environ.get('OUTLOOK_CLI_FOLDER_READ_TIMEOUT', folder_read_timeout))
        self.search_timeout = float(os.environ.get('OUTLOOK_CLI_SEARCH_TIMEOUT', search_timeout))
        self.move_timeout = float(os.environ.get('OUTLOOK_CLI_MOVE_TIMEOUT', move_timeout))

    def get_timeout_for_operation(self, operation: str) -> float:
        """
        Get timeout for specific operation type.
        
        Args:
            operation: Name of the operation
            
        Returns:
            Timeout in seconds
        """
        timeout_map = {
            "folder_read": self.folder_read_timeout,
            "search": self.search_timeout,
            "move": self.move_timeout,
        }
        
        return timeout_map.get(operation, self.default_timeout)


class CancellationToken:
    """Token for cancelling long-running operations."""
    
    def __init__(self):
        """Initialize cancellation token."""
        self.is_cancelled = False

    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True
        logger.debug("Operation cancelled via cancellation token")

    def check_cancellation(self):
        """Check if operation was cancelled and raise if so."""
        if self.is_cancelled:
            raise OutlookTimeoutError("Operation was cancelled")


class ProgressTracker:
    """Track progress of long-running operations."""
    
    def __init__(self, total_items: int, operation: str):
        """
        Initialize progress tracker.
        
        Args:
            total_items: Total number of items to process
            operation: Description of the operation
        """
        self.total_items = total_items
        self.operation = operation
        self.processed_items = 0

    def update_progress(self, processed_items: int):
        """
        Update progress with number of processed items.
        
        Args:
            processed_items: Number of items processed so far
        """
        self.processed_items = processed_items
        logger.debug(f"{self.operation}: {processed_items}/{self.total_items} items processed")

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.total_items == 0:
            return 100.0
        return min(100.0, (self.processed_items / self.total_items) * 100.0)

    @property
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.processed_items >= self.total_items

    def get_progress_message(self) -> str:
        """Get formatted progress message."""
        percentage = int(self.progress_percentage) if self.progress_percentage == int(self.progress_percentage) else f"{self.progress_percentage:.1f}"
        return f"{self.operation}: {self.processed_items}/{self.total_items} ({percentage}%)"


def with_timeout(
    timeout_seconds: float,
    operation: str = "operation",
    cancellation_token: Optional[CancellationToken] = None
):
    """
    Decorator to add timeout handling to functions.
    
    Args:
        timeout_seconds: Maximum time to allow for execution
        operation: Name of the operation (for error messages)
        cancellation_token: Optional cancellation token
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            # Check cancellation if token provided
            if cancellation_token:
                cancellation_token.check_cancellation()
            
            # Start function in a thread
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                # Thread is still running, timeout occurred
                raise OutlookTimeoutError(
                    f"{operation} timed out",
                    timeout_seconds=timeout_seconds,
                    context={"operation": operation}
                )
            
            # Check if function raised an exception
            if exception[0] is not None:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator


@contextmanager
def timeout_operation(
    timeout_seconds: float,
    operation: str,
    total_items: Optional[int] = None,
    cancellation_token: Optional[CancellationToken] = None
):
    """
    Context manager for timeout operations with progress tracking.
    
    Args:
        timeout_seconds: Maximum time to allow for execution
        operation: Name of the operation
        total_items: Total number of items (for progress tracking)
        cancellation_token: Optional cancellation token
        
    Yields:
        ProgressTracker instance
    """
    # Create progress tracker
    if total_items is None:
        total_items = 0
    tracker = ProgressTracker(total_items, operation)
    
    start_time = time.time()
    
    def check_timeout():
        if time.time() - start_time > timeout_seconds:
            raise OutlookTimeoutError(
                f"{operation} timed out",
                timeout_seconds=timeout_seconds,
                context={"operation": operation}
            )
    
    try:
        # Check cancellation if token provided
        if cancellation_token:
            cancellation_token.check_cancellation()
        
        logger.info(f"Starting {operation} with {timeout_seconds}s timeout")
        
        # Create a timeout checking thread
        timeout_thread = threading.Thread(target=lambda: None)
        timeout_thread.daemon = True
        
        yield tracker
        
        # Check timeout after context block
        check_timeout()
        
        logger.info(f"Completed {operation}")
        
    except Exception as e:
        # Re-raise any exceptions (including timeouts)
        raise