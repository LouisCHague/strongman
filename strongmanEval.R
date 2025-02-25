# Louis Hague 25/02/2025
# Strongman Analysis

# Imports
library(readr)
library(reshape2)
library(ggplot2)

setwd('C:\\Users\\louis\\strongman_project')
# Import Data
PRLiftRecords <- read.csv("PRLiftRecordsCompleteCleaned.csv", row.names=1)

# Apply gsub only to character columns
PRLiftRecords[] <- lapply(PRLiftRecords, function(x) {
  if (is.character(x)) {
    gsub("^([0-9.]+)kg$", "\\1", x)
  } else {
    x
  }
})

# Remove the columns which aren't numerical or have few records
PRLiftRecords <- PRLiftRecords[, !(colnames(PRLiftRecords) %in% c("Farmer.s.Walk.for.Distance", "Farmer.s.Hold", "Rolling.Raptor.2.","Squat..raw.","Hilt.Grandfather.Clock", "Viking.Press.for.Reps", 'Saxon.Bar.3...75mm..for.Max', 'Rolling.Thunder',"Apollon.s.Axle.Double.Overhand", "Squat.for.Reps..suited.", "Squat.for.Reps..raw.", "Silver.Dollar.Deadlift..raw.or.suited.", "Deadlift.for.Reps..suited."))]

PRLiftRecords[] <- lapply(PRLiftRecords, function(x) as.numeric(as.character(x)))
cormat <- round(cor(PRLiftRecords, use = "pairwise.complete.obs"), 2)
melted_cormat <- melt(cormat)

ggplot(data = melted_cormat, aes(x = Var1, y = Var2, fill = value)) + 
  geom_tile() +
  geom_text(aes(label = round(value, 2)), color = "white", size = 3) +  # Adds correlation values
  theme(
    axis.text.x = element_text(angle = 0, size = 6, hjust = 0.5),
    axis.text.y = element_text(size = 8)
  )


# Clustering
# Is there seperation based on maximum lift strength

# Imports
library(ggplot2)
library(cluster)

# Impute NAs with the median for each column
R_imputed <- PRLiftRecords
R_imputed[is.na(R_imputed)] <- apply(R_imputed, 2, function(x) median(x, na.rm = TRUE))[col(R_imputed)][is.na(R_imputed)]

# Standardise
scaled_data <- scale(R_imputed)

# Elbow method 
wss <- (nrow(scaled_data)-1)*sum(apply(scaled_data,2,var))
for (i in 2:10) {
  wss[i] <- sum(kmeans(scaled_data, centers=i)$withinss)
}
plot(1:10, wss, type="b", xlab="Number of clusters", ylab="Within-cluster sum of squares", main="Elbow Method")

# K-means
set.seed(42)
kmeans_result <- kmeans(scaled_data, centers = 2)
R_imputed$cluster <- kmeans_result$cluster
pca <- prcomp(scaled_data)
pca_data <- data.frame(pca$x, cluster=as.factor(R_imputed$cluster))
pca_data$Name <- rownames(pca_data)

# Step 6: Visualize the PCA results
ggplot(pca_data, aes(x=PC1, y=PC2, color=cluster)) +
  geom_point() +
  geom_text(aes(label=Name), vjust=1, hjust=1) +
  labs(title="PCA of Strongman Clusters", x="PC1", y="PC2") +
  theme_minimal()
