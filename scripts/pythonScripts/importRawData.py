#############################################
#   SWITRS DATA PROCESSING PROJECT          #
#   Part 1: Pandas Dataframe Operations     #
#   version 4.0, August 2024                #
#############################################


### REFERENCING LIBRARIES AND INITIALIZATION ###

# Instantiating the Python environment libraries, define temporal and project paths and variables


# PRELIMINARIES ----------------------------------------------------------------------------------------------------

# Python libraries and paths
import os, json, pytz, math, arcpy
from datetime import date, time, datetime, timedelta, tzinfo, timezone
import pandas as pd
import numpy as np
from pandas.api.types import infer_dtype, is_numeric_dtype, is_object_dtype, is_float_dtype, is_integer_dtype, is_string_dtype, is_datetime64_any_dtype, is_complex_dtype, is_interval_dtype, is_sparse, is_integer, is_any_real_numeric_dtype


# DATE AND TIME FUNCTION --------------------------------------------------------------------------------------------

# Setup a function to update times and display start and end information. Options:
# - 'default': last update with full datetime
# - 'data': last data update with date only
# - 'start': start with full datetime
# - 'end': end with full datetime adn time elapsed
# - 'today': today's date with full datetime
# - 'save': save with full datetime
# - 'load': load with full datetime

def update_datetime(purpose="default"):
    """Function update date and time aspects of the project
    Args:
        purpose (str): purpose of the update. Options are 'default', 'data', 'start', 'end', 'today', 'save', 'load'
    """
    global today, lastUpdateDate, lastUpdateTime, startTime, endTime, startDate, timeZone
    
    # Define time and date variables
    timeZone = pytz.timezone('America/Los_Angeles')
    today = datetime.now(timezone)
    lastUpdateDate = today.strftime("%B %d,%Y")
    lastUpdateDatetime = today.strftime("%A %B %d, %Y %I:%M %p (%Z)")
    
    # Match the purpose of the function (user input)
    match purpose:
        case "default":
            print(f"Last update: {lastUpdateDatetime}")
        case "data":
            print(f"Data last updated on: {lastUpdateDate}")
        case "start":
            startTime = datetime.now(timeZone)
            print(f"Start: {lastUpdateDatetime}")
        case "end":
            endTime = datetime.now(timeZone)
            delta = endTime - startTime
            elasped = delta - timedelta(microseconds=delta.microseconds)
            print(f"End: {lastUpdateDatetime}. Elapsed time: {elasped}")
        case "today":
            print(f"Today's date: {lastUpdateDatetime}")
        case "save":
            print(f"Project saved on: {lastUpdateDatetime}")
        case "load":
            print(f"Project loaded on: {lastUpdateDatetime}")


# PROJECT AND WORKSPACE VARIABLES -----------------------------------------------------------------------------------

# Define and maintain project, workspace, and data-related variables

# Current ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Current ArcGIS Map
mp = aprx.listMaps()[0]

# Workspace project path directories and paths to data files

# Current ArcGIS Pro project path
project = "OCSWITRS.aprx"

# Current ArcGIS Pro workspace
workspace = arcpy.workspace

# Current project path directory and geodatabase variables
path, gdb = os.path.split(arcpy.env.workspace)
pathProject = os.path.join(path, project)

# On the project folder directory
pathRawData = os.path.join(path, "RawData")
pathLayers = os.path.join(path, "Layers")
pathNotebooks = os.path.join(path, "Notebooks")

# On the project geodatabase
pathSupportingData = os.path.join(workspace, "SupportingData")

# Paths to raw data (crashes, parties, and victims)
pathRawCrashes = os.path.join(pathRawData, "Crashes.csv")
pathRawParties = os.path.join(pathRawData, "Parties.csv")
pathRawVictims = os.path.join(pathRawData, "Victims.csv")

# Paths to supporting data feature classes
pathBoundaries = os.path.join(pathSupportingData, "OCSWITRS_Boundaries")
pathCities = os.path.join(pathSupportingData, "OCSWITRS_Cities")
pathRoads = os.path.join(pathSupportingData, "OCSWITRS_Roads")
pathLookup = os.path.join(pathSupportingData, "OCSWITRS_Lookup")

# Path to JSON Codebook
pathCodebook = os.path.join(pathRawData, "codebook.json")

# Display all information
print(f"Key Project Information:\n\t- Name: {project}\n\t- Path: {path}\n\t- Project Path: {pathProject}\n\t- Workspace: {workspace}\n\t- Geodatabase: {gdb}")
print(f"Project Directories:\n\t- Raw Data: {pathRawData}\n\t- Layers: {pathLayers}\n\t- Notebooks: {pathNotebooks}\n\t- Supporting Data: {pathSupportingData}")
print(f"Supporting Feature Classes:\n\t- Boundaries: {pathBoundaries}\n\t- Cities: {pathCities}\n\t- Roads: {pathRoads}\n\t- Lookup Data: {pathLookup}")
print(f"Other Supporting Data:\n\t- JSON Codebook: {pathCodebook}")










# Get the current computer name
computerName = os.environ['COMPUTERNAME']

# get the path of the project
#projectPath = os.path.join("C:\\Users", os.getlogin(), "Documents", "OCTraffic", "SWITRS")

# get the path to OneDrive-County of Orange folder
oneDrivePath = os.path.join("C:\\Users", os.getlogin(), "OneDrive - County of Orange")
projectPath = os.path.join(oneDrivePath, "Projects", "OCTraffic", "SWITRS")

# get the path to metadata json dictionary
metadataJson = os.path.join(projectPath, "Metadata", "SwitrsCoverage.json")

# read the json file SwitrsCoverage.json and save it into a python dictionary
with open(metadataJson, 'r') as f:
    metadata = json.load(f)

# Get the path for each of the Raw Data files
crashesPath = os.path.join(projectPath, "RawData", "Crashes.csv")
partiesPath = os.path.join(projectPath, "RawData", "Parties.csv")
victimsPath = os.path.join(projectPath, "RawData", "Victims.csv")


