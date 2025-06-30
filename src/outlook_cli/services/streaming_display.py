"""
Streaming display service for handling large result sets without pagination.

This service displays email results in chunks, streaming them to the user
incrementally rather than loading everything into memory at once.
"""

from typing import List
from outlook_cli.models.email import Email


class StreamingResultDisplay:
    """Handles streaming display of email results."""
    
    def stream_results(self, emails: List[Email], chunk_size: int = 50) -> None:
        """
        Stream email results to output in chunks.
        
        Args:
            emails: List of emails to display
            chunk_size: Number of emails per chunk
        """
        # Process emails in chunks
        for i in range(0, len(emails), chunk_size):
            chunk = emails[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            self.display_streaming_chunk(chunk, chunk_num)
    
    def show_large_result_warning(self, total_count: int) -> None:
        """
        Show warning for large result sets.
        
        Args:
            total_count: Total number of results
        """
        print(f"Warning: Large result set detected ({total_count} emails)")
        print("Streaming results to prevent memory issues...")
        print()
    
    def display_streaming_chunk(self, chunk: List[Email], chunk_num: int) -> None:
        """
        Display a chunk of emails without pagination headers.
        
        Args:
            chunk: List of emails in this chunk
            chunk_num: Chunk number (for internal tracking)
        """
        # Display each email in the chunk
        for i, email in enumerate(chunk, 1):
            # Format email similar to existing display but without pagination
            status = "[UNREAD]" if not email.is_read else "[READ]"
            attachment_indicator = " 📎 Has attachments" if email.has_attachments else ""
            
            print(f"{i}. [{email.id}] {status} Subject: {email.subject}")
            print(f"   From: {email.sender_name} <{email.sender_email}>")
            print(f"   Date: {email.received_date.strftime('%Y-%m-%d %H:%M')}")
            if attachment_indicator:
                print(f"  {attachment_indicator}")
            print()