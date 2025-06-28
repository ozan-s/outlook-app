"""
Enhanced error classes with categorization and context for outlook_cli.
"""
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCategory(Enum):
    """Error categories for different handling strategies."""
    TRANSIENT = "transient"      # Retry possible
    PERMANENT = "permanent"      # No retry
    USER_ERROR = "user_error"    # User action required
    SYSTEM_ERROR = "system_error"  # System/admin action required


class OutlookError(ValueError):
    """
    Base error class for Outlook operations with categorization and context.
    
    Inherits from ValueError to maintain backward compatibility with existing
    error handling patterns in the CLI layer.
    """
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.PERMANENT,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.category = category
        self.context = context or {}
        self.suggestion = suggestion


class OutlookConnectionError(OutlookError):
    """Error for Outlook connection failures."""
    
    def __init__(self, message: str, **kwargs):
        # Default to transient for connection errors
        kwargs.setdefault('category', ErrorCategory.TRANSIENT)
        kwargs.setdefault('suggestion', "Please ensure Outlook is running and try again.")
        super().__init__(message, **kwargs)


class OutlookTimeoutError(OutlookError):
    """Error for operation timeouts."""
    
    def __init__(self, message: str, timeout_seconds: float = 30, **kwargs):
        # Default to transient for timeout errors
        kwargs.setdefault('category', ErrorCategory.TRANSIENT)
        
        # Add timeout to context
        context = kwargs.get('context', {})
        context['timeout_seconds'] = timeout_seconds
        kwargs['context'] = context
        
        # Default suggestion
        kwargs.setdefault(
            'suggestion', 
            f"Operation timed out after {timeout_seconds}s. Large folders may take longer to process."
        )
        
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class OutlookValidationError(OutlookError):
    """Error for input validation failures."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        # Default to user error for validation
        kwargs.setdefault('category', ErrorCategory.USER_ERROR)
        
        # Add field to context
        if field:
            context = kwargs.get('context', {})
            context['field'] = field
            kwargs['context'] = context
            
            # Field-specific suggestion
            kwargs.setdefault(
                'suggestion',
                f"Please check the {field} value and try again."
            )
        
        super().__init__(message, **kwargs)
        self.field = field


def get_error_suggestion(error_type: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Get contextual error suggestions based on error type and context.
    
    Args:
        error_type: Type of error (e.g., "folder_not_found", "connection_failed")
        context: Additional context for generating suggestions
        
    Returns:
        Helpful suggestion message
    """
    context = context or {}
    
    suggestions = {
        "folder_not_found": _get_folder_not_found_suggestion(context),
        "connection_failed": "Please ensure Outlook is running and try again.",
        "timeout": _get_timeout_suggestion(context),
        "validation_failed": _get_validation_suggestion(context),
    }
    
    return suggestions.get(error_type, "Use 'outlook-cli --help' for usage information.")


def _get_folder_not_found_suggestion(context: Dict[str, Any]) -> str:
    """Generate suggestion for folder not found errors."""
    folder = context.get("folder", "")
    
    # Common folder name corrections
    if folder.lower() == "inbox":
        return "Did you mean 'Inbox'? Use 'read --help' to see available folders."
    elif folder.lower() in ["sent", "sentmail"]:
        return "Did you mean 'Sent Items'? Use 'read --help' to see available folders."
    else:
        return "Check the folder name spelling. Use 'read --help' to see available folders."


def _get_timeout_suggestion(context: Dict[str, Any]) -> str:
    """Generate suggestion for timeout errors."""
    timeout_seconds = context.get("timeout_seconds", 30)
    return f"Operation timed out after {timeout_seconds}s. Large folders may take longer to process."


def _get_validation_suggestion(context: Dict[str, Any]) -> str:
    """Generate suggestion for validation errors."""
    field = context.get("field", "input")
    value = context.get("value", "")
    
    if field == "email" and value:
        return f"The email address '{value}' is not valid. Please use format: user@domain.com"
    else:
        return f"Please check the {field} value and try again."