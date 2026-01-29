"""System tray UI component."""
import sys
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from pathlib import Path


class TraySignals(QObject):
    """Signals for tray events."""
    show_details = Signal()
    pause_monitoring = Signal()
    resume_monitoring = Signal()
    export_snapshot = Signal()
    show_settings = Signal()
    quit_app = Signal()


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon with menu and live tooltip."""
    
    def __init__(self, parent=None):
        """Initialize system tray icon."""
        super().__init__(parent)
        self.signals = TraySignals()
        self.is_paused = False
        self.alert_active = False
        self._icon_color = QColor(0, 120, 215)  # Blue
        
        # Create tray menu
        self.menu = QMenu(parent)
        self._setup_menu()
        self.setContextMenu(self.menu)
        
        # Set initial icon
        self._update_icon()
        
        # Connect to tray activation
        self.activated.connect(self._on_tray_activated)
        
        # Tooltip timer
        self.tooltip_text = "PulseTray"
        self.setToolTip(self.tooltip_text)
    
    def _setup_menu(self) -> None:
        """Set up the context menu."""
        self.menu.clear()
        
        # Show Details
        action = self.menu.addAction("Show Details")
        action.triggered.connect(self.signals.show_details.emit)
        
        # Pause/Resume
        self.pause_action = self.menu.addAction("Pause Monitoring")
        self.pause_action.triggered.connect(self._on_pause_toggle)
        
        # Export
        action = self.menu.addAction("Export Snapshot")
        action.triggered.connect(self.signals.export_snapshot.emit)
        
        # Settings
        action = self.menu.addAction("Settings")
        action.triggered.connect(self.signals.show_settings.emit)
        
        self.menu.addSeparator()
        
        # Quit
        action = self.menu.addAction("Quit")
        action.triggered.connect(self.signals.quit_app.emit)
    
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.signals.show_details.emit()
    
    def _on_pause_toggle(self) -> None:
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_action.setText("Resume Monitoring")
            self.signals.pause_monitoring.emit()
        else:
            self.pause_action.setText("Pause Monitoring")
            self.signals.resume_monitoring.emit()
    
    def set_tooltip(self, text: str) -> None:
        """Update tooltip with metrics summary."""
        self.tooltip_text = text
        self.setToolTip(text)
    
    def set_alert_active(self, active: bool) -> None:
        """Set alert state and update icon."""
        self.alert_active = active
        self._update_icon()
    
    def _update_icon(self) -> None:
        """Update tray icon based on alert state."""
        if self.alert_active:
            # Red icon for alert
            color = QColor(255, 77, 77)  # Red
        else:
            # Blue icon for normal
            color = QColor(0, 120, 215)  # Blue
        
        # Create a simple colored square icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.Color.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Draw circle
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawEllipse(2, 2, 12, 12)
        
        painter.end()
        
        self.setIcon(QIcon(pixmap))
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active."""
        return not self.is_paused
