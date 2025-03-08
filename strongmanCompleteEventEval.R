# Louis Hague 03/03/2025
# Strongman Analysis

# Imports
library(reshape2)
library(tidyverse)
library(ggplot2)
library(mice)
library(dplyr)
library(readr)
library(tibble)
library(randomForest)
library(caret)
library(cluster)
#install.packages('janitor')
library(janitor)

# Remove items
rm()

# Set seed
set.seed(42)

#############
# Data Import
#############

setwd('C:\\Users\\louis\\strongman_project')
CompleteScrapeCleaned <- read_csv("CompleteScrapeCleaned.csv")

###############
# Data Cleaning
###############

# Remove kg from event columns
CompleteScrapeCleaned[] <- lapply(CompleteScrapeCleaned, function(x) {
  if (is.character(x)) {
    gsub("^([0-9.]+)kg$", "\\1", x)
  } else {
    x
  }
})

# Remove Farmers walk, difficulty in structuring records
CompleteScrapeCleaned <- CompleteScrapeCleaned %>% select(-starts_with("Farm"))

# All columns should be numeric apart from Name and Gender
CompleteScrapeCleaned[, -c(1, 2)] <- lapply(CompleteScrapeCleaned[, -c(1, 2)], as.numeric)

# How many non-NaN datapoints do we have per exercise
colSums(!is.na(CompleteScrapeCleaned))

# Remove columns with less than 400 non-NA values
CompleteScrapeCleaned <- CompleteScrapeCleaned[, colSums(!is.na(CompleteScrapeCleaned)) >= 400]
colSums(!is.na(CompleteScrapeCleaned))

# Obtain the athletes with robust strength profiles
TopAthletes <- CompleteScrapeCleaned[rowSums(!is.na(CompleteScrapeCleaned)) >= 11, ]

# If the there is more than 70% (N=297) of NaN in a column 
# then dropping that column is better than imputing
colSums(is.na(TopAthletes))

# Shorten the names of some lifts
names(TopAthletes)[names(TopAthletes) == '18" Deadlift (raw or suited)'] <- "SilverDollar Deadlift"
names(TopAthletes)[names(TopAthletes) == "Silver Dollar Deadlift (raw or suited)"] <- '18" Deadlift'

# Remove Duplicate Strongmen
TopAthletes <- TopAthletes %>% distinct(Name, .keep_all = TRUE)

# Clean the names for the mice library
TopAthletes <- TopAthletes %>% clean_names()

# Non-numeric Columns
metadata <- TopAthletes[, c("name", "gender")]

###########################################################################
# Is there a correlation between one rep max weights across different lifts
###########################################################################

# Exclude the first two columns (name and gender)
CompleteScrapeCleaned_numeric <- TopAthletes[, -c(1, 2)] 


# Compute the correlation matrix
corMatrix <- round(cor(CompleteScrapeCleaned_numeric, use = "complete.obs"), 2)

# Melt the correlation matrix for ggplot
meltcorMatrix <- melt(corMatrix)

# Heatmap
ggplot(data = meltcorMatrix, aes(x = Var1, y = Var2, fill = value)) + 
  geom_tile() +
  geom_text(aes(label = round(value, 2)), color = "white", size = 3) +
  scale_fill_continuous(name = "Cor") +  # Change the legend title to "Cor"
  theme(
    axis.text.x = element_text(angle = 0, size = 6, hjust = 0.5),
    axis.text.y = element_text(size = 8)
  )

########################
# Strongest correlations
########################

corMatrix_abs <- abs(corMatrix)
# Exclude self-correlations
diag(corMatrix_abs) <- NA

# Sort by correlation value in descending order
meltcorMatrix_abs <- melt(corMatrix_abs)
sorted_cor <- meltcorMatrix_abs[order(-meltcorMatrix_abs$value), ]

# Strongest correlations
top_correlations <- head(sorted_cor, 90)
top_correlations

##########################################################################
# Can we predict log-lift one rep max based on suited deadlift one rep max
##########################################################################
#cor(TopAthletes$deadlift_suited, TopAthletes$log_lift, use="complete.obs")

# Scatter plot with reg line
#ggplot(TopAthletes, aes(x = deadlift_suited, y = log_lift)) +
#  geom_point(color = "purple3", alpha = 0.6) +
#  geom_smooth(method = "lm", col = "orange1") +
#  labs(title = "Suited Deadlift vs Log Lift", x = "Suited Deadlift (kg)", y = "Log Lift (kg)") +
#  theme_grey()

# Fit a linear reg. model
model <- lm(deadlift_suited ~ log_lift, data = TopAthletes)

# Model summary
summary(model)
par(mfrow=c(2,2))
plot(model)

########
# Issues 
########

# High Correlation Between Movements
# Strongman athletes don’t typically train lifts in isolation.
# A model that predicts log lift purely from other lifts without 
# accounting for training overlap might miss nuances that explain performance differences.

#####################
# Random Forest Model
# To deal with the correlation between lifts
#####################

# Importance of Features
importance_rf <- randomForest(log_lift ~ ., data = CompleteScrapeCleaned_numeric, na.action = na.omit)
varImpPlot(importance_rf)

# Random Forest Model
selected_data <- CompleteScrapeCleaned_numeric[, c("log_lift", "apollons_axle_press", "dumbbell", "log_lift_for_reps")]
selected_features <- selected_data[,-1]
selected_label <- selected_data[,1]
# Impute Features
selected_features <- mice(selected_features, method = 'pmm')
selected_features <- complete(selected_features)
# Combine data
selected_data <- cbind(selected_label, selected_features)
dim(selected_data)
# Remove columns with NaN values
selected_data <- na.omit(selected_data)
dim(selected_data)

# Fit random forest model using the combined data
randomForest(log_lift ~ ., data = selected_data, na.action = na.omit)

###############################
# Optimised Random Forest Model
###############################

tuned_mtry <- tuneRF(selected_data[, -which(names(selected_data) == "log_lift")],
                     selected_data$log_lift, 
                     stepFactor = 1.5, 
                     improve = 0.01, 
                     trace = TRUE)

# 10-fold cross-validation
train_control <- trainControl(method = "cv", number = 10) 
rf_model <- train(log_lift ~ ., data = selected_data, 
                  method = "rf", 
                  trControl = train_control, 
                  tuneGrid = expand.grid(mtry = tuned_mtry[, 1])) 

print(rf_model)

##################
# Cluster Athletes 
##################

# Function to cluster athletes
perform_clustering <- function(data, gender_filter = "All", focus = "All") {
  
  # Set seed
  set.seed(42)
  
  
  # Filter Gender
  if (gender_filter == "Male") {
    data <- data %>% filter(gender == "Male")
  } else if (gender_filter == "Female") {
    data <- data %>% filter(gender == "Female")
  }
  
  # Store non-numeric columns
  metadata <- data[, c("name", "gender")]
  
  # Extract numeric columns
  data_numeric <- data[, -c(1, 2)]
  
  # Focus on lift
  if (focus == "Deadlift") {
    data_numeric <- data_numeric[, grep("deadlift", colnames(data_numeric))]
  } else if (focus == "Press") {
    data_numeric <- data_numeric[, grep("log|dumbbell|press", colnames(data_numeric))]
  }
  # print(data_numeric)
  
  # Assuming 'CompleteScrapeCleaned_numeric' is your data frame
  #non_na_counts <- colSums(!is.na(CompleteScrapeCleaned_numeric))
  # Remove columns with fewer than 2000 non-NA values
  #CompleteScrapeCleaned_numeric <- CompleteScrapeCleaned_numeric[, non_na_counts >= 2000]
  #view(CompleteScrapeCleaned_numeric)
  
  # Impute NaN values
  imputed_data <- mice(data_numeric, method = 'pmm')
  data_imputed <- complete(imputed_data)
  
  # Standardise
  scaled_data <- scale(data_imputed)
  
  # Perform K-means clust
  kmeans_result <- kmeans(scaled_data, centers = 2)
  data_imputed$cluster <- as.factor(kmeans_result$cluster)
  
  # Merge metadata
  data_imputed <- cbind(metadata, data_imputed)
  
  # Perform PCA
  pca <- prcomp(scaled_data)
  # print(pca$rotation)
  pca_data <- data.frame(pca$x, cluster = data_imputed$cluster, 
                         Gender = data_imputed$gender, Name = data_imputed$name)
  
  # If Deadlift focus, classify high deadlift vs lower deadlift
  if (focus == "Deadlift") {
    data_imputed$high_deadlift <- ifelse(data_imputed$deadlift_suited > 430, 
                                         ">430kg Deadlift", "<430kg Deadlift")
    
    # high_deadlift as factor
    data_imputed$high_deadlift <- as.factor(data_imputed$high_deadlift)
    pca_data$high_deadlift <- data_imputed$high_deadlift
  
  # Deadlift Cluster Plot
  plot <- ggplot(pca_data, aes(x = PC1, y = PC2, color = cluster, shape = high_deadlift)) +
    geom_point(size = 2, alpha = 0.8) +
    geom_text(aes(label = Name), vjust = 1, hjust = 1, size = 2.5) +
    scale_color_manual(values = c("purple3", "orange3")) +
    labs(title = paste("PCA of Strongman Clusters (", focus, ", ", gender_filter, ")", sep = ""),
         x = "PC1", y = "PC2") +
    theme_minimal()
  
  }
  
  else {
    # Basic Cluster Plot
    plot <- ggplot(pca_data, aes(x = PC1, y = PC2, color = cluster)) +
      geom_point(size = 2, alpha = 0.8) +
      geom_text(aes(label = Name), vjust = 1, hjust = 1, size = 2.5) +
      scale_color_manual(values = c("purple3", "orange3")) +
      labs(title = paste("PCA of Strongman Clusters (", focus, ", ", gender_filter, ")", sep = ""),
           x = "PC1", y = "PC2") +
      theme_minimal()
  }
  
  print(plot)
}

# Function Call
perform_clustering(TopAthletes, gender_filter = "Male", focus = "Press")

# Number of Athletes
#TopAthletes[TopAthletes$gender == 'Female',]
# TopAthletes[TopAthletes$gender == 'Male',]

# Athlete Search
#view(TopAthletes[TopAthletes$name %in% c("Vytautas Lalas", "Mitchell Hooper"), ])

#pressData <- TopAthletes[, grep("press|log|dumbbell", colnames(TopAthletes))]
#pressData <- cbind(metadata, pressData)
#view(pressData[pressData$name %in% c("Tom Stoltman","Luke Stoltman", "Rob Kearney", "Evan Singleton", "Zydrunas Savickas", "Eddie Hall" ,"Brian Shaw", "Mitchell Hooper", "Oleksii Novikov"), ])
