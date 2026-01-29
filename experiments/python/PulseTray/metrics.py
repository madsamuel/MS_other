"""System metrics collection using psutil."""
import psutil
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MetricSnapshot:
    """Snapshot of system metrics at a point in time."""
    
    timestamp: datetime
    cpu_percent: float  # 0-100
    mem_percent: float  # 0-100
    disk_percent: float  # 0-100
    net_up_bps: float  # bytes per second
    net_down_bps: float  # bytes per second
    uptime_seconds: int  # system uptime
    temp_celsius: Optional[float] = None  # CPU temperature if available
    gpu_percent: Optional[float] = None  # GPU utilization if available
    
    def __repr__(self) -> str:
        return (
            f"MetricSnapshot(time={self.timestamp.strftime('%H:%M:%S')}, "
            f"cpu={self.cpu_percent:.1f}%, mem={self.mem_percent:.1f}%, "
            f"disk={self.disk_percent:.1f}%, "
            f"up={self.net_up_bps/1024:.1f}KB/s, "
            f"down={self.net_down_bps/1024:.1f}KB/s)"
        )


class MetricsCollector:
    """Collect system metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.last_net_io = psutil.net_io_counters()
        self.last_timestamp = datetime.now()
    
    def collect(self) -> MetricSnapshot:
        """Collect current system metrics."""
        now = datetime.now()
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        
        # Disk
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent
        
        # Network (calculate bytes per second)
        current_net_io = psutil.net_io_counters()
        time_delta = (now - self.last_timestamp).total_seconds()
        
        if time_delta > 0:
            net_up_bps = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta
            net_down_bps = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta
        else:
            net_up_bps = net_down_bps = 0.0
        
        self.last_net_io = current_net_io
        self.last_timestamp = now
        
        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = int(now.timestamp() - boot_time)
        
        # Temperature (optional, may fail on some systems)
        temp_celsius = self._get_cpu_temp()
        
        return MetricSnapshot(
            timestamp=now,
            cpu_percent=cpu_percent,
            mem_percent=mem_percent,
            disk_percent=disk_percent,
            net_up_bps=net_up_bps,
            net_down_bps=net_down_bps,
            uptime_seconds=uptime_seconds,
            temp_celsius=temp_celsius,
        )
    
    @staticmethod
    def _get_cpu_temp() -> Optional[float]:
        """Try to get CPU temperature."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to get main CPU temp
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except (AttributeError, OSError):
            pass
        return None
    
    @staticmethod
    def format_bytes(bytes_val: float) -> str:
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
    
    @staticmethod
    def format_uptime(seconds: int) -> str:
        """Format uptime in human-readable format."""
        days = seconds // (24 * 3600)
        hours = (seconds % (24 * 3600)) // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
