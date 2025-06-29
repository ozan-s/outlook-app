"""
Connection health monitoring for Outlook operations.
"""
import time
import functools
from enum import Enum
from typing import Callable, Dict, Any, Optional

from .errors import OutlookConnectionError
from .logging_config import get_logger

logger = get_logger(__name__)


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"  
    RECONNECTING = "reconnecting"
    UNKNOWN = "unknown"


class ConnectionMonitor:
    """
    Monitor and manage connection health with auto-reconnection capabilities.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize connection monitor.
        
        Args:
            max_retries: Maximum number of reconnection attempts
            retry_delay: Delay between reconnection attempts in seconds
        """
        self.status = ConnectionStatus.UNKNOWN
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_check_time: Optional[float] = None

    def check_connection(self, connection_checker: Callable[[], bool]) -> ConnectionStatus:
        """
        Check connection health using provided checker function.
        
        Args:
            connection_checker: Function that returns True if connection is healthy
            
        Returns:
            Current connection status
        """
        self.last_check_time = time.time()
        
        try:
            is_healthy = connection_checker()
            self.status = ConnectionStatus.CONNECTED if is_healthy else ConnectionStatus.DISCONNECTED
            
            if self.status == ConnectionStatus.CONNECTED:
                logger.debug("Connection check successful")
            else:
                logger.warning("Connection check failed - connection is unhealthy")
                
        except Exception as e:
            logger.error(f"Connection check failed with exception: {e}")
            self.status = ConnectionStatus.DISCONNECTED
            
        return self.status

    def attempt_reconnection(self, connection_checker: Callable[[], bool]) -> bool:
        """
        Attempt to reconnect with exponential backoff.
        
        Args:
            connection_checker: Function that returns True if connection is healthy
            
        Returns:
            True if reconnection successful, False otherwise
        """
        logger.info(f"Attempting reconnection (max {self.max_retries} retries)")
        
        for attempt in range(self.max_retries):
            self.status = ConnectionStatus.RECONNECTING
            logger.debug(f"Reconnection attempt {attempt + 1}/{self.max_retries}")
            
            # Wait before retry (with exponential backoff)
            if attempt > 0:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.debug(f"Waiting {delay}s before retry")
                time.sleep(delay)
            
            # Try to reconnect
            try:
                if connection_checker():
                    self.status = ConnectionStatus.CONNECTED
                    logger.info("Reconnection successful")
                    return True
            except Exception as e:
                logger.debug(f"Reconnection attempt {attempt + 1} failed: {e}")
        
        # All attempts failed
        self.status = ConnectionStatus.DISCONNECTED
        logger.error(f"All {self.max_retries} reconnection attempts failed")
        return False

    @property
    def is_healthy(self) -> bool:
        """Check if connection is currently healthy."""
        return self.status == ConnectionStatus.CONNECTED

    def get_status_info(self) -> Dict[str, Any]:
        """
        Get detailed status information.
        
        Returns:
            Dictionary with status details
        """
        return {
            "status": self.status.value,
            "is_healthy": self.is_healthy,
            "last_check_time": self.last_check_time,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }


def monitor_connection(
    connection_checker: Callable[[], bool],
    max_retries: int = 3,
    retry_delay: float = 1.0
):
    """
    Decorator to monitor connection health before function execution.
    
    Args:
        connection_checker: Function that returns True if connection is healthy
        max_retries: Maximum number of reconnection attempts
        retry_delay: Delay between reconnection attempts
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = ConnectionMonitor(max_retries=max_retries, retry_delay=retry_delay)
            
            # Check connection health
            status = monitor.check_connection(connection_checker)
            
            if status == ConnectionStatus.DISCONNECTED:
                # Try to reconnect
                if not monitor.attempt_reconnection(connection_checker):
                    raise OutlookConnectionError(
                        f"Connection failed after {max_retries} reconnection attempts"
                    )
            
            # Connection is healthy, proceed with function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def with_connection_retry(max_retries: int = 3, retry_delay: float = 1.0):
    """
    Decorator to retry function on connection errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retry attempts
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                    
                except OutlookConnectionError as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"Connection error on attempt {attempt + 1}, retrying: {e}")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Function failed after {max_retries + 1} attempts")
                        raise
                        
                except Exception:
                    # Don't retry non-connection errors
                    raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator