"""Performance regression tests for Outlook CLI operations."""

import pytest
import time
import tempfile
import json
from datetime import datetime, timezone
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.utils.performance_monitor import PerformanceMonitor
from outlook_cli.utils.performance_baseline import PerformanceBaseline, BaselineMetrics
from outlook_cli.models.email import Email


class TestPerformanceBaseline:
    """Test performance baseline functionality."""
    
    def test_performance_baseline_initialization(self):
        """Test PerformanceBaseline initialization."""
        baseline = PerformanceBaseline()
        
        assert baseline is not None
        assert hasattr(baseline, 'record_baseline')
        assert hasattr(baseline, 'check_regression')
        assert hasattr(baseline, 'get_baseline')
    
    def test_baseline_metrics_creation(self):
        """Test BaselineMetrics data structure."""
        metrics = BaselineMetrics(
            operation="test_operation",
            baseline_duration=1.5,
            baseline_memory=100.0,
            threshold_factor=1.2,
            recorded_at=datetime.now()
        )
        
        assert metrics.operation == "test_operation"
        assert metrics.baseline_duration == 1.5
        assert metrics.baseline_memory == 100.0
        assert metrics.threshold_factor == 1.2
        assert isinstance(metrics.recorded_at, datetime)
    
    def test_record_baseline_saves_performance_data(self):
        """Test that baseline recording saves performance data."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path)
            
            # Record a baseline
            baseline.record_baseline(
                operation="read_emails",
                duration_seconds=0.5,
                memory_mb=50.0
            )
            
            # Verify file was created and contains data
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            assert "read_emails" in data
            assert data["read_emails"]["baseline_duration"] == 0.5
            assert data["read_emails"]["baseline_memory"] == 50.0
            assert "recorded_at" in data["read_emails"]
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_check_regression_detects_performance_degradation(self):
        """Test that regression checking detects performance degradation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path)
            
            # Record a baseline
            baseline.record_baseline(
                operation="search_emails",
                duration_seconds=1.0,
                memory_mb=100.0
            )
            
            # Check with acceptable performance (no regression)
            is_regression = baseline.check_regression(
                operation="search_emails",
                current_duration=1.1,  # 10% slower - within threshold
                current_memory=110.0   # 10% more memory - within threshold
            )
            assert not is_regression
            
            # Check with degraded performance (regression detected)
            is_regression = baseline.check_regression(
                operation="search_emails", 
                current_duration=2.5,  # 150% slower - significant regression
                current_memory=250.0   # 150% more memory - significant regression
            )
            assert is_regression
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_baseline_returns_stored_metrics(self):
        """Test that get_baseline returns stored metrics."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path)
            
            # Record a baseline
            baseline.record_baseline(
                operation="find_emails",
                duration_seconds=0.8,
                memory_mb=75.0
            )
            
            # Retrieve baseline
            metrics = baseline.get_baseline("find_emails")
            
            assert metrics is not None
            assert isinstance(metrics, BaselineMetrics)
            assert metrics.operation == "find_emails"
            assert metrics.baseline_duration == 0.8
            assert metrics.baseline_memory == 75.0
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestPerformanceRegressionDetection:
    """Test performance regression detection in real operations."""
    
    def test_email_search_performance_baseline_establishment(self):
        """Test establishing performance baseline for email search operations."""
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        monitor = PerformanceMonitor()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path)
            
            # Perform email search with monitoring
            monitor.start_monitoring("baseline_search")
            results = searcher.search_emails(folder_path="Inbox", is_unread=True)
            metrics = monitor.stop_monitoring("baseline_search")
            
            # Record baseline
            baseline.record_baseline(
                operation="email_search_unread",
                duration_seconds=metrics.duration_seconds,
                memory_mb=metrics.memory_used_mb
            )
            
            # Verify baseline was recorded
            recorded_baseline = baseline.get_baseline("email_search_unread")
            assert recorded_baseline is not None
            assert recorded_baseline.baseline_duration > 0
            assert recorded_baseline.baseline_memory >= 0
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_performance_regression_detection_in_filtering(self):
        """Test detection of performance regression in filtering operations."""
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        monitor = PerformanceMonitor()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path)
            
            # Establish baseline with simple search
            monitor.start_monitoring("baseline_filter")
            searcher.search_emails(folder_path="Inbox")
            baseline_metrics = monitor.stop_monitoring("baseline_filter")
            
            baseline.record_baseline(
                operation="simple_filter",
                duration_seconds=baseline_metrics.duration_seconds,
                memory_mb=baseline_metrics.memory_used_mb
            )
            
            # Simulate a potentially slower operation (complex filtering)
            monitor.start_monitoring("complex_filter")
            # Add artificial delay to simulate performance regression
            time.sleep(0.01)  # 10ms delay
            searcher.search_emails(
                folder_path="Inbox",
                sender="test@example.com",
                is_unread=True,
                has_attachment=True,
                importance="High"
            )
            complex_metrics = monitor.stop_monitoring("complex_filter")
            
            # Check for regression
            is_regression = baseline.check_regression(
                operation="simple_filter",
                current_duration=complex_metrics.duration_seconds,
                current_memory=complex_metrics.memory_used_mb
            )
            
            # Complex filtering with artificial delay should trigger regression detection
            assert is_regression
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_performance_monitoring_with_large_datasets(self):
        """Test performance monitoring with large email datasets."""
        adapter = MockOutlookAdapter()
        
        # Create a large dataset for testing
        large_email_set = []
        for i in range(1000):
            email = Email(
                id=f"perf_test_{i}",
                subject=f"Performance Test Email {i}",
                sender_email=f"sender{i % 100}@example.com",
                sender_name=f"Sender {i}",
                recipient_emails=["recipient@example.com"],
                received_date=datetime.now(timezone.utc),
                body_text="Performance test email body",
                folder_path="Inbox",
                is_read=(i % 3 == 0),
                has_attachments=(i % 10 == 0),
                importance="Normal"
            )
            large_email_set.append(email)
        
        # Mock the adapter to return large dataset
        adapter._emails["Inbox"] = large_email_set
        
        searcher = EmailSearcher(adapter)
        monitor = PerformanceMonitor()
        
        # Monitor large dataset search
        monitor.start_monitoring("large_dataset_search")
        results = searcher.search_emails(
            folder_path="Inbox",
            sender="sender5@example.com"  # Should match ~10 emails
        )
        metrics = monitor.stop_monitoring("large_dataset_search")
        
        # Verify performance metrics
        assert metrics.duration_seconds < 2.0  # Should complete within 2 seconds
        assert len(results) > 0  # Should find matching emails
        assert metrics.memory_used_mb >= 0  # Should track memory usage
    
    def test_baseline_comparison_with_tolerance(self):
        """Test baseline comparison respects tolerance thresholds."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            baseline = PerformanceBaseline(baseline_file=temp_path, threshold_factor=1.5)  # 50% tolerance
            
            # Record baseline
            baseline.record_baseline(
                operation="tolerance_test",
                duration_seconds=1.0,
                memory_mb=100.0
            )
            
            # Test within tolerance (should not be regression)
            assert not baseline.check_regression(
                operation="tolerance_test",
                current_duration=1.3,   # 30% slower - within 50% tolerance
                current_memory=130.0    # 30% more memory - within tolerance
            )
            
            # Test exceeding tolerance (should be regression)
            assert baseline.check_regression(
                operation="tolerance_test", 
                current_duration=1.8,   # 80% slower - exceeds 50% tolerance
                current_memory=180.0    # 80% more memory - exceeds tolerance
            )
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)