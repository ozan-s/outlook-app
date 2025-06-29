"""EmailMover service for moving emails between folders."""

from typing import List, Dict
from outlook_cli.adapters.outlook_adapter import OutlookAdapter


class EmailMover:
    """Service for moving emails between folders via OutlookAdapter."""
    
    def __init__(self, adapter: OutlookAdapter):
        """Initialize EmailMover with an OutlookAdapter.
        
        Args:
            adapter: OutlookAdapter instance for email operations.
        """
        self._adapter = adapter
    
    def move_email_to_folder(self, email_id: str, target_folder: str) -> bool:
        """Move a single email to the target folder.
        
        Args:
            email_id: The unique identifier of the email to move.
            target_folder: The path of the target folder.
            
        Returns:
            bool: True if the email was moved successfully.
            
        Raises:
            ValueError: If the email_id is not found or target_folder doesn't exist.
        """
        return self._adapter.move_email(email_id, target_folder)
    
    def move_multiple_emails(self, email_ids: List[str], target_folder: str) -> Dict[str, bool]:
        """Move multiple emails to the target folder.
        
        Args:
            email_ids: List of email IDs to move.
            target_folder: The path of the target folder.
            
        Returns:
            Dict[str, bool]: Dictionary mapping email_id to success status.
        """
        results = {}
        
        for email_id in email_ids:
            try:
                success = self._adapter.move_email(email_id, target_folder)
                results[email_id] = success
            except ValueError:
                # Handle individual failures gracefully
                results[email_id] = False
        
        return results