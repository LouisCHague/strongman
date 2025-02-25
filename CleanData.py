# Louis Hague, 21/02/2025

'''
The function of this file is to clean the scraped data
'''

# Imports
import pandas as pd

# Some of the records from PRLift Records are multiple reps, in comparison to 1RM
# Different formulas to calculate one rep max
# Brzycki formula: Weight × (36 / (37 – number of reps))
# Epley formula: Weight × (1 + (0.0333 × number of reps))
# Lombardi formula: Weight × (number of reps ^ 0.1)
# O’Conner formula: Weight × (1 + (0.025 × number of reps))

# Events with multiple reps
eventNames = ["Apollon's Axle Press", "Atlas Stone", "Log Lift", "Dumbbell", "Squat (suited)", "Deadlift (raw)",
              "Hummer Tire Deadlift (raw)", "Deadlift (suited)", '18" Deadlift (raw or suited)',	
              "Silver Dollar Deadlift (raw or suited)",	"Squat (raw)", "Overhead press",
              "Deadlift for Reps (raw)", "Log Lift for Reps",	"Viking Press",	"Apollon's Axle Double Overhand",
              "Rolling Thunder",	"Hilt/Grandfather Clock",	'Rolling Raptor 2"', 'Saxon Bar 3" (75mm) for Max',
              "Deadlift for Reps (suited)",	"Apollon's Axle Press for Reps", "Dumbbell for Reps",
              "Squat for Reps (suited)"]
#"Viking Press for Reps",

#eventNames = eventNames = ["Apollon's Axle Press"]

df = pd.read_csv("C:\\Users\\louis\\strongman_project\\PRLiftRecords_complete.csv")
print(df)

for event in eventNames:
    for index, row in df.iterrows():
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
            df.at[index, f'{event}'] = OneRM

# After the loop, save the DataFrame to a new CSV file (or overwrite the existing one)
df.to_csv("C:\\Users\\louis\\strongman_project\\PRLiftRecordsCompleteCleaned.csv", index=False)

# Optionally, you can also print the updated DataFrame to confirm changes
#print(df)