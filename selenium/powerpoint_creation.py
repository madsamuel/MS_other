import time
import pyautogui
from pywinauto import Application

# Path to PowerPoint application (modify if needed)
powerpoint_path = r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"

# Start PowerPoint application
app = Application().start(powerpoint_path)

# Wait for PowerPoint to open
time.sleep(5)

# Get the PowerPoint window and maximize it
app_window = app.window(title_re=".*PowerPoint.*")  # Matches any PowerPoint window
app_window.maximize()
time.sleep(2)  # Allow some time for maximization

# Add slides
for _ in range(3):  # Add 3 more slides to make a total of 4 slides
    pyautogui.hotkey('ctrl', 'm')  # Shortcut to add a new slide
    time.sleep(1)

# Add content to the slides
slide_content = [
    "Random Banana Generation",
    "Introduction to Bananas",
    "How Bananas are Generated",
    "Conclusion"
]

for i, content in enumerate(slide_content):
    pyautogui.click(x=500, y=300)  # Click on the slide to focus
    pyautogui.typewrite(content)
    pyautogui.press('enter')
    time.sleep(1)
    if i < 3:
        pyautogui.hotkey('ctrl', 'pageup')  # Move to the next slide
        time.sleep(1)

# Scroll up and down 5 times
for _ in range(5):
    pyautogui.scroll(-500)  # Scroll down
    time.sleep(1)
    pyautogui.scroll(500)  # Scroll up
    time.sleep(1)

# Save the presentation
pyautogui.hotkey('ctrl', 's')  # Save the presentation
time.sleep(1)
pyautogui.typewrite("Random_Banana_Generation.pptx")
time.sleep(1)
pyautogui.press('enter')

# Make the presentation full screen
pyautogui.hotkey('f5')  # Start the slideshow in full-screen mode
time.sleep(2)

# Close PowerPoint after a delay (optional)
time.sleep(10)  # Wait for 10 seconds before closing
app.kill()
