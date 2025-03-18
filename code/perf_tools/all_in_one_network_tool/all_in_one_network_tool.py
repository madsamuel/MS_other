#!/usr/bin/env python3
"""
all_in_one_network_tool.py

PyQt5 + WinDivert application that injects latency, jitter, and packet loss 
for outbound IPv4 traffic on Windows. Fixes "WinDivert handle is already open." 
by ensuring only ONE handle is open at a time.

Steps to use:
1) Place WinDivert.dll and WinDivert.sys in the same folder or in your PATH.
2) pip install pydivert PyQt5
3) Run this script as Administrator (it attempts to elevate if not admin).
4) Adjust Latency/Jitter/Loss in the GUI and click "Apply" or "Reset."
"""

import sys
import logging
import json
import os
import traceback
import random
import time
import heapq
import ctypes

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox,
    QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal

try:
    import pywintypes
    import win32con
    from win32com.shell.shell import ShellExecuteEx
    import wmi
    pywin32_available = True
except ImportError:
    # We can still run without pywin32 or wmi, but can't list adapters or elevate automatically
    pywin32_available = False

try:
    import pydivert
except ImportError:
    print("Error: pydivert is not installed. Please run: pip install pydivert")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    filename="network_throttler.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CONFIG_FILE = "config.json"

def is_admin():
    """
    Check if the current user has administrative privileges.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    """
    Attempt to relaunch this script with administrator privileges.
    """
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
    A QThread that uses WinDivert to capture OUTBOUND IPv4 traffic,
    applying user-defined latency, jitter, and packet loss.
    
    IMPORTANT: We use a 'with pydivert.WinDivert(...) as w' block
    and do NOT call w.open() manually inside it. The 'with' block
    automatically opens/closes the WinDivert handle.
    """

    finished = pyqtSignal()      # Emitted when the thread finishes normally
    error = pyqtSignal(str)      # Emitted if an exception occurs

    def __init__(self, latency_ms, jitter_ms, loss_percent):
        super().__init__()
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.loss_percent = loss_percent
        self.packet_queue = []   # A priority queue (release_time, packet)
        self.running = True      # Controls the main loop

    def run(self):
        """
        Main logic: capture packets, apply netem-like latency and loss, re-inject.
        """
        filter_str = "ip and outbound"

        try:
            # The 'with' statement automatically calls w.open() at the start 
            # and w.close() at the end (closing the handle).
            with pydivert.WinDivert(filter_str) as w:
                # We do NOT call w.open() here -- 'with' has done that for us.
                while self.running:
                    # 1) recv packet
                    try:
                        packet = w.recv()
                    except OSError:
                        # If the handle was closed externally, break out
                        break

                    # 2) Packet loss
                    if random.uniform(0, 100) < self.loss_percent:
                        # Drop this packet
                        continue

                    # 3) Compute total delay
                    delay_s = self.latency_ms / 1000.0
                    if self.jitter_ms > 0:
                        delay_s += random.uniform(0, self.jitter_ms) / 1000.0

                    release_time = time.time() + delay_s

                    # 4) Push into priority queue
                    heapq.heappush(self.packet_queue, (release_time, packet))

                    # 5) Release any packets whose time has arrived
                    self._release_due_packets(w)

                    # Sleep a bit to avoid max CPU usage
                    time.sleep(0.005)

                # If the user requests stop, release everything left
                self._release_remaining_packets(w)

            # Normal finish
            self.finished.emit()

        except Exception as e:
            tb_str = traceback.format_exc()
            logging.error(f"ShaperThread error: {tb_str}")
            self.error.emit(tb_str)

    def stop(self):
        """
        Signal the thread to stop the main loop.
        """
        self.running = False

    def _release_due_packets(self, w):
        """
        Re-inject any queued packets whose time has come.
        """
        now = time.time()
        while self.packet_queue and self.packet_queue[0][0] <= now:
            _, pkt = heapq.heappop(self.packet_queue)
            w.send(pkt)

    def _release_remaining_packets(self, w):
        """
        Re-inject all remaining packets if we're stopping.
        """
        while self.packet_queue:
            _, pkt = heapq.heappop(self.packet_queue)
            w.send(pkt)


class NetworkThrottler(QMainWindow):
    """
    Main PyQt window to configure latency, jitter, loss, 
    and start/stop the ShaperThread.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Throttler (WinDivert) - Single Handle Fix")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.form_layout = QFormLayout()

        # If you want to list network adapters using WMI:
        self.adapter_combo = QComboBox()

        self.latency_spin = QSpinBox()
        self.jitter_spin = QSpinBox()
        self.packet_loss_spin = QDoubleSpinBox()
        self.apply_button = QPushButton("Apply")
        self.reset_button = QPushButton("Reset")

        self.setup_ui()
        self.load_config()

        # Keep track of the current shaping thread
        self.shaper_thread = None

    def setup_ui(self):
        self.form_layout.addRow(QLabel("Network Adapter (optional):"), self.adapter_combo)
        self.form_layout.addRow(QLabel("Latency (ms):"), self.latency_spin)
        self.form_layout.addRow(QLabel("Jitter (ms):"), self.jitter_spin)
        self.form_layout.addRow(QLabel("Packet Loss (%):"), self.packet_loss_spin)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.apply_button)
        self.layout.addWidget(self.reset_button)

        # Configure spin ranges
        self.latency_spin.setRange(0, 10_000)
        self.jitter_spin.setRange(0, 10_000)
        self.packet_loss_spin.setRange(0, 100)
        self.packet_loss_spin.setDecimals(2)

        self.apply_button.clicked.connect(self.apply_settings)
        self.reset_button.clicked.connect(self.reset_settings)

        # If pywin32 + wmi are available, list adapters
        if pywin32_available:
            try:
                c = wmi.WMI()
                for interface in c.Win32_NetworkAdapter():
                    if interface.NetConnectionID:
                        self.adapter_combo.addItem(interface.NetConnectionID)
            except:
                pass

    def apply_settings(self):
        """
        Start shaping with the chosen latency, jitter, and packet loss.
        """
        # 1) Stop any existing thread (and wait for its handle to close)
        if self.shaper_thread and self.shaper_thread.isRunning():
            self.stop_shaper_thread()

        # 2) Read user values
        latency = self.latency_spin.value()
        jitter = self.jitter_spin.value()
        loss = self.packet_loss_spin.value()

        # 3) Save config
        self.save_config()

        # 4) Create and start a new shaping thread
        self.shaper_thread = ShaperThread(latency, jitter, loss)
        self.shaper_thread.finished.connect(self.on_shaper_finished)
        self.shaper_thread.error.connect(self.on_shaper_error)
        self.shaper_thread.start()

        QMessageBox.information(self, "Shaping Started", "Network shaping has started.")

    def reset_settings(self):
        """
        Reset shaping to zero (no latency, no jitter, no packet loss).
        """
        if self.shaper_thread and self.shaper_thread.isRunning():
            self.stop_shaper_thread()

        self.shaper_thread = ShaperThread(0, 0, 0.0)
        self.shaper_thread.finished.connect(self.on_shaper_finished)
        self.shaper_thread.error.connect(self.on_shaper_error)
        self.shaper_thread.start()

        # Reset the spin boxes
        self.latency_spin.setValue(0)
        self.jitter_spin.setValue(0)
        self.packet_loss_spin.setValue(0)
        self.save_config()

        QMessageBox.information(self, "Shaping Reset", "All shaping is set to normal (0).")

    def stop_shaper_thread(self):
        """
        Gracefully stop the current shaper thread and wait for it to finish.
        This ensures the WinDivert handle is actually closed 
        before we open a new one.
        """
        if self.shaper_thread:
            self.shaper_thread.stop()
            self.shaper_thread.wait()

    def on_shaper_finished(self):
        QMessageBox.information(self, "Finished", "Shaper thread finished or stopped.")

    def on_shaper_error(self, message):
        QMessageBox.critical(self, "Error in Shaper Thread", message)

    def load_config(self):
        """
        Load last user-set values from config.json
        """
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                self.latency_spin.setValue(config.get("latency", 0))
                self.jitter_spin.setValue(config.get("jitter", 0))
                self.packet_loss_spin.setValue(config.get("packet_loss", 0.0))
        except Exception as e:
            logging.exception("Error loading config")

    def save_config(self):
        """
        Save user-set values to config.json
        """
        try:
            config = {
                "latency": self.latency_spin.value(),
                "jitter": self.jitter_spin.value(),
                "packet_loss": self.packet_loss_spin.value()
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            logging.exception("Error saving config")

    def closeEvent(self, event):
        """
        When the main window closes, stop the shaping thread if running.
        """
        self.stop_shaper_thread()
        super().closeEvent(event)


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    A global exception hook that logs errors and can show a message box.
    """
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Main thread crashed with exception:\n{tb}")
    app = QApplication.instance()
    if app:
        QMessageBox.critical(None, "Fatal Error", str(exc_value))

def main():
    """
    Program entry point. Checks admin privileges, elevates if needed.
    Then runs the PyQt5 event loop with NetworkThrottler.
    """
    # 1) Check admin
    if not is_admin():
        print("Not running as admin, attempting to elevate privileges...")
        if elevate_privileges():
            sys.exit(0)
        else:
            print("Failed to elevate. Exiting.")
            sys.exit(1)

    # 2) Create QApplication
    qt_app = QApplication(sys.argv)
    sys.excepthook = handle_exception

    # 3) Create and show main window
    window = NetworkThrottler()
    window.show()

    # 4) Run event loop
    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
