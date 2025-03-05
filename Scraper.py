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
    time.sleep(2)
    # Error for some records, consistently cannot find the '+ Show additional...' element
    # If unable to find, ignore this entry
    try:
        additionalRecords = driver.find_element(By.XPATH, "//span[text()='+ Show additional strongman records']")
        # Wait until button is clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(additionalRecords))
        # Java click, does not require the element to be in view
        driver.execute_script("arguments[0].click();", additionalRecords)
        #time.sleep(5)
    except:
        print(f'ERROR: COULD NOT OPEN ADDITIONAL RECORDS FOR: {name}\n')
        return False


def scrapePRS():
    '''Scrapes personal best information'''
     # Parse event information with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Dictionary to hold event and weight
    scrapeDict = {}

    # Find Gender 
    # If this is not an athlete but a team, assign gender = None
    try:
        gender = driver.find_element(By.XPATH, '/html/body/app-root/div[5]/app-statistics/div[2]/div[3]/div/div/app-profile-statistics/div[1]/div[2]/div/app-profile-quick-fact/div[1]/div/table/tbody/tr[5]/td[2]')
    except:
        gender = None

    # Scrape event names
    events = soup.find_all('td', class_='eventName')
    for event in events:
        event_name = event.text.strip()
        scrapeDict[event_name] = None
    #print(scrapeDict)

    # Scrape personal record value for each event
    records = soup.find_all('td', class_='record ng-star-inserted')
    count = 0
    for record in records:
        # Don't go outside of the PR event table
        if count <= 19:
            record_name = record.text.strip()
            #print(record_name)
            # Remove - value when value empty
            if record_name == '-':
                record_name = pd.NA
            # Get the event name based on the index
            #print(scrapeDict)
            #print(count)
            event_name = list(scrapeDict.keys())[count]
            #print(event_name)
            scrapeDict[event_name] = record_name 
            count += 1
        else:
            break
    # print(scrapeDict)
    return(gender, scrapeDict)

# TEST 1
#search_strongman("Glenn Ross")
#scrape_event_records('Glenn Ross')

def MakePRDataframe(name):
    '''Returns df containing record data for strongman'''

    # Set up Dict containing competitor name to append to recordDict
    nameDict = {'Name': name}
    # Search for the strongman on the website
    failValue = search_strongman(name)
    # print(f'Fail value: {failValue}')

    # If search failed (Usually a duplicate entry)
    if failValue != False:
        # Pull the data from the website
        gender, recordDict = scrapePRS()

        # If the return value is NOT a team
        if gender != None:
            genderDict = {'Gender': gender.text}

            # Add the name and gender values
            recordDict = dict(genderDict,**recordDict)
            recordDict = dict(nameDict, **recordDict)

            #print(recordDict)
            recorddf = pd.DataFrame.from_dict([recordDict])
            #print(recorddf)

            # Save to CSV
            # file_name = 'StrongData.csv'
            # recorddf.to_csv(file_name, index=False)
            return recorddf
        else:
            recorddf = pd.DataFrame()
            return recorddf
    else:
        # ERROR THROWN, return blank dataframe
        recorddf = pd.DataFrame()
        return recorddf

# TEST 2
# Retrieves data for lift records
# print(strongman_scrape('Glenn Ross'))
# Retrieves data for podium placement overall and for specific lifts
# print(scrape_event_podiums('Glenn Ross'))

def PRLiftRecords(strongList,fileName):
    '''Returns PR value for various lifts'''

    # Dataframe for accumulating information
    combinedDF = pd.DataFrame(columns=['Name'])
    for strongman in strongList:
        #print(strongList)
        print(strongman)
        recorddf = MakePRDataframe(strongman)
        #print(f'Dataframe: {strongman}')
        #print(recorddf)
        combinedDF = pd.concat([combinedDF, recorddf], ignore_index=True)
    #print(combinedDF)
    # Save to CSV
    print('\nCSV SAVED!\n')
    combinedDF.to_csv(fileName, index=False)

# TEST 3
# Does it make a csv with the name Glenn Ross
# PRLiftRecords(['Glenn Ross', 'fhbwejhfbwej'], 'test_1.csv')




# Automate Data Scrape
def process_batches(file_path, batch_size):
    '''Scrape PR information for list of athletes in batches'''

    df = pd.read_csv(file_path)
    # REMOVE INDEXING BELOW
    # df = df[5400:]

    names = df['Name'].tolist()
    num_batches = len(names) // batch_size + (1 if len(names) % batch_size else 0)
    
    for i in range(num_batches):
        start_idx = i * batch_size
        #print(start_idx)
        end_idx = start_idx + batch_size
        #print(batch_size)
        batch = names[start_idx:end_idx]
        #print(batch)
        
        PRLiftRecords(batch, f'AutoScrapeNames/PRLiftRecordsAutomated_{start_idx}_{end_idx}.csv')

# Function Call
process_batches("C:\\Users\\louis\\strongman_project\\athleteNameCleaned.csv", 100)












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

#names = []

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

#PRLiftRecords(names)























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

#OverallPodium(names)
#EventPodium(names)