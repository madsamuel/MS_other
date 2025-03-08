# There is some delay in the theme change, but it works.
import sys
import os
import winreg
import ctypes
import threading

import keyboard  # For global hotkeys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox, QStyle
)

PERSONALIZE_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
APPS_LIGHT_THEME = "AppsUseLightTheme"
SYSTEM_LIGHT_THEME = "SystemUsesLightTheme"

def set_registry_value(key_path, name, value):
    ...

def get_registry_value(key_path, name):
    ...

def broadcast_settings_change():
    ...

def toggle_windows_theme():
    ...

class ThemeTogglerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Error", "System tray not available.")
            sys.exit(1)

        # Create the tray icon
        self.tray_icon = QSystemTrayIcon()

        # Option A: Use a custom icon file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.ico")  # or .ico
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback if file doesn't exist
            self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.SP_ComputerIcon))

        # Context menu
        menu = QMenu()
        toggle_action = QAction("Toggle Theme", self.tray_icon)
        toggle_action.triggered.connect(self.on_toggle_theme)
        menu.addAction(toggle_action)

        quit_action = QAction("Quit", self.tray_icon)
        quit_action.triggered.connect(self.on_quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("Theme Toggler - Click to open menu")
        self.tray_icon.show()

        # Background thread for global hotkey (Ctrl+Alt+T)
        self.hotkey = "ctrl+alt+t"
        self.hotkey_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.hotkey_thread.start()

    def listen_hotkey(self):
        keyboard.add_hotkey(self.hotkey, self.safe_toggle_theme)
        keyboard.wait()

    def safe_toggle_theme(self):
        QTimer.singleShot(0, self.on_toggle_theme)

    def on_toggle_theme(self):
        try:
            toggle_windows_theme()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to toggle theme:\n{e}")

    def on_quit(self):
        keyboard.unhook_all()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    print("Running ThemeTogglerApp...")
    app = ThemeTogglerApp()
    app.run()
    print("App exited.")
