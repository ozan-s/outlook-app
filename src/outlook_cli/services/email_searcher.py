"""EmailSearcher service for filtering emails by various criteria."""

from typing import List, Optional
from datetime import datetime
from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.models.email import Email
from outlook_cli.services.email_reader import EmailReader


class EmailSearcher:
    """Service for searching emails by sender, subject, and other criteria."""
    
    def __init__(self, adapter: OutlookAdapter):
        """Initialize EmailSearcher with an OutlookAdapter.
        
        Args:
            adapter: OutlookAdapter instance for email operations.
        """
        self._adapter = adapter
        self._email_reader = EmailReader(adapter)
    
    def search_by_sender(self, sender: str, folder_path: Optional[str] = None) -> List[Email]:
        """Search emails by sender email address or display name.
        
        Args:
            sender: Sender email address or display name to search for (case-insensitive).
            folder_path: Optional folder to search in. If None, searches all folders.
            
        Returns:
            List[Email]: Emails matching the sender criteria.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        # Get emails from specific folder or all folders
        if folder_path:
            emails = self._email_reader.get_emails_from_folder(folder_path)
        else:
            all_emails = self._email_reader.get_all_emails()
            emails = [email for folder_emails in all_emails.values() for email in folder_emails]
        
        # Filter by sender (case-insensitive, match email or display name)
        sender_lower = sender.lower()
        return [
            email for email in emails
            if sender_lower in email.sender_email.lower() or sender_lower in email.sender_name.lower()
        ]
    
    def search_by_subject(self, subject: str, folder_path: Optional[str] = None) -> List[Email]:
        """Search emails by subject keywords (partial, case-insensitive).
        
        Args:
            subject: Subject keywords to search for (case-insensitive, partial match).
            folder_path: Optional folder to search in. If None, searches all folders.
            
        Returns:
            List[Email]: Emails matching the subject criteria.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        # Get emails from specific folder or all folders
        if folder_path:
            emails = self._email_reader.get_emails_from_folder(folder_path)
        else:
            all_emails = self._email_reader.get_all_emails()
            emails = [email for folder_emails in all_emails.values() for email in folder_emails]
        
        # Filter by subject (case-insensitive partial match)
        subject_lower = subject.lower()
        return [
            email for email in emails
            if subject_lower in email.subject.lower()
        ]
    
    def search_emails(self, sender: Optional[str] = None, subject: Optional[str] = None, folder_path: Optional[str] = None, since: Optional['datetime'] = None, until: Optional['datetime'] = None) -> List[Email]:
        """Search emails by multiple criteria with AND logic.
        
        Args:
            sender: Optional sender email address or display name (case-insensitive).
            subject: Optional subject keywords (case-insensitive, partial match).
            folder_path: Optional folder to search in. If None, searches all folders.
            since: Optional start date (inclusive) - emails received on or after this date.
            until: Optional end date (inclusive) - emails received on or before this date.
            
        Returns:
            List[Email]: Emails matching ALL specified criteria.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        # Get emails from specific folder or all folders
        if folder_path:
            emails = self._email_reader.get_emails_from_folder(folder_path)
        else:
            all_emails = self._email_reader.get_all_emails()
            emails = [email for folder_emails in all_emails.values() for email in folder_emails]
        
        # Apply filters with AND logic
        filtered_emails = emails
        
        if sender:
            sender_lower = sender.lower()
            filtered_emails = [
                email for email in filtered_emails
                if sender_lower in email.sender_email.lower() or sender_lower in email.sender_name.lower()
            ]
        
        if subject:
            subject_lower = subject.lower()
            filtered_emails = [
                email for email in filtered_emails
                if subject_lower in email.subject.lower()
            ]
        
        if since:
            filtered_emails = [
                email for email in filtered_emails
                if email.received_date >= since
            ]
        
        if until:
            filtered_emails = [
                email for email in filtered_emails
                if email.received_date <= until
            ]
        
        return filtered_emails