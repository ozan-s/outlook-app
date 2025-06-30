"""Tests for FilterParsingService."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
from src.outlook_cli.services.filter_parsing_service import FilterParsingService


class TestFilterParsingService:
    """Test FilterParsingService date parsing and parameter building logic."""
    
    def setup_method(self):
        """Set up test instance."""
        self.service = FilterParsingService()
    
    def test_parse_date_filters_with_since_and_until(self):
        """Test parsing both since and until date arguments."""
        # Arrange
        args = Mock()
        args.since = "1d"
        args.until = "today"
        
        # Act
        since_date, until_date = self.service.parse_date_filters(args)
        
        # Assert
        assert since_date is not None
        assert until_date is not None
        assert isinstance(since_date, datetime)
        assert isinstance(until_date, datetime)
        assert since_date.tzinfo is not None  # Should be timezone-aware
        assert until_date.tzinfo is not None
        assert since_date < until_date
    
    def test_parse_date_filters_with_only_since(self):
        """Test parsing only since date argument."""
        # Arrange
        args = Mock()
        args.since = "2d"
        args.until = None
        
        # Act
        since_date, until_date = self.service.parse_date_filters(args)
        
        # Assert
        assert since_date is not None
        assert until_date is None
        assert isinstance(since_date, datetime)
    
    def test_parse_date_filters_with_no_dates(self):
        """Test parsing when no date arguments provided."""
        # Arrange
        args = Mock()
        args.since = None
        args.until = None
        
        # Act
        since_date, until_date = self.service.parse_date_filters(args)
        
        # Assert
        assert since_date is None
        assert until_date is None
    
    def test_build_search_params_for_read_command(self):
        """Test building search parameters for read command."""
        # Arrange
        args = Mock()
        args.folder = "Inbox"
        args.is_read = True
        args.is_unread = False
        args.has_attachment = None
        args.no_attachment = None
        args.importance = None
        args.not_sender = None
        args.not_subject = None
        
        since_date = datetime.now(timezone.utc)
        until_date = datetime.now(timezone.utc)
        
        # Act
        params = self.service.build_search_params(args, since_date, until_date)
        
        # Assert
        expected_params = {
            'folder_path': 'Inbox',
            'since': since_date,
            'until': until_date,
            'is_read': True,
            'is_unread': False,
            'has_attachment': None,
            'no_attachment': None,
            'importance': None,
            'not_sender': None,
            'not_subject': None
        }
        assert params == expected_params
    
    def test_build_search_params_for_find_command_with_keyword(self):
        """Test building search parameters for find command with keyword."""
        # Arrange
        args = Mock()
        args.folder = "Sent Items"
        args.keyword = "urgent"
        args.sender = None
        args.subject = None
        args.is_read = None
        args.is_unread = None
        args.has_attachment = True
        args.no_attachment = None
        args.importance = "High"
        args.not_sender = "spam@example.com"
        args.not_subject = "newsletter"
        
        since_date = None
        until_date = None
        
        # Act
        params = self.service.build_search_params(args, since_date, until_date)
        
        # Assert
        expected_params = {
            'folder_path': 'Sent Items',
            'since': None,
            'until': None,
            'is_read': None,
            'is_unread': None,
            'has_attachment': True,
            'no_attachment': None,
            'importance': 'High',
            'not_sender': 'spam@example.com',
            'not_subject': 'newsletter'
        }
        assert params == expected_params
        # Should not include keyword, sender, subject in basic params
        assert 'keyword' not in params
        assert 'sender' not in params
        assert 'subject' not in params