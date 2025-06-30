"""Date parsing utilities for relative and absolute dates."""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional


def _subtract_months(dt: datetime, months: int) -> datetime:
    """Subtract months from a datetime, handling month boundaries properly."""
    year = dt.year
    month = dt.month - months
    
    # Handle year rollover
    while month <= 0:
        month += 12
        year -= 1
    
    # Handle day overflow (e.g., Jan 31 - 1 month should be Dec 31, not Feb 31)
    day = dt.day
    try:
        return dt.replace(year=year, month=month, day=day)
    except ValueError:
        # Day doesn't exist in target month (e.g., Feb 31), use last day of month
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        return dt.replace(year=year, month=month, day=last_day)


def parse_relative_date(date_str: str) -> datetime:
    """Parse relative or absolute date string to datetime object.
    
    Args:
        date_str: Date string in formats:
            - Relative minutes: "30m", "90m"
            - Relative hours: "2h", "12h", "24h"
            - Relative days: "7d", "30d" 
            - Relative weeks: "2w", "4w"
            - Relative months: "1M", "3M", "6M" (uppercase M)
            - Relative years: "1y", "2y"
            - Named relative: "yesterday", "today", "tomorrow"
            - Week references: "last-week", "this-week"
            - Month references: "last-month", "this-month"
            - Year references: "last-year", "this-year"
            - Weekday names: "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
            - Weekday abbreviations: "mon", "tue", "wed", "thu", "fri", "sat", "sun"
            - Relative weekdays: "last-friday", "last-monday"
            - Absolute: "YYYY-MM-DD"
    
    Returns:
        datetime: UTC timezone-aware datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    # Preserve original for case-sensitive matching, but also create lowercase for some patterns
    original_date_str = date_str.strip()
    date_str = original_date_str.lower()
    
    # Security validation: reject path traversal attempts and suspicious patterns
    if any(pattern in date_str for pattern in ['..', '/', '\\', 'etc', 'passwd', 'shadow']):
        raise ValueError(f"Invalid date format: '{original_date_str}' contains suspicious characters")
    
    # Handle relative days (7d, 30d)
    days_match = re.match(r'^(\d+)d$', date_str)
    if days_match:
        days = int(days_match.group(1))
        return datetime.now(timezone.utc) - timedelta(days=days)
    
    # Handle relative weeks (2w, 4w)
    weeks_match = re.match(r'^(\d+)w$', date_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return datetime.now(timezone.utc) - timedelta(weeks=weeks)
    
    # Handle relative hours (2h, 12h, 24h)
    hours_match = re.match(r'^(\d+)h$', date_str)
    if hours_match:
        hours = int(hours_match.group(1))
        return datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Handle relative months (1M, 3M, 6M) - using uppercase 'M' for months (case-sensitive)
    # IMPORTANT: Check months BEFORE minutes to avoid confusion
    months_match = re.match(r'^(\d+)M$', original_date_str)
    if months_match:
        months = int(months_match.group(1))
        return _subtract_months(datetime.now(timezone.utc), months)
    
    # Handle relative minutes (30m, 90m) - using lowercase 'm' for minutes
    minutes_match = re.match(r'^(\d+)m$', date_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))
        return datetime.now(timezone.utc) - timedelta(minutes=minutes)
    
    # Handle relative years (1y, 2y)
    years_match = re.match(r'^(\d+)y$', date_str)
    if years_match:
        years = int(years_match.group(1))
        # Approximate years as 365 days each
        days = years * 365
        return datetime.now(timezone.utc) - timedelta(days=days)
    
    # Handle named relative dates
    if date_str == "yesterday":
        return datetime.now(timezone.utc) - timedelta(days=1)
    
    if date_str == "today":
        # Return start of today (00:00:00)
        now = datetime.now(timezone.utc)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if date_str == "tomorrow":
        # Return start of tomorrow (00:00:00)
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle week references
    if date_str == "last-week":
        return datetime.now(timezone.utc) - timedelta(weeks=1)
    
    if date_str == "this-week":
        # Return start of current week (Monday)
        now = datetime.now(timezone.utc)
        days_since_monday = now.weekday()  # Monday is 0
        start_of_week = now - timedelta(days=days_since_monday)
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle month references
    if date_str == "last-month":
        return _subtract_months(datetime.now(timezone.utc), 1)
    
    if date_str == "this-month":
        # Return start of current month
        now = datetime.now(timezone.utc)
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Handle year references  
    if date_str == "last-year":
        now = datetime.now(timezone.utc)
        return now.replace(year=now.year - 1)
    
    if date_str == "this-year":
        # Return start of current year
        now = datetime.now(timezone.utc)
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Handle weekday names (both full and abbreviated)
    weekday_names = {
        "monday": 0, "mon": 0,
        "tuesday": 1, "tue": 1, 
        "wednesday": 2, "wed": 2,
        "thursday": 3, "thu": 3,
        "friday": 4, "fri": 4,
        "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6
    }
    
    if date_str in weekday_names:
        target_weekday = weekday_names[date_str]
        now = datetime.now(timezone.utc)
        current_weekday = now.weekday()  # Monday is 0
        
        # Calculate days back to the most recent occurrence of this weekday
        days_back = (current_weekday - target_weekday) % 7
        if days_back == 0 and now.hour > 0:
            # If it's the same weekday but later in the day, go back a full week
            days_back = 7
        
        target_date = now - timedelta(days=days_back)
        return target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle relative weekday references (last-friday, next-monday, etc.)
    last_weekday_match = re.match(r'^last-(.+)$', date_str)
    if last_weekday_match:
        weekday_name = last_weekday_match.group(1)
        if weekday_name in weekday_names:
            target_weekday = weekday_names[weekday_name]
            now = datetime.now(timezone.utc)
            current_weekday = now.weekday()  # Monday is 0
            
            # Calculate days back to last occurrence of this weekday
            days_back = (current_weekday - target_weekday) % 7
            if days_back == 0:
                # If it's the same weekday, go back a full week
                days_back = 7
                
            target_date = now - timedelta(days=days_back)
            return target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle absolute dates (YYYY-MM-DD)
    date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_str)
    if date_match:
        year, month, day = map(int, date_match.groups())
        try:
            return datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
    
    raise ValueError(f"Invalid date format: {date_str}")


def validate_date_range(since: Optional[datetime], until: Optional[datetime]) -> None:
    """Validate that date range makes sense (since <= until).
    
    Args:
        since: Start date (optional)
        until: End date (optional)
        
    Raises:
        ValueError: If since > until
    """
    if since is not None and until is not None and since > until:
        raise ValueError("Invalid date range: 'since' date must be before or equal to 'until' date")