import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# List of random words
random_words = ["automation", "python", "selenium", "robotics", "quantum", "cybersecurity", "AI", "blockchain", "neural", "hologram"]

# List of specific words
specific_words = ["weather", "show time", "MSFT stock"]

# Select a random word from the specific list
search_word = random.choice(specific_words)

# Path to Edge WebDriver (modify if needed)
edge_driver_path = "msedgedriver.exe"  # Ensure this is in the correct location

# Set up Edge browser
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")  # Open in full-screen mode
driver = webdriver.Edge(options=options)

# Open Bing
driver.get("https://www.bing.com")

# Wait for the page to load
time.sleep(10)

# Find the search box and enter the selected word
search_box = driver.find_element(By.NAME, "q")  # 'q' is the name of Bing's search box
search_box.send_keys(search_word)

# Press Enter to search
search_box.send_keys(Keys.RETURN)

# Wait for results to load
time.sleep(3)

# Scroll up and down while waiting for time to expire
scroll_pause_time = 1  # Delay in seconds between scrolls
scroll_duration = 10  # Total duration to scroll in seconds

start_time = time.time()
while time.time() - start_time < scroll_duration:
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    # Scroll up
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(scroll_pause_time)

# Close the browser
driver.quit()
