
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager

# Obtain the chromedriver needed

driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))

val = input(“Enter a url: “)
wait = WebDriverWait(driver, 10)
driver.get(val)

get_url = driver.current_url
wait.until(EC.url_to_be(val))

if get_url == val:
    page_source = driver.page_source


#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.keys import Keys

# Set the path to your webdriver (e.g., ChromeDriver)
# Make sure you have the appropriate webdriver for your browser version
# Download ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
#driver_path = '/Users/david/bin/chromedriver'

# Create a ChromeOptions instance
#options = Options()
#options.add_argument('--disable-extensions')  # Optional: Disable browser extensions

# Create the WebDriver instance with the specified options
#driver = webdriver.Chrome(executable_path=driver_path, options=options)

# URL of the login page
login_url = 'https://example.com/login'

# Open the login page
driver.get(login_url)

# Find the username and password input fields and enter your credentials
username_field = driver.find_element_by_name('username')  # Adjust this based on the actual HTML
password_field = driver.find_element_by_name('password')  # Adjust this based on the actual HTML

# Enter the username and password
username_field.send_keys('student')
password_field.send_keys('studentpassword')

# Submit the form
password_field.send_keys(Keys.RETURN)

# Wait for the login to complete (you might need to adjust the wait time)
# This is just a simple example, you might want to use more robust waiting mechanisms
driver.implicitly_wait(10)

# Now you're logged in and can proceed with other actions on the website

# Close the browser when you're done
driver.quit()
onclick="PrintCourseworkFromSummary()"

<span title="" class="k-widget k-dropdown k-header" 
        unselectable="on" role="listbox" aria-haspopup="true" aria-expanded="false" tabindex="0" 
        aria-owns="mCourseworkRangeId_1728_listbox" 
        aria-live="polite" aria-disabled="false" aria-busy="false" style="width: 200px; margin-bottom: 3px;" 
        aria-activedescendant="a85a3313-a3a8-4554-8a62-c9a9c23d44fc">
    <span unselectable="on" class="k-dropdown-wrap k-state-default">
        <span unselectable="on" class="k-input">All Coursework
        </span>
        <span unselectable="on" class="k-select" aria-label="select">
            <span class="k-icon k-i-arrow-60-down">
            </span>
        </span>
    </span>
    <input id="mCourseworkRangeId_1728" name="mCourseworkRangeId_1728" 
            style="width: 200px; margin-bottom: 3px; display: none;" type="text" value="5" data-role="dropdownlist">
</span>
