import sys
import psutil
import socket
import os
from PyQt5 import QtWidgets, QtCore, QtGui

class PortWorker(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(list)

    def resolve_url(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    def run(self):
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
        self.data_ready.emit(open_ports)

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

        self.spinner_label = QtWidgets.QLabel()
        spinner_path = os.path.join(os.path.dirname(__file__), 'spinner.gif')
        self.spinner_movie = QtGui.QMovie(spinner_path)
        if not self.spinner_movie.isValid():
            print("Error: spinner.gif not found or invalid!")
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.spinner_label)
        self.spinner_label.hide()

        self.setLayout(layout)
        self.worker = None

        # Delay initial loading to allow the window to render
        QtCore.QTimer.singleShot(100, self.load_ports)

    def load_ports(self):
        self.spinner_label.show()
        self.spinner_movie.start()

        self.worker = PortWorker()
        self.worker.data_ready.connect(self.update_table)
        self.worker.start()

    def update_table(self, open_ports):
        self.table.setRowCount(len(open_ports))
        for row, (port, process_name, pid, remote_address, url) in enumerate(sorted(open_ports)):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(port)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(process_name))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(pid)))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(remote_address))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(url))

        self.spinner_movie.stop()
        self.spinner_label.hide()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = PortViewer()
    viewer.show()
    sys.exit(app.exec_())