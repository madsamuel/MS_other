import time
import random
import string
import pyautogui
from pywinauto import Application

def generate_random_text(num_chars=30):
    """Return a random string of letters and spaces."""
    chars = string.ascii_letters + " "
    return ''.join(random.choice(chars) for _ in range(num_chars))

def main():
    # 1. Launch PowerPoint
    powerpoint_path = r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"
    app = Application(backend="uia").start(powerpoint_path)
    time.sleep(5)  # Wait for PowerPoint to open

    # 2. Create a new blank presentation
    pyautogui.press('n')     # "New presentation" menu option
    time.sleep(1)
    pyautogui.press('enter') # Confirm
    time.sleep(3)

    # Calculate screen center once
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    # 3. Create 5 slides, each with random text
    total_slides = 5
    for slide_number in range(1, total_slides + 1):
        # For slides after the first, add a new slide with Ctrl+M
        if slide_number > 1:
            pyautogui.hotkey('ctrl', 'm')  # Create new slide
            time.sleep(2)

        pyautogui.click(center_x, center_y)
        time.sleep(1)
    

        # Generate and type random text
        random_content = f"Slide {slide_number}: " + generate_random_text(40)
        pyautogui.typewrite(random_content, interval=0.02)
        
        time.sleep(1)

    # 4. Scroll up and down the slide deck
    # Move the mouse to where the slide thumbnails typically appear (left side)
    pyautogui.moveTo(150, 300)  # Adjust as needed
    time.sleep(1)
    for _ in range(3):
        pyautogui.scroll(-500)  # Scroll down
        time.sleep(1)
        pyautogui.scroll(500)   # Scroll up
        time.sleep(1)

    # 5. Save the presentation
    pyautogui.hotkey('ctrl', 's')  # Save
    time.sleep(2)

    # Type a filename
    filename = "Randomized_Presentation.pptx"
    pyautogui.typewrite(filename, interval=0.05)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)

    # 6. Confirm overwrite prompt if it appears (press Enter just in case)
    pyautogui.press('enter')
    time.sleep(2)

    # 7. Exit PowerPoint
    pyautogui.hotkey('alt', 'f4')
    time.sleep(1)

if __name__ == "__main__":
    main()
