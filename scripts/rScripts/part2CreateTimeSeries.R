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
#libmaster = file.path(Sys.getenv("HOME"), "Knowledge Management", "Documents", "Data Science", "RPackagesInstallation.R")
#file.edit(libmaster)


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

# Load the project functions from the RData file
load(file = "projectFunctions.RData")


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
load(file = "cb.RData")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Aggregation Variable list ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 2.1. Lists by Statistic ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# List of sum columns
fsumlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fSum == 1)]
names(fsumlist) <- paste0(fsumlist, "Sum")

# List of min columns
fminlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMin == 1)]
names(fminlist) <- paste0(fminlist, "Min")

# List of max columns
fmaxlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMax == 1)]
names(fmaxlist) <- paste0(fmaxlist, "Max")

# List of mean columns
fmeanlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMean == 1)]
names(fmeanlist) <- paste0(fmeanlist, "Mean")

# List of standard deviation columns
fsdlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fSd == 1)]
names(fsdlist) <- paste0(fsdlist, "Sd")

# List of median columns
fmedianlist <- names(collisions)[sapply(collisions, function(x) attributes(x)$tsAggr$fMedian == 1)]
names(fmedianlist) <- paste0(fmedianlist, "Median")


## 2.2. Collisions Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the collisions aggregates
flistCollisions = list(
    fsum = fsumlist,
    fmin = fminlist,
    fmax = fmaxlist,
    fmean = fmeanlist,
    fsd = fsdlist,
    fmedian = fmedianlist
)


## 2.3. Crashes Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the crashes aggregates
flistCrashes <- list()
if (length(fsumlist[fsumlist %in% names(crashes)]) > 0) {
    flistCrashes$fsum <- fsumlist[fsumlist %in% names(crashes)]
}
if (length(fminlist[fminlist %in% names(crashes)]) > 0) {
    flistCrashes$fmin <- fminlist[fminlist %in% names(crashes)]
}
if (length(fmaxlist[fmaxlist %in% names(crashes)]) > 0) {
    flistCrashes$fmax <- fmaxlist[fmaxlist %in% names(crashes)]
}
if (length(fmeanlist[fmeanlist %in% names(crashes)]) > 0) {
    flistCrashes$fmean <- fmeanlist[fmeanlist %in% names(crashes)]
}
if (length(fsdlist[fsdlist %in% names(crashes)]) > 0) {
    flistCrashes$fsd <- fsdlist[fsdlist %in% names(crashes)]
}
if (length(fmedianlist[fmedianlist %in% names(crashes)]) > 0) {
    flistCrashes$fmedian <- fmedianlist[fmedianlist %in% names(crashes)]
}


## 2.4. Parties Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the parties aggregates
flistParties <- list()
if (length(fsumlist[fsumlist %in% names(parties)]) > 0) {
    flistParties$fsum <- fsumlist[fsumlist %in% names(parties)]
}
if (length(fminlist[fminlist %in% names(parties)]) > 0) {
    flistParties$fmin <- fminlist[fminlist %in% names(parties)]
}
if (length(fmaxlist[fmaxlist %in% names(parties)]) > 0) {
    flistParties$fmax <- fmaxlist[fmaxlist %in% names(parties)]
}
if (length(fmeanlist[fmeanlist %in% names(parties)]) > 0) {
    flistParties$fmean <- fmeanlist[fmeanlist %in% names(parties)]
}
if (length(fsdlist[fsdlist %in% names(parties)]) > 0) {
    flistParties$fsd <- fsdlist[fsdlist %in% names(parties)]
}
if (length(fmedianlist[fmedianlist %in% names(parties)]) > 0) {
    flistParties$fmedian <- fmedianlist[fmedianlist %in% names(parties)]
}


## 2.5. Victims Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the victims aggregates
flistVictims <- list()
if (length(fsumlist[fsumlist %in% names(victims)]) > 0) {
    flistVictims$fsum <- fsumlist[fsumlist %in% names(victims)]
}
if (length(fminlist[fminlist %in% names(victims)]) > 0) {
    flistVictims$fmin <- fminlist[fminlist %in% names(victims)]
}
if (length(fmaxlist[fmaxlist %in% names(victims)]) > 0) {
    flistVictims$fmax <- fmaxlist[fmaxlist %in% names(victims)]
}
if (length(fmeanlist[fmeanlist %in% names(victims)]) > 0) {
    flistVictims$fmean <- fmeanlist[fmeanlist %in% names(victims)]
}
if (length(fsdlist[fsdlist %in% names(victims)]) > 0) {
    flistVictims$fsd <- fsdlist[fsdlist %in% names(victims)]
}
if (length(fmedianlist[fmedianlist %in% names(victims)]) > 0) {
    flistVictims$fmedian <- fmedianlist[fmedianlist %in% names(victims)]
}


## 2.6. Cities Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine the lists into a single list for the cities aggregates
flistCities <- list()
if (length(fsumlist[fsumlist %in% names(cities)]) > 0) {
    flistCities$fsum <- fsumlist[fsumlist %in% names(cities)]
}
if (length(fminlist[fminlist %in% names(cities)]) > 0) {
    flistCities$fmin <- fminlist[fminlist %in% names(cities)]
}
if (length(fmaxlist[fmaxlist %in% names(cities)]) > 0) {
    flistCities$fmax <- fmaxlist[fmaxlist %in% names(cities)]
}
if (length(fmeanlist[fmeanlist %in% names(cities)]) > 0) {
    flistCities$fmean <- fmeanlist[fmeanlist %in% names(cities)]
}
if (length(fsdlist[fsdlist %in% names(cities)]) > 0) {
    flistCities$fsd <- fsdlist[fsdlist %in% names(cities)]
}
if (length(fmedianlist[fmedianlist %in% names(cities)]) > 0) {
    flistCities$fmedian <- fmedianlist[fmedianlist %in% names(cities)]
}


## 2.7. Roads Aggregation List ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# # Combine the lists into a single list for the roads aggregates
flistRoads <- list()
if (length(fsumlist[fsumlist %in% names(roads)]) > 0) {
    flistRoads$fsum <- fsumlist[fsumlist %in% names(roads)]
}
if (length(fminlist[fminlist %in% names(roads)]) > 0) {
    flistRoads$fmin <- fminlist[fminlist %in% names(roads)]
}
if (length(fmaxlist[fmaxlist %in% names(roads)]) > 0) {
    flistRoads$fmax <- fmaxlist[fmaxlist %in% names(roads)]
}
if (length(fmeanlist[fmeanlist %in% names(roads)]) > 0) {
    flistRoads$fmean <- fmeanlist[fmeanlist %in% names(roads)]
}
if (length(fsdlist[fsdlist %in% names(roads)]) > 0) {
    flistRoads$fsd <- fsdlist[fsdlist %in% names(roads)]
}
if (length(fmedianlist[fmedianlist %in% names(roads)]) > 0) {
    flistRoads$fmedian <- fmedianlist[fmedianlist %in% names(roads)]
}


## 2.8. Cleaning Aggregation Lists ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Delete the PartyNumberMax element from the flistVictims$fmax list
flistVictims$fmax <- flistVictims$fmax[!names(flistVictims$fmax) %in% "partyNumberMax"]

# Delete the PartyNumberMean element from the flistVictims$fmean list
flistVictims$fmean <- flistVictims$fmean[!names(flistVictims$fmean) %in% "partyNumberMean"]

# Delete the PartyNumberSd element from the flistVictims$fsd list
flistVictims$fsd <- flistVictims$fsd[!names(flistVictims$fsd) %in% "partyNumberSd"]

# Remove the individual stats lists
rm(fsumlist, fminlist, fmaxlist, fmeanlist, fsdlist, fmedianlist)


## 2.9. Prepare Aggregation Temp Dataset ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a temporary data frame for the time series aggregation
tscollisions <- collisions
tscollisions$dateYear <- as.Date(tscollisions$dateYear)
tscollisions$dateQuarter <- as.Date(tscollisions$dateQuarter)
tscollisions$dateMonth <- as.Date(tscollisions$dateMonth)
tscollisions$dateWeek <- as.Date(tscollisions$dateWeek)
tscollisions$dateDay <- as.Date(tscollisions$dateDay)

tscrashes <- crashes
tscrashes$dateYear <- as.Date(tscrashes$dateYear)
tscrashes$dateQuarter <- as.Date(tscrashes$dateQuarter)
tscrashes$dateMonth <- as.Date(tscrashes$dateMonth)
tscrashes$dateWeek <- as.Date(tscrashes$dateWeek)
tscrashes$dateDay <- as.Date(tscrashes$dateDay)

tsparties <- parties
tsparties$dateYear <- as.Date(tsparties$dateYear)
tsparties$dateQuarter <- as.Date(tsparties$dateQuarter)
tsparties$dateMonth <- as.Date(tsparties$dateMonth)
tsparties$dateWeek <- as.Date(tsparties$dateWeek)
tsparties$dateDay <- as.Date(tsparties$dateDay)

tsvictims <- victims
tsvictims$dateYear <- as.Date(tsvictims$dateYear)
tsvictims$dateQuarter <- as.Date(tsvictims$dateQuarter)
tsvictims$dateMonth <- as.Date(tsvictims$dateMonth)
tsvictims$dateWeek <- as.Date(tsvictims$dateWeek)
tsvictims$dateDay <- as.Date(tsvictims$dateDay)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Aggregation by Year ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tsMerge <- function(t1, t2, t3, t4, t5, byvar) {
    # merge the first two data frames
    merge1 <- merge(t1, t2, by = byvar)
    # if the column name in test includes ".y", delete set the column to NULL
    merge1 <- merge1[, !grepl("[.]y$", colnames(merge1))]
    # if the column name in test includes ".x", remove the ".x" from the column name
    colnames(merge1) <- gsub("[.]x$", "", colnames(merge1))
    
    # merge the third data frame
    merge2 <- merge(merge1, t3, by = byvar)
    merge2 <- merge2[, !grepl("[.]y$", colnames(merge2))]
    colnames(merge2) <- gsub("[.]x$", "", colnames(merge2))
    
    # merge the fourth data frame
    merge3 <- merge(merge2, t4, by = byvar)
    merge3 <- merge3[, !grepl("[.]y$", colnames(merge3))]
    colnames(merge3) <- gsub("[.]x$", "", colnames(merge3))
    
    # merge the fifth data frame
    merge4 <- merge(merge3, t5, by = byvar)
    merge4 <- merge4[, !grepl("[.]y$", colnames(merge4))]
    colnames(merge4) <- gsub("[.]x$", "", colnames(merge4))
    
    return(merge4)
}


## 3.1. Aggregations by data frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Aggregate selected columns of the crashes data frame by year
t1 <- data.frame(collap(tscrashes, ~dateYear, custom = flistCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by year
t2 <- data.frame(collap(tsparties, ~dateYear, custom = flistParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by year
t3 <- data.frame(collap(tsvictims, ~dateYear, custom = flistVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by year
t4 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateYear, custom = flistCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by year
t5 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateYear, custom = flistRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 3.2. Compile Year Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsYear <- tsMerge(t1, t2, t3, t4, t5, "dateYear")

# Remove the rows with missing values
tsYear <- tsYear[!is.na(tsYear$dateYear), ]

# for each column in the tsyear_collisions data frame, replace the column with a time series object
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
t1 <- data.frame(collap(tscrashes, ~dateQuarter, custom = flistCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by quarter
t2 <- data.frame(collap(tsparties, ~dateQuarter, custom = flistParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by quarter
t3 <- data.frame(collap(tsvictims, ~dateQuarter, custom = flistVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by quarter
t4 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateQuarter, custom = flistCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by quarter
t5 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateQuarter, custom = flistRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 4.2. Compile Quarter Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsQuarter <- tsMerge(t1, t2, t3, t4, t5, "dateQuarter")

# Remove the rows with missing values
tsQuarter <- tsQuarter[!is.na(tsQuarter$dateQuarter), ]

# for each column in the tsquarter_collisions data frame, replace the column with a time series object
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
t1 <- data.frame(collap(tscrashes, ~dateMonth, custom = flistCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by month
t2 <- data.frame(collap(tsparties, ~dateMonth, custom = flistParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by month
t3 <- data.frame(collap(tsvictims, ~dateMonth, custom = flistVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by month
t4 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateMonth, custom = flistCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by month
t5 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateMonth, custom = flistRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 5.2. Compile Month Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsMonth <- tsMerge(t1, t2, t3, t4, t5, "dateMonth")

# Remove the rows with missing values
tsMonth <- tsMonth[!is.na(tsMonth$dateMonth), ]

# for each column in the tsmonth_collisions data frame, replace the column with a time series object
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
t1 <- data.frame(collap(tscrashes, ~dateWeek, custom = flistCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by week
t2 <- data.frame(collap(tsparties, ~dateWeek, custom = flistParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by week
t3 <- data.frame(collap(tsvictims, ~dateWeek, custom = flistVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by week
t4 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateWeek, custom = flistCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by week
t5 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateWeek, custom = flistRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 6.2. Compile Week Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsWeek <- tsMerge(t1, t2, t3, t4, t5, "dateWeek")

# Remove the rows with missing values
tsWeek <- tsWeek[!is.na(tsWeek$dateWeek), ]

# for each column in the tsweek_collisions data frame, replace the column with a time series object
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
t1 <- data.frame(collap(tscrashes, ~dateDay, custom = flistCrashes, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the parties data frame by day
t2 <- data.frame(collap(tsparties, ~dateDay, custom = flistParties, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the victims data frame by day
t3 <- data.frame(collap(tsvictims, ~dateDay, custom = flistVictims, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the cities data frame by day
t4 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateDay, custom = flistCities, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))

# Aggregate selected columns of the roads data frame by day
t5 <- data.frame(collap(tscollisions[tscollisions$crashTag == 1,], ~dateDay, custom = flistRoads, keep.col.order = FALSE, give.names = FALSE, keep.by = TRUE))


## 7.2. Compile Day Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Combine and compile all the aggregates to a single time series data frame
tsDay <- tsMerge(t1, t2, t3, t4, t5, "dateDay")

# Remove the rows with missing values
tsDay <- tsDay[!is.na(tsDay$dateDay), ]

# for each column in the tsday_collisions data frame, replace the column with a time series object
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
rm(tscollisions, tscrashes, tsparties, tsvictims)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 9. Sort the Time Series Data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Sort the tsYear data frame by the dateYear column
tsYear <- tsYear[order(tsYear$dateYear), ]
rownames(tsYear) <- 1:nrow(tsYear)

# Sort the tsQuarter data frame by the dateQuarter column
tsQuarter <- tsQuarter[order(tsQuarter$dateQuarter), ]
rownames(tsQuarter) <- 1:nrow(tsQuarter)

# Sort the tsMonth data frame by the dateMonth column
tsMonth <- tsMonth[order(tsMonth$dateMonth), ]
rownames(tsMonth) <- 1:nrow(tsMonth)

# Sort the tsWeek data frame by the dateWeek column
tsWeek <- tsWeek[order(tsWeek$dateWeek), ]
rownames(tsWeek) <- 1:nrow(tsWeek)

# Sort the tsDay data frame by the coll_date column
tsDay <- tsDay[order(tsDay$dateDay), ]
rownames(tsDay) <- 1:nrow(tsDay)


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

# Set the working directory to the data path
setwd(prjDirs$rDataPath)

# Save the data
saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
