"""Test date parser functionality."""
import pytest
from datetime import datetime, timezone, timedelta
from outlook_cli.utils.date_parser import parse_relative_date, validate_date_range


class TestDateParser:
    """Test relative and absolute date parsing."""

    def test_parse_relative_days(self):
        """Test parsing relative days (7d, 30d)."""
        result = parse_relative_date("7d")
        expected = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_relative_weeks(self):
        """Test parsing relative weeks (2w, 4w)."""
        result = parse_relative_date("2w")
        expected = datetime.now(timezone.utc) - timedelta(weeks=2)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_yesterday(self):
        """Test parsing 'yesterday' keyword."""
        result = parse_relative_date("yesterday")
        expected = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_today(self):
        """Test parsing 'today' keyword."""
        result = parse_relative_date("today")
        now = datetime.now(timezone.utc)
        
        # Today should be very close to now (same date)
        assert result.date() == now.date()
        # Should be start of day (00:00:00)
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0

    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow' keyword."""
        result = parse_relative_date("tomorrow")
        expected = datetime.now(timezone.utc) + timedelta(days=1)
        
        # Should be start of tomorrow
        assert result.date() == expected.date()
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0

    def test_parse_week_references(self):
        """Test parsing week reference keywords."""
        now = datetime.now(timezone.utc)
        
        # last-week should be roughly 7 days ago
        result = parse_relative_date("last-week")
        assert result < now
        days_diff = (now - result).days
        assert 5 <= days_diff <= 9, f"Expected 5-9 days, got {days_diff}"  # Allow some variance for week boundaries
        
        # this-week should be recent (within current week)
        result = parse_relative_date("this-week") 
        assert result <= now
        assert (now - result).days <= 7

    def test_parse_month_references(self):
        """Test parsing month reference keywords."""
        now = datetime.now(timezone.utc)
        
        # last-month should be roughly 30 days ago
        result = parse_relative_date("last-month")
        assert result < now
        days_diff = (now - result).days
        assert 25 <= days_diff <= 35, f"Expected 25-35 days, got {days_diff}"
        
        # this-month should be within current month
        result = parse_relative_date("this-month")
        assert result <= now
        assert result.month == now.month
        assert result.year == now.year

    def test_parse_year_references(self):
        """Test parsing year reference keywords."""
        now = datetime.now(timezone.utc)
        
        # last-year should be roughly 365 days ago
        result = parse_relative_date("last-year")
        assert result < now
        days_diff = (now - result).days
        assert 360 <= days_diff <= 370, f"Expected 360-370 days, got {days_diff}"
        
        # this-year should be within current year
        result = parse_relative_date("this-year")
        assert result <= now
        assert result.year == now.year

    def test_parse_relative_hours(self):
        """Test parsing relative hours (2h, 12h, 24h)."""
        result = parse_relative_date("2h")
        expected = datetime.now(timezone.utc) - timedelta(hours=2)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1
        
        result = parse_relative_date("24h")
        expected = datetime.now(timezone.utc) - timedelta(hours=24)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_relative_minutes(self):
        """Test parsing relative minutes (30m, 90m)."""
        result = parse_relative_date("30m")
        expected = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1
        
        result = parse_relative_date("90m")
        expected = datetime.now(timezone.utc) - timedelta(minutes=90)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_relative_months(self):
        """Test parsing relative months (1M, 3M, 6M)."""
        # Test 1 month ago - verify it's approximately 1 month
        now = datetime.now(timezone.utc)
        result = parse_relative_date("1M")
        
        # Should be in the past and roughly 1 month ago (25-35 days)
        assert result < now
        days_diff = (now - result).days
        assert 25 <= days_diff <= 35, f"Expected 25-35 days, got {days_diff}"
        
        # Test 3 months ago - just verify it parses without error and is reasonable
        result = parse_relative_date("3M")
        assert result < now
        assert (now - result).days > 80  # Should be roughly 3 months (80+ days)

    def test_parse_relative_years(self):
        """Test parsing relative years (1y, 2y)."""
        result = parse_relative_date("1y")
        expected = datetime.now(timezone.utc) - timedelta(days=365)  # Approximate 365 days per year
        
        # Allow 2 day tolerance for year approximation
        assert abs((result - expected).total_seconds()) < 2 * 24 * 3600
        
        result = parse_relative_date("2y")
        expected = datetime.now(timezone.utc) - timedelta(days=730)  # Approximate 730 days for 2 years
        assert abs((result - expected).total_seconds()) < 2 * 24 * 3600

    def test_parse_absolute_date(self):
        """Test parsing absolute date (YYYY-MM-DD)."""
        result = parse_relative_date("2025-06-01")
        expected = datetime(2025, 6, 1, tzinfo=timezone.utc)
        
        assert result == expected

    def test_parse_weekday_names(self):
        """Test parsing weekday names (monday, tuesday, etc.)."""
        now = datetime.now(timezone.utc)
        
        # Test full weekday names
        for weekday in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            result = parse_relative_date(weekday)
            assert result <= now, f"{weekday} should be in the past or present"
            # Should be within the last 7 days
            assert (now - result).days <= 7, f"{weekday} should be within last 7 days"
        
        # Test abbreviated weekday names
        for weekday in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            result = parse_relative_date(weekday)
            assert result <= now, f"{weekday} should be in the past or present"
            assert (now - result).days <= 7, f"{weekday} should be within last 7 days"

    def test_parse_relative_weekdays(self):
        """Test parsing relative weekday references (last-friday, next-monday)."""
        now = datetime.now(timezone.utc)
        
        # Test last-weekday (should be in the past)
        result = parse_relative_date("last-friday")
        assert result < now, "last-friday should be in the past"
        assert (now - result).days <= 7, "last-friday should be within last 7 days"
        assert result.weekday() == 4, "last-friday should be a Friday (weekday 4)"

    def test_parse_invalid_format_raises_error(self):
        """Test that invalid date formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_relative_date("next-week")  # Not implemented yet
            
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_relative_date("invalid")
            
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_relative_date("2025-13-01")  # Invalid month

    def test_validate_date_range_valid(self):
        """Test date range validation with valid range."""
        since = datetime(2025, 6, 1, tzinfo=timezone.utc)
        until = datetime(2025, 6, 30, tzinfo=timezone.utc)
        
        # Should not raise any exception
        validate_date_range(since, until)

    def test_validate_date_range_invalid(self):
        """Test date range validation with invalid range (since > until)."""
        since = datetime(2025, 6, 30, tzinfo=timezone.utc)
        until = datetime(2025, 6, 1, tzinfo=timezone.utc)
        
        with pytest.raises(ValueError, match="Invalid date range"):
            validate_date_range(since, until)

    def test_validate_date_range_none_values(self):
        """Test date range validation with None values."""
        # Should not raise any exception when values are None
        validate_date_range(None, None)
        validate_date_range(datetime.now(timezone.utc), None)
        validate_date_range(None, datetime.now(timezone.utc))