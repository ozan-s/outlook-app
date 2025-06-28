"""EmailReader service for retrieving emails from folders."""

from outlook_cli.adapters.outlook_adapter import OutlookAdapter


class EmailReader:
    """Service for reading emails from folders via OutlookAdapter."""
    
    def __init__(self, adapter: OutlookAdapter):
        """Initialize EmailReader with an OutlookAdapter.
        
        Args:
            adapter: OutlookAdapter instance for email operations.
        """
        self._adapter = adapter