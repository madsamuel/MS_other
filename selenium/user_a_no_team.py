import time
import logging
import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# --- Setup logging ---
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = f"log-{date_str}.log"
logging.basicConfig(
    filename=log_filename,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Starting Selenium simulation script.")

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser(
    description="Selenium simulation: scroll or simulate keyboard key presses."
)
parser.add_argument(
    "--mode",
    choices=["scroll", "keyboard"],
    default="scroll",
    help="Simulation mode: 'scroll' to scroll the page, 'keyboard' to simulate key presses.",
)
args = parser.parse_args()
logging.info("Simulation mode set to '%s'.", args.mode)

# --- Initialize the Edge WebDriver ---
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
    time.sleep(3)  # wait for the page to load
    logging.info("Amazon home page loaded.")

    # Locate the search box and enter "bateries"
    logging.info("Locating the search box.")
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    logging.info("Search box found. Entering 'bateries' and submitting the search.")
    search_box.send_keys("bateries")
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(5)  # wait for search results to load
    logging.info("Search results loaded.")

    # Perform simulation for 60 seconds based on the selected mode
    simulation_duration = 60  # seconds
    start_time = time.time()
    
    # scroll down the page
    logging.info("Starting continuous scrolling simulation for %d seconds.", simulation_duration)
    scroll_pause = 2   # seconds between scrolls
    scroll_pixels = 500  # pixels to scroll each time
    scroll_count = 0
    
    while time.time() - start_time < simulation_duration:
        driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
        scroll_count += 1
        logging.info("Scrolled down %d time(s).", scroll_count)
        time.sleep(scroll_pause)
    logging.info("Completed scrolling simulation.")
    
    # simalte static page
    logging.info("Starting keyboard simulation (pressing ALT key) for %d seconds.", simulation_duration)
    actions = ActionChains(driver)
    press_interval = 1  # press key every 1 second
    press_count = 0
    
    while time.time() - start_time < simulation_duration:
        # Press and release the ALT key.
        actions.key_down(Keys.ALT).key_up(Keys.ALT).perform()
        press_count += 1
        logging.info("Simulated ALT key press %d time(s).", press_count)
        time.sleep(press_interval)
    logging.info("Completed keyboard simulation.")
    
except Exception as e:
    logging.error("An error occurred during simulation: %s", e)
finally:
    driver.quit()
    logging.info("Closed the browser and ended the Selenium session.")
