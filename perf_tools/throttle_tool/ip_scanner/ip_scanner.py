import sys
import platform
import netifaces
import subprocess
import ipaddress
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox,
    QProgressBar
)


###############################################################################
# Helper Functions
###############################################################################
def get_network_interfaces():
    """Return a dictionary: {interface_name: [IPv4 addresses]}."""
    interfaces_info = {}
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        ipv4_list = []
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip_addr = link.get('addr')
                if ip_addr and ip_addr != '127.0.0.1':
                    ipv4_list.append(ip_addr)
        if ipv4_list:
            interfaces_info[iface] = ipv4_list
    return interfaces_info


def parse_ip_range(start_ip, end_ip):
    """Convert a start and end IP into a list of IPs."""
    try:
        start_ip = ipaddress.IPv4Address(start_ip)
        end_ip = ipaddress.IPv4Address(end_ip)

        if start_ip > end_ip:
            start_ip, end_ip = end_ip, start_ip  # Swap if reversed

        return [str(ip) for ip in ipaddress.summarize_address_range(start_ip, end_ip)]
    except ipaddress.AddressValueError:
        return []


def ping_host(ip):
    """Ping a single IP once. Returns True if the host is reachable, False otherwise."""
    count_flag = "-c" if platform.system().lower() != 'windows' else "-n"
    try:
        result = subprocess.run(
            ["ping", count_flag, "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


###############################################################################
# Background Scanning Thread
###############################################################################
class ScanThread(QThread):
    result_signal = pyqtSignal(str, str)  # Emitting (IP Address, Status)
    finished_signal = pyqtSignal()  # Emitted when the scan is complete
    progress_signal = pyqtSignal(int)  # Progress update signal

    def __init__(self, ip_list, parent=None):
        super().__init__(parent)
        self.ip_list = ip_list
        self._stop_flag = False
        self._mutex = QMutex()

    def run(self):
        total_ips = len(self.ip_list)
        for index, ip in enumerate(self.ip_list):
            self._mutex.lock()
            if self._stop_flag:
                self._mutex.unlock()
                break
            self._mutex.unlock()

            status = "Alive" if ping_host(ip) else "Unreachable"
            self.result_signal.emit(ip, status)

            progress = int((index + 1) / total_ips * 100)
            self.progress_signal.emit(progress)

        self.finished_signal.emit()

    def stop(self):
        """Request to stop scanning."""
        self._mutex.lock()
        self._stop_flag = True
        self._mutex.unlock()


###############################################################################
# PyQt5 Main Window
###############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Scanner (Enhanced)")
        self.setGeometry(200, 200, 650, 450)

        self.interfaces_info = get_network_interfaces()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Network Adapter Selector
        adapter_layout = QHBoxLayout()
        adapter_label = QLabel("Select Adapter:")
        self.adapter_combo = QComboBox()
        for iface, ips in self.interfaces_info.items():
            for ip in ips:
                self.adapter_combo.addItem(f"{iface} ({ip})", ip)
        adapter_layout.addWidget(adapter_label)
        adapter_layout.addWidget(self.adapter_combo)
        self.layout.addLayout(adapter_layout)

        # IP Range Input (Two Fields)
        range_layout = QHBoxLayout()
        range_label_start = QLabel("Start IP:")
        self.range_edit_start = QLineEdit()
        self.range_edit_start.setPlaceholderText("192.168.1.1")

        range_label_end = QLabel("End IP:")
        self.range_edit_end = QLineEdit()
        self.range_edit_end.setPlaceholderText("192.168.1.254")

        range_layout.addWidget(range_label_start)
        range_layout.addWidget(self.range_edit_start)
        range_layout.addWidget(range_label_end)
        range_layout.addWidget(self.range_edit_end)
        self.layout.addLayout(range_layout)

        # Scan Button
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.layout.addWidget(self.scan_button)

        # Sortable Table for Results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["IP Address", "Status"])
        self.result_table.setSortingEnabled(True)  # Enable sorting
        self.layout.addWidget(self.result_table)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Stop Button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.scan_thread = None

    def start_scan(self):
        """Start scanning the specified IP range in a background thread."""
        start_ip = self.range_edit_start.text().strip()
        end_ip = self.range_edit_end.text().strip()

        if not start_ip or not end_ip:
            QMessageBox.warning(self, "Error", "Please enter a valid start and end IP.")
            return

        ip_list = parse_ip_range(start_ip, end_ip)
        if not ip_list:
            QMessageBox.warning(self, "Error", "Invalid IP range.")
            return

        # Clear previous scan results
        self.result_table.setRowCount(0)
        self.progress_bar.setValue(0)

        self.scan_thread = ScanThread(ip_list)
        self.scan_thread.result_signal.connect(self.handle_result)
        self.scan_thread.progress_signal.connect(self.progress_bar.setValue)
        self.scan_thread.finished_signal.connect(self.handle_finished)

        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.scan_thread.start()

    def handle_result(self, ip, status):
        """Add a row to the results table with the scan result."""
        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)

        self.result_table.setItem(row_position, 0, QTableWidgetItem(ip))
        self.result_table.setItem(row_position, 1, QTableWidgetItem(status))

    def handle_finished(self):
        """Called when the scan thread finishes."""
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.scan_thread = None

    def stop_scan(self):
        """Request the scan thread to stop."""
        if self.scan_thread is not None:
            self.scan_thread.stop()


###############################################################################
# Run Application
###############################################################################
def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
