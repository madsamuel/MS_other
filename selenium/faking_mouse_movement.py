import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # 1. Launch Chrome and position/size the window so we can calculate coordinates predictably
    driver = webdriver.Chrome()
    driver.set_window_rect(0, 0, 1280, 800)  # x=0, y=0, width=1280, height=800

    # 2. Navigate to a page with a real element to click.
    #    'saucedemo.com' is a public test site with an element ID 'user-name'.
    driver.get("https://www.saucedemo.com/")

    # 3. Wait for the element to be present & clickable
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, "user-name")))

    # 4. Scroll the element into view (just to be sure it's visible)
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    # 5. Get the element's location and size in the *page* coordinate system
    element_location = element.location
    element_size = element.size

    # Calculate the center of the element (within the page)
    element_center_x = element_location['x'] + (element_size['width'] / 2)
    element_center_y = element_location['y'] + (element_size['height'] / 2)

    # 6. Because Selenium's (0,0) is at the top-left *inside* the browser content,
    #    we must account for the browser's title bar & possible navigation bar.
    #    Adjust this based on your actual OS/browser theme.
    title_bar_height = 80  # Example offset; tweak to match your environment
    x_offset = 0
    y_offset = title_bar_height

    # Final absolute screen coordinates
    final_x = element_center_x + x_offset
    final_y = element_center_y + y_offset

    # 7. Move the real OS mouse pointer via PyAutoGUI (1 second travel)
    print(f"Moving mouse to screen coords: ({final_x}, {final_y})")
    pyautogui.moveTo(final_x, final_y, duration=1.0)

    # 8. Perform a real OS-level click
    pyautogui.click()

    # Pause to see the result
    time.sleep(3)
    driver.quit()

if __name__ == "__main__":
    main()
