"""Test project setup and infrastructure."""

import pytest
from outlook_cli import __version__


def test_package_version():
    """Test that package version is accessible."""
    assert __version__ == "0.1.0"


def test_import_package():
    """Test that main package can be imported."""
    import outlook_cli
    assert outlook_cli is not None


def test_pytest_working():
    """Test that pytest framework is functioning."""
    assert True