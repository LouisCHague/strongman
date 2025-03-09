# World's Strongest Man and World's Strongest Woman: Strength Trends & Athlete Profiling 

This repository contains the code and process used to scrape, clean, and extract data for strong-athletes, including their maximum lifts in a variety of competition exercises. The data was collected from [StrengthResults.com](https://strengthresults.com/statistics/profiles/cdcf-bbb4-4d7f-9306-26a3137e212e), focusing on extracting maximum recorded lifts for exercises of individual athletes. After filtering out teams and incomplete data, the final dataset contains records for 5,557 strongman competitors.

## Workflow Overview

The following steps were used to obtain and clean the data:

1. **Scraping Names and Birthdates (`NameScraper.py`)**  
   The first step was to scrape the names and birthdates of strong-athletes from the website, assuming that athletes listed with birthdates are more likely to have recorded maximum lifts available.
  
2. **Cleaning Names Data (`CleanNameData.py`)**  
   This script was used to remove any non-athlete entries, such as teams, from the list of scraped athlete names.

3. **Scraping Maximum Lifts (`Scraper.py`)**  
   Using Selenium, the script visited each athlete's profile page on StrengthResults.com. It searched for and scraped the maximum recorded lifts in various competition exercises for each athlete. The data was then saved in batches of 100 athletes per CSV file for easier handling.

4. **Cleaning the Data (`CleanData.py`)**  
   The data obtained from the scraping process was processed by:
     - Combining the CSV batches into a single dataframe.
     - Removing athletes who did not have any recorded lifts in any exercises.
     - Estimating the one-rep max (1RM) for events that had multiple repetitions.
     - Removing the pounds (lbs) measurement from the records to standardise the units.

5. **Identify trends, relationships, and groups between WSM & WSW athletes (`strongmanCompleteEventEval.R`)**
   - Standardises units, removes unreliable data, and filters athletes with sufficient lifts.
   - Visualises relationship between different one-rep max lifts.
   - Groups athletes by one-rep max performance using K-means and PCA.
  
## Results

### Lift Correlation Analysis
A correlation heatmap revealed strong relationships (≥0.8) between most strongathlete one-rep max lifts lifts. Notably:
- Pressing Movements: Log Lift and Apollon’s Axle Press showed high correlation (0.93-0.95), indicating transferable strength.
- Deadlift & Log Lift: Deadlift (Raw/Suited) correlated strongly with the Log Lift (0.88-0.89), suggesting significant posterior chain involvement beyond upper-body strength.

![My Image](Images/CorPlot.png)

### Log-Lift Performance Model
A Random Forest model was developed to predict Log Lift 1RM using key strength indicators (Apollon’s Axle Press, Dumbbell Press, Log Lift for Reps):
- Model R² = 90.89%, indicating a strong predictive capability.
- Root Mean Squared Error (RMSE) = 12kg, suggesting limitations due to missing biomechanical and training-related variables.
- Deadlift strength (Suited/Raw) ranked among the most significant predictors, reinforcing the importance of posterior chain development in pressing performance.
#### Limitations
- The model lacks longitudinal data (training history, recovery, nutrition), which may improve predictive accuracy.
- Correlations do not imply causation: While deadlift strength and log lift performance are highly correlated, further longitudinal studies are required to determine causal relationships.
- Variability in technique: Different pressing styles (Strict Press vs Split-Jerk) require distinct neuromuscular activation, which may impact predictive modeling accuracy.

### Clustering Analysis
- Overall Strength Clusters: Top-tier strongmen (e.g., Hafthor Björnsson, Tom Stoltman) grouped closely, reflecting elite strength trends.
- Mariusz Pudzianowski & Generational Strength Trends: Pudzianowski's dominance (5× WSM champion) is notable. However, the evolving depth of competition and modern training advancements introduce questions about whether his dominance could have been sustained in today’s field of elite strongmen.

![My Image](Images/strongmancompletecluster.png)

- Deadlift Specialists: High deadlift performers like Eddie Hall and Rauno Heinla formed distinct clusters, with projections for future record-breakers.

![My Image](Images/strongmandeadliftcluster.png)
  
- Pressing Strength: Zydrunas Savickas ("Big Z") stood apart as the strongest presser, while specialists like Luke Stoltman and Rob Kearney clustered nearby.

![My Image](Images/strongmanpresscluster.png)

- Strongwoman Clusters: Despite a smaller dataset (N=73), past WSW champions (e.g., Andrea Thompson, Donna Moore) formed a distinct grouping, with emerging athletes positioned for future success.

![My Image](Images/strongwomancompletecluster.png)

### Project Limitations
- This project highlighted the importance of thoroughly considering the potential uses and limitations of data before beginning the collection process. In hindsight, I should have more carefully evaluated how the data could be leveraged to draw meaningful conclusions. Whilst this project was an enjoyable experience, and I learned Selenium for web scraping, a more thoughtful and strategic approach to data collection at the outset would have helped in aligning the project goals with the available data

### Conclusion 
This analysis challenges the binary classification of strongman athletes (static vs. mobile lifters) by revealing nuanced strength profiles. Key takeaways:
- Elite strongman competitors exhibit distinct lifting trends, with specialisation playing a major role in competition success.
- Deadlift strength may influence pressing performance, particularly in Log and Axle Lift development.
- Strongwoman data requires expansion to fully understand performance clustering and emerging trends.
- This project lays the groundwork for future strength analysis research, emphasizing the need for longitudinal tracking and biomechanical integration for improved strongman performance modeling.
