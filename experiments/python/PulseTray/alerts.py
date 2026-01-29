"""Alert management system for threshold detection."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a single alert."""
    metric: str  # "cpu", "memory", "disk"
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_expired(self, duration_seconds: int) -> bool:
        """Check if alert has expired based on duration."""
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed > duration_seconds


class AlertManager:
    """Manage threshold-based alerts."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_callbacks = []
        self.alert_clear_callbacks = []
    
    def on_alert(self, callback: Callable[[Alert], None]) -> None:
        """Register callback for when alert is triggered."""
        self.alert_callbacks.append(callback)
    
    def on_alert_clear(self, callback: Callable[[str], None]) -> None:
        """Register callback for when alert is cleared.
        
        Args:
            callback: Called with metric name (e.g., "cpu")
        """
        self.alert_clear_callbacks.append(callback)
    
    def check_cpu(
        self,
        cpu_percent: float,
        threshold: float,
        alert_duration: int,
    ) -> Optional[Alert]:
        """Check CPU threshold.
        
        Returns:
            Alert object if triggered, None otherwise.
        """
        metric = "cpu"
        
        if cpu_percent > threshold:
            # Trigger or update alert
            if metric not in self.active_alerts:
                alert = Alert(
                    metric=metric,
                    severity=AlertSeverity.WARNING,
                    message=f"CPU usage high: {cpu_percent:.1f}%",
                    value=cpu_percent,
                    threshold=threshold,
                )
                self.active_alerts[metric] = alert
                for callback in self.alert_callbacks:
                    callback(alert)
                return alert
            else:
                # Update existing alert
                self.active_alerts[metric].value = cpu_percent
                self.active_alerts[metric].message = f"CPU usage high: {cpu_percent:.1f}%"
                self.active_alerts[metric].timestamp = datetime.now()
        else:
            # Clear alert if it exists and is expired
            if metric in self.active_alerts:
                alert = self.active_alerts[metric]
                if alert.is_expired(alert_duration):
                    del self.active_alerts[metric]
                    for callback in self.alert_clear_callbacks:
                        callback(metric)
        
        return None
    
    def check_memory(
        self,
        mem_percent: float,
        threshold: float,
    ) -> Optional[Alert]:
        """Check memory threshold."""
        metric = "memory"
        
        if mem_percent > threshold:
            if metric not in self.active_alerts:
                alert = Alert(
                    metric=metric,
                    severity=AlertSeverity.WARNING,
                    message=f"Memory usage high: {mem_percent:.1f}%",
                    value=mem_percent,
                    threshold=threshold,
                )
                self.active_alerts[metric] = alert
                for callback in self.alert_callbacks:
                    callback(alert)
                return alert
            else:
                self.active_alerts[metric].value = mem_percent
                self.active_alerts[metric].message = f"Memory usage high: {mem_percent:.1f}%"
                self.active_alerts[metric].timestamp = datetime.now()
        else:
            if metric in self.active_alerts:
                del self.active_alerts[metric]
                for callback in self.alert_clear_callbacks:
                    callback(metric)
        
        return None
    
    def check_disk(
        self,
        disk_percent: float,
        threshold: float,
    ) -> Optional[Alert]:
        """Check disk threshold."""
        metric = "disk"
        
        if disk_percent > threshold:
            if metric not in self.active_alerts:
                alert = Alert(
                    metric=metric,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Disk usage critical: {disk_percent:.1f}%",
                    value=disk_percent,
                    threshold=threshold,
                )
                self.active_alerts[metric] = alert
                for callback in self.alert_callbacks:
                    callback(alert)
                return alert
            else:
                self.active_alerts[metric].value = disk_percent
                self.active_alerts[metric].message = f"Disk usage critical: {disk_percent:.1f}%"
                self.active_alerts[metric].timestamp = datetime.now()
        else:
            if metric in self.active_alerts:
                del self.active_alerts[metric]
                for callback in self.alert_clear_callbacks:
                    callback(metric)
        
        return None
    
    def get_active_alerts(self) -> Dict[str, Alert]:
        """Get all active alerts."""
        return self.active_alerts.copy()
    
    def has_alert(self, metric: str = None) -> bool:
        """Check if any alert is active."""
        if metric:
            return metric in self.active_alerts
        return len(self.active_alerts) > 0
