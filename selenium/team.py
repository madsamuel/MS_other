import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Set up Edge WebDriver
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")  # Open in full screen
driver = webdriver.Edge(options=options)

# Step 1: Open Microsoft Teams
teams_url = "https://teams.microsoft.com/"
driver.get(teams_url)
time.sleep(10)  # Wait for login

# Step 2: Assume user joins a call (simulated wait)
print("User is in a Teams call...")
time.sleep(10)  # Simulating time in call

# Step 3: Simulate Video Playback Mode (First Half)
print("Switching to video playback mode...")
time.sleep(10)  # Simulating watching a video playback

# Step 4: Simulate Video Full-Screen Mode (Second Half)
print("Switching to full-screen mode...")
# Simulate pressing the full-screen shortcut (F11)
webdriver.ActionChains(driver).send_keys(Keys.F11).perform()
time.sleep(10)  # Simulating watching screen share

# Close Browser
print("Automation Complete. Closing browser.")
driver.quit()
