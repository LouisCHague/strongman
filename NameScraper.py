# Louis Hague 
# 26/02/2025

'''The function of the file is to scrape the names of strongmen into an excel file so we aren't relying on 
my knowledge of strongman for the sample size/increase the sample size'''

# Imports
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import pandas as pd
import csv
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

# Open a CSV file to store the results
with open('athletes.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Name'])  

    for country in select.options:
        if country.text != "Unknown":
            select.select_by_visible_text(country.text)
            time.sleep(2)
            
            # Locate and click the 'Apply Filter' button
            buttonLocator = (By.XPATH, '/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/form/button')
            filterButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(buttonLocator))
            filterButton.click()
            time.sleep(4) 
            
            print(f'\nFiltered Country: {country.text}')
            # HARD CODED, FROM 1 TO LARGE NUMBER
            for i in range(1, 10000):  
                try:
                    athleteName = driver.find_element(By.XPATH, f'/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[{i}]/td[2]/span').text
                except:
                    # We have either ran out of names or there are no names
                    print(f'Complete Records for: {country.text}')
                    # Move to next country
                    break  
                
                try:
                    # All athletes should have a date of birth
                    athleteDOB = driver.find_element(By.XPATH, f'/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[{i}]/td[4]').text
                    
                    # Athletes without a date of birth most likely don't have records
                    if '(missing)' not in athleteDOB.split():
                        print(f'Athlete Name: {athleteName}')
                        print(f'Athlete DOB: {athleteDOB}')
                        
                        # Write to CSV
                        writer.writerow([athleteName])
                except:
                    print('No DOB')

        # Result 1
        #/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[1]/td[2]/span
        #/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[1]/td[4]

        # Result 2
        #/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[2]/td[2]/span
        #/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-lists/div[7]/table/tbody/tr[2]/td[4]