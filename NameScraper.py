# Louis Hague 
# 26/02/2025

'''The function of the file is to scrape the names of strongmen into an excel file so we aren't relying on 
my knowledge of strongman for the sample size/increase the sample size'''

# Imports
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import Select

# Driver Path
edge_driver_path = r"C:\\Users\\louis\\drivers\\msedgedriver.exe"
# Create a Service object
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)
# Open the Strength Results website profile section
driver.get("https://strengthresults.com/statistics/profileLists/cdcf-bbb4-4d7f-9306-26a3137e212e")
time.sleep(3)

# Dropdown path
dropdown_locator = (By.XPATH, '//*[@id="ngb-nav-4-panel"]/app-profile-lists/form/div[1]/select') 
# Wait for the dropdown to be visible
dropdown = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(dropdown_locator)
)
# Interact with dropdown
select = Select(dropdown)

# Loop through the countries in the dropdown
# Click the apply filter button
# Loop through the names, if the name has a date of birth record the name 
for country in select.options:
    if country.text != "Unknown":
        select.select_by_visible_text(country.text)
        time.sleep(1)