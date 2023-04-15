#pip install undetected-chromedriver
# import undetected_chromedriver as uc
# driver = uc.Chrome(use_subprocess=True)
# driver.get('https://nowsecure.nl')

import undetected_chromedriver as uc
import pyperclip
import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common import by
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
DEBUG=1
if DEBUG: print("Starting!")
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Automate button clicking and pasting content.')
parser.add_argument('input_website', type=str, help='The chatGPT conversation URL for file input')
parser.add_argument('input_file', type=str, help='The path to the input text file')
parser.add_argument('--chunk_size', type=int, default=2048, help='The desired chunk size (default: 2048)')
parser.add_argument('--username', type=str, help='The username for the input website (optional)')
parser.add_argument('--password', type=str, help='The password for the input website (optional)')
parser.add_argument('--wait', type=int,default=3, help='Time to wait for chatGPT to accept input')
parser.add_argument('--resume', type=int,default=0, help='Resume from Part X -- 0 = instruction included first')

args = parser.parse_args()

# Get the username and password from environment variables if not supplied
username = args.username or os.environ.get('INPUT_WEBSITE_USERNAME')
password = args.password or os.environ.get('INPUT_WEBSITE_PASSWORD')
SLEEP_TIME = args.wait

# URLs of the websites
button_website = "https://chatgpt-prompt-splitter.jjdiaz.dev/"

# Read the input text from the file
with open(args.input_file, 'r') as file:
    input_text = file.read()


# Copy the content to the clipboard
pyperclip.copy(input_text)


# Initialize the web driver
driver = uc.Chrome(use_subprocess=True)
# driver = webdriver.Chrome()

# Open the button website
driver.get(button_website)
time.sleep(1)

dropdown_selector = driver.find_element(by=by.By.ID,value="preset")
dropdown_selector.send_keys(Keys.DOWN)


# Set the chunk size
chunk_size_input = driver.find_element(by=by.By.ID,value="split_length")
chunk_size_input.clear()
chunk_size_input.send_keys(str(args.chunk_size))

# Insert the input text into the textarea
textarea = driver.find_element(by=by.By.ID,value="prompt")
textarea.clear()
textarea.click()
#textarea.send_keys(input_text)

# Use Selenium's ActionChains to paste the content from the clipboard
actions = ActionChains(driver)
actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

# Submit the form
submit_button = driver.find_element(by=by.By.ID,value="split-btn")
submit_button.click()

# Wait for the page to load the buttons
time.sleep(3)

# Get the total number of buttons
buttons = driver.find_elements(by=by.By.CSS_SELECTOR,value=".buttons-container .copy-btn")
total_buttons = len(buttons)

def click_button_and_wait_for_URL_change(driver, css_selector, timeout=10):
    global DEBUG
    if DEBUG: print("calling click but wait first: {css_selector}")
    current_url = driver.current_url
    
    # Find the button by its CSS selector and click it
    button = driver.find_element(by=by.By.CSS_SELECTOR, value=css_selector)
    button.click()
    
    # Wait for the page to change
    WebDriverWait(driver, timeout).until(EC.url_changes(current_url))


def click_button_and_wait_for_availability_first(driver, css_selector, timeout=10):
    global DEBUG
    if DEBUG: print("calling click but wait first: {css_selector}")
    current_url = driver.current_url
    
    # Find the button by its CSS selector and click it
    button = driver.find_element(by=by.By.CSS_SELECTOR, value=css_selector)
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(button))
    button.click()
    time.sleep(1)
    # Wait for the page to change


def login_if_needed():
    global DEBUG
    if DEBUG: print("Logging in called")
    desired_url = args.input_website
    current_url = driver.current_url

    if current_url != desired_url:
        print("Begining login as not desired url")
        #assume login button available, then login page is next page
        click_button_and_wait_for_URL_change(driver,"button div", 40)
        if DEBUG: time.sleep(3)

        # Fill in the username and password fields
        username_input = driver.find_elements(by=by.By.CSS_SELECTOR,value="[name=username]")[0]
        username_input.send_keys(username)
        if DEBUG: time.sleep(3)
        
        click_button_and_wait_for_availability_first(driver,"button[type=\"submit\"]")

        password_input = driver.find_elements(by=by.By.CSS_SELECTOR,value="[name=password]")[0]
        password_input.send_keys(password)
        if DEBUG: time.sleep(3)
        
        click_button_and_wait_for_URL_change(driver,"button[type=\"submit\"]")

        # Navigate to the desired URL
        driver.get(desired_url)
        WebDriverWait(driver, 20).until(EC.url_contains(desired_url))
        if DEBUG: time.sleep(3)
        time.sleep(1)


# Open the input website in a new tab
#driver.execute_script(f"window.open('https://chat.openai.com/auth/login', 'new_window')")
# driver.execute_script(f"window.open('{args.input_website}', 'new_window')")
driver.window_new()
driver.switch_to.window(driver.window_handles[1])
# driver.get(args.input_website)
driver.get('https://chat.openai.com/auth/login')
if DEBUG: time.sleep(3)

#<p id="cf-spinner-please-wait">Please stand by, while we are checking your browser...</p>
try:
    EC.text_to_be_present_in_element(driver.find_element(by=by.By.ID,value="cf-spinner-please-wait"),"Please stand by, while we are checking your browser...")
    print("interrupted by cloudflare...")
    try:
        print("Waiting for Login button")
        WebDriverWait(driver,20).until(EC.visibility_of(driver.find_element(by=by.By.XPATH, value=f"//button/div[contains(., 'Log in')]")))
        time.sleep(1)
    except:
        print("Failed to find cloudflare login button. sleeping for 30")
        time.sleep(30)
except:
    print("No cloudflare")
finally:
    time.sleep(1)



# Check if we need to log in and navigate to the desired URL
login_if_needed()


# ...

for i in range(args.resume, total_buttons):
    # Switch to the button website tab
    driver.switch_to.window(driver.window_handles[0])
    if DEBUG: time.sleep(3)

    # Find the button by index
    button = buttons[i]

    # Click the button to copy the text block
    button.click()

    # Switch to the input website tab
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(1)
    # Find the input box by unique CSS selector
    input_box = driver.find_elements(by=by.By.CSS_SELECTOR, value="form textarea[placeholder=\"Send a message...\"]")[0]

    # Paste the copied text block into the input box and press Enter
    input_box.send_keys(Keys.CONTROL, "v")
    if DEBUG: time.sleep(3)
    input_box.send_keys(Keys.ENTER)

    # Wait for the action to complete
    time.sleep(SLEEP_TIME)

# Close the browser
time.sleep(SLEEP_TIME)
driver.quit()

