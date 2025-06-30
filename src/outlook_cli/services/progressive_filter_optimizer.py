"""Progressive filtering optimization for email search operations."""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from outlook_cli.models.email import Email


@dataclass
class FilterSelectivity:
    """Represents the selectivity of a filter operation."""
    
    filter_name: str
    estimated_selectivity: float  # 0.0 = most selective, 1.0 = least selective
    priority: int
    
    def __lt__(self, other: 'FilterSelectivity') -> bool:
        """Compare selectivity for sorting (more selective first)."""
        # Primary sort by estimated selectivity
        if self.estimated_selectivity != other.estimated_selectivity:
            return self.estimated_selectivity < other.estimated_selectivity
        # Secondary sort by priority
        return self.priority < other.priority
    
    def __eq__(self, other: 'FilterSelectivity') -> bool:
        """Check equality for selectivity."""
        return (self.estimated_selectivity == other.estimated_selectivity and 
                self.priority == other.priority)


class ProgressiveFilterOptimizer:
    """Optimizer for applying email filters in order of selectivity."""
    
    def __init__(self):
        """Initialize the progressive filter optimizer."""
        # Estimated selectivity values based on typical email characteristics
        self._selectivity_estimates = {
            'sender': 0.05,  # Specific sender is very selective
            'subject': 0.15,  # Subject keywords are quite selective
            'importance': 0.1,  # High importance is selective
            'has_attachment': 0.3,  # Attachment presence is moderately selective
            'no_attachment': 0.7,  # No attachment is less selective
            'is_read': 0.6,  # Read status is less selective
            'is_unread': 0.4,  # Unread is more selective than read
            'since': 0.3,  # Date ranges are moderately selective
            'until': 0.3,  # Date ranges are moderately selective
            'folder_path': 0.8,  # Folder filtering is least selective (many emails per folder)
            'not_sender': 0.95,  # Exclusion filters are least selective
            'not_subject': 0.95,  # Exclusion filters are least selective
        }
    
    def calculate_filter_selectivity(self, filters: Dict[str, Any]) -> List[FilterSelectivity]:
        """Calculate selectivity for each active filter.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of FilterSelectivity objects for active filters
        """
        selectivities = []
        priority = 1
        
        for filter_name, filter_value in filters.items():
            if filter_value is not None:
                estimated_selectivity = self._selectivity_estimates.get(filter_name, 0.5)
                
                # Adjust selectivity based on filter value characteristics
                if filter_name == 'sender' and '@' in str(filter_value):
                    # Full email address is more selective than partial name
                    estimated_selectivity *= 0.5
                elif filter_name in ['subject', 'not_subject'] and len(str(filter_value)) > 10:
                    # Longer search terms are more selective
                    estimated_selectivity *= 0.7
                
                selectivity = FilterSelectivity(
                    filter_name=filter_name,
                    estimated_selectivity=estimated_selectivity,
                    priority=priority
                )
                selectivities.append(selectivity)
                priority += 1
        
        return selectivities
    
    def order_filters_by_selectivity(self, selectivities: List[FilterSelectivity]) -> List[FilterSelectivity]:
        """Order filters by selectivity (most selective first).
        
        Args:
            selectivities: List of FilterSelectivity objects
            
        Returns:
            Sorted list with most selective filters first
        """
        return sorted(selectivities)
    
    def apply_filters_progressively(self, emails: List[Email], filters: Dict[str, Any]) -> List[Email]:
        """Apply filters in order of selectivity for optimal performance.
        
        Args:
            emails: List of emails to filter
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of emails
        """
        if not filters or not emails:
            return emails
        
        # Calculate and order filters by selectivity
        selectivities = self.calculate_filter_selectivity(filters)
        ordered_selectivities = self.order_filters_by_selectivity(selectivities)
        
        # Apply filters progressively
        filtered_emails = emails
        
        for selectivity in ordered_selectivities:
            filter_name = selectivity.filter_name
            filter_value = filters[filter_name]
            
            # Apply the specific filter
            filtered_emails = self._apply_single_filter(filtered_emails, filter_name, filter_value)
            
            # Early termination if no emails remain
            if not filtered_emails:
                break
        
        return filtered_emails
    
    def _apply_single_filter(self, emails: List[Email], filter_name: str, filter_value: Any) -> List[Email]:
        """Apply a single filter to the email list.
        
        Args:
            emails: List of emails to filter
            filter_name: Name of the filter to apply
            filter_value: Value for the filter
            
        Returns:
            Filtered list of emails
        """
        if filter_name == 'sender':
            sender_lower = str(filter_value).lower()
            return [
                email for email in emails
                if sender_lower in email.sender_email.lower() or sender_lower in email.sender_name.lower()
            ]
        
        elif filter_name == 'subject':
            subject_lower = str(filter_value).lower()
            return [
                email for email in emails
                if subject_lower in email.subject.lower()
            ]
        
        elif filter_name == 'since':
            return [
                email for email in emails
                if email.received_date >= filter_value
            ]
        
        elif filter_name == 'until':
            return [
                email for email in emails
                if email.received_date <= filter_value
            ]
        
        elif filter_name == 'is_read':
            return [email for email in emails if email.is_read] if filter_value else emails
        
        elif filter_name == 'is_unread':
            return [email for email in emails if not email.is_read] if filter_value else emails
        
        elif filter_name == 'has_attachment':
            return [email for email in emails if email.has_attachments] if filter_value else emails
        
        elif filter_name == 'no_attachment':
            return [email for email in emails if not email.has_attachments] if filter_value else emails
        
        elif filter_name == 'importance':
            importance_lower = str(filter_value).lower()
            return [
                email for email in emails
                if email.importance.lower() == importance_lower
            ]
        
        elif filter_name == 'not_sender':
            not_sender_lower = str(filter_value).lower()
            return [
                email for email in emails
                if not_sender_lower not in email.sender_email.lower() 
                and not_sender_lower not in email.sender_name.lower()
            ]
        
        elif filter_name == 'not_subject':
            not_subject_lower = str(filter_value).lower()
            return [
                email for email in emails
                if not_subject_lower not in email.subject.lower()
            ]
        
        # For unknown filters, return emails unchanged
        return emails