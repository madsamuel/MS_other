import time
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Create a log file name with the current date
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = f"log-{date_str}.log"

# Configure logging
logging.basicConfig(
    filename=log_filename,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Starting Selenium script to navigate Amazon and scroll continuously.")

# Initialize the Edge WebDriver (ensure msedgedriver is installed and in PATH)
try:
    driver = webdriver.Edge()
    logging.info("Edge WebDriver initialized.")
except Exception as e:
    logging.error("Failed to initialize Edge WebDriver: %s", e)
    raise

try:
    # Navigate to Amazon
    logging.info("Navigating to https://www.amazon.com")
    driver.get("https://www.amazon.com")
    
    # Allow the page to load
    time.sleep(3)
    logging.info("Amazon home page loaded.")

    # Locate the search box by its id and enter "bateries"
    logging.info("Locating the search box.")
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    logging.info("Search box found. Entering 'bateries' and submitting the search.")
    search_box.send_keys("bateries")
    search_box.send_keys(Keys.RETURN)
    
    # Wait for the search results to load
    time.sleep(5)
    logging.info("Search results loaded.")

    # Scroll continuously for 1 minute
    logging.info("Starting continuous scrolling for 60 seconds.")
    start_time = time.time()
    scroll_pause = 2  # seconds between scrolls
    scroll_pixels = 500  # pixels to scroll down each time

    scroll_count = 0
    while time.time() - start_time < 60:
        driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
        scroll_count += 1
        logging.info("Scrolled down %d time(s).", scroll_count)
        time.sleep(scroll_pause)
    
    logging.info("Completed 60 seconds of scrolling.")
    
except Exception as e:
    logging.error("An error occurred during the script execution: %s", e)
finally:
    # Close the browser after scrolling
    driver.quit()
    logging.info("Closed the browser and ended the Selenium session.")
