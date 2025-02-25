import sys
import os
import platform
import netifaces
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QLineEdit,
    QMessageBox
)

def get_network_interfaces():
    """Return a dict: {interface_name: [ipv4_addresses], ...} using netifaces."""
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

def parse_ip_range(ip_range_str):
    """
    Parse an IP range string like '192.168.1.1 - 192.168.1.254' or '192.168.1.1-192.168.1.100'
    into a list of IP addresses. Returns a list of all IPs in that range.
    """
    # Normalize input (remove spaces)
    ip_range_str = ip_range_str.replace(" ", "")
    if '-' not in ip_range_str:
        return []

    start_str, end_str = ip_range_str.split('-')
    start_parts = start_str.split('.')
    end_parts = end_str.split('.')
    if len(start_parts) != 4 or len(end_parts) != 4:
        return []

    start_octets = list(map(int, start_parts))
    end_octets = list(map(int, end_parts))

    # Convert to a single integer for easy iteration
    start_int = (
        (start_octets[0] << 24)
        + (start_octets[1] << 16)
        + (start_octets[2] << 8)
        + start_octets[3]
    )
    end_int = (
        (end_octets[0] << 24)
        + (end_octets[1] << 16)
        + (end_octets[2] << 8)
        + end_octets[3]
    )

    if end_int < start_int:
        # If the user reversed them, swap
        start_int, end_int = end_int, start_int

    ip_list = []
    for ip_int in range(start_int, end_int + 1):
        octet1 = (ip_int >> 24) & 255
        octet2 = (ip_int >> 16) & 255
        octet3 = (ip_int >> 8) & 255
        octet4 = ip_int & 255
        ip_list.append(f"{octet1}.{octet2}.{octet3}.{octet4}")

    return ip_list

def ping_host(ip):
    """Ping a single IP once, return True if responsive, False otherwise."""
    # Use different commands depending on OS
    count_flag = "-c" if platform.system().lower() != 'windows' else "-n"
    cmd = f"ping {count_flag} 1 {ip}"
    exit_code = os.system(cmd + " > nul 2>&1" if platform.system().lower() == 'windows' else cmd + " > /dev/null 2>&1")
    return exit_code == 0

class ScanThread(QThread):
    """
    QThread to scan a list of IP addresses with ping_host and emit results.
    """
    result_signal = pyqtSignal(str)  # Emitted whenever we have a result
    finished_signal = pyqtSignal()   # Emitted when done scanning

    def __init__(self, ip_list, parent=None):
        super().__init__(parent)
        self.ip_list = ip_list
        self._stop_flag = False

    def run(self):
        for ip in self.ip_list:
            if self._stop_flag:
                break
            responsive = ping_host(ip)
            if responsive:
                self.result_signal.emit(f"Alive: {ip}")
            else:
                self.result_signal.emit(f"Unreachable: {ip}")
        self.finished_signal.emit()

    def stop(self):
        """Request to stop scanning."""
        self._stop_flag = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Scanner (by The Bananas)")

        self.interfaces_info = get_network_interfaces()
        # UI elements
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Network adapter selector
        adapter_layout = QHBoxLayout()
        adapter_label = QLabel("Select Adapter:")
        self.adapter_combo = QComboBox()
        for iface, ips in self.interfaces_info.items():
            # E.g., "Ethernet0 (192.168.1.10)"
            for ip in ips:
                self.adapter_combo.addItem(f"{iface} ({ip})", ip)
        adapter_layout.addWidget(adapter_label)
        adapter_layout.addWidget(self.adapter_combo)
        self.layout.addLayout(adapter_layout)

        # IP range input
        range_layout = QHBoxLayout()
        range_label = QLabel("IP Range (e.g. 192.168.1.1 - 192.168.1.254):")
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText("192.168.1.1 - 192.168.1.254")
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.range_edit)
        self.layout.addLayout(range_layout)

        # Scan button
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.layout.addWidget(self.scan_button)

        # Results text area
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.scan_thread = None

    def start_scan(self):
        """Start scanning the specified IP range in a background thread."""
        ip_range_str = self.range_edit.text().strip()
        if not ip_range_str:
            QMessageBox.warning(self, "Error", "Please enter a valid IP range.")
            return

        ip_list = parse_ip_range(ip_range_str)
        if not ip_list:
            QMessageBox.warning(self, "Error", f"Could not parse IP range: {ip_range_str}")
            return

        # Clear the results text
        self.result_text.clear()

        self.scan_thread = ScanThread(ip_list)
        self.scan_thread.result_signal.connect(self.handle_result)
        self.scan_thread.finished_signal.connect(self.handle_finished)

        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.result_text.append(f"Starting scan of {len(ip_list)} IP(s)...")
        self.scan_thread.start()

    def handle_result(self, message):
        """Add the scan result text to the results box."""
        self.result_text.append(message)

    def handle_finished(self):
        """Called when the scan thread finishes."""
        self.result_text.append("Scan complete.\n")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.scan_thread = None

    def stop_scan(self):
        """Request the scan thread to stop."""
        if self.scan_thread is not None:
            self.scan_thread.stop()
            self.result_text.append("Stopping scan...")

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
