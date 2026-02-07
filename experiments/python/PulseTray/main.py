"""Main PulseTray application."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread
from PySide6.QtGui import QIcon

from config import Config
from metrics import MetricsCollector
from state import MetricsStore
from alerts import AlertManager
from tray import SystemTrayIcon
from details_window import DetailsWindow
from settings_window import SettingsWindow


class PulseTrayCoreApp:
    """Core application logic."""
    
    def __init__(self):
        """Initialize PulseTray application."""
        # Configuration
        self.config = Config()
        
        # Metrics and state
        self.collector = MetricsCollector()
        self.store = MetricsStore(self.config.get("history_minutes"))
        self.alert_manager = AlertManager()
        
        # UI Components
        self.tray_icon = SystemTrayIcon()
        self.details_window = None
        self.settings_window = None
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._collect_metrics)
        
        # Alert callbacks
        self.alert_manager.on_alert(self._on_alert_triggered)
        self.alert_manager.on_alert_clear(self._on_alert_cleared)
        
        # Connect tray signals
        self.tray_icon.signals.show_details.connect(self.show_details_window)
        self.tray_icon.signals.pause_monitoring.connect(self._on_pause)
        self.tray_icon.signals.resume_monitoring.connect(self._on_resume)
        self.tray_icon.signals.export_snapshot.connect(self._on_export)
        self.tray_icon.signals.quit_app.connect(self._on_quit)
        
        # Add settings option if tray has it
        try:
            self.tray_icon.signals.show_settings.connect(self.show_settings_window)
        except AttributeError:
            pass  # Settings not in tray signals yet
        
        self.running = True
        self.paused = False
    
    def start(self) -> None:
        """Start the application."""
        # Show tray icon
        self.tray_icon.show()
        
        # Start metrics collection
        poll_interval = int(self.config.get("poll_interval") * 1000)
        self.update_timer.start(poll_interval)
        
        print(f"PulseTray started. Polling every {poll_interval}ms")
    
    def stop(self) -> None:
        """Stop the application."""
        self.running = False
        self.update_timer.stop()
        if self.details_window:
            self.details_window.close()
        self.tray_icon.hide()
        QApplication.quit()
    
    def _collect_metrics(self) -> None:
        """Collect metrics and update UI."""
        if self.paused:
            return
        
        try:
            # Collect snapshot
            snapshot = self.collector.collect()
            self.store.add(snapshot)
            
            # Check thresholds
            self._check_alerts(snapshot)
            
            # Update tray tooltip
            tooltip = (
                f"CPU: {snapshot.cpu_percent:.1f}%\n"
                f"Memory: {snapshot.mem_percent:.1f}%\n"
                f"Disk: {snapshot.disk_percent:.1f}%\n"
                f"↑ {snapshot.net_up_bps / (1024*1024):.2f} MB/s "
                f"↓ {snapshot.net_down_bps / (1024*1024):.2f} MB/s"
            )
            self.tray_icon.set_tooltip(tooltip)
            
            # Update details window if open
            if self.details_window and self.details_window.isVisible():
                self.details_window.update_metrics(snapshot)
        
        except Exception as e:
            print(f"Error collecting metrics: {e}")
    
    def _check_alerts(self, snapshot) -> None:
        """Check metric thresholds and manage alerts."""
        cpu_threshold = self.config.get("cpu_alert")
        mem_threshold = self.config.get("memory_alert")
        disk_threshold = self.config.get("disk_alert")
        alert_duration = self.config.get("alert_duration_seconds")
        
        # Check each metric
        self.alert_manager.check_cpu(
            snapshot.cpu_percent,
            cpu_threshold,
            alert_duration
        )
        self.alert_manager.check_memory(
            snapshot.mem_percent,
            mem_threshold
        )
        self.alert_manager.check_disk(
            snapshot.disk_percent,
            disk_threshold
        )
        
        # Update tray icon alert state
        self.tray_icon.set_alert_active(self.alert_manager.has_alert())
    
    def _on_alert_triggered(self, alert) -> None:
        """Handle alert triggered."""
        print(f"ALERT: {alert.message}")
        
        if self.config.get("show_notifications"):
            try:
                from PySide6.QtWidgets import QMessageBox, QApplication
                # Note: In a real app, use proper desktop notifications
                # For now, just print
                pass
            except Exception as e:
                print(f"Notification error: {e}")
    
    def _on_alert_cleared(self, metric: str) -> None:
        """Handle alert cleared."""
        print(f"Alert cleared: {metric}")
    
    def show_details_window(self) -> None:
        """Show or focus the details window."""
        if self.details_window is None:
            self.details_window = DetailsWindow()
            self.details_window.closed.connect(self._on_details_closed)
            self.details_window.set_thresholds(
                self.config.get("cpu_alert"),
                self.config.get("memory_alert"),
                self.config.get("disk_alert"),
            )
        
        if self.store.get_latest():
            self.details_window.update_metrics(self.store.get_latest())
        
        self.details_window.show()
        self.details_window.raise_()
        self.details_window.activateWindow()
    
    def _on_details_closed(self) -> None:
        """Handle details window closed."""
        self.details_window = None
    
    def show_settings_window(self) -> None:
        """Show or focus the settings window."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.config)
            # Connect to close event via destroyed signal
            self.settings_window.destroyed.connect(self._on_settings_closed)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def _on_settings_closed(self) -> None:
        """Handle settings window closed."""
        self.settings_window = None
    
    def _on_pause(self) -> None:
        """Handle pause monitoring."""
        self.paused = True
        print("Monitoring paused")
    
    def _on_resume(self) -> None:
        """Handle resume monitoring."""
        self.paused = False
        print("Monitoring resumed")
    
    def _on_export(self) -> None:
        """Export current snapshot."""
        import csv
        from datetime import datetime
        
        try:
            export_path = Path.home() / "PulseTray_Export.csv"
            
            history = self.store.get_history(minutes=10)
            
            with open(export_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "CPU %", "Memory %", "Disk %",
                    "Upload MB/s", "Download MB/s"
                ])
                
                for snapshot in history:
                    writer.writerow([
                        snapshot.timestamp.isoformat(),
                        f"{snapshot.cpu_percent:.1f}",
                        f"{snapshot.mem_percent:.1f}",
                        f"{snapshot.disk_percent:.1f}",
                        f"{snapshot.net_up_bps / (1024*1024):.2f}",
                        f"{snapshot.net_down_bps / (1024*1024):.2f}",
                    ])
            
            print(f"Exported metrics to {export_path}")
            
            # Show notification
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    None,
                    "Export Successful",
                    f"Metrics exported to:\n{export_path}"
                )
            except Exception:
                pass
        
        except Exception as e:
            print(f"Export failed: {e}")
    
    def _on_quit(self) -> None:
        """Handle quit request."""
        self.stop()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Create and start app
    pulse_tray = PulseTrayCoreApp()
    pulse_tray.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
