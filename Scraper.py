# Louis Hague, 21/02/2025

'''
The function of this file is to scrape data from the Strength Results website,
this includes information such as personal bests, event podium placement and overall competition placement.
The three final functions will take a list of strongman names, search for these on the website and pipe
the result into a csv for later data science projects
'''

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

# Driver Path
edge_driver_path = r"C:\\Users\\louis\\drivers\\msedgedriver.exe"
# Create a Service object
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)
# Open the Strength Results website, Eddie Hall profile (No generic profile page)
driver.get("https://strengthresults.com/statistics/profiles/cdcf-bbb4-4d7f-9306-26a3137e212e")
# time.sleep(3)

def search_strongman(name):
    '''Loads webpage for specified strongman'''
    search_box = driver.find_element(By.ID, "search2")
    search_box.clear()
    search_box.send_keys(name)
    time.sleep(2)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)
    # Need to open the link to present all records
    element =driver.find_element(By.XPATH, "//span[text()='+ Show additional strongman records']")
    # Java click, does not require the element to be in view like Selenium
    driver.execute_script("arguments[0].click();", element)
    time.sleep(5)

def scrapePRS():
    '''Scrapes personal best information'''
     # Parse event information with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Dictionary to hold event and weight
    scrapeDict = {}

    # Scrape event names
    events = soup.find_all('td', class_='eventName')
    for event in events:
        event_name = event.text.strip()
        scrapeDict[event_name] = None
    #print(scrapeDict)

    # Scrape event record values
    records = soup.find_all('td', class_='record ng-star-inserted')
    count = 0
    for record in records:
        record_name = record.text.strip()
        #print(record_name)
        # Remove - value when value empty
        if record_name == '-':
           record_name = pd.NA
        # Get the event name based on the index
        #print(scrapeDict)
        event_name = list(scrapeDict.keys())[count]
        #print(event_name)
        scrapeDict[event_name] = record_name 
        count += 1
    # print(scrapeDict)
    return(scrapeDict)

def scrapePodium(athleteName):
    '''Scrapes athlete information and podium information from the page'''
     # Parse event information with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Scrape event names
    events = soup.find_all('tr', class_='ng-star-inserted')

    # Initialize variables to track state
    high_profile_data = []
    collect_high_profile = False

    # Loop through the rows
    for event in events:
        event_name = event.text.strip()
        # Clean up the text by removing extra spaces
        cleaned_text = re.sub(r'\s+', ' ', event_name).strip()
        
        # Check if we are within the "International, high-profile" section
        if "International, high-profile" in cleaned_text:
            collect_high_profile = True
            high_profile_data.append(cleaned_text)

        elif collect_high_profile:
            high_profile_data.append(cleaned_text)

    # HARD CODED #####################
    # Competition Rank Results
    compRank = high_profile_data[0:8]
    # # Need to put data into a dictionary for transformation to df
    compDict = {}
    compDict[athleteName] = compRank
    # Process data into DataFrame 
    processed_data = []

    for athlete, events in compDict.items():
        athlete_dict = {"Athlete": athlete}
        
        for event in events:
            parts = event.split()
            # HARD CODED BASED ON PLACEMENT NUMBER
            event_name = " ".join(parts[:-20])  
            #print(event_name)
            placements = list(map(int, parts[-20:])) 
            #print(placements)
            
            # Store each placement as a separate column
            for rank, value in enumerate(placements, start=1):
                athlete_dict[f"{event_name}_{rank}"] = value
        
        processed_data.append(athlete_dict)
    podiumDF = pd.DataFrame(processed_data)
    # print(podiumDF)     

    # Lift Rank Results
    # Remove Info from the end of the result
    liftRank = []
    for i in high_profile_data:
        if i[-4:] == "Info":
            liftRank.append(i[:-5])

    # Need to put data into a dictionary for transformation to df
    liftDict = {}
    liftDict[athleteName] = liftRank
    # Process data into DataFrame 
    processed_data = []

    for athlete, events in liftDict.items():
        athlete_dict = {"Athlete": athlete}
        
        for event in events:
            parts = event.split()
            # HARD CODED BASED ON PLACEMENT NUMBER
            event_name = " ".join(parts[:-10])  
            placements = list(map(int, parts[-10:])) 
            
            # Store each placement as a separate column
            for rank, value in enumerate(placements, start=1):
                athlete_dict[f"{event_name}_{rank}"] = value
        
        processed_data.append(athlete_dict)

    liftPodiumDf = pd.DataFrame(processed_data)
    # print(liftPodiumDf)

    return podiumDF, liftPodiumDf

# TEST 1
#search_strongman("Glenn Ross")
#scrape_event_records('Glenn Ross')
#scrape_event_podiums('Glenn Ross')

def MakePRDataframe(name):
    '''Returns df containing record data for strongman'''

    # Set up Dict containing competitor name to append to recordDict
    nameDict = {'Name': name}
    # Search for the strongman on the website
    search_strongman(name)

    # Pull the data from the website
    recordDict = scrapePRS()
    recordDict = dict(nameDict, **recordDict)
    #print(recordDict)
    recorddf = pd.DataFrame.from_dict([recordDict])
    #print(recorddf)

    # Save to CSV
    # file_name = 'StrongData.csv'
    # recorddf.to_csv(file_name, index=False)

    return recorddf

# TEST 2
# Retrieves data for lift records
# print(strongman_scrape('Glenn Ross'))
# Retrieves data for podium placement overall and for specific lifts
# print(scrape_event_podiums('Glenn Ross'))



def PRLiftRecords(strongList):
    '''Returns PR value for various lifts'''

    # Dataframe for accumulating information
    combinedDF = pd.DataFrame(columns=['Name'])
    for strongman in strongList:
        print(strongman)
        recorddf = MakePRDataframe(strongman)
        combinedDF = pd.concat([combinedDF, recorddf], ignore_index=True)
    #print(combinedDF)
    # Save to CSV
    file_name = 'PRLiftRecords_4.csv'
    combinedDF.to_csv(file_name, index=False)

def OverallPodium(strongList):
    '''Returns placement for complete competitions'''

    # Dataframe for accumulating information
    combinedDF = pd.DataFrame(columns=['Athlete'])
    for strongman in strongList:
        search_strongman(strongman)
        recorddf, seconddf = scrapePodium(strongman)
        combinedDF = pd.concat([combinedDF, recorddf], ignore_index=True)
    print(combinedDF)
    # Save to CSV
    file_name = 'OverallPodium.csv'
    combinedDF.to_csv(file_name, index=False)

def EventPodium(strongList):
    '''Returns podium placement for all events'''

    # Dataframe for accumulating information
    combinedDF = pd.DataFrame(columns=['Athlete'])
    for strongman in strongList:
        search_strongman(strongman)
        # Returns two dataframes, we only need one
        recorddf, seconddf = scrapePodium(strongman)
        combinedDF = pd.concat([combinedDF, seconddf], ignore_index=True)
    # print(combinedDF)
    # Save to CSV
    file_name = 'EventPodium.csv'
    combinedDF.to_csv(file_name, index=False)

# Test 3
# names = [
#     "Glenn Ross",
#     "Mark Felix",
#     "Luke Stoltman",
#     "Rauno Heinla",
#     "Laurence Shahlaei",
#     "Evan Singleton",
#     "Trey Mitchell",
#     "Adam Bishop",
#     "Rob Kearney",
#     "Gavin Bilton",
#     "Kevin Faires",
#     "Mateusz Kieliszkowski",
#     "Konstantine Janashia",
#     "Iron Biby",
#     "Bobby Thompson",
#     "Svend Karlsen",
#     "Mariusz Pudzianowski",
#     "Vasyl Virastyuk",
#     "Phil Pfister",
#     "Žydrūnas Savickas",
#     "Brian Shaw",
#     "Eddie Hall",
#     "Hafthór Júlíus Björnsson",
#     "Martins Licis",
#     "Oleksii Novikov",
#     "Tom Stoltman",
#     "Mitchell Hooper"
# ]

names = []

# BATCH 1
# "Pavlo Kordiyaka", "Tom Stoltman", "Bobby Thompson", "Konstantine Janashia", "Pa O'Dwyer", 
#     "Eddie Williams", "Oleksii Novikov", "Luke Stoltman", "Gavin Bilton", "Thomas Evans", 
#     "Kristján Jón Haraldsson", "Fadi El Masri", "Mitchell Hooper", "Mathew Ragg", "Aivars Šmaukstelis", 
#     "Mateusz Kieliszkowski", "Graham Hicks", "Spenser Remick", "Jaco Schoonwinkel", "Brian Shaw", 
#     "Rauno Heinla", "Adam Bishop", "Kevin Faires", "Gabriel Rhéaume", "Trey Mitchell", "Evan Singleton", 
#     "Eyþór Ingólfsson Melsteð"
# BATCH 2
# "Mark Felix", "Paul Smith", "Travis Ortmayer", "Jean-François Caron", 
#     "Martin Forsmark", "Robert Oberst", "Mateusz Baron", "Hafþór Júlíus Björnsson", "Dimitar Savatinov", 
#     "Rafal Kobylarz", "Josh Thigpen", "Akos Nagy", "Žydrūnas Savickas", "Mikhail Shivlyakov", 
#     "Nick Best", "David Nystrom", "Benedikt Magnússon", "Laurence Shahlaei", "Jerry Pritchett", 
#     "Dainis Zageris", "Krzysztof Radzikowski", "Gerhard Van Staden", "Mike Burke"
# BATCH 3
#     "Eddie Hall", "Matjaž Belšak", "Grzegorz Szymanski", "Mike Caruso", "Ole Martin Hansen", 
#     "Luke Richardson", "Iron Biby", "Svend Karlsen", "Mariusz Pudzianowski", "Vasyl Virastyuk", 
#     "Phil Pfister", "Martins Licis", "Glenn Ross", "Rob Kearney","Mikhail Koklyaev", "Robert Frampton",
#     "Jarek Dymek"

# Pull Data
# Use the functions individually
# Need to add error correction when there are issues with HTML 'Show more...'

PRLiftRecords(names)
#OverallPodium(names)
#EventPodium(names)