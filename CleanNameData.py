# Louis Hague
# 28/02/2025

'''
I have a list of strongmen names, however some are team names
remove all team names from the list
'''

# Imports
import pandas as pd

df = pd.read_csv("C:\\Users\\louis\\strongman_project\\athletes.csv")
#print(df)
df = df[~df['Name'].str.contains('Team', na=False)]
df_cleaned = df[~df['Name'].str.contains('TEAM', na=False)]
#print(df_cleaned)
df_cleaned.to_csv("C:\\Users\\louis\\strongman_project\\athleteNameCleaned.csv", index=False)