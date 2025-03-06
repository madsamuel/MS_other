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
    if prob > 0.25 or prob < 0.5:
        print("Your connection is degradating please take action here.")
        sys.exit(1)
    elif prob >= 0.5 or prob < 0.75:
        print("Your connection is degradating please take action here.")
        sys.exit(1)
    elif prob > 0.75:
        print("Your connection is degrading beyound usability.")
        sys.exit(1)

    # Locate icon.ico in the same directory as this script
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.png")

    # Create and show the toast notification
    toaster = ToastNotifier()
    toaster.show_toast(
        "Windows App",                  # <-- Notification Title
        f"Prediction Value: {prob}",    # <-- Notification Body
        icon_path=icon_path,           # <-- Local icon.ico for the toast
        duration=5                     # Notification persists for 5 seconds
    )

    # Keep the script alive until the notification is closed
    while toaster.notification_active():
        pass

if __name__ == "__main__":
    main()