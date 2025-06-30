"""Performance monitoring utilities for Outlook CLI operations."""

import time
import psutil
import threading
from dataclasses import dataclass
from typing import Dict, Optional, Any, Callable
from functools import wraps


@dataclass
class PerformanceMetrics:
    """Container for performance metrics data."""
    
    operation_name: str
    duration_seconds: float
    memory_used_mb: float
    peak_memory_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "operation_name": self.operation_name,
            "duration_seconds": self.duration_seconds,
            "memory_used_mb": self.memory_used_mb,
            "peak_memory_mb": self.peak_memory_mb
        }
    
    def __str__(self) -> str:
        """String representation of metrics."""
        return (f"PerformanceMetrics(operation_name={self.operation_name}, "
                f"duration_seconds={self.duration_seconds}, "
                f"memory_used_mb={self.memory_used_mb}, "
                f"peak_memory_mb={self.peak_memory_mb})")


class PerformanceMonitor:
    """Monitor performance metrics for Outlook CLI operations."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._completed_metrics: Dict[str, PerformanceMetrics] = {}
        self._lock = threading.Lock()
    
    def start_monitoring(self, operation_name: str) -> None:
        """Start monitoring a specific operation.
        
        Args:
            operation_name: Name of the operation to monitor
        """
        with self._lock:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            self._active_operations[operation_name] = {
                "start_time": time.time(),
                "start_memory": memory_info.rss / 1024 / 1024,  # Convert to MB
                "peak_memory": memory_info.rss / 1024 / 1024,
                "process": process
            }
    
    def stop_monitoring(self, operation_name: str) -> PerformanceMetrics:
        """Stop monitoring and return metrics.
        
        Args:
            operation_name: Name of the operation to stop monitoring
            
        Returns:
            PerformanceMetrics object with collected data
        """
        with self._lock:
            if operation_name not in self._active_operations:
                raise ValueError(f"Operation '{operation_name}' was not being monitored")
            
            operation_data = self._active_operations[operation_name]
            end_time = time.time()
            
            # Calculate duration
            duration = end_time - operation_data["start_time"]
            
            # Get current memory usage
            current_memory = operation_data["process"].memory_info().rss / 1024 / 1024
            memory_used = current_memory - operation_data["start_memory"]
            peak_memory = max(operation_data["peak_memory"], current_memory)
            
            # Create metrics
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                duration_seconds=duration,
                memory_used_mb=memory_used,
                peak_memory_mb=peak_memory
            )
            
            # Store and cleanup
            self._completed_metrics[operation_name] = metrics
            del self._active_operations[operation_name]
            
            return metrics
    
    def get_metrics(self, operation_name: str) -> Optional[PerformanceMetrics]:
        """Get stored metrics for a completed operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            PerformanceMetrics if available, None otherwise
        """
        return self._completed_metrics.get(operation_name)
    
    def monitor_performance(self, operation_name: str) -> Callable:
        """Decorator to monitor performance of a function.
        
        Args:
            operation_name: Name for the operation
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.start_monitoring(operation_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.stop_monitoring(operation_name)
            return wrapper
        return decorator