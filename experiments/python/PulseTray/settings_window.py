"""Settings window for PulseTray - Modern polished UI."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QSpinBox, QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter
from PySide6.QtCore import QTimer


class ModernToggle(QCheckBox):
    """Smooth animated toggle switch matching Windows modern style."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(54, 28))
        self.setMaximumSize(QSize(54, 28))
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
                outline: none;
            }
            QCheckBox::indicator {
                width: 54px;
                height: 28px;
                border-radius: 14px;
                background-color: #ccc;
                border: none;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
            }
            QCheckBox::indicator:hover {
                background-color: #e0e0e0;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            QCheckBox::indicator:pressed {
                background-color: #d0d0d0;
            }
            QCheckBox::indicator:checked:pressed {
                background-color: #0066b2;
            }
        """)


def create_metric_icon(name: str) -> QPixmap:
    """Create a simple icon for metric types."""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Color based on metric type
    colors = {
        "CPU Usage": QColor(255, 152, 0),      # Orange
        "Memory Usage": QColor(76, 175, 80),   # Green
        "Disk Usage": QColor(63, 81, 181),     # Blue
        "Network Upload": QColor(233, 30, 99), # Pink
        "Network Download": QColor(103, 58, 183), # Purple
    }
    
    color = colors.get(name, QColor(0, 150, 136))
    
    # Draw filled circle
    painter.setBrush(color)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 20, 20)
    
    # Draw icon based on type
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 10, QFont.Bold))
    
    if name == "CPU Usage":
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "⚡")
    elif name == "Memory Usage":
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📊")
    elif name == "Disk Usage":
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "💾")
    elif name == "Network Upload":
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "↑")
    elif name == "Network Download":
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "↓")
    
    painter.end()
    return pixmap


class MetricRow(QFrame):
    """Modern metric row with icon, name, and toggle."""
    
    toggled = Signal(bool)
    
    def __init__(self, name: str, enabled: bool = True):
        super().__init__()
        self.name = name
        
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e5e5e5;
                padding: 0px;
            }
            QFrame:hover {
                background-color: #f9f9f9;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(create_metric_icon(name))
        icon_label.setFixedSize(28, 28)
        
        # Metric name
        label = QLabel(name)
        label.setFont(QFont("Segoe UI", 10, QFont.Normal))
        label.setStyleSheet("color: #2d2d2d;")
        
        # Toggle
        self.toggle = ModernToggle()
        self.toggle.setChecked(enabled)
        self.toggle.stateChanged.connect(self._on_toggled)
        
        layout.addWidget(icon_label)
        layout.addWidget(label, 1)
        layout.addWidget(self.toggle)
        
        self.setLayout(layout)
    
    def _on_toggled(self):
        self.toggled.emit(self.toggle.isChecked())
    
    def is_enabled(self) -> bool:
        return self.toggle.isChecked()


class SettingsWindow(QMainWindow):
    """Modern polished settings window."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("PulseTray Settings")
        self.setGeometry(100, 100, 580, 750)
        self.setMinimumWidth(520)
        self.setMaximumWidth(700)
        
        # Modern color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section with gradient feel
        header_widget = QWidget()
        header_widget.setFixedHeight(140)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #e5e5e5;
            }
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(8)
        
        # Title with better typography
        title = QLabel("Monitoring Preferences")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a1a1a; letter-spacing: 0px;")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Customize which metrics to monitor")
        subtitle_font = QFont("Segoe UI", 10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #7a7a7a;")
        header_layout.addWidget(subtitle)
        
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #c5c5c5;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a5a5a5;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #f5f5f5;")
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # Metrics section background
        metrics_container = QWidget()
        metrics_container.setStyleSheet("background-color: white;")
        metrics_layout = QVBoxLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(0)
        
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
        
        self.metrics = {}
        for i, (metric_name, enabled) in enumerate(metrics_list):
            row = MetricRow(metric_name, enabled)
            row.toggled.connect(lambda checked, name=metric_name: self._on_metric_toggled(name, checked))
            self.metrics[metric_name] = row
            metrics_layout.addWidget(row)
        
        metrics_container.setLayout(metrics_layout)
        scroll_layout.addWidget(metrics_container)
        
        # Add spacing
        scroll_layout.addSpacing(12)
        
        # Settings section
        settings_container = QWidget()
        settings_container.setStyleSheet("background-color: white;")
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(12)
        
        # Section title
        section_title = QLabel("Advanced Settings")
        section_title_font = QFont("Segoe UI", 11, QFont.Bold)
        section_title.setFont(section_title_font)
        section_title.setStyleSheet("color: #1a1a1a;")
        settings_layout.addWidget(section_title)
        
        # Poll interval setting
        poll_container = QWidget()
        poll_layout = QHBoxLayout()
        poll_layout.setContentsMargins(0, 8, 0, 8)
        poll_layout.setSpacing(12)
        
        poll_label = QLabel("Poll Interval (seconds):")
        poll_label_font = QFont("Segoe UI", 10)
        poll_label.setFont(poll_label_font)
        poll_label.setStyleSheet("color: #2d2d2d;")
        
        self.poll_spinbox = QSpinBox()
        self.poll_spinbox.setRange(1, 60)
        self.poll_spinbox.setValue(int(self.config.get("poll_interval", 1)))
        self.poll_spinbox.setMaximumWidth(80)
        self.poll_spinbox.setMinimumHeight(32)
        self.poll_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 6px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 10px;
                font-weight: 500;
            }
            QSpinBox:hover {
                border: 1px solid #0078d4;
                background-color: #ffffff;
            }
            QSpinBox:focus {
                border: 2px solid #0078d4;
                background-color: #ffffff;
            }
        """)
        self.poll_spinbox.valueChanged.connect(self._on_poll_interval_changed)
        
        poll_layout.addWidget(poll_label)
        poll_layout.addStretch()
        poll_layout.addWidget(self.poll_spinbox)
        
        poll_container.setLayout(poll_layout)
        settings_layout.addWidget(poll_container)
        
        settings_container.setLayout(settings_layout)
        scroll_layout.addWidget(settings_container)
        
        # Stretch at end
        scroll_layout.addStretch()
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll)
        
        # Footer with button
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: #f5f5f5; border-top: 1px solid #e5e5e5;")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(24, 16, 24, 16)
        
        footer_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(36)
        close_btn.setFont(QFont("Segoe UI", 10, QFont.Normal))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e5e5e5;
                color: #1a1a1a;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-weight: 500;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
                border: 1px solid #b3b3b3;
            }
            QPushButton:pressed {
                background-color: #cccccc;
                border: 1px solid #a0a0a0;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        footer_layout.addWidget(close_btn)
        footer_widget.setLayout(footer_layout)
        main_layout.addWidget(footer_widget)
        
        main_widget.setLayout(main_layout)
    
    def _on_metric_toggled(self, metric_name: str, enabled: bool) -> None:
        """Handle metric toggle."""
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
    
    def _on_poll_interval_changed(self, value: int) -> None:
        """Handle poll interval change."""
        self.config.set("poll_interval", float(value))
        self.settings_changed.emit({"poll_interval": float(value)})


    
    def closeEvent(self, event):
        """Handle window close."""
        event.accept()
