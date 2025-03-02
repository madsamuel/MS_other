import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox
)
from PyQt5.QtCore import QTimer, Qt


class ProcessTab(QWidget):
    """Tab that lists running processes and lets you kill a selected process."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        # Updated to 5 columns: PID, Name, CPU %, Memory %, Executable
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory %", "Executable"])
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        # Button layout
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_processes)

        self.kill_button = QPushButton("Kill Process")
        self.kill_button.clicked.connect(self.kill_selected_process)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.kill_button)
        self.layout.addLayout(button_layout)

        # Timer to auto-refresh every 5 seconds (optional)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_processes)
        self.timer.start(5000)

        # Initial load
        self.refresh_processes()

    def refresh_processes(self):
        """Refresh the process list table, including the executable path."""
        self.table.setRowCount(0)  # Clear current rows

        # Gather process info including executable (exe)
        # Some processes may not have an exe, so we default to an empty string.
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'exe']):
            pid = str(proc.info['pid'])
            name = proc.info['name'] or ""
            cpu = f"{proc.info['cpu_percent']:.1f}"
            mem = f"{proc.info['memory_percent']:.1f}"
            exe = proc.info['exe'] or ""  # Executable path

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Populate table items
            self.table.setItem(row_position, 0, QTableWidgetItem(pid))
            self.table.setItem(row_position, 1, QTableWidgetItem(name))
            self.table.setItem(row_position, 2, QTableWidgetItem(cpu))
            self.table.setItem(row_position, 3, QTableWidgetItem(mem))
            self.table.setItem(row_position, 4, QTableWidgetItem(exe))

        # Resize columns to contents
        self.table.resizeColumnsToContents()

    def kill_selected_process(self):
        """Kill the currently selected process."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a process to kill.")
            return

        pid_item = self.table.item(row, 0)
        if not pid_item:
            return

        pid = int(pid_item.text())
        try:
            proc = psutil.Process(pid)
            proc.kill()
            QMessageBox.information(self, "Success", f"Process {pid} killed successfully.")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            QMessageBox.critical(self, "Error", f"Could not kill process {pid}. Reason: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error killing process {pid}: {e}")

        # Refresh after kill attempt
        self.refresh_processes()


class ServicesTab(QWidget):
    """Tab that lists Windows services and allows starting/stopping them (Windows only)."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Display Name", "Status", "Start Type"])
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_services)
        self.start_button = QPushButton("Start Service")
        self.start_button.clicked.connect(self.start_selected_service)
        self.stop_button = QPushButton("Stop Service")
        self.stop_button.clicked.connect(self.stop_selected_service)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        self.layout.addLayout(button_layout)

        # Initial load
        self.refresh_services()

    def refresh_services(self):
        """Refresh the list of Windows services."""
        import psutil
        try:
            services = psutil.win_service_iter()
        except AttributeError:
            QMessageBox.critical(
                self, "Error",
                "psutil.win_service_iter() not available on this platform. "
                "Services tab works only on Windows."
            )
            return

        self.table.setRowCount(0)
        for svc in services:
            name = svc.name()
            display_name = svc.display_name()
            try:
                status = svc.status()
            except psutil.AccessDenied:
                status = "AccessDenied"
            start_type = svc.start_type()  # e.g. 'manual', 'automatic'

            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(name))
            self.table.setItem(row_pos, 1, QTableWidgetItem(display_name))
            self.table.setItem(row_pos, 2, QTableWidgetItem(status))
            self.table.setItem(row_pos, 3, QTableWidgetItem(start_type))

        self.table.resizeColumnsToContents()

    def get_selected_service(self):
        """Returns the psutil.Service object for the currently selected service row, or None."""
        row = self.table.currentRow()
        if row < 0:
            return None

        item = self.table.item(row, 0)
        if not item:
            return None

        service_name = item.text()
        import psutil
        try:
            return psutil.win_service_get(service_name)
        except Exception:
            return None

    def start_selected_service(self):
        """Start the selected Windows service."""
        svc = self.get_selected_service()
        if svc is None:
            QMessageBox.warning(self, "No Selection", "Please select a service to start.")
            return

        try:
            svc.start()
            QMessageBox.information(self, "Success", f"Service '{svc.name()}' started.")
        except psutil.AccessDenied:
            QMessageBox.critical(self, "Access Denied", f"Cannot start '{svc.name()}'. Run as administrator.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting service '{svc.name()}': {e}")

        self.refresh_services()

    def stop_selected_service(self):
        """Stop the selected Windows service."""
        svc = self.get_selected_service()
        if svc is None:
            QMessageBox.warning(self, "No Selection", "Please select a service to stop.")
            return

        import psutil
        try:
            svc.stop()
            QMessageBox.information(self, "Success", f"Service '{svc.name()}' stopped.")
        except psutil.AccessDenied:
            QMessageBox.critical(self, "Access Denied", f"Cannot stop '{svc.name()}'. Run as administrator.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping service '{svc.name()}': {e}")

        self.refresh_services()


class MainWindow(QMainWindow):
    """Main application window with tabs for Processes and Services."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Task Manager")
        self.resize(900, 500)

        tab_widget = QTabWidget(self)
        self.setCentralWidget(tab_widget)

        # Processes tab
        self.process_tab = ProcessTab()
        tab_widget.addTab(self.process_tab, "Processes")

        # Services tab
        self.services_tab = ServicesTab()
        tab_widget.addTab(self.services_tab, "Services")


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
