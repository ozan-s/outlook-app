"""
Streaming paginator service for handling large result sets in chunks.

This service provides iterator-based chunking of email results with
memory monitoring capabilities.
"""

from typing import List, Iterator
from outlook_cli.models.email import Email
from outlook_cli.utils.resource_monitor import ResourceMonitor


class StreamingPaginator:
    """Handles chunked iteration of email results for streaming display."""
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
    
    def stream_all_results(self, items: List[Email], chunk_size: int = None) -> Iterator[List[Email]]:
        """
        Stream all results in chunks with memory monitoring.
        
        Args:
            items: List of emails to stream
            chunk_size: Number of emails per chunk (uses get_chunk_size() if None)
            
        Yields:
            List[Email]: Chunks of emails
        """
        if chunk_size is None:
            chunk_size = self.get_chunk_size()
        
        # Process in chunks
        for i in range(0, len(items), chunk_size):
            # Check memory usage before processing chunk
            self.resource_monitor.check_memory_usage()
            
            chunk = items[i:i + chunk_size]
            yield chunk
    
    def get_chunk_size(self) -> int:
        """
        Get the optimal chunk size for streaming.
        
        Returns:
            int: Optimal chunk size (default 50)
        """
        return 50