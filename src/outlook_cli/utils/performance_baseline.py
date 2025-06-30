"""Performance baseline tracking and regression detection."""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


@dataclass
class BaselineMetrics:
    """Container for baseline performance metrics."""
    
    operation: str
    baseline_duration: float
    baseline_memory: float
    threshold_factor: float
    recorded_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "operation": self.operation,
            "baseline_duration": self.baseline_duration,
            "baseline_memory": self.baseline_memory,
            "threshold_factor": self.threshold_factor,
            "recorded_at": self.recorded_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaselineMetrics':
        """Create BaselineMetrics from dictionary."""
        recorded_at = datetime.fromisoformat(data["recorded_at"])
        
        return cls(
            operation=data["operation"],
            baseline_duration=data["baseline_duration"],
            baseline_memory=data["baseline_memory"],
            threshold_factor=data["threshold_factor"],
            recorded_at=recorded_at
        )


class PerformanceBaseline:
    """Manager for performance baselines and regression detection."""
    
    def __init__(self, baseline_file: Optional[str] = None, threshold_factor: float = 1.2):
        """Initialize performance baseline manager.
        
        Args:
            baseline_file: Path to baseline storage file. If None, uses default.
            threshold_factor: Factor for regression detection (1.2 = 20% tolerance)
        """
        self._baseline_file = baseline_file or "outlook_cli_performance_baseline.json"
        self._threshold_factor = threshold_factor
        self._baselines: Dict[str, BaselineMetrics] = {}
        
        # Load existing baselines
        self._load_baselines()
    
    def record_baseline(self, operation: str, duration_seconds: float, memory_mb: float) -> None:
        """Record a performance baseline for an operation.
        
        Args:
            operation: Name of the operation
            duration_seconds: Baseline execution time
            memory_mb: Baseline memory usage
        """
        baseline = BaselineMetrics(
            operation=operation,
            baseline_duration=duration_seconds,
            baseline_memory=memory_mb,
            threshold_factor=self._threshold_factor,
            recorded_at=datetime.now()
        )
        
        self._baselines[operation] = baseline
        self._save_baselines()
    
    def check_regression(self, operation: str, current_duration: float, current_memory: float) -> bool:
        """Check if current performance represents a regression.
        
        Args:
            operation: Name of the operation
            current_duration: Current execution time
            current_memory: Current memory usage
            
        Returns:
            True if performance regression detected, False otherwise
        """
        baseline = self._baselines.get(operation)
        if baseline is None:
            # No baseline exists - record current performance as baseline
            self.record_baseline(operation, current_duration, current_memory)
            return False
        
        # Check if current performance exceeds threshold
        duration_threshold = baseline.baseline_duration * baseline.threshold_factor
        memory_threshold = baseline.baseline_memory * baseline.threshold_factor
        
        duration_regression = current_duration > duration_threshold
        memory_regression = current_memory > memory_threshold
        
        return duration_regression or memory_regression
    
    def get_baseline(self, operation: str) -> Optional[BaselineMetrics]:
        """Get baseline metrics for an operation.
        
        Args:
            operation: Name of the operation
            
        Returns:
            BaselineMetrics if exists, None otherwise
        """
        return self._baselines.get(operation)
    
    def _load_baselines(self) -> None:
        """Load baselines from file."""
        if not os.path.exists(self._baseline_file):
            return
        
        try:
            with open(self._baseline_file, 'r') as f:
                data = json.load(f)
            
            for operation, baseline_data in data.items():
                baseline_data["operation"] = operation
                baseline = BaselineMetrics.from_dict(baseline_data)
                self._baselines[operation] = baseline
        except (json.JSONDecodeError, KeyError, ValueError):
            # Handle corrupted baseline file gracefully
            self._baselines = {}
    
    def _save_baselines(self) -> None:
        """Save baselines to file."""
        try:
            # Create directory if it doesn't exist
            baseline_path = Path(self._baseline_file)
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert baselines to saveable format
            data = {}
            for operation, baseline in self._baselines.items():
                baseline_dict = baseline.to_dict()
                # Remove operation key since it's used as the main key
                del baseline_dict["operation"]
                data[operation] = baseline_dict
            
            with open(self._baseline_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            # Handle write errors gracefully - don't crash the application
            pass