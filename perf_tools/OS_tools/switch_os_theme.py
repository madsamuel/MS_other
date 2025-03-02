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

# Registry path and value names
PERSONALIZE_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
APPS_LIGHT_THEME = "AppsUseLightTheme"
SYSTEM_LIGHT_THEME = "SystemUsesLightTheme"


def set_registry_value(key_path, name, value):
    """Sets a DWORD registry value in HKEY_CURRENT_USER."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)


def get_registry_value(key_path, name):
    """Gets a DWORD registry value from HKEY_CURRENT_USER. Returns None if not found."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, name)
            return val
    except FileNotFoundError:
        return None


def broadcast_settings_change():
    """Tell Windows to re-check settings so the theme change is applied immediately."""
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    SMTO_NORMAL = 0x0002

    user32 = ctypes.windll.user32
    user32.SendMessageTimeoutW(
        HWND_BROADCAST,
        WM_SETTINGCHANGE,
        0,
        0,
        SMTO_NORMAL,
        100,
        None
    )


def toggle_windows_theme():
    """
    Mimic the PowerShell logic:

    # If AppsUseLightTheme is 1 (Light Mode), switch both to 0 (Dark Mode)
    # Otherwise, switch both to 1 (Light Mode)
    """
    current_apps_theme = get_registry_value(PERSONALIZE_KEY_PATH, APPS_LIGHT_THEME)
    if current_apps_theme is None:
        current_apps_theme = 1  # Default to Light if not found

    # If currently Light (1), switch both to 0; else switch both to 1
    if current_apps_theme == 1:
        # Light -> Dark
        set_registry_value(PERSONALIZE_KEY_PATH, APPS_LIGHT_THEME, 0)
        set_registry_value(PERSONALIZE_KEY_PATH, SYSTEM_LIGHT_THEME, 0)
    else:
        # Dark -> Light
        set_registry_value(PERSONALIZE_KEY_PATH, APPS_LIGHT_THEME, 1)
        set_registry_value(PERSONALIZE_KEY_PATH, SYSTEM_LIGHT_THEME, 1)

    broadcast_settings_change()


class ThemeTogglerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # If system tray is not available, exit
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Error", "System tray not available.")
            sys.exit(1)

        # Create the tray icon
        self.tray_icon = QSystemTrayIcon()

        # Use a default icon (computer icon) or your own .ico/.png
        # Example using a built-in style icon:
        self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.SP_ComputerIcon))

        # Optional: if you have a custom icon file:
        # icon_path = os.path.join(os.path.dirname(__file__), "theme_icon.png")
        # self.tray_icon.setIcon(QIcon(icon_path))

        # Build the tray menu
        menu = QMenu()
        toggle_action = QAction("Toggle Theme", self.tray_icon)
        toggle_action.triggered.connect(self.on_toggle_theme)
        menu.addAction(toggle_action)

        quit_action = QAction("Quit", self.tray_icon)
        quit_action.triggered.connect(self.on_quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("Theme Toggler - Right-click for options")
        self.tray_icon.show()

        # Start a background thread to listen for the global hotkey (Ctrl+Alt+T)
        self.hotkey = "ctrl+alt+t"
        self.hotkey_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.hotkey_thread.start()

    def listen_hotkey(self):
        """Listen for the global hotkey in a background thread."""
        keyboard.add_hotkey(self.hotkey, self.safe_toggle_theme)
        keyboard.wait()

    def safe_toggle_theme(self):
        """
        We can't safely call UI code from a foreign thread.
        We'll schedule the theme toggle on the main Qt thread with QTimer.singleShot(0, ...).
        """
        QTimer.singleShot(0, self.on_toggle_theme)

    def on_toggle_theme(self):
        """Handler for toggling theme with error handling."""
        try:
            toggle_windows_theme()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to toggle theme:\n{e}")

    def on_quit(self):
        """Quit the application."""
        keyboard.unhook_all()  # Stop listening to hotkeys
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """Run the Qt event loop."""
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = ThemeTogglerApp()
    app.run()
