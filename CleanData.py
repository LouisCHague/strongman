# Louis Hague, 05/03/2025

'''
The function of this file is to combine all the CSVs into a single file and clean the scraped data
'''

# Imports
import os
import pandas as pd

# Folder containing the CSV files
filePath = "C:\\Users\\louis\\strongman_project\\AutoScrapeNames"

# Store DataFrames
dfList = []

# Combine CSVs
for file in os.listdir(filePath):
    file_path = os.path.join(filePath, file)
    df = pd.read_csv(file_path)
    dfList.append(df)

completeDF = pd.concat(dfList, ignore_index=True, sort=False)
print(completeDF)

# Remove athletes with NaN values for all exercises 
completeDF = completeDF.dropna(subset=completeDF.columns[2:], how='all')
# print(completeDF.iloc[0])

# # Some of the records from PRLift Records are multiple reps, in comparison to 1RM
# # Different formulas to calculate one rep max
# # Brzycki formula: Weight × (36 / (37 – number of reps))
# # Epley formula: Weight × (1 + (0.0333 × number of reps))
# # Lombardi formula: Weight × (number of reps ^ 0.1)
# # O’Conner formula: Weight × (1 + (0.025 × number of reps))

# Events
eventNames = ["Apollon's Axle Press", 'Atlas Stone', 'Deadlift (suited)', 'Log Lift',
              'Dumbbell', 'Squat (suited)', '18" Deadlift (raw or suited)', 'Silver Dollar Deadlift (raw or suited)',
              'Deadlift (raw)', 'Squat (raw)', 'Overhead press', 'Hummer Tire Deadlift (raw)', 'Viking Press',
              "Apollon's Axle Double Overhand", 'Rolling Thunder', 'Hilt/Grandfather Clock', 'Rolling Raptor 2"',
              'Saxon Bar 3" (75mm) for Max', "Farmer's Walk for Distance", "Farmer's Hold", 'Log Lift for Reps',
              'Deadlift for Reps (raw)', 'Deadlift for Reps (suited)', 'Dumbbell for Reps', "Apollon's Axle Press for Reps",
              'Viking Press for Reps', 'Squat for Reps (raw)', 'Squat for Reps (suited)']

for event in eventNames:
    for index, row in completeDF.iterrows():
        weightValue = row[f'{event}']
        # Need to ignore the NaN values
        if isinstance(weightValue, str) and '/' in weightValue:
            weightKG = weightValue[0:weightValue.index('/')]
            # Convert PRs with multiple reps into 1RM
            if 'x' in weightKG:
                # Weight lifted
                repWeight = weightKG[:weightKG.index('k')]
                # Number of reps
                repNumber = weightKG[weightKG.index('x')+1]
                # 1RM Calculation
                repWeight = float(repWeight.strip())
                repNumber = float(repNumber.strip())
                OneRM = repWeight * (36 / (37 - repNumber))
                # Conversion to string
                OneRM = str(round(OneRM,1))+'kg'
            else:
                # Remove trailing from removing /
                OneRM = weightKG.strip()

            # Override the value
            completeDF.at[index, f'{event}'] = OneRM

# print(completeDF)
completeDF.to_csv("C:\\Users\\louis\\strongman_project\\CompleteScrapeCleaned.csv", index=False)
