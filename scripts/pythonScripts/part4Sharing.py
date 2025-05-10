# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OC SWITRS GIS Data Processing
# Part 4 - Sharing ArcGIS Online
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOC SWITRS GIS Data Processing - Part 4 - Sharing ArcGIS Online\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1. Preliminaries
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Preliminaries")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.1. Referencing Libraries and Initialization
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.1. Referencing Libraries and Initialization")

# Instantiating python libraries for the project

# %%
# Import Python libraries
import os, json, pytz, math, arcpy, arcgis
from datetime import date, time, datetime, timedelta, tzinfo, timezone
from arcpy import metadata as md
from dotenv import load_dotenv

# important as it "enhances" Pandas by importing these classes (from ArcGIS API for Python)
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">1.2. Project and Workspace Variables</h2>

# %% [markdown]
# Define and maintain project, workspace, ArcGIS, and data-related variables

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Project and Geodatabase Paths</h3>

# %% [markdown]
# Define the ArcGIS pro project variables

# %%
# Current notebook directory
notebookDir = os.getcwd()

# Define the project folder (parent directory of the current working directory)
projectFolder = os.path.dirname(os.getcwd())

# %% [markdown]
# Which running environment this notebook is using? (1 = Visual Studio Code, 2 = ArcGIS Pro)

# %%
runEnv = input("Enter the running environment (1=VSCode, 2=ArcGIS Pro): ")

# %% [markdown]
# Load environment variables from the .env file

# %%
# Load environment variables from .env file
load_dotenv()

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">ArcGIS Pro Paths</h3>

# %% [markdown]
# ArcGIS pro related paths

# %%
# OCSWITRS project AGP path
agpFolder = os.path.join(projectFolder, "AGPSWITRS")

# AGP APRX file name and path
aprxName = "AGPSWITRS.aprx"
aprxPath = os.path.join(agpFolder, aprxName)

# ArcGIS Pro project geodatabase and path
gdbName = "AGPSWITRS.gdb"
gdbPath = os.path.join(agpFolder, gdbName)

# ArcGIS pro project
if runEnv == "1":  # VSCode
    print("Running in VSCode (project = aprxPath)")
    aprxObj = aprxPath
elif runEnv == "2":  # ArcGIS Pro
    print("Running in ArcGIS Pro (project = CURRENT)")
    aprxObj = "CURRENT"

try:
    # Set the ArcGIS Pro project based on the environment
    # Use arcpy.mp.ArcGISProject() function to initialize the project
    aprx = arcpy.mp.ArcGISProject(aprxObj)

    # Close all map views
    aprx.closeViews()
except Exception as e:
    print(f"Error loading ArcGIS Project: {e}")

# Current ArcGIS workspace (arcpy)
arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace
# Enable overwriting existing outputs
arcpy.env.overwriteOutput = True
# Disable adding outputs to map
arcpy.env.addOutputsToMap = False

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Folder Paths</h3>

# %%
# Raw data folder path
rawDataFolder = os.path.join(projectFolder, "data", "raw")

# Maps folder path
mapsFolder = os.path.join(projectFolder, "maps")

# Layers folder path
layersFolder = os.path.join(projectFolder, "layers")
layersTemplate = os.path.join(layersFolder, "templates")

# Layouts folder path
layoutsFolder = os.path.join(projectFolder, "layouts")

# Notebooks folder path
notebooksFolder = os.path.join(projectFolder, "notebooks")
codebookPath = os.path.join(projectFolder, "scripts", "codebook", "cb.json")

# %% [markdown]
# Geodatabase feature datasets paths (directories)

# %%
# RawData feature dataset in the geodatabase
gdbRawData = os.path.join(gdbPath, "raw")

# RawData feature dataset in the geodatabase
gdbSupportingData = os.path.join(gdbPath, "supporting")

# AnalysisData feature dataset in the geodatabase
gdbAnalysisData = os.path.join(gdbPath, "analysis")

# HotSpotData feature dataset in the geodatabase
gdbHotspotData = os.path.join(gdbPath, "hotspots")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Data Folder Paths</h3>

# %% [markdown]
# The most current raw data files cover the periods from 01/01/2013 to 09/30/2024. The data files are already processed in the R scripts and imported into the project's geodatabase.

# %%
# Add the start date of the raw data to a new python datetime object
dateStart = datetime(2012, 1, 1)

# Add the end date of the raw data to a new python datetime object
dateEnd = datetime(2024, 12, 31)

# Define time and date variables
timeZone = pytz.timezone("US/Pacific")
today = datetime.now(timeZone)
dateUpdated = today.strftime("%B %d, %Y")
timeUpdated = today.strftime("%I:%M %p")

# %% [markdown]
# Define date strings for metadata

# %%
# String defining the years of the raw data
mdYears = f"{dateStart.year}-{dateEnd.year}"

# String defining the start and end dates of the raw data
mdDates = (
    f"Data from {dateStart.strftime('%B %d, %Y')} to {dateEnd.strftime('%B %d, %Y')}"
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Codebook</h3>

# %%
# Load the JSON file from directory and store it in a variable
with open(codebookPath) as jsonFile:
    codebook = json.load(jsonFile)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">1.3. ArcGIS Pro Workspace</h2>

# %% [markdown]
# Set the workspace and environment settings for the ArcGIS Pro project

# %%
# Set the workspace and environment to the root of the project geodatabase
arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace

# Current ArcGIS workspace (arcpy)
arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace

# Enable overwriting existing outputs
arcpy.env.overwriteOutput = True

# Disable adding outputs to map
arcpy.env.addOutputsToMap = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">1.4. Map and Layout Lists</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Project Maps</h3>

# %%
# List of maps to be created for the project
mapList = [
    "collisions",
    "crashes",
    "parties",
    "victims",
    "injuries",
    "fatalities",
    "fhs100m1km",
    "fhs150m2km",
    "fhs100m5km",
    "fhsRoads500ft",
    "ohsRoads500ft",
    "roadCrashes",
    "roadHotspots",
    "roadBuffers",
    "roadSegments",
    "roads",
    "pointFhs",
    "pointOhs",
    "popDens",
    "houDens",
    "areaCities",
    "areaBlocks",
    "summaries",
    "analysis",
    "regression",
]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Project Layouts</h3>

# %%
# List or layouts to be created for the project
layoutList = ["maps", "injuries", "hotspots", "roads", "points", "densities", "areas"]

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">3. ArcGIS Online Operations</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.1. Sign In</h2>

# %%
# Sign in to portal
arcpy.SignInToPortal(
    "https://www.arcgis.com", os.getenv("AGO_USERNAME"), os.getenv("AGO_PASSWORD")
)

# %%
# Get the portal description and key information
portalDesc = arcpy.GetPortalDescription()

# Print Basic Portal Information
print(f"Portal: {portalDesc['name']}")
print(f"User: {portalDesc['user']['fullName']} ({portalDesc['user']['username']})")

# %% [markdown]
# Path to store ArcGIS Online staging feature layers

# %%
agoPrjPath = os.path.join(projectFolder, "data", "ago")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.2. Maps and Feature Layers</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Collisions Map and Supporting Layers</h3>

# %% [markdown]
# Maps and Layers Definitions for the Collisions Map

# %%
collisionsMap = aprx.listMaps("collisions")[0]
collisionsLayer = collisionsMap.listLayers("OCSWITRS Collisions")[0]
roadsLayer = collisionsMap.listLayers("OCSWITRS Roads")[0]
blocksLayer = collisionsMap.listLayers("OCSWITRS Census Blocks")[0]
citiesLayer = collisionsMap.listLayers("OCSWITRS Cities")[0]
boundariesLayer = collisionsMap.listLayers("OCSWITRS Boundaries")[0]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Crashes Map and Layer</h3>

# %% [markdown]
# Crashes Map and layer definitions

# %%
crashesMap = aprx.listMaps("crashes")[0]
crashesLayer = crashesMap.listLayers("OCSWITRS Crashes")[0]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Parties Map and Layer</h3>

# %% [markdown]
# Parties map and layer definitions

# %%
partiesMap = aprx.listMaps("parties")[0]
partiesLayer = partiesMap.listLayers("OCSWITRS Parties")[0]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Victims Map and Layer</h3>

# %% [markdown]
# Victims map and layer definitions

# %%
victimsMap = aprx.listMaps("victims")[0]
victimsLayer = victimsMap.listLayers("OCSWITRS Victims")[0]

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.2. Sharing Supporting Layers</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Boundaries Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the Boundaries layer
serviceName = "OC Boundaries"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = collisionsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, boundariesLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the boundaries layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Cities Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the Cities layer
serviceName = "OCSWITRS Cities"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = collisionsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, citiesLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the boundaries layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Roads Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the Roads layer
serviceName = "OCSWITRS Roads"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = collisionsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, roadsLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the roads layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Census Blocks Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the Blocks layer
serviceName = "OCSWITRS Census Blocks"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = collisionsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, blocksLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the blocks layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.3. Sharing SWITRS Data Layers</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Crashes Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the crashes layer
serviceName = "OCSWITRS Crashes"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = crashesMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, crashesLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the crashes layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Parties Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definition variables for the parties layer
serviceName = "OCSWITRS Parties"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = partiesMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, partiesLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the parties layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Victims Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definitions variables for the victims layer
serviceName = "OCSWITRS Victims"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = victimsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, victimsLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the victims layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Collisions Service Layer</h3>

# %% [markdown]
# Service definition variables

# %%
# Provide the service definitions variables for the collisions layer
serviceName = "OCSWITRS Collisions"
serviceFolder = "OCTraffic"
serviceCredits = "Dr. Kostas Alexandridis, GISP"
sddraftFile = serviceName + ".sddraft"
sddraftOutput = os.path.join(agoPrjPath, sddraftFile)
sdFile = serviceName + ".sd"
sdOutput = os.path.join(agoPrjPath, sdFile)

# Define the server type
serverType = "HOSTING_SERVER"

# Create a feature service draft object
sddraft = collisionsMap.getWebLayerSharingDraft(
    serverType, "FEATURE", serviceName, collisionsLayer
)

# Set the properties of the feature service draft object
sddraft.overwriteExistingService = True
sddraft.portalFolder = serviceFolder
sddraft.credits = serviceCredits

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraftOutput)

# %% [markdown]
# Stage the service definition for the collisions layer

# %%
print("Start Staging")
arcpy.server.StageService(
    in_service_definition_draft=sddraftOutput, out_service_definition=sdOutput
)

# %% [markdown]
# Publish the service definition to ArcGIS Online portal (updating the existing service)

# %%
# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(
    in_sd_file=sdOutput,
    in_server=serverType,
    in_service_name=serviceName,
    in_folder_type="EXISTING",
    in_folder=serviceFolder,
    in_startupType="STARTED",
)

# %% [markdown]
#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region End of Script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nEnd of Script")
