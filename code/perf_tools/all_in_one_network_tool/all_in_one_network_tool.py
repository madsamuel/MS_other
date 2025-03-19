import sys
import logging
import json
import os
import traceback
import random
import time
import heapq
import ctypes

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox,
    QComboBox
)
from PySide6.QtCore import QThread, Signal

try:
    import pywintypes
    import win32con
    from win32com.shell.shell import ShellExecuteEx
    import wmi
    pywin32_available = True
except ImportError:
    pywin32_available = False

try:
    import pydivert
except ImportError:
    print("Error: pydivert is not installed. Please run: pip install pydivert")
    sys.exit(1)

# Configure logging to file "network_throttler.log"
logging.basicConfig(
    level=logging.ERROR,
    filename="network_throttler.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CONFIG_FILE = "config.json"


def is_admin():
    """Check if the current user has administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate_privileges():
    """Attempt to relaunch this script with administrator privileges."""
    params = {
        "verb": "runas",
        "file": sys.executable,
        "parameters": " ".join(sys.argv),
        "show": win32con.SW_SHOWNORMAL
    }
    try:
        ShellExecuteEx(**params)
        return True
    except Exception as e:
        logging.error(f"Failed to elevate privileges: {e}")
        print("Failed to elevate privileges. Please run as administrator.")
        return False


class ShaperThread(QThread):
    """
    A QThread that uses WinDivert to capture IPv4 traffic,
    applying user-defined latency, jitter, and packet loss.

    The filter used depends on the 'direction' parameter.
    IMPORTANT: We use a 'with pydivert.WinDivert(...) as w' block and do NOT call
    w.open() manually. The 'with' block automatically opens and later closes the handle.
    """
    finished = Signal()
    error = Signal(str)

    def __init__(self, latency_ms, jitter_ms, loss_percent, direction):
        super().__init__()
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.loss_percent = loss_percent
        self.direction = direction  # Expected: "Inbound", "Outbound", or "Both"
        self.packet_queue = []      # Priority queue: (release_time, packet)
        self.running = True
        self.max_queue_length = 1000  # Safety limit to avoid runaway memory usage

    def run(self):
        """
        Main logic: capture packets based on the chosen direction,
        apply latency/jitter/loss, and re-inject.
        """
        # Build the filter string based on the selected direction.
        if self.direction == "Inbound":
            filter_str = "ip and inbound"
        elif self.direction == "Both":
            filter_str = "ip and (inbound or outbound)"
        else:
            filter_str = "ip and outbound"

        consecutive_drops = 0

        try:
            with pydivert.WinDivert(filter_str) as w:
                # 'with' automatically opens the handle.
                while self.running:
                    try:
                        packet = w.recv()  # Blocking call.
                    except OSError:
                        break  # Handle closed externally.

                    # Apply packet loss.
                    if random.uniform(0, 100) < self.loss_percent:
                        consecutive_drops += 1
                        if consecutive_drops > 3:
                            logging.warning("More than 3 consecutive packets dropped.")
                        continue
                    else:
                        consecutive_drops = 0

                    # Compute delay (latency + random jitter).
                    delay_s = self.latency_ms / 1000.0
                    if self.jitter_ms > 0:
                        delay_s += random.uniform(0, self.jitter_ms) / 1000.0
                    release_time = time.time() + delay_s

                    # Enqueue the packet if within queue limit.
                    if len(self.packet_queue) < self.max_queue_length:
                        heapq.heappush(self.packet_queue, (release_time, packet))
                    else:
                        logging.error("Packet queue exceeded maximum length; dropping packet.")

                    self._release_due_packets(w)
                    time.sleep(0.005)

                # Release any remaining packets.
                self._release_remaining_packets(w)
            self.finished.emit()
        except Exception as e:
            tb_str = traceback.format_exc()
            logging.error(f"ShaperThread error: {tb_str}")
            self.error.emit(tb_str)

    def stop(self):
        """Signal the thread to stop."""
        self.running = False

    def _release_due_packets(self, w):
        now = time.time()
        while self.packet_queue and self.packet_queue[0][0] <= now:
            _, pkt = heapq.heappop(self.packet_queue)
            try:
                w.send(pkt)
            except Exception as e:
                logging.error(f"Error sending packet: {e}")

    def _release_remaining_packets(self, w):
        while self.packet_queue:
            _, pkt = heapq.heappop(self.packet_queue)
            try:
                w.send(pkt)
            except Exception as e:
                logging.error(f"Error sending remaining packet: {e}")


class NetworkThrottler(QMainWindow):
    """
    Main PySide6 window to configure latency, jitter, packet loss, and traffic direction.
    Uses ShaperThread to apply shaping using WinDivert.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Throttler (PySide6 + WinDivert) - Direction Control")
        self.setGeometry(100, 100, 450, 350)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.form_layout = QFormLayout()

        # Optional adapter selection (not used in filtering in this example)
        self.adapter_combo = QComboBox()
        # New ComboBox for selecting traffic direction.
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Outbound", "Inbound", "Both"])

        self.latency_spin = QSpinBox()
        self.jitter_spin = QSpinBox()
        self.packet_loss_spin = QDoubleSpinBox()
        self.apply_button = QPushButton("Apply")
        self.reset_button = QPushButton("Reset")

        self.setup_ui()
        self.load_config()

        self.shaper_thread = None

    def setup_ui(self):
        self.form_layout.addRow(QLabel("Network Adapter (optional):"), self.adapter_combo)
        self.form_layout.addRow(QLabel("Direction:"), self.direction_combo)
        self.form_layout.addRow(QLabel("Latency (ms):"), self.latency_spin)
        self.form_layout.addRow(QLabel("Jitter (ms):"), self.jitter_spin)
        self.form_layout.addRow(QLabel("Packet Loss (%):"), self.packet_loss_spin)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.apply_button)
        self.layout.addWidget(self.reset_button)

        self.latency_spin.setRange(0, 10000)
        self.jitter_spin.setRange(0, 10000)
        self.packet_loss_spin.setRange(0, 100)
        self.packet_loss_spin.setDecimals(2)

        self.apply_button.clicked.connect(self.apply_settings)
        self.reset_button.clicked.connect(self.reset_settings)

        if pywin32_available:
            try:
                c = wmi.WMI()
                for interface in c.Win32_NetworkAdapter():
                    if interface.NetConnectionID:
                        self.adapter_combo.addItem(interface.NetConnectionID)
            except Exception as e:
                logging.error(f"Error populating adapter list: {e}")

    def apply_settings(self):
        """Start shaping with the chosen parameters and direction."""
        if self.shaper_thread and self.shaper_thread.isRunning():
            self.stop_shaper_thread()

        latency = self.latency_spin.value()
        jitter = self.jitter_spin.value()
        loss = self.packet_loss_spin.value()
        direction = self.direction_combo.currentText()

        self.save_config()

        self.shaper_thread = ShaperThread(latency, jitter, loss, direction)
        self.shaper_thread.finished.connect(self.on_shaper_finished)
        self.shaper_thread.error.connect(self.on_shaper_error)
        self.shaper_thread.start()

        QMessageBox.information(self, "Shaping Started",
                                f"Network shaping ({direction}) has started.")

    def reset_settings(self):
        """Reset shaping to normal (0 latency, jitter, and packet loss)."""
        if self.shaper_thread and self.shaper_thread.isRunning():
            self.stop_shaper_thread()

        direction = self.direction_combo.currentText()
        self.shaper_thread = ShaperThread(0, 0, 0.0, direction)
        self.shaper_thread.finished.connect(self.on_shaper_finished)
        self.shaper_thread.error.connect(self.on_shaper_error)
        self.shaper_thread.start()

        self.latency_spin.setValue(0)
        self.jitter_spin.setValue(0)
        self.packet_loss_spin.setValue(0)
        self.save_config()

        QMessageBox.information(self, "Shaping Reset", "All shaping has been reset to normal (0).")

    def stop_shaper_thread(self):
        if self.shaper_thread:
            self.shaper_thread.stop()
            self.shaper_thread.wait()

    def on_shaper_finished(self):
        QMessageBox.information(self, "Finished", "Shaper thread finished or stopped.")

    def on_shaper_error(self, message):
        QMessageBox.critical(self, "Error in Shaper Thread", message)

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                self.latency_spin.setValue(config.get("latency", 0))
                self.jitter_spin.setValue(config.get("jitter", 0))
                self.packet_loss_spin.setValue(config.get("packet_loss", 0.0))
                # Optionally load saved direction if desired.
        except Exception as e:
            logging.error(f"Error loading config: {e}")

    def save_config(self):
        try:
            config = {
                "latency": self.latency_spin.value(),
                "jitter": self.jitter_spin.value(),
                "packet_loss": self.packet_loss_spin.value()
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def closeEvent(self, event):
        self.stop_shaper_thread()
        super().closeEvent(event)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook: log and show error message."""
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Main thread crashed with exception:\n{tb}")
    app = QApplication.instance()
    if app:
        QMessageBox.critical(None, "Fatal Error", str(exc_value))


def main():
    try:
        if not is_admin():
            print("Not running as admin, attempting to elevate privileges...")
            if elevate_privileges():
                sys.exit(0)
            else:
                print("Failed to elevate. Exiting.")
                sys.exit(1)

        qt_app = QApplication(sys.argv)
        sys.excepthook = handle_exception

        window = NetworkThrottler()
        window.show()

        sys.exit(qt_app.exec())
    except Exception:
        logging.exception("Exception in main()")
        raise


if __name__ == "__main__":
    main()