import sys
import psutil
import socket
from PyQt5 import QtWidgets, QtCore

class PortViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Open Ports Viewer')
        self.setGeometry(100, 100, 800, 400)

        layout = QtWidgets.QVBoxLayout()

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Port', 'Process Name', 'PID', 'Remote Address', 'URL'])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.load_ports)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_ports()

    def resolve_url(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    def load_ports(self):
        connections = psutil.net_connections()

        open_ports = []
        for conn in connections:
            if conn.status in ('LISTEN', 'ESTABLISHED'):
                pid = conn.pid
                local_port = conn.laddr.port
                remote_ip = conn.raddr.ip if conn.raddr else "N/A"
                remote_address = f"{remote_ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                url = self.resolve_url(remote_ip) if remote_ip != "N/A" else "N/A"
                process_name = psutil.Process(pid).name() if pid else 'Unknown'
                open_ports.append((local_port, process_name, pid, remote_address, url))

        self.table.setRowCount(len(open_ports))
        for row, (port, process_name, pid, remote_address, url) in enumerate(sorted(open_ports)):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(port)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(process_name))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(pid)))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(remote_address))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(url))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = PortViewer()
    viewer.show()
    sys.exit(app.exec_())
