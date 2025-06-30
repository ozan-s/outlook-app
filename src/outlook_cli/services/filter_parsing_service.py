"""Service for parsing and building email filter parameters."""

from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from outlook_cli.utils.date_parser import parse_relative_date, validate_date_range


class FilterParsingService:
    """Service to extract and validate filter parameters from CLI arguments."""
    
    def parse_date_filters(self, args) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract and validate date filters from CLI args.
        
        Args:
            args: CLI arguments object with since and until attributes
            
        Returns:
            Tuple of (since_date, until_date) - may be None if not provided
            
        Raises:
            ValueError: If date parsing fails or date range is invalid
        """
        since_date = None
        until_date = None
        
        if args.since:
            since_date = parse_relative_date(args.since)
        if args.until:
            until_date = parse_relative_date(args.until)
            
        # Validate date range if both are provided
        validate_date_range(since_date, until_date)
        
        return since_date, until_date
    
    def build_search_params(self, args, since_date: Optional[datetime], until_date: Optional[datetime]) -> Dict[str, Any]:
        """Build EmailSearcher parameter dict from CLI args.
        
        Args:
            args: CLI arguments object
            since_date: Parsed since date (may be None)
            until_date: Parsed until date (may be None)
            
        Returns:
            Dictionary of parameters for EmailSearcher.search_emails()
        """
        return {
            'folder_path': args.folder,
            'since': since_date,
            'until': until_date,
            'is_read': args.is_read,
            'is_unread': args.is_unread,
            'has_attachment': args.has_attachment,
            'no_attachment': args.no_attachment,
            'importance': args.importance,
            'not_sender': args.not_sender,
            'not_subject': args.not_subject
        }