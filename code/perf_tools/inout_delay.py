import time
import pyautogui
from pywinauto import Application

# Path to PowerPoint application (modify if needed)
powerpoint_path = r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"

# Start PowerPoint application
app = Application().start(powerpoint_path)

# Wait for PowerPoint to open
time.sleep(5)

# Create a new presentation
pyautogui.hotkey('alt', 'f')  # Open the File menu
time.sleep(1)
pyautogui.press('n')  # Select New
time.sleep(1)
pyautogui.press('enter')  # Confirm to create a new presentation
time.sleep(2)

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

# Close PowerPoint
app.kill()
