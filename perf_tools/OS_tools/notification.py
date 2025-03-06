# Sample of an app running locally that pushes notification to windows notification hubimport sys
import sys
import os
from win10toast import ToastNotifier

def main():
    """
    Displays a toast notification on Windows 10+ with a probability value (0..1).
    If no argument is supplied, defaults to 0.5.
    Uses an icon named 'icon.ico' in the same folder.
    """
    default_prob = 0.5

    # Check command-line args
    if len(sys.argv) < 2:
        prob = default_prob
        print(f"No argument supplied. Using default probability={default_prob}")
    else:
        try:
            prob = float(sys.argv[1])
        except ValueError:
            print("Error: The argument must be a numeric value between 0 and 1.")
            sys.exit(1)

    # Validate the probability
    if prob < 0 or prob > 1:
        print("Error: Probability must be between 0 and 1.")
        sys.exit(1)

    # Use range-based logic for clarity
    if prob < 0.25:
        # If you want a message for lower range, add it here
        # e.g. "Everything is stable."
        print("Connection is stable.")
    elif 0.25 <= prob < 0.5:
        print("Your connection is degrading, please take action.")
    elif 0.5 <= prob < 0.75:
        print("Your connection is degrading further, please take action soon.")
    else:  # prob >= 0.75
        print("Your connection is degrading beyond usability.")

    # Locate icon.ico in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.ico")  # or "icon.png" if you really prefer .png

    if not os.path.exists(icon_path):
        print(f"Warning: Icon file not found at {icon_path}. Toast will show without icon.")
        icon_path = None  # If missing, the toast will still appear, just no icon.

    # Create and show the toast notification
    toaster = ToastNotifier()
    toaster.show_toast(
        "Windows App",                # <-- Notification Title
        f"Prediction Value: {prob}",  # <-- Notification Body
        icon_path=icon_path,         # <-- Local icon if available
        duration=5                   # Notification persists for 5 seconds
    )

    # Keep the script alive until the notification is closed
    while toaster.notification_active():
        pass

if __name__ == "__main__":
    main()
