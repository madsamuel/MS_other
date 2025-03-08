import sys
import os
import threading
import ctypes
import time

import win32api
import win32con
import win32gui

# For the tray icon
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image

# Global variables
AWAKE_MODE_ENABLED = True  # If True, block normal shutdown attempts
STOP_EVENT = threading.Event()  # Signals the hidden window thread to stop

WNDCLASS_NAME = "PreventShutdownClass"


def wndproc(hWnd, message, wParam, lParam):
    """
    Window procedure (WndProc) that handles messages sent to our hidden window.
    We intercept WM_QUERYENDSESSION to block shutdown/logoff attempts if AWAKE_MODE_ENABLED is True.
    """
    global AWAKE_MODE_ENABLED

    if message == win32con.WM_QUERYENDSESSION:
        if AWAKE_MODE_ENABLED:
            print("Attempting to block system shutdown (Awake Mode ON)...")
            return 0  # Return 0 = prevent the shutdown
        else:
            print("Allowing system shutdown (Awake Mode OFF).")
            return 1  # Return nonzero to allow

    elif message == win32con.WM_ENDSESSION:
        # WM_ENDSESSION is sent if Windows proceeds with shutdown/logoff
        if wParam:  # wParam = True means the session is ending
            print("System is ending the session. (Shutdown not blocked)")
        else:
            print("Session end was canceled or not happening.")

    return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


def hidden_window_thread():
    """
    Runs in a background thread. Creates an invisible window to intercept shutdown attempts.
    Enters a message loop to handle Win32 events until STOP_EVENT is set.
    """
    hInst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hInst
    wndclass.lpszClassName = WNDCLASS_NAME
    wndclass.lpfnWndProc = wndproc  # Custom wndproc
    atom = win32gui.RegisterClass(wndclass)

    # Create an invisible window
    hWnd = win32gui.CreateWindow(
        atom,
        "PreventShutdownWindow",  # window name (not visible)
        0,                        # style
        0, 0, 0, 0,               # x, y, width, height
        0, 0, hInst, None
    )

    # Show/hide the window (0,0 size, so effectively invisible)
    win32gui.ShowWindow(hWnd, win32con.SW_HIDE)
    win32gui.UpdateWindow(hWnd)

    print("Awake Mode thread started. Currently:", "ON" if AWAKE_MODE_ENABLED else "OFF")

    # Message loop
    try:
        while not STOP_EVENT.is_set():
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Hidden window thread exiting.")


def toggle_awake_mode(icon):
    """
    Toggle the global AWAKE_MODE_ENABLED flag.
    """
    global AWAKE_MODE_ENABLED
    AWAKE_MODE_ENABLED = not AWAKE_MODE_ENABLED
    print(f"Awake Mode is now {'ON' if AWAKE_MODE_ENABLED else 'OFF'}")

    # Update the tray icon text to reflect the new state
    update_tray_menu(icon)


def update_tray_menu(icon):
    """
    Update the tray icon's menu label to show correct Awake Mode status.
    """
    global AWAKE_MODE_ENABLED

    # Rebuild the menu with the current label
    icon.menu = Menu(
        item(
            f"Awake Mode is {'ON' if AWAKE_MODE_ENABLED else 'OFF'} (click to toggle)",
            lambda: toggle_awake_mode(icon)
        ),
        item(
            "Quit",
            lambda: quit_app(icon)
        )
    )


def quit_app(icon):
    """
    Quit the tray app and stop the hidden window thread, allowing normal shutdown.
    """
    print("Exiting app. Shutdown can proceed normally now.")
    STOP_EVENT.set()       # Signal the hidden window thread to exit
    icon.stop()            # Stop the pystray icon event loop


def setup_tray_icon():
    """
    Create and return a pystray Icon object with an initial menu, loading icon.ico
    from the same folder as this script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.ico")

    try:
        icon_img = Image.open(icon_path)
    except Exception as e:
        print(f"Failed to load icon from '{icon_path}': {e}")
        print("Using a fallback red square icon instead.")
        icon_img = Image.new('RGB', (16, 16), color=(255, 0, 0))

    icon = pystray.Icon(
        name="PreventShutdown",
        title="PreventShutdown",
        icon=icon_img
    )

    update_tray_menu(icon)
    return icon


def main():
    # 1. Start the hidden window thread
    thread = threading.Thread(target=hidden_window_thread, daemon=True)
    thread.start()

    # 2. Create tray icon with menu
    icon = setup_tray_icon()

    # 3. Run the tray icon event loop (blocks until icon.stop() is called)
    print("Tray icon running. Right-click or left-click the tray to toggle Awake Mode or Quit.")
    icon.run()

    # Wait for hidden window thread to exit
    thread.join()
    print("Main thread exiting. Goodbye!")


if __name__ == "__main__":
    main()
