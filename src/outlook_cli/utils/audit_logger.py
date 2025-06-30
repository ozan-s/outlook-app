"""Audit logging utilities for Outlook CLI operations."""

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class AuditEntry:
    """Container for audit log entries."""
    
    timestamp: datetime
    operation: str
    user: str
    details: Dict[str, Any]
    result_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation,
            "user": self.user,
            "details": self.details,
            "result_count": self.result_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create AuditEntry from dictionary."""
        timestamp_str = data["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str)
        
        return cls(
            timestamp=timestamp,
            operation=data["operation"],
            user=data["user"],
            details=data["details"],
            result_count=data["result_count"]
        )


class AuditLogger:
    """Logger for audit trail of Outlook CLI operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize audit logger.
        
        Args:
            log_file: Path to audit log file. If None, uses default.
        """
        self._log_file = log_file or "outlook_cli_audit.log"
        self._enabled = os.environ.get('OUTLOOK_CLI_AUDIT_ENABLED', 'true').lower() == 'true'
        
        # Create log directory if needed
        if self._enabled:
            log_path = Path(self._log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_filter_operation(self, operation: str, filters: Dict[str, Any], 
                           user: str, result_count: int) -> None:
        """Log a filter operation.
        
        Args:
            operation: Name of the operation (read, find, etc.)
            filters: Dictionary of applied filters
            user: User performing the operation
            result_count: Number of results returned
        """
        if not self._enabled:
            return
        
        entry = AuditEntry(
            timestamp=datetime.now(),
            operation=operation,
            user=user,
            details={"filters": filters, "type": "filter_operation"},
            result_count=result_count
        )
        
        self._write_entry(entry)
    
    def log_performance_metrics(self, operation: str, duration_seconds: float,
                              memory_used_mb: float, result_count: int) -> None:
        """Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration_seconds: Time taken for operation
            memory_used_mb: Memory used during operation
            result_count: Number of results processed
        """
        if not self._enabled:
            return
        
        entry = AuditEntry(
            timestamp=datetime.now(),
            operation=operation,
            user=os.environ.get('USER', 'unknown'),
            details={
                "type": "performance_metrics",
                "duration_seconds": duration_seconds,
                "memory_used_mb": memory_used_mb
            },
            result_count=result_count
        )
        
        self._write_entry(entry)
    
    def get_audit_entries(self, limit: int = 100) -> List[AuditEntry]:
        """Get recent audit entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of AuditEntry objects
        """
        if not self._enabled or not os.path.exists(self._log_file):
            return []
        
        entries = []
        try:
            with open(self._log_file, 'r') as f:
                lines = f.readlines()
                
            # Take last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in recent_lines:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        entry = AuditEntry.from_dict(data)
                        entries.append(entry)
                    except (json.JSONDecodeError, KeyError):
                        # Skip malformed entries
                        continue
        except IOError:
            # Handle file read errors gracefully
            pass
        
        return entries
    
    def _write_entry(self, entry: AuditEntry) -> None:
        """Write an audit entry to the log file.
        
        Args:
            entry: AuditEntry to write
        """
        try:
            with open(self._log_file, 'a') as f:
                json_data = json.dumps(entry.to_dict())
                f.write(json_data + '\n')
        except IOError:
            # Handle write errors gracefully - don't crash the application
            pass