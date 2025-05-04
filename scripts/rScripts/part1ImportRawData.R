#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data Processing #
# PART 1: MERGING AND COMBINING DATASETS ####
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
pacman::p_load(RColorBrewer, lubridate, jsonlite, dplyr, magrittr, R6, haven, labelr, plyr, stringr, purrr, glue, Hmisc, psych, tibble, here, tidyr, chattr, knitr, labelled, collapse, formattable, sf, sp, arcgisbinding, ggthemes, arcgisutils)


# Check the licences for the ArcGIS binding
arc.check_product()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Definitions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

getwd()

## 2.1. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the project functions from the RData file located in the /Data/R directory
load(file = file.path(getwd(), "scripts", "rData", "projectFunctions.RData"))


## 2.2. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- projectMetadata(part = 1)

# Get the project directories
prjDirs <- projectDirectories()

# if needed, open the library master file
#system(paste("code --", glue("\"{prjDirs$master_lib_path}\"")))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Import Raw Data (initialization) ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 3.1. Import Raw Data from Disk ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# In the following segment, we import the raw csv data from disk, compile a list of the data frames, rename the NAME column to city (in the cities df), and import the codebook JSON file data.

# The raw data for crashes, parties, and victims are already pre-merged and saved to RData files in the previous script (Part0-MergeRawData.R). We are loading them here, along with the merged data dictionary.

# import the raw data dictionary from disk
load(file = file.path(prjDirs$rDataPath, "dataDict.RData"))

# import crashes raw data from disk
load(file = file.path(prjDirs$rDataPath, "crashes.RData"))

# import parties raw data from disk
load(file = file.path(prjDirs$rDataPath, "parties.RData"))

# import victims raw data from disk
load(file = file.path(prjDirs$rDataPath, "victims.RData"))


# import cities from ArcGIS pro geodatabase
cities.agp <- arc.open(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "cities"))
cities <- arc.data2sf(arc.select(object = cities.agp))
rm(cities.agp)

# Set the cities coordinate system to WGS 1984 Web Mercator (Auxiliary Sphere) (EPSG: 3857)
st_crs(cities) <- 3857
st_crs(cities)$proj4string

# import roads from ArcGIS pro geodatabase
roads.agp <- arc.open(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "roads"))
roads <- arc.data2sf(arc.select(object = roads.agp))
rm(roads.agp)

# Set the roads coordinate system to WGS 1984 Web Mercator (Auxiliary Sphere) (EPSG: 3857)
st_crs(roads) <- 3857
st_crs(roads)$proj4string

# import boundaries from ArcGIS pro geodatabase
boundaries.agp <- arc.open(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "boundaries"))
boundaries <- arc.data2sf(arc.select(object = boundaries.agp))
rm(boundaries.agp)

# Set the boundaries coordinate system to WGS 1984 Web Mercator (Auxiliary Sphere) (EPSG: 3857)
st_crs(boundaries) <- 3857
st_crs(boundaries)$proj4string

# Number of rows
print(glue("Crashes: {nrow(crashes)} cases\nParties: {nrow(parties)} cases\nVictims: {nrow(victims)} cases\nCities: {nrow(cities)} cities\nRoads: {nrow(roads)} road segments"))

# Compile a list of the data frames
dfList <- c("crashes", "parties", "victims", "cities", "roads")

# rename the NAME column to city in the cities data frame
colnames(cities)[colnames(cities) == "NAME"] <- "CITY"

# Reorder the columns in the crashes data frame
crashes <- crashes[, c(
    "CASE_ID", "CITY", "COLLISION_DATE", "COLLISION_TIME", "ACCIDENT_YEAR",
    "DAY_OF_WEEK", "PROC_DATE", "COLLISION_SEVERITY", "PARTY_COUNT",
    "NUMBER_KILLED", "NUMBER_INJURED", "COUNT_SEVERE_INJ", "COUNT_VISIBLE_INJ",
    "COUNT_COMPLAINT_PAIN", "COUNT_PED_KILLED", "COUNT_PED_INJURED",
    "COUNT_BICYCLIST_KILLED", "COUNT_BICYCLIST_INJURED", "COUNT_MC_KILLED",
    "COUNT_MC_INJURED", "PRIMARY_COLL_FACTOR", "TYPE_OF_COLLISION",
    "PEDESTRIAN_ACCIDENT", "BICYCLE_ACCIDENT", "MOTORCYCLE_ACCIDENT",
    "TRUCK_ACCIDENT", "HIT_AND_RUN", "ALCOHOL_INVOLVED", "JURIS",
    "OFFICER_ID", "REPORTING_DISTRICT", "CHP_SHIFT", "CNTY_CITY_LOC",
    "SPECIAL_COND", "BEAT_TYPE", "CHP_BEAT_TYPE", "CHP_BEAT_CLASS",
    "BEAT_NUMBER", "PRIMARY_RD", "SECONDARY_RD", "DISTANCE", "DIRECTION",
    "INTERSECTION", "WEATHER_1", "WEATHER_2", "ROAD_SURFACE", "ROAD_COND_1",
    "ROAD_COND_2", "LIGHTING", "CONTROL_DEVICE", "STATE_HWY_IND",
    "SIDE_OF_HWY", "TOW_AWAY", "PCF_CODE_OF_VIOL", "PCF_VIOL_CATEGORY",
    "PCF_VIOLATION", "PCF_VIOL_SUBSECTION", "MVIW", "PED_ACTION",
    "NOT_PRIVATE_PROPERTY", "STWD_VEHTYPE_AT_FAULT", "CHP_VEHTYPE_AT_FAULT",
    "PRIMARY_RAMP", "SECONDARY_RAMP", "LATITUDE", "LONGITUDE", "POINT_X",
    "POINT_Y", "POPULATION", "CITY_DIVISION_LAPD", "CALTRANS_COUNTY",
    "CALTRANS_DISTRICT", "STATE_ROUTE", "ROUTE_SUFFIX", "POSTMILE_PREFIX",
    "POSTMILE", "LOCATION_TYPE", "RAMP_INTERSECTION", "CHP_ROAD_TYPE",
    "COUNTY"
)]

# Reorder the columns in the parties data frame
parties <- parties[, c(
    "CASE_ID", "PARTY_NUMBER", "ACCIDENT_YEAR", "PARTY_TYPE", "AT_FAULT",
    "PARTY_SEX", "PARTY_AGE", "RACE", "PARTY_NUMBER_KILLED", "PARTY_NUMBER_INJURED",
    "INATTENTION", "PARTY_SOBRIETY", "PARTY_DRUG_PHYSICAL", "DIR_OF_TRAVEL",
    "PARTY_SAFETY_EQUIP_1", "PARTY_SAFETY_EQUIP_2", "FINAN_RESPONS",
    "SP_INFO_1", "SP_INFO_2", "SP_INFO_3", "OAF_VIOLATION_CODE",
    "OAF_VIOL_CAT", "OAF_VIOL_SECTION", "OAF_VIOLATION_SUFFIX", "OAF_1",
    "OAF_2", "MOVE_PRE_ACC", "VEHICLE_YEAR", "VEHICLE_MAKE", "STWD_VEHICLE_TYPE",
    "CHP_VEH_TYPE_TOWING", "CHP_VEH_TYPE_TOWED", "SPECIAL_INFO_F",
    "SPECIAL_INFO_G"
)]

# Reorder the columns in the victims data frame
victims <- victims[, c(
    "CASE_ID", "PARTY_NUMBER", "VICTIM_NUMBER", "ACCIDENT_YEAR",
    "VICTIM_ROLE", "VICTIM_SEX", "VICTIM_AGE", "VICTIM_DEGREE_OF_INJURY",
    "VICTIM_SEATING_POSITION", "VICTIM_SAFETY_EQUIP_1", "VICTIM_SAFETY_EQUIP_2",
    "VICTIM_EJECTED", "COUNTY", "CITY"
)]


## 3.2. Import Codebook ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the codebook cb from the codebook_path
load(file.path(prjDirs$codebookPath, "cb.RData"))

# Convert the codebook into a tibble table for convenience
cbTable <- tibble(
    varOrder = sapply(cb, function(x) x$varOrder),
    varName = sapply(cb, function(x) x$varName),
    rawData = sapply(cb, function(x) x$rawData),
    rawName = sapply(cb, function(x) x$rawName),
    label = sapply(cb, function(x) x$label),
    description = sapply(cb, function(x) x$description),
    varClass = sapply(cb, function(x) x$varClass),
    varType = sapply(cb, function(x) x$varType),
    varCategory = sapply(cb, function(x) x$varCategory),
    hasSource = sapply(cb, function(x) x$hasSource),
    recodeOriginal = sapply(cb, function(x) x$recodeOriginal),
    isLabeled = sapply(cb, function(x) x$isLabeled),
    labels = sapply(cb, function(x) x$labels),
    inCrashes = sapply(cb, function(x) x$inCrashes),
    inParties = sapply(cb, function(x) x$inParties),
    inVictims = sapply(cb, function(x) x$inVictims),
    inCollisions = sapply(cb, function(x) x$inCollisions),
    inCities = sapply(cb, function(x) x$inCities),
    inRoads = sapply(cb, function(x) x$inRoads),
    tsAggr = sapply(cb, function(x) x$tsAggr),
    toKeep = sapply(cb, function(x) x$toKeep),
    varNotes = sapply(cb, function(x) x$varNotes)
)

# View the reference table
#View(cbTable)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. Raw Data Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 4.1. Process variable names and columns ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# for each of the data frames below, process their data by:
# 1. Creating a list of names for the crashes dataframe (contains newname as name and oldname as value)
# 2. Renaming the columns in the crashes data frame using the newnames from the list
# 3. Removing all the deprecated and unused columns from the crashes data frame


### Crashes Data Frame ####

# Select the names of the columns that are present in the raw data and have crashes and rename the crashes data frame columns with their new names
for (newName in names(cbTable$varName[cbTable$rawData == 1 & cbTable$inCrashes == 1])) {
    oldName <- cbTable$rawName[cbTable$varName == newName]
    if (oldName %in% names(crashes)) {
        colnames(crashes)[colnames(crashes) == oldName] <- newName
    }
}

# Remove all the deprecated and unused columns from the crashes data frame
crashes <- subset(crashes, select = names(crashes) %in% names(cbTable$varName[cbTable$rawData == 1 & cbTable$inCrashes == 1]))

# Remove temp variables
rm(newName, oldName)


### Parties Data Frame ####

# Select the names of the columns that are present in the raw data and have crashes and rename the crashes data frame columns with their new names
for (newName in names(cbTable$varName[cbTable$rawData == 1 & cbTable$inParties == 1])) {
    oldName <- cbTable$rawName[cbTable$varName == newName]
    if (oldName %in% names(parties)) {
        colnames(parties)[colnames(parties) == oldName] <- newName
    }
}

# Remove all the deprecated and unused columns from the crashes data frame
parties <- subset(parties, select = names(parties) %in% names(cbTable$varName[cbTable$rawData == 1 & cbTable$inParties == 1]))

# Remove temp variables
rm(newName, oldName)


### Victims Data Frame ####

# Select the names of the columns that are present in the raw data and have crashes and rename the crashes data frame columns with their new names
for (newName in names(cbTable$varName[cbTable$rawData == 1 & cbTable$inVictims == 1])) {
    oldName <- cbTable$rawName[cbTable$varName == newName]
    if (oldName %in% names(victims)) {
        colnames(victims)[colnames(victims) == oldName] <- newName
    }
}

# Remove all the deprecated and unused columns from the crashes data frame
victims <- subset(victims, select = names(victims) %in% names(cbTable$varName[cbTable$rawData == 1 & cbTable$inVictims == 1]))

# Remove temp variables
rm(newName, oldName)


### Cities Data Frame ####

# Select the names of the columns that are present in the raw data and have crashes and rename the crashes data frame columns with their new names
for (newName in names(cbTable$varName[cbTable$rawData == 1 & cbTable$inCities == 1])) {
    oldName <- cbTable$rawName[cbTable$varName == newName]
    if (oldName %in% names(cities)) {
        colnames(cities)[colnames(cities) == oldName] <- newName
    }
}

# Remove all the deprecated and unused columns from the crashes data frame
cities <- subset(cities, select = names(cities) %in% names(cbTable$varName[cbTable$rawData == 1 & cbTable$inCities == 1]))

# Remove temp variables
rm(newName, oldName)


### Roads Data Frame ####

# Select the names of the columns that are present in the raw data and have crashes and rename the crashes data frame columns with their new names
for (newName in names(cbTable$varName[cbTable$rawData == 1 & cbTable$inRoads == 1])) {
    oldName <- cbTable$rawName[cbTable$varName == newName]
    if (oldName %in% names(roads)) {
        colnames(roads)[colnames(roads) == oldName] <- newName
    }
}

# Remove all the deprecated and unused columns from the crashes data frame
roads <- subset(roads, select = names(roads) %in% names(cbTable$varName[cbTable$rawData == 1 & cbTable$inRoads == 1]))

# Remove temp variables
rm(newName, oldName)


## 4.2. Remove Leading and Trailing Whitespace ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Remove leading and trailing whitespace from the columns of the datasets
for (df in c("crashes", "parties", "victims")) {
    print(glue("Removing leading and trailing whitespace from the {df} dataset"))
    assign(df, get(df) %>% mutate_all(str_squish))
}
rm(df)


## 4.3. Add Frame Labels ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# For each of the datasets below, add a frame label to the dataset
#crashes <- add_frame_lab(crashes, frame.lab = "OCSWITRS Crashes Dataset")
#parties <- add_frame_lab(parties, frame.lab = "OCSWITRS Parties Dataset")
#victims <- add_frame_lab(victims, frame.lab = "OCSWITRS Victims Dataset")
#cities <- add_frame_lab(cities, frame.lab = "OCSWITRS Cities Dataset")
#roads <- add_frame_lab(roads, frame.lab = "OCSWITRS Roads Dataset")


## 4.4. Add CID, PID, and VID Columns ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add the CID, PID, and VID columns to the datasets (crashes, parties, and victims)


### Add CID Columns ####

# Generate CID column for all the datasets by converting the CaseId column to a character
crashes$cid <- as.character(crashes$caseId)
parties$cid <- as.character(parties$caseId)
victims$cid <- as.character(victims$caseId)

# order the CID columns after the CaseId columns
crashes <- crashes %>% relocate(cid, .after = caseId)
parties <- parties %>% relocate(cid, .after = caseId)
victims <- victims %>% relocate(cid, .after = caseId)


### Add PID Columns ####

# Generate CID column for the datasets by converting the CaseId column to a character
parties$pid <- paste(as.character(parties$caseId), as.character(parties$partyNumber), sep = "-")
victims$pid <- paste(as.character(victims$caseId), as.character(victims$partyNumber), sep = "-")

# order the PID columns after the cid columns
parties <- parties %>% relocate(pid, .after = cid)
victims <- victims %>% relocate(pid, .after = cid)


### Add VID Columns ####

# Generate CID column for the datasets by converting the CaseId column to a character
victims$vid <- paste(as.character(victims$caseId), as.character(victims$partyNumber), as.character(victims$victimNumber), sep = "-")

# order the VID columns after the pid columns
victims <- victims %>% relocate(vid, .after = pid)


## 4.5. Add TotalCrashes, TotalParties, TotalVictims Columns ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add the TotalCrashes, TotalParties and TotalVictims columns to the crashes, parties and victims data frames as appropriately.

# Add count of crashes per cid in the crashes data frame
crashes <- crashes %>% add_count(cid, name = "crashesCidCount")
crashes <- crashes %>% relocate(crashesCidCount, .after = cid)

# Add count of parties per cid and pid in the parties data frame
parties <- parties %>% add_count(cid, name = "partiesCidCount")
parties <- parties %>% add_count(pid, name = "partiesPidCount")
parties <- parties %>% relocate(partiesCidCount, .after = pid)
parties <- parties %>% relocate(partiesPidCount, .after = partiesCidCount)

# Add count of victims per cid, pid and vid in the victims data frame
victims <- victims %>% add_count(cid, name = "victimsCidCount")
victims <- victims %>% add_count(pid, name = "victimsPidCount")
victims <- victims %>% add_count(vid, name = "victimsVidCount")
victims <- victims %>% relocate(victimsCidCount, .after = vid)
victims <- victims %>% relocate(victimsPidCount, .after = victimsCidCount)
victims <- victims %>% relocate(victimsVidCount, .after = victimsPidCount)


## 4.6. Additional Column Processing ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### City Names Title Case ####

# Convert the city names to title case on the crashes dataset
crashes$city <- str_to_title(crashes$city)

# Same with the roads
roads$placeName <- str_to_title(roads$placeName)


### Convert all counts into numeric ####

# Convert all the count columns to integers
for (i in c("caseId", "partyCount", "numberKilled", "numberInj", "countSevereInj", "countVisibleInj", "countComplaintPain", "countPedKilled", "countPedInj", "countBicKilled", "countBicInj", "countMcKilled", "countMcInj")) {
    if (i %in% names(crashes)) {
        crashes[[glue(i)]] <- as.integer(crashes[[glue(i)]])
    }
}

# Convert the distance, longitude, latitude, pointX, and pointY columns to double
for (i in c("distance", "longitude", "latitude", "pointX", "pointY")) {
    if (i %in% names(crashes)) {
        crashes[[glue(i)]] <- as.double(crashes[[glue(i)]])
    }
}

# Convert the partyAge, partyNumberKilled, partyNumberInj, victimAge, victimNumberKilled, and victimNumberInj columns to integers
for (i in c("caseId", "partyNumber", "partyAge", "partyNumberKilled", "partyNumberInj", "victimNumber", "victimAge", "victimNumberKilled", "victimNumberInj", "vehicleYear")) {
    if (i %in% names(parties)) {
        parties[[glue(i)]] <- as.integer(parties[[glue(i)]])
    }
    if (i %in% names(victims)) {
        victims[[glue(i)]] <- as.integer(victims[[glue(i)]])
    }
}

# Convert the area, population and housing density columns to double
for (i in c("cityAreaSqmi", "cityPopDens", "cityHouDens")) {
    if (i %in% names(cities)) {
        cities[[glue(i)]] <- as.double(cities[[glue(i)]])
    }
}

# Convert the population, housingUnits, cityPopAsian, cityPopBlack, cityPopHispanic, cityPopWhite, cityVehicles, and cityTravelTime columns to integers
for (i in c("cityPopTotal", "cityHouTotal", "cityPopAsian", "cityPopBlack", "cityPopHispanic", "cityPopWhite", "cityVehicles", "cityTravelTime")) {
    if (i %in% names(cities)) {
        cities[[glue(i)]] <- as.integer(cities[[glue(i)]])
    }
}

# Convert the roadLength column to double
if ("roadLength" %in% names(roads)) {
    roads$roadLength <- as.double(roads$roadLength)
}

rm(i)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 5. Data Processing ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 5.1. Tagging Datasets ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# For each of the crashes, parties, and victims data frames, add a tag column to the data frame to indicate if the observation belongs to this dataset.


### Crashes Tag ####
#crashes <- crashes %>% add_count(cid, name = "crashes_case_tag")

# Create count of crashes per cid in the crashes data frame
crashes <- crashes %>% group_by(cid) %>% dplyr::mutate(crashesCaseTag = n())

# Order the crashes_case_tag column after the caseId column
crashes <- crashes %>% relocate(crashesCaseTag, .after = caseId)


### Parties Tag ####
#parties <- parties %>% add_ount(cid, name = "partiesCaseTag")

# Create count of parties per cid in the parties data frame
parties <- parties %>% group_by(cid) %>% dplyr::mutate(partiesCaseTag = n())

# Order the parties_case_tag column after the partyNumber column
parties <- parties %>% relocate(partiesCaseTag, .after = partyNumber)


### Victims Tag ####

# Create count of victims per cid in the victims data frame
victims <- victims %>% group_by(cid) %>% dplyr::mutate(victimsCaseTag = n())

# Order the victims_case_tag column after the victim_number column
victims <- victims %>% relocate(victimsCaseTag, .after = victimNumber)


## 5.2. Add Dataset Identifiers ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add the dataset identifiers to the crashes, parties, and victims data frames


### Crashes Identifiers ####

# Add unique tag
crashes$crashTag <- 1

# Order the tag
crashes <- crashes %>% relocate(crashTag, .after = cid)


### Parties Identifiers ####

# Add unique tag
parties$partyTag <- 1

# Order the tag
parties <- parties %>% relocate(partyTag, .after = pid)


### Victims Identifiers ####

# Add unique tag
victims$victimTag <- 1

# Order the tag
victims <- victims %>% relocate(victimTag, .after = vid)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 6. Date and Time Data Frame Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 6.1. Convert Data Types ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Convert the accident year to integer, if it is not already
if (class(crashes$accidentYear) != "integer") {
    crashes$accidentYear <- as.integer(crashes$accidentYear)
}


## 6.2. Collision and Process Date Conversion ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# convert the processDate into date by using the first 4 digits as year, the next 2 as month, and the last 2 as day (in place)
crashes$dateProcess <- as.POSIXlt(crashes$processDate, format = "%Y-%m-%d", tz = "America/Los_Angeles")

# Convert the collision time to integer, if it is not already
if (class(crashes$collTime) != "integer") {
    crashes$collTime <- as.integer(crashes$collTime)
}

# Define function to convert the collTime to a formatted time string
formatCollTime <- function(x) {
    if (nchar(x) == 1) {
        paste0("00:0", x, ":00")
    } else if (nchar(x) == 2) {
        paste0("00:", x, ":00")
    } else if (nchar(x) == 3) {
        paste0("0", substr(x, 1, 1), ":", substr(x, 2, 3), ":00")
    } else if (nchar(x) == 4 & x < 2400) {
        paste0(substr(x, 1, 2), ":", substr(x, 3, 4), ":00")
    } else {
        "00:00:00"
    }
}

# create temporary column to store the formatted time
crashes$collTimeTemp <- lapply(crashes$collTime, formatCollTime)

# Convert the collDate and collTime columns to a datetime object
crashes$dateDatetime <- as.POSIXlt(paste(crashes$collDate, crashes$collTimeTemp), format = "%Y-%m-%d %H:%M", tz = "America/Los_Angeles")

# Remove the temporary column
crashes$collTimeTemp <- NULL


## 6.3. Create Date and Time Individual Columns ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Year (Date) ####

# Create a year date column
crashes$dateYear <- floor_date(crashes$dateDatetime, unit = "year")

# Create a year column
crashes$dtYear <- as.integer(crashes$dateDatetime$year + 1900)


### Quarter (Date) ####

# Create a quarter date
crashes$dateQuarter <- floor_date(crashes$dateDatetime, unit = "quarter")

# Create a quarter column
crashes$dtQuarter <- as.integer(quarter(crashes$dateDatetime, type = "quarter"))

# label the quarter column
val_labels(crashes$dtQuarter) <- cb$dtQuarter$labels[cb$dtQuarter$labels %in% unique(crashes$dtQuarter)]


### Month (Date) ####

# Create a month date
crashes$dateMonth <- floor_date(crashes$dateDatetime, unit = "month")

# Create a month column (numbers)
crashes$dtMonth <- as.integer(crashes$dateDatetime$mon + 1)

# Label the month column
val_labels(crashes$dtMonth) <- cb$dtMonth$labels[cb$dtMonth$labels %in% unique(crashes$dtMonth)]


### Week of the Year (Date) ####

# Create a week date
crashes$dateWeek <- floor_date(crashes$dateDatetime, unit = "week")

# Create a week of the year column
crashes$dtYearWeek <- as.integer(crashes$dateDatetime$yday %/% 7 + 1)

### Day (Date) ####

# Create a day date
crashes$dateDay <- floor_date(crashes$dateDatetime, unit = "day")

### Week Day (Date) ####

# Create a week column (names)
crashes$dtWeekDay <- as.integer(crashes$dateDatetime$wday + 1)

# Label the week column
val_labels(crashes$dtWeekDay) <- cb$dtWeekDay$labels


### Day of the Month (Date) ####

# Create a day of the month column
crashes$dtMonthDay <- as.integer(crashes$dateDatetime$mday)


### Day of the Year (Date) ####

# Create a day of the year column
crashes$dtYearDay <- as.integer(crashes$dateDatetime$yday + 1)


### Hour and Minute (Time) ####

# Create a hour column
crashes$dtHour <- as.integer(crashes$dateDatetime$hour)

# Create a minute column
crashes$dtMinute <- as.integer(crashes$dateDatetime$min)


### Daylight Savings Time and Time Zone (Time) ####

# Create a daylight savings time flag column (0 = no, 1 = yes, -1 = unknown)
crashes$dtDst <- crashes$dateDatetime$isdst

# label the daylight savings time column
val_labels(crashes$dtDst) <- cb$dtDst$labels[cb$dtDst$labels %in% unique(crashes$dtDst)]

# Create a time zone column
crashes$dtZone <- crashes$dateDatetime$zone

# Convert the time zone column to an integer by recoding its values
crashes$dtZone <- as.integer(recode(crashes$dtZone, `PST` = -8, `PDT` = -7, .missing = NULL, .default = 999))
crashes$dtZone[crashes$dtZone == 999] <- NA

# Label the time zone column
val_labels(crashes$dtZone) <- cb$dtZone$labels[cb$dtZone$labels %in% unique(crashes$dtZone)]


### Order the New Date and Time Columns ####

# relocate the new datetime columns after the collDateTime column
crashes <- crashes %>% relocate(dateDatetime, .after = city)
crashes <- crashes %>% relocate(dateYear, .after = dateDatetime)
crashes <- crashes %>% relocate(dateQuarter, .after = dateYear)
crashes <- crashes %>% relocate(dateMonth, .after = dateQuarter)
crashes <- crashes %>% relocate(dateWeek, .after = dateMonth)
crashes <- crashes %>% relocate(dateDay, .after = dateWeek)
crashes <- crashes %>% relocate(dateProcess, .after = dateDay)
crashes <- crashes %>% relocate(dtYear, .after = dateProcess)
crashes <- crashes %>% relocate(dtQuarter, .after = dtYear)
crashes <- crashes %>% relocate(dtMonth, .after = dtQuarter)
crashes <- crashes %>% relocate(dtYearWeek, .after = dtMonth)
crashes <- crashes %>% relocate(dtWeekDay, .after = dtYearWeek)
crashes <- crashes %>% relocate(dtMonthDay, .after = dtWeekDay)
crashes <- crashes %>% relocate(dtYearDay, .after = dtMonthDay)
crashes <- crashes %>% relocate(dtHour, .after = dtYearDay)
crashes <- crashes %>% relocate(dtMinute, .after = dtHour)
crashes <- crashes %>% relocate(dtDst, .after = dtMinute)
crashes <- crashes %>% relocate(dtZone, .after = dtDst)


## 6.4. Collision Time Intervals ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a new column in the crashes data frame called collTimeIntervals
crashes$collTimeIntervals <- NA

# Create a new collumn in the crashes data frame called collTimeIntervals that has value of 1 if the collTime is between 00:00 and 06:00, 2 if it is between 06:00 and 12:00, 3 if it is between 12:00 and 18:00, 4 if it is between 18:00 and 24:00
crashes$collTimeIntervals[which(crashes$dtHour >= 0 & crashes$dtHour <= 6)] <- 1
crashes$collTimeIntervals[which(crashes$dtHour > 6 & crashes$dtHour <= 12)] <- 2
crashes$collTimeIntervals[which(crashes$dtHour > 12 & crashes$dtHour <= 18)] <- 3
crashes$collTimeIntervals[which(crashes$dtHour > 18 & crashes$dtHour <= 24)] <- 4
crashes$collTimeIntervals[which(crashes$dtHour > 24)] <- 9

# convert to integer
crashes$collTimeIntervals <- as.integer(crashes$collTimeIntervals)

# Add labels to the collTimeIntervals column
val_labels(crashes$collTimeIntervals) <- cb$collTimeIntervals$labels[cb$collTimeIntervals$labels %in% unique(crashes$collTimeIntervals)]

# order the collTimeIntervals column after the collTime column
crashes <- crashes %>% relocate(collTimeIntervals, .after = collTime)


## 6.5. Rush Hours ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Rush Hours Intervals ####

# create a new column in the crashes dataframe called rushHours that has value of 1 if the dtWeekDay is between 2 and 6 (Monday to Friday) and the collTime is between 07:00 and 10:00, 2 if the dtWeekDay is between 2 and 6 (Monday to Friday) and the collTime is between 16:00 and 19:00,9 if the collTime is greater than 2400, and 3 otherwise.
crashes$rushHours <- as.integer(ifelse(
    crashes$dtWeekDay >= 2 & crashes$dtWeekDay <= 6 & crashes$dtHour >= 7 & crashes$dtHour <= 10,
    1,
    ifelse(
        crashes$dtWeekDay >= 2 & crashes$dtWeekDay <= 6 & crashes$dtHour >= 16 & crashes$dtHour <= 19,
        2,
        ifelse(
            crashes$dtHour > 24,
            9,
            0
        )
    )
))

# label the rushHours column
val_labels(crashes$rushHours) <- cb$rushHours$labels

# order the rushHours column after the collTimeIntervals column
crashes <- crashes %>% relocate(rushHours, .after = collTimeIntervals)


### Rush Hours Indicators ####

# create a new column in the crashes dataframe called rushHoursBin that has value of 1 if the rushHours is 1 or 2, and 0 otherwise
crashes$rushHoursBin <- as.integer(ifelse(crashes$rushHours == 1 | crashes$rushHours == 2, 1, 0))

# label the rushHoursBin column
val_labels(crashes$rushHoursBin) <- cb$rushHoursBin$labels

# order the rushHoursBin column after the rushHours column
crashes <- crashes %>% relocate(rushHoursBin, .after = rushHours)

# save the data frames to disk
#saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 7. Collision Severity Processing ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 7.1. Factoring Collision Severity ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Convert the collision severity to an integer
crashes$collSeverity <- as.integer(crashes$collSeverity)

# recode the collision seveirity from values from 0 to 0, 4 to 1, 3 to 2, 2 to 3, and 1 to 4
crashes$collSeverity <- as.integer(recode(crashes$collSeverity, `0` = 0, `4` = 1, `3` = 2, `2` = 3, `1` = 4, .missing = NULL, .default = 999))
crashes$collSeverity[crashes$collSeverity == 999] <- NA

# label the collision severity column
val_labels(crashes$collSeverity) <- cb$collSeverity$labels[cb$collSeverity$labels %in% unique(crashes$collSeverity)]


## 7.2. Binary Collision Severity ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate a new column in the crashes data frame called collSeverityBin that has value of 1 if the collSeverity is 3 or 4, and 0 otherwise
crashes$collSeverityBin <- as.integer(ifelse(crashes$collSeverity == 3 | crashes$collSeverity == 4, 1, 0))

# Label the collSeverityBin column
val_labels(crashes$collSeverityBin) <- cb$collSeverityBin$labels[cb$collSeverityBin$labels %in% unique(crashes$collSeverityBin)]

# Order the collSeverityBin column after the collSeverity column
crashes <- crashes %>% relocate(collSeverityBin, .after = collSeverity)


## 7.3. Ranked Collision Severity ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate a new column in the crashes data frame called collseverityranked that ranks the collision severity based on the number of killed and severe injuries
crashes$collSeverityRank <- as.integer(ifelse(
    crashes$numberKilled == 0 & crashes$countSevereInj == 0, 0,
    ifelse(
        crashes$numberKilled == 0 & crashes$countSevereInj == 1, 1,
        ifelse(
            crashes$numberKilled == 0 & crashes$countSevereInj > 1, 2,
            ifelse(
                crashes$numberKilled == 1 & crashes$countSevereInj == 0, 3,
                ifelse(
                    crashes$numberKilled == 1 & crashes$countSevereInj == 1, 4,
                    ifelse(
                        crashes$numberKilled == 1 & crashes$countSevereInj > 1, 5,
                        ifelse(
                            crashes$numberKilled > 1 & crashes$countSevereInj == 0, 6,
                            ifelse(
                                crashes$numberKilled > 1 & crashes$countSevereInj == 1, 7,
                                ifelse(
                                    crashes$numberKilled > 1 & crashes$countSevereInj > 1, 8, NA
                                )
                            )
                        )
                    )
                )
            )
        )
    )
))

# Label the collSeverityRank column
val_labels(crashes$collSeverityRank) <- cb$collSeverityRank$labels[cb$collSeverityRank$labels %in% unique(crashes$collSeverityRank)]

# Order the collseverityranked column after the collSeverityBin column
crashes <- crashes %>% relocate(collSeverityRank, .after = collSeverityBin)


## 7.4. Collision Severity Numeric ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate a new column in the crashes data frame called collSeverityNum that is the integer value of the collSeverity column
crashes$collSeverityNum <- as.integer(crashes$collSeverity)

# Generate a new column in the craashes data frame called collSeverityRankNum that is the integer value of the collSeverityRank column
crashes$collSeverityRankNum <- as.integer(crashes$collSeverityRank)

# Relocate the collSeverityNum column after the collSeverity column
crashes <- crashes %>% relocate(collSeverityNum, .after = collSeverity)

# Relocate the collSeverityRankNum column after the collSeverityRank column
crashes <- crashes %>% relocate(collSeverityRankNum, .after = collSeverityRank)


## 7.5. Collision Severity Indicators ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the collSeverityRank column into three new columns: indSevere, indFatal, and indMulti, with the following values:


### Severe Injury Indicator ####

# Severe injury indicator
crashes$indSevere <- as.integer(ifelse(crashes$collSeverity == 3, 1, 0))

# Label the indSevere column
val_labels(crashes$indSevere) <- cb$indSevere$labels[cb$indSevere$labels %in% unique(crashes$indSevere)]

# order the indSevere column after the collSeverityRank column
crashes <- crashes %>% relocate(indSevere, .after = collSeverityRank)


### Fatal Injury Indicator ####

# Fatal injury indicator
crashes$indFatal <- as.integer(ifelse(crashes$collSeverity == 4, 1, 0))

# Label the indFatal column
val_labels(crashes$indFatal) <- cb$indFatal$labels[cb$indFatal$labels %in% unique(crashes$indFatal)]

# order the indFatal column after the indSevere column
crashes <- crashes %>% relocate(indFatal, .after = indSevere)


### Multiple Severe or Fatal Injuries Indicator ####

# Multiple injuries indicator
crashes$indMulti <- as.integer(ifelse(crashes$collSeverityRank %in% c(2, 5, 6, 7, 8), 1, 0))

# Label the indMulti column
val_labels(crashes$indMulti) <- cb$indMulti$labels[cb$indMulti$labels %in% unique(crashes$indMulti)]

# order the indMulti column after the indFatal column
crashes <- crashes %>% relocate(indMulti, .after = indFatal)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 8. Generate New Counts ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 8.1. Generate victim count ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate a new column in the crashes data frame called victimCount that is the sum of the numberKilled and numberInj columns
crashes$victimCount <- as.integer(crashes$numberKilled + crashes$numberInj)

# order the victimCount column after the partyCount column
crashes <- crashes %>% relocate(victimCount, .after = partyCount)


## 8.2. Generate car passenger killed and injured count ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate a new column in the crashes data frame called countCarKilled that is the difference between the numberKilled and the sum of countPedKilled, countBicKilled, and countMcKilled columns
crashes$countCarKilled <- as.integer(crashes$numberKilled - crashes$countPedKilled - crashes$countBicKilled - crashes$countMcKilled)

# order the countCarKilled column after the countComplaintPain column
crashes <- crashes %>% relocate(countCarKilled, .after = countComplaintPain)

# Generate a new column in the crashes data frame called countCarInj that is the difference between the numberInj and the sum of countPedInj, countBicInj, and countMcInj columns
crashes$countCarInj <- as.integer(crashes$numberInj - crashes$countPedInj - crashes$countBicInj - crashes$countMcInj)

# order the countCarInj column after the countCarKilled column
crashes <- crashes %>% relocate(countCarInj, .after = countCarKilled)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 9. Crash Characteristics ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 9.1. Primary crash factor ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the primary crash factor to numeric
crashes$primaryCollFactor <- as.integer(recode(crashes$primaryCollFactor, "A" = 1, "B" = 2, "C" = 3, "D" = 3, "E" = 5, "-" = 0, .missing = NULL, .default = 999))
crashes$primaryCollFactor[crashes$primaryCollFactor == 999] <- NA

# Label the primary crash factor
val_labels(crashes$primaryCollFactor) <- cb$primaryCollFactor$labels[cb$primaryCollFactor$labels %in% unique(crashes$primaryCollFactor)]


## 9.2. Collision Type ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the collision type to numeric
crashes$typeOfColl <- as.integer(recode(crashes$typeOfColl, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "-" = 0, .missing = NULL, .default = 999))
crashes$typeOfColl[crashes$typeOfColl == 999] <- NA

# Label the collision type
val_labels(crashes$typeOfColl) <- cb$typeOfColl$labels[cb$typeOfColl$labels %in% unique(crashes$typeOfColl)]


## 9.3. Pedestrian Crash ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the pedestrian crash to numeric
crashes$pedAccident <- as.integer(recode(crashes$pedAccident, "Y" = 1, .missing = NULL, .default = 999))
crashes$pedAccident[crashes$pedAccident == 999] <- NA

# Label the pedestrian crash
val_labels(crashes$pedAccident) <- cb$pedAccident$labels[cb$pedAccident$labels %in% unique(crashes$pedAccident)]


## 9.4. Bicycle Crash ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the bicycle crash to numeric
crashes$bicAccident <- as.integer(recode(crashes$bicAccident, "Y" = 1, .missing = NULL, .default = 999))
crashes$bicAccident[crashes$bicAccident == 999] <- NA

# Label the bicycle crash
val_labels(crashes$bicAccident) <- cb$bicAccident$labels[cb$bicAccident$labels %in% unique(crashes$bicAccident)]


## 9.5. Motorcycle Crash ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the motorcycle crash to numeric
crashes$mcAccident <- as.integer(recode(crashes$mcAccident, "Y" = 1, .missing = NULL, .default = 999))
crashes$mcAccident[crashes$mcAccident == 999] <- NA

# Label the motorcycle crash
val_labels(crashes$mcAccident) <- cb$mcAccident$labels[cb$mcAccident$labels %in% unique(crashes$mcAccident)]


## 9.6. Truck Crash ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the truck crash to numeric
crashes$truckAccident <- as.integer(recode(crashes$truckAccident, "Y" = 1, .missing = NULL, .default = 999))
crashes$truckAccident[crashes$truckAccident == 999] <- NA

# Label the truck crash
val_labels(crashes$truckAccident) <- cb$truckAccident$labels[cb$truckAccident$labels %in% unique(crashes$truckAccident)]


## 9.7. Hit and Run ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Hit and Run (type of) ####

# Recode the hit and run to numeric
crashes$hitAndRun <- as.integer(recode(crashes$hitAndRun, "N" = 0, "M" = 1, "F" = 2, .missing = NULL, .default = 999))
crashes$hitAndRun[crashes$hitAndRun == 999] <- NA

# Label the hit and run
val_labels(crashes$hitAndRun) <- cb$hitAndRun$labels[cb$hitAndRun$labels %in% unique(crashes$hitAndRun)]


### Hit and Run (binary) ####

# Create a binary column called hitAndRunBin that has value of 1 if the hitAndRun is 1 or 2, and 0 otherwise
crashes$hitAndRunBin <- as.integer(ifelse(crashes$hitAndRun == 1 | crashes$hitAndRun == 2, 1, 0))

# Label the hitAndRunBin column
val_labels(crashes$hitAndRunBin) <- cb$hitAndRunBin$labels

# Order the hitAndRunBin column after the hitAndRun column
crashes <- crashes %>% relocate(hitAndRunBin, .after = hitAndRun)


## 9.8. Alcohol Involved ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the alcohol involved to numeric
crashes$alcoholInvolved <- as.integer(recode(crashes$alcoholInvolved, "Y" = 1, .missing = NULL, .default = 999))
crashes$alcoholInvolved[crashes$alcoholInvolved == 999] <- NA

# Label the alcohol involved
val_labels(crashes$alcoholInvolved) <- cb$alcoholInvolved$labels[cb$alcoholInvolved$labels %in% unique(crashes$alcoholInvolved)]


## 9.9. CHP Shift ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP shift to numeric
crashes$chpShift <- as.integer(crashes$chpShift)

# Label the CHP shift
val_labels(crashes$chpShift) <- cb$chpShift$labels[cb$chpShift$labels %in% unique(crashes$chpShift)]


## 9.10. Special Conditions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the special conditions to numeric
crashes$specialCond <- as.integer(recode(crashes$specialCond, "0" = 0, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "6" = 6, "-" = 9, .missing = NULL, .default = 999))
crashes$specialCond[crashes$specialCond == 999] <- NA

# label the special conditions
val_labels(crashes$specialCond) <- cb$specialCond$labels[cb$specialCond$labels %in% unique(crashes$specialCond)]


## 9.11. Beat Type ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the beat type to numeric
crashes$beatType <- as.integer(recode(crashes$beatType, "0" = 0, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "6" = 6, "7" = 7, "8" = 8, .missing = NULL, .default = 999))
crashes$beatType[crashes$beatType == 999] <- NA

# label the beat type
val_labels(crashes$beatType) <- cb$beatType$labels[cb$beatType$labels %in% unique(crashes$beatType)]


## 9.12. CHP Beat Type ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP beat type to numeric
crashes$chpBeatType <- as.integer(recode(crashes$chpBeatType, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "A" = 6, "S" = 7, "0" = 0, "6" = 8, "7" = 9, "8" = 10, "9" = 11, .missing = NULL, .default = 999))
crashes$chpBeatType[crashes$chpBeatType == 999] <- NA

# label the CHP beat type
val_labels(crashes$chpBeatType) <- cb$chpBeatType$labels[cb$chpBeatType$labels %in% unique(crashes$chpBeatType)]


## 9.13. CHP Beat Class ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP beat class to numeric
crashes$chpBeatClass <- as.integer(recode(crashes$chpBeatClass, "1" = 1, "2" = 2, "0" = 0, .missing = NULL, .default = 999))
crashes$chpBeatClass[crashes$chpBeatClass == 999] <- NA

# label the CHP beat class
val_labels(crashes$chpBeatClass) <- cb$chpBeatClass$labels[cb$chpBeatClass$labels %in% unique(crashes$chpBeatClass)]


## 9.14. Direction ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the direction to numeric
crashes$direction <- as.integer(recode(crashes$direction, "N" = 1, "S" = 2, "E" = 3, "W" = 4, .missing = NULL, .default = 999))
crashes$direction[crashes$direction == 999] <- NA

# label the direction
val_labels(crashes$direction) <- cb$direction$labels[cb$direction$labels %in% unique(crashes$direction)]


## 9.15. Intersection ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the intersection to numeric
crashes$intersection <- as.integer(recode(crashes$intersection, "Y" = 1, "N" = 0, "-" = 9, .missing = NULL, .default = 999))
crashes$intersection[crashes$intersection == 999] <- NA

# label the intersection
val_labels(crashes$intersection) <- cb$intersection$labels[cb$intersection$labels %in% unique(crashes$intersection)]


## 9.16. Weather Conditions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Weather 1 ####

# Recode the weather1 to numeric
crashes$weather1 <- as.integer(recode(crashes$weather1, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "G" = 6, "F" = 7, "-" = 0, .missing = NULL, .default = 999))
crashes$weather1[crashes$weather1 == 999] <- NA

# label the weather1
val_labels(crashes$weather1) <- cb$weather1$labels[cb$weather1$labels %in% unique(crashes$weather1)]


### Weather 2 ####

# Recode the weather2 to numeric
crashes$weather2 <- as.integer(recode(crashes$weather2, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "G" = 6, "F" = 7, "-" = 0, .missing = NULL, .default = 999))
crashes$weather2[crashes$weather2 == 999] <- NA

# label the weather2
val_labels(crashes$weather2) <- cb$weather2$labels[cb$weather2$labels %in% unique(crashes$weather2)]


### Combined Weather ####

# Combine the weather1 and weather2 columns into a new column called weatherComb
crashes$weatherComb <- as.integer((crashes$weather1 * 10) + crashes$weather2)

# label the weatherComb
val_labels(crashes$weatherComb) <- cb$weatherComb$labels[cb$weatherComb$labels %in% unique(crashes$weatherComb)]

# order the weatherComb column after the weather2 column
crashes <- crashes %>% relocate(weatherComb, .after = weather2)


## 9.17. Road Surface ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the road surface to numeric
crashes$roadSurface <- as.integer(recode(crashes$roadSurface, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "H" = 5, "-" = 0, .missing = NULL, .default = 999))
crashes$roadSurface[crashes$roadSurface == 999] <- NA

# label the road surface
val_labels(crashes$roadSurface) <- cb$roadSurface$labels[cb$roadSurface$labels %in% unique(crashes$roadSurface)]


## 9.18. Road Condition ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the road condition 1 to numeric
crashes$roadCond1 <- as.integer(recode(crashes$roadCond1, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "-" = 0, .missing = NULL, .default = 999))
crashes$roadCond1[crashes$roadCond1 == 999] <- NA

# label the road condition 1
val_labels(crashes$roadCond1) <- cb$roadCond1$labels[cb$roadCond1$labels %in% unique(crashes$roadCond1)]

# Recode the road condition 2 to numeric
crashes$roadCond2 <- as.integer(recode(crashes$roadCond2, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "-" = 0, .missing = NULL, .default = 999))
crashes$roadCond2[crashes$roadCond2 == 999] <- NA

# label the road condition 2
val_labels(crashes$roadCond2) <- cb$roadCond2$labels[cb$roadCond2$labels %in% unique(crashes$roadCond2)]


## 9.19. Lighting ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the lighting to numeric
crashes$lighting <- as.integer(recode(crashes$lighting, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "-" = 0, .missing = NULL, .default = 999))
crashes$lighting[crashes$lighting == 999] <- NA

# label the lighting
val_labels(crashes$lighting) <- cb$lighting$labels[cb$lighting$labels %in% unique(crashes$lighting)]


## 9.20. Control Device ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the control device to numeric
crashes$controlDevice <- as.integer(recode(crashes$controlDevice, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "-" = 0, .missing = NULL, .default = 999))
crashes$controlDevice[crashes$controlDevice == 999] <- NA

# label the control device
val_labels(crashes$controlDevice) <- cb$controlDevice$labels[cb$controlDevice$labels %in% unique(crashes$controlDevice)]


## 9.21. State Highway Indicator ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the state highway indicator to numeric
crashes$stateHwyInd <- as.integer(recode(crashes$stateHwyInd, "Y" = 1, "N" = 0, "-" = 9, .missing = NULL, .default = 999))
crashes$stateHwyInd[crashes$stateHwyInd == 999] <- NA

# label the state highway indicator
val_labels(crashes$stateHwyInd) <- cb$stateHwyInd$labels[cb$stateHwyInd$labels %in% unique(crashes$stateHwyInd)]


## 9.22. Side of Highway ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the side of highway to numeric
crashes$sideOfHwy <- as.integer(recode(crashes$sideOfHwy, "N" = 1, "S" = 2, "E" = 3, "W" = 4, "L" = 5, "R" = 6, .missing = NULL, .default = 999))
crashes$sideOfHwy[crashes$sideOfHwy == 999] <- NA

# label the side of highway
val_labels(crashes$sideOfHwy) <- cb$sideOfHwy$labels[cb$sideOfHwy$labels %in% unique(crashes$sideOfHwy)]


## 9.23. Tow Away ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the tow away to numeric
crashes$towAway <- as.integer(recode(crashes$towAway, "Y" = 1, "N" = 0, .missing = NULL, .default = 999))
crashes$towAway[crashes$towAway == 999] <- NA

# label the tow away
val_labels(crashes$towAway) <- cb$towAway$labels[cb$towAway$labels %in% unique(crashes$towAway)]


## 9.24. PCF Code of Violation ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the PCF code of violation to numeric
crashes$pcfCodeOfViol <- as.integer(recode(crashes$pcfCodeOfViol, "B" = 1, "C" = 2, "H" = 3, "I" = 4, "O" = 5, "P" = 6, "S" = 7, "W" = 8, "-" = 0, .missing = NULL, .default = 999))
crashes$pcfCodeOfViol[crashes$pcfCodeOfViol == 999] <- NA

# label the PCF code of violation
val_labels(crashes$pcfCodeOfViol) <- cb$pcfCodeOfViol$labels[cb$pcfCodeOfViol$labels %in% unique(crashes$pcfCodeOfViol)]


## 9.25. PCF Violation Category ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the PCF violation category to numeric
crashes$pcfViolCategory <- as.integer(recode(crashes$pcfViolCategory, "01" = 1, "02" = 2, "03" = 3, "04" = 4, "05" = 5, "06" = 6, "07" = 7, "08" = 8, "09" = 9, "10" = 10, "11" = 11, "12" = 12, "13" = 13, "14" = 14, "15" = 15, "16" = 16, "17" = 17, "18" = 18, "19" = 19, "20" = 20, "21" = 21, "22" = 22, "23" = 23, "24" = 24, "00" = 0, "-" = 99, .missing = NULL, .default = 999))
crashes$pcfViolCategory[crashes$pcfViolCategory == 999] <- NA

# label the PCF violation category
val_labels(crashes$pcfViolCategory) <- cb$pcfViolCategory$labels[cb$pcfViolCategory$labels %in% unique(crashes$pcfViolCategory)]


## 9.26. MVIW ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Recode the MVIW to numeric
crashes$mviw <- as.integer(recode(crashes$mviw, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "I" = 9, "J" = 10, "0" = 11, "1" = 12, "2" = 13, "3" = 14, "4" = 15, "5" = 16, "6" = 17, "7" = 18, "8" = 19, "9" = 20, "-" = 0, .missing = NULL, .default = 999))
crashes$mviw[crashes$mviw == 999] <- NA

# label the MVIW
val_labels(crashes$mviw) <- cb$mviw$labels[cb$mviw$labels %in% unique(crashes$mviw)]


## 9.27. Pedestrian Action ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the pedestrian action to numeric
crashes$pedAction <- as.integer(recode(crashes$pedAction, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "-" = 0, .missing = NULL, .default = 999))
crashes$pedAction[crashes$pedAction == 999] <- NA

# label the pedestrian action
val_labels(crashes$pedAction) <- cb$pedAction$labels[cb$pedAction$labels %in% unique(crashes$pedAction)]


## 9.28. Not Private Property ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the not private property to numeric
crashes$notPrivateProperty <- as.integer(recode(crashes$notPrivateProperty, "Y" = 1, .missing = NULL, .default = 999))
crashes$notPrivateProperty[crashes$notPrivateProperty == 999] <- NA

# label the not private property
val_labels(crashes$notPrivateProperty) <- cb$notPrivateProperty$labels[cb$notPrivateProperty$labels %in% unique(crashes$notPrivateProperty)]


## 9.29. State Wide Vehicle Type at Fault ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the state wide vehicle type at fault to numeric
crashes$stwdVehTypeAtFault <- as.integer(recode(crashes$stwdVehTypeAtFault, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "I" = 9, "J" = 10, "K" = 11, "L" = 12, "M" = 13, "N" = 14, "O" = 15, "-" = 0, .missing = NULL, .default = 999))
crashes$stwdVehTypeAtFault[crashes$stwdVehTypeAtFault == 999] <- NA

# label the state wide vehicle type at fault
val_labels(crashes$stwdVehTypeAtFault) <- cb$stwdVehTypeAtFault$labels[cb$stwdVehTypeAtFault$labels %in% unique(crashes$stwdVehTypeAtFault)]

## 9.30. CHP Vehicle Type at Fault ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP vehicle type at fault to numeric
crashes$chpVehTypeAtFault <- as.integer(recode(crashes$chpVehTypeAtFault, "01" = 1, "02" = 2, "03" = 3, "04" = 4, "05" = 5, "06" = 6, "07" = 7, "08" = 8, "09" = 9, "10" = 10, "11" = 11, "12" = 12, "13" = 13, "14" = 14, "15" = 15, "16" = 16, "17" = 17, "18" = 18, "19" = 19, "20" = 20, "21" = 21, "22" = 22, "23" = 23, "24" = 24, "25" = 25, "26" = 26, "27" = 27, "28" = 28, "29" = 29, "30" = 30, "31" = 31, "32" = 32, "33" = 33, "34" = 34, "35" = 35, "36" = 36, "37" = 37, "38" = 38, "39" = 39, "40" = 40, "41" = 41, "42" = 42, "43" = 43, "44" = 44, "45" = 45, "46" = 46, "47" = 47, "48" = 48, "49" = 49, "50" = 50, "51" = 51, "52" = 52, "53" = 53, "54" = 54, "55" = 55, "56" = 56, "57" = 57, "58" = 58, "59" = 59, "60" = 60, "61" = 61, "62" = 62, "63" = 63, "64" = 64, "65" = 65, "66" = 66, "71" = 71, "72" = 72, "73" = 73, "75" = 75, "76" = 76, "77" = 77, "78" = 78, "79" = 79, "81" = 81, "82" = 82, "83" = 83, "85" = 85, "86" = 86, "87" = 87, "88" = 88, "89" = 89, "91" = 91, "93" = 93, "94" = 94, "95" = 95, "96" = 96, "97" = 97, "98" = 98, "99" = 99, "-"  =  0, .missing = NULL, .default = 999))
crashes$chpVehTypeAtFault[crashes$chpVehTypeAtFault == 999] <- NA

# label the CHP vehicle type at fault
val_labels(crashes$chpVehTypeAtFault) <- cb$chpVehTypeAtFault$labels[cb$chpVehTypeAtFault$labels %in% unique(crashes$chpVehTypeAtFault)]


## 9.31. Primary and Secondary Ramp ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the primary ramp to numeric
crashes$primaryRamp <- as.integer(recode(crashes$primaryRamp, "TO" = 1, "FR" = 2, "NF" = 3, "SF" = 4, "EF" = 5, "WF" = 6, "NO" = 7, "SO" = 8, "EO" = 9, "WO" = 10, "TR" = 11, "CO" = 12, "CN" = 13, "-" = 0, .missing = NULL, .default = 999))
crashes$primaryRamp[crashes$primaryRamp == 999] <- NA

# label the primary ramp
val_labels(crashes$primaryRamp) <- cb$primaryRamp$labels[cb$primaryRamp$labels %in% unique(crashes$primaryRamp)]

# Recode the secondary ramp to numeric
crashes$secondaryRamp <- as.integer(recode(crashes$secondaryRamp, "TO" = 1, "FR" = 2, "NF" = 3, "SF" = 4, "EF" = 5, "WF" = 6, "NO" = 7, "SO" = 8, "EO" = 9, "WO" = 10, "TR" = 11, "CO" = 12, "CN" = 13, "-" = 0, .missing = NULL, .default = 999))
crashes$secondaryRamp[crashes$secondaryRamp == 999] <- NA

# label the secondary ramp
val_labels(crashes$secondaryRamp) <- cb$secondaryRamp$labels[cb$secondaryRamp$labels %in% unique(crashes$secondaryRamp)]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 10. Party Characteristics ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 10.1. Party Type ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the party type to numeric
parties$partyType <- as.integer(recode(parties$partyType, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "6" = 6, "-" = 0, .missing = NULL, .default = 999))
parties$partyType[parties$partyType == 999] <- NA

# Label the party type
val_labels(parties$partyType) <- cb$partyType$labels[cb$partyType$labels %in% unique(parties$partyType)]


## 10.2. At Fault ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the at fault to numeric
parties$atFault <- as.integer(recode(parties$atFault, "N" = 0, "Y" = 1, .missing = NULL, .default = 999))
parties$atFault[parties$atFault == 999] <- NA

# Label the at fault
val_labels(parties$atFault) <- cb$atFault$labels[cb$atFault$labels %in% unique(parties$atFault)]


## 10.3. Party Sex ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the party sex to numeric
parties$partySex <- as.integer(recode(parties$partySex, "M" = 1, "F" = 2, "X" = 3, "-" = 0, .missing = NULL, .default = 999))
parties$partySex[parties$partySex == 999] <- NA

# Label the party sex
val_labels(parties$partySex) <- cb$partySex$labels[cb$partySex$labels %in% unique(parties$partySex)]


## 10.4. Party Age ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the unknown party age to NA
parties$partyAge[which(parties$partyAge >= 998)] <- NA

# Create a new column for party age group
parties$partyAgeGroup <- as.integer(NA)

# Create age groups for party age in the form (a,b], i.e., the lowest age is not included in the group, but the highest age is.
parties$partyAgeGroup[which(parties$partyAge >= 0 & parties$partyAge <= 10)] <- 1
parties$partyAgeGroup[which(parties$partyAge > 10 & parties$partyAge <= 18)] <- 2
parties$partyAgeGroup[which(parties$partyAge > 18 & parties$partyAge <= 25)] <- 3
parties$partyAgeGroup[which(parties$partyAge > 25 & parties$partyAge <= 35)] <- 4
parties$partyAgeGroup[which(parties$partyAge > 35 & parties$partyAge <= 45)] <- 5
parties$partyAgeGroup[which(parties$partyAge > 45 & parties$partyAge <= 55)] <- 6
parties$partyAgeGroup[which(parties$partyAge > 55 & parties$partyAge <= 65)] <- 7
parties$partyAgeGroup[which(parties$partyAge > 65 & parties$partyAge <= 80)] <- 8
parties$partyAgeGroup[which(parties$partyAge > 80 & parties$partyAge <= 100)] <- 9
parties$partyAgeGroup[which(parties$partyAge > 100 & parties$partyAge <= 125)] <- 10
parties$partyAgeGroup[which(parties$partyAge >= 125)] <- 0
parties$partyAgeGroup[which(parties$partyAge >= 998)] <- NA

# Recode the partyAgeGroup to numeric
parties$partyAgeGroup <- as.integer(parties$partyAgeGroup)

# Label the partyAgeGroup
val_labels(parties$partyAgeGroup) <- cb$partyAgeGroup$labels[cb$partyAgeGroup$labels %in% unique(parties$partyAgeGroup)]

# order the partyAgeGroup column after the partyAge column
parties <- parties %>% relocate(partyAgeGroup, .after = partyAge)


## 10.5. Party Race ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the partyRace to numeric
parties$partyRace <- as.integer(recode(parties$partyRace, "A" = 1, "B" = 2, "H" = 3, "O" = 4, "W" = 5, .missing = NULL, .default = 999))
parties$partyRace[parties$partyRace == 999] <- NA

# Label the partyRace
val_labels(parties$partyRace) <- cb$partyRace$labels[cb$partyRace$labels %in% unique(parties$partyRace)]


## 10.6. Inattention ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the inattention to numeric
parties$inattention <- as.integer(recode(parties$inattention, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "I" = 9, "J" = 10, "K" = 11, "P" = 12, "-" = 0, .missing = NULL, .default = 999))
parties$inattention[parties$inattention == 999] <- NA

# Label the inattention
val_labels(parties$inattention) <- cb$inattention$labels[cb$inattention$labels %in% unique(parties$inattention)]


## 10.7. Party Sobriety ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the party sobriety to numeric
parties$partySobriety <- as.integer(recode(parties$partySobriety, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "G" = 5, "H" = 6, "-" = 0, .missing = NULL, .default = 999))
parties$partySobriety[parties$partySobriety == 999] <- NA

# Label the party sobriety
val_labels(parties$partySobriety) <- cb$partySobriety$labels[cb$partySobriety$labels %in% unique(parties$partySobriety)]


### Party Sobriety Indicator (dui alcohol indicator) ####

# create a new variable duiAlcoholInd if the party sobriety is 2 and 0 otherwise
parties$duiAlcoholInd <- as.integer(ifelse(parties$partySobriety == 2, 1, 0))

# label the duiAlcoholInd
val_labels(parties$duiAlcoholInd) <- cb$duiAlcoholInd$labels[cb$duiAlcoholInd$labels %in% unique(parties$duiAlcoholInd)]

# order the duiAlcoholInd column after the partySobriety column
parties <- parties %>% relocate(duiAlcoholInd, .after = partySobriety)


## 10.8. Party Drug Physical ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the party drug physical to numeric
parties$partyDrugPhysical <- as.integer(recode(parties$partyDrugPhysical, "E" = 1, "F" = 2, "G" = 3, "H" = 4, "I" = 5, "-" = 0, .missing = NULL, .default = 999))
parties$partyDrugPhysical[parties$partyDrugPhysical == 999] <- NA

# Label the party drug physical
val_labels(parties$partyDrugPhysical) <- cb$partyDrugPhysical$labels[cb$partyDrugPhysical$labels %in% unique(parties$partyDrugPhysical)]


### Party Drug Physical Indicator (dui drug indicator) ####

# create a new variable duiDrugInd if the party drug physical is 1 and 0 otherwise
parties$duiDrugInd <- as.integer(ifelse(parties$partyDrugPhysical == 1, 1, 0))

# label the duiDrugInd
val_labels(parties$duiDrugInd) <- cb$duiDrugInd$labels[cb$duiDrugInd$labels %in% unique(parties$duiDrugInd)]

# order the duiDrugInd column after the partyDrugPhysical column
parties <- parties %>% relocate(duiDrugInd, .after = partyDrugPhysical)


## 10.9. Direction of Travel ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the direction of travel to numeric
parties$dirOfTravel <- as.integer(recode(parties$dirOfTravel, "N" = 1, "S" = 2, "E" = 3, "W" = 4, "-" = 0, .missing = NULL, .default = 999))
parties$dirOfTravel[parties$dirOfTravel == 999] <- NA

# Label the direction of travel
val_labels(parties$dirOfTravel) <- cb$dirOfTravel$labels[cb$dirOfTravel$labels %in% unique(parties$dirOfTravel)]


## 10.10. Party Safety Equipment ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Party Safety Equipment 1 ####

# Recode the party safety equipment 1 to numeric
parties$partySafetyEq1 <- as.integer(recode(parties$partySafetyEq1, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "J" = 9, "K" = 10, "L" = 11, "M" = 12, "N" = 13, "P" = 14, "Q" = 15, "R" = 16, "S" = 17, "T" = 18, "U" = 19, "V" = 20, "W" = 21, "X" = 22, "Y" = 23, "-" = 0, .missing = NULL, .default = 999))
parties$partySafetyEq1[parties$partySafetyEq1 == 999] <- NA

# Label the party safety equipment 1
val_labels(parties$partySafetyEq1) <- cb$partySafetyEq1$labels[cb$partySafetyEq1$labels %in% unique(parties$partySafetyEq1)]


### Party Safety Equipment 2 ####

# Recode the party safety equipment 2 to numeric
parties$partySafetyEq2 <- as.integer(recode(parties$partySafetyEq2, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "J" = 9, "K" = 10, "L" = 11, "M" = 12, "N" = 13, "P" = 14, "Q" = 15, "R" = 16, "S" = 17, "T" = 18, "U" = 19, "V" = 20, "W" = 21, "X" = 22, "Y" = 23, "-" = 0, .missing = NULL, .default = 999))
parties$partySafetyEq2[parties$partySafetyEq2 == 999] <- NA

# Label the party safety equipment 2
val_labels(parties$partySafetyEq2) <- cb$partySafetyEq2$labels[cb$partySafetyEq2$labels %in% unique(parties$partySafetyEq2)]


## 10.11. Financial Responsibility ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the financial responsibility to numeric
parties$finanRespons <- as.integer(recode(parties$finanRespons, "N" = 0, "Y" = 1, "O" = 2, "E" = 3, .missing = NULL, .default = 999))
parties$finanRespons[parties$finanRespons == 999] <- NA

# Label the financial responsibility
val_labels(parties$finanRespons) <- cb$finanRespons$labels[cb$finanRespons$labels %in% unique(parties$finanRespons)]


## 10.12. Party Special Information ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Special Information 1 ####

# Recode the special information 1 to numeric
parties$spInfo1 <- as.integer(recode(parties$spInfo1, "A" = 1, "-" = 0, .missing = NULL, .default = 999))
parties$spInfo1[parties$spInfo1 == 999] <- NA

# Label the special information 1
val_labels(parties$spInfo1) <- cb$spInfo1$labels[cb$spInfo1$labels %in% unique(parties$spInfo1)]


### Special Information 2 ####

# Recode the special information 2 to numeric
parties$spInfo2 <- as.integer(recode(parties$spInfo2, "B" = 1, "C" = 2, "D" = 3, "1" = 4, "2" = 5, "3" = 6, "4" = 7, "-" = 0, .missing = NULL, .default = 999))
parties$spInfo2[parties$spInfo2 == 999] <- NA

# Label the special information 2
val_labels(parties$spInfo2) <- cb$spInfo2$labels[cb$spInfo2$labels %in% unique(parties$spInfo2)]


### Special Information 3 ####

# Recode the special information 3 to numeric
parties$spInfo3 <- as.integer(recode(parties$spInfo3, "E" = 1, "-" = 0, .missing = NULL, .default = 999))
parties$spInfo3[parties$spInfo3 == 999] <- NA

# Label the special information 3
val_labels(parties$spInfo3) <- cb$spInfo3$labels[cb$spInfo3$labels %in% unique(parties$spInfo3)]


## 10.13. OAF Violation Code ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the OAF violation code to numeric
parties$oafViolCode <- as.integer(recode(parties$oafViolCode, "B" = 1, "C" = 2, "H" = 3, "I" = 4, "O" = 5, "P" = 6, "S" = 7, "W" = 8, "-" = 0, .missing = NULL, .default = 999))
parties$oafViolCode[parties$oafViolCode == 999] <- NA

# Label the OAF violation code
val_labels(parties$oafViolCode) <- cb$oafViolCode$labels[cb$oafViolCode$labels %in% unique(parties$oafViolCode)]


## 10.14. OAF Violation Category ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the OAF violation category to numeric
parties$oafViolCat <- as.integer(recode(parties$oafViolCat, "01" = 1, "02" = 2, "03" = 3, "05" = 5, "06" = 6, "08" = 8, "09" = 9, "10" = 10, "11" = 11, "13" = 13, "15" = 15, "16" = 16, "17" = 17, "18" = 18, "19" = 19, "20" = 20, "21" = 21, "22" = 22, "23" = 23, "24" = 24, "25" = 25, "26" = 26, "27" = 27, "28" = 28, "29" = 29, "30" = 30, "31" = 31, "33" = 33, "34" = 34, "35" = 35, "38" = 36, "39" = 39, "40" = 40, "43" = 43, "44" = 44, "46" = 46, "47" = 47, "48" = 48, "49" = 49, "50" = 50, "51" = 51, "52" = 52, "53" = 53, "60" = 60, "61" = 61, "62" = 62, "63" = 63, "00" = 0, "-" = 99, .missing = NULL, .default = 999))
parties$oafViolCat[parties$oafViolCat == 999] <- NA

# Label the OAF violation category
val_labels(parties$oafViolCat) <- cb$oafViolCat$labels[cb$oafViolCat$labels %in% unique(parties$oafViolCat)]


## 10.15. OAF Violation Section ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### OAF Violation Section 1 ####

# Recode the OAF violation section 1 to numeric
parties$oaf1 <- as.integer(recode(parties$oaf1, "A" = 1, "E" = 2, "F" = 3, "G" = 4, "H" = 5, "I" = 6, "J" = 7, "K" = 8, "L" = 9, "M" = 10, "N" = 11, "O" = 12, "P" = 13, "Q" = 14, "R" = 15, "S" = 16, "T" = 17, "U" = 18, "V" = 19, "W" = 20, "X" = 21, "Y" = 22, "-" = 0, .missing = NULL, .default = 909))
parties$oaf1[parties$oaf1 == 909] <- NA

# Label the OAF violation section 1
val_labels(parties$oaf1) <- cb$oaf1$labels[cb$oaf1$labels %in% unique(parties$oaf1)]


### OAF Violation Section 2 ####

# Recode the OAF violation section 2 to numeric
parties$oaf2 <- as.integer(recode(parties$oaf2, "A" = 1, "E" = 2, "F" = 3, "G" = 4, "H" = 5, "I" = 6, "J" = 7, "K" = 8, "L" = 9, "M" = 10, "N" = 11, "O" = 12, "P" = 13, "Q" = 14, "R" = 15, "S" = 16, "T" = 17, "U" = 18, "V" = 19, "W" = 20, "X" = 21, "Y" = 22, "-" = 0, .missing = NULL, .default = 999))
parties$oaf2[parties$oaf2 == 999] <- NA

# Label the OAF violation section 2
val_labels(parties$oaf2) <- cb$oaf2$labels[cb$oaf2$labels %in% unique(parties$oaf2)]


## 10.16. Movement Preceeding Accident ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the movement preceeding accident to numeric
parties$movePreAcc <- as.integer(recode(parties$movePreAcc, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "I" = 9, "J" = 10, "K" = 11, "L" = 12, "M" = 13, "N" = 14, "O" = 15, "P" = 16, "Q" = 17, "R" = 18, "S" = 19, "-" = 0, .missing = NULL, .default = 999))
parties$movePreAcc[parties$movePreAcc == 999] <- NA

# Label the movement preceeding accident
val_labels(parties$movePreAcc) <- cb$movePreAcc$labels[cb$movePreAcc$labels %in% unique(parties$movePreAcc)]


## 10.17. Vehicle Year ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Correct value of vehicle year from 1201 to 2011
parties$vehicleYear[which(parties$vehicleYear == 1201)] <- 2011
parties$vehicleYear[which(parties$vehicleYear == 215)] <- 2015
parties$vehicleYear[which(parties$vehicleYear == 2916)] <- 2016
parties$vehicleYear[which(parties$vehicleYear == 2203)] <- 2003
parties$vehicleYear[which(parties$vehicleYear == 2108)] <- 2018
parties$vehicleYear[which(parties$vehicleYear == 2102)] <- 2012
parties$vehicleYear[which(parties$vehicleYear == 2101)] <- 2011
parties$vehicleYear[which(parties$vehicleYear == 2047)] <- 2017

# Create a new column vehicleYearGroup and set it to NA
parties$vehicleYearGroup <- as.integer(NA)

# Group the vehicle year into decades
parties$vehicleYearGroup[which(parties$vehicleYear >= 1900 & parties$vehicleYear <= 1950)] <- 1
parties$vehicleYearGroup[which(parties$vehicleYear > 1950 & parties$vehicleYear <= 1960)] <- 2
parties$vehicleYearGroup[which(parties$vehicleYear > 1960 & parties$vehicleYear <= 1970)] <- 3
parties$vehicleYearGroup[which(parties$vehicleYear > 1970 & parties$vehicleYear <= 1980)] <- 4
parties$vehicleYearGroup[which(parties$vehicleYear > 1980 & parties$vehicleYear <= 1990)] <- 5
parties$vehicleYearGroup[which(parties$vehicleYear > 1990 & parties$vehicleYear <= 2000)] <- 6
parties$vehicleYearGroup[which(parties$vehicleYear > 2000 & parties$vehicleYear <= 2010)] <- 7
parties$vehicleYearGroup[which(parties$vehicleYear > 2010 & parties$vehicleYear <= 2020)] <- 8
parties$vehicleYearGroup[which(parties$vehicleYear > 2020 & parties$vehicleYear <= 2030)] <- 9

# Label the vehicle year group
val_labels(parties$vehicleYearGroup) <- cb$vehicleYearGroup$labels[cb$vehicleYearGroup$labels %in% unique(parties$vehicleYearGroup)]

# order the vehicleYearGroup column after the vehicleYear column
parties <- parties %>% relocate(vehicleYearGroup, .after = vehicleYear)


## 10.18. Vehicle Type ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the state wide vehicle type to numeric
parties$stwdVehicleType <- as.integer(recode(parties$stwdVehicleType, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "I" = 9, "J" = 10, "K" = 11, "L" = 12, "M" = 13, "N" = 14, "O" = 15, "-" = 0, .missing = NULL, .default = 999))
parties$stwdVehicleType[parties$stwdVehicleType == 999] <- NA

# Label the state wide vehicle type
val_labels(parties$stwdVehicleType) <- cb$stwdVehicleType$labels[cb$stwdVehicleType$labels %in% unique(parties$stwdVehicleType)]


## 10.19. CHP Vehicle Towing ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP vehicle towing to numeric
parties$chpVehTypeTowing <- as.integer(recode(parties$chpVehTypeTowing, "01" = 1, "02" = 2, "03" = 3, "04" = 4, "05" = 5, "06" = 6, "07" = 7, "08" = 8, "09" = 9, "10" = 10, "11" = 11, "12" = 12, "13" = 13, "14" = 14, "15" = 15, "16" = 16, "17" = 17, "18" = 18, "19" = 19, "20" = 20, "21" = 21, "22" = 22, "23" = 23, "24" = 24, "25" = 25, "26" = 26, "27" = 27, "28" = 28, "29" = 29, "30" = 30, "31" = 31, "32" = 32, "33" = 33, "34" = 34, "35" = 35, "36" = 36, "37" = 37, "38" = 38, "39" = 39, "40" = 40, "41" = 41, "42" = 42, "43" = 43, "44" = 44, "45" = 45, "46" = 46, "47" = 47, "48" = 48, "49" = 49, "50" = 50, "51" = 51, "52" = 52, "53" = 53, "54" = 54, "55" = 55, "56" = 56, "57" = 57, "58" = 58, "59" = 59, "60" = 60, "61" = 61, "62" = 62, "63" = 63, "64" = 64, "65" = 65, "66" = 66, "71" = 71, "72" = 72, "73" = 73, "75" = 75, "76" = 76, "77" = 77, "78" = 78, "79" = 79, "81" = 81, "82" = 82, "83" = 83, "85" = 85, "86" = 86, "87" = 87, "88" = 88, "89" = 89, "91" = 91, "93" = 93, "94" = 94, "95" = 95, "96" = 96, "97" = 97, "98" = 98, "99" = 99, "-"  =  0, .missing = NULL, .default = 999))
parties$chpVehTypeTowing[parties$chpVehTypeTowing == 999] <- NA

# Label the CHP vehicle towing
val_labels(parties$chpVehTypeTowing) <- cb$chpVehTypeTowing$labels[cb$chpVehTypeTowing$labels %in% unique(parties$chpVehTypeTowing)]


## 10.20. CHP Vehicle Type Towed ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the CHP vehicle type towed to numeric
parties$chpVehTypeTowed <- as.integer(recode(parties$chpVehTypeTowed, "01" = 1, "02" = 2, "03" = 3, "04" = 4, "05" = 5, "06" = 6, "07" = 7, "08" = 8, "09" = 9, "10" = 10, "11" = 11, "12" = 12, "13" = 13, "14" = 14, "15" = 15, "16" = 16, "17" = 17, "18" = 18, "19" = 19, "20" = 20, "21" = 21, "22" = 22, "23" = 23, "24" = 24, "25" = 25, "26" = 26, "27" = 27, "28" = 28, "29" = 29, "30" = 30, "31" = 31, "32" = 32, "33" = 33, "34" = 34, "35" = 35, "36" = 36, "37" = 37, "38" = 38, "39" = 39, "40" = 40, "41" = 41, "42" = 42, "43" = 43, "44" = 44, "45" = 45, "46" = 46, "47" = 47, "48" = 48, "49" = 49, "50" = 50, "51" = 51, "52" = 52, "53" = 53, "54" = 54, "55" = 55, "56" = 56, "57" = 57, "58" = 58, "59" = 59, "60" = 60, "61" = 61, "62" = 62, "63" = 63, "64" = 64, "65" = 65, "66" = 66, "71" = 71, "72" = 72, "73" = 73, "75" = 75, "76" = 76, "77" = 77, "78" = 78, "79" = 79, "81" = 81, "82" = 82, "83" = 83, "85" = 85, "86" = 86, "87" = 87, "88" = 88, "89" = 89, "91" = 91, "93" = 93, "94" = 94, "95" = 95, "96" = 96, "97" = 97, "98" = 98, "99" = 99, "-"  =  0, .missing = NULL, .default = 999))
parties$chpVehTypeTowed[parties$chpVehTypeTowed == 999] <- NA

# Label the CHP vehicle type towed
val_labels(parties$chpVehTypeTowed) <- cb$chpVehTypeTowed$labels[cb$chpVehTypeTowed$labels %in% unique(parties$chpVehTypeTowed)]


## 10.21. Special Info ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Special Info F ####

# Recode the special info F to numeric
parties$specialInfoF <- as.integer(recode(parties$specialInfoF, "F" = 1, "-" = 0, .missing = NULL, .default = 999))
parties$specialInfoF[parties$specialInfoF == 999] <- NA

# Label the special info F
val_labels(parties$specialInfoF) <- cb$specialInfoF$labels[cb$specialInfoF$labels %in% unique(parties$specialInfoF)]


### Special Info G ####

# Recode the special info G to numeric
parties$specialInfoG <- as.integer(recode(parties$specialInfoG, "G" = 1, "-" = 0, .missing = NULL, .default = 999))
parties$specialInfoG[parties$specialInfoG == 999] <- NA

# Label the special info G
val_labels(parties$specialInfoG) <- cb$specialInfoG$labels[cb$specialInfoG$labels %in% unique(parties$specialInfoG)]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 11. Victim Characteristics ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 11.1. Victim Role ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the victim role to numeric
victims$victimRole <- as.integer(recode(victims$victimRole, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "6" = 6, "-" = 0, .missing = NULL, .default = 999))
victims$victimRole[which(victims$victimRole == 999)] <- NA

# Label the victim role
val_labels(victims$victimRole) <- cb$victimRole$labels[cb$victimRole$labels %in% unique(victims$victimRole)]


## 11.2. Victim Sex ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the victim sex to numeric
victims$victimSex <- as.integer(recode(victims$victimSex, "M" = 1, "F" = 2, "X" = 3, "-" = 0, .missing = NULL, .default = 999))
victims$victimSex[which(victims$victimSex == 999)] <- NA

# Label the victim sex
val_labels(victims$victimSex) <- cb$victimSex$labels[cb$victimSex$labels %in% unique(victims$victimSex)]


## 11.3. Victim Age ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

victims$victimAge[which(victims$victimAge >= 998)] <- NA

# Create a new column victimAgeGroup and set it to NA
victims$victimAgeGroup <- as.integer(NA)

# Group the victim age into age groups
victims$victimAgeGroup[which(victims$victimAge >= 0 & victims$victimAge <= 10)] <- 1
victims$victimAgeGroup[which(victims$victimAge > 10 & victims$victimAge <= 18)] <- 2
victims$victimAgeGroup[which(victims$victimAge > 18 & victims$victimAge <= 25)] <- 3
victims$victimAgeGroup[which(victims$victimAge > 25 & victims$victimAge <= 35)] <- 4
victims$victimAgeGroup[which(victims$victimAge > 35 & victims$victimAge <= 45)] <- 5
victims$victimAgeGroup[which(victims$victimAge > 45 & victims$victimAge <= 55)] <- 6
victims$victimAgeGroup[which(victims$victimAge > 55 & victims$victimAge <= 65)] <- 7
victims$victimAgeGroup[which(victims$victimAge > 65 & victims$victimAge <= 80)] <- 8
victims$victimAgeGroup[which(victims$victimAge > 80 & victims$victimAge <= 100)] <- 9
victims$victimAgeGroup[which(victims$victimAge > 100 & victims$victimAge <= 125)] <- 10
victims$victimAgeGroup[which(victims$victimAge >= 125)] <- 0
victims$victimAgeGroup[which(victims$victimAge >= 998)] <- NA

# Convert to integer
victims$victimAgeGroup <- as.integer(victims$victimAgeGroup)

# Label the victim age group
val_labels(victims$victimAgeGroup) <- cb$victimAgeGroup$labels[cb$victimAgeGroup$labels %in% unique(victims$victimAgeGroup)]

# order the victimAgeGroup column after the victimAge column
victims <- victims %>% relocate(victimAgeGroup, .after = victimAge)


## 11.4. Victim Degree of Injury ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the victim degree of injury to numeric
victims$victimDegreeOfInjury <- as.integer(recode(victims$victimDegreeOfInjury, "0" = 0, "4" = 1, "7" = 2, "6" = 3, "3" = 4, "5" = 5, "2" = 6, "1" = 7, "-" = 9, .missing = NULL, .default = 999))
victims$victimDegreeOfInjury[which(victims$victimDegreeOfInjury == 999)] <- NA

# Label the victim degree of injury
val_labels(victims$victimDegreeOfInjury) <- cb$victimDegreeOfInjury$labels[cb$victimDegreeOfInjury$labels %in% unique(victims$victimDegreeOfInjury)]

# Create a binary variable for the victim degree of injury
victims$victimDegreeOfInjuryBin <- as.integer(
    ifelse(
        victims$victimDegreeOfInjury %in% c(0, 1, 2, 3), 0,
        ifelse(
            victims$victimDegreeOfInjury %in% c(4, 5, 6, 7), 1, NA
        )
    )
)

# Label the victim degree of injury binary
val_labels(victims$victimDegreeOfInjuryBin) <- cb$victimDegreeOfInjuryBin$labels[cb$victimDegreeOfInjuryBin$labels %in% unique(victims$victimDegreeOfInjuryBin)]

# order the victimDegreeOfInjuryBin column after the victimDegreeOfInjury column
victims <- victims %>% relocate(victimDegreeOfInjuryBin, .after = victimDegreeOfInjury)


## 11.5. Victim Seating Position ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the victim seating position to numeric
victims$victimSeatingPosition <- as.integer(recode(victims$victimSeatingPosition, "1" = 1, "2" = 2, "3" = 3, "4" = 4, "5" = 5, "6" = 6, "7" = 7, "8" = 8, "9" = 9, "0" = 9, "A" = 10, "B" = 11, "C" = 12, "D" = 13, "E" = 14, "F" = 15, "G" = 16, "H" = 17, "I" = 18, "J" = 19, "K" = 20, "L" = 21, "M" = 22, "N" = 23, "O" = 24, "P" = 25, "Q" = 26, "R" = 27, "S" = 28, "T" = 29, "U" = 39, "V" = 31, "W" = 32, "X" = 33, "Y" = 34, "Z" = 35, "-" = 99, .missing = NULL, .default = 999))
victims$victimSeatingPosition[which(victims$victimSeatingPosition == 999)] <- NA

# Label the victim seating position
val_labels(victims$victimSeatingPosition) <- cb$victimSeatingPosition$labels[cb$victimSeatingPosition$labels %in% unique(victims$victimSeatingPosition)]


## 11.6. Victim Safety Equipment ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Victim Safety Equipment 1 ####

# Recode the victim safety equipment 1 to numeric
victims$victimSafetyEq1 <- as.integer(recode(victims$victimSafetyEq1, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "J" = 9, "K" = 10, "L" = 11, "M" = 12, "N" = 13, "P" = 14, "Q" = 15, "R" = 16, "S" = 17, "T" = 18, "U" = 19, "V" = 20, "W" = 21, "X" = 22, "Y" = 23, "-" = 0, .missing = NULL, .default = 999))
victims$victimDegreeOfInjury[which(victims$victimDegreeOfInjury == 999)] <- NA

# Label the victim safety equipment 1
val_labels(victims$victimSafetyEq1) <- cb$victimSafetyEq1$labels[cb$victimSafetyEq1$labels %in% unique(victims$victimSafetyEq1)]


### Victim Safety Equipment 2 ####

# Recode the victim safety equipment 2 to numeric
victims$victimSafetyEq2 <- as.integer(recode(victims$victimSafetyEq2, "A" = 1, "B" = 2, "C" = 3, "D" = 4, "E" = 5, "F" = 6, "G" = 7, "H" = 8, "J" = 9, "K" = 10, "L" = 11, "M" = 12, "N" = 13, "P" = 14, "Q" = 15, "R" = 16, "S" = 17, "T" = 18, "U" = 19, "V" = 20, "W" = 21, "X" = 22, "Y" = 23, "-" = 0, .missing = NULL, .default = 999))
victims$victimSafetyEq2[which(victims$victimSafetyEq2 == 999)] <- NA

# Label the victim safety equipment 2
val_labels(victims$victimSafetyEq2) <- cb$victimSafetyEq2$labels[cb$victimSafetyEq2$labels %in% unique(victims$victimSafetyEq2)]


## 11.7. Victim Ejected ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recode the victim ejected to numeric
victims$victimEjected <- as.integer(recode(victims$victimEjected, "0" = 0, "1" = 1, "2" = 2, "3" = 3, "-" = 9, .missing = NULL, .default = 999))
victims$victimEjected[which(victims$victimEjected == 999)] <- NA

# Label the victim ejected
val_labels(victims$victimEjected) <- cb$victimEjected$labels[cb$victimEjected$labels %in% unique(victims$victimEjected)]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 12. City Characteristics ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a new double variable in the cities data frame that divides the travel time by the number of vehicles
cities$cityMeanTravelTime <- as.double(cities$cityTravelTime / cities$cityVehicles)

# order the cityMeanTravelTime column after the cityTravelTime column
cities <- cities %>% relocate(cityMeanTravelTime, .after = cityTravelTime)

# Save the cleaned datasets
#saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 13. Add Column Attributes ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add column attributes to the crashes data frame
crashes <- addAttributes(crashes, cb)

# Add column attributes to the parties data frame
parties <- addAttributes(parties, cb)

# Add column attributes to the victims data frame
victims <- addAttributes(victims, cb)

# Add column attributes to the cities data frame
cities <- addAttributes(cities, cb)

# Add column attributes to the roads data frame
roads <- addAttributes(roads, cb)

# Save the cleaned datasets
#saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 14. Merge Datasets ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 14.1. Preparing Roads Dataset for Merging ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a table of road categories by city (contains counts for each category)
t1 <- table("city" = roads$placeName, roads$roadCat, exclude = "")
# remove if the city column in t1 is NA
t1 <- t1[!is.na(rownames(t1)), ]

# Convert the table to a data frame
roadsAggr <- as.data.frame.matrix(t1)

# Add the city column to the data frame from the matrix row names
roadsAggr$city <- rownames(roadsAggr)

# Aggregate the roads dataset by city and calculate the mean road length across all road lengths in each city
t2 <- aggregate.data.frame(roads$roadLength[roads$placeName != ""], by = list("city" = roads$placeName[roads$placeName != ""]), FUN = mean, simplify = TRUE)

# Aggregate the roads dataset by city and calculate the sum of all road lengths in each city
t3 <- aggregate.data.frame(roads$roadLength[roads$placeName != ""], by = list("city" = roads$placeName[roads$placeName != ""]), FUN = sum, simplify = TRUE)

# Add the mean road length column to the aggregated roads data frame
roadsAggr$roadLengthMean <- t2$x

# Add the sum of road lengths column to the aggregated roads data frame
roadsAggr$roadLengthSum <- t3$x

# Reorder the aggregated roads data frame
roadsAggr <- roadsAggr[c("city", "Primary", "Secondary", "Local", "roadLengthMean", "roadLengthSum")]

# Rename the columns of the aggregated roads data frame
colnames(roadsAggr)[colnames(roadsAggr) == "city"] <- "placeName"
colnames(roadsAggr)[colnames(roadsAggr) == "Primary"] <- "roadsPrimary"
colnames(roadsAggr)[colnames(roadsAggr) == "Secondary"] <- "roadsSecondary"
colnames(roadsAggr)[colnames(roadsAggr) == "Local"] <- "roadsLocal"

# Add the aggregated roads data frame to the original roads data frame
roads <- merge(roads, roadsAggr, by = "placeName", all.x = TRUE, suffixes = c(".roads", ".aggr"), no.dups = TRUE)

# Convert the columns to the correct data types
roads$roadsPrimary <- as.integer(roads$roadsPrimary)
roads$roadsSecondary <- as.integer(roads$roadsSecondary)
roads$roadsLocal <- as.integer(roads$roadsLocal)
roads$roadLengthMean <- as.double(roads$roadLengthMean)
roads$roadLengthSum <- as.double(roads$roadLengthSum)

# Rename the columns of the roads data frame back to city
colnames(roadsAggr)[colnames(roadsAggr) == "placeName"] <- "city"

# Now the roadsAggr data frame is ready for merging


## 14.2. Merging Datasets ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Merge the three datasets ####

# First, merge the crashes and parties datasets based on the Case ID and CID columns (outer join)
temp1 <- merge(crashes, parties, by = c("caseId", "cid"), all = TRUE, suffixes = c(".crashes", ".parties"), no.dups = TRUE)

# Secondly, merge the temp dataset with the victims dataset based on the Case ID, CID, PID and Party Number columns (outer join)
temp2 <- merge(temp1, victims, by = c("caseId", "cid", "pid", "partyNumber"), all = TRUE, suffixes = c(".join1", ".victims"), no.dups = TRUE)

# Thirdly, merge the temp2 dataset with the cities dataset based on the City column (inner left join)
temp3 <- merge(temp2, cities, by = "city", all.x = TRUE, suffixes = c(".join2", ".cities"), no.dups = TRUE)

# The final merge, contains the combined collisions data frame
collisions <- merge(temp3, roadsAggr, by = "city", all.x = TRUE, suffixes = c(".join3", ".roads"), no.dups = TRUE)

# We can now remove all the temporary datasets (except of the aggregated roads data frame)
rm(t1, t2, t3, temp1, temp2, temp3, roadsAggr)

### Add date and time variables to the parties and victims datasets ####

# Add date and time variables from the crashes data frame to the parties data frame on the CID column
parties <- merge(parties, select(crashes, cid, dateDatetime, dateYear, dateQuarter, dateMonth, dateWeek, dateDay, dateProcess, dtYear, dtQuarter, dtMonth, dtYearWeek, dtWeekDay, dtMonthDay, dtYearDay, dtHour, dtMinute, dtDst, dtZone, collDate, collTime, accidentYear, processDate, collSeverity, collSeverityNum, collSeverityRank, collSeverityRankNum), by = "cid", all.x = TRUE, suffixes = c(".parties", ".crashes"), no.dups = TRUE)

# Reorder the columns of the parties data frame by the order they appear in the codebook
parties <- parties[names(cb)[names(cb) %in% names(parties)]]

# Add date and time variables from the crashes data frame to the victims data frame on the CID column
victims <- merge(victims, select(crashes, cid, dateDatetime, dateYear, dateQuarter, dateMonth, dateWeek, dateDay, dateProcess, dtYear, dtQuarter, dtMonth, dtYearWeek, dtWeekDay, dtMonthDay, dtYearDay, dtHour, dtMinute, dtDst, dtZone, collDate, collTime, accidentYear, processDate, collSeverity, collSeverityNum, collSeverityRank, collSeverityRankNum), by = "cid", all.x = TRUE, suffixes = c(".victims", ".crashes"), no.dups = TRUE)

# Reorder the columns of the victims data frame by the order they appear in the codebook
victims <- victims[names(cb)[names(cb) %in% names(victims)]]


## 14.3. Formatting and Ordering the Collisions Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Convert the columns to the correct data types
collisions$roadLengthMean <- as.double(collisions$roadLengthMean)
collisions$roadLengthSum <- as.double(collisions$roadLengthSum)

### Reorder the Columns of the Collisions Data Frame ####

# Reorder the columns of the collisions data frame by the order they appear in the codebook
collisions <- collisions[names(cb)[names(cb) %in% names(collisions)]]


## 14.4. Update the tag variables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# First, sort the collisions data frame by CID, PID and VID
collisions <- collisions[order(collisions$cid, collisions$pid, collisions$vid), ]

# Replace the crashTag column with 1 if it is the first occurrence of a CID, otherwise 0
collisions$crashTag <- +(!duplicated(collisions$cid))

# Replace the partyTag column with 1 if it is the first occurrence of a PID, otherwise 0
collisions$partyTag <- +(!duplicated(collisions$pid))

# Replace the victimTag column with 1 if it is the first occurrence of a VID, otherwise 0
collisions$victimTag <- +(!duplicated(collisions$vid))


## 14.5. Create Combined Indicator Column ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a combined indicator column that combines the crashTag, partyTag and victimTag columns
collisions$combinedInd <- as.integer((collisions$crashTag * 100) + (collisions$partyTag * 10) + collisions$victimTag)

# Recode the combined indicator column to numeric
collisions$combinedInd <- as.integer(recode(collisions$combinedInd, "100" = 1, "10" = 2, "1" = 3, "11" = 4, "101" = 5, "110" = 6, "111" = 7, .missing = NULL, .default = 999))
collisions$combinedInd[which(collisions$combinedInd == 999)] <- NA

# Label the combined indicator column
val_labels(collisions$combinedInd) <- cb$combinedInd$labels[cb$combinedInd$labels %in% unique(collisions$combinedInd)]

# order the combinedInd column after the victimTag column
collisions <- collisions %>% relocate(combinedInd, .after = victimTag)

# remove the geometry from the collisions data frame
#collisions <- collisions %>% select(-geometry)


## 14.6. Add Column Attributes to the Merged Dataset ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add column attributes to the collisions data frame
collisions <- addAttributes(collisions, cb)


# Reorder the columns of the datasets by the order they appear in the codebook
crashes <- crashes[names(cb)[names(cb) %in% names(crashes)]]
parties <- parties[names(cb)[names(cb) %in% names(parties)]]
victims <- victims[names(cb)[names(cb) %in% names(victims)]]
collisions <- collisions[names(cb)[names(cb) %in% names(collisions)]]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 15. Spatial Operations ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 15.1. Add X and Y Coordinates ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# add pointX and pointY from crashes to the parties database by matching cid
parties <- left_join(parties, select(crashes, cid, pointX, pointY), by = "cid")

# add pointX and pointY from crashes to the victims database by matching cid
victims <- left_join(victims, select(crashes, cid, pointX, pointY), by = "cid")


## 15.2. Convert to spatial data frames ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Select cases within OC boundaries ####

# Minimum Confined Coordinates for Orange County
ocBoundingCoor <- list(
    xmin = -118.11978472,
    xmax = -117.41283672,
    ymin = 33.38712529,
    ymax = 33.94763946
)

# Select crashes within the bounding coordinates of Orange County
crashes <- crashes %>%
    filter(
        pointX >= ocBoundingCoor$xmin,
        pointX <= ocBoundingCoor$xmax,
        pointY >= ocBoundingCoor$ymin,
        pointY <= ocBoundingCoor$ymax
    )

# Select parties within the bounding coordinates of Orange County
parties <- parties %>%
    filter(
        pointX >= ocBoundingCoor$xmin,
        pointX <= ocBoundingCoor$xmax,
        pointY >= ocBoundingCoor$ymin,
        pointY <= ocBoundingCoor$ymax
    )

# Select victims within the bounding coordinates of Orange County
victims <- victims %>%
    filter(
        pointX >= ocBoundingCoor$xmin,
        pointX <= ocBoundingCoor$xmax,
        pointY >= ocBoundingCoor$ymin,
        pointY <= ocBoundingCoor$ymax
    )

# Select collisions within the bounding coordinates of Orange County
collisions <- collisions %>%
    filter(
        pointX >= ocBoundingCoor$xmin,
        pointX <= ocBoundingCoor$xmax,
        pointY >= ocBoundingCoor$ymin,
        pointY <= ocBoundingCoor$ymax
    )


### Convert to spatial data frames ####

# Create an sf object from the filtered crashes data frame (originally set as WGS 1984, EPSG: 4326)
crashes <- st_as_sf(crashes, coords = c("pointX", "pointY"), remove = FALSE, crs = 4326)

# Create an sf object from the filtered parties data frame
parties <- st_as_sf(parties, coords = c("pointX", "pointY"), remove = FALSE, crs = 4326)

# Create an sf object from the filtered victims data frame
victims <- st_as_sf(victims, coords = c("pointX", "pointY"), remove = FALSE, crs = 4326)

# Create an sf object from the filtered collisions data frame
collisions <- st_as_sf(collisions, coords = c("pointX", "pointY"), remove = FALSE, crs = 4326)

# Convert the Coordinate Reference System (CRS) of the sf object to WGS 1984 Web Mercator (Auxiliary Sphere) (EPSG: 3857) - See more: https://epsg.io/3857
crashes <- st_transform(crashes, 3857)
parties <- st_transform(parties, 3857)
victims <- st_transform(victims, 3857)
collisions <- st_transform(collisions, 3857)


# Display the Coordinate Reference System (CRS) of the sf object
st_crs(crashes)$proj4string
st_crs(parties)$proj4string
st_crs(victims)$proj4string
st_crs(cities)$proj4string
st_crs(roads)$proj4string
st_crs(boundaries)$proj4string


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 16. Wrapping Up ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 16.1. Sort the Dataframes by Datetime ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Sort the rows of the crashes data frame by the cid column
crashes <- crashes[order(crashes$cid), ]
crashes <- addAttributes(crashes, cb)

# Sort the rows of the parties data frame by the cid and pid columns
parties <- parties[order(parties$cid, parties$pid), ]
parties <- addAttributes(parties, cb)

# Sort the rows of the victims data frame by the cid, pid and vid columns
victims <- victims[order(victims$cid, victims$pid, victims$vid), ]
victims <- addAttributes(victims, cb)

# Sort the rows of the collisions data frame by the cid, pid and vid columns
collisions <- collisions[order(collisions$cid, collisions$pid, collisions$vid), ]
collisions <- addAttributes(collisions, cb)

# Sort the rows of the cities data frame by the city column
cities <- cities[order(cities$city), ]
cities <- addAttributes(cities, cb)

# Sort the rows of the roads data frame by the rid column
roads <- roads[order(roads$roadId), ]
roads <- addAttributes(roads, cb)


## 16.2. Collisions data frame label ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#collisions <- add_frame_lab(collisions, frame.lab = "OCSWITRS Collisions Dataset")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 17. Export to ArcGIS ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


## 17.1. Crashes Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the crashes spatial data frame to a new object
crashes.agp <- crashes

# Convert the date columns to datetime
crashes.agp$dateDatetime <- as.POSIXct(crashes.agp$dateDatetime, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateYear <- as.POSIXct(crashes.agp$dateYear, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateQuarter <- as.POSIXct(crashes.agp$dateQuarter, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateMonth <- as.POSIXct(crashes.agp$dateMonth, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateWeek <- as.POSIXct(crashes.agp$dateWeek, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateDay <- as.POSIXct(crashes.agp$dateDay, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
crashes.agp$dateProcess <- as.POSIXct(crashes.agp$dateProcess, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

# Convert all the variables that have value labels to factors
for (var in names(crashes.agp)) {
    if (is.labelled(crashes.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        crashes.agp[[var]] <- as_factor(crashes.agp[[var]])
    }
}

# Write the crashes spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "RawData", "crashes"), crashes.agp, overwrite = TRUE)


## 17.2. Parties Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the parties spatial data frame to a new object
parties.agp <- parties

# Convert the date columns to POSIXct
parties.agp$dateDatetime <- as.POSIXct(parties.agp$dateDatetime, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateYear <- as.POSIXct(parties.agp$dateYear, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateQuarter <- as.POSIXct(parties.agp$dateQuarter, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateMonth <- as.POSIXct(parties.agp$dateMonth, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateWeek <- as.POSIXct(parties.agp$dateWeek, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateDay <- as.POSIXct(parties.agp$dateDay, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
parties.agp$dateProcess <- as.POSIXct(parties.agp$dateProcess, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

# Convert all the variables that have value labels to factors
for (var in names(parties.agp)) {
    if (is.labelled(parties.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        parties.agp[[var]] <- as_factor(parties.agp[[var]])
    }
}

# Write the parties spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "RawData", "parties"), parties.agp, overwrite = TRUE)


## 17.3. Victims Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the victims spatial data frame to a new object
victims.agp <- victims

# Convert the date columns to POSIXct
victims.agp$dateDatetime <- as.POSIXct(victims.agp$dateDatetime, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateYear <- as.POSIXct(victims.agp$dateYear, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateQuarter <- as.POSIXct(victims.agp$dateQuarter, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateMonth <- as.POSIXct(victims.agp$dateMonth, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateWeek <- as.POSIXct(victims.agp$dateWeek, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateDay <- as.POSIXct(victims.agp$dateDay, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
victims.agp$dateProcess <- as.POSIXct(victims.agp$dateProcess, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

# Convert all the variables that have value labels to factors
for (var in names(victims.agp)) {
    if (is.labelled(victims.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        victims.agp[[var]] <- as_factor(victims.agp[[var]])
    }
}

# Write the victims spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "RawData", "victims"), victims.agp, overwrite = TRUE)


## 17.4. Collisions Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the collisions spatial data frame to a new object
collisions.agp <- collisions

# Convert the date columns to POSIXct
collisions.agp$dateDatetime <- as.POSIXct(collisions.agp$dateDatetime, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateYear <- as.POSIXct(collisions.agp$dateYear, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateQuarter <- as.POSIXct(collisions.agp$dateQuarter, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateMonth <- as.POSIXct(collisions.agp$dateMonth, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateWeek <- as.POSIXct(collisions.agp$dateWeek, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateDay <- as.POSIXct(collisions.agp$dateDay, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
collisions.agp$dateProcess <- as.POSIXct(collisions.agp$dateProcess, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")

# Convert all the variables that have value labels to factors
for (var in names(collisions.agp)) {
    if (is.labelled(collisions.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        collisions.agp[[var]] <- as_factor(collisions.agp[[var]])
    }
}

# Write the collisions spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "RawData", "collisions"), collisions.agp, overwrite = TRUE)


## 17.5. Cities Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the cities spatial data frame to a new object
cities.agp <- cities

# Convert all the variables that have value labels to factors
for (var in names(cities.agp)) {
    if (is.labelled(cities.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        cities.agp[[var]] <- as_factor(cities.agp[[var]])
    }
}

# Write the cities spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "cities"), cities.agp, validate = TRUE, overwrite = TRUE)


## 17.6. Roads Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the roads spatial data frame to a new object
roads.agp <- roads

# Convert all the variables that have value labels to factors
for (var in names(roads.agp)) {
    if (is.labelled(roads.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        roads.agp[[var]] <- as_factor(roads.agp[[var]])
    }
}

# Write the roads spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "roads"), roads.agp, validate = TRUE, overwrite = TRUE)


## 17.7. Boundaries Spatial Data Frame ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Copy the boundaries spatial data frame to a new object
boundaries.agp <- boundaries

# Convert all the variables that have value labels to factors
for (var in names(boundaries.agp)) {
    if (is.labelled(boundaries.agp[[var]])) {
        cat("Variable", var, "is labelled\n")
        boundaries.agp[[var]] <- as_factor(boundaries.agp[[var]])
    }
}

# Write the boundaries spatial data frame to the ArcGIS Pro project geodatabase
arc.write(file.path(prjDirs$agpPath, "AGPSWITRS.gdb", "SupportingData", "boundaries"), boundaries.agp, validate = TRUE, overwrite = TRUE)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 18. Save to Disk ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Save the cleaned datasets
saveToDisk()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
