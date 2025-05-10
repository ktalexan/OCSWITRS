# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OC SWITRS GIS Data Processing
# Part 3 - Map Layout Processing
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOC SWITRS GIS Data Processing - Part 3 - Map Layout Processing\n")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1. Preliminaries
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1. Preliminaries")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.1. Referencing Libraries and Initialization
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.1. Referencing Libraries and Initialization")

# Instantiating python libraries for the project

# Import Python libraries
import os, json, pytz, math, arcpy, arcgis
from datetime import date, time, datetime, timedelta, tzinfo, timezone
from arcpy import metadata as md
import numpy as np

# important as it "enhances" Pandas by importing these classes (from ArcGIS API for Python)
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# endregion


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.2. Project and Workspace Variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.2. Project and Workspace Variables")

# Define and maintain project, workspace, ArcGIS, and data-related variables


# region Project and Geodatabase Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project and Geodatabase Paths")

# Define the ArcGIS pro project variables

# Parent project Directory
projectFolder = os.path.dirname(os.getcwd())

# Current notebook directory
notebookDir = os.path.join(projectFolder, "notebooks")

# endregion


# region ArcGIS Pro Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- ArcGIS Pro Paths")

# ArcGIS pro related paths

# OCSWITRS project AGP path
agpFolder = os.path.join(projectFolder, "AGPSWITRS")

# AGP APRX file name and path
aprxName = "AGPSWITRS.aprx"
aprxPath = os.path.join(agpFolder, aprxName)

# ArcGIS Pro project geodatabase and path
gdbName = "AGPSWITRS.gdb"
gdbPath = os.path.join(agpFolder, gdbName)

# ArcGIS pro project
aprx = arcpy.mp.ArcGISProject(aprxPath)

# Close all map views
aprx.closeViews()

# Current ArcGIS workspace (arcpy)
arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace
# Enable overwriting existing outputs
arcpy.env.overwriteOutput = True
# Disable adding outputs to map
arcpy.env.addOutputsToMap = False

# endregion


# region Folder Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Folder Paths")

# Raw data folder path
rawDataFolder = os.path.join(projectFolder, "data", "raw")

# Maps folder path
mapsFolder = os.path.join(projectFolder, "maps")

# Layers folder path
layersFolder = os.path.join(projectFolder, "layers")
layersTemplates = os.path.join(layersFolder, "templates")

# Layouts folder path
layoutsFolder = os.path.join(projectFolder, "layouts")

# Notebooks folder path
notebooksFolder = os.path.join(projectFolder, "notebooks")
codebookPath = os.path.join(projectFolder, "scripts", "codebook", "cb.json")

# Analysis and Graphics folder path
analysisFolder = os.path.join(projectFolder, "analysis")
graphicsFolder = os.path.join(analysisFolder, "graphics")

# Geodatabase feature datasets paths (directories)

# RawData feature dataset in the geodatabase
gdbRawData = os.path.join(gdbPath, "raw")

# RawData feature dataset in the geodatabase
gdbSupportingData = os.path.join(gdbPath, "supporting")

# AnalysisData feature dataset in the geodatabase
gdbAnalysisData = os.path.join(gdbPath, "analysis")

# HotSpotData feature dataset in the geodatabase
gdbHotspotData = os.path.join(gdbPath, "hotspots")

# endregion


# region Data Folder Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Data Folder Paths")

# The most current raw data files cover the periods from 01/01/2013 to 09/30/2024. The data files are already processed in the R scripts and imported into the project's geodatabase.

# Add the start date of the raw data to a new python datetime object
dateStart = datetime(2012, 1, 1, 0, 0, 0)

# Add the end date of the raw data to a new python datetime object
dateEnd = datetime(2024, 12, 31, 23, 59, 59)

# Define time and date variables
timeZone = pytz.timezone("US/Pacific")
today = datetime.now(timeZone)
dateUpdated = today.strftime("%B %d, %Y")
timeUpdated = today.strftime("%I:%M %p")

# Define date strings for metadata

# String defining the years of the raw data
mdYears = f"{dateStart.year}-{dateEnd.year}"

# String defining the start and end dates of the raw data
mdDates = (
    f"Data from {dateStart.strftime('%B %d, %Y')} to {dateEnd.strftime('%B %d, %Y')}"
)

# endregion


# region Codebook
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Codebook")

# Load the JSON file from directory and store it in a variable
with open(codebookPath) as json_file:
    codebook = json.load(json_file)

# endregion


# region JSON CIM Exports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- JSON CIM Exports")

# Creating a function to export the CIM JSON files to disk.
def exportCim(cimType, cimObject, cimName):
    """Export a CIM object to a file in both native (MAPX, PAGX, LYRX) and JSON CIM formats."""
    match cimType:
        # When the CIM object is a map
        case "map":
            # Export the CIM object to a MAPX file
            print(f"Exporting {cimName} map to MAPX...")
            cimObject.exportToMAPX(os.path.join(mapsFolder, cimName + ".mapx"))
            print(arcpy.GetMessages())

            # Export the CIM object to a JSON file
            print(f"Exporting {cimName} map to JSON...\n")
            with open(os.path.join(mapsFolder, cimName + ".mapx"), "r") as f:
                data = f.read()
            with open(os.path.join(mapsFolder, cimName + ".json"), "w") as f:
                f.write(data)

        # When the CIM object is a layout
        case "layout":
            # Export the CIM object to a PAGX file
            print(f"Exporting {cimName} layout to PAGX...")
            cimObject.exportToPAGX(os.path.join(layoutsFolder, cimName + ".pagx"))
            print(arcpy.GetMessages())

            # Export the CIM object to a JSON file
            print(f"Exporting {cimName} layout to JSON...\n")
            with open(os.path.join(layoutsFolder, cimName + ".pagx"), "r") as f:
                data = f.read()
            with open(os.path.join(layoutsFolder, cimName + ".json"), "w") as f:
                f.write(data)

        # When the CIM object is a layer
        case "layer":
            # Export the CIM object to a LYRX file
            print(f"Exporting {cimName} layer to LYRX...")
            # Reformat the name of the output file
            for m in aprx.listMaps():
                for l in m.listLayers():
                    if l == cimObject:
                        cimNewName = (
                            m.name.title() + "Map-" + l.name.replace("OCSWITRS ", "")
                        )
            # Save the layer to a LYRX file
            arcpy.management.SaveToLayerFile(
                cimObject, os.path.join(layersFolder, cimNewName + ".lyrx")
            )
            print(arcpy.GetMessages())

            # Export the CIM object to a JSON file
            print(f"Exporting {cimName} layer to JSON...\n")
            with open(os.path.join(layersFolder, cimNewName + ".lyrx"), "r") as f:
                data = f.read()
            with open(os.path.join(layersFolder, cimNewName + ".json"), "w") as f:
                f.write(data)

# endregion
# endregion 1.2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.3. ArcGIS Pro Workspace
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.3. ArcGIS Pro Workspace")

# Set the workspace and environment settings for the ArcGIS Pro project

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

# endregion 1.3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.4. Map and Layout Lists
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.4. Map and Layout Lists")


# region Project Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project Maps")

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

# endregion


# region Project Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project Layouts")

# List or layouts to be created for the project
layoutList = ["maps", "injuries", "hotspots", "roads", "points", "density", "areas"]

# endregion
# endregion 1.4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.5. Feature Class Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.5. Feature Class Definitions")


# region Raw Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Raw Data Feature Classes")

# Define paths for the feature classes in the raw data feature dateset of the geodatabase
collisions = os.path.join(gdbRawData, "collisions")
crashes = os.path.join(gdbRawData, "crashes")
parties = os.path.join(gdbRawData, "parties")
victims = os.path.join(gdbRawData, "victims")

# endregion


# region Supporting Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Supporting Data Feature Classes")

# Define paths for the feature classes in the supporting data feature dateset of the geodatabase
boundaries = os.path.join(gdbSupportingData, "boundaries")
cities = os.path.join(gdbSupportingData, "cities")
blocks = os.path.join(gdbSupportingData, "blocks")
roads = os.path.join(gdbSupportingData, "roads")

# endregion


# region Analysis Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Analysis Data Feature Classes")

# Define paths for the feature classes in the analysis data feature dateset of the geodatabase
roadsMajor = os.path.join(gdbAnalysisData, "roadsMajor")
roadsMajorBuffers = os.path.join(gdbAnalysisData, "roadsMajorBuffers")
roadsMajorBuffersSum = os.path.join(gdbAnalysisData, "roadsMajorBuffersSum")
roadsMajorPointsAlongLines = os.path.join(gdbAnalysisData, "roadsMajorPointsAlongLines")
roadsMajorSplit = os.path.join(gdbAnalysisData, "roadsMajorSplit")
roadsMajorSplitBuffer = os.path.join(gdbAnalysisData, "roadsMajorSplitBuffer")
roadsMajorSplitBufferSum = os.path.join(gdbAnalysisData, "roadsMajorSplitBufferSum")
blocksSum = os.path.join(gdbAnalysisData, "blocksSum")
citiesSum = os.path.join(gdbAnalysisData, "citiesSum")
crashes500ftFromMajorRoads = os.path.join(gdbAnalysisData, "crashes500ftFromMajorRoads")

# endregion


# region Hot Spot Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spot Data Feature Classes")

# Define paths for the feature classes in the hot spot data feature dateset of the geodatabase
crashesHotspots = os.path.join(gdbHotspotData, "crashesHotspots")
crashesOptimizedHotspots = os.path.join(gdbHotspotData, "crashesOptimizedHotspots")
crashesFindHotspots100m1km = os.path.join(gdbHotspotData, "crashesFindHotspots100m1km")
crashesFindHotspots150m2km = os.path.join(gdbHotspotData, "crashesFindHotspots150m2km")
crashesFindHotspots100m5km = os.path.join(gdbHotspotData, "crashesFindHotspots100m5km")
crashesHotspots500ftFromMajorRoads = os.path.join(
    gdbHotspotData, "crashesHotspots500ftFromMajorRoads"
)
crashesFindHotspots500ftMajorRoads500ft1mi = os.path.join(
    gdbHotspotData, "crashesFindHotspots500ftMajorRoads500ft1mi"
)

# endregion
# endregion 1.5


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.6. Map Layer Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.6. Map Layer Definitions")


# region Project Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project Maps")

# Define the maps of the project

# OCSWITRS Data Maps
mapCollisions = aprx.listMaps("collisions")[0]
mapCrashes = aprx.listMaps("crashes")[0]
mapParties = aprx.listMaps("parties")[0]
mapVictims = aprx.listMaps("victims")[0]
mapInjuries = aprx.listMaps("injuries")[0]
mapFatalities = aprx.listMaps("fatalities")[0]
mapRoadCrashes = aprx.listMaps("roadCrashes")[0]

# OCSWITRS Hotspot Maps
mapFhs100m1km = aprx.listMaps("fhs100m1km")[0]
mapFhs150m2km = aprx.listMaps("fhs150m2km")[0]
mapFhs100m5km = aprx.listMaps("fhs100m5km")[0]
mapFhsRoads500ft = aprx.listMaps("fhsRoads500ft")[0]
mapOhsRoads500ft = aprx.listMaps("ohsRoads500ft")[0]
mapRoadHotspots = aprx.listMaps("roadHotspots")[0]
mapPointFhs = aprx.listMaps("pointFhs")[0]
mapPointOhs = aprx.listMaps("pointOhs")[0]

# OCSWITRS Supporting Data Maps
mapRoadBuffers = aprx.listMaps("roadBuffers")[0]
mapRoadSegments = aprx.listMaps("roadSegments")[0]
mapRoads = aprx.listMaps("roads")[0]
mapPopDens = aprx.listMaps("popDens")[0]
mapHouDens = aprx.listMaps("houDens")[0]
mapAreaCities = aprx.listMaps("areaCities")[0]
mapAreaBlocks = aprx.listMaps("areaBlocks")[0]

# OCSWITRS Analysis and Processing Maps
mapSummaries = aprx.listMaps("summaries")[0]
mapAnalysis = aprx.listMaps("analysis")[0]
mapRegression = aprx.listMaps("regression")[0]

# endregion


# region Collisions Map 1 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Collisions Map 1 Layers")

# Define the layers for the collisions map

# Define map layers
mapCollisionsLyrBoundaries = mapCollisions.listLayers("OCSWITRS Boundaries")[0]
mapCollisionsLyrCities = mapCollisions.listLayers("OCSWITRS Cities")[0]
mapCollisionsLyrBlocks = mapCollisions.listLayers("OCSWITRS Census Blocks")[0]
mapCollisionsLyrRoads = mapCollisions.listLayers("OCSWITRS Roads")[0]
mapCollisionsLyrCollisions = mapCollisions.listLayers("OCSWITRS Collisions")[0]

# List layers in map
print("Collisions Map Layers:")
for l in mapCollisions.listLayers():
    print(f"- {l.name}")

# Count Collisions
countCollisions = int(arcpy.management.GetCount(collisions)[0])
print(f"Count of Collisions: {countCollisions:,}")

# endregion


# region Crashes Map 2 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes Map 2 Layers")

# Define the layers for the crashes map

# Define map layers
mapCrashesLyrBoundaries = mapCrashes.listLayers("OCSWITRS Boundaries")[0]
mapCrashesLyrCities = mapCrashes.listLayers("OCSWITRS Cities")[0]
mapCrashesLyrBlocks = mapCrashes.listLayers("OCSWITRS Census Blocks")[0]
mapCrashesLyrRoads = mapCrashes.listLayers("OCSWITRS Roads")[0]
mapCrashesLyrCrashes = mapCrashes.listLayers("OCSWITRS Crashes")[0]

# List layers in map
print("Crashes Map Layers:")
for l in mapCrashes.listLayers():
    print(f"- {l.name}")

countCrashes = int(arcpy.management.GetCount(crashes)[0])
print(f"Count of Crashes: {countCrashes:,}")

# endregion


# region Parties Map 3 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Parties Map 3 Layers")

# Define map layers
mapPartiesLyrBoundaries = mapParties.listLayers("OCSWITRS Boundaries")[0]
mapPartiesLyrCities = mapParties.listLayers("OCSWITRS Cities")[0]
mapPartiesLyrBlocks = mapParties.listLayers("OCSWITRS Census Blocks")[0]
mapPartiesLyrRoads = mapParties.listLayers("OCSWITRS Roads")[0]
mapPartiesLyrParties = mapParties.listLayers("OCSWITRS Parties")[0]

# List layers in map
print("Parties Map Layers:")
for l in mapParties.listLayers():
    print(f"- {l.name}")

countParties = int(arcpy.management.GetCount(parties)[0])
print(f"Count of Parties: {countParties:,}")

# endregion


# region Victims Map 4 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims Map 4 Layers")

# Define map layers
mapVictimsLyrBoundaries = mapVictims.listLayers("OCSWITRS Boundaries")[0]
mapVictimsLyrCities = mapVictims.listLayers("OCSWITRS Cities")[0]
mapVictimsLyrBlocks = mapVictims.listLayers("OCSWITRS Census Blocks")[0]
mapVictimsLyrRoads = mapVictims.listLayers("OCSWITRS Roads")[0]
mapVictimsLyrVictims = mapVictims.listLayers("OCSWITRS Victims")[0]

# List layers in map
print("Victims Map Layers:")
for l in mapVictims.listLayers():
    print(f"- {l.name}")

countVictims = int(arcpy.management.GetCount(victims)[0])
print(f"Count of Victims: {countVictims:,}")

# endregion


# region Injuries Map 5 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Injuries Map 5 Layers")

# Define map layers
mapInjuriesLyrBoundaries = mapInjuries.listLayers("OCSWITRS Boundaries")[0]
mapInjuriesLyrCities = mapInjuries.listLayers("OCSWITRS Cities")[0]
mapInjuriesLyrBlocks = mapInjuries.listLayers("OCSWITRS Census Blocks")[0]
mapInjuriesLyrVictims = mapInjuries.listLayers("OCSWITRS Victims")[0]

# List layers in map
print("Injuries Map Layers:")
for l in mapInjuries.listLayers():
    print(f"- {l.name}")

# endregion


# region Fatalities Map 6 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Fatalities Map 6 Layers")

# Define map layers
mapFatalitiesLyrBoundaries = mapFatalities.listLayers("OCSWITRS Boundaries")[0]
mapFatalitiesLyrRoads = mapFatalities.listLayers("OCSWITRS Roads")[0]
mapFatalitiesLyrRoadsMajorBuffers = mapFatalities.listLayers(
    "OCSWITRS Major Roads Buffers"
)[0]
mapFatalitiesLyrFatalities = mapFatalities.listLayers("OCSWITRS Crashes")[0]

# List layers in map
print("Fatalities Map Layers:")
for l in mapFatalities.listLayers():
    print(f"- {l.name}")

# endregion


# region Hot Spots (100m, 1km) Map 7 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spots (100m, 1km) Map 7 Layers")

# Define map layers
mapFhs100m1kmLyrBoundaries = mapFhs100m1km.listLayers("OCSWITRS Boundaries")[0]
mapFhs100m1kmLyrCities = mapFhs100m1km.listLayers("OCSWITRS Cities")[0]
mapFhs100m1kmLyrBlocks = mapFhs100m1km.listLayers("OCSWITRS Census Blocks")[0]
mapFhs100m1kmLyrRoads = mapFhs100m1km.listLayers("OCSWITRS Roads")[0]
mapFhs100m1kmLyrFhs100m1km = mapFhs100m1km.listLayers(
    "OCSWITRS Crashes Find Hot Spots 100m 1km"
)[0]

# List layers in map
print("Find Hotspots 100m 1km Map Layers:")
for l in mapFhs100m1km.listLayers():
    print(f"- {l.name}")

# endregion


# region Hot Spots (150m, 2km) Map 8 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spots (150m, 2km) Map 8 Layers")

# Define map layers
mapFhs150m2kmLyrBoundaries = mapFhs150m2km.listLayers("OCSWITRS Boundaries")[0]
mapFhs150m2kmLyrCities = mapFhs150m2km.listLayers("OCSWITRS Cities")[0]
mapFhs150m2kmLyrBlocks = mapFhs150m2km.listLayers("OCSWITRS Census Blocks")[0]
mapFhs150m2kmLyrRoads = mapFhs150m2km.listLayers("OCSWITRS Roads")[0]
mapFhs150m2kmLyrFhs150m2km = mapFhs150m2km.listLayers(
    "OCSWITRS Crashes Find Hot Spots 150m 2km"
)[0]

# List layers in map
print("Find Hotspots 150m 2km Map Layers:")
for l in mapFhs150m2km.listLayers():
    print(f"- {l.name}")

# endregion


# region Hot Spots (100m, 5km) Map 9 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spots (100m, 5km) Map 9 Layers")

# Define map layers
mapFhs100m5kmLyrBoundaries = mapFhs100m5km.listLayers("OCSWITRS Boundaries")[0]
mapFhs100m5kmLyrCities = mapFhs100m5km.listLayers("OCSWITRS Cities")[0]
mapFhs100m5kmLyrBlocks = mapFhs100m5km.listLayers("OCSWITRS Census Blocks")[0]
mapFhs100m5kmLyrRoads = mapFhs100m5km.listLayers("OCSWITRS Roads")[0]
mapFhs100m5kmLyrFhs100m5km = mapFhs100m5km.listLayers(
    "OCSWITRS Crashes Find Hot Spots 100m 5km"
)[0]

# List layers in map
print("Find Hotspots 100m 5km Map Layers:")
for l in mapFhs100m5km.listLayers():
    print(f"- {l.name}")

# endregion


# region Hot Spots 500ft from Major Roads Map 10 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spots 500ft from Major Roads Map 10 Layers")

# Define map layers
mapFhsRoads500ftLyrBoundaries = mapFhsRoads500ft.listLayers("OCSWITRS Boundaries")[0]
mapFhsRoads500ftLyrCities = mapFhsRoads500ft.listLayers("OCSWITRS Cities")[0]
mapFhsRoads500ftLyrBlocks = mapFhsRoads500ft.listLayers("OCSWITRS Census Blocks")[0]
mapFhsRoads500ftLyrRoads = mapFhsRoads500ft.listLayers("OCSWITRS Roads")[0]
mapFhsRoads500ftLyrFhsRoads500ft = mapFhsRoads500ft.listLayers(
    "OCSWITRS Crashes Find Hot Spots 500 Feet from Major Roads 500ft 1mi"
)[0]

# List layers in map
print("Find Hotspots 500 Feet from Major Roads Map Layers:")
for l in mapFhsRoads500ft.listLayers():
    print(f"- {l.name}")

# endregion


# region Optimized Hot Spots 500ft from Major Roads Map 11 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Optimized Hot Spots 500ft from Major Roads Map 11 Layers")

# Define map layers
mapOhsRoads500ftLyrBoundaries = mapOhsRoads500ft.listLayers("OCSWITRS Boundaries")[0]
mapOhsRoads500ftLyrCities = mapOhsRoads500ft.listLayers("OCSWITRS Cities")[0]
mapOhsRoads500ftLyrBlocks = mapOhsRoads500ft.listLayers("OCSWITRS Census Blocks")[0]
mapOhsRoads500ftLyrRoads = mapOhsRoads500ft.listLayers("OCSWITRS Roads")[0]
mapOhsRoads500ftLyrOhsRoads500ft = mapOhsRoads500ft.listLayers(
    "OCSWITRS Crashes Find Hot Spots 500 Feet from Major Roads 500ft 1mi"
)[0]

# List layers in map
print("Optimized Hotspots 500 Feet from Major Roads Map Layers:")
for l in mapOhsRoads500ft.listLayers():
    print(f"- {l.name}")

# endregion


# region Major Road Crashes Map 12 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Crashes Map 12 Layers")

# Define map layers
mapRoadCrashesLyrBoundaries = mapRoadCrashes.listLayers("OCSWITRS Boundaries")[0]
mapRoadCrashesLyrBlocks = mapRoadCrashes.listLayers("OCSWITRS Census Blocks")[0]
mapRoadCrashesLyrRoadsMajor = mapRoadCrashes.listLayers("OCSWITRS Major Roads")[0]
mapRoadCrashesLyrCrashes500ftRoads = mapRoadCrashes.listLayers(
    "OCSWITRS Crashes 500 Feet from Major Roads"
)[0]

# List layers in map
print("Major Road Crasjes Map Layers:")
for l in mapRoadCrashes.listLayers():
    print(f"- {l.name}")

# endregion


# region Major Road Hotspots Map 13 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Hotspots Map 13 Layers")

# Define map layers
mapRoadHotspotsLyrBoundaries = mapRoadHotspots.listLayers("OCSWITRS Boundaries")[0]
mapRoadHotspotsLyrBlocks = mapRoadHotspots.listLayers("OCSWITRS Census Blocks")[0]
mapRoadHotspotsLyrRoadsMajor = mapRoadHotspots.listLayers("OCSWITRS Major Roads")[0]
mapRoadHotspotsLyrCrashesHotspots = mapRoadHotspots.listLayers(
    "OCSWITRS Crashes Hot Spots 500 Feet from Major Roads"
)

# List layers in map
print("Major Road Hotspots Map Layers:")
for l in mapRoadHotspots.listLayers():
    print(f"- {l.name}")

# endregion


# region Major Road Buffers Map 14 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Buffers Map 14 Layers")

# Define map layers
mapRoadBuffersLyrBoundaries = mapRoadBuffers.listLayers("OCSWITRS Boundaries")[0]
mapRoadBuffersLyrBlocks = mapRoadBuffers.listLayers("OCSWITRS Census Blocks")[0]
mapRoadBuffersLyrRoadsMajor = mapRoadBuffers.listLayers("OCSWITRS Major Roads")[0]
mapRoadBuffersLyrRoadBuffers = mapRoadBuffers.listLayers(
    "OCSWITRS Major Roads Buffers Summary"
)[0]

# List layers in map
print("Major Road Buffers Map Layers:")
for l in mapRoadBuffers.listLayers():
    print(f"- {l.name}")

# endregion


# region Major Road Segments Map 15 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Segments Map 15 Layers")

# Define map layers
mapRoadSegmentsLyrBoundaries = mapRoadSegments.listLayers("OCSWITRS Boundaries")[0]
mapRoadSegmentsLyrBlocks = mapRoadSegments.listLayers("OCSWITRS Census Blocks")[0]
mapRoadSegmentsLyrRoadsMajor = mapRoadSegments.listLayers("OCSWITRS Major Roads")[0]
mapRoadSegmentsLyrRoadsMajorSplit = mapRoadSegments.listLayers(
    "OCSWITRS Major Roads Split Buffer Summary"
)[0]

# List layers in map
print("Major Road Segments Map Layers:")
for l in mapRoadSegments.listLayers():
    print(f"- {l.name}")

# endregion


# region Major Road Segments Map 16 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Segments Map 16 Layers")

# Define map layers
mapRoadsLyrRoadsMajor = mapRoads.listLayers("OCSWITRS Major Roads")[0]
mapRoadsLyrRoadsMajorBuffers = mapRoads.listLayers("OCSWITRS Major Roads Buffers")[0]
mapRoadsLyrRoadsMajorBuffersSum = mapRoads.listLayers(
    "OCSWITRS Major Roads Buffers Summary"
)[0]
mapRoadsLyrRoadsMajorPointsAlongLines = mapRoads.listLayers(
    "OCSWITRS Major Roads Points Along Lines"
)[0]
mapRoadsLyrRoadsMajorSplit = mapRoads.listLayers("OCSWITRS Major Roads Split")[0]
mapRoadsLyrRoadsMajorSplitBuffer = mapRoads.listLayers(
    "OCSWITRS Major Roads Split Buffer"
)[0]
mapRoadsLyrRoadsMajorSplitBufferSum = mapRoads.listLayers(
    "OCSWITRS Major Roads Split Buffer Summary"
)[0]

# List layers in map
print("Roads Map Layers:")
for l in mapRoads.listLayers():
    print(f"- {l.name}")

# endregion


# region Population Density Map 17 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Population Density Map 17 Layers")

# Define map layers
mapPointFhsLyrBoundaries = mapPointFhs.listLayers("OCSWITRS Boundaries")[0]
mapPointFhsLyrRoadsMajor = mapPointFhs.listLayers("OCSWITRS Major Roads")[0]
mapPointFhsLyrFhs = mapPointFhs.listLayers("OCSWITRS Crashes Hot Spots")[0]

# List layers in map
print("Hotspot Points Map Layers:")
for l in mapPointFhs.listLayers():
    print(f"- {l.name}")

# endregion


# region Optimized Hotspot Points Map 18 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Optimized Hotspot Points Map 18 Layers")

# Define map layers
mapPointOhsLyrBoundaries = mapPointOhs.listLayers("OCSWITRS Boundaries")[0]
mapPointOhsLyrRoadsMajor = mapPointOhs.listLayers("OCSWITRS Major Roads")[0]
mapPointOhsLyrOhs = mapPointOhs.listLayers("OCSWITRS Crashes Optimized Hot Spots")[0]

# List layers in map
print("Optimized Hotspot Points Map Layers:")
for l in mapPointOhs.listLayers():
    print(f"- {l.name}")

# endregion


# region Population Density Map 19 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Population Density Map 19 Layers")

# Define map layers
mapPopDensLyrBoundaries = mapPopDens.listLayers("OCSWITRS Boundaries")[0]
mapPopDensLyrRoadsMajor = mapPopDens.listLayers("OCSWITRS Major Roads")[0]
mapPopDensLyrPopDens = mapPopDens.listLayers("OCSWITRS Population Density")[0]

# List layers in map
print("Population Density Map Layers:")
for l in mapPopDens.listLayers():
    print(f"- {l.name}")

# endregion


# region Housing Density Map 20 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Housing Density Map 20 Layers")

# Define map layers
mapHouDensLyrBoundaries = mapHouDens.listLayers("OCSWITRS Boundaries")[0]
mapHouDensLyrRoadsMajor = mapHouDens.listLayers("OCSWITRS Major Roads")[0]
mapHouDensLyrHouDens = mapHouDens.listLayers("OCSWITRS Housing Density")[0]

# List layers in map
print("Housing Density Map Layers:")
for l in mapHouDens.listLayers():
    print(f"- {l.name}")

# endregion


# region Victims by City Areas Map 21 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims by City Areas Map 21 Layers")

# Define map layers
mapAreaCitiesLyrBoundaries = mapAreaCities.listLayers("OCSWITRS Boundaries")[0]
mapAreaCitiesLyrRoadsMajor = mapAreaCities.listLayers("OCSWITRS Major Roads")[0]
mapAreaCitiesLyrCities = mapAreaCities.listLayers("OCSWITRS Cities Summary")[0]

# List layers in map
print("Victims by City Areas Map Layers:")
for l in mapAreaCities.listLayers():
    print(f"- {l.name}")

# endregion


# region Victims by Census Blocks Map 22 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims by Census Blocks Map 22 Layers")

# Define map layers
mapAreaBlocksLyrBoundaries = mapAreaBlocks.listLayers("OCSWITRS Boundaries")[0]
mapAreaBlocksLyrRoadsMajor = mapAreaBlocks.listLayers("OCSWITRS Major Roads")[0]
mapAreaBlocksLyrBlocks = mapAreaBlocks.listLayers("OCSWITRS Census Blocks Summary")[0]

# List layers in map
print("Victims by Census Block Areas Map Layers:")
for l in mapAreaBlocks.listLayers():
    print(f"- {l.name}")

# endregion


# region Summaries Map 23 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summaries Map 23 Layers")

# Define map layers
mapSummariesLyrBlocksSum = mapSummaries.listLayers("OCSWITRS Census Blocks Summary")[0]
mapSummariesLyrCitiesSum = mapSummaries.listLayers("OCSWITRS Cities Summary")[0]
mapSummariesLyrCrashes500ftFromMajorRoads = mapSummaries.listLayers(
    "OCSWITRS Crashes 500 Feet from Major Roads"
)[0]

# List layers in map
print("Summaries Map Layers:")
for l in mapSummaries.listLayers():
    print(f"- {l.name}")

# endregion


# region Analysis Map 24 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Analysis Map 24 Layers")

# Define map layers
mapAnalysisLyrCrashesHotspots = mapAnalysis.listLayers("OCSWITRS Crashes Hot Spots")[0]
mapAnalysisLyrCrashesOptimizedHotspots = mapAnalysis.listLayers(
    "OCSWITRS Crashes Optimized Hot Spots"
)[0]

# List layers in map
print("Analysis Map Layers:")
for l in mapAnalysis.listLayers():
    print(f"- {l.name}")

# endregion


# region Regression Map 25 Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Regression Map 25 Layers")

# Define map layers
mapRegressionLyrBoundaries = mapRegression.listLayers("OCSWITRS Boundaries")[0]
mapRegressionLyrCities = mapRegression.listLayers("OCSWITRS Cities")[0]
mapRegressionLyrBlocks = mapRegression.listLayers("OCSWITRS Census Blocks")[0]
mapRegressionLyrRoads = mapRegression.listLayers("OCSWITRS Roads")[0]

# List layers in map
print("Regression Map Layers:")
for l in mapRegression.listLayers():
    print(f"- {l.name}")

# endregion
# endregion 1.6


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.7. Project and Map Extent
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.7. Project and Map Extent")

# Define and create the project and map extent

# Define the map extent coordinates
xmin = -13150753.258299999
ymin = 3942787.8856000006
xmax = -13069273.7991
ymax = 4029458.1212000027

# Get the spatial reference of the boundaries layer
ref = arcpy.Describe(boundaries).spatialReference

# Set the map extent
prjExtent = arcpy.Extent(xmin, ymin, xmax, ymax, spatial_reference=ref)

# endregion 1.7
# endregion 1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2. Project Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. Project Layouts")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.1. Setup Map Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.1. Setup Map Layouts")


# region Layout Configuration
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layout Configuration")

# Setting up layout configuration variables. Options are:
# - Single map frame: 6 x 4 inches (landscape)
# - Dual map frames: 12 x 4 inches (landscape) (two 6 x 4 inches frames)
# - Four map frames: 12 x 8 inches (landscape) (four 6 x 4 inches frames)

# Function to setup layout configuration
def layoutConfiguration(nmf):
    # Match the number of map frames in layout
    match nmf:
        case 1:
            lytConfig = {
                "pageWidth": 11.0,
                "pageHeight": 8.5,
                "pageUnits": "INCH",
                "rows": 1,
                "cols": 1,
                "nmf": 1,
                "mf1": {
                    "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "t1": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 8.25,
                    "geometry": arcpy.Point(0.25, 8.25),
                },
                "na": {
                    "width": 0.3606,
                    "height": 0.75,
                    "anchor": "BOTTOM_RIGHT_CORNER",
                    "coordX": 10.75,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(10.75, 0.25),
                },
                "sb": {
                    "width": 4.5,
                    "height": 0.5,
                    "anchor": "BOTTOM_MID_POINT",
                    "coordX": 5.5,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(5.5, 0.25),
                },
                "cr": {
                    "width": 0.0,
                    "height": 0.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "lg1": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(0.25, 0.25),
                },
            }
        case 2:
            lytConfig = {
                "pageWidth": 22.0,
                "pageHeight": 8.5,
                "pageUnits": "INCH",
                "rows": 1,
                "cols": 2,
                "nmf": 2,
                "mf1": {
                    "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "mf2": {
                    "coords": [(11.0, 8.5), (22.0, 8.5), (11.0, 0.0), (22.0, 0.0)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(11.0, 0.0),
                },
                "t1": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 8.25,
                    "geometry": arcpy.Point(0.25, 8.25),
                },
                "t2": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 8.25,
                    "geometry": arcpy.Point(11.25, 8.25),
                },
                "na": {
                    "width": 0.3606,
                    "height": 0.75,
                    "anchor": "BOTTOM_RIGHT_CORNER",
                    "coordX": 21.75,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(21.75, 0.25),
                },
                "sb": {
                    "width": 4.5,
                    "height": 0.5,
                    "anchor": "BOTTOM_MID_POINT",
                    "coordX": 16.5,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(16.5, 0.25),
                },
                "cr": {
                    "width": 0.0,
                    "height": 0.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "lg1": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(0.25, 0.25),
                },
                "lg2": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(11.25, 0.25),
                },
            }
        case 4:
            lytConfig = {
                "pageWidth": 22.0,
                "pageHeight": 17.0,
                "pageUnits": "INCH",
                "rows": 2,
                "cols": 2,
                "nmf": 4,
                "mf1": {
                    "coords": [(0.0, 17.0), (11.0, 17.0), (0.0, 8.5), (11.0, 8.5)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 8.5,
                    "geometry": arcpy.Point(0.0, 8.5),
                },
                "mf2": {
                    "coords": [(11.0, 17.0), (22.0, 17.0), (11.0, 8.5), (22.0, 8.5)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.0,
                    "coordY": 8.5,
                    "geometry": arcpy.Point(11.0, 8.5),
                },
                "mf3": {
                    "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "mf4": {
                    "coords": [(11.0, 8.5), (22.0, 8.5), (11.0, 0.0), (22.0, 0.0)],
                    "width": 11.0,
                    "height": 8.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(11.0, 0.0),
                },
                "t1": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 16.75,
                    "geometry": arcpy.Point(0.25, 16.75),
                },
                "t2": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 16.75,
                    "geometry": arcpy.Point(11.25, 16.75),
                },
                "t3": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 8.25,
                    "geometry": arcpy.Point(0.25, 8.25),
                },
                "t4": {
                    "width": 1.9184,
                    "height": 0.3414,
                    "anchor": "TOP_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 8.25,
                    "geometry": arcpy.Point(11.25, 8.25),
                },
                "na": {
                    "width": 0.3606,
                    "height": 0.75,
                    "anchor": "BOTTOM_RIGHT_CORNER",
                    "coordX": 21.75,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(21.75, 0.25),
                },
                "sb": {
                    "width": 4.5,
                    "height": 0.5,
                    "anchor": "BOTTOM_MID_POINT",
                    "coordX": 16.75,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(16.75, 0.25),
                },
                "cr": {
                    "width": 0.5,
                    "height": 0.5,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.0,
                    "coordY": 0.0,
                    "geometry": arcpy.Point(0.0, 0.0),
                },
                "lg1": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 8.75,
                    "geometry": arcpy.Point(0.25, 8.75),
                },
                "lg2": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 8.75,
                    "geometry": arcpy.Point(11.25, 8.75),
                },
                "lg3": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 0.25,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(0.25, 0.25),
                },
                "lg4": {
                    "width": 4.5,
                    "height": 2.0,
                    "anchor": "BOTTOM_LEFT_CORNER",
                    "coordX": 11.25,
                    "coordY": 0.25,
                    "geometry": arcpy.Point(11.25, 0.25),
                },
            }
    return lytConfig

# Apply the layout configuration to all layouts

# Define layout configurations for each map
mapsLytConfig = layoutConfiguration(4)
injuriesLytConfig = layoutConfiguration(2)
hotspotsLytConfig = layoutConfiguration(4)
roadsLytConfig = layoutConfiguration(4)
pointsLytConfig = layoutConfiguration(2)
densityLytConfig = layoutConfiguration(2)
areasLytConfig = layoutConfiguration(2)

# Add the layout configurations to a new dictionary
lytDict = {
    "maps": mapsLytConfig,
    "injuries": injuriesLytConfig,
    "hotspots": hotspotsLytConfig,
    "roads": roadsLytConfig,
    "points": pointsLytConfig,
    "density": densityLytConfig,
    "areas": areasLytConfig,
}

# endregion


# region Remove Old Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Remove Old Layouts")

# Remove all old layouts from the ArcGIS Pro project
if aprx.listLayouts():
    for l in aprx.listLayouts():
        print(f"Deleting layout: {l.name}")
        aprx.deleteItem(l)
else:
    print("No layouts to delete.")

# endregion


# region Create New Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create New Layouts")

# Create new layouts in the ArcGIS Pro project

# for each of the layouts in the list, if it exists, delete it
for l in layoutList:
    for i in aprx.listLayouts():
        if i.name == l:
            print(f"Deleting layout: {l}")
            aprx.deleteItem(i)
    # Create new layouts
    print(f"Creating layout: {l}")
    aprx.createLayout(
        page_width=lytDict[l]["pageWidth"],
        page_height=lytDict[l]["pageHeight"],
        page_units=lytDict[l]["pageUnits"],
        name=l,
    )

# List all the newly created layouts
print("\nNewly created layouts:")
for l in aprx.listLayouts():
    print(f"- {l.name}")

# Store the layout objects in variables
mapsLayout = aprx.listLayouts("maps")[0]  # maps layout
injuriesLayout = aprx.listLayouts("injuries")[0]  # injuries layout
hotspotsLayout = aprx.listLayouts("hotspots")[0]  # hotspots layout
roadsLayout = aprx.listLayouts("roads")[0]  # road hotspots layout
pointsLayout = aprx.listLayouts("points")[0]  # point hotspots layout
densityLayout = aprx.listLayouts("density")[0]  # densities layout
areasLayout = aprx.listLayouts("areas")[0]  # areas layout

# endregion
# endregion 2.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.2. Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.2. Layout Metadata")


# region Maps Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Maps Layout Metadata")

# Create a new metadata object for the maps layout and assign it to the layout
mdoMapsLayout = md.Metadata()
mdoMapsLayout.title = "OCSWITRS Maps Layout"
mdoMapsLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapsLayout.summary = "Layout for the OCSWITRS Project Maps"
mdoMapsLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Maps</span></p></div></div></div>"""
mdoMapsLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapsLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapsLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
mapsLayout.metadata = mdoMapsLayout

# endregion


# region Injuries Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Injuries Layout Metadata")

# Create a new metadata object for the injuries layout and assign it to the layout
mdoInjuriesLayout = md.Metadata()
mdoInjuriesLayout.title = "OCSWITRS Injuries Layout"
mdoInjuriesLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoInjuriesLayout.summary = "Layout for the OCSWITRS Project Injuries"
mdoInjuriesLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Injuries</span></p></div></div></div>"""
mdoInjuriesLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoInjuriesLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoInjuriesLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
injuriesLayout.metadata = mdoInjuriesLayout

# endregion


# region Hotspots Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspots Layout Metadata")

# Create a new metadata object for the hotspots layout and assign it to the layout
mdoHotspotsLayout = md.Metadata()
mdoHotspotsLayout.title = "OCSWITRS Hot Spots Layout"
mdoHotspotsLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoHotspotsLayout.summary = "Layout for the OCSWITRS Project Hot Spots"
mdoHotspotsLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Hot Spots</span></p></div></div></div>"""
mdoHotspotsLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoHotspotsLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoHotspotsLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
hotspotsLayout.metadata = mdoHotspotsLayout

# endregion


# region Roads Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Roads Layout Metadata")

# Create a new metadata object for the roads layout and assign it to the layout
mdoRoadsLayout = md.Metadata()
mdoRoadsLayout.title = "OCSWITRS Road Hot Spots Layout"
mdoRoadsLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoRoadsLayout.summary = "Layout for the OCSWITRS Project Roads Hot Spots"
mdoRoadsLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Hot Spots</span></p></div></div></div>"""
mdoRoadsLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoRoadsLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoRoadsLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
roadsLayout.metadata = mdoRoadsLayout

# endregion


# region Points Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Points Layout Metadata")

# Create a new metadata object for the points hotspots layout and assign it to the layout
mdoPointsLayout = md.Metadata()
mdoPointsLayout.title = "OCSWITRS Optimized Hot Spots Layout"
mdoPointsLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoPointsLayout.summary = "Layout for the OCSWITRS Project Optimized Hot Spots"
mdoPointsLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Optimized Hot Spots</span></p></div></div></div>"""
mdoPointsLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoPointsLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoPointsLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
pointsLayout.metadata = mdoPointsLayout

# endregion


# region Density Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Density Layout Metadata")

# Create a new metadata object for the densities layout and assign it to the layout
mdoDensityLayout = md.Metadata()
mdoDensityLayout.title = "OCSWITRS Densities Layout"
mdoDensityLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoDensityLayout.summary = "Layout for the OCSWITRS Project Densities"
mdoDensityLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Densities</span></p></div></div></div>"""
mdoDensityLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoDensityLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoDensityLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
densityLayout.metadata = mdoDensityLayout

# endregion


# region Areas Layout Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Areas Layout Metadata")

# Create a new metadata object for the areas layout and assign it to the layout
mdoAreasLayout = md.Metadata()
mdoAreasLayout.title = "OCSWITRS Areas Layout"
mdoAreasLayout.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoAreasLayout.summary = "Layout for the OCSWITRS Project Areas"
mdoAreasLayout.description = """<div style="text-align:Left;"><div><div><p><span>Layout for the OCSWITRS Project Areas</span></p></div></div></div>"""
mdoAreasLayout.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoAreasLayout.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoAreasLayout.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the layout
areasLayout.metadata = mdoAreasLayout

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 2.2
# endregion 2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3. Maps Layout Processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3. Maps Layout Processing")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.1. Layout View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.1. Layout View")


# region Set Maps Layout View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Set Maps Layout View")

# Close all views and open the map layout

# Close all previous views
aprx.closeViews()

# Open the maps layout view
mapsLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# endregion
# endregion 3.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.2. Add Map Frames
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.2. Add Map Frames")


# region Remove Old Map Frames
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Remove Old Map Frames")

# Delete all layout data frames and elements

# Delete all map frames from the layout
for el in mapsLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        mapsLayout.deleteElement(el)

# endregion


# region Map Frame Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Map Frame Definitions")

# List of maps to be added as map frames to the layout
mapsMfList = [mapCollisions, mapCrashes, mapParties, mapVictims]

# Number of map frames
mapsMfCount = len(mapsMfList)

# Number of rows and columns for the map frames
mapsMfCols = 2
mapsMfRows = math.ceil(mapsMfCount / mapsMfCols)

# Map frame page dimensions
mapsMfPageWidth = lytDict["maps"]["pageWidth"]
mapsMfPageHeight = lytDict["maps"]["pageHeight"]

# Map frame names
mapsMfNames = [f"mf{i}" for i in range(1, mapsMfCount + 1)]

# endregion


# region Map Frame 1
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Map Frame 1")

# Add collisions map frame (map frame 1)

# Add the mapframe to the layout
mapsMf1 = mapsLayout.createMapFrame(
    geometry=lytDict["maps"]["mf1"]["geometry"],
    map=mapsMfList[0],
    name=f"{mapsLayout.name}{mapsMfNames[0].title()}",
)

# Set up map frame properties
mapsMf1.name = f"{mapsLayout.name}{mapsMfNames[0].title()}"
mapsMf1.setAnchor(lytDict["maps"]["mf1"]["anchor"])
mapsMf1.elementWidth = lytDict["maps"]["mf1"]["width"]
mapsMf1.elementHeight = lytDict["maps"]["mf1"]["height"]
mapsMf1.elementPositionX = lytDict["maps"]["mf1"]["coordX"]
mapsMf1.elementPositionY = lytDict["maps"]["mf1"]["coordY"]
mapsMf1.elementRotation = 0
mapsMf1.visible = True
mapsMf1.map = mapsMfList[0]
mapsMf1Cim = mapsMf1.getDefinition("V3")
mapsMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
mapsMf1.setDefinition(mapsMf1Cim)

# endregion


# region Map Frame 2
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Map Frame 2")

# Add crashes map frame (map frame 2)

# Add the mapframe to the layout
mapsMf2 = mapsLayout.createMapFrame(
    geometry=lytDict["maps"]["mf2"]["geometry"],
    map=mapsMfList[1],
    name=f"{mapsLayout.name}{mapsMfNames[1].title()}",
)

# Set up map frame properties
mapsMf2.name = f"{mapsLayout.name}{mapsMfNames[1].title()}"
mapsMf2.setAnchor(lytDict["maps"]["mf2"]["anchor"])
mapsMf2.elementWidth = lytDict["maps"]["mf2"]["width"]
mapsMf2.elementHeight = lytDict["maps"]["mf2"]["height"]
mapsMf2.elementPositionX = lytDict["maps"]["mf2"]["coordX"]
mapsMf2.elementPositionY = lytDict["maps"]["mf2"]["coordY"]
mapsMf2.elementRotation = 0
mapsMf2.visible = True
mapsMf2.map = mapsMfList[1]
mapsMf2Cim = mapsMf2.getDefinition("V3")
mapsMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
mapsMf2.setDefinition(mapsMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 3</h3>

# %% [markdown]
# Add parties map frame (map frame 3)

# %%
# Add the mapframe to the layout
mapsMf3 = mapsLayout.createMapFrame(
    geometry=lytDict["maps"]["mf3"]["geometry"],
    map=mapsMfList[2],
    name=f"{mapsLayout.name}{mapsMfNames[2].title()}",
)

# Set up map frame properties
mapsMf3.name = f"{mapsLayout.name}{mapsMfNames[2].title()}"
mapsMf3.setAnchor(lytDict["maps"]["mf3"]["anchor"])
mapsMf3.elementWidth = lytDict["maps"]["mf3"]["width"]
mapsMf3.elementHeight = lytDict["maps"]["mf3"]["height"]
mapsMf3.elementPositionX = lytDict["maps"]["mf3"]["coordX"]
mapsMf3.elementPositionY = lytDict["maps"]["mf3"]["coordY"]
mapsMf3.elementRotation = 0
mapsMf3.visible = True
mapsMf3.map = mapsMfList[2]
mapsMf3Cim = mapsMf3.getDefinition("V3")
mapsMf3Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
mapsMf3.setDefinition(mapsMf3Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 4</h3>

# %% [markdown]
# Add victims map frame (map frame 4)

# %%
# Add the mapframe to the layout
mapsMf4 = mapsLayout.createMapFrame(
    geometry=lytDict["maps"]["mf4"]["geometry"],
    map=mapsMfList[3],
    name=f"{mapsLayout.name}{mapsMfNames[3].title()}",
)

# Set up map frame properties
mapsMf4.name = f"{mapsLayout.name}{mapsMfNames[3].title()}"
mapsMf4.setAnchor(lytDict["maps"]["mf4"]["anchor"])
mapsMf4.elementWidth = lytDict["maps"]["mf4"]["width"]
mapsMf4.elementHeight = lytDict["maps"]["mf4"]["height"]
mapsMf4.elementPositionX = lytDict["maps"]["mf4"]["coordX"]
mapsMf4.elementPositionY = lytDict["maps"]["mf4"]["coordY"]
mapsMf4.elementRotation = 0
mapsMf4.visible = True
mapsMf4.map = mapsMfList[3]
mapsMf4Cim = mapsMf4.getDefinition("V3")
mapsMf4Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
mapsMf4.setDefinition(mapsMf4Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map views (zoom to layers)

# %%
mapsMf1.camera.setExtent(prjExtent)
mapsMf2.camera.setExtent(prjExtent)
mapsMf3.camera.setExtent(prjExtent)
mapsMf4.camera.setExtent(prjExtent)

# %% [markdown]
# Turn on the visibility of the appropriate layers for each map frame

# %%
# Loop through map frames and turn on appropriate layers
for mf in mapsLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Collisions",
            "OCSWITRS Crashes",
            "OCSWITRS Parties",
            "OCSWITRS Victims",
            "OCSWITRS Roads",
            "OCSWITRS Cities",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
mapsNa = mapsLayout.createMapSurroundElement(
    geometry=lytDict["maps"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=mapsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
mapsNa.name = "na"
mapsNa.setAnchor(lytDict["maps"]["na"]["anchor"])
mapsNa.elementWidth = lytDict["maps"]["na"]["width"]
mapsNa.elementHeight = lytDict["maps"]["na"]["height"]
mapsNa.elementPositionX = lytDict["maps"]["na"]["coordX"]
mapsNa.elementPositionY = lytDict["maps"]["na"]["coordY"]
mapsNa.elementRotation = 0
mapsNa.visible = True
mapsNaCim = mapsNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
mapsSb = mapsLayout.createMapSurroundElement(
    geometry=lytDict["maps"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=mapsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Set scale bar properties

# %%
# Set up scale bar properties
mapsSb.name = "sb"
mapsSb.setAnchor(lytDict["maps"]["sb"]["anchor"])
mapsSb.elementWidth = lytDict["maps"]["sb"]["width"]
mapsSb.elementHeight = lytDict["maps"]["sb"]["height"]
mapsSb.elementPositionX = lytDict["maps"]["sb"]["coordX"]
mapsSb.elementPositionY = lytDict["maps"]["sb"]["coordY"]
mapsSb.elementRotation = 0
mapsSb.visible = True
mapsSbCim = mapsSb.getDefinition("V3")
mapsSbCim.labelSymbol.symbol.height = 14
mapsSb.setDefinition(mapsSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if mapsLayout.listElements("TEXT_ELEMENT", "cr"):
    mapsLayout.deleteElement("cr")

# Add the credits text to the layout
mapsCr = aprx.createTextElement(
    container=mapsLayout,
    geometry=lytDict["maps"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='maps' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
mapsCr.name = "cr"
mapsCr.setAnchor(lytDict["maps"]["cr"]["anchor"])
mapsCr.elementPositionX = 0
mapsCr.elementPositionY = 0
mapsCr.elementRotation = 0
mapsCr.visible = False
mapsCrCim = mapsCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in mapsLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        mapsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Severity Legend (Collisions Severity)</h3>

# %% [markdown]
# Adding severity Legend (legend 1) to the layout

# %%
# Add the legend to the layout
mapsLg1 = mapsLayout.createMapSurroundElement(
    geometry=lytDict["maps"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=mapsMf1,
    name="lg1",
)

# %% [markdown]
# Set density legend properties

# %%
# Obtain the CIM object of the legend
mapsLg1Cim = mapsLg1.getDefinition("V3")

# Disable the legend title
mapsLg1Cim.showTitle = False

# Adjust fitting of the legend frame
mapsLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the collisions layer, and turn off the rest of the layers
for i in mapsLg1Cim.items:
    if i.name == "OCSWITRS Collisions":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
        i.showFeatureCount = True
    else:
        i.isVisible = False

# Update the legend CIM definitions
mapsLg1.setDefinition(mapsLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
mapsLg1.name = "lg1"
mapsLg1.setAnchor(lytDict["maps"]["lg1"]["anchor"])
mapsLg1.elementPositionX = lytDict["maps"]["lg1"]["coordX"]
mapsLg1.elementPositionY = lytDict["maps"]["lg1"]["coordY"]
mapsLg1.elementRotation = 0
mapsLg1.visible = True
mapsLg1.mapFrame = mapsMf1
mapsLg1Cim = mapsLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Roads Legend</h3>

# %% [markdown]
# Adding Roads Legend (legend 2) to the layout

# %%
# Add the legend to the layout
mapsLg2 = mapsLayout.createMapSurroundElement(
    geometry=lytDict["maps"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=mapsMf1,
    name="lg2",
)

# %% [markdown]
# Set roads legend properties

# %%
# Obtain the CIM object of the legend
mapsLg2Cim = mapsLg2.getDefinition("V3")

# Disable the legend title
mapsLg2Cim.showTitle = False

# Adjust fitting of the legend frame
mapsLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in mapsLg2Cim.items:
    if i.name == "OCSWITRS Roads":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
        i.showFeatureCount = True
    else:
        i.isVisible = False

# Update the legend CIM definitions
mapsLg2.setDefinition(mapsLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
mapsLg2.name = "lg2"
mapsLg2.setAnchor(lytDict["maps"]["lg2"]["anchor"])
mapsLg2.elementPositionX = lytDict["maps"]["lg2"]["coordX"]
mapsLg2.elementPositionY = lytDict["maps"]["lg2"]["coordY"]
mapsLg2.elementRotation = 0
mapsLg2.visible = True
mapsLg2.mapFrame = mapsMf1
mapsLg2_cim = mapsLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 3: Density Legend (Cities)</h3>

# %% [markdown]
# Adding Severity Legend (legend 3) to the layout

# %%
# Add the legend to the layout
mapsLg3 = mapsLayout.createMapSurroundElement(
    geometry=lytDict["maps"]["lg3"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=mapsMf1,
    name="lg3",
)

# %% [markdown]
# Set severity legend properties

# %%
# Obtain the CIM object of the legend
mapsLg3Cim = mapsLg3.getDefinition("V3")

# Disable the legend title
mapsLg3Cim.showTitle = False

# Adjust fitting of the legend frame
mapsLg3Cim.fittingStrategy = "AdjustFrame"

# Turn on the cities and boundaries layers, and turn off the rest of the layers
for i in mapsLg3Cim.items:
    if i.name == "OCSWITRS Cities":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    elif i.name == "OCSWITRS Boundaries":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
mapsLg3.setDefinition(mapsLg3Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
mapsLg3.name = "lg3"
mapsLg3.setAnchor(lytDict["maps"]["lg3"]["anchor"])
mapsLg3.elementPositionX = lytDict["maps"]["lg3"]["coordX"]
mapsLg3.elementPositionY = lytDict["maps"]["lg3"]["coordY"]
mapsLg3.elementRotation = 0
mapsLg3.visible = True
mapsLg3.mapFrame = mapsMf1
mapsLg3Cim = mapsLg3.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the collisions map frame (title 1)

# %%
# Check if the collisions title already exist and if it is, delete it
if mapsLayout.listElements("TEXT_ELEMENT", "t1"):
    mapsLayout.deleteElement("t1")

# Add the title to the layout
mapsT1 = aprx.createTextElement(
    container=mapsLayout,
    geometry=lytDict["maps"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Collisions (Count: {countCollisions:,})",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
mapsT1.name = "t1"
mapsT1.setAnchor(lytDict["maps"]["t1"]["anchor"])
mapsT1.elementPositionX = lytDict["maps"]["t1"]["coordX"]
mapsT1.elementPositionY = lytDict["maps"]["t1"]["coordY"]
mapsT1.elementRotation = 0
mapsT1.visible = True
mapsT1.text = f"(a) Collisions (Count: {countCollisions:,})"
mapsT1.textSize = 20
mapsT1Cim = mapsT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the crashes map frame (title 2)

# %%
# Check if the crashes title already exist and if it is, delete it
if mapsLayout.listElements("TEXT_ELEMENT", "t2"):
    mapsLayout.deleteElement("t2")

# Add the title to the layout
mapsT2 = aprx.createTextElement(
    container=mapsLayout,
    geometry=lytDict["maps"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Crashes (Count: {countCrashes:,})",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
mapsT2.name = "t2"
mapsT2.setAnchor(lytDict["maps"]["t2"]["anchor"])
mapsT2.elementPositionX = lytDict["maps"]["t2"]["coordX"]
mapsT2.elementPositionY = lytDict["maps"]["t2"]["coordY"]
mapsT2.elementRotation = 0
mapsT2.visible = True
mapsT2.text = f"(b) Crashes (Count: {countCrashes:,})"
mapsT2.textSize = 20
mapsT2Cim = mapsT2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 3</h3>

# %% [markdown]
# Add title for for the parties map frame (title 3)

# %%
# Check if the parties title already exist and if it is, delete it
if mapsLayout.listElements("TEXT_ELEMENT", "t3"):
    mapsLayout.deleteElement("t3")

# Add the title to the layout
mapsT3 = aprx.createTextElement(
    container=mapsLayout,
    geometry=lytDict["maps"]["t3"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t3",
    text_type="POINT",
    text=f"(c) Parties (Count: {countParties:,})",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
mapsT3.name = "t3"
mapsT3.setAnchor(lytDict["maps"]["t3"]["anchor"])
mapsT3.elementPositionX = lytDict["maps"]["t3"]["coordX"]
mapsT3.elementPositionY = lytDict["maps"]["t3"]["coordY"]
mapsT3.elementRotation = 0
mapsT3.visible = True
mapsT3.text = f"(c) Parties (Count: {countParties:,})"
mapsT3.textSize = 20
mapsT3Cim = mapsT3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 4</h3>

# %% [markdown]
# Add title for for the victims map frame (title 4)

# %%
# Check if the victims title already exist and if it is, delete it
if mapsLayout.listElements("TEXT_ELEMENT", "t4"):
    mapsLayout.deleteElement("t4")

# Add the title to the layout
mapsT4 = aprx.createTextElement(
    container=mapsLayout,
    geometry=lytDict["maps"]["t4"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t4",
    text_type="POINT",
    text=f"(d) Victims (Count: {countVictims:,})",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
mapsT4.name = "t4"
mapsT4.setAnchor(lytDict["maps"]["t4"]["anchor"])
mapsT4.elementPositionX = lytDict["maps"]["t4"]["coordX"]
mapsT4.elementPositionY = lytDict["maps"]["t4"]["coordY"]
mapsT4.elementRotation = 0
mapsT4.visible = True
mapsT4.text = f"(d) Victims (Count: {countVictims:,})"
mapsT4.textSize = 20
mapsT4Cim = mapsT4.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">3.8. Export Maps Layout</h2>

# %% [markdown]
# Get maps layout CIM

# %%
mapsLayoutCim = mapsLayout.getDefinition("V3")  # Maps layout CIM

# %% [markdown]
# Export maps layout to disk

# %%
exportCim("layout", mapsLayout, mapsLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export maps layout to PNG (Figure 10)
mapsLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig10-MapsLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">4. Injuries Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set Injuries Layout View</h3>

# %% [markdown]
# Close all views and open the injuries layout

# %%
# Close all previous views
aprx.closeViews()

# Open the injuries layout view
injuriesLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in injuriesLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        injuriesLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %%
# List of maps to be added as map frames to the layout
injuriesMfList = [mapInjuries, mapFatalities]

# Number of map frames
injuriesMfCount = len(injuriesMfList)

# Number of rows and columns for the map frames
injuriesMfCols = 2
injuriesMfRows = math.ceil(injuriesMfCount / injuriesMfCols)

# Map frame page dimensions
injuriesMfPageWidth = lytDict["injuries"]["pageWidth"]
injuriesMfPageHeight = lytDict["injuries"]["pageHeight"]

# Map frame names
injuriesMfNames = [f"mf{i}" for i in range(1, injuriesMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Victims map frame (map frame 1)

# %%
# Add the mapframe to the layout
injuriesMf1 = injuriesLayout.createMapFrame(
    geometry=lytDict["injuries"]["mf1"]["geometry"],
    map=injuriesMfList[0],
    name=f"{injuriesLayout.name}{injuriesMfNames[0].title()}",
)

# Set up map frame properties
injuriesMf1.name = f"{injuriesLayout.name}{injuriesMfNames[0].title()}"
injuriesMf1.setAnchor(lytDict["injuries"]["mf1"]["anchor"])
injuriesMf1.elementWidth = lytDict["injuries"]["mf1"]["width"]
injuriesMf1.elementHeight = lytDict["injuries"]["mf1"]["height"]
injuriesMf1.elementPositionX = lytDict["injuries"]["mf1"]["coordX"]
injuriesMf1.elementPositionY = lytDict["injuries"]["mf1"]["coordY"]
injuriesMf1.elementRotation = 0
injuriesMf1.visible = True
injuriesMf1.map = injuriesMfList[0]
injuriesMf1Cim = injuriesMf1.getDefinition("V3")
injuriesMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
injuriesMf1.setDefinition(injuriesMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Fatalities map frame (map frame 2)

# %%
# Add the mapframe to the layout
injuriesMf2 = injuriesLayout.createMapFrame(
    geometry=lytDict["injuries"]["mf2"]["geometry"],
    map=injuriesMfList[1],
    name=f"{injuriesLayout.name}{injuriesMfNames[1].title()}",
)

# Set up map frame properties
injuriesMf2.name = f"{injuriesLayout.name}{injuriesMfNames[1].title()}"
injuriesMf2.setAnchor(lytDict["injuries"]["mf2"]["anchor"])
injuriesMf2.elementWidth = lytDict["injuries"]["mf2"]["width"]
injuriesMf2.elementHeight = lytDict["injuries"]["mf2"]["height"]
injuriesMf2.elementPositionX = lytDict["injuries"]["mf2"]["coordX"]
injuriesMf2.elementPositionY = lytDict["injuries"]["mf2"]["coordY"]
injuriesMf2.elementRotation = 0
injuriesMf2.visible = True
injuriesMf2.map = injuriesMfList[1]
injuriesMf2Cim = injuriesMf2.getDefinition("V3")
injuriesMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
injuriesMf2.setDefinition(injuriesMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
injuriesMf1.camera.setExtent(prjExtent)
injuriesMf2.camera.setExtent(prjExtent)

# %% [markdown]
# Turn on appropriate layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in injuriesLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Victims",
            "OCSWITRS Crashes",
            "OCSWITRS Major Roads Buffers",
            "OCSWITRS Roads",
            "OCSWITRS Cities",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
injuriesNa = injuriesLayout.createMapSurroundElement(
    geometry=lytDict["injuries"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=injuriesMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
injuriesNa.name = "na"
injuriesNa.setAnchor(lytDict["injuries"]["na"]["anchor"])
injuriesNa.elementWidth = lytDict["injuries"]["na"]["width"]
injuriesNa.elementHeight = lytDict["injuries"]["na"]["height"]
injuriesNa.elementPositionX = lytDict["injuries"]["na"]["coordX"]
injuriesNa.elementPositionY = lytDict["injuries"]["na"]["coordY"]
injuriesNa.elementRotation = 0
injuriesNa.visible = True
injuriesNaCim = injuriesNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
injuriesSb = injuriesLayout.createMapSurroundElement(
    geometry=lytDict["injuries"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=injuriesMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Set scale bar properties

# %%
# Set up scale bar properties
injuriesSb.name = "sb"
injuriesSb.setAnchor(lytDict["injuries"]["sb"]["anchor"])
injuriesSb.elementWidth = lytDict["injuries"]["sb"]["width"]
injuriesSb.elementHeight = lytDict["injuries"]["sb"]["height"]
injuriesSb.elementPositionX = lytDict["injuries"]["sb"]["coordX"]
injuriesSb.elementPositionY = lytDict["injuries"]["sb"]["coordY"]
injuriesSb.elementRotation = 0
injuriesSb.visible = True
injuriesSbCim = injuriesSb.getDefinition("V3")
injuriesSbCim.labelSymbol.symbol.height = 14
injuriesSb.setDefinition(injuriesSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if injuriesLayout.listElements("TEXT_ELEMENT", "cr"):
    injuriesLayout.deleteElements("cr")

# Add the credits text to the layout
injuriesCr = aprx.createTextElement(
    container=injuriesLayout,
    geometry=lytDict["injuries"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='injuries' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
injuriesCr.name = "cr"
injuriesCr.setAnchor(lytDict["injuries"]["cr"]["anchor"])
injuriesCr.elementPositionX = 0
injuriesCr.elementPositionY = 0
injuriesCr.elementRotation = 0
injuriesCr.visible = False
injuriesCrCim = injuriesCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in injuriesLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        injuriesLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Severity Legend (Injuries Severity)</h3>

# %% [markdown]
# Adding Severity Legend (legend 1) to the layout

# %%
# Add the legend to the layout
injuriesLg1 = injuriesLayout.createMapSurroundElement(
    geometry=lytDict["injuries"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=injuriesMf1,
    name="lg1",
)

# %% [markdown]
# Set severity legend properties

# %%
# Obtain the CIM object of the legend
injuriesLg1Cim = injuriesLg1.getDefinition("V3")

# Disable the legend title
injuriesLg1Cim.showTitle = False

# Adjust fitting of the legend frame
injuriesLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the victims layer, and turn off the rest of the layers
for i in injuriesLg1Cim.items:
    if i.name == "OCSWITRS Victims":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
        i.showFeatureCount = True
    else:
        i.isVisible = False

# Update the legend CIM definitions
injuriesLg1.setDefinition(injuriesLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
injuriesLg1.name = "lg1"
injuriesLg1.setAnchor(lytDict["injuries"]["lg1"]["anchor"])
injuriesLg1.elementPositionX = lytDict["injuries"]["lg1"]["coordX"]
injuriesLg1.elementPositionY = lytDict["injuries"]["lg1"]["coordY"]
injuriesLg1.elementRotation = 0
injuriesLg1.visible = True
injuriesLg1.mapFrame = injuriesMf1
injuriesLg1Cim = injuriesLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Fatalities and Roads Legend</h3>

# %% [markdown]
# Adding Fatalities and Roads Legend (legend 2) to the layout

# %%
# Add the legend to the layout
injuriesLg2 = injuriesLayout.createMapSurroundElement(
    geometry=lytDict["injuries"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=injuriesMf2,
    name="lg2",
)

# %% [markdown]
# Set fatalities and roads legend properties

# %%
# Obtain the CIM object of the legend
injuriesLg2Cim = injuriesLg2.getDefinition("V3")

# Disable the legend title
injuriesLg2Cim.showTitle = False

# Adjust fitting of the legend frame
injuriesLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the fatalities layer, and turn off the rest of the layers
for i in injuriesLg2Cim.items:
    if i.name == "OCSWITRS Crashes":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    elif i.name == "OCSWITRS Major Roads Buffers":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    elif i.name == "OCSWITRS Roads":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
injuriesLg2.setDefinition(injuriesLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
injuriesLg2.name = "lg2"
injuriesLg2.setAnchor(lytDict["injuries"]["lg2"]["anchor"])
injuriesLg2.elementPositionX = lytDict["injuries"]["lg2"]["coordX"]
injuriesLg2.elementPositionY = lytDict["injuries"]["lg2"]["coordY"]
injuriesLg2.elementRotation = 0
injuriesLg2.visible = True
injuriesLg2.mapFrame = injuriesMf2
injuriesLg2Cim = injuriesLg2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the victims map frame (title 1)

# %%
# Check if the victims title already exist and if it is, delete it
if injuriesLayout.listElements("TEXT_ELEMENT", "t1"):
    injuriesLayout.deleteElement("t1")

# Add the title to the layout
injuriesT1 = aprx.createTextElement(
    container=injuriesLayout,
    geometry=lytDict["injuries"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Victim Injuries",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
injuriesT1.name = "t1"
injuriesT1.setAnchor(lytDict["injuries"]["t1"]["anchor"])
injuriesT1.elementPositionX = lytDict["injuries"]["t1"]["coordX"]
injuriesT1.elementPositionY = lytDict["injuries"]["t1"]["coordY"]
injuriesT1.elementRotation = 0
injuriesT1.visible = True
injuriesT1.text = f"(a) Victim Injuries"
injuriesT1.textSize = 20
injuriesT1Cim = injuriesT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the fatalities map frame (title 2)

# %%
# Check if the crashes title already exist and if it is, delete it
if injuriesLayout.listElements("TEXT_ELEMENT", "t2"):
    injuriesLayout.deleteElement("t2")

# Add the title to the layout
injuriesT2 = aprx.createTextElement(
    container=injuriesLayout,
    geometry=lytDict["injuries"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Victim Fatalities",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
injuriesT2.name = "t2"
injuriesT2.setAnchor(lytDict["injuries"]["t2"]["anchor"])
injuriesT2.elementPositionX = lytDict["injuries"]["t2"]["coordX"]
injuriesT2.elementPositionY = lytDict["injuries"]["t2"]["coordY"]
injuriesT2.elementRotation = 0
injuriesT2.visible = True
injuriesT2.text = f"(b) Victim Fatalities"
injuriesT2.textSize = 20
injuriesT2Cim = injuriesT2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.8. Export Injuries Layout</h2>

# %% [markdown]
# Get injuries layout CIM

# %%
injuriesLayoutCim = injuriesLayout.getDefinition("V3")  # Injuries layout CIM

# %% [markdown]
# Export injuries layout to disk

# %%
exportCim("layout", injuriesLayout, injuriesLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export injuries layout to PNG (Figure 11)
injuriesLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig11-InjuriesLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">5. Hotspots Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set Hotspots Layout View</h3>

# %% [markdown]
# Close all views and open the hotspots layout

# %%
# Close all previous views
aprx.closeViews()

# Open the hotspots layout view
hotspotsLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in hotspotsLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        hotspotsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %% [markdown]
# Map frames definitions and calculations

# %%
# List of maps to be added as map frames to the layout
hotspotsMfList = [mapFhs100m1km, mapFhs150m2km, mapFhs100m5km, mapFhsRoads500ft]

# Number of map frames
hotspotsMfCount = len(hotspotsMfList)

# Number of rows and columns for the map frames
hotspotsMfCols = 2
hotspotsMfRows = math.ceil(hotspotsMfCount / hotspotsMfCols)

# Map frame page dimensions
hotspotsMfPageWidth = lytDict["hotspots"]["pageWidth"]
hotspotsMfPageHeight = lytDict["hotspots"]["pageHeight"]

# Map frame names
hotspotsMfNames = [f"mf{i}" for i in range(1, hotspotsMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Hot Spots (100m, 1km) map frame (map frame 1)

# %%
# Add the mapframe to the layout
hotspotsMf1 = hotspotsLayout.createMapFrame(
    geometry=lytDict["hotspots"]["mf1"]["geometry"],
    map=hotspotsMfList[0],
    name=f"{hotspotsLayout.name}{hotspotsMfNames[0].title()}",
)

# Set up map frame properties
hotspotsMf1.name = f"{hotspotsLayout.name}{hotspotsMfNames[0].title()}"
hotspotsMf1.setAnchor(lytDict["hotspots"]["mf1"]["anchor"])
hotspotsMf1.elementWidth = lytDict["hotspots"]["mf1"]["width"]
hotspotsMf1.elementHeight = lytDict["hotspots"]["mf1"]["height"]
hotspotsMf1.elementPositionX = lytDict["hotspots"]["mf1"]["coordX"]
hotspotsMf1.elementPositionY = lytDict["hotspots"]["mf1"]["coordY"]
hotspotsMf1.elementRotation = 0
hotspotsMf1.visible = True
hotspotsMf1.map = hotspotsMfList[0]
hotspotsMf1Cim = hotspotsMf1.getDefinition("V3")
hotspotsMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
hotspotsMf1.setDefinition(hotspotsMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Hot Spots (150m, 2km) map frame (map frame 2)

# %%
# Add the mapframe to the layout
hotspotsMf2 = hotspotsLayout.createMapFrame(
    geometry=lytDict["hotspots"]["mf2"]["geometry"],
    map=hotspotsMfList[1],
    name=f"{hotspotsLayout.name}{hotspotsMfNames[1].title()}",
)

# Set up map frame properties
hotspotsMf2.name = f"{hotspotsLayout.name}{hotspotsMfNames[1].title()}"
hotspotsMf2.setAnchor(lytDict["hotspots"]["mf2"]["anchor"])
hotspotsMf2.elementWidth = lytDict["hotspots"]["mf2"]["width"]
hotspotsMf2.elementHeight = lytDict["hotspots"]["mf2"]["height"]
hotspotsMf2.elementPositionX = lytDict["hotspots"]["mf2"]["coordX"]
hotspotsMf2.elementPositionY = lytDict["hotspots"]["mf2"]["coordY"]
hotspotsMf2.elementRotation = 0
hotspotsMf2.visible = True
hotspotsMf2.map = hotspotsMfList[1]
hotspotsMf2Cim = hotspotsMf2.getDefinition("V3")
hotspotsMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
hotspotsMf2.setDefinition(hotspotsMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 3</h3>

# %% [markdown]
# Add Hot Spots (100m, 5km) map frame (map frame 3)

# %%
# Add the mapframe to the layout
hotspotsMf3 = hotspotsLayout.createMapFrame(
    geometry=lytDict["hotspots"]["mf3"]["geometry"],
    map=hotspotsMfList[2],
    name=f"{hotspotsLayout.name}{hotspotsMfNames[2].title()}",
)

# Set up map frame properties
hotspotsMf3.name = f"{hotspotsLayout.name}{hotspotsMfNames[2].title()}"
hotspotsMf3.setAnchor(lytDict["hotspots"]["mf3"]["anchor"])
hotspotsMf3.elementWidth = lytDict["hotspots"]["mf3"]["width"]
hotspotsMf3.elementHeight = lytDict["hotspots"]["mf3"]["height"]
hotspotsMf3.elementPositionX = lytDict["hotspots"]["mf3"]["coordX"]
hotspotsMf3.elementPositionY = lytDict["hotspots"]["mf3"]["coordY"]
hotspotsMf3.elementRotation = 0
hotspotsMf3.visible = True
hotspotsMf3.map = hotspotsMfList[2]
hotspotsMf3Cim = hotspotsMf3.getDefinition("V3")
hotspotsMf3Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
hotspotsMf3.setDefinition(hotspotsMf3Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 4</h3>

# %% [markdown]
# Add Hot Spots (500ft from Major Roads) map frame (map frame 4)

# %%
# Add the mapframe to the layout
hotspotsMf4 = hotspotsLayout.createMapFrame(
    geometry=lytDict["hotspots"]["mf4"]["geometry"],
    map=hotspotsMfList[3],
    name=f"{hotspotsLayout.name}{hotspotsMfNames[3].title()}",
)

# Set up map frame properties
hotspotsMf4.name = f"{hotspotsLayout.name}{hotspotsMfNames[3].title()}"
hotspotsMf4.setAnchor(lytDict["hotspots"]["mf4"]["anchor"])
hotspotsMf4.elementWidth = lytDict["hotspots"]["mf4"]["width"]
hotspotsMf4.elementHeight = lytDict["hotspots"]["mf4"]["height"]
hotspotsMf4.elementPositionX = lytDict["hotspots"]["mf4"]["coordX"]
hotspotsMf4.elementPositionY = lytDict["hotspots"]["mf4"]["coordY"]
hotspotsMf4.elementRotation = 0
hotspotsMf4.visible = True
hotspotsMf4.map = hotspotsMfList[3]
hotspotsMf4Cim = hotspotsMf4.getDefinition("V3")
hotspotsMf4Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
hotspotsMf4.setDefinition(hotspotsMf4Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
hotspotsMf1.camera.setExtent(prjExtent)
hotspotsMf2.camera.setExtent(prjExtent)
hotspotsMf3.camera.setExtent(prjExtent)
hotspotsMf4.camera.setExtent(prjExtent)

# %% [markdown]
# Adjust visibility of the layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in hotspotsLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Crashes Find Hot Spots 100m 1km",
            "OCSWITRS Crashes Find Hot Spots 150m 2km",
            "OCSWITRS Crashes Find Hot Spots 100m 5km",
            "OCSWITRS Crashes Find Hot Spots 500 Feet from Major Roads 500ft 1mi",
            "OCSWITRS Boundaries",
            "OCSWITRS Roads",
            "OCSWITRS Census Blocks",
            "Light Gray Base",
        ]:
            l.visible = True
            if l.name in ["OCSWITRS Census Blocks", "OCSWITRS Roads"]:
                l.transparency = 65
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
hotspotsNa = hotspotsLayout.createMapSurroundElement(
    geometry=lytDict["hotspots"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=hotspotsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
hotspotsNa.name = "na"
hotspotsNa.setAnchor(lytDict["hotspots"]["na"]["anchor"])
hotspotsNa.elementWidth = lytDict["hotspots"]["na"]["width"]
hotspotsNa.elementHeight = lytDict["hotspots"]["na"]["height"]
hotspotsNa.elementPositionX = lytDict["hotspots"]["na"]["coordX"]
hotspotsNa.elementPositionY = lytDict["hotspots"]["na"]["coordY"]
hotspotsNa.elementRotation = 0
hotspotsNa.visible = True
hotspotsNaCim = hotspotsNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
hotspotsSb = hotspotsLayout.createMapSurroundElement(
    geometry=lytDict["hotspots"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=hotspotsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Set scale bar properties

# %%
# Set up scale bar properties
hotspotsSb.name = "sb"
hotspotsSb.setAnchor(lytDict["hotspots"]["sb"]["anchor"])
hotspotsSb.elementWidth = lytDict["hotspots"]["sb"]["width"]
hotspotsSb.elementHeight = lytDict["hotspots"]["sb"]["height"]
hotspotsSb.elementPositionX = lytDict["hotspots"]["sb"]["coordX"]
hotspotsSb.elementPositionY = lytDict["hotspots"]["sb"]["coordY"]
hotspotsSb.elementRotation = 0
hotspotsSb.visible = True
hotspotsSbCim = hotspotsSb.getDefinition("V3")
hotspotsSbCim.labelSymbol.symbol.height = 14
hotspotsSb.setDefinition(hotspotsSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if hotspotsLayout.listElements("TEXT_ELEMENT", "cr"):
    hotspotsLayout.deleteElement("cr")

# Add the credits text to the layout
hotspotsCr = aprx.createTextElement(
    container=hotspotsLayout,
    geometry=lytDict["hotspots"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='hotspots' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
hotspotsCr.name = "cr"
hotspotsCr.setAnchor(lytDict["hotspots"]["cr"]["anchor"])
hotspotsCr.elementPositionX = 0
hotspotsCr.elementPositionY = 0
hotspotsCr.elementRotation = 0
hotspotsCr.visible = False
hotspotsCrCim = hotspotsCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in hotspotsLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        hotspotsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Hotspots Legend</h3>

# %% [markdown]
# Adding Hotspots Legend (legend 1) to the layout

# %%
# Add the legend to the layout
hotspotsLg1 = hotspotsLayout.createMapSurroundElement(
    geometry=lytDict["hotspots"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=hotspotsMf1,
    name="lg1",
)

# %% [markdown]
# Set hotspots legend properties

# %%
# Obtain the CIM object of the legend
hotspotsLg1Cim = hotspotsLg1.getDefinition("V3")

# Disable the legend title
hotspotsLg1Cim.showTitle = False

# Adjust fitting of the legend frame
hotspotsLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the hotspots layer, and turn off the rest of the layers
for i in hotspotsLg1Cim.items:
    if i.name == "OCSWITRS Crashes Find Hot Spots 100m 1km":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
hotspotsLg1.setDefinition(hotspotsLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
hotspotsLg1.name = "lg1"
hotspotsLg1.setAnchor(lytDict["hotspots"]["lg1"]["anchor"])
hotspotsLg1.elementPositionX = lytDict["hotspots"]["lg1"]["coordX"]
hotspotsLg1.elementPositionY = lytDict["hotspots"]["lg1"]["coordY"]
hotspotsLg1.elementRotation = 0
hotspotsLg1.visible = True
hotspotsLg1.mapFrame = hotspotsMf1
hotspotsLg1Cim = hotspotsLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Roads Legend</h3>

# %% [markdown]
# Adding Roads Legend (legend 2) to the layout

# %%
# Add the legend to the layout
hotspotsLg2 = hotspotsLayout.createMapSurroundElement(
    geometry=lytDict["hotspots"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=hotspotsMf1,
    name="lg2",
)

# %% [markdown]
# Set roads legend properties

# %%
# Obtain the CIM object of the legend
hotspotsLg2Cim = hotspotsLg2.getDefinition("V3")

# Disable the legend title
hotspotsLg2Cim.showTitle = False

# Adjust fitting of the legend frame
hotspotsLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in hotspotsLg2Cim.items:
    if i.name == "OCSWITRS Roads":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
hotspotsLg2.setDefinition(hotspotsLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
hotspotsLg2.name = "lg2"
hotspotsLg2.setAnchor(lytDict["hotspots"]["lg2"]["anchor"])
hotspotsLg2.elementPositionX = lytDict["hotspots"]["lg2"]["coordX"]
hotspotsLg2.elementPositionY = lytDict["hotspots"]["lg2"]["coordY"]
hotspotsLg2.elementRotation = 0
hotspotsLg2.visible = True
hotspotsLg2.mapFrame = hotspotsMf1
hotspotsLg2Cim = hotspotsLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 3: Density Legend</h3>

# %% [markdown]
# Adding Density (Cencus Blocks) Legend (legend 3) to the layout

# %%
# Add the legend to the layout
hotspotsLg3 = hotspotsLayout.createMapSurroundElement(
    geometry=lytDict["hotspots"]["lg3"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=hotspotsMf1,
    name="lg3",
)

# %% [markdown]
# Set density legend properties

# %%
# Obtain the CIM object of the legend
hotspotsLg3Cim = hotspotsLg3.getDefinition("V3")

# Disable the legend title
hotspotsLg3Cim.showTitle = False

# Adjust fitting of the legend frame
hotspotsLg3Cim.fittingStrategy = "AdjustFrame"

# Turn on the fhs100m1km layer, and turn off the rest of the layers
for i in hotspotsLg3Cim.items:
    if i.name == "OCSWITRS Census Blocks":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
hotspotsLg3.setDefinition(hotspotsLg3Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
hotspotsLg3.name = "lg3"
hotspotsLg3.setAnchor(lytDict["hotspots"]["lg3"]["anchor"])
hotspotsLg3.elementPositionX = lytDict["hotspots"]["lg3"]["coordX"]
hotspotsLg3.elementPositionY = lytDict["hotspots"]["lg3"]["coordY"]
hotspotsLg3.elementRotation = 0
hotspotsLg3.visible = True
hotspotsLg3.mapFrame = hotspotsMf1
hotspotsLg3Cim = hotspotsLg3.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the hotspots (100m, 1km) map frame (title 1)

# %%
# Check if the fhs100m1km title already exist and if it is, delete it
if hotspotsLayout.listElements("TEXT_ELEMENT", "t1"):
    hotspotsLayout.deleteElement("t1")

# Add the title to the layout
hotspotsT1 = aprx.createTextElement(
    container=hotspotsLayout,
    geometry=lytDict["hotspots"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Crashes Hot Spots (100m Bins, 1km NN)",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
hotspotsT1.name = "t1"
hotspotsT1.setAnchor(lytDict["hotspots"]["t1"]["anchor"])
hotspotsT1.elementPositionX = lytDict["hotspots"]["t1"]["coordX"]
hotspotsT1.elementPositionY = lytDict["hotspots"]["t1"]["coordY"]
hotspotsT1.elementRotation = 0
hotspotsT1.visible = True
hotspotsT1.text = f"(a) Crashes Hot Spots (100m Bins, 1km NN)"
hotspotsT1.textSize = 20
findHotspotsT1Cim = hotspotsT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the hotspots (150m, 2km) map frame (title 2)

# %%
# Check if the fhs150m2km title already exist and if it is, delete it
if hotspotsLayout.listElements("TEXT_ELEMENT", "t2"):
    hotspotsLayout.deleteElement("t2")

# Add the title to the layout
hotspotsT2 = aprx.createTextElement(
    container=hotspotsLayout,
    geometry=lytDict["hotspots"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Crashes Hot Spots (150m Bins, 2km NN)",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
hotspotsT2.name = "t2"
hotspotsT2.setAnchor(lytDict["hotspots"]["t2"]["anchor"])
hotspotsT2.elementPositionX = lytDict["hotspots"]["t2"]["coordX"]
hotspotsT2.elementPositionY = lytDict["hotspots"]["t2"]["coordY"]
hotspotsT2.elementRotation = 0
hotspotsT2.visible = True
hotspotsT2.text = f"(b) Crashes Hot Spots (150m Bins, 2km NN)"
hotspotsT2.textSize = 20
findHotspotsT2Cim = hotspotsT2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 3</h3>

# %% [markdown]
# Add title for for the hotspots (100m, 5km) map frame (title 3)

# %%
# Check if the fhs100m5km title already exist and if it is, delete it
if hotspotsLayout.listElements("TEXT_ELEMENT", "t3"):
    hotspotsLayout.deleteElement("t3")

# Add the title to the layout
hotspotsT3 = aprx.createTextElement(
    container=hotspotsLayout,
    geometry=lytDict["hotspots"]["t3"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t3",
    text_type="POINT",
    text=f"(c) Crashes Hot Spots (100m Bins, 5km NN)",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
hotspotsT3.name = "t3"
hotspotsT3.setAnchor(lytDict["hotspots"]["t3"]["anchor"])
hotspotsT3.elementPositionX = lytDict["hotspots"]["t3"]["coordX"]
hotspotsT3.elementPositionY = lytDict["hotspots"]["t3"]["coordY"]
hotspotsT3.elementRotation = 0
hotspotsT3.visible = True
hotspotsT3.text = f"(c) Crashes Hot Spots (100m Bins, 5km NN)"
hotspotsT3.textSize = 20
hotspotsT3Cim = hotspotsT3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 4</h3>

# %% [markdown]
# Add title for for the hotspots 500ft from major roads map frame (title 4)

# %%
# Check if the fhsRoads500ft title already exist and if it is, delete it
if hotspotsLayout.listElements("TEXT_ELEMENT", "t4"):
    hotspotsLayout.deleteElement("t4")

# Add the title to the layout
hotspotsT4 = aprx.createTextElement(
    container=hotspotsLayout,
    geometry=lytDict["hotspots"]["t4"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t4",
    text_type="POINT",
    text=f"(d) Crashes Hot Spots (500ft from Major Roads)",
)

# %% [markdown]
# Set title properties

# %%
# Set up title properties
hotspotsT4.name = "t4"
hotspotsT4.setAnchor(lytDict["hotspots"]["t4"]["anchor"])
hotspotsT4.elementPositionX = lytDict["hotspots"]["t4"]["coordX"]
hotspotsT4.elementPositionY = lytDict["hotspots"]["t4"]["coordY"]
hotspotsT4.elementRotation = 0
hotspotsT4.visible = True
hotspotsT4.text = f"(d) Crashes Hot Spots (500ft from Major Roads)"
hotspotsT4.textSize = 20
hotspotsT4Cim = hotspotsT4.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">5.8. Export Hotspots Layout</h2>

# %% [markdown]
# Get hotspots layout CIM

# %%
hotspotsLayoutCim = hotspotsLayout.getDefinition("V3")  # Find Hotspots layout CIM

# %% [markdown]
# Export hotspots layout to disk

# %%
exportCim("layout", hotspotsLayout, hotspotsLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export find hotspots layout to PNG (Figure 12)
hotspotsLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig12-HotspotsLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">6. Roads Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set Road Hotspots Layout View</h3>

# %% [markdown]
# Close all views and open the map layout

# %%
# Close all previous views
aprx.closeViews()

# Open the roads layout view
roadsLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in roadsLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        roadsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %% [markdown]
# Map frames definitions and calculations

# %%
# List of maps to be added as map frames to the layout
roadsMfList = [mapRoadCrashes, mapRoadHotspots, mapRoadBuffers, mapRoadSegments]

# Number of map frames
roadsMfCount = len(roadsMfList)

# Number of rows and columns for the map frames
roadsMfCols = 2
roadsMfRows = math.ceil(roadsMfCount / roadsMfCols)

# Map frame page dimensions
roadsMfPageWidth = lytDict["roads"]["pageWidth"]
roadsMfPageHeight = lytDict["roads"]["pageHeight"]

# Map frame names
roadsMfNames = [f"mf{i}" for i in range(1, roadsMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Crashes within 500ft of Major Roads map frame (map frame 1)

# %%
# Add the mapframe to the layout
roadsMf1 = roadsLayout.createMapFrame(
    geometry=lytDict["roads"]["mf1"]["geometry"],
    map=roadsMfList[0],
    name=f"{roadsLayout.name}{roadsMfNames[0].title()}",
)

# Set up map frame properties
roadsMf1.name = f"{roadsLayout.name}{roadsMfNames[0].title()}"
roadsMf1.setAnchor(lytDict["roads"]["mf1"]["anchor"])
roadsMf1.elementWidth = lytDict["roads"]["mf1"]["width"]
roadsMf1.elementHeight = lytDict["roads"]["mf1"]["height"]
roadsMf1.elementPositionX = lytDict["roads"]["mf1"]["coordX"]
roadsMf1.elementPositionY = lytDict["roads"]["mf1"]["coordY"]
roadsMf1.elementRotation = 0
roadsMf1.visible = True
roadsMf1.map = roadsMfList[0]
roadsMf1Cim = roadsMf1.getDefinition("V3")
roadsMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
roadsMf1.setDefinition(roadsMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Crashes Hotspots 500ft of Major Roads map frame (map frame 2)

# %%
# Add the mapframe to the layout
roadsMf2 = roadsLayout.createMapFrame(
    geometry=lytDict["roads"]["mf2"]["geometry"],
    map=roadsMfList[1],
    name=f"{roadsLayout.name}{roadsMfNames[1].title()}",
)

# Set up map frame properties
roadsMf2.name = f"{roadsLayout.name}{roadsMfNames[1].title()}"
roadsMf2.setAnchor(lytDict["roads"]["mf2"]["anchor"])
roadsMf2.elementWidth = lytDict["roads"]["mf2"]["width"]
roadsMf2.elementHeight = lytDict["roads"]["mf2"]["height"]
roadsMf2.elementPositionX = lytDict["roads"]["mf2"]["coordX"]
roadsMf2.elementPositionY = lytDict["roads"]["mf2"]["coordY"]
roadsMf2.elementRotation = 0
roadsMf2.visible = True
roadsMf2.map = roadsMfList[1]
roadsMf2Cim = roadsMf2.getDefinition("V3")
roadsMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
roadsMf2.setDefinition(roadsMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 3</h3>

# %% [markdown]
# Add Major Road and Highway Buffers map frame (map frame 3)

# %%
# Add the mapframe to the layout
roadsMf3 = roadsLayout.createMapFrame(
    geometry=lytDict["roads"]["mf3"]["geometry"],
    map=roadsMfList[2],
    name=f"{roadsLayout.name}{roadsMfNames[2].title()}",
)

# Set up map frame properties
roadsMf3.name = f"{roadsLayout.name}{roadsMfNames[2].title()}"
roadsMf3.setAnchor(lytDict["roads"]["mf3"]["anchor"])
roadsMf3.elementWidth = lytDict["roads"]["mf3"]["width"]
roadsMf3.elementHeight = lytDict["roads"]["mf3"]["height"]
roadsMf3.elementPositionX = lytDict["roads"]["mf3"]["coordX"]
roadsMf3.elementPositionY = lytDict["roads"]["mf3"]["coordY"]
roadsMf3.elementRotation = 0
roadsMf3.visible = True
roadsMf3.map = roadsMfList[2]
roadsMf3Cim = roadsMf3.getDefinition("V3")
roadsMf3Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
roadsMf3.setDefinition(roadsMf3Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 4</h3>

# %% [markdown]
# Add Major Road Segments (1,000ft along lines) map frame (map frame 4)

# %%
# Add the mapframe to the layout
roadsMf4 = roadsLayout.createMapFrame(
    geometry=lytDict["roads"]["mf4"]["geometry"],
    map=roadsMfList[3],
    name=f"{roadsLayout.name}{roadsMfNames[3].title()}",
)

# Set up map frame properties
roadsMf4.name = f"{roadsLayout.name}{roadsMfNames[3].title()}"
roadsMf4.setAnchor(lytDict["roads"]["mf4"]["anchor"])
roadsMf4.elementWidth = lytDict["roads"]["mf4"]["width"]
roadsMf4.elementHeight = lytDict["roads"]["mf4"]["height"]
roadsMf4.elementPositionX = lytDict["roads"]["mf4"]["coordX"]
roadsMf4.elementPositionY = lytDict["roads"]["mf4"]["coordY"]
roadsMf4.elementRotation = 0
roadsMf4.visible = True
roadsMf4.map = roadsMfList[3]
roadsMf4Cim = roadsMf4.getDefinition("V3")
roadsMf4Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
roadsMf4.setDefinition(roadsMf4Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
roadsMf1.camera.setExtent(prjExtent)
roadsMf2.camera.setExtent(prjExtent)
roadsMf3.camera.setExtent(prjExtent)
roadsMf4.camera.setExtent(prjExtent)

# %% [markdown]
# Adjust visibility of the layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in roadsLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Crashes 500 Feet from Major Roads",
            "OCSWITRS Crashes Hot Spots 500 Feet from Major Roads",
            "OCSWITRS Major Roads Buffers Summary",
            "OCSWITRS Major Roads Split Buffer Summary",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
            l.transparency = 0
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
roadsNa = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=roadsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
roadsNa.name = "na"
roadsNa.setAnchor(lytDict["roads"]["na"]["anchor"])
roadsNa.elementWidth = lytDict["roads"]["na"]["width"]
roadsNa.elementHeight = lytDict["roads"]["na"]["height"]
roadsNa.elementPositionX = lytDict["roads"]["na"]["coordX"]
roadsNa.elementPositionY = lytDict["roads"]["na"]["coordY"]
roadsNa.elementRotation = 0
roadsNa.visible = True
roadsNaCim = roadsNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
roadsSb = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=roadsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Set scale bar properties

# %%
# Set up scale bar properties
roadsSb.name = "sb"
roadsSb.setAnchor(lytDict["roads"]["sb"]["anchor"])
roadsSb.elementWidth = lytDict["roads"]["sb"]["width"]
roadsSb.elementHeight = lytDict["roads"]["sb"]["height"]
roadsSb.elementPositionX = lytDict["roads"]["sb"]["coordX"]
roadsSb.elementPositionY = lytDict["roads"]["sb"]["coordY"]
roadsSb.elementRotation = 0
roadsSb.visible = True
roadsSbCim = roadsSb.getDefinition("V3")
roadsSbCim.labelSymbol.symbol.height = 14
roadsSb.setDefinition(roadsSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if roadsLayout.listElements("TEXT_ELEMENT", "cr"):
    roadsLayout.deleteElement("cr")

# Add the credits text to the layout
roadsCr = aprx.createTextElement(
    container=roadsLayout,
    geometry=lytDict["roads"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='roads' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
roadsCr.name = "cr"
roadsCr.setAnchor(lytDict["roads"]["cr"]["anchor"])
roadsCr.elementPositionX = 0
roadsCr.elementPositionY = 0
roadsCr.elementRotation = 0
roadsCr.visible = False
roadsCrCim = roadsCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in roadsLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        roadsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Road Crashes Legend</h3>

# %% [markdown]
# Adding Road Crashes Legend (legend 1) to the layout

# %%
# Add the legend to the layout
roadsLg1 = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=roadsMf1,
    name="lg1",
)

# %% [markdown]
# Set road crashes legend properties

# %%
# Obtain the CIM object of the legend
roadsLg1Cim = roadsLg1.getDefinition("V3")

# Disable the legend title
roadsLg1Cim.showTitle = False

# Adjust fitting of the legend frame
roadsLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in roadsLg1Cim.items:
    if i.name == "OCSWITRS Crashes 500 Feet from Major Roads":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
roadsLg1.setDefinition(roadsLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
roadsLg1.name = "lg1"
roadsLg1.setAnchor(lytDict["roads"]["lg1"]["anchor"])
roadsLg1.elementPositionX = lytDict["roads"]["lg1"]["coordX"]
roadsLg1.elementPositionY = lytDict["roads"]["lg1"]["coordY"]
roadsLg1.elementRotation = 0
roadsLg1.visible = True
roadsLg1.mapFrame = roadsMf1
roadsLg1Cim = roadsLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Road Hotspots Legend</h3>

# %% [markdown]
# Adding Road Hotspots Legend (legend 2) to the layout

# %%
# Add the legend to the layout
roadsLg2 = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=roadsMf2,
    name="lg2",
)

# %% [markdown]
# Set road hotspots legend properties

# %%
# Obtain the CIM object of the legend
roadsLg2Cim = roadsLg2.getDefinition("V3")

# Disable the legend title
roadsLg2Cim.showTitle = False

# Adjust fitting of the legend frame
roadsLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in roadsLg2Cim.items:
    if i.name == "OCSWITRS Crashes Hot Spots 500 Feet from Major Roads":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
roadsLg2.setDefinition(roadsLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
roadsLg2.name = "lg2"
roadsLg2.setAnchor(lytDict["roads"]["lg2"]["anchor"])
roadsLg2.elementPositionX = lytDict["roads"]["lg2"]["coordX"]
roadsLg2.elementPositionY = lytDict["roads"]["lg2"]["coordY"]
roadsLg2.elementRotation = 0
roadsLg2.visible = True
roadsLg2.mapFrame = roadsMf2
roadsLg2Cim = roadsLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 3: Road Buffers Legend</h3>

# %% [markdown]
# Adding Road Buffers Legend (legend 3) to the layout

# %%
# Add the legend to the layout
roadsLg3 = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["lg3"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=roadsMf3,
    name="lg3",
)

# %% [markdown]
# Set road buffers legend properties

# %%
# Obtain the CIM object of the legend
roadsLg3Cim = roadsLg3.getDefinition("V3")

# Disable the legend title
roadsLg3Cim.showTitle = False

# Adjust fitting of the legend frame
roadsLg3Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in roadsLg3Cim.items:
    if i.name == "OCSWITRS Major Roads Buffers Summary":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
roadsLg3.setDefinition(roadsLg3Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
roadsLg3.name = "lg3"
roadsLg3.setAnchor(lytDict["roads"]["lg3"]["anchor"])
roadsLg3.elementPositionX = lytDict["roads"]["lg3"]["coordX"]
roadsLg3.elementPositionY = lytDict["roads"]["lg3"]["coordY"]
roadsLg3.elementRotation = 0
roadsLg3.visible = True
roadsLg3.mapFrame = roadsMf3
roadsLg3Cim = roadsLg3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 4: Road Segments Legend</h3>

# %% [markdown]
# Adding Road Segments Legend (legend 4) to the layout

# %%
# Add the legend to the layout
roadsLg4 = roadsLayout.createMapSurroundElement(
    geometry=lytDict["roads"]["lg4"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=roadsMf4,
    name="lg4",
)

# %% [markdown]
# Set road segments legend properties

# %%
# Obtain the CIM object of the legend
roadsLg4Cim = roadsLg4.getDefinition("V3")

# Disable the legend title
roadsLg4Cim.showTitle = False

# Adjust fitting of the legend frame
roadsLg4Cim.fittingStrategy = "AdjustFrame"

# Turn on the roads layer, and turn off the rest of the layers
for i in roadsLg4Cim.items:
    if i.name == "OCSWITRS Major Roads Split Buffer Summary":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
roadsLg4.setDefinition(roadsLg4Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
roadsLg4.name = "lg4"
roadsLg4.setAnchor(lytDict["roads"]["lg4"]["anchor"])
roadsLg4.elementPositionX = lytDict["roads"]["lg4"]["coordX"]
roadsLg4.elementPositionY = lytDict["roads"]["lg4"]["coordY"]
roadsLg4.elementRotation = 0
roadsLg4.visible = True
roadsLg4.mapFrame = roadsMf4
roadsLg4Cim = roadsLg4.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the crashes within 500ft of major roads map frame (title 1)

# %%
# Check if the fhsRoads500ft title already exist and if it is, delete it
if roadsLayout.listElements("TEXT_ELEMENT", "t1"):
    roadsLayout.deleteElement("t1")

# Add the title to the layout
roadsT1 = aprx.createTextElement(
    container=roadsLayout,
    geometry=lytDict["roads"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Crashes (500ft from Major Roads)",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
roadsT1.name = "t1"
roadsT1.setAnchor(lytDict["roads"]["t1"]["anchor"])
roadsT1.elementPositionX = lytDict["roads"]["t1"]["coordX"]
roadsT1.elementPositionY = lytDict["roads"]["t1"]["coordY"]
roadsT1.elementRotation = 0
roadsT1.visible = True
roadsT1.text = f"(a) Crashes (500ft from Major Roads)"
roadsT1.textSize = 20
roadsT1Cim = roadsT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for the OCSWITRS Crashes Hot Spots 500 Feet from Major Roads map frame (title 2)

# %%
# Check if the fhsRoads500ft title already exist and if it is, delete it
if roadsLayout.listElements("TEXT_ELEMENT", "t2"):
    roadsLayout.deleteElement("t2")

# Add the title to the layout
roadsT2 = aprx.createTextElement(
    container=roadsLayout,
    geometry=lytDict["roads"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Crashes Hot Spots (500ft from Major Roads)",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
roadsT2.name = "t2"
roadsT2.setAnchor(lytDict["roads"]["t2"]["anchor"])
roadsT2.elementPositionX = lytDict["roads"]["t2"]["coordX"]
roadsT2.elementPositionY = lytDict["roads"]["t2"]["coordY"]
roadsT2.elementRotation = 0
roadsT2.visible = True
roadsT2.text = f"(b) Crashes Hot Spots (500ft from Major Roads)"
roadsT2.textSize = 20
roadsT2Cim = roadsT2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 3</h3>

# %% [markdown]
# Add title for the OCSWITRS Major Roads Buffers Summary map frame (title 3)

# %%
# Check if the fhsRoads500ft title already exist and if it is, delete it
if roadsLayout.listElements("TEXT_ELEMENT", "t3"):
    roadsLayout.deleteElement("t3")

# Add the title to the layout
roadsT3 = aprx.createTextElement(
    container=roadsLayout,
    geometry=lytDict["roads"]["t3"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t3",
    text_type="POINT",
    text=f"(c) Major Roads Buffers",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
roadsT3.name = "t3"
roadsT3.setAnchor(lytDict["roads"]["t3"]["anchor"])
roadsT3.elementPositionX = lytDict["roads"]["t3"]["coordX"]
roadsT3.elementPositionY = lytDict["roads"]["t3"]["coordY"]
roadsT3.elementRotation = 0
roadsT3.visible = True
roadsT3.text = f"(c) Major Roads Buffers"
roadsT3.textSize = 20
roadsT3Cim = roadsT3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 4</h3>

# %% [markdown]
# Add title for the OCSWITRS Major Roads Split Buffer Summary map frame (title 4)

# %%
# Check if the fhsRoads500ft title already exist and if it is, delete it
if roadsLayout.listElements("TEXT_ELEMENT", "t4"):
    roadsLayout.deleteElement("t4")

# Add the title to the layout
roadsT4 = aprx.createTextElement(
    container=roadsLayout,
    geometry=lytDict["roads"]["t4"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t4",
    text_type="POINT",
    text=f"(d) Major Road Segments (1,000ft length)",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
roadsT4.name = "t4"
roadsT4.setAnchor(lytDict["roads"]["t4"]["anchor"])
roadsT4.elementPositionX = lytDict["roads"]["t4"]["coordX"]
roadsT4.elementPositionY = lytDict["roads"]["t4"]["coordY"]
roadsT4.elementRotation = 0
roadsT4.visible = True
roadsT4.text = f"(d) Major Road Segments (1,000ft length)"
roadsT4.textSize = 20
roadsT4Cim = roadsT4.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">6.8. Export Road Hotspots Layout</h2>

# %% [markdown]
# Get roads layout CIM

# %%
roadsLayoutCim = roadsLayout.getDefinition("V3")  # Roads layout CIM

# %% [markdown]
# Export roads layout to disk

# %%
exportCim("layout", roadsLayout, roadsLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export roads layout to PNG (Figure 13)
roadsLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig13-RoadsLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">7. Points Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set Optimized Hotspots Layout View</h3>

# %%
# Close all previous views
aprx.closeViews()

# Open the points layout view
pointsLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in pointsLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        pointsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %% [markdown]
# Map frames definitions and calculations

# %%
# List of maps to be added as map frames to the layout
pointsMfList = [mapPointFhs, mapPointOhs]

# Number of map frames
pointsMfCount = len(pointsMfList)

# Number of rows and columns for the map frames
pointsMfCols = 2
pointsMfRows = math.ceil(pointsMfCount / pointsMfCols)

# Map frame page dimensions
pointsMfPageWidth = lytDict["points"]["pageWidth"]
pointsMfPageHeight = lytDict["points"]["pageHeight"]

# Map frame names
pointsMfNames = [f"mf{i}" for i in range(1, pointsMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Hotspot Points map frame (map frame 1)

# %%
# Add the mapframe to the layout
pointsMf1 = pointsLayout.createMapFrame(
    geometry=lytDict["points"]["mf1"]["geometry"],
    map=pointsMfList[0],
    name=f"{pointsLayout.name}{pointsMfNames[0].title()}",
)

# Set up map frame properties
pointsMf1.name = f"{pointsLayout.name}{pointsMfNames[0].title()}"
pointsMf1.setAnchor(lytDict["points"]["mf1"]["anchor"])
pointsMf1.elementWidth = lytDict["points"]["mf1"]["width"]
pointsMf1.elementHeight = lytDict["points"]["mf1"]["height"]
pointsMf1.elementPositionX = lytDict["points"]["mf1"]["coordX"]
pointsMf1.elementPositionY = lytDict["points"]["mf1"]["coordY"]
pointsMf1.elementRotation = 0
pointsMf1.visible = True
pointsMf1.map = pointsMfList[0]
pointsMf1Cim = pointsMf1.getDefinition("V3")
pointsMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
pointsMf1.setDefinition(pointsMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Optimized Hotspot Points map frame (map frame 2)

# %%
# Add the mapframe to the layout
pointsMf2 = pointsLayout.createMapFrame(
    geometry=lytDict["points"]["mf2"]["geometry"],
    map=pointsMfList[1],
    name=f"{pointsLayout.name}{pointsMfNames[1].title()}",
)

# Set up map frame properties
pointsMf2.name = f"{pointsLayout.name}{pointsMfNames[1].title()}"
pointsMf2.setAnchor(lytDict["points"]["mf2"]["anchor"])
pointsMf2.elementWidth = lytDict["points"]["mf2"]["width"]
pointsMf2.elementHeight = lytDict["points"]["mf2"]["height"]
pointsMf2.elementPositionX = lytDict["points"]["mf2"]["coordX"]
pointsMf2.elementPositionY = lytDict["points"]["mf2"]["coordY"]
pointsMf2.elementRotation = 0
pointsMf2.visible = True
pointsMf2.map = pointsMfList[1]
pointsMf2Cim = pointsMf2.getDefinition("V3")
pointsMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
pointsMf2.setDefinition(pointsMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
pointsMf1.camera.setExtent(prjExtent)
pointsMf2.camera.setExtent(prjExtent)

# %% [markdown]
# Adjust visibility of the layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in pointsLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Crashes Hot Spots",
            "OCSWITRS Crashes Optimized Hot Spots",
            "OCSWITRS Roads",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
            l.transparency = 0
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
pointsNa = pointsLayout.createMapSurroundElement(
    geometry=lytDict["points"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=pointsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
pointsNa.name = "na"
pointsNa.setAnchor(lytDict["points"]["na"]["anchor"])
pointsNa.elementWidth = lytDict["points"]["na"]["width"]
pointsNa.elementHeight = lytDict["points"]["na"]["height"]
pointsNa.elementPositionX = lytDict["points"]["na"]["coordX"]
pointsNa.elementPositionY = lytDict["points"]["na"]["coordY"]
pointsNa.elementRotation = 0
pointsNa.visible = True
pointsNaCim = pointsNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
pointsSb = pointsLayout.createMapSurroundElement(
    geometry=lytDict["points"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=pointsMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Add scale bar properties

# %%
# Set up scale bar properties
pointsSb.name = "sb"
pointsSb.setAnchor(lytDict["points"]["sb"]["anchor"])
pointsSb.elementWidth = lytDict["points"]["sb"]["width"]
pointsSb.elementHeight = lytDict["points"]["sb"]["height"]
pointsSb.elementPositionX = lytDict["points"]["sb"]["coordX"]
pointsSb.elementPositionY = lytDict["points"]["sb"]["coordY"]
pointsSb.elementRotation = 0
pointsSb.visible = True
pointsSbCim = pointsSb.getDefinition("V3")
pointsSbCim.labelSymbol.symbol.height = 14
pointsSb.setDefinition(pointsSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if pointsLayout.listElements("TEXT_ELEMENT", "cr"):
    pointsLayout.deleteElement("cr")

# Add the credits text to the layout
pointsCr = aprx.createTextElement(
    container=pointsLayout,
    geometry=lytDict["points"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='points' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
pointsCr.name = "cr"
pointsCr.setAnchor(lytDict["points"]["cr"]["anchor"])
pointsCr.elementPositionX = 0
pointsCr.elementPositionY = 0
pointsCr.elementRotation = 0
pointsCr.visible = False
pointsCrCim = pointsCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in pointsLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        pointsLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Hotspots Points Legend</h3>

# %% [markdown]
# Adding Hotspots Points Legend (legend 1) to the layout

# %%
# Add the legend to the layout
pointsLg1 = pointsLayout.createMapSurroundElement(
    geometry=lytDict["points"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=pointsMf1,
    name="lg1",
)

# %% [markdown]
# Set hotspots points legend properties

# %%
# Obtain the CIM object of the legend
pointsLg1Cim = pointsLg1.getDefinition("V3")

# Disable the legend title
pointsLg1Cim.showTitle = False

# Adjust fitting of the legend frame
pointsLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the hotspots point layer, and turn off the rest of the layers
for i in pointsLg1Cim.items:
    if i.name == "OCSWITRS Crashes Hot Spots":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
pointsLg1.setDefinition(pointsLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
pointsLg1.name = "lg1"
pointsLg1.setAnchor(lytDict["points"]["lg1"]["anchor"])
pointsLg1.elementPositionX = lytDict["points"]["lg1"]["coordX"]
pointsLg1.elementPositionY = lytDict["points"]["lg1"]["coordY"]
pointsLg1.elementRotation = 0
pointsLg1.visible = True
pointsLg1.mapFrame = pointsMf1
pointsLg1Cim = pointsLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Optimized Hotspots Points Legend</h3>

# %% [markdown]
# Adding Optimized Hotspots Points Legend (legend 2) to the layout

# %%
# Add the legend to the layout
pointsLg2 = pointsLayout.createMapSurroundElement(
    geometry=lytDict["points"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=pointsMf2,
    name="lg2",
)

# %% [markdown]
# Set optimized hotspots points legend properties

# %%
# Obtain the CIM object of the legend
pointsLg2Cim = pointsLg2.getDefinition("V3")

# Disable the legend title
pointsLg2Cim.showTitle = False

# Adjust fitting of the legend frame
pointsLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the optimized hotspots point layer, and turn off the rest of the layers
for i in pointsLg2Cim.items:
    if i.name == "OCSWITRS Crashes Optimized Hot Spots":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
pointsLg2.setDefinition(pointsLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
pointsLg2.name = "lg2"
pointsLg2.setAnchor(lytDict["points"]["lg2"]["anchor"])
pointsLg2.elementPositionX = lytDict["points"]["lg2"]["coordX"]
pointsLg2.elementPositionY = lytDict["points"]["lg2"]["coordY"]
pointsLg2.elementRotation = 0
pointsLg2.visible = True
pointsLg2.mapFrame = pointsMf2
pointsLg2Cim = pointsLg2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the hotspots points map frame (title 1)

# %%
# Check if the title already exist and if it is, delete it
if pointsLayout.listElements("TEXT_ELEMENT", "t1"):
    pointsLayout.deleteElement("t1")

# Add the title to the layout
pointsT1 = aprx.createTextElement(
    container=pointsLayout,
    geometry=lytDict["points"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Crashes Hot Spots",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
pointsT1.name = "t1"
pointsT1.setAnchor(lytDict["points"]["t1"]["anchor"])
pointsT1.elementPositionX = lytDict["points"]["t1"]["coordX"]
pointsT1.elementPositionY = lytDict["points"]["t1"]["coordY"]
pointsT1.elementRotation = 0
pointsT1.visible = True
pointsT1.text = f"(a) Crashes Hot Spots"
pointsT1.textSize = 20
pointsT1Cim = pointsT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the optimized hotspots points map frame (title 2)

# %%
# Check if the title already exist and if it is, delete it
if pointsLayout.listElements("TEXT_ELEMENT", "t2"):
    pointsLayout.deleteElement("t2")

# Add the title to the layout
pointsT2 = aprx.createTextElement(
    container=pointsLayout,
    geometry=lytDict["points"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Optimized Crashes Hot Spots",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
pointsT2.name = "t2"
pointsT2.setAnchor(lytDict["points"]["t2"]["anchor"])
pointsT2.elementPositionX = lytDict["points"]["t2"]["coordX"]
pointsT2.elementPositionY = lytDict["points"]["t2"]["coordY"]
pointsT2.elementRotation = 0
pointsT2.visible = True
pointsT2.text = f"(b) Optimized Crashes Hot Spots"
pointsT2.textSize = 20
pointsT2Cim = pointsT2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">7.8. Export Points Hotspots Layout</h2>

# %% [markdown]
# Get points layout CIM

# %%
pointsLayoutCim = pointsLayout.getDefinition("V3")  # Points layout CIM

# %% [markdown]
# Export points layout to disk

# %%
exportCim("layout", pointsLayout, pointsLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export points layout to PNG (Figure 14)
pointsLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig14-PointsLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">8. Density Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set Density Layout View</h3>

# %%
# Close all previous views
aprx.closeViews()

# Open the densities layout view
densityLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in densityLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        densityLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %% [markdown]
# Map frames definitions and calculations

# %%
# List of maps to be added as map frames to the layout
densityMfList = [mapPopDens, mapHouDens]

# Number of map frames
densityMfCount = len(densityMfList)

# Number of rows and columns for the map frames
densityMfCols = 2
densityMfRows = math.ceil(densityMfCount / densityMfCols)

# Map frame page dimensions
densityMfPageWidth = lytDict["density"]["pageWidth"]
densityMfPageHeight = lytDict["density"]["pageHeight"]

# Map frame names
densityMfNames = [f"mf{i}" for i in range(1, densityMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Population Density map frame (map frame 1)

# %%
# Add the mapframe to the layout
densityMf1 = densityLayout.createMapFrame(
    geometry=lytDict["density"]["mf1"]["geometry"],
    map=densityMfList[0],
    name=f"{densityLayout.name}{densityMfNames[0].title()}",
)

# Set up map frame properties
densityMf1.name = f"{densityLayout.name}{densityMfNames[0].title()}"
densityMf1.setAnchor(lytDict["density"]["mf1"]["anchor"])
densityMf1.elementWidth = lytDict["density"]["mf1"]["width"]
densityMf1.elementHeight = lytDict["density"]["mf1"]["height"]
densityMf1.elementPositionX = lytDict["density"]["mf1"]["coordX"]
densityMf1.elementPositionY = lytDict["density"]["mf1"]["coordY"]
densityMf1.elementRotation = 0
densityMf1.visible = True
densityMf1.map = densityMfList[0]
densityMf1Cim = densityMf1.getDefinition("V3")
densityMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
densityMf1.setDefinition(densityMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Housing Density map frame (map frame 2)

# %%
# Add the mapframe to the layout
densityMf2 = densityLayout.createMapFrame(
    geometry=lytDict["density"]["mf2"]["geometry"],
    map=densityMfList[1],
    name=f"{densityLayout.name}{densityMfNames[1].title()}",
)

# Set up map frame properties
densityMf2.name = f"{densityLayout.name}{densityMfNames[1].title()}"
densityMf2.setAnchor(lytDict["density"]["mf2"]["anchor"])
densityMf2.elementWidth = lytDict["density"]["mf2"]["width"]
densityMf2.elementHeight = lytDict["density"]["mf2"]["height"]
densityMf2.elementPositionX = lytDict["density"]["mf2"]["coordX"]
densityMf2.elementPositionY = lytDict["density"]["mf2"]["coordY"]
densityMf2.elementRotation = 0
densityMf2.visible = True
densityMf2.map = densityMfList[1]
densityMf2Cim = densityMf2.getDefinition("V3")
densityMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
densityMf2.setDefinition(densityMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
densityMf1.camera.setExtent(prjExtent)
densityMf2.camera.setExtent(prjExtent)

# %% [markdown]
# Adjust visibility of the layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in densityLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Population Density",
            "OCSWITRS Housing Density",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
            l.transparency = 0
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
densityNa = densityLayout.createMapSurroundElement(
    geometry=lytDict["density"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=densityMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
densityNa.name = "na"
densityNa.setAnchor(lytDict["density"]["na"]["anchor"])
densityNa.elementWidth = lytDict["density"]["na"]["width"]
densityNa.elementHeight = lytDict["density"]["na"]["height"]
densityNa.elementPositionX = lytDict["density"]["na"]["coordX"]
densityNa.elementPositionY = lytDict["density"]["na"]["coordY"]
densityNa.elementRotation = 0
densityNa.visible = True
densityNaCim = densityNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
densitySb = densityLayout.createMapSurroundElement(
    geometry=lytDict["density"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=densityMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Add scale bar properties

# %%
# Set up scale bar properties
densitySb.name = "sb"
densitySb.setAnchor(lytDict["density"]["sb"]["anchor"])
densitySb.elementWidth = lytDict["density"]["sb"]["width"]
densitySb.elementHeight = lytDict["density"]["sb"]["height"]
densitySb.elementPositionX = lytDict["density"]["sb"]["coordX"]
densitySb.elementPositionY = lytDict["density"]["sb"]["coordY"]
densitySb.elementRotation = 0
densitySb.visible = True
densitySbCim = densitySb.getDefinition("V3")
densitySbCim.labelSymbol.symbol.height = 14
densitySb.setDefinition(densitySbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if densityLayout.listElements("TEXT_ELEMENT", "cr"):
    densityLayout.deleteElement("cr")

# Add the credits text to the layout
densityCr = aprx.createTextElement(
    container=densityLayout,
    geometry=lytDict["density"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='density' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
densityCr.name = "cr"
densityCr.setAnchor(lytDict["density"]["cr"]["anchor"])
densityCr.elementPositionX = 0
densityCr.elementPositionY = 0
densityCr.elementRotation = 0
densityCr.visible = False
densityCrCim = densityCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in densityLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        densityLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Population Density Legend</h3>

# %% [markdown]
# Adding Population Density Legend (legend 1) to the layout

# %%
# Add the legend to the layout
densityLg1 = densityLayout.createMapSurroundElement(
    geometry=lytDict["density"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=densityMf1,
    name="lg1",
)

# %% [markdown]
# Set population density legend properties

# %%
# Obtain the CIM object of the legend
densityLg1Cim = densityLg1.getDefinition("V3")

# Disable the legend title
densityLg1Cim.showTitle = False

# Adjust fitting of the legend frame
densityLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the population density layer, and turn off the rest of the layers
for i in densityLg1Cim.items:
    if i.name == "OCSWITRS Population Density":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
densityLg1.setDefinition(densityLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
densityLg1.name = "lg1"
densityLg1.setAnchor(lytDict["density"]["lg1"]["anchor"])
densityLg1.elementPositionX = lytDict["density"]["lg1"]["coordX"]
densityLg1.elementPositionY = lytDict["density"]["lg1"]["coordY"]
densityLg1.elementRotation = 0
densityLg1.visible = True
densityLg1.mapFrame = densityMf1
densityLg1Cim = densityLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Housing Density Legend</h3>

# %% [markdown]
# Adding Housing Density Legend (legend 2) to the layout

# %%
# Add the legend to the layout
densityLg2 = densityLayout.createMapSurroundElement(
    geometry=lytDict["density"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=densityMf2,
    name="lg2",
)

# %% [markdown]
# Set housing density legend properties

# %%
# Obtain the CIM object of the legend
densityLg2Cim = densityLg2.getDefinition("V3")

# Disable the legend title
densityLg2Cim.showTitle = False

# Adjust fitting of the legend frame
densityLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the housing density layer, and turn off the rest of the layers
for i in densityLg2Cim.items:
    if i.name == "OCSWITRS Housing Density":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
densityLg2.setDefinition(densityLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
densityLg2.name = "lg2"
densityLg2.setAnchor(lytDict["density"]["lg2"]["anchor"])
densityLg2.elementPositionX = lytDict["density"]["lg2"]["coordX"]
densityLg2.elementPositionY = lytDict["density"]["lg2"]["coordY"]
densityLg2.elementRotation = 0
densityLg2.visible = True
densityLg2.mapFrame = densityMf2
densityLg2Cim = densityLg2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the population density map frame

# %%
# Check if the title already exist and if it is, delete it
if densityLayout.listElements("TEXT_ELEMENT", "t1"):
    densityLayout.deleteElement("t1")

# Add the title to the layout
densityT1 = aprx.createTextElement(
    container=densityLayout,
    geometry=lytDict["density"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Population Density",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
densityT1.name = "t1"
densityT1.setAnchor(lytDict["density"]["t1"]["anchor"])
densityT1.elementPositionX = lytDict["density"]["t1"]["coordX"]
densityT1.elementPositionY = lytDict["density"]["t1"]["coordY"]
densityT1.elementRotation = 0
densityT1.visible = True
densityT1.text = f"(a) Population Density"
densityT1.textSize = 20
densityT1Cim = densityT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the housing density map frame

# %%
# Check if the title already exist and if it is, delete it
if densityLayout.listElements("TEXT_ELEMENT", "t2"):
    densityLayout.deleteElement("t2")

# Add the title to the layout
densityT2 = aprx.createTextElement(
    container=densityLayout,
    geometry=lytDict["density"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Housing Density",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
densityT2.name = "t2"
densityT2.setAnchor(lytDict["density"]["t2"]["anchor"])
densityT2.elementPositionX = lytDict["density"]["t2"]["coordX"]
densityT2.elementPositionY = lytDict["density"]["t2"]["coordY"]
densityT2.elementRotation = 0
densityT2.visible = True
densityT2.text = f"(b) Housing Density"
densityT2.textSize = 20
densityT2Cim = densityT2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">8.8. Export Densities Layout</h2>

# %% [markdown]
# Get densities layout CIM

# %%
densityLayoutCim = densityLayout.getDefinition("V3")  # Density layout CIM

# %% [markdown]
# Export densities layout to disk

# %%
exportCim("layout", densityLayout, densityLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export density layout to PNG (Figure 15)
densityLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig15-DensityLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">9. Areas Layout Processing</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.1. Layout View</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Set City Areas Layout View</h3>

# %%
# Close all previous views
aprx.closeViews()

# Open the city areas layout view
areasLayout.openView()

# set the main layout as active view
layout = aprx.activeView

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.2. Add Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Map Frames</h3>

# %% [markdown]
# Delete all layout data frames and elements

# %%
# Delete all map frames from the layout
for el in areasLayout.listElements():
    if el.type == "MAPFRAME_ELEMENT":
        print(f"Deleting map frame: {el.name}")
        areasLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame Definitions</h3>

# %% [markdown]
# Map frames definitions and calculations

# %%
# List of maps to be added as map frames to the layout
areasMfList = [mapAreaCities, mapAreaBlocks]

# Number of map frames
areasMfCount = len(areasMfList)

# Number of rows and columns for the map frames
areasMfCols = 2
areasMfRows = math.ceil(areasMfCount / areasMfCols)

# Map frame page dimensions
areasMfPageWidth = lytDict["areas"]["pageWidth"]
areasMfPageHeight = lytDict["areas"]["pageHeight"]

# Map frame names
areasMfNames = [f"mf{i}" for i in range(1, areasMfCount + 1)]

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 1</h3>

# %% [markdown]
# Add Victims by City Areas map frame (map frame 1)

# %%
# Add the mapframe to the layout
areasMf1 = areasLayout.createMapFrame(
    geometry=lytDict["areas"]["mf1"]["geometry"],
    map=areasMfList[0],
    name=f"{areasLayout.name}{areasMfNames[0].title()}",
)

# Set up map frame properties
areasMf1.name = f"{areasLayout.name}{areasMfNames[0].title()}"
areasMf1.setAnchor(lytDict["areas"]["mf1"]["anchor"])
areasMf1.elementWidth = lytDict["areas"]["mf1"]["width"]
areasMf1.elementHeight = lytDict["areas"]["mf1"]["height"]
areasMf1.elementPositionX = lytDict["areas"]["mf1"]["coordX"]
areasMf1.elementPositionY = lytDict["areas"]["mf1"]["coordY"]
areasMf1.elementRotation = 0
areasMf1.visible = True
areasMf1.map = areasMfList[0]
areasMf1Cim = areasMf1.getDefinition("V3")
areasMf1Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
areasMf1.setDefinition(areasMf1Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frame 2</h3>

# %% [markdown]
# Add Victims by Census Blocks map frame (map frame 2)

# %%
# Add the mapframe to the layout
areasMf2 = areasLayout.createMapFrame(
    geometry=lytDict["areas"]["mf2"]["geometry"],
    map=areasMfList[1],
    name=f"{areasLayout.name}{areasMfNames[1].title()}",
)

# Set up map frame properties
areasMf2.name = f"{areasLayout.name}{areasMfNames[1].title()}"
areasMf2.setAnchor(lytDict["areas"]["mf2"]["anchor"])
areasMf2.elementWidth = lytDict["areas"]["mf2"]["width"]
areasMf2.elementHeight = lytDict["areas"]["mf2"]["height"]
areasMf2.elementPositionX = lytDict["areas"]["mf2"]["coordX"]
areasMf2.elementPositionY = lytDict["areas"]["mf2"]["coordY"]
areasMf2.elementRotation = 0
areasMf2.visible = True
areasMf2.map = areasMfList[1]
areasMf2Cim = areasMf2.getDefinition("V3")
areasMf2Cim.graphicFrame.borderSymbol.symbol.symbolLayers[0].enable = False
areasMf2.setDefinition(areasMf2Cim)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Adjust Map Frame Layer Visibility</h3>

# %% [markdown]
# Set extent for the map frame

# %%
areasMf1.camera.setExtent(prjExtent)
areasMf2.camera.setExtent(prjExtent)

# %% [markdown]
# Adjust visibility of the layers

# %%
# Loop through map frames and turn on appropriate layers
for mf in areasLayout.listElements("MAPFRAME_ELEMENT"):
    for l in mf.map.listLayers():
        if l.name in [
            "OCSWITRS Cities Summary",
            "OCSWITRS Census Blocks Summary",
            "OCSWITRS Boundaries",
            "Light Gray Base",
        ]:
            l.visible = True
            l.transparency = 0
        else:
            l.visible = False

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.3. Add North Arrow</h2>

# %% [markdown]
# Adding north arrow

# %%
# Add the North Arrow to the layout
areasNa = areasLayout.createMapSurroundElement(
    geometry=lytDict["areas"]["na"]["geometry"],
    mapsurround_type="NORTH_ARROW",
    mapframe=areasMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "North_Arrow", "ArcGIS North 1")[0],
    name="na",
)

# %% [markdown]
# Set north arrow properties

# %%
# Set up north arrow properties
areasNa.name = "na"
areasNa.setAnchor(lytDict["areas"]["na"]["anchor"])
areasNa.elementWidth = lytDict["areas"]["na"]["width"]
areasNa.elementHeight = lytDict["areas"]["na"]["height"]
areasNa.elementPositionX = lytDict["areas"]["na"]["coordX"]
areasNa.elementPositionY = lytDict["areas"]["na"]["coordY"]
areasNa.elementRotation = 0
areasNa.visible = True
areasNaCim = areasNa.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.4. Add Scale Bar</h2>

# %% [markdown]
# Adding scale bar

# %%
# Add the Scale Bar to the layout
areasSb = areasLayout.createMapSurroundElement(
    geometry=lytDict["areas"]["sb"]["geometry"],
    mapsurround_type="SCALE_BAR",
    mapframe=areasMf1,
    style_item=aprx.listStyleItems("ArcGIS 2D", "SCALE_BAR", "Scale Line 1")[0],
    name="sb",
)

# %% [markdown]
# Add scale bar properties

# %%
# Set up scale bar properties
areasSb.name = "sb"
areasSb.setAnchor(lytDict["areas"]["sb"]["anchor"])
areasSb.elementWidth = lytDict["areas"]["sb"]["width"]
areasSb.elementHeight = lytDict["areas"]["sb"]["height"]
areasSb.elementPositionX = lytDict["areas"]["sb"]["coordX"]
areasSb.elementPositionY = lytDict["areas"]["sb"]["coordY"]
areasSb.elementRotation = 0
areasSb.visible = True
areasSbCim = areasSb.getDefinition("V3")
areasSbCim.labelSymbol.symbol.height = 14
areasSb.setDefinition(areasSbCim)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.5. Add Dynamic Text (Service Layer Credits)</h2>

# %% [markdown]
# Add dynamic text element for the service layer credits

# %%
if areasLayout.listElements("TEXT_ELEMENT", "cr"):
    areasLayout.deleteElement("cr")

# Add the credits text to the layout
areasCr = aprx.createTextElement(
    container=areasLayout,
    geometry=lytDict["areas"]["cr"]["geometry"],
    text_size=6,
    font_family_name="Inter 9pt Regular",
    style_item=None,
    name="cr",
    text_type="POINT",
    text="<dyn type='layout' name='areas' property='serviceLayerCredits'/>",
)

# %% [markdown]
# Set dynamic text properties

# %%
# Set up credits text properties
areasCr.name = "cr"
areasCr.setAnchor(lytDict["areas"]["cr"]["anchor"])
areasCr.elementPositionX = 0
areasCr.elementPositionY = 0
areasCr.elementRotation = 0
areasCr.visible = False
areasCrCim = areasCr.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.6. Add New Legends</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Remove Old Legends</h3>

# %%
# Remove all old legends from the layout
for el in areasLayout.listElements():
    if el.type == "LEGEND_ELEMENT":
        print(f"Deleting legend: {el.name}")
        areasLayout.deleteElement(el)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 1: Victims by City Areas Legend</h3>

# %% [markdown]
# Adding Victims by City Areas Legend (legend 1) to the layout

# %%
# Add the legend to the layout
areasLg1 = areasLayout.createMapSurroundElement(
    geometry=lytDict["areas"]["lg1"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=areasMf1,
    name="lg1",
)

# %% [markdown]
# Set victims by city areas legend properties

# %%
# Obtain the CIM object of the legend
areasLg1Cim = areasLg1.getDefinition("V3")

# Disable the legend title
areasLg1Cim.showTitle = False

# Adjust fitting of the legend frame
areasLg1Cim.fittingStrategy = "AdjustFrame"

# Turn on the area cities layer, and turn off the rest of the layers
for i in areasLg1Cim.items:
    if i.name == "OCSWITRS Cities Summary":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
areasLg1.setDefinition(areasLg1Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
areasLg1.name = "lg1"
areasLg1.setAnchor(lytDict["areas"]["lg1"]["anchor"])
areasLg1.elementPositionX = lytDict["areas"]["lg1"]["coordX"]
areasLg1.elementPositionY = lytDict["areas"]["lg1"]["coordY"]
areasLg1.elementRotation = 0
areasLg1.visible = True
areasLg1.mapFrame = areasMf1
areasLg1Cim = areasLg1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legend 2: Victims by Census Blocks Legend</h3>

# %% [markdown]
# Adding Victims by Census Blocks Legend (legend 2) to the layout

# %%
# Add the legend to the layout
areasLg2 = areasLayout.createMapSurroundElement(
    geometry=lytDict["areas"]["lg2"]["geometry"],
    mapsurround_type="LEGEND",
    mapframe=areasMf2,
    name="lg2",
)

# %% [markdown]
# Set victims by census blocks legend properties

# %%
# Obtain the CIM object of the legend
areasLg2Cim = areasLg2.getDefinition("V3")

# Disable the legend title
areasLg2Cim.showTitle = False

# Adjust fitting of the legend frame
areasLg2Cim.fittingStrategy = "AdjustFrame"

# Turn on the area blocks layer, and turn off the rest of the layers
for i in areasLg2Cim.items:
    if i.name == "OCSWITRS Census Blocks Summary":
        i.isVisible = True
        i.showLayerName = False
        i.autoVisibility = True
        i.keepTogetherOption = "Items"
        i.scaleToPatch = False
        i.headingSymbol.symbol.height = 16
        i.labelSymbol.symbol.height = 14
    else:
        i.isVisible = False

# Update the legend CIM definitions
areasLg2.setDefinition(areasLg2Cim)

# %% [markdown]
# Adjust overall legend properties

# %%
# Set up legend properties
areasLg2.name = "lg2"
areasLg2.setAnchor(lytDict["areas"]["lg2"]["anchor"])
areasLg2.elementPositionX = lytDict["areas"]["lg2"]["coordX"]
areasLg2.elementPositionY = lytDict["areas"]["lg2"]["coordY"]
areasLg2.elementRotation = 0
areasLg2.visible = True
areasLg2.mapFrame = areasMf2
areasLg2Cim = areasLg2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.7. Add Titles for Map Frames</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 1</h3>

# %% [markdown]
# Add title for for the victims by city areas map frame

# %%
# Check if the title already exist and if it is, delete it
if areasLayout.listElements("TEXT_ELEMENT", "t1"):
    areasLayout.deleteElement("t1")

# Add the title to the layout
areasT1 = aprx.createTextElement(
    container=areasLayout,
    geometry=lytDict["areas"]["t1"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t1",
    text_type="POINT",
    text=f"(a) Area Cities",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
areasT1.name = "t1"
areasT1.setAnchor(lytDict["areas"]["t1"]["anchor"])
areasT1.elementPositionX = lytDict["areas"]["t1"]["coordX"]
areasT1.elementPositionY = lytDict["areas"]["t1"]["coordY"]
areasT1.elementRotation = 0
areasT1.visible = True
areasT1.text = f"(a) Area Cities"
areasT1.textSize = 20
areasT1Cim = areasT1.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Title 2</h3>

# %% [markdown]
# Add title for for the victims by census blocks map frame

# %%
# Check if the title already exist and if it is, delete it
if areasLayout.listElements("TEXT_ELEMENT", "t2"):
    areasLayout.deleteElement("t2")

# Add the title to the layout
areasT2 = aprx.createTextElement(
    container=areasLayout,
    geometry=lytDict["areas"]["t2"]["geometry"],
    text_size=20,
    font_family_name="Inter 18pt Medium",
    style_item=None,
    name="t2",
    text_type="POINT",
    text=f"(b) Area Blocks",
)

# %% [markdown]
# Add title properties

# %%
# Set up title properties
areasT2.name = "t2"
areasT2.setAnchor(lytDict["areas"]["t2"]["anchor"])
areasT2.elementPositionX = lytDict["areas"]["t2"]["coordX"]
areasT2.elementPositionY = lytDict["areas"]["t2"]["coordY"]
areasT2.elementRotation = 0
areasT2.visible = True
areasT2.text = f"(b) Area Blocks"
areasT2.textSize = 20
areasT2Cim = areasT2.getDefinition("V3")

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">9.8. Export City Areas Layout</h2>

# %% [markdown]
# Get city areas layout CIM

# %%
areasLayoutCim = areasLayout.getDefinition("V3")  # Areas layout CIM

# %% [markdown]
# Export city areas layout to disk

# %%
exportCim("layout", areasLayout, areasLayout.name)

# %% [markdown]
# Export layout image to the graphics project directory

# %%
# Export areas layout to PNG (Figure 16)
areasLayout.exportToPNG(
    out_png=os.path.join(graphicsFolder, "Fig16-AreasLayout.png"),
    resolution=300,
    color_mode="24-BIT_TRUE_COLOR",
    transparent_background=False,
    embed_color_profile=False,
    clip_to_elements=True,
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %% [markdown]
# <h1 style="font-weight:bold; color:orangered; border-bottom: 2px solid orangered">10. Layout Elements and CIM</h1>

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.1. Maps Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
mapsLayoutMapFrames = mapsLayout.listElements(element_type="MAPFRAME_ELEMENT")
mapsLayoutLegendSet = mapsLayout.listElements(element_type="LEGEND_ELEMENT")
mapsLayoutScaleBars = mapsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
mapsLayoutNorthArrows = mapsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
mapsLayoutTitles = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t*")
mapsLayoutText = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in mapsLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
mapsLayoutMf1 = mapsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="mapsMf1"
)[0]
mapsLayoutMf2 = mapsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="mapsMf2"
)[0]
mapsLayoutMf3 = mapsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="mapsMf3"
)[0]
mapsLayoutMf4 = mapsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="mapsMf4"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
mapsLayoutMf1Cim = mapsLayoutMf1.getDefinition("V3")
mapsLayoutMf2Cim = mapsLayoutMf2.getDefinition("V3")
mapsLayoutMf3Cim = mapsLayoutMf3.getDefinition("V3")
mapsLayoutMf4Cim = mapsLayoutMf4.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in mapsLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
mapsLayoutLg1 = mapsLayout.listElements(element_type="LEGEND_ELEMENT", wildcard="lg1")[
    0
]
mapsLayoutLg2 = mapsLayout.listElements(element_type="LEGEND_ELEMENT", wildcard="lg2")[
    0
]
mapsLayoutLg3 = mapsLayout.listElements(element_type="LEGEND_ELEMENT", wildcard="lg3")[
    0
]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
mapsLayoutLg1Cim = mapsLayoutLg1.getDefinition("V3")
mapsLayoutLg2Cim = mapsLayoutLg2.getDefinition("V3")
mapsLayoutLg3Cim = mapsLayoutLg3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in mapsLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in mapsLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
mapsLayoutSb = mapsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
mapsLayoutNa = mapsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
mapsLayoutSbCim = mapsLayoutSb.getDefinition("V3")
mapsLayoutNaCim = mapsLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in mapsLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in mapsLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
mapsLayoutT1 = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t1")[0]
mapsLayoutT2 = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t2")[0]
mapsLayoutT3 = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t3")[0]
mapsLayoutT4 = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t4")[0]
mapsLayoutCr = mapsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
mapsLayoutT1Cim = mapsLayoutT1.getDefinition("V3")
mapsLayoutT2Cim = mapsLayoutT2.getDefinition("V3")
mapsLayoutT3Cim = mapsLayoutT3.getDefinition("V3")
mapsLayoutT4Cim = mapsLayoutT4.getDefinition("V3")
mapsLayoutCrCim = mapsLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
mapsLayoutCIM = mapsLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", mapsLayout, mapsLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.2. Injuries Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
injuriesLayoutMapFrames = injuriesLayout.listElements(element_type="MAPFRAME_ELEMENT")
injuriesLayoutLegendSet = injuriesLayout.listElements(element_type="LEGEND_ELEMENT")
injuriesLayoutScaleBars = injuriesLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
injuriesLayoutNorthArrows = injuriesLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
injuriesLayoutTitles = injuriesLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t*"
)
injuriesLayoutText = injuriesLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in injuriesLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
injuriesLayoutMf1 = injuriesLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="injuriesMf1"
)[0]
injuriesLayoutMf2 = injuriesLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="injuriesMf2"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
injuriesLayoutMf1Cim = injuriesLayoutMf1.getDefinition("V3")
injuriesLayoutMf2Cim = injuriesLayoutMf2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in injuriesLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
injuriesLayoutLg1 = injuriesLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
injuriesLayoutLg2 = injuriesLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
injuriesLayoutLg1Cim = injuriesLayoutLg1.getDefinition("V3")
injuriesLayoutLg2Cim = injuriesLayoutLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in injuriesLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in injuriesLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
injuriesLayoutSb = injuriesLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
injuriesLayoutNa = injuriesLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
injuriesLayoutSbCim = injuriesLayoutSb.getDefinition("V3")
injuriesLayoutNaCim = injuriesLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in injuriesLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in injuriesLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
injuriesLayoutT1 = injuriesLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t1"
)[0]
injuriesLayoutT2 = injuriesLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t2"
)[0]
injuriesLayoutCr = injuriesLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
injuriesLayoutT1Cim = injuriesLayoutT1.getDefinition("V3")
injuriesLayoutT2Cim = injuriesLayoutT2.getDefinition("V3")
injuriesLayoutCrCim = injuriesLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
injuriesLayoutCIM = injuriesLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", injuriesLayout, injuriesLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.3. Hotspots Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
hotspotsLayoutMapFrames = hotspotsLayout.listElements(element_type="MAPFRAME_ELEMENT")
hotspotsLayoutLegendSet = hotspotsLayout.listElements(element_type="LEGEND_ELEMENT")
hotspotsLayoutScaleBars = hotspotsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
hotspotsLayoutNorthArrows = hotspotsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
hotspotsLayoutTitles = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t*"
)
hotspotsLayoutText = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in hotspotsLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
hotspotsLayoutMf1 = hotspotsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="hotspotsMf1"
)[0]
hotspotsLayoutMf2 = hotspotsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="hotspotsMf2"
)[0]
hotspotsLayoutMf3 = hotspotsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="hotspotsMf3"
)[0]
hotspotsLayoutMf4 = hotspotsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="hotspotsMf4"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
hotspotsLayoutMf1Cim = hotspotsLayoutMf1.getDefinition("V3")
hotspotsLayoutMf2Cim = hotspotsLayoutMf2.getDefinition("V3")
hotspotsLayoutMf3Cim = hotspotsLayoutMf3.getDefinition("V3")
hotspotsLayoutMf4Cim = hotspotsLayoutMf4.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in hotspotsLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
hotspotsLayoutLg1 = hotspotsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
hotspotsLayoutLg2 = hotspotsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]
hotspotsLayoutLg3 = hotspotsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg3"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
hotspotsLayoutLg1Cim = hotspotsLayoutLg1.getDefinition("V3")
hotspotsLayoutLg2Cim = hotspotsLayoutLg2.getDefinition("V3")
hotspotsLayoutLg3Cim = hotspotsLayoutLg3.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in hotspotsLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in hotspotsLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
hotspotsLayoutSb = hotspotsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
hotspotsLayoutNa = hotspotsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
hotspotsLayoutSbCim = hotspotsLayoutSb.getDefinition("V3")
hotspotsLayoutNaCim = hotspotsLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in hotspotsLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in hotspotsLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
hotspotsLayoutT1 = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t1"
)[0]
hotspotsLayoutT2 = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t2"
)[0]
hotspotsLayoutT3 = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t3"
)[0]
hotspotsLayoutT4 = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t4"
)[0]
hotspotsLayoutCr = hotspotsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
hotspotsLayoutT1Cim = hotspotsLayoutT1.getDefinition("V3")
hotspotsLayoutT2Cim = hotspotsLayoutT2.getDefinition("V3")
hotspotsLayoutT3Cim = hotspotsLayoutT3.getDefinition("V3")
hotspotsLayoutT4Cim = hotspotsLayoutT4.getDefinition("V3")
hotspotsLayoutCrCim = hotspotsLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
hotspotsLayoutCIM = hotspotsLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", hotspotsLayout, hotspotsLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.4. Roads Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
roadsLayoutMapFrames = roadsLayout.listElements(element_type="MAPFRAME_ELEMENT")
roadsLayoutLegendSet = roadsLayout.listElements(element_type="LEGEND_ELEMENT")
roadsLayoutScaleBars = roadsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
roadsLayoutNorthArrows = roadsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
roadsLayoutTitles = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t*")
roadsLayoutText = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in roadsLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
roadsLayoutMf1 = roadsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="roadsMf1"
)[0]
roadsLayoutMf2 = roadsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="roadsMf2"
)[0]
roadsLayoutMf3 = roadsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="roadsMf3"
)[0]
roadsLayoutMf4 = roadsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="roadsMf4"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
roadsLayoutMf1Cim = roadsLayoutMf1.getDefinition("V3")
roadsLayoutMf2Cim = roadsLayoutMf2.getDefinition("V3")
roadsLayoutMf3Cim = roadsLayoutMf3.getDefinition("V3")
roadsLayoutMf4Cim = roadsLayoutMf4.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in roadsLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
roadsLayoutLg1 = roadsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
roadsLayoutLg2 = roadsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]
roadsLayoutLg3 = roadsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg3"
)[0]
roadsLayoutLg4 = roadsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg4"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
roadsLayoutLg1Cim = roadsLayoutLg1.getDefinition("V3")
roadsLayoutLg2Cim = roadsLayoutLg2.getDefinition("V3")
roadsLayoutLg3Cim = roadsLayoutLg3.getDefinition("V3")
roadsLayoutLg4Cim = roadsLayoutLg4.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in roadsLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in roadsLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
roadsLayoutSb = roadsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
roadsLayoutNa = roadsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
roadsLayoutSbCim = roadsLayoutSb.getDefinition("V3")
roadsLayoutNaCim = roadsLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in roadsLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in roadsLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
roadsLayoutT1 = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t1")[0]
roadsLayoutT2 = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t2")[0]
roadsLayoutT3 = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t3")[0]
roadsLayoutT4 = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t4")[0]
roadsLayoutCr = roadsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
roadsLayoutT1Cim = roadsLayoutT1.getDefinition("V3")
roadsLayoutT2Cim = roadsLayoutT2.getDefinition("V3")
roadsLayoutT3Cim = roadsLayoutT3.getDefinition("V3")
roadsLayoutT4Cim = roadsLayoutT4.getDefinition("V3")
roadsLayoutCrCim = roadsLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
roadsLayoutCIM = roadsLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", roadsLayout, roadsLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.5. Points Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
pointsLayoutMapFrames = pointsLayout.listElements(element_type="MAPFRAME_ELEMENT")
pointsLayoutLegendSet = pointsLayout.listElements(element_type="LEGEND_ELEMENT")
pointsLayoutScaleBars = pointsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
pointsLayoutNorthArrows = pointsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
pointsLayoutTitles = pointsLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t*"
)
pointsLayoutText = pointsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in pointsLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
pointsLayoutMf1 = pointsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="pointsMf1"
)[0]
pointsLayoutMf2 = pointsLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="pointsMf2"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
pointsLayoutMf1Cim = pointsLayoutMf1.getDefinition("V3")
pointsLayoutMf2Cim = pointsLayoutMf2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in pointsLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
pointsLayoutLg1 = pointsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
pointsLayoutLg2 = pointsLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
pointsLayoutLg1Cim = pointsLayoutLg1.getDefinition("V3")
pointsLayoutLg2Cim = pointsLayoutLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in pointsLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in pointsLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
pointsLayoutSb = pointsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
pointsLayoutNa = pointsLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
pointsLayoutSbCim = pointsLayoutSb.getDefinition("V3")
pointsLayoutNaCim = pointsLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in pointsLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in pointsLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
pointsLayoutT1 = pointsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t1")[
    0
]
pointsLayoutT2 = pointsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t2")[
    0
]
pointsLayoutCr = pointsLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")[
    0
]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
pointsLayoutT1Cim = pointsLayoutT1.getDefinition("V3")
pointsLayoutT2Cim = pointsLayoutT2.getDefinition("V3")
pointsLayoutCrCim = pointsLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
pointsLayoutCIM = pointsLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", pointsLayout, pointsLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.6. Density Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
densityLayoutMapFrames = densityLayout.listElements(element_type="MAPFRAME_ELEMENT")
densityLayoutLegendSet = densityLayout.listElements(element_type="LEGEND_ELEMENT")
densityLayoutScaleBars = densityLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
densityLayoutNorthArrows = densityLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
densityLayoutTitles = densityLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t*"
)
densityLayoutText = densityLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in densityLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
densityLayoutMf1 = densityLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="densityMf1"
)[0]
densityLayoutMf2 = densityLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="densityMf2"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
densityLayoutMf1Cim = densityLayoutMf1.getDefinition("V3")
densityLayoutMf2Cim = densityLayoutMf2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in densityLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
densityLayoutLg1 = densityLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
densityLayoutLg2 = densityLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
densityLayoutLg1Cim = densityLayoutLg1.getDefinition("V3")
densityLayoutLg2Cim = densityLayoutLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in densityLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in densityLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
densityLayoutSb = densityLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
densityLayoutNa = densityLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
densityLayoutSbCim = densityLayoutSb.getDefinition("V3")
densityLayoutNaCim = densityLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in densityLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in densityLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
densityLayoutT1 = densityLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t1"
)[0]
densityLayoutT2 = densityLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="t2"
)[0]
densityLayoutCr = densityLayout.listElements(
    element_type="TEXT_ELEMENT", wildcard="cr"
)[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
densityLayoutT1Cim = densityLayoutT1.getDefinition("V3")
densityLayoutT2Cim = densityLayoutT2.getDefinition("V3")
densityLayoutCrCim = densityLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
densityLayoutCIM = densityLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", densityLayout, densityLayout.name)

# %% [markdown]
# <h2 style="font-weight:bold; color:dodgerblue; border-bottom: 1px solid dodgerblue; padding-left: 25px">4.7. Areas Layout Elements</h2>

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout Elements</h3>

# %% [markdown]
# Get all the elements of the layout by element type and functionality

# %%
# Layout element lists
areasLayoutMapFrames = areasLayout.listElements(element_type="MAPFRAME_ELEMENT")
areasLayoutLegendSet = areasLayout.listElements(element_type="LEGEND_ELEMENT")
areasLayoutScaleBars = areasLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)
areasLayoutNorthArrows = areasLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)
areasLayoutTitles = areasLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t*")
areasLayoutText = areasLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Map Frames</h3>

# %% [markdown]
# Get the map frames of the layout elements

# %%
# List map frames
print(f"Map Frames:")
for i in areasLayoutMapFrames:
    print(f"- {i.name}")

# %%
# Get map frames
areasLayoutMf1 = areasLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="areasMf1"
)[0]
areasLayoutMf2 = areasLayout.listElements(
    element_type="MAPFRAME_ELEMENT", wildcard="areasMf2"
)[0]

# %% [markdown]
# Get the map frame CIM objects for each map frame

# %%
# get map frame CIMs
areasLayoutMf1Cim = areasLayoutMf1.getDefinition("V3")
areasLayoutMf2Cim = areasLayoutMf2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Legends</h3>

# %% [markdown]
# Get the legends of the layout

# %%
# List legends
print(f"Legends:")
for i in areasLayoutLegendSet:
    print(f"- {i.name}")

# %%
# Get legends
areasLayoutLg1 = areasLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg1"
)[0]
areasLayoutLg2 = areasLayout.listElements(
    element_type="LEGEND_ELEMENT", wildcard="lg2"
)[0]

# %% [markdown]
# Get the legend CIM objects for each legend

# %%
# Get legend CIMs
areasLayoutLg1Cim = areasLayoutLg1.getDefinition("V3")
areasLayoutLg2Cim = areasLayoutLg2.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Scale Bar and North Arrow</h3>

# %% [markdown]
# Get the scale bar and north arrow of the layout

# %%
# List scale bars
print(f"Scale Bars:")
for i in areasLayoutScaleBars:
    print(f"- {i.name}")

# List north arrows
print(f"North Arrows:")
for i in areasLayoutNorthArrows:
    print(f"- {i.name}")

# %%
# Get scale bars and north arrows
areasLayoutSb = areasLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="sb"
)[0]
areasLayoutNa = areasLayout.listElements(
    element_type="MAPSURROUND_ELEMENT", wildcard="na"
)[0]

# %% [markdown]
# Get the scale bar and north arrow CIM objects

# %%
# Get scale bar and north arrow CIMs
areasLayoutSbCim = areasLayoutSb.getDefinition("V3")
areasLayoutNaCim = areasLayoutNa.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Titles and Text Elements</h3>

# %% [markdown]
# Get the titles and text elements of the layout

# %%
# List titles
print(f"Titles:")
for i in areasLayoutTitles:
    print(f"- {i.name}")

# List text
print(f"Text:")
for i in areasLayoutText:
    print(f"- {i.name}")

# %%
# Get titles and text
areasLayoutT1 = areasLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t1")[0]
areasLayoutT2 = areasLayout.listElements(element_type="TEXT_ELEMENT", wildcard="t2")[0]
areasLayoutCr = areasLayout.listElements(element_type="TEXT_ELEMENT", wildcard="cr")[0]

# %% [markdown]
# Get the title and text CIM objects

# %%
# Get title and text CIMs
areasLayoutT1Cim = areasLayoutT1.getDefinition("V3")
areasLayoutT2Cim = areasLayoutT2.getDefinition("V3")
areasLayoutCrCim = areasLayoutCr.getDefinition("V3")

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Layout CIM</h3>

# %% [markdown]
# Get the layout CIM object

# %%
# layout CIM
areasLayoutCIM = areasLayout.getDefinition("V3")

# %% [markdown]
# Export the layout CIM to disk

# %%
# Export CIM to disk
exportCim("layout", areasLayout, areasLayout.name)

# %% [markdown]
# <h3 style="font-weight:bold; color:lime; padding-left: 50px">Save Project</h3>

# %%
# Save the project
aprx.save()

# %%
gisDataFolder = os.path.join(projectFolder, "Data", "GIS")

# %%
arcpy.conversion.FeatureClassToShapefile(collisions, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(crashes, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(parties, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(victims, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(roads, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(cities, gisDataFolder)
arcpy.conversion.FeatureClassToShapefile(blocks, gisDataFolder)

# %% [markdown]
# <div style = "background-color:indigo"><center>
# <h1 style="font-weight:bold; color:goldenrod; border-top: 2px solid goldenrod; border-bottom: 2px solid goldenrod; padding-top: 5px; padding-bottom: 10px">End of Script</h1>
# </center></div>


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region End of Script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nEnd of Script")
