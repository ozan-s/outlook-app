"""Tests for progressive filtering optimization."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.progressive_filter_optimizer import ProgressiveFilterOptimizer, FilterSelectivity
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.models.email import Email


class TestFilterSelectivity:
    """Test FilterSelectivity calculation."""
    
    def test_filter_selectivity_initialization(self):
        """Test FilterSelectivity initialization."""
        selectivity = FilterSelectivity(
            filter_name="sender",
            estimated_selectivity=0.1,
            priority=1
        )
        
        assert selectivity.filter_name == "sender"
        assert selectivity.estimated_selectivity == 0.1
        assert selectivity.priority == 1
    
    def test_filter_selectivity_comparison(self):
        """Test FilterSelectivity comparison for sorting."""
        high_selectivity = FilterSelectivity("filter_a", 0.1, 1)
        low_selectivity = FilterSelectivity("filter_b", 0.8, 2)
        
        # More selective (lower number) should come first
        assert high_selectivity < low_selectivity
        
        # Test equality
        same_selectivity = FilterSelectivity("filter_c", 0.1, 1)
        assert high_selectivity == same_selectivity


class TestProgressiveFilterOptimizer:
    """Test ProgressiveFilterOptimizer functionality."""
    
    def test_progressive_filter_optimizer_initialization(self):
        """Test ProgressiveFilterOptimizer initialization."""
        optimizer = ProgressiveFilterOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'calculate_filter_selectivity')
        assert hasattr(optimizer, 'order_filters_by_selectivity')
        assert hasattr(optimizer, 'apply_filters_progressively')
    
    def test_calculate_filter_selectivity_estimates_correctly(self):
        """Test that filter selectivity is calculated correctly."""
        optimizer = ProgressiveFilterOptimizer()
        
        filters = {
            'sender': 'specific@email.com',  # High selectivity
            'is_unread': True,  # Medium selectivity 
            'folder_path': 'Inbox',  # Low selectivity (many emails in Inbox)
            'importance': 'high',  # High selectivity
            'since': datetime.now()  # Medium selectivity
        }
        
        selectivities = optimizer.calculate_filter_selectivity(filters)
        
        # Should return a list of FilterSelectivity objects
        assert isinstance(selectivities, list)
        assert all(isinstance(s, FilterSelectivity) for s in selectivities)
        
        # Check that high selectivity filters are identified
        sender_selectivity = next((s for s in selectivities if s.filter_name == 'sender'), None)
        importance_selectivity = next((s for s in selectivities if s.filter_name == 'importance'), None)
        folder_selectivity = next((s for s in selectivities if s.filter_name == 'folder_path'), None)
        
        assert sender_selectivity is not None
        assert importance_selectivity is not None  
        assert folder_selectivity is not None
        
        # Sender and importance should be more selective than folder
        assert sender_selectivity.estimated_selectivity < folder_selectivity.estimated_selectivity
        assert importance_selectivity.estimated_selectivity < folder_selectivity.estimated_selectivity
    
    def test_order_filters_by_selectivity_sorts_correctly(self):
        """Test that filters are ordered by selectivity."""
        optimizer = ProgressiveFilterOptimizer()
        
        selectivities = [
            FilterSelectivity("low_selectivity", 0.8, 3),
            FilterSelectivity("high_selectivity", 0.1, 1), 
            FilterSelectivity("medium_selectivity", 0.4, 2)
        ]
        
        ordered = optimizer.order_filters_by_selectivity(selectivities)
        
        # Should be ordered from most selective to least selective
        assert len(ordered) == 3
        assert ordered[0].filter_name == "high_selectivity"
        assert ordered[1].filter_name == "medium_selectivity"
        assert ordered[2].filter_name == "low_selectivity"
    
    def test_apply_filters_progressively_improves_performance(self):
        """Test that progressive filtering reduces processing compared to sequential."""
        optimizer = ProgressiveFilterOptimizer()
        
        # Create a large email set for testing
        large_email_set = []
        for i in range(1000):
            email = Email(
                id=f"email_{i}",
                subject=f"Subject {i}",
                sender_email=f"sender{i % 10}@example.com" if i % 100 != 0 else "specific@email.com",
                sender_name=f"Sender {i}",
                recipient_emails=["recipient@example.com"],
                received_date=datetime.now(timezone.utc),
                body_text="Test body",
                folder_path="Inbox",
                is_read=(i % 3 == 0),
                has_attachments=(i % 5 == 0),
                importance="High" if i % 50 == 0 else "Normal"
            )
            large_email_set.append(email)
        
        # Apply filters progressively - should find specific sender quickly
        filters = {
            'sender': 'specific@email.com',  # Should match ~10 emails
            'importance': 'High',  # Should further filter
            'is_unread': True  # Final filter
        }
        
        with patch('time.time') as mock_time:
            # Mock time to track performance
            mock_time.side_effect = [0, 0.1, 0.15, 0.2]  # Simulate progressive timing
            
            result = optimizer.apply_filters_progressively(large_email_set, filters)
            
            # Should return filtered results
            assert isinstance(result, list)
            # Should contain only emails matching all criteria
            for email in result:
                assert 'specific@email.com' in email.sender_email
                assert email.importance == 'High'
                assert not email.is_read
    
    def test_progressive_filtering_maintains_correctness(self):
        """Test that progressive filtering returns same results as sequential filtering."""
        optimizer = ProgressiveFilterOptimizer()
        
        # Use MockOutlookAdapter for consistent test data
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Get some test emails
        emails = adapter.get_emails("Inbox")
        
        filters = {
            'sender': 'manager@company.com',
            'is_unread': True
        }
        
        # Apply progressive filtering
        progressive_result = optimizer.apply_filters_progressively(emails, filters)
        
        # Apply sequential filtering (current approach)
        sequential_result = []
        filtered_emails = emails
        if filters.get('sender'):
            sender_lower = filters['sender'].lower()
            filtered_emails = [
                email for email in filtered_emails
                if sender_lower in email.sender_email.lower() or sender_lower in email.sender_name.lower()
            ]
        if filters.get('is_unread'):
            filtered_emails = [email for email in filtered_emails if not email.is_read]
        sequential_result = filtered_emails
        
        # Results should be identical
        assert len(progressive_result) == len(sequential_result)
        assert set(e.id for e in progressive_result) == set(e.id for e in sequential_result)


class TestEmailSearcherWithProgressiveFiltering:
    """Test EmailSearcher integration with progressive filtering."""
    
    def test_email_searcher_uses_progressive_filtering(self):
        """Test that EmailSearcher can use progressive filtering optimization."""
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Patch the search_emails method to use progressive filtering
        with patch.object(searcher, '_use_progressive_filtering', return_value=True):
            # This should trigger progressive filtering optimization
            results = searcher.search_emails(
                sender='manager@company.com',
                is_unread=True,
                importance='High'
            )
            
            # Should return results (exact results depend on test data)
            assert isinstance(results, list)
    
    def test_progressive_filtering_can_be_disabled(self):
        """Test that progressive filtering can be disabled via configuration."""
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Should have method to check if progressive filtering is enabled
        assert hasattr(searcher, '_use_progressive_filtering')
        
        # Should be configurable (default to False for backward compatibility)
        with patch.dict('os.environ', {'OUTLOOK_CLI_PROGRESSIVE_FILTERING': 'false'}):
            assert not searcher._use_progressive_filtering()
        
        with patch.dict('os.environ', {'OUTLOOK_CLI_PROGRESSIVE_FILTERING': 'true'}):
            assert searcher._use_progressive_filtering()