"""Tests for Folder model."""

import pytest
from pydantic import ValidationError
from outlook_cli.models import Folder


def test_folder_creation_with_valid_data():
    """Test creating a Folder with all valid required fields."""
    folder_data = {
        "path": "Inbox",
        "name": "Inbox",
        "email_count": 25,
        "unread_count": 5
    }
    
    folder = Folder(**folder_data)
    
    assert folder.path == "Inbox"
    assert folder.name == "Inbox"
    assert folder.email_count == 25
    assert folder.unread_count == 5


def test_folder_creation_with_subfolder():
    """Test creating a Folder with subfolder path."""
    folder_data = {
        "path": "Inbox/Important",
        "name": "Important",
        "email_count": 10,
        "unread_count": 2
    }
    
    folder = Folder(**folder_data)
    
    assert folder.path == "Inbox/Important"
    assert folder.name == "Important"
    assert folder.email_count == 10
    assert folder.unread_count == 2


def test_folder_validation_negative_email_count():
    """Test that negative email count raises ValidationError."""
    folder_data = {
        "path": "Inbox",
        "name": "Inbox",
        "email_count": -1,  # Negative count should fail
        "unread_count": 5
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Folder(**folder_data)
    
    assert "email_count" in str(exc_info.value)


def test_folder_validation_negative_unread_count():
    """Test that negative unread count raises ValidationError."""
    folder_data = {
        "path": "Inbox",
        "name": "Inbox",
        "email_count": 25,
        "unread_count": -1  # Negative count should fail
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Folder(**folder_data)
    
    assert "unread_count" in str(exc_info.value)


def test_folder_validation_unread_greater_than_total():
    """Test that unread count greater than total raises ValidationError."""
    folder_data = {
        "path": "Inbox",
        "name": "Inbox",
        "email_count": 5,
        "unread_count": 10  # Unread > total should fail
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Folder(**folder_data)
    
    assert "unread_count" in str(exc_info.value) or "email_count" in str(exc_info.value)


def test_folder_validation_empty_path():
    """Test that empty folder path raises ValidationError."""
    folder_data = {
        "path": "",  # Empty path should fail
        "name": "Inbox",
        "email_count": 25,
        "unread_count": 5
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Folder(**folder_data)
    
    assert "path" in str(exc_info.value)


def test_folder_validation_empty_name():
    """Test that empty folder name raises ValidationError."""
    folder_data = {
        "path": "Inbox",
        "name": "",  # Empty name should fail
        "email_count": 25,
        "unread_count": 5
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Folder(**folder_data)
    
    assert "name" in str(exc_info.value)