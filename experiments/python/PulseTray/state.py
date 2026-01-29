"""State management and data storage for metrics history."""
from collections import deque
from typing import List, Optional
from datetime import datetime, timedelta
from metrics import MetricSnapshot


class MetricsStore:
    """Ring buffer to store metric history."""
    
    def __init__(self, max_minutes: int = 10):
        """Initialize metrics store.
        
        Args:
            max_minutes: Maximum history to keep (assuming 1 snapshot per second)
        """
        self.max_size = max_minutes * 60  # 1 snapshot per second
        self.metrics: deque = deque(maxlen=self.max_size)
        self.current_snapshot: Optional[MetricSnapshot] = None
        self.alert_state = {
            "cpu": False,
            "memory": False,
            "disk": False,
        }
    
    def add(self, snapshot: MetricSnapshot) -> None:
        """Add a metric snapshot to history."""
        self.metrics.append(snapshot)
        self.current_snapshot = snapshot
    
    def get_latest(self) -> Optional[MetricSnapshot]:
        """Get the most recent snapshot."""
        return self.current_snapshot
    
    def get_history(self, minutes: int = None) -> List[MetricSnapshot]:
        """Get metric history.
        
        Args:
            minutes: How many minutes back to retrieve. None = all.
        
        Returns:
            List of MetricSnapshot sorted by timestamp.
        """
        if minutes is None:
            return list(self.metrics)
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics if m.timestamp >= cutoff]
    
    def get_avg_cpu(self, minutes: int = 1) -> float:
        """Get average CPU usage over last N minutes."""
        history = self.get_history(minutes)
        if not history:
            return 0.0
        return sum(m.cpu_percent for m in history) / len(history)
    
    def get_avg_memory(self, minutes: int = 1) -> float:
        """Get average memory usage over last N minutes."""
        history = self.get_history(minutes)
        if not history:
            return 0.0
        return sum(m.mem_percent for m in history) / len(history)
    
    def get_avg_disk(self, minutes: int = 1) -> float:
        """Get average disk usage over last N minutes."""
        history = self.get_history(minutes)
        if not history:
            return 0.0
        return sum(m.disk_percent for m in history) / len(history)
    
    def get_max_cpu(self, minutes: int = 1) -> float:
        """Get peak CPU usage over last N minutes."""
        history = self.get_history(minutes)
        if not history:
            return 0.0
        return max(m.cpu_percent for m in history)
    
    def get_max_memory(self, minutes: int = 1) -> float:
        """Get peak memory usage over last N minutes."""
        history = self.get_history(minutes)
        if not history:
            return 0.0
        return max(m.mem_percent for m in history)
    
    def set_alert(self, metric: str, active: bool) -> bool:
        """Set alert state. Returns True if state changed."""
        if metric not in self.alert_state:
            return False
        
        old_state = self.alert_state[metric]
        self.alert_state[metric] = active
        return old_state != active
    
    def is_alerting(self, metric: str = None) -> bool:
        """Check if any alerts are active."""
        if metric:
            return self.alert_state.get(metric, False)
        return any(self.alert_state.values())
