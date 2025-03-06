# Sample of an app running locally that pushes notification to windows notification hubimport sys
import sys
from win10toast import ToastNotifier

def main():
    """
    Simple script that takes a probability (0 <= p <= 1) and shows a Windows notification.
    If no argument is provided, defaults to 0.5.
    """
    # Default probability
    default_prob = 0.5

    if len(sys.argv) < 2:
        # No command-line argument provided, so we use our default
        prob = default_prob
        print(f"No argument supplied. Using default probability={default_prob}")
    else:
        # Parse the argument
        try:
            prob = float(sys.argv[1])
        except ValueError:
            print("Error: The argument must be a numeric value between 0 and 1.")
            sys.exit(1)

    # Validate the probability
    if prob < 0 or prob > 1:
        print("Error: Probability must be between 0 and 1.")
        sys.exit(1)

    # Create the toaster/notification
    toaster = ToastNotifier()
    toaster.show_toast(
        "Prediction App",
        f"Prediction Value: {prob}",
        duration=5  # Notification stays for 5 seconds
    )

    # Keep Python running until the notification is closed
    while toaster.notification_active():
        pass

if __name__ == "__main__":
    main()
