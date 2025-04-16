import sys
import win32con
import win32api
import win32gui

# Window class name
WNDCLASS_NAME = "PreventShutdownClass"


def wndproc(hWnd, message, wParam, lParam):
    """
    Window procedure (WndProc) that handles messages sent to our invisible window.
    We intercept WM_QUERYENDSESSION to block shutdown/logoff attempts.
    """
    if message == win32con.WM_QUERYENDSESSION:
        # This message is sent when the user tries to log off or shut down.
        # Returning 0 (False) indicates: "No, we do not allow shutting down."
        print("Attempting to block system shutdown...")
        return 0  # Prevent the shutdown
    
    elif message == win32con.WM_ENDSESSION:
        # If we did not block it, Windows might send WM_ENDSESSION if it's proceeding.
        # This message indicates the session is actually ending.
        # You could do cleanup here. For demonstration, just print:
        if wParam:
            print("System is ending the session (shutdown not blocked).")
        else:
            print("Session end was canceled or not happening.")
    
    # For all other messages, we use the default window procedure.
    return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


def main():
    # 1. Register a Window Class
    hInst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hInst
    wndclass.lpszClassName = WNDCLASS_NAME
    wndclass.lpfnWndProc = wndproc  # Our custom wndproc
    atom = win32gui.RegisterClass(wndclass)
    
    # 2. Create an invisible window
    hWnd = win32gui.CreateWindow(
        atom,
        "PreventShutdownWindow",         # window name (not visible)
        0,                               # style
        0, 0, 0, 0,                      # x, y, width, height
        0, 0, hInst, None
    )
    
    # 3. Show the window (though it's sized 0x0) and update
    #    Actually not visible, but we still "show" it to keep the message loop functional.
    win32gui.ShowWindow(hWnd, win32con.SW_HIDE)
    win32gui.UpdateWindow(hWnd)
    
    print("PreventShutdown script running.\n"
          "This tries to block normal shutdowns/logoffs.\n"
          "Press Ctrl+C in this console to exit (or kill the process) and allow shutdowns again.\n")

    # 4. Enter a standard message loop to receive messages
    try:
        while True:
            win32gui.PumpWaitingMessages()
            # Sleep or do something idle
            win32api.Sleep(100)
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting. Shutdown can proceed normally now.")


if __name__ == "__main__":
    main()
