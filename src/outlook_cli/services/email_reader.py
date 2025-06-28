"""EmailReader service for retrieving emails from folders."""

from typing import List, Dict
from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.models.email import Email


class EmailReader:
    """Service for reading emails from folders via OutlookAdapter."""
    
    def __init__(self, adapter: OutlookAdapter):
        """Initialize EmailReader with an OutlookAdapter.
        
        Args:
            adapter: OutlookAdapter instance for email operations.
        """
        self._adapter = adapter
    
    def get_emails_from_folder(self, folder_path: str) -> List[Email]:
        """Get all emails from a specific folder.
        
        Args:
            folder_path: Path to the folder (e.g., 'Inbox', 'Sent Items').
            
        Returns:
            List[Email]: All emails in the specified folder.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        return self._adapter.get_emails(folder_path)
    
    def get_all_emails(self) -> Dict[str, List[Email]]:
        """Get all emails from all folders.
        
        Returns:
            Dict[str, List[Email]]: Dictionary mapping folder paths to their emails.
        """
        folders = self._adapter.get_folders()
        return {folder.path: self._adapter.get_emails(folder.path) for folder in folders}