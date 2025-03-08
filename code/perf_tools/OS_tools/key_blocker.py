import keyboard
import time

def main():
    # Block the 'a' key system-wide
    keyboard.block_key('a')

    print("The 'a' key is now blocked at the system level.")
    print("Press CTRL+SHIFT+F12 to exit and unblock the 'a' key.")

    # Add a global hotkey to unblock and exit
    keyboard.add_hotkey('ctrl+shift+f12', unblock_and_exit)

    # Keep the script running indefinitely
    # (or until the unblock hotkey is pressed)
    while True:
        time.sleep(1)

def unblock_and_exit():
    """Unblock the 'a' key and terminate the script."""
    keyboard.unblock_key('a')
    print("The 'a' key is now unblocked. Exiting the script.")
    keyboard.unhook_all_hotkeys()
    raise SystemExit(0)

if __name__ == "__main__":
    # IMPORTANT: On Windows, run this as Admin so the hook can be installed system-wide.
    main()
