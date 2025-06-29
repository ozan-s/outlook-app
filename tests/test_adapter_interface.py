"""Test for OutlookAdapter interface completeness."""

from outlook_cli.adapters.outlook_adapter import OutlookAdapter
from outlook_cli.models import Email


def test_outlook_adapter_has_get_email_by_id_method():
    """Test that OutlookAdapter interface includes get_email_by_id method."""
    # This test will fail until we add the method to the interface
    assert hasattr(OutlookAdapter, 'get_email_by_id'), "OutlookAdapter must have get_email_by_id method"
    
    # Verify method signature exists by checking it's abstract
    method = getattr(OutlookAdapter, 'get_email_by_id')
    assert hasattr(method, '__isabstractmethod__'), "get_email_by_id must be an abstract method"
    assert getattr(method, '__isabstractmethod__'), "get_email_by_id must be marked as abstract"


def test_get_email_by_id_method_signature():
    """Test that get_email_by_id has correct method signature."""
    # This will fail until the method is properly defined
    import inspect
    
    # Get the method from the class
    method = getattr(OutlookAdapter, 'get_email_by_id', None)
    assert method is not None, "get_email_by_id method must exist"
    
    # Check signature
    sig = inspect.signature(method)
    params = list(sig.parameters.keys())
    
    # Should have self and email_id parameters
    assert 'self' in params, "Method must have self parameter"
    assert 'email_id' in params, "Method must have email_id parameter"
    
    # Check return annotation (Email type)
    assert sig.return_annotation == Email, "Method must return Email type"