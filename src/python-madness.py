import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# URLs of the websites
button_website = "https://www.example.com"
input_website = "https://shopify.pdfdatanet.com"

driver = webdriver.Chrome()
# Open the button website
driver.get(button_website)
print(driver.current_url)

# Open the input website in a new tab
driver.execute_script(f"window.open('{input_website}', 'new_window')")
print(driver.current_url)
driver.switch_to.window('new_window')
print(driver.current_url)
driver.quit()