"""Mock implementation of OutlookAdapter for testing."""

from typing import List, Dict
from datetime import datetime, timezone, timedelta
from outlook_cli.models import Email, Folder
from .outlook_adapter import OutlookAdapter


class MockOutlookAdapter(OutlookAdapter):
    """Mock implementation of OutlookAdapter for testing."""
    
    def __init__(self):
        """Initialize mock adapter with realistic test data."""
        self._folders = [
            Folder(path="Inbox", name="Inbox", email_count=25, unread_count=5),
            Folder(path="Sent Items", name="Sent Items", email_count=120, unread_count=0),
            Folder(path="Drafts", name="Drafts", email_count=3, unread_count=3),
            Folder(path="Deleted Items", name="Deleted Items", email_count=42, unread_count=0),
            Folder(path="Custom/Projects", name="Projects", email_count=15, unread_count=2),
            Folder(path="Custom/Archive", name="Archive", email_count=200, unread_count=0),
        ]
        
        # Create test emails for different folders
        self._emails = self._create_test_emails()
    
    def _create_test_emails(self) -> Dict[str, List[Email]]:
        """Create realistic test emails for different folders."""
        emails = {}
        
        # Inbox emails
        emails["Inbox"] = [
            Email(
                id="inbox-001",
                subject="Weekly Team Meeting",
                sender_email="manager@company.com",
                sender_name="Alice Manager",
                recipient_emails=["user@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(hours=2),
                body_text="Hi team, our weekly meeting is scheduled for Friday at 2 PM.",
                folder_path="Inbox",
                has_attachments=False,
                is_read=False,
                importance="High"
            ),
            Email(
                id="inbox-002",
                subject="Project Update Required",
                sender_email="pm@company.com",
                sender_name="Bob ProjectManager",
                recipient_emails=["user@company.com", "team@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(days=1),
                body_text="Please provide an update on the current project status.",
                folder_path="Inbox",
                has_attachments=True,
                attachment_count=2,
                is_read=True
            ),
            Email(
                id="inbox-003",
                subject="System Maintenance Notice",
                sender_email="it@company.com",
                sender_name="IT Support",
                recipient_emails=["all@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(days=2),
                body_text="The system will be down for maintenance this weekend.",
                folder_path="Inbox",
                has_attachments=False,
                is_read=True
            )
        ]
        
        # Sent Items emails
        emails["Sent Items"] = [
            Email(
                id="sent-001",
                subject="Re: Project Update Required",
                sender_email="user@company.com",
                sender_name="Current User",
                recipient_emails=["pm@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(hours=6),
                body_text="The project is on track and will be completed by Friday.",
                folder_path="Sent Items",
                has_attachments=False,
                is_read=True
            ),
            Email(
                id="sent-002",
                subject="Meeting Notes",
                sender_email="user@company.com",
                sender_name="Current User",
                recipient_emails=["team@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(days=3),
                body_text="Here are the notes from yesterday's meeting.",
                folder_path="Sent Items",
                has_attachments=True,
                attachment_count=1,
                is_read=True
            )
        ]
        
        # Drafts emails
        emails["Drafts"] = [
            Email(
                id="draft-001",
                subject="Vacation Request",
                sender_email="user@company.com",
                sender_name="Current User",
                recipient_emails=["hr@company.com"],
                received_date=datetime.now(timezone.utc) - timedelta(hours=12),
                body_text="I would like to request vacation time for next month.",
                folder_path="Drafts",
                has_attachments=False,
                is_read=False
            )
        ]
        
        return emails
    
    def get_folders(self) -> List[Folder]:
        """Get all available folders."""
        return self._folders.copy()
    
    def get_folder_info(self, folder_path: str) -> Folder:
        """Get information about a specific folder."""
        for folder in self._folders:
            if folder.path == folder_path:
                return folder
        raise ValueError(f"Folder '{folder_path}' not found")
    
    def get_emails(self, folder_path: str) -> List[Email]:
        """Get all emails from a specific folder."""
        # First check if folder exists
        if not any(folder.path == folder_path for folder in self._folders):
            raise ValueError(f"Folder '{folder_path}' not found")
        
        # Return emails if folder exists (empty list if no emails in folder)
        if folder_path not in self._emails:
            return []
        return self._emails[folder_path].copy()
    
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """Move an email to a different folder."""
        # Find the email in any folder
        email_to_move = None
        source_folder = None
        
        for folder_path, emails in self._emails.items():
            for email in emails:
                if email.id == email_id:
                    email_to_move = email
                    source_folder = folder_path
                    break
            if email_to_move:
                break
        
        if not email_to_move:
            raise ValueError(f"Email '{email_id}' not found")
        
        # Check if target folder exists
        if not any(folder.path == target_folder for folder in self._folders):
            raise ValueError(f"Target folder '{target_folder}' not found")
        
        # Remove from source folder
        self._emails[source_folder].remove(email_to_move)
        
        # Update email folder path and add to target folder
        email_to_move.folder_path = target_folder
        if target_folder not in self._emails:
            self._emails[target_folder] = []
        self._emails[target_folder].append(email_to_move)
        
        return True
    
    def get_email_by_id(self, email_id: str) -> Email:
        """Get a specific email by its unique identifier."""
        # Search across all folders for the email ID
        for folder_path, emails in self._emails.items():
            for email in emails:
                if email.id == email_id:
                    return email
        
        # Email not found
        raise ValueError(f"Email '{email_id}' not found")