from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set options for headless mode
options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1920x1080')

# Initialize WebDriver
driver = webdriver.Chrome(options=options)

# To go to a website
driver.get('https://google.com')

# Let's print page title
print(f"Page Title : {driver.title}")

# Quit Browser session
driver.quit()

