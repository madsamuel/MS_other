import time
import pyautogui
from pywinauto import Application

# Step 1: Open Start Menu and Search for "Teams"
print("Opening Start Menu...")
pyautogui.press("win")  # Press Windows key to open Start menu
time.sleep(1)  # Wait for Start Menu to appear

print("Typing 'Teams'...")
pyautogui.typewrite("Teams", interval=0.1)  # Type "Teams"
time.sleep(2)  # Wait for search results to appear

# Step 2: Select the Microsoft Teams app and press Enter
print("Selecting Teams from search results...")
pyautogui.press("enter")  # Open the first search result (Teams)
time.sleep(10)  # Wait for Teams to fully load

# Step 3: Connect to Teams Window using pywinauto
print("Connecting to Microsoft Teams...")
app = Application().connect(title_re=".*Microsoft Teams.*")
teams_window = app.window(title_re=".*Microsoft Teams.*")

# Step 4: Maximize the Teams Window
teams_window.maximize()
print("Teams is now maximized.")

# Step 5: Join a Teams Call Automatically
print("Joining a Teams Call...")
join_button = teams_window.child_window(title="Join", control_type="Button")
if join_button.exists():
    join_button.click()
    print("Joined the call successfully.")
else:
    print("Join button not found!")

time.sleep(5)  # Wait for call connection

