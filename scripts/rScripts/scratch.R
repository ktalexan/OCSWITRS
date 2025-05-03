
# Define the list of libraries to be loaded
liblist <- c("RColorBrewer","lubridate", "jsonlite", "dplyr", "magrittr", "R6", "haven", "labelr", "plyr", "stringr", "purrr", "glue", "Hmisc", "psych", "tibble", "here", "tidyr", "chattr", "knitr", "labelled", "collapse", "formattable", "sf", "sp", "arcgisbinding", "ggthemes", "arcgisutils")

# Load the libraries
sapply(liblist, require, character.only = TRUE)


# Set the initial working directory to the R data directory
setwd(file.path(Sys.getenv("OneDriveCommercial"), "Documents", "OCSWITRS", "Data", "R"))


## 2.1. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the project functions from the RData file
load(file = "project_functions.RData")


## 2.2. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- project_metadata(part = 1)

# Get the project directories
prj_dirs <- project_directories()

# if needed, open the library master file
#system(paste("code --", glue("\"{prj_dirs$master_lib_path}\"")))


## 2.3. Set the working directory ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the working directory to the data directory
setwd(prj_dirs$raw_data_path)
getwd()


crashes1<- read.csv("Crashes_2012-01-01_2012-12-31.csv", header = TRUE, sep = ",")
crashes2 <- read.csv(glue("Crashes_{metadata$start_date}_{metadata$end_date}.csv"), header = TRUE, sep = ",")
crashes <- rbind(crashes1, crashes2)

parties1 <- read.csv("Parties_2012-01-01_2012-12-31.csv", header = TRUE, sep = ",")
parties2 <- read.csv(glue("Parties_{metadata$start_date}_{metadata$end_date}.csv"), header = TRUE, sep = ",")
parties <- rbind(parties1, parties2)

victims1 <- read.csv("Victims_2012-01-01_2012-12-31.csv", header = TRUE, sep = ",")
victims2 <- read.csv(glue("Victims_{metadata$start_date}_{metadata$end_date}.csv"), header = TRUE, sep = ",")
victims <- rbind(victims1, victims2)

# count the rows in the crashes1 data frame
nrow(crashes1) + nrow(crashes2) == nrow(crashes)
nrow(parties1) + nrow(parties2) == nrow(parties)

# find the columns in parties2 that are not in parties1
setdiff(colnames(parties2), colnames(parties1))

parties1$VEHICLE_VIN <- NA
parties1$VehicleAutomationEngagedCode <- NA
parties1$VehicleAutomationLevelCode <- NA
parties1$BikewayFacilityCode <- NA
parties1$Lane <- NA
parties1$ThruLanes <- NA
parties1$TotalLanes <- NA
parties1$SpeedLimit <- NA



# Export the crashes data frame to csv
write.csv(crashes, "Crashes_2012-01-01_2024-09-30.csv", row.names = FALSE)
write.csv(parties, "Parties_2012-01-01_2024-09-30.csv", row.names = FALSE)
write.csv(victims, "Victims_2012-01-01_2024-09-30.csv", row.names = FALSE)
