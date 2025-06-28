"""
Tests for enhanced error classes with categorization.
"""
import pytest

from outlook_cli.utils.errors import (
    OutlookError,
    OutlookConnectionError,
    OutlookTimeoutError,
    OutlookValidationError,
    ErrorCategory,
    get_error_suggestion
)


class TestOutlookError:
    """Test base OutlookError class."""

    def test_outlook_error_has_category_and_context(self):
        """Test that OutlookError includes category and context."""
        error = OutlookError(
            message="Test error",
            category=ErrorCategory.USER_ERROR,
            context={"operation": "test_operation", "input": "test_input"}
        )
        
        assert str(error) == "Test error"
        assert error.category == ErrorCategory.USER_ERROR
        assert error.context["operation"] == "test_operation"
        assert error.context["input"] == "test_input"

    def test_outlook_error_with_suggestion(self):
        """Test that OutlookError can include recovery suggestions."""
        error = OutlookError(
            message="Folder not found",
            category=ErrorCategory.USER_ERROR,
            suggestion="Check the folder name and try again."
        )
        
        assert error.suggestion == "Check the folder name and try again."

    def test_outlook_error_defaults(self):
        """Test OutlookError default values."""
        error = OutlookError("Simple error")
        
        assert str(error) == "Simple error"
        assert error.category == ErrorCategory.PERMANENT
        assert error.context == {}
        assert error.suggestion is None


class TestErrorSubclasses:
    """Test specific error subclasses."""

    def test_connection_error_defaults_to_transient(self):
        """Test that connection errors are marked as transient by default."""
        error = OutlookConnectionError("Connection failed")
        
        assert error.category == ErrorCategory.TRANSIENT
        assert "Connection failed" in str(error)

    def test_timeout_error_defaults_to_transient(self):
        """Test that timeout errors are marked as transient by default."""
        error = OutlookTimeoutError("Operation timed out", timeout_seconds=30)
        
        assert error.category == ErrorCategory.TRANSIENT
        assert error.timeout_seconds == 30
        assert "Operation timed out" in str(error)

    def test_validation_error_defaults_to_user_error(self):
        """Test that validation errors are marked as user errors by default."""
        error = OutlookValidationError("Invalid input", field="email")
        
        assert error.category == ErrorCategory.USER_ERROR
        assert error.field == "email"
        assert "Invalid input" in str(error)

    def test_connection_error_with_retry_suggestion(self):
        """Test connection error includes retry suggestion."""
        error = OutlookConnectionError("Cannot connect to Outlook")
        
        assert "retry" in error.suggestion.lower() or "ensure" in error.suggestion.lower()

    def test_timeout_error_with_timeout_context(self):
        """Test timeout error includes timeout in context."""
        error = OutlookTimeoutError("Folder read timed out", timeout_seconds=45)
        
        assert error.context["timeout_seconds"] == 45
        assert "45" in error.suggestion

    def test_validation_error_with_field_context(self):
        """Test validation error includes field in context."""
        error = OutlookValidationError("Email format invalid", field="sender_email")
        
        assert error.context["field"] == "sender_email"
        assert "sender_email" in error.suggestion


class TestErrorCategory:
    """Test error category enumeration."""

    def test_error_category_values(self):
        """Test that all expected error categories exist."""
        assert ErrorCategory.TRANSIENT.value == "transient"
        assert ErrorCategory.PERMANENT.value == "permanent"
        assert ErrorCategory.USER_ERROR.value == "user_error"
        assert ErrorCategory.SYSTEM_ERROR.value == "system_error"

    def test_error_category_comparison(self):
        """Test error category comparison."""
        assert ErrorCategory.TRANSIENT == ErrorCategory.TRANSIENT
        assert ErrorCategory.TRANSIENT != ErrorCategory.PERMANENT


class TestErrorSuggestions:
    """Test error suggestion utility functions."""

    def test_get_error_suggestion_for_folder_not_found(self):
        """Test suggestion for folder not found errors."""
        suggestion = get_error_suggestion("folder_not_found", {"folder": "InBox"})
        
        assert suggestion is not None
        assert "inbox" in suggestion.lower() or "available folders" in suggestion.lower()

    def test_get_error_suggestion_for_connection_failed(self):
        """Test suggestion for connection failures."""
        suggestion = get_error_suggestion("connection_failed")
        
        assert suggestion is not None
        assert "outlook" in suggestion.lower()
        assert "running" in suggestion.lower()

    def test_get_error_suggestion_for_timeout(self):
        """Test suggestion for timeout errors."""
        suggestion = get_error_suggestion("timeout", {"timeout_seconds": 30})
        
        assert suggestion is not None
        assert "30" in suggestion
        assert "large" in suggestion.lower() or "longer" in suggestion.lower()

    def test_get_error_suggestion_for_unknown_error_type(self):
        """Test that unknown error types return generic suggestion."""
        suggestion = get_error_suggestion("unknown_error_type")
        
        assert suggestion is not None
        assert "help" in suggestion.lower() or "support" in suggestion.lower()

    def test_get_error_suggestion_with_context(self):
        """Test that error suggestions use context when available."""
        suggestion = get_error_suggestion(
            "validation_failed", 
            {"field": "email", "value": "invalid-email"}
        )
        
        assert suggestion is not None
        assert "email" in suggestion.lower()


class TestErrorIntegration:
    """Test error classes integration with existing patterns."""

    def test_outlook_error_compatible_with_valueerror_pattern(self):
        """Test that OutlookError can be caught as ValueError for backward compatibility."""
        # OutlookError should inherit from ValueError to maintain existing patterns
        error = OutlookError("Test error")
        
        # Should be catchable as ValueError
        with pytest.raises(ValueError):
            raise error

    def test_error_classes_preserve_message_access(self):
        """Test that error messages are accessible for CLI error handling."""
        errors = [
            OutlookError("Base error"),
            OutlookConnectionError("Connection error"),
            OutlookTimeoutError("Timeout error", timeout_seconds=10),
            OutlookValidationError("Validation error", field="test")
        ]
        
        for error in errors:
            # Should be convertible to string for CLI display
            message = str(error)
            assert len(message) > 0
            assert isinstance(message, str)