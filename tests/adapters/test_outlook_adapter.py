"""Tests for OutlookAdapter abstract interface."""

import pytest
from outlook_cli.adapters import OutlookAdapter


def test_outlook_adapter_cannot_be_instantiated_directly():
    """Test that OutlookAdapter abstract class cannot be instantiated directly."""
    with pytest.raises(TypeError) as exc_info:
        OutlookAdapter()
    
    assert "Can't instantiate abstract class" in str(exc_info.value)