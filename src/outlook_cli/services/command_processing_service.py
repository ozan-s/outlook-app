"""Service for common email command processing patterns."""

from typing import Dict, Any, Optional
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.email_sorting_service import EmailSortingService
from outlook_cli.services.paginator import Paginator


class CommandProcessingService:
    """Service to handle common email command processing patterns."""
    
    def __init__(self, adapter_factory):
        """Initialize with adapter factory for creating adapters.
        
        Args:
            adapter_factory: Factory for creating Outlook adapters
        """
        self.adapter_factory = adapter_factory
    
    def process_email_command(self, args, search_params: Dict[str, Any], operation_name: str, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Common pattern: search -> sort -> paginate -> return results.
        
        Args:
            args: CLI arguments object with sort_by, sort_order attributes
            search_params: Parameters to pass to EmailSearcher.search_emails()
            operation_name: Name of operation for logging/error purposes
            page_size: Optional custom page size for pagination (default: 10)
            
        Returns:
            Dictionary containing:
            - emails: List of email objects (sorted if requested)
            - paginator: Paginator instance (None if no emails)
            - current_page: Current page of emails (None if no emails)
            
        Raises:
            Exception: Any errors from adapter creation, email searching, sorting, or pagination
        """
        # Initialize EmailSearcher with configured adapter
        adapter_type = getattr(args, 'adapter', None)
        adapter = self.adapter_factory.create_adapter(adapter_type)
        searcher = EmailSearcher(adapter)
        
        # Perform email search
        emails = searcher.search_emails(**search_params)
        
        # Handle empty results
        if not emails:
            return {
                'emails': [],
                'paginator': None,
                'current_page': None
            }
        
        # Apply sorting if specified
        if args.sort_by:
            sorting_service = EmailSortingService()
            emails = sorting_service.sort_emails(emails, args.sort_by, args.sort_order)
        
        # Paginate emails (use custom page size or default 10 per page)
        effective_page_size = page_size if page_size is not None else 10
        paginator = Paginator(emails, page_size=effective_page_size)
        current_page = paginator.get_current_page()
        
        return {
            'emails': emails,
            'paginator': paginator,
            'current_page': current_page
        }