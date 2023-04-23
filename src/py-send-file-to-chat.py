#Uses code/service from https://github.com/jupediaz/chatgpt-prompt-splitter/
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
DEBUG=0
if DEBUG: print("Starting!")
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Automate button clicking and pasting content.')
parser.add_argument('input_website', type=str, help='The chatGPT conversation URL for file input')
parser.add_argument('input_file', type=str, help='The path to the input text file')
parser.add_argument('--chunk_size', type=int, default=2048, help='The desired chunk size (default: 2048)')
parser.add_argument('--username', type=str, help='The username for the input website (optional) Env Variable INPUT_WEBSITE_USERNAME')
parser.add_argument('--password', type=str, help='The password for the input website (optional) Env Variable INPUT_WEBSITE_PASSWORD')
parser.add_argument('--wait', type=int,default=3, help='Time to wait for chatGPT to accept input (optional:3s)')
parser.add_argument('--resume', type=int,default=0, help='Resume from Part X, default 0 = instruction included first')

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

# Now POC works, change to chunk self, like https://github.com/jupediaz/chatgpt-prompt-splitter/blob/main/api/index.py#L36-L59
def beep():
    print('\a')
    # testimport os
    #
    ## Windows
    #if os.name == 'nt':
    #    os.system('echo \a')
    #
    ## macOS
    #elif os.name == 'darwin':
    #    os.system('say "beep"')
    #
    ## Linux
    #else:
    #    os.system('echo -e "\a"')

    #OR----
    # import simpleaudio as sa
    # 
    # # Define the audio data as a byte string
    # audio_data = bytes.fromhex('FF 00 FF 00') * 440
    # 
    # # Create a SimpleAudio playback object and play the audio data
    # playback = sa.play_buffer(audio_data, 1, 2, 44100)
    # playback.wait_done()




# Copy the content to the clipboard
pyperclip.copy(input_text)


# Initialize the web driver
driver = uc.Chrome(use_subprocess=True)
# driver = webdriver.Chrome()


def find_first_element_by_selector(selector, selector_type=by.By.CSS_SELECTOR, wait_time=20, ec=EC.presence_of_element_located):
    element = WebDriverWait(driver, wait_time).until(ec((selector_type, selector)))
    return element

# click_me_button = find_first_element_by_selector("button div:contains('Click me')", ec=EC.element_to_be_clickable)
# message_box = find_first_element_by_selector("textarea[placeholder='Enter your message']")
# user_input = find_first_element_by_selector("[id^='user_']")

# find_button_by_text = lambda text: driver.find_element(by=by.By.CSS_SELECTOR, value=f"button div[contains(text(),'{text}')]/..")
# find_textarea_by_placeholder = lambda placeholder: driver.find_element(by=by.By.CSS_SELECTOR, value=f"textarea[placeholder='{placeholder}']")
# find_element_by_id_starts_with = lambda id_prefix: driver.find_element(by=by.By.XPATH, value=f"//*[starts-with(@id,'{id_prefix}')]")

def find_button_by_div_text(text , timeout=20):
    return find_first_element_by_selector(
        selector=f"//button/div[contains(text(),'{text}')]",
        selector_type= by.By.XPATH,
        wait_time=timeout
        )#.find_element(by=by.By.XPATH, value="..")

def find_textarea_by_placeholder(placeholder):
    return find_first_element_by_selector(f"textarea[placeholder='{placeholder}']")

def find_element_by_id_starts_with(id_prefix):
    return find_first_element_by_selector(f"*[id^='{id_prefix}']")


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
        print("Failed to find openAI login button. sleeping for 1.5s")
        time.sleep(1.5)
    try:
        print("Looking for Login button")
        WebDriverWait(driver,20).until(EC.visibility_of(driver.find_element(by=by.By.XPATH, value=f"//button/div[contains(., 'Log in')]")))
        time.sleep(1)
    except:
        beep()
        print("Failed to find openAI login button. sleeping for 60s - get to conversation page manually")
        time.sleep(1.5)
        
except:
    print("No cloudflare")
finally:
    time.sleep(1)



# Check if we need to log in and navigate to the desired URL
login_if_needed()


# paste in each chunk

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
    try:
        find_button_by_div_text('Stop generating', 5)
    except:
        print("Failed to find Stop generating button. sleeping for 0.5s")
        time.sleep(0.5)
    finally:
        pass
    find_button_by_div_text('Regenerate response')
    #time.sleep(SLEEP_TIME)

# Close the browser
time.sleep(SLEEP_TIME)
driver.quit()

