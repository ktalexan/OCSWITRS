#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data Processing #
# PART 2: CREATING TIME SERIES DATA ####
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 1.1. Environment Setup ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Empty the R environment before running the code
rm(list = ls())

# Set the plot size for the R graphics device
#dev.new(width = 6, height = 4, unit="in")

# Open the R Libraries master file (located in Obsidian's library folder) - Already defined in the project_directories function
#libMaster = file.path(Sys.getenv("HOME"), "Knowledge Management", "Documents", "Data Science", "RPackagesInstallation.R")
#file.edit(libMaster)


## 1.2. Import Libraries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the pacman library. If not installed, install it first.
if (!requireNamespace("pacman", quietly = TRUE)) {
    install.packages("pacman")
}
library(pacman)

# Load the required libraries using pacman
pacman::p_load(RColorBrewer, lubridate, jsonlite, dplyr, magrittr, R6, haven, labelr, plyr, stringr, purrr, glue, Hmisc, psych, tibble, here, tidyr, chattr, knitr, labelled, collapse, formattable, sf, sp, ggthemes, arcgisutils)


## 1.3. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

getwd()

# Load the project functions from the RData file located in the /Data/R directory
load(file = file.path(getwd(), "scripts", "rData", "projectFunctions.RData"))


## 1.4. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- projectMetadata(part = 2)

# Get the project directories
prjDirs <- projectDirectories()

# if needed, open the library master file
#system(paste("code --", glue("\"{prjDirs$master_lib_path}\"")))


## 1.5. Set the working directory ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the working directory to the data directory
setwd(prjDirs$rDataPath)
getwd()


## 1.6. Load Data Frames ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the OCSWITRS data from the RData file
sapply(c("collisions.RData", "collisions.agp.RData", "crashes.RData", "crashes.agp.RData", "parties.RData", "parties.agp.RData", "victims.RData", "victims.agp.RData", "cities.RData", "cities.agp.RData", "roads.RData", "roads.agp.RData", "boundaries.RData", "boundaries.agp.RData"), load, .GlobalEnv)

# load the codebook file
load(file = file.path(prjDirs$codebookPath, "cb.RData"))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Aggregation Variable list ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 2.1. Lists by Statistic ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# List of sum columns
fSumList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fSum == 1)]
names(fSumList) <- paste0(fSumList, "Sum")

# List of min columns
fMinList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMin == 1)]
names(fMinList) <- paste0(fMinList, "Min")

# List of max columns
fMaxList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMax == 1)]
names(fMaxList) <- paste0(fMaxList, "Max")

# List of mean columns
fMeanList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMean == 1)]
names(fMeanList) <- paste0(fMeanList, "Mean")

# List of standard deviation columns
fSdList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fSd == 1)]
names(fSdList) <- paste0(fSdList, "Sd")

# List of median columns
fMedianList <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMedian == 1)]
names(fMedianList) <- paste0(fMedianList, "Median")


## 2.2. Collisions Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the collisions aggregates
fListCollisions <- list(
    fsum = fSumList,
    fmin = fMinList,
    fmax = fMaxList,
    fmean = fMeanList,
    fsd = fSdList,
    fmedian = fMedianList
)


## 2.3. Crashes Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the crashes aggregates
fListCrashes <- list()
if (length(fSumList[fSumList %in% names(crashes)]) > 0) {
    fListCrashes$fsum <- fSumList[fSumList %in% names(crashes)]
}
if (length(fMinList[fMinList %in% names(crashes)]) > 0) {
    fListCrashes$fmin <- fMinList[fMinList %in% names(crashes)]
}
if (length(fMaxList[fMaxList %in% names(crashes)]) > 0) {
    fListCrashes$fmax <- fMaxList[fMaxList %in% names(crashes)]
}
if (length(fMeanList[fMeanList %in% names(crashes)]) > 0) {
    fListCrashes$fmean <- fMeanList[fMeanList %in% names(crashes)]
}
if (length(fSdList[fSdList %in% names(crashes)]) > 0) {
    fListCrashes$fsd <- fSdList[fSdList %in% names(crashes)]
}
if (length(fMedianList[fMedianList %in% names(crashes)]) > 0) {
    fListCrashes$fmedian <- fMedianList[fMedianList %in% names(crashes)]
}


## 2.4. Parties Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the parties aggregates
fListParties <- list()
if (length(fSumList[fSumList %in% names(parties)]) > 0) {
    fListParties$fsum <- fSumList[fSumList %in% names(parties)]
}
if (length(fMinList[fMinList %in% names(parties)]) > 0) {
    fListParties$fmin <- fMinList[fMinList %in% names(parties)]
}
if (length(fMaxList[fMaxList %in% names(parties)]) > 0) {
    fListParties$fmax <- fMaxList[fMaxList %in% names(parties)]
}
if (length(fMeanList[fMeanList %in% names(parties)]) > 0) {
    fListParties$fmean <- fMeanList[fMeanList %in% names(parties)]
}
if (length(fSdList[fSdList %in% names(parties)]) > 0) {
    fListParties$fsd <- fSdList[fSdList %in% names(parties)]
}
if (length(fMedianList[fMedianList %in% names(parties)]) > 0) {
    fListParties$fmedian <- fMedianList[fMedianList %in% names(parties)]
}


## 2.5. Victims Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the victims aggregates
fListVictims <- list()
if (length(fSumList[fSumList %in% names(victims)]) > 0) {
    fListVictims$fsum <- fSumList[fSumList %in% names(victims)]
}
if (length(fMinList[fMinList %in% names(victims)]) > 0) {
    fListVictims$fmin <- fMinList[fMinList %in% names(victims)]
}
if (length(fMaxList[fMaxList %in% names(victims)]) > 0) {
    fListVictims$fmax <- fMaxList[fMaxList %in% names(victims)]
}
if (length(fMeanList[fMeanList %in% names(victims)]) > 0) {
    fListVictims$fmean <- fMeanList[fMeanList %in% names(victims)]
}
if (length(fSdList[fSdList %in% names(victims)]) > 0) {
    fListVictims$fsd <- fSdList[fSdList %in% names(victims)]
}
if (length(fMedianList[fMedianList %in% names(victims)]) > 0) {
    fListVictims$fmedian <- fMedianList[fMedianList %in% names(victims)]
}


## 2.6. Cities Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the cities aggregates
fListCities <- list()
if (length(fSumList[fSumList %in% names(cities)]) > 0) {
    fListCities$fsum <- fSumList[fSumList %in% names(cities)]
}
if (length(fMinList[fMinList %in% names(cities)]) > 0) {
    fListCities$fmin <- fMinList[fMinList %in% names(cities)]
}
if (length(fMaxList[fMaxList %in% names(cities)]) > 0) {
    fListCities$fmax <- fMaxList[fMaxList %in% names(cities)]
}
if (length(fMeanList[fMeanList %in% names(cities)]) > 0) {
    fListCities$fmean <- fMeanList[fMeanList %in% names(cities)]
}
if (length(fSdList[fSdList %in% names(cities)]) > 0) {
    fListCities$fsd <- fSdList[fSdList %in% names(cities)]
}
if (length(fMedianList[fMedianList %in% names(cities)]) > 0) {
    fListCities$fmedian <- fMedianList[fMedianList %in% names(cities)]
}


## 2.7. Roads Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# # Combine the lists into a single list for the roads aggregates
fListRoads <- list()
if (length(fSumList[fSumList %in% names(roads)]) > 0) {
    fListRoads$fsum <- fSumList[fSumList %in% names(roads)]
}
if (length(fMinList[fMinList %in% names(roads)]) > 0) {
    fListRoads$fmin <- fMinList[fMinList %in% names(roads)]
}
if (length(fMaxList[fMaxList %in% names(roads)]) > 0) {
    fListRoads$fmax <- fMaxList[fMaxList %in% names(roads)]
}
if (length(fMeanList[fMeanList %in% names(roads)]) > 0) {
    fListRoads$fmean <- fMeanList[fMeanList %in% names(roads)]
}
if (length(fSdList[fSdList %in% names(roads)]) > 0) {
    fListRoads$fsd <- fSdList[fSdList %in% names(roads)]
}
if (length(fMedianList[fMedianList %in% names(roads)]) > 0) {
    fListRoads$fmedian <- fMedianList[fMedianList %in% names(roads)]
}


## 2.8. Cleaning Aggregation Lists ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Delete the PartyNumberMax element from the fListVictims$fMax list
fListVictims$fmax <- fListVictims$fmax[!names(fListVictims$fmax) %in% "partyNumberMax"]

# Delete the PartyNumberMean element from the fListVictims$fMean list
fListVictims$fmean <- fListVictims$fmean[!names(fListVictims$fmean) %in% "partyNumberMean"]

# Delete the PartyNumberSd element from the fListVictims$fSd list
fListVictims$fsd <- fListVictims$fsd[!names(fListVictims$fsd) %in% "partyNumberSd"]

# Remove the individual stats lists
rm(fSumList, fMinList, fMaxList, fMeanList, fSdList, fMedianList)


## 2.9. Prepare Aggregation Temp Dataset ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a temporary data frame for the time series aggregation
tsCollisions <- collisions
tsCollisions$dateYear <- as.Date(tsCollisions$dateYear)
tsCollisions$dateQuarter <- as.Date(tsCollisions$dateQuarter)
tsCollisions$dateMonth <- as.Date(tsCollisions$dateMonth)
tsCollisions$dateWeek <- as.Date(tsCollisions$dateWeek)
tsCollisions$dateDay <- as.Date(tsCollisions$dateDay)

tsCrashes <- crashes
tsCrashes$dateYear <- as.Date(tsCrashes$dateYear)
tsCrashes$dateQuarter <- as.Date(tsCrashes$dateQuarter)
tsCrashes$dateMonth <- as.Date(tsCrashes$dateMonth)
tsCrashes$dateWeek <- as.Date(tsCrashes$dateWeek)
tsCrashes$dateDay <- as.Date(tsCrashes$dateDay)

tsParties <- parties
tsParties$dateYear <- as.Date(tsParties$dateYear)
tsParties$dateQuarter <- as.Date(tsParties$dateQuarter)
tsParties$dateMonth <- as.Date(tsParties$dateMonth)
tsParties$dateWeek <- as.Date(tsParties$dateWeek)
tsParties$dateDay <- as.Date(tsParties$dateDay)

tsVictims <- victims
tsVictims$dateYear <- as.Date(tsVictims$dateYear)
tsVictims$dateQuarter <- as.Date(tsVictims$dateQuarter)
tsVictims$dateMonth <- as.Date(tsVictims$dateMonth)
tsVictims$dateWeek <- as.Date(tsVictims$dateWeek)
tsVictims$dateDay <- as.Date(tsVictims$dateDay)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Aggregation by Year ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tsMerge <- function(t1, t2, t3, t4, t5, byVar) {
    # merge the first two data frames
    merge1 <- merge(t1, t2, by = byVar)
    # if the column name in test includes ".y", delete set the column to NULL
    merge1 <- merge1[, !grepl("[.]y$", colnames(merge1))]
    # if the column name in test includes ".x", remove the ".x" from the column name
    colnames(merge1) <- gsub("[.]x$", "", colnames(merge1))
    
    # merge the third data frame
    merge2 <- merge(merge1, t3, by = byVar)
    merge2 <- merge2[, !grepl("[.]y$", colnames(merge2))]
    colnames(merge2) <- gsub("[.]x$", "", colnames(merge2))
    
    # merge the fourth data frame
    merge3 <- merge(merge2, t4, by = byVar)
    merge3 <- merge3[, !grepl("[.]y$", colnames(merge3))]
    colnames(merge3) <- gsub("[.]x$", "", colnames(merge3))
    
    # merge the fifth data frame
    merge4 <- merge(merge3, t5, by = byVar)
    merge4 <- merge4[, !grepl("[.]y$", colnames(merge4))]
    colnames(merge4) <- gsub("[.]x$", "", colnames(merge4))
    
    return(merge4)
}


## 3.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by year
t1 <- data.frame(collap(tsCrashes, ~dateYear, custom = fListCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by year
t2 <- data.frame(collap(tsParties, ~dateYear, custom = fListParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by year
t3 <- data.frame(collap(tsVictims, ~dateYear, custom = fListVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by year
t4 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateYear, custom = fListCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by year
t5 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateYear, custom = fListRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 3.2. Compile Year Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsYear <- tsMerge(t1, t2, t3, t4, t5, "dateYear")

# Remove the rows with missing values
tsYear <- tsYear[!is.na(tsYear$dateYear), ]

# for each column in the tsYear_collisions data frame, replace the column with a time series object
for (i in 2:ncol(tsYear)) {
    tsYear[[i]] <- ts(tsYear[[i]], frequency = 1, start = c(2012))
}
rm(i, t1, t2, t3, t4, t5)


## 3.3. Add new variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate combined fatal and severe count
tsYear$countFatalSevereSum <- tsYear$numberKilledSum + tsYear$countSevereInjSum
tsYear$countFatalSevereMean <- tsYear$numberKilledMean + tsYear$countSevereInjMean
tsYear$countFatalSevereSd <- tsYear$numberKilledSd + tsYear$countSevereInjSd

# order the sum_fatal_severe after the sum_number_injured column in the tsYear data frame
tsYear <- tsYear %>% relocate(countFatalSevereSum, .after = countSevereInjSum)
tsYear <- tsYear %>% relocate(countFatalSevereMean, .after = countSevereInjMean)
tsYear <- tsYear %>% relocate(countFatalSevereSd, .after = countSevereInjSd)

# generate combined minor and pain count
tsYear$countMinorPainSum <- tsYear$countVisibleInjSum + tsYear$countComplaintPainSum
tsYear$countMinorPainMean <- tsYear$countVisibleInjMean + tsYear$countComplaintPainMean
tsYear$countMinorPainSd <- tsYear$countVisibleInjSd + tsYear$countComplaintPainSd

# order the sum_minor_pain after the countComplaintPainSum column in the tsYear data frame
tsYear <- tsYear %>% relocate(countMinorPainSum, .after = countComplaintPainSum)
tsYear <- tsYear %>% relocate(countMinorPainMean, .after = countComplaintPainMean)
tsYear <- tsYear %>% relocate(countMinorPainSd, .after = countComplaintPainSd)


## 3.4. General Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add data frame label
tsYear <- add_frame_lab(tsYear, frame.lab = "OCSWITRS Annual Time Series")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. Aggregation by Quarter ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 4.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by quarter
t1 <- data.frame(collap(tsCrashes, ~dateQuarter, custom = fListCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by quarter
t2 <- data.frame(collap(tsParties, ~dateQuarter, custom = fListParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by quarter
t3 <- data.frame(collap(tsVictims, ~dateQuarter, custom = fListVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by quarter
t4 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateQuarter, custom = fListCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by quarter
t5 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateQuarter, custom = fListRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 4.2. Compile Quarter Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsQuarter <- tsMerge(t1, t2, t3, t4, t5, "dateQuarter")

# Remove the rows with missing values
tsQuarter <- tsQuarter[!is.na(tsQuarter$dateQuarter), ]

# for each column in the tsQuarter_collisions data frame, replace the column with a time series object
for (i in 3:ncol(tsQuarter)) {
    tsQuarter[[i]] <- ts(tsQuarter[[i]], frequency = 4, start = c(2013, 1))
}
rm(i, t1, t2, t3, t4, t5)


## 4.3. Add new variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate combined fatal and severe count
tsQuarter$countFatalSevereSum <- tsQuarter$numberKilledSum + tsQuarter$countSevereInjSum
tsQuarter$countFatalSevereMean <- tsQuarter$numberKilledMean + tsQuarter$countSevereInjMean
tsQuarter$countFatalSevereSd <- tsQuarter$numberKilledSd + tsQuarter$countSevereInjSd

# order the sum_fatal_severe after the sum_number_injured column in the tsQuarter data frame
tsQuarter <- tsQuarter %>% relocate(countFatalSevereSum, .after = countSevereInjSum)
tsQuarter <- tsQuarter %>% relocate(countFatalSevereMean, .after = countSevereInjMean)
tsQuarter <- tsQuarter %>% relocate(countFatalSevereSd, .after = countSevereInjSd)

# generate combined minor and pain count
tsQuarter$countMinorPainSum <- tsQuarter$countVisibleInjSum + tsQuarter$countComplaintPainSum
tsQuarter$countMinorPainMean <- tsQuarter$countVisibleInjMean + tsQuarter$countComplaintPainMean
tsQuarter$countMinorPainSd <- tsQuarter$countVisibleInjSd + tsQuarter$countComplaintPainSd

# order the sum_minor_pain after the countComplaintPainSum column in the tsQuarter data frame
tsQuarter <- tsQuarter %>% relocate(countMinorPainSum, .after = countComplaintPainSum)
tsQuarter <- tsQuarter %>% relocate(countMinorPainMean, .after = countComplaintPainMean)
tsQuarter <- tsQuarter %>% relocate(countMinorPainSd, .after = countComplaintPainSd)


## 4.4. General Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add data frame label
tsQuarter <- add_frame_lab(tsQuarter, frame.lab = "OCSWITRS Quarterly Time Series")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 5. Aggregation by Month ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 5.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by month
t1 <- data.frame(collap(tsCrashes, ~dateMonth, custom = fListCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by month
t2 <- data.frame(collap(tsParties, ~dateMonth, custom = fListParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by month
t3 <- data.frame(collap(tsVictims, ~dateMonth, custom = fListVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by month
t4 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateMonth, custom = fListCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by month
t5 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateMonth, custom = fListRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 5.2. Compile Month Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsMonth <- tsMerge(t1, t2, t3, t4, t5, "dateMonth")

# Remove the rows with missing values
tsMonth <- tsMonth[!is.na(tsMonth$dateMonth), ]

# for each column in the tsMonth_collisions data frame, replace the column with a time series object
for (i in 3:ncol(tsMonth)) {
    tsMonth[[i]] <- ts(tsMonth[[i]], frequency = 12, start = c(2013, 1))
}
rm(i, t1, t2, t3, t4, t5)


## 5.3. Add new variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate combined fatal and severe count
tsMonth$countFatalSevereSum <- tsMonth$numberKilledSum + tsMonth$countSevereInjSum
tsMonth$countFatalSevereMean <- tsMonth$numberKilledMean + tsMonth$countSevereInjMean
tsMonth$countFatalSevereSd <- tsMonth$numberKilledSd + tsMonth$countSevereInjSd

# order the sum_fatal_severe after the sum_number_injured column in the tsMonth data frame
tsMonth <- tsMonth %>% relocate(countFatalSevereSum, .after = countSevereInjSum)
tsMonth <- tsMonth %>% relocate(countFatalSevereMean, .after = countSevereInjMean)
tsMonth <- tsMonth %>% relocate(countFatalSevereSd, .after = countSevereInjSd)

# generate combined minor and pain count
tsMonth$countMinorPainSum <- tsMonth$countVisibleInjSum + tsMonth$countComplaintPainSum
tsMonth$countMinorPainMean <- tsMonth$countVisibleInjMean + tsMonth$countComplaintPainMean
tsMonth$countMinorPainSd <- tsMonth$countVisibleInjSd + tsMonth$countComplaintPainSd

# order the sum_minor_pain after the countComplaintPainSum column in the tsMonth data frame
tsMonth <- tsMonth %>% relocate(countMinorPainSum, .after = countComplaintPainSum)
tsMonth <- tsMonth %>% relocate(countMinorPainMean, .after = countComplaintPainMean)
tsMonth <- tsMonth %>% relocate(countMinorPainSd, .after = countComplaintPainSd)


## 5.4. General Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add data frame label
tsMonth <- add_frame_lab(tsMonth, frame.lab = "OCSWITRS Monthly Time Series")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 6. Aggregation by Week ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 6.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by week
t1 <- data.frame(collap(tsCrashes, ~dateWeek, custom = fListCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by week
t2 <- data.frame(collap(tsParties, ~dateWeek, custom = fListParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by week
t3 <- data.frame(collap(tsVictims, ~dateWeek, custom = fListVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by week
t4 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateWeek, custom = fListCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by week
t5 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateWeek, custom = fListRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 6.2. Compile Week Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsWeek <- tsMerge(t1, t2, t3, t4, t5, "dateWeek")

# Remove the rows with missing values
tsWeek <- tsWeek[!is.na(tsWeek$dateWeek), ]

# for each column in the tsWeek_collisions data frame, replace the column with a time series object
for (i in 3:ncol(tsWeek)) {
    tsWeek[[i]] <- ts(tsWeek[[i]], frequency = 53, start = c(2013, 1))
}
rm(i, t1, t2, t3, t4, t5)


## 6.3. Add new variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate combined fatal and severe count
tsWeek$countFatalSevereSum <- tsWeek$numberKilledSum + tsWeek$countSevereInjSum
tsWeek$countFatalSevereMean <- tsWeek$numberKilledMean + tsWeek$countSevereInjMean
tsWeek$countFatalSevereSd <- tsWeek$numberKilledSd + tsWeek$countSevereInjSd

# order the sum_fatal_severe after the sum_number_injured column in the tsWeek data frame
tsWeek <- tsWeek %>% relocate(countFatalSevereSum, .after = countSevereInjSum)
tsWeek <- tsWeek %>% relocate(countFatalSevereMean, .after = countSevereInjMean)
tsWeek <- tsWeek %>% relocate(countFatalSevereSd, .after = countSevereInjSd)

# generate combined minor and pain count
tsWeek$countMinorPainSum <- tsWeek$countVisibleInjSum + tsWeek$countComplaintPainSum
tsWeek$countMinorPainMean <- tsWeek$countVisibleInjMean + tsWeek$countComplaintPainMean
tsWeek$countMinorPainSd <- tsWeek$countVisibleInjSd + tsWeek$countComplaintPainSd

# order the sum_minor_pain after the countComplaintPainSum column in the tsWeek data frame
tsWeek <- tsWeek %>% relocate(countMinorPainSum, .after = countComplaintPainSum)
tsWeek <- tsWeek %>% relocate(countMinorPainMean, .after = countComplaintPainMean)
tsWeek <- tsWeek %>% relocate(countMinorPainSd, .after = countComplaintPainSd)


## 6.4. General Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add data frame label
tsWeek <- add_frame_lab(tsWeek, frame.lab = "OCSWITRS Weekly Time Series")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 7. Aggregation by Day ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 7.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by day
t1 <- data.frame(collap(tsCrashes, ~dateDay, custom = fListCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by day
t2 <- data.frame(collap(tsParties, ~dateDay, custom = fListParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by day
t3 <- data.frame(collap(tsVictims, ~dateDay, custom = fListVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by day
t4 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateDay, custom = fListCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by day
t5 <- data.frame(collap(tsCollisions[tsCollisions$crashTag == 1, ], ~dateDay, custom = fListRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 7.2. Compile Day Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsDay <- tsMerge(t1, t2, t3, t4, t5, "dateDay")

# Remove the rows with missing values
tsDay <- tsDay[!is.na(tsDay$dateDay), ]

# for each column in the tsDay_collisions data frame, replace the column with a time series object
for (i in 3:ncol(tsDay)) {
    tsDay[[i]] <- ts(tsDay[[i]], frequency = 365, start = c(2013, 1))
}
rm(i, t1, t2, t3, t4, t5)


## 7.3. Add new variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate combined fatal and severe count
tsDay$countFatalSevereSum <- tsDay$numberKilledSum + tsDay$countSevereInjSum
tsDay$countFatalSevereMean <- tsDay$numberKilledMean + tsDay$countSevereInjMean
tsDay$countFatalSevereSd <- tsDay$numberKilledSd + tsDay$countSevereInjSd

# order the sum_fatal_severe after the sum_number_injured column in the tsDay data frame
tsDay <- tsDay %>% relocate(countFatalSevereSum, .after = countSevereInjSum)
tsDay <- tsDay %>% relocate(countFatalSevereMean, .after = countSevereInjMean)
tsDay <- tsDay %>% relocate(countFatalSevereSd, .after = countSevereInjSd)

# generate combined minor and pain count
tsDay$countMinorPainSum <- tsDay$countVisibleInjSum + tsDay$countComplaintPainSum
tsDay$countMinorPainMean <- tsDay$countVisibleInjMean + tsDay$countComplaintPainMean
tsDay$countMinorPainSd <- tsDay$countVisibleInjSd + tsDay$countComplaintPainSd

# order the sum_minor_pain after the countComplaintPainSum column in the tsDay data frame
tsDay <- tsDay %>% relocate(countMinorPainSum, .after = countComplaintPainSum)
tsDay <- tsDay %>% relocate(countMinorPainMean, .after = countComplaintPainMean)
tsDay <- tsDay %>% relocate(countMinorPainSd, .after = countComplaintPainSd)


## 7.4. General Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add data frame label
tsDay <- add_frame_lab(tsDay, frame.lab = "OCSWITRS Daily Time Series")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 8. Remove Temp time series data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Remove the temporary data frame
rm(tsCollisions, tsCrashes, tsParties, tsVictims)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 9. Sort the Time Series Data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Sort the tsYear data frame by the dateYear column
tsYear <- tsYear[order(tsYear$dateYear), ]
rownames(tsYear) <- seq_len(nrow(tsYear))

# Sort the tsQuarter data frame by the dateQuarter column
tsQuarter <- tsQuarter[order(tsQuarter$dateQuarter), ]
rownames(tsQuarter) <- seq_len(nrow(tsQuarter))

# Sort the tsMonth data frame by the dateMonth column
tsMonth <- tsMonth[order(tsMonth$dateMonth), ]
rownames(tsMonth) <- seq_len(nrow(tsMonth))

# Sort the tsWeek data frame by the dateWeek column
tsWeek <- tsWeek[order(tsWeek$dateWeek), ]
rownames(tsWeek) <- seq_len(nrow(tsWeek))

# Sort the tsDay data frame by the coll_date column
tsDay <- tsDay[order(tsDay$dateDay), ]
rownames(tsDay) <- seq_len(nrow(tsDay))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 10. Add Time Series Attributes ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add attributes to the time series data frames using the addTsAttributes function
tsYear <- addTsAttributes(tsYear, cb)
tsQuarter <- addTsAttributes(tsQuarter, cb)
tsMonth <- addTsAttributes(tsMonth, cb)
tsWeek <- addTsAttributes(tsWeek, cb)
tsDay <- addTsAttributes(tsDay, cb)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11. Save Time Series Data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the working directory to the root project directory
setwd(prjDirs$prjPath)

# Save the data
saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
