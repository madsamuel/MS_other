import sys
import psutil
import csv
from datetime import datetime
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QFileDialog, QMessageBox, QHBoxLayout
)


class BandwidthMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bandwidth Monitor")
        self.setGeometry(200, 200, 400, 250)

        self.interface = None
        self.interval = 1
        self.csv_output = None

        self.total_sent = 0.0
        self.total_received = 0.0

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bandwidth)

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.interface_selector = QComboBox()
        self.interface_selector.addItem("All Interfaces", None)
        for iface in psutil.net_if_addrs().keys():
            self.interface_selector.addItem(iface, iface)

        layout.addWidget(QLabel("Select Network Interface:"))
        layout.addWidget(self.interface_selector)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval (s):"))
        self.interval_selector = QSpinBox()
        self.interval_selector.setRange(1, 60)
        self.interval_selector.setValue(1)
        interval_layout.addWidget(self.interval_selector)
        layout.addLayout(interval_layout)

        self.sent_label = QLabel("Sent: 0.00 MB")
        self.received_label = QLabel("Received: 0.00 MB")
        layout.addWidget(self.sent_label)
        layout.addWidget(self.received_label)

        file_layout = QHBoxLayout()
        self.file_label = QLabel("Output: None")
        file_layout.addWidget(self.file_label)
        select_file_btn = QPushButton("Select CSV")
        select_file_btn.clicked.connect(self.select_csv_file)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def select_csv_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file:
            self.csv_output = file
            self.file_label.setText(f"Output: {file}")

    def start_monitoring(self):
        self.interface = self.interface_selector.currentData()
        self.interval = self.interval_selector.value()

        if self.csv_output:
            with open(self.csv_output, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(["Timestamp", "Sent(MB)", "Received(MB)", "TotalSent(MB)", "TotalReceived(MB)"])

        self.total_sent = 0.0
        self.total_received = 0.0
        self.timer.start(self.interval * 1000)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitoring(self):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.information(self, "Monitoring Stopped", "Bandwidth monitoring has stopped.")

    def update_bandwidth(self):
        counters_before = psutil.net_io_counters(pernic=bool(self.interface))
        net_io_before = counters_before.get(self.interface) if self.interface else counters_before

        QTimer.singleShot(self.interval * 1000, lambda: self.calculate_bandwidth(net_io_before))

    def calculate_bandwidth(self, net_io_before):
        counters_after = psutil.net_io_counters(pernic=bool(self.interface))
        net_io_after = counters_after.get(self.interface) if self.interface else counters_after

        sent = (net_io_after.bytes_sent - net_io_before.bytes_sent) / (1024 * 1024)
        recv = (net_io_after.bytes_recv - net_io_before.bytes_recv) / (1024 * 1024)

        self.total_sent += sent
        self.total_received += recv

        self.sent_label.setText(f"Sent: {self.total_sent:.2f} MB")
        self.received_label.setText(f"Received: {self.total_received:.2f} MB")

        if self.csv_output:
            with open(self.csv_output, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"{sent:.2f}", f"{recv:.2f}",
                    f"{self.total_sent:.2f}", f"{self.total_received:.2f}"
                ])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BandwidthMonitor()
    window.show()
    sys.exit(app.exec())