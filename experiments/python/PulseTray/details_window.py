"""Details window popup UI."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from metrics import MetricsCollector, MetricSnapshot


class MetricCard(QFrame):
    """Card widget for displaying a single metric."""
    
    def __init__(self, title: str, parent=None):
        """Initialize metric card."""
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 12px;
                background-color: #f9f9f9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("--")
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        layout.addWidget(self.value_label)
        
        # Status indicator
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    def set_value(self, value: float, unit: str = "", status: str = "normal") -> None:
        """Set the metric value and status.
        
        Args:
            value: Numeric value
            unit: Unit string (e.g., "%", "MB/s")
            status: "normal", "warning", or "critical"
        """
        self.value_label.setText(f"{value:.1f} {unit}")
        
        # Set status color
        colors = {
            "normal": QColor(76, 175, 80),  # Green
            "warning": QColor(255, 193, 7),  # Yellow
            "critical": QColor(244, 67, 54),  # Red
        }
        color = colors.get(status, colors["normal"])
        self.value_label.setStyleSheet(f"color: {color.name()};")
        
        # Set status text
        status_map = {
            "normal": "✓ Normal",
            "warning": "⚠ Warning",
            "critical": "✗ Critical",
        }
        self.status_label.setText(status_map.get(status, ""))
        self.status_label.setStyleSheet(f"color: {color.name()}; font-weight: bold;")


class DetailsWindow(QWidget):
    """Popup window showing detailed metrics."""
    
    closed = Signal()
    
    def __init__(self, parent=None):
        """Initialize details window."""
        super().__init__(parent)
        self.setWindowTitle("PulseTray - System Metrics")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        self.hostname_label = QLabel("System")
        hostname_font = QFont()
        hostname_font.setPointSize(12)
        hostname_font.setBold(True)
        self.hostname_label.setFont(hostname_font)
        header_layout.addWidget(self.hostname_label)
        
        self.uptime_label = QLabel("Uptime: --")
        header_layout.addStretch()
        header_layout.addWidget(self.uptime_label)
        
        layout.addLayout(header_layout)
        
        # Metric cards grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        self.cpu_card = MetricCard("CPU Usage")
        self.mem_card = MetricCard("Memory Usage")
        self.disk_card = MetricCard("Disk Usage")
        self.net_up_card = MetricCard("Network Upload")
        self.net_down_card = MetricCard("Network Download")
        
        grid_layout.addWidget(self.cpu_card, 0, 0)
        grid_layout.addWidget(self.mem_card, 0, 1)
        grid_layout.addWidget(self.disk_card, 1, 0)
        grid_layout.addWidget(self.net_up_card, 1, 1)
        grid_layout.addWidget(self.net_down_card, 2, 0)
        
        layout.addLayout(grid_layout)
        
        # Footer
        self.update_time_label = QLabel("Last update: --")
        self.update_time_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.update_time_label)
        
        layout.addStretch()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._request_update)
        
        self.current_snapshot = None
        self.thresholds = {"cpu": 85, "memory": 80, "disk": 90}
    
    def set_thresholds(self, cpu: float, memory: float, disk: float) -> None:
        """Set alert thresholds."""
        self.thresholds = {"cpu": cpu, "memory": memory, "disk": disk}
    
    def update_metrics(self, snapshot: MetricSnapshot) -> None:
        """Update display with new metrics."""
        self.current_snapshot = snapshot
        
        # Update hostname
        try:
            import socket
            hostname = socket.gethostname()
            self.hostname_label.setText(hostname)
        except Exception:
            self.hostname_label.setText("System")
        
        # Update uptime
        from metrics import MetricsCollector
        uptime_str = MetricsCollector.format_uptime(snapshot.uptime_seconds)
        self.uptime_label.setText(f"Uptime: {uptime_str}")
        
        # Update cards
        cpu_status = self._get_status(snapshot.cpu_percent, self.thresholds["cpu"])
        self.cpu_card.set_value(snapshot.cpu_percent, "%", cpu_status)
        
        mem_status = self._get_status(snapshot.mem_percent, self.thresholds["memory"])
        self.mem_card.set_value(snapshot.mem_percent, "%", mem_status)
        
        disk_status = self._get_status(snapshot.disk_percent, self.thresholds["disk"])
        self.disk_card.set_value(snapshot.disk_percent, "%", disk_status)
        
        # Network
        net_up_mb = snapshot.net_up_bps / (1024 * 1024)
        net_down_mb = snapshot.net_down_bps / (1024 * 1024)
        self.net_up_card.set_value(net_up_mb, "MB/s", "normal")
        self.net_down_card.set_value(net_down_mb, "MB/s", "normal")
        
        # Update time
        time_str = snapshot.timestamp.strftime("%H:%M:%S")
        self.update_time_label.setText(f"Last update: {time_str}")
    
    @staticmethod
    def _get_status(value: float, threshold: float) -> str:
        """Determine status based on threshold."""
        if value > threshold:
            return "critical"
        elif value > threshold * 0.8:
            return "warning"
        return "normal"
    
    def start_updating(self, interval_ms: int = 1000) -> None:
        """Start auto-updating metrics."""
        self.update_timer.start(interval_ms)
    
    def stop_updating(self) -> None:
        """Stop auto-updating metrics."""
        self.update_timer.stop()
    
    def _request_update(self) -> None:
        """Request update from parent."""
        # This will be connected to main app's update signal
        pass
    
    def closeEvent(self, event) -> None:
        """Handle window close."""
        self.stop_updating()
        self.closed.emit()
        event.accept()
