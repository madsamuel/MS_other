import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # 1. Launch Chrome and maximize
    driver = webdriver.Chrome()
    driver.maximize_window()

    # 2. Go to YouTube
    driver.get("https://www.youtube.com/")

    # 3. Wait for the search bar to be present & clickable
    wait = WebDriverWait(driver, 10)
    # The main YouTube search box has CSS id="search" for the <input>
    search_bar = driver.find_element(By.ID, "search")

    # 4. (Optional) Scroll the element into view, just to ensure it's on-screen
    driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)

    # 5. Get element's location & size in page coordinates
    element_location = search_bar.location
    element_size = search_bar.size

    # Calculate the center point
    element_center_x = element_location['x'] + element_size['width'] / 2
    element_center_y = element_location['y'] + element_size['height'] / 2

    # 6. Account for title/navigation bar offsets 
    #    (adjust these values if your click lands incorrectly).
    title_bar_height = 80  # approximate offset for Windows with Chrome
    x_offset = 0
    y_offset = title_bar_height

    final_x = element_center_x + x_offset
    final_y = element_center_y + y_offset

    # 7. Move the OS mouse pointer to the search bar, then click
    print(f"Moving mouse to screen coords: ({final_x}, {final_y})")
    pyautogui.moveTo(final_x, final_y, duration=1.0)
    pyautogui.click()

    # 8. Type the search text and press ENTER
    pyautogui.typewrite("banana video", interval=0.05)
    pyautogui.press("enter")

    # Pause so we can watch the result
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    main()
