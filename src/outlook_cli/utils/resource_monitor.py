"""Resource monitoring and limits for Outlook CLI operations."""

import os
import time
import psutil
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional


class ResourceExceededError(Exception):
    """Exception raised when resource limits are exceeded."""
    
    def __init__(self, message: str, resource_type: str, 
                 limit_value: Optional[float] = None, 
                 actual_value: Optional[float] = None):
        """Initialize ResourceExceededError.
        
        Args:
            message: Error message
            resource_type: Type of resource that was exceeded
            limit_value: The configured limit
            actual_value: The actual value that exceeded the limit
        """
        super().__init__(message)
        self.resource_type = resource_type
        self.limit_value = limit_value
        self.actual_value = actual_value


@dataclass
class ResourceLimits:
    """Configuration for resource limits."""
    
    max_memory_mb: float
    max_processing_time_seconds: float
    max_result_count: int
    
    def __init__(self, 
                 max_memory_mb: Optional[float] = None,
                 max_processing_time_seconds: Optional[float] = None,
                 max_result_count: Optional[int] = None):
        """Initialize ResourceLimits with defaults from environment.
        
        Args:
            max_memory_mb: Maximum memory usage in MB
            max_processing_time_seconds: Maximum processing time in seconds
            max_result_count: Maximum number of results to process
        """
        # Set defaults or use environment variables
        self.max_memory_mb = (
            max_memory_mb if max_memory_mb is not None 
            else float(os.environ.get('OUTLOOK_CLI_MAX_MEMORY_MB', '1024'))
        )
        self.max_processing_time_seconds = (
            max_processing_time_seconds if max_processing_time_seconds is not None
            else float(os.environ.get('OUTLOOK_CLI_MAX_PROCESSING_TIME', '300'))
        )
        self.max_result_count = (
            max_result_count if max_result_count is not None
            else int(os.environ.get('OUTLOOK_CLI_MAX_RESULT_COUNT', '50000'))
        )


class OperationMonitor:
    """Monitor for a single operation."""
    
    def __init__(self, resource_monitor: 'ResourceMonitor', start_time: float):
        """Initialize operation monitor.
        
        Args:
            resource_monitor: Parent ResourceMonitor instance
            start_time: When the operation started
        """
        self._resource_monitor = resource_monitor
        self._start_time = start_time
    
    def check_memory(self) -> None:
        """Check current memory usage against limits."""
        self._resource_monitor.check_memory_usage()
    
    def check_time(self) -> None:
        """Check current processing time against limits."""
        self._resource_monitor.check_processing_time(self._start_time)
    
    def check_result_count(self, count: int) -> None:
        """Check result count against limits.
        
        Args:
            count: Number of results processed so far
        """
        self._resource_monitor.check_result_count(count)


class ResourceMonitor:
    """Monitor and enforce resource limits for operations."""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        """Initialize ResourceMonitor.
        
        Args:
            limits: ResourceLimits configuration. If None, uses defaults.
        """
        self._limits = limits or ResourceLimits()
        self._process = psutil.Process()
    
    def check_memory_usage(self) -> None:
        """Check current memory usage against limits.
        
        Raises:
            ResourceExceededError: If memory limit is exceeded
        """
        memory_info = self._process.memory_info()
        current_memory_mb = memory_info.rss / 1024 / 1024
        
        if current_memory_mb > self._limits.max_memory_mb:
            raise ResourceExceededError(
                f"Memory limit exceeded: {current_memory_mb:.1f}MB > {self._limits.max_memory_mb}MB",
                resource_type="memory",
                limit_value=self._limits.max_memory_mb,
                actual_value=current_memory_mb
            )
    
    def check_processing_time(self, start_time: float) -> None:
        """Check processing time against limits.
        
        Args:
            start_time: When the operation started (from time.time())
            
        Raises:
            ResourceExceededError: If processing time limit is exceeded
        """
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if elapsed_time > self._limits.max_processing_time_seconds:
            raise ResourceExceededError(
                f"Processing time limit exceeded: {elapsed_time:.1f}s > {self._limits.max_processing_time_seconds}s",
                resource_type="processing_time",
                limit_value=self._limits.max_processing_time_seconds,
                actual_value=elapsed_time
            )
    
    def check_result_count(self, count: int) -> None:
        """Check result count against limits.
        
        Args:
            count: Number of results
            
        Raises:
            ResourceExceededError: If result count limit is exceeded
        """
        if count > self._limits.max_result_count:
            raise ResourceExceededError(
                f"Result count limit exceeded: {count} > {self._limits.max_result_count}",
                resource_type="result_count",
                limit_value=self._limits.max_result_count,
                actual_value=count
            )
    
    @contextmanager
    def monitor_operation(self):
        """Context manager for monitoring an operation.
        
        Yields:
            OperationMonitor instance for checking limits during operation
        """
        start_time = time.time()
        operation_monitor = OperationMonitor(self, start_time)
        
        try:
            yield operation_monitor
        finally:
            # Final checks when operation completes
            pass