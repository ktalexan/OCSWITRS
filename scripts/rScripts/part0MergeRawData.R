
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data Processing #
# PART 0: MERGING RAW DATA ####
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 1.1. Environmental Setup ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Empty the R environment before running the code
rm(list = ls())

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
pacman::p_load(lubridate, jsonlite, dplyr, magrittr, R6, haven, labelr, plyr, stringr, purrr, glue, Hmisc, psych, tibble, here, tidyr, chattr, knitr, labelled, collapse, formattable)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Definitions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the initial working directory to the R data directory
prjDir <- getwd()


## 2.1. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the project functions from the RData file located in the /Data/R directory
load(file = file.path(prjDir, "scripts", "rData", "projectFunctions.RData"))


## 2.2. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- projectMetadata(part = 1)

# Get the project directories
prjDirs <- projectDirectories()

# if needed, open the library master file
#system(paste("code --", glue("\"{prjDirs$master_lib_path}\"")))


## 2.3. Set the working directory ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the working directory to the data directory
setwd(prjDirs$rawDataPath)
getwd()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Import Raw Data (initialization) ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 3.1. Import Raw Data from Disk ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a summary data frame to store the data dictionary
dataDict <- data.frame(matrix(ncol = 6, nrow = 0))
colnames(dataDict) <- c("year", "dateStart", "dateEnd", "countCrashes", "countParties", "countVictims")

i <- 1
for (year in metadata$projectYears) {
    dataDict[i, "year"] <- year
    for (set in c("Crashes", "Parties", "Victims")) {
        # import the data from disk
        data <- read.csv(glue("{set}_{year}.csv"), header = TRUE, sep = ",")
        if (set == "Crashes") {
            dateStart <- min(as.Date(data$COLLISION_DATE, format = "%Y-%m-%d"))
            dataDict[i, "dateStart"] <- dateStart
            dateEnd <- max(as.Date(data$COLLISION_DATE, format = "%Y-%m-%d"))
            dataDict[i, "dateEnd"] <- dateEnd
            countCrashes <- nrow(data)
            dataDict[i, "countCrashes"] <- countCrashes
        } else if (set == "Parties") {
            countParties <- nrow(data)
            dataDict[i, "countParties"] <- countParties
        } else if (set == "Victims") {
            countVictims <- nrow(data)
            dataDict[i, "countVictims"] <- countVictims
        }
    }
    i <- i + 1
    rm(data, dateStart, dateEnd, countCrashes, countParties, countVictims)
}
rm(i, year, set)


## 3.2. Merge Raw Data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Merge the crashes raw data files
crashes <- data.frame()
for (year in metadata$projectYears) {
    data <- read.csv(glue("Crashes_{year}.csv"), header = TRUE, sep = ",")
    crashes <- rbind(crashes, data)
}

# Merge the parties raw data files
parties <- data.frame()
for (year in metadata$projectYears) {
    data <- read.csv(glue("Parties_{year}.csv"), header = TRUE, sep = ",")
    parties <- rbind(parties, data)
}

# Merge the victims raw data files
victims <- data.frame()
for (year in metadata$projectYears) {
    data <- read.csv(glue("Victims_{year}.csv"), header = TRUE, sep = ",")
    victims <- rbind(victims, data)
}

## 3.3. Save the Merged Data ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Change the working directly to the R data directory
setwd(prjDirs$rDataPath)
getwd()

# Save the merged data to disk
save(crashes, file = "crashes.RData")
save(parties, file = "parties.RData")
save(victims, file = "victims.RData")

# Save the data dictionary to disk
save(dataDict, file = "dataDict.RData")

# Set the working directory back to the project directory
setwd(prjDirs$prjPath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
