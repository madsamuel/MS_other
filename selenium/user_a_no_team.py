import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Initialize the Edge WebDriver (ensure msedgedriver is installed)
driver = webdriver.Edge()

try:
    # Navigate to Amazon
    driver.get("https://www.amazon.com")
    
    # Allow the page to load
    time.sleep(3)
    
    # Locate the search box (Amazon's search input id is "twotabsearchtextbox")
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys("bateries")
    search_box.send_keys(Keys.RETURN)
    
    # Wait for the search results to load
    time.sleep(5)
    
    # Scroll continuously for 1 minute
    start_time = time.time()
    scroll_pause = 2  # seconds between scrolls
    scroll_pixels = 500  # pixels to scroll down each time

    while time.time() - start_time < 60:
        driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
        time.sleep(scroll_pause)

finally:
    # Close the browser after scrolling
    driver.quit()
