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
    
    def search_emails(self, sender: Optional[str] = None, subject: Optional[str] = None, folder_path: Optional[str] = None, since: Optional['datetime'] = None, until: Optional['datetime'] = None, is_read: Optional[bool] = None, is_unread: Optional[bool] = None, has_attachment: Optional[bool] = None, no_attachment: Optional[bool] = None, importance: Optional[str] = None, not_sender: Optional[str] = None, not_subject: Optional[str] = None) -> List[Email]:
        """Search emails by multiple criteria with AND logic.
        
        Args:
            sender: Optional sender email address or display name (case-insensitive).
            subject: Optional subject keywords (case-insensitive, partial match).
            folder_path: Optional folder to search in. If None, searches all folders.
            since: Optional start date (inclusive) - emails received on or after this date.
            until: Optional end date (inclusive) - emails received on or before this date.
            is_read: If True, return only read emails.
            is_unread: If True, return only unread emails.
            has_attachment: If True, return only emails with attachments.
            no_attachment: If True, return only emails without attachments.
            importance: Filter by importance level ("high", "normal", "low") (case-insensitive).
            not_sender: Exclude emails from this sender (case-insensitive partial match).
            not_subject: Exclude emails with this text in subject (case-insensitive partial match).
            
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
        
        # Apply existing filters
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
        
        # Apply new filter methods
        filtered_emails = self.filter_by_read_status(filtered_emails, is_read, is_unread)
        filtered_emails = self.filter_by_attachments(filtered_emails, has_attachment, no_attachment)
        filtered_emails = self.filter_by_importance(filtered_emails, importance)
        filtered_emails = self.filter_by_exclusions(filtered_emails, not_sender, not_subject)
        
        return filtered_emails
    
    def filter_by_read_status(self, emails: List[Email], is_read: Optional[bool] = None, is_unread: Optional[bool] = None) -> List[Email]:
        """Filter emails by read status.
        
        Args:
            emails: List of emails to filter.
            is_read: If True, return only read emails.
            is_unread: If True, return only unread emails.
            
        Returns:
            List[Email]: Filtered emails based on read status.
        """
        if is_read:
            return [email for email in emails if email.is_read]
        elif is_unread:
            return [email for email in emails if not email.is_read]
        else:
            return emails
    
    def filter_by_attachments(self, emails: List[Email], has_attachment: Optional[bool] = None, no_attachment: Optional[bool] = None) -> List[Email]:
        """Filter emails by attachment status.
        
        Args:
            emails: List of emails to filter.
            has_attachment: If True, return only emails with attachments.
            no_attachment: If True, return only emails without attachments.
            
        Returns:
            List[Email]: Filtered emails based on attachment status.
        """
        if has_attachment:
            return [email for email in emails if email.has_attachments]
        elif no_attachment:
            return [email for email in emails if not email.has_attachments]
        else:
            return emails
    
    def filter_by_importance(self, emails: List[Email], importance: Optional[str] = None) -> List[Email]:
        """Filter emails by importance level.
        
        Args:
            emails: List of emails to filter.
            importance: Importance level ("high", "normal", "low") (case-insensitive).
            
        Returns:
            List[Email]: Filtered emails based on importance level.
        """
        if importance:
            importance_title_case = importance.title()  # Convert "high" -> "High"
            return [email for email in emails if email.importance == importance_title_case]
        else:
            return emails
    
    def filter_by_exclusions(self, emails: List[Email], not_sender: Optional[str] = None, not_subject: Optional[str] = None) -> List[Email]:
        """Filter out emails matching exclusion criteria.
        
        Args:
            emails: List of emails to filter.
            not_sender: Exclude emails from this sender (case-insensitive partial match).
            not_subject: Exclude emails with this text in subject (case-insensitive partial match).
            
        Returns:
            List[Email]: Filtered emails with exclusions applied.
        """
        filtered_emails = emails
        
        if not_sender:
            not_sender_lower = not_sender.lower()
            filtered_emails = [
                email for email in filtered_emails
                if not_sender_lower not in email.sender_email.lower() 
                and not_sender_lower not in email.sender_name.lower()
            ]
        
        if not_subject:
            not_subject_lower = not_subject.lower()
            filtered_emails = [
                email for email in filtered_emails
                if not_subject_lower not in email.subject.lower()
            ]
        
        return filtered_emails