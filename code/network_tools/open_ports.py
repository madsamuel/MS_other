import sys
import psutil
from PyQt5 import QtWidgets, QtCore

class PortViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Open Ports Viewer')
        self.setGeometry(100, 100, 700, 400)

        layout = QtWidgets.QVBoxLayout()

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Port', 'Process Name', 'PID', 'Remote Address'])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.load_ports)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_ports()

    def load_ports(self):
        connections = psutil.net_connections()

        open_ports = []
        for conn in connections:
            if conn.status == 'LISTEN' or conn.status == 'ESTABLISHED':
                pid = conn.pid
                local_port = conn.laddr.port
                remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                process_name = psutil.Process(pid).name() if pid else 'Unknown'
                open_ports.append((local_port, process_name, pid, remote_address))

        self.table.setRowCount(len(open_ports))
        for row, (port, process_name, pid, remote_address) in enumerate(sorted(open_ports)):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(port)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(process_name))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(pid)))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(remote_address))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = PortViewer()
    viewer.show()
    sys.exit(app.exec_())