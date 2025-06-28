"""Paginator service for handling email pagination."""

from typing import List, Dict
from outlook_cli.models.email import Email


class Paginator:
    """Service for paginating email lists with navigation."""
    
    def __init__(self, items: List[Email], page_size: int = 10):
        """Initialize Paginator with email list and page size.
        
        Args:
            items: List of emails to paginate.
            page_size: Number of items per page (default 10).
        """
        self._items = items
        self._page_size = page_size
        self._current_page = 1 if items else 0
        self._total_pages = (len(items) + page_size - 1) // page_size if items else 0
    
    def get_current_page(self) -> List[Email]:
        """Get emails for the current page.
        
        Returns:
            List[Email]: Emails for current page (up to page_size items).
        """
        if not self._items or self._current_page == 0:
            return []
        
        start_idx = (self._current_page - 1) * self._page_size
        end_idx = start_idx + self._page_size
        return self._items[start_idx:end_idx]
    
    def next_page(self) -> bool:
        """Move to next page if possible.
        
        Returns:
            bool: True if moved to next page, False if already at last page.
        """
        if self._current_page < self._total_pages:
            self._current_page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        """Move to previous page if possible.
        
        Returns:
            bool: True if moved to previous page, False if already at first page.
        """
        if self._current_page > 1:
            self._current_page -= 1
            return True
        return False
    
    def get_page_info(self) -> Dict[str, int]:
        """Get information about current pagination state.
        
        Returns:
            Dict[str, int]: Page info with current_page, total_pages, total_items, items_per_page.
        """
        return {
            "current_page": self._current_page,
            "total_pages": self._total_pages,
            "total_items": len(self._items),
            "items_per_page": self._page_size
        }