"""EmailSortingService for sorting emails by various criteria."""

from typing import List
from outlook_cli.models.email import Email


class EmailSortingService:
    """Service for sorting emails by different fields and orders."""
    
    def sort_emails(self, emails: List[Email], sort_by: str, sort_order: str) -> List[Email]:
        """Sort emails by specified field and order.
        
        Args:
            emails: List of emails to sort.
            sort_by: Field to sort by ('received_date', 'subject', 'sender', 'importance').
            sort_order: Sort order ('asc' for ascending, 'desc' for descending).
            
        Returns:
            List[Email]: Sorted emails.
        """
        if not emails:
            return emails
            
        # Default to received_date desc if no sort specified
        if not sort_by:
            sort_by = "received_date"
            sort_order = "desc"
            
        reverse = sort_order == "desc"
        
        if sort_by == "received_date":
            return sorted(emails, key=lambda email: email.received_date, reverse=reverse)
        elif sort_by == "subject":
            return sorted(emails, key=lambda email: email.subject.lower(), reverse=reverse)
        elif sort_by == "sender":
            return sorted(emails, key=lambda email: email.sender_email.lower(), reverse=reverse)
        elif sort_by == "importance":
            # Sort by importance (High→Normal→Low for desc, Low→Normal→High for asc)
            importance_order = {"High": 3, "Normal": 2, "Low": 1}
            return sorted(emails, key=lambda email: importance_order.get(email.importance, 0), reverse=reverse)
        else:
            # Unknown sort field, return emails unsorted
            return emails