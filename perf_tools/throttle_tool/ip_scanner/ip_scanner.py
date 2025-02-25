import sys
import os
import platform
import netifaces
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox
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
    start_parts = start_ip.split('.')
    end_parts = end_ip.split('.')
    
    if len(start_parts) != 4 or len(end_parts) != 4:
        return []

    start_octets = list(map(int, start_parts))
    end_octets = list(map(int, end_parts))

    start_int = (
        (start_octets[0] << 24) + (start_octets[1] << 16) +
        (start_octets[2] << 8) + start_octets[3]
    )
    end_int = (
        (end_octets[0] << 24) + (end_octets[1] << 16) +
        (end_octets[2] << 8) + end_octets[3]
    )

    if end_int < start_int:
        start_int, end_int = end_int, start_int  # Swap if reversed

    ip_list = []
    for ip_int in range(start_int, end_int + 1):
        ip_list.append(f"{(ip_int >> 24) & 255}.{(ip_int >> 16) & 255}.{(ip_int >> 8) & 255}.{ip_int & 255}")

    return ip_list


def ping_host(ip):
    """Ping a single IP once. Returns True if the host is reachable, False otherwise."""
    count_flag = "-c" if platform.system().lower() != 'windows' else "-n"
    cmd = f"ping {count_flag} 1 {ip}"
    exit_code = os.system(cmd + " > nul 2>&1" if platform.system().lower() == 'windows' else cmd + " > /dev/null 2>&1")
    return exit_code == 0


###############################################################################
# Background Scanning Thread
###############################################################################
class ScanThread(QThread):
    result_signal = pyqtSignal(str, str)  # Emitting (IP Address, Status)
    finished_signal = pyqtSignal()  # Emitted when the scan is complete

    def __init__(self, ip_list, parent=None):
        super().__init__(parent)
        self.ip_list = ip_list
        self._stop_flag = False

    def run(self):
        for ip in self.ip_list:
            if self._stop_flag:
                break
            status = "Alive" if ping_host(ip) else "Unreachable"
            self.result_signal.emit(ip, status)
        self.finished_signal.emit()

    def stop(self):
        """Request to stop scanning."""
        self._stop_flag = True


###############################################################################
# PyQt5 Main Window
###############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Scanner")
        self.setGeometry(200, 200, 600, 400)

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

        self.scan_thread = ScanThread(ip_list)
        self.scan_thread.result_signal.connect(self.handle_result)
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
