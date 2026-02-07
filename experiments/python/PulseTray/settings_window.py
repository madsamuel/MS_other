"""Settings window for PulseTray."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QSpinBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class MetricToggle(QWidget):
    """Custom widget for metric toggle."""
    
    toggled = Signal(bool)
    
    def __init__(self, name: str, enabled: bool = True):
        """Initialize metric toggle."""
        super().__init__()
        self.name = name
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Metric name
        label = QLabel(name)
        label.setFont(QFont("Segoe UI", 11))
        label.setMinimumWidth(150)
        
        # Toggle checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(enabled)
        self.checkbox.toggled.connect(self.toggled.emit)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(self.checkbox)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                border-bottom: 1px solid #e0e0e0;
            }
        """)
    
    def is_enabled(self) -> bool:
        """Check if metric is enabled."""
        return self.checkbox.isChecked()


class SettingsWindow(QMainWindow):
    """Settings window for PulseTray."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, config):
        """Initialize settings window."""
        super().__init__()
        self.config = config
        self.setWindowTitle("PulseTray Settings")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
        """)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Monitoring Preferences")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("padding: 20px 20px 10px 20px; color: #1a1a1a;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("Enable or disable monitoring for each metric")
        subtitle.setStyleSheet("padding: 0px 20px 15px 20px; color: #666; font-size: 11px;")
        main_layout.addWidget(subtitle)
        
        # Scroll area for metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # Metric toggles
        self.metrics = {}
        
        # Get current settings
        cpu_enabled = self.config.get("monitor_cpu", True)
        mem_enabled = self.config.get("monitor_memory", True)
        disk_enabled = self.config.get("monitor_disk", True)
        net_up_enabled = self.config.get("monitor_network_upload", True)
        net_down_enabled = self.config.get("monitor_network_download", True)
        
        metrics_list = [
            ("CPU Usage", cpu_enabled),
            ("Memory Usage", mem_enabled),
            ("Disk Usage", disk_enabled),
            ("Network Upload", net_up_enabled),
            ("Network Download", net_down_enabled),
        ]
        
        for metric_name, enabled in metrics_list:
            toggle = MetricToggle(metric_name, enabled)
            toggle.toggled.connect(lambda checked, name=metric_name: self._on_metric_toggled(name, checked))
            self.metrics[metric_name] = toggle
            scroll_layout.addWidget(toggle)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll)
        
        # Separator
        separator = QLabel()
        separator.setStyleSheet("border-top: 1px solid #e0e0e0;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # Settings section
        settings_container = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 15, 20, 15)
        
        # Poll interval
        poll_layout = QHBoxLayout()
        poll_label = QLabel("Poll Interval (seconds):")
        poll_label.setMinimumWidth(150)
        
        self.poll_spinbox = QSpinBox()
        self.poll_spinbox.setRange(0.1, 60)
        self.poll_spinbox.setSingleStep(0.5)
        self.poll_spinbox.setValue(self.config.get("poll_interval", 2))
        self.poll_spinbox.setMaximumWidth(80)
        self.poll_spinbox.valueChanged.connect(self._on_poll_interval_changed)
        
        poll_layout.addWidget(poll_label)
        poll_layout.addStretch()
        poll_layout.addWidget(self.poll_spinbox)
        settings_layout.addLayout(poll_layout)
        
        settings_container.setLayout(settings_layout)
        settings_container.setStyleSheet("background-color: white;")
        main_layout.addWidget(settings_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 15, 20, 15)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        main_widget.setLayout(main_layout)
    
    def _on_metric_toggled(self, metric_name: str, enabled: bool) -> None:
        """Handle metric toggle."""
        # Map display names to config keys
        config_map = {
            "CPU Usage": "monitor_cpu",
            "Memory Usage": "monitor_memory",
            "Disk Usage": "monitor_disk",
            "Network Upload": "monitor_network_upload",
            "Network Download": "monitor_network_download",
        }
        
        config_key = config_map.get(metric_name)
        if config_key:
            self.config.set(config_key, enabled)
            self.settings_changed.emit({"metric": metric_name, "enabled": enabled})
    
    def _on_poll_interval_changed(self, value: float) -> None:
        """Handle poll interval change."""
        self.config.set("poll_interval", value)
        self.settings_changed.emit({"poll_interval": value})
    
    def closeEvent(self, event):
        """Handle window close."""
        event.accept()
