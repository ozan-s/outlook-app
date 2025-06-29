"""Adapter factory for creating the appropriate Outlook adapter."""

import os
import sys
from typing import Optional
from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter


class AdapterFactory:
    """Factory class for creating Outlook adapters based on configuration."""
    
    @staticmethod
    def create_adapter(adapter_type: Optional[str] = None) -> OutlookAdapter:
        """
        Create an Outlook adapter based on configuration.
        
        Args:
            adapter_type: Type of adapter to create ('mock' or 'real'). 
                         If None, checks environment variable and defaults to 'real' on Windows, 'mock' elsewhere.
        
        Returns:
            Configured OutlookAdapter instance
        
        Raises:
            ValueError: If adapter_type is invalid
        """
        # Determine adapter type from parameters, environment, or default
        if adapter_type is None:
            # Default to 'real' on Windows, 'mock' elsewhere for safe development
            default_adapter = 'real' if sys.platform == 'win32' else 'mock'
            adapter_type = os.environ.get('OUTLOOK_ADAPTER', default_adapter)
        
        adapter_type = adapter_type.lower()
        
        if adapter_type == 'mock':
            return MockOutlookAdapter()
        elif adapter_type == 'real':
            return PyWin32OutlookAdapter()
        else:
            raise ValueError(
                f"Invalid adapter type: '{adapter_type}'. "
                f"Valid options are: 'mock', 'real'"
            )