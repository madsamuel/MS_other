#!/usr/bin/env python3
"""
Network Emulator for Windows using PyQt5 + WinDivert + pydivert.

- Emulates latency, jitter, packet loss, and bandwidth throttling.
- Requires running with admin privileges and WinDivert installed.

Install:
    pip install pydivert PyQt5
Download WinDivert:
    https://github.com/basil00/Divert
Place WinDivert.dll and driver files in PATH or current directory.
"""

import sys
import random
import time
import threading
import heapq
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QSpinBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
import pydivert  # pip install pydivert


class PacketScheduler:
    """
    Manages packet scheduling, latency, jitter, loss, and bandwidth throttling.
    Uses a priority queue to hold packets with their future release times.
    """

    def __init__(self):
        # User-configurable settings
        self.latency_ms = 0
        self.jitter_ms = 0
        self.loss_percent = 0
        self.bandwidth_kbps = 0

        # For bandwidth throttling (token bucket)
        self.tokens_per_second = 0
        self.token_bucket = 0
        self.last_token_time = time.time()

        # Priority queue for scheduled packets (release_time, packet)
        self.packet_queue = []
        self.lock = threading.Lock()

        self.running = False
        self.thread = None

    def update_settings(self, latency_ms, jitter_ms, loss_percent, bandwidth_kbps):
        """
        Update shaping parameters (thread safe).
        """
        with self.lock:
            self.latency_ms = latency_ms
            self.jitter_ms = jitter_ms
            self.loss_percent = loss_percent
            self.bandwidth_kbps = bandwidth_kbps
            # Update token generation rate
            self.tokens_per_second = bandwidth_kbps / 8.0  # kbps -> kBytes/s
            # Reset token bucket if desired
            self.token_bucket = self.tokens_per_second  # start with 1 second worth of tokens

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._packet_releaser, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        with self.lock:
            self.packet_queue.clear()

    def schedule_packet(self, packet):
        """
        Calculate when to release this packet based on latency + jitter + 
        possible bandwidth constraints, then store in the queue.
        Also account for potential packet loss.
        """
        with self.lock:
            # Packet loss check
            if random.uniform(0, 100) < self.loss_percent:
                # Drop packet
                return

            # Latency + jitter
            base_delay = self.latency_ms / 1000.0
            if self.jitter_ms > 0:
                jitter = random.uniform(0, self.jitter_ms) / 1000.0
            else:
                jitter = 0

            delay = base_delay + jitter
            release_time = time.time() + delay

            # Insert into priority queue
            heapq.heappush(self.packet_queue, (release_time, packet))

    def _packet_releaser(self):
        """
        Continuously checks the queue for packets whose release times have arrived,
        then re-injects them if bandwidth tokens are available.
        """
        while self.running:
            now = time.time()
            with self.lock:
                # Refill token bucket based on elapsed time
                elapsed = now - self.last_token_time
                self.last_token_time = now
                self.token_bucket += self.tokens_per_second * elapsed
                # Cap the bucket to one second worth, to prevent huge backlog 
                # if we want to keep the model simpler.
                if self.token_bucket > self.tokens_per_second:
                    self.token_bucket = self.tokens_per_second

                # Release any packets whose time has arrived and we have tokens for.
                released_packets = []
                while self.packet_queue and self.packet_queue[0][0] <= now:
                    release_time, packet = heapq.heappop(self.packet_queue)
                    pkt_size = len(packet.raw) / 1024.0  # in kBytes
                    # Check if we have enough tokens (bandwidth)
                    if self.bandwidth_kbps > 0:
                        if pkt_size <= self.token_bucket:
                            # Use tokens
                            self.token_bucket -= pkt_size
                            released_packets.append(packet)
                        else:
                            # Not enough tokens: reinsert packet with a small delay
                            # so we try again in ~10ms
                            heapq.heappush(self.packet_queue, (now + 0.01, packet))
                            break
                    else:
                        # No bandwidth limit, just release
                        released_packets.append(packet)

            # Re-inject outside the lock to keep concurrency safe
            for packet in released_packets:
                # Re-inject the packet
                packet.send()

            # Sleep briefly to avoid spinning
            time.sleep(0.005)


class NetworkEmulatorApp(QMainWindow):
    """
    PyQt5 GUI for Windows network emulation.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Network Emulator")
        self.setMinimumSize(400, 250)

        # Scheduler that processes shaping
        self.scheduler = PacketScheduler()

        # WinDivert handle
        self.divert_handle = None
        self.capture_thread = None
        self.capture_running = False

        # Build UI
        self._build_ui()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        form_layout = QFormLayout()

        # Latency (ms)
        self.latency_spin = QDoubleSpinBox()
        self.latency_spin.setRange(0, 10000)
        self.latency_spin.setValue(0)
        form_layout.addRow("Latency (ms):", self.latency_spin)

        # Jitter (ms)
        self.jitter_spin = QDoubleSpinBox()
        self.jitter_spin.setRange(0, 10000)
        self.jitter_spin.setValue(0)
        form_layout.addRow("Jitter (ms):", self.jitter_spin)

        # Packet loss (%)
        self.loss_spin = QDoubleSpinBox()
        self.loss_spin.setRange(0, 100)
        self.loss_spin.setDecimals(3)
        self.loss_spin.setValue(0)
        form_layout.addRow("Packet Loss (%):", self.loss_spin)

        # Bandwidth (Kbps)
        self.bandwidth_spin = QSpinBox()
        self.bandwidth_spin.setRange(0, 10000000)  # up to 10 Gbps in Kbps
        self.bandwidth_spin.setValue(0)
        form_layout.addRow("Bandwidth (Kbps):", self.bandwidth_spin)

        # Buttons
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)

    def on_start(self):
        """
        Starts packet capturing via WinDivert and applies the user settings.
        """
        if self.capture_running:
            QMessageBox.warning(self, "Already Running", "Capture is already running.")
            return

        # Get user settings
        latency_ms = self.latency_spin.value()
        jitter_ms = self.jitter_spin.value()
        loss_pct = self.loss_spin.value()
        bandwidth_kbps = self.bandwidth_spin.value()

        # Update the scheduler
        self.scheduler.update_settings(latency_ms, jitter_ms, loss_pct, bandwidth_kbps)
        self.scheduler.start()

        # Start capturing in a new thread
        self.capture_running = True
        self.capture_thread = threading.Thread(target=self._capture_packets, daemon=True)
        self.capture_thread.start()

        QMessageBox.information(self, "Started", "Network emulation started.")

    def on_stop(self):
        """
        Stops packet capturing and resets the scheduler.
        """
        if not self.capture_running:
            QMessageBox.warning(self, "Not Running", "Capture is not running.")
            return

        self.capture_running = False

        if self.divert_handle is not None:
            self.divert_handle.close()
            self.divert_handle = None

        if self.capture_thread:
            self.capture_thread.join()
            self.capture_thread = None

        self.scheduler.stop()

        QMessageBox.information(self, "Stopped", "Network emulation stopped.")

    def _capture_packets(self):
        """
        Capture loop for WinDivert. For simplicity, we capture all outbound and inbound IP packets.
        You can refine the filter to match specific addresses or ports.
        """
        # Example filter: "true" (all traffic). Adjust as needed.
        # You might specify: "outbound or inbound and ip" to capture IP packets only, etc.
        # Please see WinDivert filter syntax: https://reqrypt.org/windivert-doc.html#filter_language
        filter_str = "true"
        try:
            self.divert_handle = pydivert.WinDivert(filter_str)
            self.divert_handle.open()

            while self.capture_running:
                packet = self.divert_handle.recv()  # blocks until a packet is available
                # Hand it off to the scheduler for possible dropping, delay, re-injection
                self.scheduler.schedule_packet(packet)

        except pydivert.WinDivertError as e:
            # This often occurs if the driver isn't installed or we lack admin privileges
            print(f"WinDivert error: {e}")
        finally:
            if self.divert_handle:
                self.divert_handle.close()
                self.divert_handle = None


def main():
    app = QApplication(sys.argv)
    window = NetworkEmulatorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
