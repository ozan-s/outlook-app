"""Abstract OutlookAdapter interface.

This module defines the contract for all Outlook adapters, enabling
dependency injection and cross-platform development.
"""

from abc import ABC, abstractmethod
from typing import List
from outlook_cli.models import Email, Folder


class OutlookAdapter(ABC):
    """Abstract interface for Outlook operations.
    
    This class defines the contract that all Outlook adapters must implement,
    enabling dependency injection and supporting both mock and real implementations.
    """
    
    @abstractmethod
    def get_folders(self) -> List[Folder]:
        """Get all available folders.
        
        Returns:
            List[Folder]: All folders accessible through this adapter.
        """
        pass
    
    @abstractmethod
    def get_folder_info(self, folder_path: str) -> Folder:
        """Get information about a specific folder.
        
        Args:
            folder_path: The path to the folder (e.g., 'Inbox', 'Inbox/Subfolder').
            
        Returns:
            Folder: Information about the specified folder.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        pass
    
    @abstractmethod
    def get_emails(self, folder_path: str) -> List[Email]:
        """Get all emails from a specific folder.
        
        Args:
            folder_path: The path to the folder containing emails.
            
        Returns:
            List[Email]: All emails in the specified folder.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        pass
    
    @abstractmethod
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """Move an email to a different folder.
        
        Args:
            email_id: Unique identifier of the email to move.
            target_folder: Path to the destination folder.
            
        Returns:
            bool: True if the move was successful, False otherwise.
            
        Raises:
            ValueError: If email_id or target_folder does not exist.
        """
        pass