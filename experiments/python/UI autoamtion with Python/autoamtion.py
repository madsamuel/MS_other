

# UI automation using pyautogui and webbrowser
import pyautogui
import webbrowser
import time

# Open the browser to the target URL
url = "https://home.startrekfleetcommand.com/"
webbrowser.open(url)

# Wait for the browser to open and page to load
time.sleep(5)  # Adjust if needed for slower connections

print("Move your mouse to the 'Go To Store' button and press Enter in this window.")
input()
go_to_store_pos = pyautogui.position()
print(f"Recorded 'Go To Store' button position: {go_to_store_pos}")
pyautogui.click(go_to_store_pos)
time.sleep(3)

print("Move your mouse to the 'Sign in with Scopely' button and press Enter in this window.")
input()
sign_in_scopely_pos = pyautogui.position()
print(f"Recorded 'Sign in with Scopely' button position: {sign_in_scopely_pos}")
pyautogui.click(sign_in_scopely_pos)
time.sleep(5)

print("Automation complete.")