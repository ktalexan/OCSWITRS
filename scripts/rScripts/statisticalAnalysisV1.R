##########################################
# OCSWITRS Statistical Analysis          #
# Version 1                              #
##########################################

# Load the pandas pickle data from the file
# using the reticulate package


# --------------------------------------
# PART 1 - PRELIMINARIES AND DATA IMPORT
# --------------------------------------

# Load the reticulate package
library(reticulate)
library(here)

# Import pandas
pd <- import("pandas")

# Path of the pandas pickle file(s)
collisionsPicklePath <- file.path(here(), "Data", "Python", "dfCollisions.pkl")
crashesPicklePath <- file.path(here(), "Data", "Python", "dfCrashes.pkl")
partiesPicklePath <- file.path(here(), "Data", "Python", "dfParties.pkl")
victimsPicklePath <- file.path(here(), "Data", "Python", "dfVictims.pkl")


# Load the collision pandas pickle data from the file
dfCollisions <- pd$read_pickle(collisionsPicklePath)

# Load the crashes pandas pickle data from the file
dfCrashes <- pd$read_pickle(crashesPath)

# Load the parties pandas pickle data from the file
dfParties <- pd$read_pickle(partiesPath)

# Load the victims pandas pickle data from the file
dfVictims <- pd$read_pickle(victimsPath)

# load the dplyr library
library(dplyr)

# :oad the ggplot library
library(ggplot2)

# --------------------------------------
# PART 2 - BASIC STATISTICAL ANALYSIS
# --------------------------------------

dfCollisions %>%
    summarise(
        n = n(),
        nUnique = n_distinct(CaseId),
        nUniqueCrashes = n_distinct(CID),
        nUniqueParties = n_distinct(PID),
        nUniqueVictims = n_distinct(VID),
        meanParties = mean(PARTY_NUMBER),
        meanVictims = mean(VICTIM_NUMBER)
    )



dfCollisions %>%
    group_by(CITY_NAME) %>%
    summarise(Mean = mean(PARTY_NUMBER)) %>%
    ggplot(aes(x=reorder(CITY_NAME, -Mean), y=Mean, fill=CITY_NAME)) +
    geom_bar(stat="identity") +
    theme(axis.text.x=element_text(angle=90)) +
    labs(
        x = "City",
        y = "Average Number of Parties",
        title = paste("Average Number of Parties by City (n=",nrow(dfCollisions),")"
      )
    )


dfCollisions %>%
    group_by(CITY_NAME) %>%
    summarise(Mean = mean(VICTIM_NUMBER)) %>%
    ggplot(aes(x=reorder(CITY_NAME, -Mean), y=Mean, fill=CITY_NAME)) +
    geom_bar(stat="identity") +
    theme(axis.text.x=element_text(angle=90)) +
    labs(
        x = "City",
        y = "Average Number of Victims",
        title = paste("Average Number of Victims by City (n=",nrow(dfCollisions),")"
        )
    )



dfCollisions %>%
    group_by(WEATHER_1) %>%
    summarise(Mean = mean(VICTIM_NUMBER)) %>%
    ggplot(aes(x=reorder(WEATHER_1, -Mean), y=Mean, fill=WEATHER_1)) +
    geom_bar(stat="identity") +
    theme(axis.text.x=element_text(angle=90)) +
    labs(
        x = "Weather Condition",
        y = "Average Number of Victims",
        title = paste("Average Number of Victims by Weather Condition (n=",nrow(dfCollisions),")"
        )
    )


dfCollisions %>%
    filter(dfCollisions$VICTIM_AGE <= 100) %>%
    summary(dfCollisions$VICTIM_AGE)
