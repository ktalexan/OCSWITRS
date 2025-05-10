# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OC SWITRS GIS Data Processing
# Part 2 - Map Processing
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOC SWITRS GIS Data Processing - Part 2 - Maps Processing\n")


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

# important as it "enhances" Pandas by importing these classes (from ArcGIS API for Python)
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# endregion 1.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.2. Project and Workspace Variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.2. Project and Workspace Variables")

# Define and maintain project, workspace, ArcGIS, and data-related variables


# region Project and Geodatabase Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project and Geodatabase Paths")

# Define the ArcGIS pro project variables

# Parent project Directory
projectFolder = os.path.dirname(os.getcwd())

# Current notebook directory
notebookDir = os.path.join(projectFolder, "notebooks")

# endregion


# region ArcGIS Pro Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Codebook")

# Load the JSON file from directory and store it in a variable
with open(codebookPath) as jsonFile:
    codebook = json.load(jsonFile)

# endregion


# region JSON CIM Exports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# region 1.4. Map List
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.4. Map List")


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
layoutList = ["maps", "injuries", "hotspots", "roads", "points", "densities", "areas"]

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
# endregion 1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2. Project Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. Project Maps")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.1. Setup Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.1. Setup Maps")


# region Remove Old Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Remove Old Maps")

# First delete all raw data maps from ArcGIS pro current project
if aprx.listMaps():
    for m in aprx.listMaps():
        if m.name in mapList:
            print(f"Removing {m.name} map from the project...")
            aprx.deleteItem(m)
        else:
            print(f"Map {m.name} is not in the list of maps to be created.")
else:
    print("No maps are currently in the project.")

# endregion


# region Create New Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create New Maps")

# Create new raw data maps in current ArcGIS Pro project

# for each of the maps in the list, if it exists, delete it
c = 1
for m in mapList:
    for i in aprx.listMaps():
        if i.name == m:
            print(f"Deleting map: {m}")
            aprx.deleteItem(i)
    # Create new maps
    print(f"Creating map {c}: {m}")
    aprx.createMap(m)
    c += 1

# Store the map objects in variables

# OCSWITRS Data Maps
mapCollisions = aprx.listMaps("collisions")[0]
mapCrashes = aprx.listMaps("crashes")[0]
mapParties = aprx.listMaps("parties")[0]
mapVictims = aprx.listMaps("victims")[0]
mapInjuries = aprx.listMaps("injuries")[0]
mapFatalities = aprx.listMaps("fatalities")[0]

# OCSWITRS Hotspot Maps
mapFhs100m1km = aprx.listMaps("fhs100m1km")[0]
mapFhs150m2km = aprx.listMaps("fhs150m2km")[0]
mapFhs100m5km = aprx.listMaps("fhs100m5km")[0]
mapFhsRoads500ft = aprx.listMaps("fhsRoads500ft")[0]
mapOhsRoads500ft = aprx.listMaps("ohsRoads500ft")[0]
mapPointFhs = aprx.listMaps("pointFhs")[0]
mapPointOhs = aprx.listMaps("pointOhs")[0]

# OCSWITRS Supporting Data Maps
mapRoads = aprx.listMaps("roads")[0]
mapRoadCrashes = aprx.listMaps("roadCrashes")[0]
mapRoadHotspots = aprx.listMaps("roadHotspots")[0]
mapRoadBuffers = aprx.listMaps("roadBuffers")[0]
mapRoadSegments = aprx.listMaps("roadSegments")[0]
mapPopDens = aprx.listMaps("popDens")[0]
mapHouDens = aprx.listMaps("houDens")[0]
mapAreaCities = aprx.listMaps("areaCities")[0]
mapAreaBlocks = aprx.listMaps("areaBlocks")[0]

# OCSWITRS Analysis and Processing Maps
mapSummaries = aprx.listMaps("summaries")[0]
mapAnalysis = aprx.listMaps("analysis")[0]
mapRegression = aprx.listMaps("regression")[0]

# endregion


# region Change Map Basemaps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Change Map Basemaps")

# For each map, replace the existing basemap ("Topographic") with the "Dark Gray Canvas" basemap
for m in aprx.listMaps():
    print(f"Map: {m.name}")
    for l in m.listLayers():
        if l.isBasemapLayer:
            print(f"  - Removing Basemap: {l.name}")
            m.removeLayer(l)
    print(f"  - Adding Basemap: Light Gray Canvas")
    m.addBasemap("Light Gray Canvas")

# Turn off the basemap reference layer for all maps
for m in aprx.listMaps():
    print(f"Map: {m.name}")
    for l in m.listLayers():
        if l.name == "Light Gray Reference":
            l.visible = False

# endregion
# endregion 2.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.2. Map Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.2. Map Metadata")


# region Collisions Map 1 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Collisions Map 1 Metadata")

# Create a new metadata object for the collisions map and assign it to the map
mdoMapCollisions = md.Metadata()
mdoMapCollisions.title = "OCSWITRS Collisions Map"
mdoMapCollisions.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transporation"
mdoMapCollisions.summary = f"Statewide Integrated Traffic Records System (SWITRS) Collisions Map for Orange County, California ({mdYears})"
mdoMapCollisions.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapCollisions.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapCollisions.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapCollisions.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapCollisions.metadata = mdoMapCollisions

# endregion


# region Crashes Map 2 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes Map 2 Metadata")

# Create a new metadata object for the crashes map and assign it to the map
mdoMapCrashes = md.Metadata()
mdoMapCrashes.title = "OCSWITRS Crashes Map"
mdoMapCrashes.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapCrashes.summary = f"Statewide Integrated Traffic Records System (SWITRS) Crashes Map for Orange County, California ({mdYears})"
mdoMapCrashes.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on crashes</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapCrashes.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapCrashes.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapCrashes.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapCrashes.metadata = mdoMapCrashes

# endregion


# region Parties Map 3 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Parties Map 3 Metadata")

# Create a new metadata object for the parties map and assign it to the map
mdoMapParties = md.Metadata()
mdoMapParties.title = "OCSWITRS Parties Map"
mdoMapParties.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Parties, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapParties.summary = f"Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Parties Data for Orange County, California ({mdYears})"
mdoMapParties.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on parties involved in crash incidents</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapParties_credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapParties.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapParties.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/1e07bb1002f9457fa6fd3540fdb08e29/data"

# Apply the metadata to the map
mapParties.metadata = mdoMapParties

# endregion


# region Victims Map 4 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims Map 4 Metadata")

# Create a new metadata object for the victims map and assign it to the map
mdoMapVictims = md.Metadata()
mdoMapVictims.title = "OCSWITRS Victims Map"
mdoMapVictims.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Victims, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapVictims.summary = f"Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Victims Data for Orange County, California ({mdYears})"
mdoMapVictims.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on victims/persons involved in crash incidents</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapVictims.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapVictims.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapVictims.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/78682395df4744009c58625f1db0c25b/data"

# Apply the metadata to the map
mapVictims.metadata = mdoMapVictims

# endregion


# region Injuries Map 5 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Injuries Map 5 Metadata")

# Create a new metadata object for the injuries map and assign it to the map
mdoMapInjuries = md.Metadata()
mdoMapInjuries.title = "OCSWITRS Injuries Map"
mdoMapInjuries.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Injuries, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapInjuries.summary = f"Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Injuries Data for Orange County, California ({mdYears})"
mdoMapInjuries.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on injuries sustained by victims in crash incidents</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapInjuries.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapInjuries.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapInjuries.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/78682395df4744009c58625f1db0c25b/data"

# Apply the metadata to the map
mapInjuries.metadata = mdoMapInjuries

# endregion


# region Fatalities Map 6 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Fatalities Map 6 Metadata")

# Create a new metadata object for the fatalities map and assign it to the map
mdoMapFatalities = md.Metadata()
mdoMapFatalities.title = "OCSWITRS Fatalities Map"
mdoMapFatalities.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transporation"
mdoMapFatalities.summary = f"Statewide Integrated Traffic Records System (SWITRS) Fatalities Map for Orange County, California ({mdYears})"
mdoMapFatalities.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">victim fatality counts per accident in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapFatalities.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapFatalities.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapFatalities.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapFatalities.metadata = mdoMapFatalities

# endregion


# region Hotspots (100m, 1km) Map 7 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspots (100m, 1km) Map 7 Metadata")

# Create a new metadata object for the hotspots (100m, 1km) map and assign it to the map
mdoMapFhs100m1km = md.Metadata()
mdoMapFhs100m1km.title = "OCSWITRS Hot Spot Analysis 100m 1km Map"
mdoMapFhs100m1km.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapFhs100m1km.summary = f"Statewide Integrated Traffic Records System (SWITRS) Hot Spot Analysis 100m 1km Map for Orange County, California ({mdYears})"
mdoMapFhs100m1km.description = """<div style="text-align:Left;"><div><div><p><span>Hot Spot Analysis for the OCSWITRS Project Data using 100m bins and 1km neighborhood radius grid</span></p></div></div></div>"""
mdoMapFhs100m1km.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapFhs100m1km.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapFhs100m1km.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapFhs100m1km.metadata = mdoMapFhs100m1km

# endregion


# region Hotspots (150m, 2km) Map 8 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspots (150m, 2km) Map 8 Metadata")

# Create a new metadata object for the hotspots (150m, 2km) map and assign it to the map
mdoMapFhs150m2km = md.Metadata()
mdoMapFhs150m2km.title = "OCSWITRS Hot Spot Analysis 150m 2km Map"
mdoMapFhs150m2km.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapFhs150m2km.summary = f"Statewide Integrated Traffic Records System (SWITRS) Hot Spot Analysis 150m 2km Map for Orange County, California ({mdYears})"
mdoMapFhs150m2km.description = """<div style="text-align:Left;"><div><div><p><span>Hot Spot Analysis for the OCSWITRS Project Data using 150m bins and 2km neighborhood radius grid</span></p></div></div></div>"""
mdoMapFhs150m2km.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapFhs150m2km.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapFhs150m2km.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapFhs150m2km.metadata = mdoMapFhs150m2km

# endregion


# region Hotspots (100m, 5km) Map 9 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspots (100m, 5km) Map 9 Metadata")

# Create a new metadata object for the hotspots (100m, 5km) map and assign it to the map
mdoMapFhs100m5km = md.Metadata()
mdoMapFhs100m5km.title = "OCSWITRS Hot Spot Analysis 100m 5km Map"
mdoMapFhs100m5km.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapFhs100m5km.summary = f"Statewide Integrated Traffic Records System (SWITRS) Hot Spot Analysis 100m 5km Map for Orange County, California ({mdYears})"
mdoMapFhs100m5km.description = """<div style="text-align:Left;"><div><div><p><span>Hot Spot Analysis for the OCSWITRS Project Data using 100m bins and 5km neighborhood radius grid</span></p></div></div></div>"""
mdoMapFhs100m5km.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapFhs100m5km.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapFhs100m5km.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapFhs100m5km.metadata = mdoMapFhs100m5km

# endregion


# region Hotspots 500ft from Major Roads Map 10 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspots 500ft from Major Roads Map 10 Metadata")

# Create a new metadata object for the hotspots 500ft from major roads map and assign it to the map
mdoMapFhsRoads500ft = md.Metadata()
mdoMapFhsRoads500ft.title = "OCSWITRS Hot Spots within 500ft from Major Roads Map"
mdoMapFhsRoads500ft.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapFhsRoads500ft.summary = f"Statewide Integrated Traffic Records System (SWITRS) Hot Spots within 500ft from Major Roads Map for Orange County, California ({mdYears})"
mdoMapFhsRoads500ft.description = """<div style="text-align:Left;"><div><div><p><span>Hot Spot Analysis for the OCSWITRS Project Data within 500ft from Major Roads</span></p></div></div></div>"""
mdoMapFhsRoads500ft.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapFhsRoads500ft.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapFhsRoads500ft.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapFhsRoads500ft.metadata = mdoMapFhsRoads500ft

# endregion


# region Optimized Hotspots 500ft from Major Roads Map 11 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Optimized Hotspots 500ft from Major Roads Map 11 Metadata")

# Create a new metadata object for the optimized hotspots 500ft from major roads map and assign it to the map
mdoMapOhsRoads500ft = md.Metadata()
mdoMapOhsRoads500ft.title = (
    "OCSWITRS Optimized Hot Spots within 500ft from Major Roads Map"
)
mdoMapOhsRoads500ft.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapOhsRoads500ft.summary = f"Statewide Integrated Traffic Records System (SWITRS) Optimized Hot Spots within 500ft from Major Roads Map for Orange County, California ({mdYears})"
mdoMapOhsRoads500ft.description = """<div style="text-align:Left;"><div><div><p><span>Optimized Hot Spot Analysis for the OCSWITRS Project Data within 500ft from Major Roads</span></p></div></div></div>"""
mdoMapOhsRoads500ft.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapOhsRoads500ft.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapOhsRoads500ft.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapOhsRoads500ft.metadata = mdoMapOhsRoads500ft

# endregion


# region Major Road Crashes Map 12 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Crashes Map 12 Metadata")

# Create a new metadata object for the major road crashes map and assign it to the map
mdoMapRoadCrashes = md.Metadata()
mdoMapRoadCrashes.title = "OCSWITRS Major Road Crashes Map"
mdoMapRoadCrashes.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapRoadCrashes.summary = f"Statewide Integrated Traffic Records System (SWITRS) Road Crashes Map for Orange County, California ({mdYears})"
mdoMapRoadCrashes.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on road crashes in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapRoadCrashes.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRoadCrashes.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRoadCrashes.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapRoadCrashes.metadata = mdoMapRoadCrashes

# endregion


# region Major Road Hotspots Map 13 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Hotspots Map 13 Metadata")

# Create a new metadata object for the major road hotspots map and assign it to the map
mdoMapRoadHotspots = md.Metadata()
mdoMapRoadHotspots.title = "OCSWITRS Major Road Hotspots Map"
mdoMapRoadHotspots.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapRoadHotspots.summary = f"Statewide Integrated Traffic Records System (SWITRS) Road Hotspots Map for Orange County, California ({mdYears})"
mdoMapRoadHotspots.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on road hotspots in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapRoadHotspots.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRoadHotspots.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRoadHotspots.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapRoadHotspots.metadata = mdoMapRoadHotspots

# endregion


# region Major Road Buffers Map 14 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Buffers Map 14 Metadata")

# Create a new metadata object for the major road buffers map and assign it to the map
mdoMapRoadBuffers = md.Metadata()
mdoMapRoadBuffers.title = "OCSWITRS Major Road Buffers Map"
mdoMapRoadBuffers.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapRoadBuffers.summary = f"Statewide Integrated Traffic Records System (SWITRS) Road Buffers Map for Orange County, California ({mdYears})"
mdoMapRoadBuffers.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on road buffers in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapRoadBuffers.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRoadBuffers.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRoadBuffers.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapRoadBuffers.metadata = mdoMapRoadBuffers

# endregion


# region Major Road Buffer Segments Map 15 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Buffer Segments Map 15 Metadata")

# Create a new metadata object for the major road buffer segments map and assign it to the map
mdoMapRoadSegments = md.Metadata()
mdoMapRoadSegments.title = "OCSWITRS Major Road Segments Map"
mdoMapRoadSegments.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapRoadSegments.summary = f"Statewide Integrated Traffic Records System (SWITRS) Road Segments Map for Orange County, California ({mdYears})"
mdoMapRoadSegments.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on road segments in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoMapRoadSegments.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRoadSegments.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRoadSegments.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapRoadSegments.metadata = mdoMapRoadSegments

# endregion


# region Major Road Segments Map 16 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Major Road Segments Map 16 Metadata")

# Create a new metadata object for the roads map and assign it to the map
mdoMapRoads = md.Metadata()
mdoMapRoads.title = "OCSWITRS Roads Processing Map"
mdoMapRoads.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoMapRoads.summary = "Roads Processing Map for the OCSWITRS Project"
mdoMapRoads.description = """<div style="text-align:Left;"><div><div><p><span>The Orange County Roads Network is a comprehensive representation of all roads in the area, including primary roads and highways, secondary roads, and local roads. The data are sourced from the Orange County Department of Public Works and are updated regularly to reflect the most current road network configuration.</span></p></div></div></div>"""
mdoMapRoads.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRoads.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRoads.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Apply the metadata to the map
mapRoads.metadata = mdoMapRoads

# endregion


# region Hotspot Points Map 17 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hotspot Points Map 17 Metadata")

# Create a new metadata object for the hotspot points map and assign it to the map
mdoMapPointFhs = md.Metadata()
mdoMapPointFhs.title = "OCSWITRS Point Features Hot Spots Map"
mdoMapPointFhs.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapPointFhs.summary = f"Statewide Integrated Traffic Records System (SWITRS) Point Features Hot Spots Map for Orange County, California ({mdYears})"
mdoMapPointFhs.description = """<div style="text-align:Left;"><div><div><p><span>Hot Spot Analysis for the OCSWITRS Project Data using point features</span></p></div></div></div>"""
mdoMapPointFhs.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapPointFhs.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapPointFhs.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapPointFhs.metadata = mdoMapPointFhs

# endregion


# region Optimized Hotspot Points Map 18 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Optimized Hotspot Points Map 18 Metadata")

# Create a new metadata object for the optimized hotspot points map and assign it to the map
mdoMapPointOhs = md.Metadata()
mdoMapPointOhs.title = "OCSWITRS Point Features Optimized Hot Spots Map"
mdoMapPointOhs.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapPointOhs.summary = f"Statewide Integrated Traffic Records System (SWITRS) Point Features Optimized Hot Spots Map for Orange County, California ({mdYears})"
mdoMapPointOhs.description = """<div style="text-align:Left;"><div><div><p><span>Optimized Hot Spot Analysis for the OCSWITRS Project Data using point features</span></p></div></div></div>"""
mdoMapPointOhs.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapPointOhs.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapPointOhs.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapPointOhs.metadata = mdoMapPointOhs

# endregion


# region Population Density Map 19 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Population Density Map 19 Metadata")

# Create a new metadata object for the population density map and assign it to the map
mdoMapPopDens = md.Metadata()
mdoMapPopDens.title = "OCSWITRS Population Density Map"
mdoMapPopDens.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoMapPopDens.summary = "Population Density Map for the OCSWITRS Project"
mdoMapPopDens.description = """<div style="text-align:Left;"><div><div><p><span>The map displays the population density (per square mile) in Orange County by Census Blocks (US Census 2000). The data source is the US Centennial Census of 2000.</span></p></div></div></div>"""
mdoMapPopDens.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapPopDens.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapPopDens.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Apply the metadata to the map
mapPopDens.metadata = mdoMapPopDens

# endregion

# region Housing Density Map 20 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Housing Density Map 20 Metadata")

# Create a new metadata object for the housing density map and assign it to the map
mdoMapHouDens = md.Metadata()
mdoMapHouDens.title = "OCSWITRS Housing Density Map"
mdoMapHouDens.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoMapHouDens.summary = "Housing Density Map for the OCSWITRS Project"
mdoMapHouDens.description = """<div style="text-align:Left;"><div><div><p><span>The map displays the housing density (per square mile) in Orange County by Census Blocks (US Census 2000). The data source is the US Centennial Census of 2000.</span></p></div></div></div>"""
mdoMapHouDens.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapHouDens.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapHouDens.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Apply the metadata to the map
mapHouDens.metadata = mdoMapHouDens

# endregion


# region City Areas Victims Map 21 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- City Areas Victims Map 21 Metadata")

# Create a new metadata object for the victims by city areas map and assign it to the map
mdoMapAreaCities = md.Metadata()
mdoMapAreaCities.title = "OCSWITRS City Areas Victims Count Map"
mdoMapAreaCities.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoMapAreaCities.summary = "City Areas Victims Count Map for the OCSWITRS Project"
mdoMapAreaCities.description = """<div style="text-align:Left;"><div><div><p><span>The map displays the number of victims involved in traffic incidents in Orange County by City Areas. The data source is the SWITRS database maintained by the California Highway Patrol (CHP).</span></p></div></div></div>"""
mdoMapAreaCities.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapAreaCities.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapAreaCities.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Apply the metadata to the map
mapAreaCities.metadata = mdoMapAreaCities

# endregion


# region Census Blocks Victims Map 22 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Census Blocks Victims Map 22 Metadata")

# Create a new metadata object for the victims by census blocks map and assign it to the map
mdoMapAreaBlocks = md.Metadata()
mdoMapAreaBlocks.title = "OCSWITRS Census Blocks Victims Count Map"
mdoMapAreaBlocks.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoMapAreaBlocks.summary = "Census Blocks Victims Count Map for the OCSWITRS Project"
mdoMapAreaBlocks.description = """<div style="text-align:Left;"><div><div><p><span>The map displays the number of victims involved in traffic incidents in Orange County by Census Blocks. The data source is the SWITRS database maintained by the California Highway Patrol (CHP).</span></p></div></div></div>"""
mdoMapAreaBlocks.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapAreaBlocks.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapAreaBlocks.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Apply the metadata to the map
mapAreaBlocks.metadata = mdoMapAreaBlocks

# endregion


# region Summaries Map 23 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summaries Map 23 Metadata")

# Create a new metadata object for the summaries map and assign it to the map
mdoMapSummaries = md.Metadata()
mdoMapSummaries.title = "OCSWITRS Summaries Map"
mdoMapSummaries.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapSummaries.summary = f"Statewide Integrated Traffic Records System (SWITRS) Summaries Map for Orange County, California ({mdYears})"
mdoMapSummaries.description = """<div style="text-align:Left;"><div><div><p><span>Summarized data representation and visualization for the Orange County OCSWITRS traffic incident data.</span></p></div></div></div>"""
mdoMapSummaries.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapSummaries.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapSummaries.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapSummaries.metadata = mdoMapSummaries

# endregion


# region Analysis Map 24 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Analysis Map 24 Metadata")

# Create a new metadata object for the analysis map and assign it to the map
mdoMapAnalysis = md.Metadata()
mdoMapAnalysis.title = "OCSWITRS Analysis Map"
mdoMapAnalysis.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapAnalysis.summary = f"Statewide Integrated Traffic Records System (SWITRS) Analysis Map for Orange County, California ({mdYears})"
mdoMapAnalysis.description = """<div style="text-align:Left;"><div><div><p><span>Analysis and visualization for the OCSWITRS Project Data</span></p></div></div></div>"""
mdoMapAnalysis.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapAnalysis.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapAnalysis.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapAnalysis.metadata = mdoMapAnalysis

# endregion


# region Regression Map 25 Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Regression Map 25 Metadata")

# Create a new metadata object for the regression map and assign it to the map
mdoMapRegression = md.Metadata()
mdoMapRegression.title = "OCSWITRS Regression Analysis Map"
mdoMapRegression.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoMapRegression.summary = f"Statewide Integrated Traffic Records System (SWITRS) Regression Analysis Map for Orange County, California ({mdYears})"
mdoMapRegression.description = """<div style="text-align:Left;"><div><div><p><span>Regression Analysis for the OCSWITRS Project Data</span></p></div></div></div>"""
mdoMapRegression.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoMapRegression.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoMapRegression.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata to the map
mapRegression.metadata = mdoMapRegression

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 2.2
# endregion 2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3. Map Layers Processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nMap Layers Processing")

# In this section we will be creating map layers for the feature classes in the geodatabase. The layers will be added to the maps and layouts.



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.1 Time Settings Configuration
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.1 Time Settings Configuration")

# Define time settings configuration for the map layers

# Define the key time parameters for the layers using a dictionary
timeSettings = {
    "st": datetime(2012, 1, 1, 0, 0, 0),
    "et": datetime(2024, 9, 30, 23, 59, 59),
    "td": datetime(2024, 9, 30, 23, 59, 59) - datetime(2012, 1, 1, 0, 0, 0),
    "stf": "dateDatetime",
    "tsi": 1.0,
    "tsiu": "months",
    "tz": arcpy.mp.ListTimeZones("*Pacific*")[0],
}
# where, st: start time, et: end time, td: time extent, stf: time field,
# tsi: time interval, tsiu: time units, tz: time zone

# Define a function that enables time settings in data layers
def setLayerTime(layer):
    """Set the time properties for a layer in the map"""
    # Check if the layer is time-enabled
    if not layer.isTimeEnabled:
        # Enable time for the layer
        layer.enableTime("dateDatetime", "", "TRUE", None)
        # Set the start time for the layer
        layer.time.startTime = timeSettings["st"]
        # Set the end time for the layer
        layer.time.endTime = timeSettings["et"]
        # Set the time field for the layer
        layer.time.startTimeField = timeSettings["stf"]
        # Set the time step interval for the layer
        layer.time.timeStepInterval = timeSettings["tsi"]
        # Set the time step interval units for the layer
        layer.time.timeStepIntervalUnits = timeSettings["tsiu"]
        # Set the time zone for the layer
        layer.time.timeZone = timeSettings["tz"]

    # Re assign step interval and time units
    if layer.isTimeEnabled:
        layer.time.timeStepInterval = 1.0
        layer.time.timeStepIntervalUnits = "months"

# endregion 3.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.2 Collisions Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.2 Collisions Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the collisions map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the roads map view
mapCollisions.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map
for lyr in mapCollisions.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapCollisions.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapCollisionsLyrBoundaries = mapCollisions.addDataFromPath(boundaries)
mapCollisionsLyrCities = mapCollisions.addDataFromPath(cities)
mapCollisionsLyrBlocks = mapCollisions.addDataFromPath(blocks)
mapCollisionsLyrRoads = mapCollisions.addDataFromPath(roads)
mapCollisionsLyrCollisions = mapCollisions.addDataFromPath(collisions)

# Set layer visibility on the map
mapCollisionsLyrBoundaries.visible = False
mapCollisionsLyrCities.visible = False
mapCollisionsLyrBlocks.visible = False
mapCollisionsLyrRoads.visible = False
mapCollisionsLyrCollisions.visible = False

# endregion


# region Enable Time Settings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Enable Time Settings")

# Setup and enable time settings for the collisions map layers
setLayerTime(mapCollisionsLyrCollisions)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Collisions layer

# Apply the symbology for the Collisions data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCollisionsLyrCollisions,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Collisions.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCollisionsLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCollisionsLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCollisionsLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCollisionsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the collisions map layers
mapCollisionsCimBoundaries = mapCollisionsLyrBoundaries.getDefinition("V3")
mapCollisionsCimCities = mapCollisionsLyrCities.getDefinition("V3")
mapCollisionsCimBlocks = mapCollisionsLyrBlocks.getDefinition("V3")
mapCollisionsCimRoads = mapCollisionsLyrRoads.getDefinition("V3")
mapCollisionsCimCollisions = mapCollisionsLyrCollisions.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapCollisionsCimBoundaries.renderer.heading = "Boundaries"
mapCollisionsCimCities.renderer.heading = "City Population Density"
mapCollisionsCimBlocks.renderer.heading = "Population Density"
mapCollisionsCimRoads.renderer.heading = "Road Categories"
mapCollisionsCimCollisions.renderer.heading = "Severity Level"

# Update the map layer definitions
mapCollisionsLyrBoundaries.setDefinition(mapCollisionsCimBoundaries)
mapCollisionsLyrCities.setDefinition(mapCollisionsCimCities)
mapCollisionsLyrBlocks.setDefinition(mapCollisionsCimBlocks)
mapCollisionsLyrRoads.setDefinition(mapCollisionsCimRoads)
mapCollisionsLyrCollisions.setDefinition(mapCollisionsCimCollisions)

# Update the CIM definition for the collisions map
cimCollisions = mapCollisions.getDefinition("V3")  # Collisions map CIM

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the collisions map mapx file
exportCim("map", mapCollisions, "collisions")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.
for l in mapCollisions.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.3 Crashes Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.3 Crashes Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the crashes map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the crashes map view
mapCrashes.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map
for lyr in mapCrashes.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapCrashes.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapCrashesLyrBoundaries = mapCrashes.addDataFromPath(boundaries)
mapCrashesLyrCities = mapCrashes.addDataFromPath(cities)
mapCrashesLyrBlocks = mapCrashes.addDataFromPath(blocks)
mapCrashesLyrRoads = mapCrashes.addDataFromPath(roads)
mapCrashesLyrCrashes = mapCrashes.addDataFromPath(crashes)

# Set layer visibility on the map
mapCrashesLyrBoundaries.visible = False
mapCrashesLyrCities.visible = False
mapCrashesLyrBlocks.visible = False
mapCrashesLyrRoads.visible = False
mapCrashesLyrCrashes.visible = False

# endregion


# region Enable Time Settings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Enable Time Settings")

# Setup and enable time settings for the crashes map layers
setLayerTime(mapCrashesLyrCrashes)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Crashes layer

# Apply the symbology for the Collisions data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCrashesLyrCrashes,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Crashes.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCrashesLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCrashesLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCrashesLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapCrashesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the crashes map layers
mapCrashesCimBoundaries = mapCrashesLyrBoundaries.getDefinition("V3")
mapCrashesCimCities = mapCrashesLyrCities.getDefinition("V3")
mapCrashesCimBlocks = mapCrashesLyrBlocks.getDefinition("V3")
mapCrashesCimRoads = mapCrashesLyrRoads.getDefinition("V3")
mapCrashesCimCrashes = mapCrashesLyrCrashes.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapCrashesCimBoundaries.renderer.heading = "Boundaries"
mapCrashesCimCities.renderer.heading = "City Population Density"
mapCrashesCimBlocks.renderer.heading = "Population Density"
mapCrashesCimRoads.renderer.heading = "Road Categories"
mapCrashesCimCrashes.renderer.heading = "Severity Level"

# Update the map layer definitions
mapCrashesLyrBoundaries.setDefinition(mapCrashesCimBoundaries)
mapCrashesLyrCities.setDefinition(mapCrashesCimCities)
mapCrashesLyrBlocks.setDefinition(mapCrashesCimBlocks)
mapCrashesLyrRoads.setDefinition(mapCrashesCimRoads)
mapCrashesLyrCrashes.setDefinition(mapCrashesCimCrashes)

# Update the CIM definition for the crashes map
cimCrashes = mapCrashes.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the crashes map mapx file
exportCim("map", mapCrashes, "crashes")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapCrashes.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.4 Parties Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.4 Parties Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the parties map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the parties map view
mapParties.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map
for lyr in mapParties.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapParties.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapPartiesLyrBoundaries = mapParties.addDataFromPath(boundaries)
mapPartiesLyrCities = mapParties.addDataFromPath(cities)
mapPartiesLyrBlocks = mapParties.addDataFromPath(blocks)
mapPartiesLyrRoads = mapParties.addDataFromPath(roads)
mapPartiesLyrParties = mapParties.addDataFromPath(parties)

# Set layer visibility on the map
mapPartiesLyrBoundaries.visible = False
mapPartiesLyrCities.visible = False
mapPartiesLyrBlocks.visible = False
mapPartiesLyrRoads.visible = False
mapPartiesLyrParties.visible = False

# endregion


# region Enable Time Settings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Enable Time Settings")

# Setup and enable time settings for the parties map layers

setLayerTime(mapPartiesLyrParties)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Parties layer

# Apply the symbology for the Parties data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPartiesLyrParties,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Parties.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPartiesLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPartiesLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPartiesLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPartiesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the parties map layers
mapPartiesCimBoundaries = mapPartiesLyrBoundaries.getDefinition("V3")
mapPartiesCimCities = mapPartiesLyrCities.getDefinition("V3")
mapPartiesCimBlocks = mapPartiesLyrBlocks.getDefinition("V3")
mapPartiesCimRoads = mapPartiesLyrRoads.getDefinition("V3")
mapPartiesCimParties = mapPartiesLyrParties.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapPartiesCimBoundaries.renderer.heading = "Boundaries"
mapPartiesCimCities.renderer.heading = "City Population Density"
mapPartiesCimBlocks.renderer.heading = "Population Density"
mapPartiesCimRoads.renderer.heading = "Road Categories"
mapPartiesCimParties.renderer.heading = "Severity Level"

# Update the map layer definitions
mapPartiesLyrBoundaries.setDefinition(mapPartiesCimBoundaries)
mapPartiesLyrCities.setDefinition(mapPartiesCimCities)
mapPartiesLyrBlocks.setDefinition(mapPartiesCimBlocks)
mapPartiesLyrRoads.setDefinition(mapPartiesCimRoads)
mapPartiesLyrParties.setDefinition(mapPartiesCimParties)

# Update the CIM defintion for the parties map
partiesCim = mapParties.getDefinition("V3")

# endregion

# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the parties map mapx file
exportCim("map", mapParties, "parties")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapParties.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.5 Victims Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.5 Victims Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the victims map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the victims map view
mapVictims.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapVictims.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapVictims.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapVictimsLyrBoundaries = mapVictims.addDataFromPath(boundaries)
mapVictimsLyrCities = mapVictims.addDataFromPath(cities)
mapVictimsLyrBlocks = mapVictims.addDataFromPath(blocks)
mapVictimsLyrRoads = mapVictims.addDataFromPath(roads)
mapVictimsLyrVictims = mapVictims.addDataFromPath(victims)

# Set layer visibility on the map
mapVictimsLyrBoundaries.visible = False
mapVictimsLyrCities.visible = False
mapVictimsLyrBlocks.visible = False
mapVictimsLyrRoads.visible = False
mapVictimsLyrVictims.visible = False

# endregion


# region Enable Time Settings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Enable Time Settings")

# Setup and enable time settings for the victims map layers
setLayerTime(mapVictimsLyrVictims)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Victims layer

# Apply the symbology for the Victims data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapVictimsLyrVictims,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Victims.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapVictimsLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapVictimsLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapVictimsLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapVictimsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the victims map layers
mapVictimsCimBoundaries = mapVictimsLyrBoundaries.getDefinition("V3")
mapVictimsCimCities = mapVictimsLyrCities.getDefinition("V3")
mapVictimsCimBlocks = mapVictimsLyrBlocks.getDefinition("V3")
mapVictimsCimRoads = mapVictimsLyrRoads.getDefinition("V3")
mapVictimsCimVictims = mapVictimsLyrVictims.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapVictimsCimBoundaries.renderer.heading = "Boundaries"
mapVictimsCimCities.renderer.heading = "City Population Density"
mapVictimsCimBlocks.renderer.heading = "Population Density"
mapVictimsCimRoads.renderer.heading = "Road Categories"
mapVictimsCimVictims.renderer.heading = "Severity Level"

# Update the map layer definitions
mapVictimsLyrBoundaries.setDefinition(mapVictimsCimBoundaries)
mapVictimsLyrCities.setDefinition(mapVictimsCimCities)
mapVictimsLyrBlocks.setDefinition(mapVictimsCimBlocks)
mapVictimsLyrRoads.setDefinition(mapVictimsCimRoads)
mapVictimsLyrVictims.setDefinition(mapVictimsCimVictims)

# Update the CIM definition for the victims map
cimVictims = mapVictims.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapVictims, "victims")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapVictims.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.5


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.6 Injuries Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.6 Injuries Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the injuries map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the injuries map view
mapInjuries.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all layers from the map
for lyr in mapInjuries.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapInjuries.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapInjuriesLyrBoundaries = mapInjuries.addDataFromPath(boundaries)
mapInjuriesLyrCities = mapInjuries.addDataFromPath(cities)
mapInjuriesLyrBlocks = mapInjuries.addDataFromPath(blocks)
mapInjuriesLyrVictims = mapInjuries.addDataFromPath(victims)

# Set layer visibility on the map
mapInjuriesLyrBoundaries.visible = False
mapInjuriesLyrCities.visible = False
mapInjuriesLyrBlocks.visible = False
mapInjuriesLyrVictims.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Victims layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapInjuriesLyrVictims,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Victims.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapInjuriesLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapInjuriesLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapInjuriesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapInjuriesCimBoundaries = mapInjuriesLyrBoundaries.getDefinition("V3")
mapInjuriesCimCities = mapInjuriesLyrCities.getDefinition("V3")
mapInjuriesCimBlocks = mapInjuriesLyrBlocks.getDefinition("V3")
mapInjuriesCimVictims = mapInjuriesLyrVictims.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapInjuriesCimBoundaries.renderer.heading = "Boundaries"
mapInjuriesCimCities.renderer.heading = "City Population Density"
mapInjuriesCimBlocks.renderer.heading = "Population Density"
mapInjuriesCimVictims.renderer.heading = "Severity Level"

# Update the map layer definitions
mapInjuriesLyrBoundaries.setDefinition(mapInjuriesCimBoundaries)
mapInjuriesLyrCities.setDefinition(mapInjuriesCimCities)
mapInjuriesLyrBlocks.setDefinition(mapInjuriesCimBlocks)
mapInjuriesLyrVictims.setDefinition(mapInjuriesCimVictims)

# Update the CIM definition for the regression map
cimInjuries = mapInjuries.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapInjuries, "injuries")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapInjuries.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.6


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.7 Fatalities Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.7 Fatalities Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the fatalities map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the fatalities map view
mapFatalities.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapFatalities.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapFatalities.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapFatalitiesLyrBoundaries = mapFatalities.addDataFromPath(boundaries)
mapFatalitiesLyrRoads = mapFatalities.addDataFromPath(roads)
mapFatalitiesLyrRoadsMajorBuffers = mapFatalities.addDataFromPath(roadsMajorBuffers)
mapFatalitiesLyrFatalities = mapFatalities.addDataFromPath(crashes)

# Set layer visibility on the map
mapFatalitiesLyrBoundaries.visible = False
mapFatalitiesLyrRoads.visible = False
mapFatalitiesLyrRoadsMajorBuffers.visible = False
mapFatalitiesLyrFatalities.visible = False

# Move layers
mapFatalities.moveLayer(
    reference_layer=mapFatalitiesLyrRoads,
    move_layer=mapFatalitiesLyrRoadsMajorBuffers,
    insert_position="BEFORE",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Fatalities layer

# Apply the symbology for the Fatalities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFatalitiesLyrFatalities,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Crashes Killed Victims.lyrx"
    ),
    symbology_fields=[["VALUE_FIELD", "numberKilled", "numberKilled"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Major Road Buffers Layer

# Apply the symbology for the Major Road Buffers data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFatalitiesLyrRoadsMajorBuffers,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Major Roads Buffers.lyrx"
    ),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFatalitiesLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFatalitiesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the fatalities map layers
mapFatalitiesCimBoundaries = mapFatalitiesLyrBoundaries.getDefinition("V3")
mapFatalitiesCimRoads = mapFatalitiesLyrRoads.getDefinition("V3")
mapFatalitiesCimRoadsMajorBuffers = mapFatalitiesLyrRoadsMajorBuffers.getDefinition(
    "V3"
)
mapFatalitiesCimFatalities = mapFatalitiesLyrFatalities.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapFatalitiesCimBoundaries.renderer.heading = "Boundaries"
mapFatalitiesCimRoads.renderer.heading = "Road Categories"
mapFatalitiesCimRoadsMajorBuffers.renderer.heading = "Major Road Buffers"
mapFatalitiesCimFatalities.renderer.heading = "Victims Killed"

# Update the map layer definitions
mapFatalitiesLyrBoundaries.setDefinition(mapFatalitiesCimBoundaries)
mapFatalitiesLyrRoads.setDefinition(mapFatalitiesCimRoads)
mapFatalitiesLyrRoadsMajorBuffers.setDefinition(mapFatalitiesCimRoadsMajorBuffers)
mapFatalitiesLyrFatalities.setDefinition(mapFatalitiesCimFatalities)

# Update the CIM definition for the fatalities map
cimFatalities = mapFatalities.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the fatalities map mapx file
exportCim("map", mapFatalities, "fatalities")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapFatalities.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.7


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.8 Hotspots (100m, 1km) Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.8 Hotspots (100m, 1km) Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the hotspots (100m, 1km) map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the hotspots100m1km map view
mapFhs100m1km.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapFhs100m1km.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapFhs100m1km.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapFhs100m1kmLyrBoundaries = mapFhs100m1km.addDataFromPath(boundaries)
mapFhs100m1kmLyrCities = mapFhs100m1km.addDataFromPath(cities)
mapFhs100m1kmLyrBlocks = mapFhs100m1km.addDataFromPath(blocks)
mapFhs100m1kmLyrRoads = mapFhs100m1km.addDataFromPath(roads)
mapFhs100m1kmLyrFhs100m1km = mapFhs100m1km.addDataFromPath(crashesFindHotspots100m1km)

# Set layer visibility on the map
mapFhs100m1kmLyrBoundaries.visible = False
mapFhs100m1kmLyrCities.visible = False
mapFhs100m1kmLyrBlocks.visible = False
mapFhs100m1kmLyrRoads.visible = False
mapFhs100m1kmLyrFhs100m1km.visible = False

# Move layers
mapFhs100m1km.moveLayer(
    reference_layer=mapFhs100m1kmLyrBoundaries,
    move_layer=mapFhs100m1kmLyrRoads,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m1kmLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m1kmLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m1kmLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m1kmLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the hotspots100m1km map layers
mapFhs100m1kmCimBoundaries = mapFhs100m1kmLyrBoundaries.getDefinition("V3")
mapFhs100m1kmCimCities = mapFhs100m1kmLyrCities.getDefinition("V3")
mapFhs100m1kmCimBlocks = mapFhs100m1kmLyrBlocks.getDefinition("V3")
mapFhs100m1kmCimRoads = mapFhs100m1kmLyrRoads.getDefinition("V3")
mapFhs100m1kmCimFhs100m1km = mapFhs100m1kmLyrFhs100m1km.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapFhs100m1kmCimBoundaries.renderer.heading = "Boundaries"
mapFhs100m1kmCimCities.renderer.heading = "City Population Density"
mapFhs100m1kmCimBlocks.renderer.heading = "Population Density"
mapFhs100m1kmCimRoads.renderer.heading = "Road Categories"
mapFhs100m1kmCimFhs100m1km.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapFhs100m1kmLyrBoundaries.setDefinition(mapFhs100m1kmCimBoundaries)
mapFhs100m1kmLyrCities.setDefinition(mapFhs100m1kmCimCities)
mapFhs100m1kmLyrBlocks.setDefinition(mapFhs100m1kmCimBlocks)
mapFhs100m1kmLyrRoads.setDefinition(mapFhs100m1kmCimRoads)
mapFhs100m1kmLyrFhs100m1km.setDefinition(mapFhs100m1kmCimFhs100m1km)

# Update the CIM definition for the hotspots (100m, 1km) map
cimFhs100m1km = mapFhs100m1km.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapFhs100m1km, "hotspots100m1km")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapFhs100m1km.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.8


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.9 Hotspots (150m, 2km) Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.9 Hotspots (150m, 2km) Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the hotspots (150m, 2km) map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the hotspots150m2km map view
mapFhs150m2km.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapFhs150m2km.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapFhs150m2km.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapFhs150m2kmLyrBoundaries = mapFhs150m2km.addDataFromPath(boundaries)
mapFhs150m2kmLyrCities = mapFhs150m2km.addDataFromPath(cities)
mapFhs150m2kmLyrBlocks = mapFhs150m2km.addDataFromPath(blocks)
mapFhs150m2kmLyrRoads = mapFhs150m2km.addDataFromPath(roads)
mapFhs150m2kmLyrFhs150m2km = mapFhs150m2km.addDataFromPath(crashesFindHotspots150m2km)

# Set layer visibility on the map
mapFhs150m2kmLyrBoundaries.visible = False
mapFhs150m2kmLyrCities.visible = False
mapFhs150m2kmLyrBlocks.visible = False
mapFhs150m2kmLyrRoads.visible = False
mapFhs150m2kmLyrFhs150m2km.visible = False

# Move layers
mapFhs150m2km.moveLayer(
    reference_layer=mapFhs150m2kmLyrBoundaries,
    move_layer=mapFhs150m2kmLyrRoads,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs150m2kmLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs150m2kmLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs150m2kmLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs150m2kmLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the hotspots150m2km map layers
mapFhs150m2kmCimBoundaries = mapFhs150m2kmLyrBoundaries.getDefinition("V3")
mapFhs150m2kmCimCities = mapFhs150m2kmLyrCities.getDefinition("V3")
mapFhs150m2kmCimBlocks = mapFhs150m2kmLyrBlocks.getDefinition("V3")
mapFhs150m2kmCimRoads = mapFhs150m2kmLyrRoads.getDefinition("V3")
mapFhs150m2kmCimFhs150m2km = mapFhs150m2kmLyrFhs150m2km.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapFhs150m2kmCimBoundaries.renderer.heading = "Boundaries"
mapFhs150m2kmCimCities.renderer.heading = "City Population Density"
mapFhs150m2kmCimBlocks.renderer.heading = "Population Density"
mapFhs150m2kmCimRoads.renderer.heading = "Road Categories"
mapFhs150m2kmCimFhs150m2km.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapFhs150m2kmLyrBoundaries.setDefinition(mapFhs150m2kmCimBoundaries)
mapFhs150m2kmLyrCities.setDefinition(mapFhs150m2kmCimCities)
mapFhs150m2kmLyrBlocks.setDefinition(mapFhs150m2kmCimBlocks)
mapFhs150m2kmLyrRoads.setDefinition(mapFhs150m2kmCimRoads)
mapFhs150m2kmLyrFhs150m2km.setDefinition(mapFhs150m2kmCimFhs150m2km)

# Update the CIM definition for the hotspots (150m, 2km) map
cimFhs150m2km = mapFhs150m2km.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapFhs150m2km, "hotspots150m2km")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapFhs150m2km.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.9


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.10 Hotspots (100m, 5km) Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.10 Hotspots (100m, 5km) Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the hotspots (100m, 5km) map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the hotspots100m5km map view
mapFhs100m5km.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapFhs100m5km.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapFhs100m5km.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapFhs100m5kmLyrBoundaries = mapFhs100m5km.addDataFromPath(boundaries)
mapFhs100m5kmLyrCities = mapFhs100m5km.addDataFromPath(cities)
mapFhs100m5kmLyrBlocks = mapFhs100m5km.addDataFromPath(blocks)
mapFhs100m5kmLyrRoads = mapFhs100m5km.addDataFromPath(roads)
mapFhs100m5kmLyrFhs100m5km = mapFhs100m5km.addDataFromPath(crashesFindHotspots100m5km)

# Set layer visibility on the map
mapFhs100m5kmLyrBoundaries.visible = False
mapFhs100m5kmLyrCities.visible = False
mapFhs100m5kmLyrBlocks.visible = False
mapFhs100m5kmLyrRoads.visible = False
mapFhs100m5kmLyrFhs100m5km.visible = False

# Move layers
mapFhs100m5km.moveLayer(
    reference_layer=mapFhs100m5kmLyrBoundaries,
    move_layer=mapFhs100m5kmLyrRoads,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m5kmLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m5kmLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m5kmLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhs100m5kmLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the hotspots100m5km map layers
mapFhs100m5kmCimBoundaries = mapFhs100m5kmLyrBoundaries.getDefinition("V3")
mapFhs100m5kmCimCities = mapFhs100m5kmLyrCities.getDefinition("V3")
mapFhs100m5kmCimBlocks = mapFhs100m5kmLyrBlocks.getDefinition("V3")
mapFhs100m5kmCimRoads = mapFhs100m5kmLyrRoads.getDefinition("V3")
mapFhs100m5kmCimFhs100m5km = mapFhs100m5kmLyrFhs100m5km.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapFhs100m5kmCimBoundaries.renderer.heading = "Boundaries"
mapFhs100m5kmCimCities.renderer.heading = "City Population Density"
mapFhs100m5kmCimBlocks.renderer.heading = "Population Density"
mapFhs100m5kmCimRoads.renderer.heading = "Road Categories"
mapFhs100m5kmCimFhs100m5km.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapFhs100m5kmLyrBoundaries.setDefinition(mapFhs100m5kmCimBoundaries)
mapFhs100m5kmLyrCities.setDefinition(mapFhs100m5kmCimCities)
mapFhs100m5kmLyrBlocks.setDefinition(mapFhs100m5kmCimBlocks)
mapFhs100m5kmLyrRoads.setDefinition(mapFhs100m5kmCimRoads)
mapFhs100m5kmLyrFhs100m5km.setDefinition(mapFhs100m5kmCimFhs100m5km)

# Update the CIM definition for the hotspots (100m, 5km) map
cimFhs100m5kmLyr = mapFhs100m5km.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapFhs100m5km, "hotspots100m5km")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapFhs100m5km.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.10


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.11 Hotspots 500ft from Major Roads Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.11 Hotspots 500ft from Major Roads Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the hotspots 500ft from major roads map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the hotspotsroads500ft map view
mapFhsRoads500ft.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapFhsRoads500ft.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapFhsRoads500ft.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapFhsRoads500ftLyrBoundaries = mapFhsRoads500ft.addDataFromPath(boundaries)
mapFhsRoads500ftLyrCities = mapFhsRoads500ft.addDataFromPath(cities)
mapFhsRoads500ftLyrBlocks = mapFhsRoads500ft.addDataFromPath(blocks)
mapFhsRoads500ftLyrRoads = mapFhsRoads500ft.addDataFromPath(roads)
mapFhsRoads500ftLyrFhsRoads500ft = mapFhsRoads500ft.addDataFromPath(
    crashesFindHotspots500ftMajorRoads500ft1mi
)

# Set layer visibility on the map
mapFhsRoads500ftLyrBoundaries.visible = False
mapFhsRoads500ftLyrCities.visible = False
mapFhsRoads500ftLyrBlocks.visible = False
mapFhsRoads500ftLyrRoads.visible = False
mapFhsRoads500ftLyrFhsRoads500ft.visible = False

# Move layers
mapFhsRoads500ft.moveLayer(
    reference_layer=mapFhsRoads500ftLyrBoundaries,
    move_layer=mapFhsRoads500ftLyrRoads,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhsRoads500ftLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhsRoads500ftLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhsRoads500ftLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapFhsRoads500ftLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the hotspotsroads500ft map layers
mapFhsRoads500ftCimBoundaries = mapFhsRoads500ftLyrBoundaries.getDefinition("V3")
mapFhsRoads500ftCimCities = mapFhsRoads500ftLyrCities.getDefinition("V3")
mapFhsRoads500ftCimBlocks = mapFhsRoads500ftLyrBlocks.getDefinition("V3")
mapFhsRoads500ftCimRoads = mapFhsRoads500ftLyrRoads.getDefinition("V3")
mapFhsRoads500ftCimFhsRoads500ft = mapFhsRoads500ftLyrFhsRoads500ft.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapFhsRoads500ftCimBoundaries.renderer.heading = "Boundaries"
mapFhsRoads500ftCimCities.renderer.heading = "City Population Density"
mapFhsRoads500ftCimBlocks.renderer.heading = "Population Density"
mapFhsRoads500ftCimRoads.renderer.heading = "Road Categories"
mapFhsRoads500ftCimFhsRoads500ft.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapFhsRoads500ftLyrBoundaries.setDefinition(mapFhsRoads500ftCimBoundaries)
mapFhsRoads500ftLyrCities.setDefinition(mapFhsRoads500ftCimCities)
mapFhsRoads500ftLyrBlocks.setDefinition(mapFhsRoads500ftCimBlocks)
mapFhsRoads500ftLyrRoads.setDefinition(mapFhsRoads500ftCimRoads)
mapFhsRoads500ftLyrFhsRoads500ft.setDefinition(mapFhsRoads500ftCimFhsRoads500ft)

# Update the CIM defintion for the hotspots 500ft from major roads map
cimFhsRoads500ft = mapFhsRoads500ft.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapFhsRoads500ft, "hotspotsroads500ft")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapFhsRoads500ft.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.11


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.12 Optimized Hotspots 500ft from Major Roads Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.12 Optimized Hotspots 500ft from Major Roads Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Open the optimized hotspots 500ft from major roads map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the optimized hot spots map view
mapOhsRoads500ft.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapOhsRoads500ft.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapOhsRoads500ft.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapOhsRoads500ftLyrBoundaries = mapOhsRoads500ft.addDataFromPath(boundaries)
mapOhsRoads500ftLyrCities = mapOhsRoads500ft.addDataFromPath(cities)
mapOhsRoads500ftLyrBlocks = mapOhsRoads500ft.addDataFromPath(blocks)
mapOhsRoads500ftLyrRoads = mapOhsRoads500ft.addDataFromPath(roads)
mapOhsRoads500ftLyrOhsRoads500ft = mapOhsRoads500ft.addDataFromPath(
    crashesFindHotspots500ftMajorRoads500ft1mi
)

# Set layer visibility on the map
mapOhsRoads500ftLyrBoundaries.visible = False
mapOhsRoads500ftLyrCities.visible = False
mapOhsRoads500ftLyrBlocks.visible = False
mapOhsRoads500ftLyrRoads.visible = False
mapOhsRoads500ftLyrOhsRoads500ft.visible = False

# Move layers
mapOhsRoads500ft.moveLayer(
    reference_layer=mapOhsRoads500ftLyrBoundaries,
    move_layer=mapOhsRoads500ftLyrRoads,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapOhsRoads500ftLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# - Cities layer

# Apply the symbology for the cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapOhsRoads500ftLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapOhsRoads500ftLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)

# - Roads layer

# Apply the symbology for the roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapOhsRoads500ftLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the optimized hot spots map layers
mapOhsRoads500ftCimBoundaries = mapOhsRoads500ftLyrBoundaries.getDefinition("V3")
mapOhsRoads500ftCimCities = mapOhsRoads500ftLyrCities.getDefinition("V3")
mapOhsRoads500ftCimBlocks = mapOhsRoads500ftLyrBlocks.getDefinition("V3")
mapOhsRoads500ftCimRoads = mapOhsRoads500ftLyrRoads.getDefinition("V3")
mapOhsRoads500ftCimOhsRoads500ft = mapOhsRoads500ftLyrOhsRoads500ft.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapOhsRoads500ftCimBoundaries.renderer.heading = "Boundaries"
mapOhsRoads500ftCimCities.renderer.heading = "City Population Density"
mapOhsRoads500ftCimBlocks.renderer.heading = "Population Density"
mapOhsRoads500ftCimRoads.renderer.heading = "Road Categories"
mapOhsRoads500ftCimOhsRoads500ft.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapOhsRoads500ftLyrBoundaries.setDefinition(mapOhsRoads500ftCimBoundaries)
mapOhsRoads500ftLyrCities.setDefinition(mapOhsRoads500ftCimCities)
mapOhsRoads500ftLyrBlocks.setDefinition(mapOhsRoads500ftCimBlocks)
mapOhsRoads500ftLyrRoads.setDefinition(mapOhsRoads500ftCimRoads)
mapOhsRoads500ftLyrOhsRoads500ft.setDefinition(mapOhsRoads500ftCimOhsRoads500ft)

# Update the CIM definition for the major roads map
cimOhsRoads500ft = mapOhsRoads500ft.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the optimized hot spots map mapx file
exportCim("map", mapOhsRoads500ft, "optimizedHotspotsRoads500ft")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapOhsRoads500ft.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.12


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.13 Major Road Crashes Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.13 Major Road Crashes Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the regression map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the road crashes map view
mapRoadCrashes.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRoadCrashes.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapRoadCrashes.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRoadCrashesLyrBoundaries = mapRoadCrashes.addDataFromPath(boundaries)
mapRoadCrashesLyrBlocks = mapRoadCrashes.addDataFromPath(blocks)
mapRoadCrashesLyrRoadsMajor = mapRoadCrashes.addDataFromPath(roadsMajor)
mapRoadCrashesLyrCrashes500ftRoads = mapRoadCrashes.addDataFromPath(
    crashes500ftFromMajorRoads
)

# Set layer visibility on the map
mapRoadCrashesLyrBoundaries.visible = False
mapRoadCrashesLyrBlocks.visible = False
mapRoadCrashesLyrRoadsMajor.visible = False
mapRoadCrashesLyrCrashes500ftRoads.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Crashes (500ft from Major Roads) layer

# Apply the symbology for the Crashes 500ft from Major Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadCrashesLyrCrashes500ftRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Crashes.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadCrashesLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the census blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadCrashesLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadCrashesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapRoadCrashesCimBoundaries = mapRoadCrashesLyrBoundaries.getDefinition("V3")
mapRoadCrashesCimBlocks = mapRoadCrashesLyrBlocks.getDefinition("V3")
mapRoadCrashesCimRoadsMajor = mapRoadCrashesLyrRoadsMajor.getDefinition("V3")
mapRoadCrashesCimCrashes500ftRoads = mapRoadCrashesLyrCrashes500ftRoads.getDefinition(
    "V3"
)

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRoadCrashesCimBoundaries.renderer.heading = "Boundaries"
mapRoadCrashesCimBlocks.renderer.heading = "Population Density"
mapRoadCrashesCimRoadsMajor.renderer.heading = "Major Roads"
mapRoadCrashesCimRoadsMajor.renderer.heading = "Severity Level"

# Update the map layer definitions
mapRoadCrashesLyrBoundaries.setDefinition(mapRoadCrashesCimBoundaries)
mapRoadCrashesLyrBlocks.setDefinition(mapRoadCrashesCimBlocks)
mapRoadCrashesLyrRoadsMajor.setDefinition(mapRoadCrashesCimRoadsMajor)
mapRoadCrashesLyrCrashes500ftRoads.setDefinition(mapRoadCrashesCimCrashes500ftRoads)

# Update the CIM definition for the regression map
cimRoadCrashes = mapRoadCrashes.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRoadCrashes, "roadCrashes")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRoadCrashes.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.13


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.14 Major Road Hotspots Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.14 Major Road Hotspots Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the road hotspots map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the road hotspots map view
mapRoadHotspots.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRoadHotspots.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapRoadHotspots.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRoadHotspotsLyrBoundaries = mapRoadHotspots.addDataFromPath(boundaries)
mapRoadHotspotsLyrBlocks = mapRoadHotspots.addDataFromPath(blocks)
mapRoadHotspotsLyrRoadsMajor = mapRoadHotspots.addDataFromPath(roadsMajor)
mapRoadHotspotsLyrCrashesHotspots = mapRoadHotspots.addDataFromPath(
    crashesHotspots500ftFromMajorRoads
)

# Set layer visibility on the map
mapRoadHotspotsLyrBoundaries.visible = False
mapRoadHotspotsLyrBlocks.visible = False
mapRoadHotspotsLyrRoadsMajor.visible = False
mapRoadHotspotsLyrCrashesHotspots.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadHotspotsLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the census blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadHotspotsLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadHotspotsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapRoadHotspotsCimBoundaries = mapRoadHotspotsLyrBoundaries.getDefinition("V3")
mapRoadHotspotsCimBlocks = mapRoadHotspotsLyrBlocks.getDefinition("V3")
mapRoadHotspotsCimRoadsMajor = mapRoadHotspotsLyrRoadsMajor.getDefinition("V3")
mapRoadHotspotsCimCrashesHotspots = mapRoadHotspotsLyrCrashesHotspots.getDefinition(
    "V3"
)

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRoadHotspotsCimBoundaries.renderer.heading = "Boundaries"
mapRoadHotspotsCimBlocks.renderer.heading = "Population Density"
mapRoadHotspotsCimRoadsMajor.renderer.heading = "Major Roads"
mapRoadHotspotsCimCrashesHotspots.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapRoadHotspotsLyrBoundaries.setDefinition(mapRoadHotspotsCimBoundaries)
mapRoadHotspotsLyrBlocks.setDefinition(mapRoadHotspotsCimBlocks)
mapRoadHotspotsLyrRoadsMajor.setDefinition(mapRoadHotspotsCimRoadsMajor)
mapRoadHotspotsLyrCrashesHotspots.setDefinition(mapRoadHotspotsCimCrashesHotspots)

# Update the CIM definition for the regression map
cimRoadHotspots = mapRoadHotspots.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRoadHotspots, "regression")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRoadHotspots.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.14


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.15 Major Road Buffers Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.15 Major Road Buffers Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the regression map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the regression map view
mapRoadBuffers.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRoadBuffers.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapRoadBuffers.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRoadBuffersLyrBoundaries = mapRoadBuffers.addDataFromPath(boundaries)
mapRoadBuffersLyrBlocks = mapRoadBuffers.addDataFromPath(blocks)
mapRoadBuffersLyrRoadsMajor = mapRoadBuffers.addDataFromPath(roadsMajor)
mapRoadBuffersLyrRoadBuffers = mapRoadBuffers.addDataFromPath(roadsMajorBuffersSum)

# Set layer visibility on the map
mapRoadBuffersLyrBoundaries.visible = False
mapRoadBuffersLyrBlocks.visible = False
mapRoadBuffersLyrRoadsMajor.visible = False
mapRoadBuffersLyrRoadBuffers.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Road Buffer Fatalities layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadBuffersLyrRoadBuffers,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Major Roads Buffers Summary.lyrx"
    ),
    symbology_fields=[["VALUE_FIELD", "sum_numberKilled", "sum_numberKilled"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# * Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadBuffersLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadBuffersLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadBuffersLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapRoadBuffersCimBoundaries = mapRoadBuffersLyrBoundaries.getDefinition("V3")
mapRoadBuffersCimBlocks = mapRoadBuffersLyrBlocks.getDefinition("V3")
mapRoadBuffersCimRoadsMajor = mapRoadBuffersLyrRoadsMajor.getDefinition("V3")
mapRoadBuffersCimRoadBuffers = mapRoadBuffersLyrRoadBuffers.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRoadBuffersCimBoundaries.renderer.heading = "Boundaries"
mapRoadBuffersCimBlocks.renderer.heading = "Population Density"
mapRoadBuffersCimRoadsMajor.renderer.heading = "Major Roads"
mapRoadBuffersCimRoadBuffers.renderer.heading = "Fatalities (entire segment)"

# Update the map layer definitions
mapRoadBuffersLyrBoundaries.setDefinition(mapRoadBuffersCimBoundaries)
mapRoadBuffersLyrBlocks.setDefinition(mapRoadBuffersCimBlocks)
mapRoadBuffersLyrRoadsMajor.setDefinition(mapRoadBuffersCimRoadsMajor)
mapRoadBuffersLyrRoadBuffers.setDefinition(mapRoadBuffersCimRoadBuffers)

# Update the CIM definition for the regression map
cimRoadBuffers = mapRoadBuffers.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRoadBuffers, "roadBuffers")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRoadBuffers.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.15


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.16 Major Road Segments Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.16 Major Road Segments Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the major road segments map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the major road segments map view
mapRoadSegments.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRoadSegments.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
mapRoadSegments.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRoadSegmentsLyrBoundaries = mapRoadSegments.addDataFromPath(boundaries)
mapRoadSegmentsLyrBlocks = mapRoadSegments.addDataFromPath(blocks)
mapRoadSegmentsLyrRoadsMajor = mapRoadSegments.addDataFromPath(roadsMajor)
mapRoadSegmentsLyrRoadsMajorSplit = mapRoadSegments.addDataFromPath(
    roadsMajorSplitBufferSum
)

# Set layer visibility on the map
mapRoadSegmentsLyrBoundaries.visible = False
mapRoadSegmentsLyrBlocks.visible = False
mapRoadSegmentsLyrRoadsMajor.visible = False
mapRoadSegmentsLyrRoadsMajorSplit.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Major Roads Split Buffer Summary layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadSegmentsLyrRoadsMajorSplit,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Major Roads Split Buffer Summary.lyrx"
    ),
    symbology_fields=[["VALUE_FIELD", "sum_victimCount", "sum_victimCount"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadSegmentsLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadSegmentsLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadSegmentsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapRoadSegmentsCimBoundaries = mapRoadSegmentsLyrBoundaries.getDefinition("V3")
mapRoadSegmentsCimBlocks = mapRoadSegmentsLyrBlocks.getDefinition("V3")
mapRoadSegmentsCimRoadsMajor = mapRoadSegmentsLyrRoadsMajor.getDefinition("V3")
mapRoadSegmentsCimRoadsMajorSplit = mapRoadSegmentsLyrRoadsMajorSplit.getDefinition(
    "V3"
)

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRoadSegmentsCimBoundaries.renderer.heading = "Boundaries"
mapRoadSegmentsCimBlocks.renderer.heading = "Population Density"
mapRoadSegmentsCimRoadsMajor.renderer.heading = "Major Roads"
mapRoadSegmentsCimRoadsMajorSplit.renderer.heading = "Victim Count per 1,000ft segment"

# Update the map layer definitions
mapRoadSegmentsLyrBoundaries.setDefinition(mapRoadSegmentsCimBoundaries)
mapRoadSegmentsLyrBlocks.setDefinition(mapRoadSegmentsCimBlocks)
mapRoadSegmentsLyrRoadsMajor.setDefinition(mapRoadSegmentsCimRoadsMajor)
mapRoadSegmentsLyrRoadsMajorSplit.setDefinition(mapRoadSegmentsCimRoadsMajorSplit)

# Update the CIM definition for the regression map
cimRoadSegments = mapRoadSegments.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRoadSegments, "roadSegments")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRoadSegments.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.16


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.17 Roads Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.17 Roads Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the roads map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the roads map view
mapRoads.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRoads.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapRoads.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRoadsLyrRoadsMajor = mapRoads.addDataFromPath(roadsMajor)
mapRoadsLyrRoadsMajorBuffers = mapRoads.addDataFromPath(roadsMajorBuffers)
mapRoadsLyrRoadsMajorBuffersSum = mapRoads.addDataFromPath(roadsMajorBuffersSum)
mapRoadsLyrRoadsMajorPointsAlongLines = mapRoads.addDataFromPath(
    roadsMajorPointsAlongLines
)
mapRoadsLyrRoadsMajorSplit = mapRoads.addDataFromPath(roadsMajorSplit)
mapRoadsLyrRoadsMajorSplitBuffer = mapRoads.addDataFromPath(roadsMajorSplitBuffer)
mapRoadsLyrRoadsMajorSplitBufferSum = mapRoads.addDataFromPath(roadsMajorSplitBufferSum)

# Set layer visibility on the map
mapRoadsLyrRoadsMajor.visible = False
mapRoadsLyrRoadsMajorBuffers.visible = False
mapRoadsLyrRoadsMajorBuffersSum.visible = False
mapRoadsLyrRoadsMajorPointsAlongLines.visible = False
mapRoadsLyrRoadsMajorSplit.visible = False
mapRoadsLyrRoadsMajorSplitBuffer.visible = False
mapRoadsLyrRoadsMajorSplitBufferSum.visible = False

# move the layers
mapRoads.moveLayer(
    reference_layer=mapRoadsLyrRoadsMajorBuffers,
    move_layer=mapRoadsLyrRoadsMajorBuffersSum,
    insert_position="BEFORE",
)
mapRoads.moveLayer(
    reference_layer=mapRoadsLyrRoadsMajorBuffersSum,
    move_layer=mapRoadsLyrRoadsMajorPointsAlongLines,
    insert_position="BEFORE",
)
mapRoads.moveLayer(
    reference_layer=mapRoadsLyrRoadsMajorBuffersSum,
    move_layer=mapRoadsLyrRoadsMajorSplitBuffer,
    insert_position="BEFORE",
)
mapRoads.moveLayer(
    reference_layer=mapRoadsLyrRoadsMajorSplitBuffer,
    move_layer=mapRoadsLyrRoadsMajorSplitBufferSum,
    insert_position="BEFORE",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Major Roads layer

# Apply the symbology for the Major Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadsLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Major Road Split layer

# Apply the symbology for the major roads layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRoadsLyrRoadsMajorSplit,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the roads map layers
mapRoadsCimRoadsMajor = mapRoadsLyrRoadsMajor.getDefinition("V3")
mapRoadsCimRoadsMajorBuffers = mapRoadsLyrRoadsMajorBuffers.getDefinition("V3")
mapRoadsCimRoadsMajorBuffersSum = mapRoadsLyrRoadsMajorBuffersSum.getDefinition("V3")
mapRoadsCimRoadsMajorPointsAlongLines = (
    mapRoadsLyrRoadsMajorPointsAlongLines.getDefinition("V3")
)
mapRoadsCimRoadsMajorSplit = mapRoadsLyrRoadsMajorSplit.getDefinition("V3")
mapRoadsCimRoadsMajorSplitBuffer = mapRoadsLyrRoadsMajorSplitBuffer.getDefinition("V3")
mapRoadsCimRoadsMajorSplitBufferSum = mapRoadsLyrRoadsMajorSplitBufferSum.getDefinition(
    "V3"
)

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRoadsCimRoadsMajor.renderer.heading = "Road Category"
mapRoadsCimRoadsMajorBuffers.renderer.heading = "Major Road Buffers"
mapRoadsCimRoadsMajorBuffersSum.renderer.heading = "Major Road Buffers"
mapRoadsCimRoadsMajorPointsAlongLines.renderer.heading = "Major Road Points Along Lines"
mapRoadsCimRoadsMajorSplit.renderer.heading = "Road Category"
mapRoadsCimRoadsMajorSplitBuffer.renderer.heading = "Major Road Buffers"

# Update the map layer definitions
mapRoadsLyrRoadsMajor.setDefinition(mapRoadsCimRoadsMajor)
mapRoadsLyrRoadsMajorBuffers.setDefinition(mapRoadsCimRoadsMajorBuffers)
mapRoadsLyrRoadsMajorBuffersSum.setDefinition(mapRoadsCimRoadsMajorBuffersSum)
mapRoadsLyrRoadsMajorPointsAlongLines.setDefinition(
    mapRoadsCimRoadsMajorPointsAlongLines
)
mapRoadsLyrRoadsMajorSplit.setDefinition(mapRoadsCimRoadsMajorSplit)
mapRoadsLyrRoadsMajorSplitBuffer.setDefinition(mapRoadsCimRoadsMajorSplitBuffer)
mapRoadsLyrRoadsMajorSplitBufferSum.setDefinition(mapRoadsCimRoadsMajorSplitBufferSum)

# Update the CIM definition for the roads map
cimRoads = mapRoads.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRoads, "roads")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRoads.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.17


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.18 Hotspot Points Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.18 Hotspot Points Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the hotspot points map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the hotspot points map view
mapPointFhs.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapPointFhs.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapPointFhs.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapPointFhsLyrBoundaries = mapPointFhs.addDataFromPath(boundaries)
mapPointFhsLyrRoadsMajor = mapPointFhs.addDataFromPath(roadsMajor)
mapPointFhsLyrFhs = mapPointFhs.addDataFromPath(crashesHotspots)

# Set layer visibility on the map
mapPointFhsLyrBoundaries.visible = False
mapPointFhsLyrRoadsMajor.visible = False
mapPointFhsLyrFhs.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Major Roads layer

# Apply the symbology for the Major Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPointFhsLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Boundaries layer

# Apply the symbology for the boundaires data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPointFhsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the major roads map layers
mapPointFhsCimBoundaries = mapPointFhsLyrBoundaries.getDefinition("V3")
mapPointFhsCimRoadsMajor = mapPointFhsLyrRoadsMajor.getDefinition("V3")
mapPointFhsCimFhs = mapPointFhsLyrFhs.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapPointFhsCimBoundaries.renderer.heading = "Boundaries"
mapPointFhsCimRoadsMajor.renderer.heading = "Major Roads"
mapPointFhsCimFhs.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapPointFhsLyrBoundaries.setDefinition(mapPointFhsCimBoundaries)
mapPointFhsLyrRoadsMajor.setDefinition(mapPointFhsCimRoadsMajor)
mapPointFhsLyrFhs.setDefinition(mapPointFhsCimFhs)

# Update the CIM definition for the major roads map
cimPointFhs = mapPointFhs.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the major roads map mapx file
exportCim("map", mapPointFhs, "pointFhs")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapPointFhs.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.18


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.19 Optimized Hotspot Points Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.19 Optimized Hotspot Points Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the optimized hotspot points map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the optimized hot spot points map view
mapPointOhs.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapPointOhs.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapPointOhs.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapPointOhsLyrBoundaries = mapPointOhs.addDataFromPath(boundaries)
mapPointOhsLyrRoadsMajor = mapPointOhs.addDataFromPath(roadsMajor)
mapPointOhsLyrOhs = mapPointOhs.addDataFromPath(crashesOptimizedHotspots)

# Set layer visibility on the map
mapPointOhsLyrBoundaries.visible = False
mapPointOhsLyrRoadsMajor.visible = False
mapPointOhsLyrOhs.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Major Roads layer

# Apply the symbology for the Major Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPointOhsLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Boundaries layer

# Apply the symbology for the boundaires data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPointOhsLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the road buffers sum map layers
mapPointOhsCimBoundaries = mapPointOhsLyrBoundaries.getDefinition("V3")
mapPointOhsCimRoadsMajor = mapPointOhsLyrRoadsMajor.getDefinition("V3")
mapPointOhsCimOhs = mapPointOhsLyrOhs.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapPointOhsCimBoundaries.renderer.heading = "Boundaries"
mapPointOhsCimRoadsMajor.renderer.heading = "Major Roads"
mapPointOhsCimOhs.renderer.heading = "Getis-Ord Gi*"

# Update the map layer definitions
mapPointOhsLyrBoundaries.setDefinition(mapPointOhsCimBoundaries)
mapPointOhsLyrRoadsMajor.setDefinition(mapPointOhsCimRoadsMajor)
mapPointOhsLyrOhs.setDefinition(mapPointOhsCimOhs)

# Update the CIM definition for the major roads map
cimPointOhs = mapPointOhs.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the road buffers map mapx file
exportCim("map", mapPointOhs, "pointOhs")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapPointOhs.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.19


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.20 Population Density Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.20 Population Density Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the densities map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the population densities map view
mapPopDens.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapPopDens.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapPopDens.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapPopDensLyrBoundaries = mapPopDens.addDataFromPath(boundaries)
mapPopDensLyrRoadsMajor = mapPopDens.addDataFromPath(roadsMajor)
mapPopDensLyrPopDens = mapPopDens.addDataFromPath(blocksSum)

# Rename the layer
mapPopDensLyrPopDens.name = "OCSWITRS Population Density"

# Set layer visibility on the map
mapPopDensLyrBoundaries.visible = False
mapPopDensLyrRoadsMajor.visible = False
mapPopDensLyrPopDens.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Population Density layer

# Apply the symbology for the Housing Density data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPopDensLyrPopDens,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Population Density.lyrx"
    ),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPopDensLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapPopDensLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the densities map layers
mapPopDensCimBoundaries = mapPopDensLyrBoundaries.getDefinition("V3")
mapPopDensCimRoadsMajor = mapPopDensLyrRoadsMajor.getDefinition("V3")
mapPopDensCimPopDens = mapPopDensLyrPopDens.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapPopDensCimBoundaries.renderer.heading = "Boundaries"
mapPopDensCimRoadsMajor.renderer.heading = "Major Roads"
mapPopDensCimPopDens.renderer.heading = "Population Density"

# Update the map layer definitions
mapPopDensLyrBoundaries.setDefinition(mapPopDensCimBoundaries)
mapPopDensLyrRoadsMajor.setDefinition(mapPopDensCimRoadsMajor)
mapPopDensLyrPopDens.setDefinition(mapPopDensCimPopDens)

# Apply CIM operations to the layers in the densities map
cimPopDens = mapPopDens.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the densities map mapx file
exportCim("map", mapPopDens, "popDens")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapPopDens.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.20


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.21 Housing Density Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.21 Housing Density Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the housing density map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the housing density map view
mapHouDens.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapHouDens.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapHouDens.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapHouDensLyrBoundaries = mapHouDens.addDataFromPath(boundaries)
mapHouDensLyrRoadsMajor = mapHouDens.addDataFromPath(roadsMajor)
mapHouDensLyrHouDens = mapHouDens.addDataFromPath(blocksSum)

# Rename the layer
mapHouDensLyrHouDens.name = "OCSWITRS Housing Density"

# Set layer visibility on the map
mapHouDensLyrBoundaries.visible = False
mapHouDensLyrRoadsMajor.visible = False
mapHouDensLyrHouDens.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Housing Density layer

# Apply the symbology for the Housing Density data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapHouDensLyrHouDens,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Housing Density.lyrx"),
    symbology_fields=[["VALUE_FIELD", "housingDensity", "housingDensity"]],
    update_symbology="MAINTAIN",
)

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapHouDensLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapHouDensLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapHouDensCimBoundaries = mapHouDensLyrBoundaries.getDefinition("V3")
mapHouDensCimRoadsMajor = mapHouDensLyrRoadsMajor.getDefinition("V3")
mapHouDensCimHouDens = mapHouDensLyrHouDens.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapHouDensCimBoundaries.renderer.heading = "Boundaries"
mapHouDensCimRoadsMajor.renderer.heading = "Major Roads"
mapHouDensCimHouDens.renderer.heading = "Housing Density"

# Update the map layer definitions
mapHouDensLyrBoundaries.setDefinition(mapHouDensCimBoundaries)
mapHouDensLyrRoadsMajor.setDefinition(mapHouDensCimRoadsMajor)
mapHouDensLyrHouDens.setDefinition(mapHouDensCimHouDens)

# Update the CIM definition for the regression map
cimHouDens = mapHouDens.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapHouDens, "houDens")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapHouDens.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.21


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.22 Victims by City Areas Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.22 Victims by City Areas Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Open the city areas map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the city areas map layers
mapAreaCities.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapAreaCities.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapAreaCities.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapAreaCitiesLyrBoundaries = mapAreaCities.addDataFromPath(boundaries)
mapAreaCitiesLyrRoadsMajor = mapAreaCities.addDataFromPath(roadsMajor)
mapAreaCitiesLyrCities = mapAreaCities.addDataFromPath(citiesSum)

# Set layer visibility on the map
mapAreaCitiesLyrBoundaries.visible = False
mapAreaCitiesLyrRoadsMajor.visible = False
mapAreaCitiesLyrCities.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Boundaries layer

# Apply the symbology for the boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaCitiesLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaCitiesLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - City Areas Summary layer

# Apply the symbology for the cities sum data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaCitiesLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities Summary.lyrx"),
    symbology_fields=[["VALUE_FIELD", "sum_victimCount", "sum_victimCount"]],
    update_symbology="MAINTAIN",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the cities map layers
mapAreaCitiesCimBoundaries = mapAreaCitiesLyrBoundaries.getDefinition("V3")
mapAreaCitiesCimRoadsMajor = mapAreaCitiesLyrRoadsMajor.getDefinition("V3")
mapAreaCitiesCimCities = mapAreaCitiesLyrCities.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapAreaCitiesCimBoundaries.renderer.heading = "Boundaries"
mapAreaCitiesCimRoadsMajor.renderer.heading = "Major Roads"
mapAreaCitiesCimCities.renderer.heading = "Victim Count"

# Update the map layer definitions
mapAreaCitiesLyrBoundaries.setDefinition(mapAreaCitiesCimBoundaries)
mapAreaCitiesLyrRoadsMajor.setDefinition(mapAreaCitiesCimRoadsMajor)
mapAreaCitiesLyrCities.setDefinition(mapAreaCitiesCimCities)

# Update the CIM definition for the city area map
cimAreasCities = mapAreaCities.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the Cities map mapx file
exportCim("map", mapAreaCities, "areaCities")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapAreaCities.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.22


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.23 Victims by Census Blocks Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.23 Victims by Census Blocks Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Open the census blocks map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the census blocks map view
mapAreaBlocks.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapAreaBlocks.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapAreaBlocks.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapAreaBlocksLyrBoundaries = mapAreaBlocks.addDataFromPath(boundaries)
mapAreaBlocksLyrRoadsMajor = mapAreaBlocks.addDataFromPath(roadsMajor)
mapAreaBlocksLyrBlocks = mapAreaBlocks.addDataFromPath(blocksSum)

# Set layer visibility on the map
mapAreaBlocksLyrBoundaries.visible = False
mapAreaBlocksLyrRoadsMajor.visible = False
mapAreaBlocksLyrBlocks.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Boundaries layer

# Apply the symbology for the boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaBlocksLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)

# - Major Roads layer

# Apply the symbology for the major roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaBlocksLyrRoadsMajor,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Major Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)

# - Census Blocks Summary layer

# Apply the symbology for the census blocks sum data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapAreaBlocksLyrBlocks,
    in_symbology_layer=os.path.join(
        layersTemplates, "OCSWITRS Census Blocks Summary.lyrx"
    ),
    symbology_fields=[["VALUE_FIELD", "sum_victimCount", "sum_victimCount"]],
    update_symbology="DEFAULT",
)

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the blocks map layers
mapAreaBlocksCimBoundaries = mapAreaBlocksLyrBoundaries.getDefinition("V3")
mapAreaBlocksCimRoadsMajor = mapAreaBlocksLyrRoadsMajor.getDefinition("V3")
mapAreaBlocksCimBlocks = mapAreaBlocksLyrBlocks.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapAreaBlocksCimBoundaries.renderer.heading = "Boundaries"
mapAreaBlocksCimRoadsMajor.renderer.heading = "Major Roads"
mapAreaBlocksCimBlocks.renderer.heading = "Victim Count"

# Update the map layer definitions
mapAreaBlocksLyrBoundaries.setDefinition(mapAreaBlocksCimBoundaries)
mapAreaBlocksLyrRoadsMajor.setDefinition(mapAreaBlocksCimRoadsMajor)
mapAreaBlocksLyrBlocks.setDefinition(mapAreaBlocksCimBlocks)

# Update the CIM definition for the major roads map
cimAreaBlocks = mapAreaBlocks.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the Blocks map mapx file
exportCim("map", mapAreaBlocks, "areaBlocks")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapAreaBlocks.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.23


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.24 Summaries Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.24 Summaries Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the summaries map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the summaries map view
mapSummaries.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapSummaries.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapSummaries.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapSummariesLyrBlocksSum = mapSummaries.addDataFromPath(blocksSum)
mapSummariesLyrCitiesSum = mapSummaries.addDataFromPath(citiesSum)
mapSummariesLyrCrashes500ftFromMajorRoads = mapSummaries.addDataFromPath(
    crashes500ftFromMajorRoads
)

# Set layer visibility on the map
mapSummariesLyrBlocksSum.visible = False
mapSummariesLyrCitiesSum.visible = False
mapSummariesLyrCrashes500ftFromMajorRoads.visible = False

# Move the layers
mapSummaries.moveLayer(
    reference_layer=mapSummariesLyrBlocksSum,
    move_layer=mapSummariesLyrCitiesSum,
    insert_position="AFTER",
)

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Census Block Summary layer

# Apply the symbology for the Census 2020 Blocks summary layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapSummariesLyrBlocksSum,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities Summary layer

# Apply the symbology for the Cities summary layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapSummariesLyrCitiesSum,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Crashes 500ft from Major Roads layer

# Apply the symbology for the Crashes 500ft from Major Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapSummariesLyrCrashes500ftFromMajorRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Collisions.lyrx"),
    symbology_fields=[["VALUE_FIELD", "collSeverity", "collSeverity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the summaries map layers
mapSummariesCimBlocksSum = mapSummariesLyrBlocksSum.getDefinition("V3")
mapSummariesCimCitiesSum = mapSummariesLyrCitiesSum.getDefinition("V3")
mapSummariesCimCrashes500ftFromMajorRoads = (
    mapSummariesLyrCrashes500ftFromMajorRoads.getDefinition("V3")
)

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapSummariesCimBlocksSum.renderer.heading = "Population Density"
mapSummariesCimCitiesSum.renderer.heading = "City Population Density"
mapSummariesCimCrashes500ftFromMajorRoads.renderer.heading = "Collision Severity"

# Update the map layer definitions
mapSummariesLyrBlocksSum.setDefinition(mapSummariesCimBlocksSum)
mapSummariesLyrCitiesSum.setDefinition(mapSummariesCimCitiesSum)
mapSummariesLyrCrashes500ftFromMajorRoads.setDefinition(
    mapSummariesCimCrashes500ftFromMajorRoads
)

# Update the CIM definition for the summaries map
summariesCim = mapSummaries.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapSummaries, "summaries")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapSummaries.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.23


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.25 Analysis Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.25 Analysis Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the analysis map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the analysis map view
mapAnalysis.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapAnalysis.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapAnalysis.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapAnalysisLyrCrashesHotspots = mapAnalysis.addDataFromPath(crashesHotspots)
mapAnalysisLyrCrashesOptimizedHotspots = mapAnalysis.addDataFromPath(
    crashesOptimizedHotspots
)

# Set layer visibility on the map
mapAnalysisLyrCrashesHotspots.visible = False
mapAnalysisLyrCrashesOptimizedHotspots.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Update the CIM definition for the analysis map
analysisCim = mapAnalysis.getDefinition("V3")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the analysis map layers
mapAnalysisCimCrashesHotspots = mapAnalysisLyrCrashesHotspots.getDefinition("V3")
mapAnalysisCimCrashesOptimizedHotspots = (
    mapAnalysisLyrCrashesOptimizedHotspots.getDefinition("V3")
)

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapAnalysis, "analysis")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapAnalysis.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.24


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.26 Regression Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.26 Regression Map Layers")


# region Open Map View
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Open Map View")

# Close all open maps, open the regression map and set it as the active map

# Close all previous map views
aprx.closeViews()

# Open the regression map view
mapRegression.openView()

# set the main map as active map
map = aprx.activeMap

# Remove all layers from the active map

# Remove all the layers from the map
for lyr in mapRegression.listLayers():
    if not lyr.isBasemapLayer:
        print(f"Removing layer: {lyr.name}")
        mapRegression.removeLayer(lyr)

# endregion


# region Add Layers to Map
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Add Layers to Map")

# Add the feature classes as layers to the map (in order, as the first layer goes to the bottom of the contents)

# Add the data layers to the map
mapRegressionLyrBoundaries = mapRegression.addDataFromPath(boundaries)
mapRegressionLyrCities = mapRegression.addDataFromPath(cities)
mapRegressionLyrBlocks = mapRegression.addDataFromPath(blocks)
mapRegressionLyrRoads = mapRegression.addDataFromPath(roads)

# Set layer visibility on the map
mapRegressionLyrBoundaries.visible = False
mapRegressionLyrCities.visible = False
mapRegressionLyrBlocks.visible = False
mapRegressionLyrRoads.visible = False

# endregion


# region Layer Symbology
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer Symbology")

# Define symbology for each of the map layers. The symbology is predefined in the project's template layer folders.

# - Roads layer

# Apply the symbology for the Roads data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRegressionLyrRoads,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Roads.lyrx"),
    symbology_fields=[["VALUE_FIELD", "roadCat", "roadCat"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Census Blocks layer

# Apply the symbology for the US Census 2020 Blocks data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRegressionLyrBlocks,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Census Blocks.lyrx"),
    symbology_fields=[["VALUE_FIELD", "populationDensity", "populationDensity"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Cities layer

# Apply the symbology for the Cities data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRegressionLyrCities,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Cities.lyrx"),
    symbology_fields=[["VALUE_FIELD", "cityPopDens", "cityPopDens"]],
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# - Boundaries layer

# Apply the symbology for the Boundaries data layer
arcpy.management.ApplySymbologyFromLayer(
    in_layer=mapRegressionLyrBoundaries,
    in_symbology_layer=os.path.join(layersTemplates, "OCSWITRS Boundaries.lyrx"),
    symbology_fields=None,
    update_symbology="MAINTAIN",
)
print(arcpy.GetMessages())

# endregion


# region Layer CIM Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Layer CIM Operations")

# Generate CIM JSON configuration for layers

# Get CIM definitions for the regression map layers
mapRegressionCimBoundaries = mapRegressionLyrBoundaries.getDefinition("V3")
mapRegressionCimCities = mapRegressionLyrCities.getDefinition("V3")
mapRegressionCimBlocks = mapRegressionLyrBlocks.getDefinition("V3")
mapRegressionCimRoads = mapRegressionLyrRoads.getDefinition("V3")

# Set symbology headings and update CIM definitions for layers

# Set the layer headings
mapRegressionCimBoundaries.renderer.heading = "Boundaries"
mapRegressionCimCities.renderer.heading = "Cities"
mapRegressionCimBlocks.renderer.heading = "Census Blocks"
mapRegressionCimRoads.renderer.heading = "Roads"

# Update the map layer definitions
mapRegressionLyrBoundaries.setDefinition(mapRegressionCimBoundaries)
mapRegressionLyrCities.setDefinition(mapRegressionCimCities)
mapRegressionLyrBlocks.setDefinition(mapRegressionCimBlocks)
mapRegressionLyrRoads.setDefinition(mapRegressionCimRoads)

# Update the CIM definition for the regression map
cimRegression = mapRegression.getDefinition("V3")

# endregion


# region Export Map and Map Layers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Export Map and Map Layers")

# Update the mapx file with the new layers

# Update the victims map mapx file
exportCim("map", mapRegression, "regression")

# Export map layers as CIM JSON `.lyrx` files to the layers folder directory of the project.

# Export the layers to JSON
for l in mapRegression.listLayers():
    if not l.isBasemapLayer:
        exportCim("layer", l, l.name)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 3.25
# endregion 3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 4 Map CIM and Exporting
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n4 Map CIM and Exporting")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 4.1 Map CIM Processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n4.1 Map CIM Processing")


# region Get Map CIM
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Get Map CIM")

# For each map, obtain the map CIM object

# Get the CIM definitions for the OCSWIRS maps
cimCollisions = mapCollisions.getDefinition("V3")
cimCrashes = mapCollisions.getDefinition("V3")
cimParties = mapCollisions.getDefinition("V3")
cimVictims = mapVictims.getDefinition("V3")
cimInjuries = mapInjuries.getDefinition("V3")
cimFatalities = mapFatalities.getDefinition("V3")
cimFhs100m1km = mapFhs100m1km.getDefinition("V3")
cimFhs150m2km = mapFhs150m2km.getDefinition("V3")
cimFhs100m5km = mapFhs100m5km.getDefinition("V3")
cimFhsRoads500ft = mapFhsRoads500ft.getDefinition("V3")
cimOhsRoads500ft = mapOhsRoads500ft.getDefinition("V3")
cimRoadCrashes = mapRoadCrashes.getDefinition("V3")
cimRoadHotspots = mapRoadHotspots.getDefinition("V3")
cimRoadBuffers = mapRoadBuffers.getDefinition("V3")
cimRoadSegments = mapRoadSegments.getDefinition("V3")
cimRoads = mapRoads.getDefinition("V3")
cimPointFhs = mapPointFhs.getDefinition("V3")
cimPointOhs = mapPointOhs.getDefinition("V3")
cimPopDens = mapPopDens.getDefinition("V3")
cimHouDens = mapHouDens.getDefinition("V3")
cimAreaCities = mapAreaCities.getDefinition("V3")
cimAreaBlocks = mapAreaBlocks.getDefinition("V3")
cimSummaries = mapSummaries.getDefinition("V3")
cimAnalysis = mapAnalysis.getDefinition("V3")
cimRegression = mapRegression.getDefinition("V3")

# endregion


# region Use Service Layer IDs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Use Service Layer IDs")

# Change the map properties to allow assignment of unique numeric IDs for sharing web layers

# Collisions Map
cimCollisions.useServiceLayerIDs = True
mapCollisions.setDefinition(cimCollisions)
# Crashes Map
cimCrashes.useServiceLayerIDs = True
mapCrashes.setDefinition(cimCrashes)
# Parties Map
cimParties.useServiceLayerIDs = True
mapParties.setDefinition(cimParties)
# Victims Map
cimVictims.useServiceLayerIDs = True
mapVictims.setDefinition(cimVictims)
# Injuries Map
cimInjuries.useServiceLayerIDs = True
mapInjuries.setDefinition(cimInjuries)
# Fatalities Map
cimFatalities.useServiceLayerIDs = True
mapFatalities.setDefinition(cimFatalities)
# FHS 100m 1km Map
cimFhs100m1km.useServiceLayerIDs = True
mapFhs100m1km.setDefinition(cimFhs100m1km)
# FHS 150m 2km Map
cimFhs150m2km.useServiceLayerIDs = True
mapFhs150m2km.setDefinition(cimFhs150m2km)
# FHS 100m 5km Map
cimFhs100m5km.useServiceLayerIDs = True
mapFhs100m5km.setDefinition(cimFhs100m5km)
# FHS Roads 500ft Map
cimFhsRoads500ft.useServiceLayerIDs = True
mapFhsRoads500ft.setDefinition(cimFhsRoads500ft)
# OHS Roads 500ft Map
cimOhsRoads500ft.useServiceLayerIDs = True
mapOhsRoads500ft.setDefinition(cimOhsRoads500ft)
# Road Crashes Map
cimRoadCrashes.useServiceLayerIDs = True
mapRoadCrashes.setDefinition(cimRoadCrashes)
# Road Hotspots Map
cimRoadHotspots.useServiceLayerIDs = True
mapRoadHotspots.setDefinition(cimRoadHotspots)
# Road Buffers Map
cimRoadBuffers.useServiceLayerIDs = True
mapRoadBuffers.setDefinition(cimRoadBuffers)
# Road Segments Map
cimRoadSegments.useServiceLayerIDs = True
mapRoadSegments.setDefinition(cimRoadSegments)
# Roads Map
cimRoads.useServiceLayerIDs = True
mapRoads.setDefinition(cimRoads)
# Point FHS Map
cimPointFhs.useServiceLayerIDs = True
mapPointFhs.setDefinition(cimPointFhs)
# Point OHS Map
cimPointOhs.useServiceLayerIDs = True
mapPointOhs.setDefinition(cimPointOhs)
# Population Density Map
cimPopDens.useServiceLayerIDs = True
mapPopDens.setDefinition(cimPopDens)
# Housing Density Map
cimHouDens.useServiceLayerIDs = True
mapHouDens.setDefinition(cimHouDens)
# Area Cities Map
cimAreaCities.useServiceLayerIDs = True
mapAreaCities.setDefinition(cimAreaCities)
# Area Blocks Map
cimAreaBlocks.useServiceLayerIDs = True
mapAreaBlocks.setDefinition(cimAreaBlocks)
# Summaries Map
cimSummaries.useServiceLayerIDs = True
mapSummaries.setDefinition(cimSummaries)
# Analysis Map
cimAnalysis.useServiceLayerIDs = True
mapAnalysis.setDefinition(cimAnalysis)
# Regression Map
cimRegression.useServiceLayerIDs = True
mapRegression.setDefinition(cimRegression)

# endregion
# endregion 4.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 4.2 Export Maps to JSON
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n4.2 Export Maps to JSON")

# Export maps to mapx CIM JSON files
for m in aprx.listMaps():
    print(f"Exporting {m.name} map...")
    exportCim("map", m, m.name)


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 4.2
# endregion 4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region End of Script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nEnd of Script")

#endregion
