import sys
import os
import json
import keyboard
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QLabel, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt


CONFIG_FILE = "hotkeys_config.json"
HOTKEYS = [
    "ctrl+shift+f1",
    "ctrl+shift+f2",
    "ctrl+shift+f3",
    "ctrl+shift+f4",
    "ctrl+shift+f5",
    "ctrl+shift+f6",
    "ctrl+shift+f7",
    "ctrl+shift+f8",
    "ctrl+shift+f9",
    "ctrl+shift+f10",
    "ctrl+shift+f11",
    "ctrl+shift+f12",
]


class HotkeyManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotkey Manager")
        self.resize(600, 400)

        # Central widget + layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Instruction label
        info_label = QLabel(
            "Assign executables to Ctrl+Shift+F1..F12.\n"
            "Click 'Register Hotkeys' to activate.\n"
            "You must run this script as Administrator for global hotkeys."
        )
        main_layout.addWidget(info_label)

        # Table for hotkeys
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Hotkey", "Executable Path"])
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(HOTKEYS))
        main_layout.addWidget(self.table)

        # Make the second column (Exe Path) expand to fill available space
        header = self.table.horizontalHeader()
        # Column 0 = Hotkey; Column 1 = Executable path
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Populate the table with hotkeys
        for row, hotkey in enumerate(HOTKEYS):
            # First column: read-only hotkey name
            item_hotkey = QTableWidgetItem(hotkey)
            item_hotkey.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # not editable
            self.table.setItem(row, 0, item_hotkey)

            # Second column: placeholder for the path (editable)
            item_path = QTableWidgetItem("")
            self.table.setItem(row, 1, item_path)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Load config button
        self.load_button = QPushButton("Load Config")
        self.load_button.clicked.connect(self.load_config)
        buttons_layout.addWidget(self.load_button)

        # Save config button
        self.save_button = QPushButton("Save Config")
        self.save_button.clicked.connect(self.save_config)
        buttons_layout.addWidget(self.save_button)

        # Browse button (to open file dialog for the selected row)
        self.browse_button = QPushButton("Browse Exe for Selected Row")
        self.browse_button.clicked.connect(self.browse_for_exe)
        buttons_layout.addWidget(self.browse_button)

        # Register hotkeys button
        self.register_button = QPushButton("Register Hotkeys")
        self.register_button.clicked.connect(self.register_hotkeys)
        buttons_layout.addWidget(self.register_button)

        main_layout.addLayout(buttons_layout)

        # Load config if exists
        self.load_config()

        # Track whether hotkeys are currently registered
        self.hotkeys_registered = False

    def load_config(self):
        """Load the hotkey-to-program mapping from a JSON config file."""
        if not os.path.exists(CONFIG_FILE):
            return  # No config yet, do nothing

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config:\n{e}")
            return

        # data should be a dict of {hotkey: exe_path}
        for row in range(len(HOTKEYS)):
            hotkey_item = self.table.item(row, 0)
            path_item = self.table.item(row, 1)
            if not hotkey_item or not path_item:
                continue

            hk = hotkey_item.text()
            path = data.get(hk, "")
            path_item.setText(path)

        # Adjust column sizes (the second column is set to stretch, so this ensures initial display is neat)
        self.table.resizeColumnsToContents()

    def save_config(self):
        """Save the hotkey-to-program mapping to a JSON config file."""
        data = {}
        for row in range(len(HOTKEYS)):
            hotkey_item = self.table.item(row, 0)
            path_item = self.table.item(row, 1)
            if not hotkey_item or not path_item:
                continue

            hotkey = hotkey_item.text()
            exe_path = path_item.text().strip()
            if exe_path:
                data[hotkey] = exe_path

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Config Saved", f"Configuration saved to {CONFIG_FILE}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")

    def browse_for_exe(self):
        """Open a file dialog for the selected row's 'Executable Path' cell."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a row in the table first.")
            return

        exe_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable",
            "",
            "Executables (*.exe);;All Files (*)"
        )
        if exe_path:
            self.table.item(row, 1).setText(exe_path)

    def register_hotkeys(self):
        """Register the hotkeys system-wide. If already registered, re-register."""
        # Unregister existing hotkeys if they are currently active
        if self.hotkeys_registered:
            keyboard.unhook_all_hotkeys()
            self.hotkeys_registered = False

        # Read table data
        mapping = {}
        for row in range(len(HOTKEYS)):
            hotkey_item = self.table.item(row, 0)
            path_item = self.table.item(row, 1)
            if not hotkey_item or not path_item:
                continue

            hotkey = hotkey_item.text().strip()
            exe_path = path_item.text().strip()
            if exe_path:
                mapping[hotkey] = exe_path

        # Register each hotkey
        for hotkey, path in mapping.items():
            # For example, "ctrl+shift+f1" => run "C:/MyFolder/MyApp.exe"
            keyboard.add_hotkey(hotkey, self.create_launcher(path))

        self.hotkeys_registered = True
        QMessageBox.information(
            self,
            "Hotkeys Registered",
            "All configured hotkeys are now active.\n"
            "Press them from any app to launch the assigned program."
        )

    def create_launcher(self, exe_path):
        """Return a function that launches the exe_path when invoked."""
        def launcher():
            try:
                if os.path.exists(exe_path):
                    # If the path is a valid file path
                    os.startfile(exe_path)
                else:
                    # If the user typed something else, let system handle it
                    subprocess.Popen(exe_path, shell=True)
            except Exception as e:
                print(f"Failed to launch {exe_path}: {e}")
        return launcher


def main():
    app = QApplication(sys.argv)
    window = HotkeyManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
