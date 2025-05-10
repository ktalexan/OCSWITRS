# -*- coding: utf-8 -*-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OC SWITRS GIS Data Processing
# Part 1 - Feature Class Geoprocessing
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\nOC SWITRS GIS Data Processing - Part 1 - Feature Class Geoprocessing\n")


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
import os, sys, json, math
from datetime import date, time, datetime, timedelta, tzinfo, timezone
import arcpy, arcgis, pytz
from arcpy import metadata as md

# important as it "enhances" Pandas by importing these classes (from ArcGIS API for Python)
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# endregion 1.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.2. Project and Workspace Variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.2. Project and Workspace Variables")

# Define and maintain project, workspace, ArcGIS, and data-related variables


# region Project and Geodatabase Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Project and Geodatabase Paths")
# Define the ArcGIS pro project variables

# Current notebook directory
notebookDir = os.getcwd()
# Define the project folder (parent directory of the current working directory)
projectFolder = os.path.dirname(os.getcwd())

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
# ArcGIS Pro Project object
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
layersTemplate = os.path.join(layersFolder, "templates")
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
dateStart = datetime(2012, 1, 1)
# Add the end date of the raw data to a new python datetime object
dateEnd = datetime(2024, 12, 31)
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
def export_cim(cimType, cimObject, cimName):
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
layoutList = ["maps", "injuries", "hotspots", "roads", "points", "densities", "areas"]

# endregion
# endregion 1.4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 1.5. Clean Up Data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n1.5. Clean Up Data")

# region Delete Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Delete Feature Classes")

# Clean up the feature classes in the geodatabase for the Analysis and Hotspot Feature Datasets
for d in ["analysis", "hotspots"]:
    print(f"Dataset: {d}")
    for f in arcpy.ListFeatureClasses(feature_dataset=d):
        print(f"- Removing {f} feature class from the project...")
        arcpy.management.Delete(f)

# endregion


# region Delete Maps
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Delete Maps")

# Clean up the maps in the project structure
for m in aprx.listMaps():
    print(f"- Removing {m.name} map from the project...")
    aprx.deleteItem(m)

# endregion


# region Delete Layouts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Delete Layouts")

# Clean up the layouts in the project structure
for l in aprx.listLayouts():
    print(f"- Removing {l.name} layout from the project...")
    aprx.deleteItem(l)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 1.5
# endregion 1
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2. Geodatabase Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2. Geodatabase Operations")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.1. Raw Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.1. Raw Data Feature Classes")

# region Feature Class Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Paths")

# Paths to raw data geodatabase feature classes

# Paths to raw data feature classes
victims = os.path.join(gdbRawData, "victims")
parties = os.path.join(gdbRawData, "parties")
crashes = os.path.join(gdbRawData, "crashes")
collisions = os.path.join(gdbRawData, "collisions")

# endregion


# region Feature Class Fields
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Fields")

# Obtain a list of fields for each raw data geodatabase feature class

# Fields for the raw data feature classes
victimsFields = [f.name for f in arcpy.ListFields(victims)]  # victims field list
partiesFields = [f.name for f in arcpy.ListFields(parties)]  # parties field list
crashesFields = [f.name for f in arcpy.ListFields(crashes)]  # crashes field list
collisionsFields = [
    f.name for f in arcpy.ListFields(collisions)
]  # collisions field list

# endregion


# region Raw Counts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Raw Counts")

# Count rows in each of the raw data geodatabase feature classes

# Get the count for the raw data feature classes
victimsCount = int(arcpy.management.GetCount(victims)[0])
partiesCount = int(arcpy.management.GetCount(parties)[0])
crashesCount = int(arcpy.management.GetCount(crashes)[0])
collisionsCount = int(arcpy.management.GetCount(collisions)[0])

print(
    f"\nRaw Data Counts:\n- Victims: {victimsCount:,}\n- Parties: {partiesCount:,}\n- Crashes: {crashesCount:,}\n- Collisions: {collisionsCount:,}"
)

# endregion


# region Feature Class Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Aliases")

# Adding feature class alias for the collisions feature class

# Collisions feature class alias
collisionsAlias = "OCSWITRS Collisions"
# Collisions feature class
arcpy.AlterAliasName(collisions, collisionsAlias)
print(f"Collisions: {arcpy.GetMessages()}")

# Adding field aliases to the collisions feature class

# Collisions field aliases
for f in collisionsFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=collisions, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Crashes Feature Class Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes Feature Class Aliases")

# Adding feature class alias for the crashes feature class

# Crashes feature class alias
crashesAlias = "OCSWITRS Crashes"
# Crashes feature class
arcpy.AlterAliasName(crashes, crashesAlias)
print(f"Crashes: {arcpy.GetMessages()}")

# Adding field aliases to the crashes feature class

# Crashes field aliases
for f in crashesFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=crashes, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Parties Feature Class Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Parties Feature Class Aliases")

# Adding feature class alias for the parties feature class

# Parties feature class alias
partiesAlias = "OCSWITRS Parties"
# Parties feature class
arcpy.AlterAliasName(parties, partiesAlias)
print(f"Parties: {arcpy.GetMessages()}")

# Adding field aliases to the parties feature class

# Parties field aliases
for f in partiesFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=parties, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Victims Feature Class Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims Feature Class Aliases")

# Adding feature class alias for the victims feature class

# Victims feature class alias
victimsAlias = "OCSWITRS Victims"
# Victims feature class
arcpy.AlterAliasName(victims, victimsAlias)
print(f"Victims: {arcpy.GetMessages()}")


# Adding field aliases to the victims feature class

# Victims field aliases
for f in victimsFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=victims, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion
# endregion 2.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.2. Supporting Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.2. Supporting Data Feature Classes")


# region Feature Class Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Paths")

# Paths to the supporting data geodatabase feature classes

# Paths to supporting data feature classes
boundaries = os.path.join(gdbSupportingData, "boundaries")
cities = os.path.join(gdbSupportingData, "cities")
blocks = os.path.join(gdbSupportingData, "blocks")
roads = os.path.join(gdbSupportingData, "roads")

# endregion


# region Feature Class Fields
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Fields")

# Obtain the list fields of the supporting data geodatabase feature classes

# Fields for the supporting data feature classes
boundariesFields = [f.name for f in arcpy.ListFields(boundaries)]
# boundaries field list
citiesFields = [f.name for f in arcpy.ListFields(cities)]  # cities field list
blocksFields = [f.name for f in arcpy.ListFields(blocks)]  # censusBlocks field list
roadsFields = [f.name for f in arcpy.ListFields(roads)]  # roads field list

# endregion


# region Row Counts
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Row Counts")

# Count rows in each of the supporting data geodatabase feature classes

# Get the count for the supporting data feature classes
boundariesCount = int(arcpy.management.GetCount(boundaries)[0])
citiesCount = int(arcpy.management.GetCount(cities)[0])
blocksCount = int(arcpy.management.GetCount(blocks)[0])
roadsCount = int(arcpy.management.GetCount(roads)[0])

# Print the counts
print(
    f"Supporting Data Counts:\n- Boundaries: {boundariesCount:,}\n- Cities: {citiesCount:,}\n- Census Blocks: {blocksCount:,}\n- Roads: {roadsCount:,}"
)

# endregion


# region Roads Feature Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Roads Feature Class")

# Adding feature class alias for the roads feature class

# Roads feature class alias
roadsAlias = "OCSWITRS Roads"
# Roads feature class
arcpy.AlterAliasName(roads, roadsAlias)
print(f"Roads: {arcpy.GetMessages()}")

# Adding field aliases to the roads feature class

# Roads field aliases
for f in roadsFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=roads, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Census Blocks Feature Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Census Blocks Feature Class")

# Adding feature class alias for the census blocks feature class

# Census Blocks feature class alias
blocksAlias = "OCSWITRS Census Blocks"
# Census Blocks feature class
arcpy.AlterAliasName(blocks, blocksAlias)
print(f"USC 2020 Census Blocks: {arcpy.GetMessages()}")

# Adding field aliases to the census blocks feature class
# Census Blocks field aliases
for f in blocksFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=blocks, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Cities Feature Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Cities Feature Class")

# Adding feature class alias for the cities feature class

# Cities feature class alias
citiesAlias = "OCSWITRS Cities"
# Cities feature class
arcpy.AlterAliasName(cities, citiesAlias)
print(f"Cities: {arcpy.GetMessages()}")

# Adding field aliases to the cities feature class
# Cities field aliases
for f in citiesFields:
    if f in list(codebook.keys()):
        print(f"\tMatch {codebook[f]['varOrder']}: {f} ({codebook[f]['label']})")
        arcpy.management.AlterField(
            in_table=cities, field=f, new_field_alias=codebook[f]["label"]
        )
print(arcpy.GetMessages())

# endregion


# region Boundaries Feature Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Boundaries Feature Class")

# Adding feature class alias for the boundaries feature class

# Boundaries feature class alias
boundariesAlias = "OCSWITRS Boundaries"
# Boundaries feature class
arcpy.AlterAliasName(boundaries, boundariesAlias)
print(f"Boundaries: {arcpy.GetMessages()}")

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 2.2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.3. Data Enrichment Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.3. Data Enrichment Feature Classes")


# region Feature Class Paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Paths")

collisions1 = os.path.join(gdbRawData, "collisions1")

# endregion


# region Feature Class Joins
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Feature Class Joins")

# Join the collisions feature class with the censusBlocks feature class
arcpy.analysis.SpatialJoin(
    target_features=collisions,
    join_features=blocks,
    out_feature_class=collisions1,
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    match_option="INTERSECT",
    search_radius=None,
    distance_field_name=None,
    match_fields=None,
)

# endregion
# endregion 2.3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.4. Analysis Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.4. Analysis Data Feature Classes")


# region Delete all Old Analysis Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Delete all Old Analysis Feature Classes")

# Loop through all analysis data feature dataset and delete all feature classes
for f in arcpy.ListFeatureClasses(feature_dataset="analysis"):
    print(f"Deleting {f}...")
    arcpy.Delete_management(f)
    print(arcpy.GetMessages())

# endregion


# region Create Major Roads
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create Major Roads")

# Separate the primary and secondary roads from the local roads

# Output feature class for the major roads
roadsMajor = os.path.join(gdbAnalysisData, "roadsMajor")

# Select the major (primary and secondary) roads from the roads feature class
arcpy.analysis.Select(
    in_features=roads,
    out_feature_class=roadsMajor,
    where_clause="roadCat = 'Primary' Or roadCat = 'Secondary'",
)
print(arcpy.GetMessages())

# Add feature class alias for the major roads feature class

# Define the major roads layer alias and modify the feature class alias
roadsMajorAlias = "OCSWITRS Major Roads"
arcpy.AlterAliasName(roadsMajor, roadsMajorAlias)
print(arcpy.GetMessages())

# Obtain the list of fields for the major roads feature class
roadsMajorFields = [
    f.name for f in arcpy.ListFields(roadsMajor)
]  # roadsMajor field list

# Field Aliases for the major roads feature class
for f in arcpy.ListFields(roadsMajor):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Create Major Roads Buffers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create Major Roads Buffers")

# Create road buffers for the primary and secondary roads

# Output feature class for the major roads buffers
roadsMajorBuffers = os.path.join(gdbAnalysisData, "roadsMajorBuffers")

# Buffer the major roads feature class by 250 meters (on each side)
arcpy.analysis.Buffer(
    in_features=roadsMajor,
    out_feature_class=roadsMajorBuffers,
    buffer_distance_or_field="250 Meters",
    line_side="FULL",
    line_end_type="FLAT",
    dissolve_option="NONE",
    dissolve_field=None,
    method="PLANAR",
)
print(arcpy.GetMessages())

# Add feature class alias for the major road buffers feature class

# Define the major roads buffers layer alias and modify the feature class alias
roadsMajorBuffersAlias = "OCSWITRS Major Roads Buffers"
arcpy.AlterAliasName(roadsMajorBuffers, roadsMajorBuffersAlias)
print(arcpy.GetMessages())

# Obtain the list of fields for the major road buffers feature class
roadsMajorBuffersFields = [
    f.name for f in arcpy.ListFields(roadsMajorBuffers)
]  # roadsMajorBuffers field list

# Field Aliases for the major roads buffers feature class
for f in arcpy.ListFields(roadsMajorBuffers):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Summarize Major Road Buffers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summarize Major Road Buffers")

# Create a summary for each of the road buffers that contains statistics and counts of crash collision data

# Output feature class for the summarized major roads buffers
roadsMajorBuffersSum = os.path.join(gdbAnalysisData, "roadsMajorBuffersSum")

# Summarize the major roads buffers feature class by key crashes attributes
arcpy.analysis.SummarizeWithin(
    in_polygons=roadsMajorBuffers,
    in_sum_features=crashes,
    out_feature_class=roadsMajorBuffersSum,
    keep_all_polygons="KEEP_ALL",
    sum_fields=[
        ["crashTag", "Sum"],
        ["partyCount", "Sum"],
        ["victimCount", "Sum"],
        ["numberKilled", "Sum"],
        ["numberInj", "Sum"],
        ["countSevereInj", "Sum"],
        ["countVisibleInj", "Sum"],
        ["countComplaintPain", "Sum"],
        ["countCarKilled", "Sum"],
        ["countCarInj", "Sum"],
        ["countPedKilled", "Sum"],
        ["countPedInj", "Sum"],
        ["countBicKilled", "Sum"],
        ["countBicInj", "Sum"],
        ["countMcKilled", "Sum"],
        ["countMcInj", "Sum"],
        ["collSeverityNum", "Mean"],
        ["collSeverityRankNum", "Mean"],
    ],
)
print(arcpy.GetMessages())

# Add feature class alias for the summarized major road buffers feature class

# Define the major roads buffers summary layer alias and modify the feature class alias
roadsMajorBuffersSumAlias = "OCSWITRS Major Roads Buffers Summary"
arcpy.AlterAliasName(roadsMajorBuffersSum, roadsMajorBuffersSumAlias)
print(arcpy.GetMessages())

# Obtain the fields for the summarized major road buffers feature class
roadsMajorBuffersSumFields = [
    f.name for f in arcpy.ListFields(roadsMajorBuffersSum)
]  # roadsMajorBuffersSum field list

# Field Aliases for the major roads buffers summary feature class
for f in arcpy.ListFields(roadsMajorBuffersSum):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Points 1,000 ft along major road lines
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Points 1,000 ft along major road lines")

# Generate points every 1,000 feet along the major road lines

# Create a path for the new summarized major road buffers feature class
roadsMajorPointsAlongLines = os.path.join(gdbAnalysisData, "roadsMajorPointsAlongLines")

arcpy.management.GeneratePointsAlongLines(
    Input_Features=roadsMajor,
    Output_Feature_Class=roadsMajorPointsAlongLines,
    Point_Placement="DISTANCE",
    Distance="1000 Feet",
    Percentage=None,
    Include_End_Points="NO_END_POINTS",
    Add_Chainage_Fields="NO_CHAINAGE",
    Distance_Field=None,
    Distance_Method="PLANAR",
)

# Add feature class alias for the points along major road lines feature class

# Define the major roads points along lines layer alias and modify the feature class alias
roadsMajorPointsAlongLinesAlias = "OCSWITRS Major Roads Points Along Lines"
arcpy.AlterAliasName(roadsMajorPointsAlongLines, roadsMajorPointsAlongLinesAlias)
print(arcpy.GetMessages())

# Obtain the fields for the points along major road lines feature class
roadsMajorPointsAlongLinesFields = [
    f.name for f in arcpy.ListFields(roadsMajorPointsAlongLines)
]  # roadsMajorPointsAlongLines field list

# Field Aliases for the major roads points along lines feature class
for f in arcpy.ListFields(roadsMajorPointsAlongLines):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Split Road Segments 1,000 ft apart
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Split Road Segments 1,000 ft apart")

# Split road segments at the points (1,000 feet apart)

# Create a path for the new split major roads feature class
roadsMajorSplit = os.path.join(gdbAnalysisData, "roadsMajorSplit")

# Split the major roads at the points along the lines
arcpy.management.SplitLineAtPoint(
    in_features=roadsMajor,
    point_features=roadsMajorPointsAlongLines,
    out_feature_class=roadsMajorSplit,
    search_radius="1000 Feet",
)

# Add feature class alias for the split road segments feature class

# Define the major roads split layer alias and modify the feature class alias
roadsMajorSplitAlias = "OCSWITRS Major Roads Split"
arcpy.AlterAliasName(roadsMajorSplit, roadsMajorSplitAlias)
print(arcpy.GetMessages())

# Obtain the fields for the split road segments feature class
roadsMajorSplitFields = [
    f.name for f in arcpy.ListFields(roadsMajorSplit)
]  # roadsMajorSplit field list

# Field Aliases for the major roads split feature class
for f in arcpy.ListFields(roadsMajorSplit):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Buffers 500ft around road segments
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Buffers 500ft around road segments")

# Create buffers (500 ft) around the road segments (1,000 feet)

# Create a path for the new split major roads feature class
roadsMajorSplitBuffer = os.path.join(gdbAnalysisData, "roadsMajorSplitBuffer")

# Buffer the split major roads by 500 feet
arcpy.analysis.Buffer(
    in_features=roadsMajorSplit,
    out_feature_class=roadsMajorSplitBuffer,
    buffer_distance_or_field="500 Feet",
    line_side="FULL",
    line_end_type="FLAT",
    dissolve_option="NONE",
    dissolve_field=None,
    method="PLANAR",
)

# Add feature class alias for the road segment buffers feature class

# Define the major roads split buffer layer alias and modify the feature class alias
roadsMajorSplitBufferAlias = "OCSWITRS Major Roads Split Buffer"
arcpy.AlterAliasName(roadsMajorSplitBuffer, roadsMajorSplitBufferAlias)
print(arcpy.GetMessages())

# Obtain the fields for the road segment buffers feature class
roadsMajorSplitBufferFields = [
    f.name for f in arcpy.ListFields(roadsMajorSplitBuffer)
]  # roadsMajorSplitBuffer field list

# Field Aliases for the major roads split buffer feature class
for f in arcpy.ListFields(roadsMajorSplitBuffer):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Summarize road segments buffers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summarize road segments buffers")

# Summarize the crash collision data for each of the road segments

# Create a path for the new summarized major road buffers feature class
roadsMajorSplitBufferSum = os.path.join(gdbAnalysisData, "roadsMajorSplitBufferSum")

# Summarize the data within the major road buffers from the crashes data
arcpy.analysis.SummarizeWithin(
    in_polygons=roadsMajorSplitBuffer,
    in_sum_features=crashes,
    out_feature_class=roadsMajorSplitBufferSum,
    keep_all_polygons="KEEP_ALL",
    sum_fields=[
        ["crashTag", "Sum"],
        ["partyCount", "Sum"],
        ["victimCount", "Sum"],
        ["numberKilled", "Sum"],
        ["numberInj", "Sum"],
        ["countSevereInj", "Sum"],
        ["countVisibleInj", "Sum"],
        ["countComplaintPain", "Sum"],
        ["countCarKilled", "Sum"],
        ["countCarInj", "Sum"],
        ["countPedKilled", "Sum"],
        ["countPedInj", "Sum"],
        ["countBicKilled", "Sum"],
        ["countBicInj", "Sum"],
        ["countMcKilled", "Sum"],
        ["countMcInj", "Sum"],
        ["collSeverityNum", "Mean"],
        ["collSeverityRankNum", "Mean"],
    ],
)

# Add feature class alias for the summarized road segments buffers feature class

# Define the major roads split buffer summary layer alias and modify the feature class alias
roadsMajorSplitBufferSumAlias = "OCSWITRS Major Roads Split Buffer Summary"
arcpy.AlterAliasName(roadsMajorSplitBufferSum, roadsMajorSplitBufferSumAlias)
print(arcpy.GetMessages())

# Obtain the fields for the summarized road segments buffers feature class
roadsMajorSplitBufferSumFields = [
    f.name for f in arcpy.ListFields(roadsMajorSplitBufferSum)
]  # roadsMajorSplitBufferSum field list

# Field Aliases for the major roads split buffer summary feature class
for f in arcpy.ListFields(roadsMajorSplitBufferSum):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Summarize Census Blocks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summarize Census Blocks")


# Create a summary for each of the Census blocks that contains statistics and counts of crash collision data

# Create a path for the new summarized US 2020 Census Blocks feature class
blocksSum = os.path.join(gdbAnalysisData, "blocksSum")

arcpy.analysis.SummarizeWithin(
    in_polygons=blocks,
    in_sum_features=crashes,
    out_feature_class=blocksSum,
    keep_all_polygons="KEEP_ALL",
    sum_fields=[
        ["crashTag", "Sum"],
        ["partyCount", "Sum"],
        ["victimCount", "Sum"],
        ["numberKilled", "Sum"],
        ["numberInj", "Sum"],
        ["countSevereInj", "Sum"],
        ["countVisibleInj", "Sum"],
        ["countComplaintPain", "Sum"],
        ["countCarKilled", "Sum"],
        ["countCarInj", "Sum"],
        ["countPedKilled", "Sum"],
        ["countPedInj", "Sum"],
        ["countBicKilled", "Sum"],
        ["countBicInj", "Sum"],
        ["countMcKilled", "Sum"],
        ["countMcInj", "Sum"],
        ["collSeverityNum", "Mean"],
        ["collSeverityRankNum", "Mean"],
    ],
)

# Add feature class alias for the summarized Census blocks feature class

# Define the US 2020 Census Blocks summary layer alias and modify the feature class alias
blocksSumAlias = "OCSWITRS Census Blocks Summary"
arcpy.AlterAliasName(blocksSum, blocksSumAlias)
print(arcpy.GetMessages())

# Obtain the fields for the summarized Census blocks feature class
blocksSumFields = [
    f.name for f in arcpy.ListFields(blocksSum)
]  # cenBlocksSum field list

# Field Aliases for the US 2020 Census Blocks summary feature class
for f in arcpy.ListFields(blocksSum):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Summarize Cities
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Summarize Cities")

# Create a summary for each of the cities that contains statistics and counts of crash collision data

# Create a path for the new summarized US 2020 Census Blocks feature class
citiesSum = os.path.join(gdbAnalysisData, "citiesSum")

# Summarize the data within the cities from the crashes data
arcpy.analysis.SummarizeWithin(
    in_polygons=cities,
    in_sum_features=crashes,
    out_feature_class=citiesSum,
    keep_all_polygons="KEEP_ALL",
    sum_fields=[
        ["crashTag", "Sum"],
        ["partyCount", "Sum"],
        ["victimCount", "Sum"],
        ["numberKilled", "Sum"],
        ["numberInj", "Sum"],
        ["countSevereInj", "Sum"],
        ["countVisibleInj", "Sum"],
        ["countComplaintPain", "Sum"],
        ["countCarKilled", "Sum"],
        ["countCarInj", "Sum"],
        ["countPedKilled", "Sum"],
        ["countPedInj", "Sum"],
        ["countBicKilled", "Sum"],
        ["countBicInj", "Sum"],
        ["countMcKilled", "Sum"],
        ["countMcInj", "Sum"],
        ["collSeverityNum", "Mean"],
        ["collSeverityRankNum", "Mean"],
    ],
)

# Add feature class alias for the summarized cities feature class

# Define the cities summary layer alias and modify the feature class alias
citiesSumAlias = "OCSWITRS Cities Summary"
arcpy.AlterAliasName(citiesSum, citiesSumAlias)
print(arcpy.GetMessages())

# Obtain the fields for the summarized cities feature class
citiesSumFields = [f.name for f in arcpy.ListFields(citiesSum)]  # citiesSum field list

# Field Aliases for the cities summary feature class
for f in arcpy.ListFields(citiesSum):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Crashes within 500ft from Major Roads
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes within 500ft from Major Roads")

# Select all crashes that are within 500 ft of the major roads

# Create a path for the new feature class
crashes500ftFromMajorRoads = os.path.join(gdbAnalysisData, "crashes500ftFromMajorRoads")

# Select the crashes within 500 feet of the major roads and store it in a temporary layer
tempLyr = arcpy.management.SelectLayerByLocation(
    in_layer=crashes,
    select_features=roadsMajor,
    search_distance="500 Feet",
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT",
)

# Export the selected crashes to a new feature class
arcpy.conversion.ExportFeatures(
    in_features=tempLyr,
    out_features=crashes500ftFromMajorRoads,
    where_clause="",
    use_field_alias_as_name="NOT_USE_ALIAS",
)
print(arcpy.GetMessages())

# Delete the temporary layer
arcpy.management.Delete(tempLyr)

# Add feature class alias for the crashes within 500 ft from major roads feature class

# Define the crashes 500 feet from major roads layer alias and modify the feature class alias
crashes500ftFromMajorRoadsAlias = "OCSWITRS Crashes 500 Feet from Major Roads"
arcpy.AlterAliasName(crashes500ftFromMajorRoads, crashes500ftFromMajorRoadsAlias)
print(arcpy.GetMessages())

# Obtain the fields for the crashes within 500 ft from major roads feature class
crashes500ftFromMajorRoadsFields = [
    f.name for f in arcpy.ListFields(crashes500ftFromMajorRoads)
]  # crashes500ftFromMajorRoads field list

# Field Aliases for the crashes 500 feet from major roads feature class
for f in arcpy.ListFields(crashes500ftFromMajorRoads):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Crashes (Collision Severity) Exploratory Regression
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes (Collision Severity) Exploratory Regression")

# Generate a collision severity binary indicator to crashes dataset

# Add collision severity binary indicator to crashes
arcpy.management.CalculateField(
    in_table=crashes,
    field="severityBin",
    expression="sevbin(!collSeverityBin!)",
    expression_type="PYTHON3",
    code_block="""def sevbin(x):
    if x == "Severe or fatal":
        return 1
    elif x == "None, minor or pain":
        return 0""",
    field_type="SHORT",
    enforce_domains="NO_ENFORCE_DOMAINS",
)

# Add a field alias for the collision severity binary indicator
arcpy.management.AlterField(
    in_table=crashes, field="severityBin", new_field_alias="Severity Binary"
)

# Perform exploratory regression to predict the binary severity bin
arcpy.stats.ExploratoryRegression(
    Input_Features=crashes,
    Dependent_Variable="severityBin",
    Candidate_Explanatory_Variables="accidentYear;collSeverityNum;collSeverityRankNum;partyCount;victimCount;numberKilled;numberInj;countSevereInj;countVisibleInj;countComplaintPain;countCarKilled;countCarInj;countPedKilled;countPedInj;countBicKilled;countBicInj;countMcKilled;countMcInj",
    Weights_Matrix_File=None,
    Output_Report_File=None,
    Output_Results_Table=None,
    Maximum_Number_of_Explanatory_Variables=5,
    Minimum_Number_of_Explanatory_Variables=1,
    Minimum_Acceptable_Adj_R_Squared=0.5,
    Maximum_Coefficient_p_value_Cutoff=0.05,
    Maximum_VIF_Value_Cutoff=7.5,
    Minimum_Acceptable_Jarque_Bera_p_value=0.1,
    Minimum_Acceptable_Spatial_Autocorrelation_p_value=0.1,
)

# endregion


# region Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Save Project")

# Save the project
aprx.save()

# endregion
# endregion 2.4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 2.5. Hotspot Data Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n2.5. Hotspot Data Feature Classes")


# region Delete all Old Hotspot Feature Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Delete all Old Hotspot Feature Classes")

# Loop through all hotspot data feature dataset and delete all feature classes
for f in arcpy.ListFeatureClasses(feature_dataset="hotspots"):
    print(f"Deleting {f}...")
    arcpy.Delete_management(f)
    print(arcpy.GetMessages())

# endregion


# region Create Hot Spots (Crashes, Collision Severity)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Create Hot Spots (Crashes, Collision Severity)")

# Create a hot spot analysis for the crash collision data (collision severity)

# Create a path for the new crashes hot spots feature class
crashesHotspots = os.path.join(gdbHotspotData, "crashesHotspots")

# Create hot spots points
arcpy.stats.HotSpots(
    Input_Feature_Class=crashes,
    Input_Field="collSeverityNum",
    Output_Feature_Class=crashesHotspots,
    Conceptualization_of_Spatial_Relationships="FIXED_DISTANCE_BAND",
    Distance_Method="EUCLIDEAN_DISTANCE",
    Standardization="ROW",
    Distance_Band_or_Threshold_Distance=None,
    Self_Potential_Field=None,
    Weights_Matrix_File=None,
    Apply_False_Discovery_Rate__FDR__Correction="NO_FDR",
    number_of_neighbors=None,
)

# Add feature class alias for the hot spots (crashes, collision severity) feature class

# Define the crashes hot spots layer alias and modify the feature class alias
crashesHotspotsAlias = "OCSWITRS Crashes Hot Spots"
arcpy.AlterAliasName(crashesHotspots, crashesHotspotsAlias)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (crashes, collision severity) feature class
crashesHotspotsFields = [
    f.name for f in arcpy.ListFields(crashesHotspots)
]  # crashesHotspots field list

# Field Aliases for the crashes hot spots feature class
for f in arcpy.ListFields(crashesHotspots):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Optimized Hot Spots (Crashes, Collision Severity, 1,000m)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Optimized Hot Spots (Crashes, Collision Severity, 1,000m)")

# Optimized hot spot analysis for the crash collision data (collision severity)

# Create a path for the new optimized crashes hot spots feature class
crashesOptimizedHotspots = os.path.join(gdbHotspotData, "crashesOptimizedHotspots")

# Perform Optimized Hot Spot Analysis on the crashes data
arcpy.stats.OptimizedHotSpotAnalysis(
    Input_Features=crashes,
    Output_Features=crashesOptimizedHotspots,
    Analysis_Field="collSeverityNum",
    Incident_Data_Aggregation_Method="COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS",
    Bounding_Polygons_Defining_Where_Incidents_Are_Possible=None,
    Polygons_For_Aggregating_Incidents_Into_Counts=None,
    Density_Surface=None,
    Cell_Size=None,
    Distance_Band="1000 Meters",
)

# Add feature class alias for the optimized hot spots (crashes, collision severity, 1,000 m) feature class

# Define the optimized crashes hot spots layer alias and modify the feature class alias
crashesOptimizedHotspotsAlias = "OCSWITRS Crashes Optimized Hot Spots"
arcpy.AlterAliasName(crashesOptimizedHotspots, crashesOptimizedHotspotsAlias)
print(arcpy.GetMessages())

# Obtain the fields for the optimized hot spots (crashes, collision severity, 1,000 m) feature class
crashesOptimizedHotspotsFields = [
    f.name for f in arcpy.ListFields(crashesOptimizedHotspots)
]  # crashesOptimizedHotspots field list

# Field Aliases for the optimized crashes hot spots feature class
for f in arcpy.ListFields(crashesOptimizedHotspots):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Find Hot Spots (Crashes, 100m bins, 1km neighbors)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Find Hot Spots (Crashes, 100m bins, 1km neighbors)")


# Find hot spots for the crash collision data using 100 m bins and 1 km neighborhood radius (328 ft/ 0.621 mi)

# Create a path for the new crashes find hot spots feature class
crashesFindHotspots100m1km = os.path.join(gdbHotspotData, "crashesFindHotspots100m1km")

# Find the hot spots within the crashes data
arcpy.gapro.FindHotSpots(
    point_layer=crashes,
    out_feature_class=crashesFindHotspots100m1km,
    bin_size="100 Meters",
    neighborhood_size="1 Kilometers",
    time_step_interval=None,
    time_step_alignment="START_TIME",
    time_step_reference=None,
)

# Add feature class alias for the hot spots (crashes, 100m bins, 1km neighbors) feature class

# Define the crashes find hot spots layer alias and modify the feature class alias
crashesFindHotspots100m1kmAlias = "OCSWITRS Crashes Find Hot Spots 100m 1km"
arcpy.AlterAliasName(crashesFindHotspots100m1km, crashesFindHotspots100m1kmAlias)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (crashes, 100m bins, 1km neighbors) feature class
crashesFindHotspots100m1kmFields = [
    f.name for f in arcpy.ListFields(crashesFindHotspots100m1km)
]  # crashesFindHotspots100m1km field list

# Field Aliases for the crashes find hot spots feature class
for f in arcpy.ListFields(crashesFindHotspots100m1km):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Find Hot Spots (Crashes, 150m bins, 2km neighbors)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Find Hot Spots (Crashes, 150m bins, 2km neighbors)")

# Find hot spots for the crash collision data using 150 m bins and 2 km neighborhood radius (492 ft/ 1.24 mi)

# Create a path for the new crashes find hot spots feature class
crashesFindHotspots150m2km = os.path.join(gdbHotspotData, "crashesFindHotspots150m2km")

# Find the hot spots within the crashes data
arcpy.gapro.FindHotSpots(
    point_layer=crashes,
    out_feature_class=crashesFindHotspots150m2km,
    bin_size="150 Meters",
    neighborhood_size="2 Kilometers",
    time_step_interval=None,
    time_step_alignment="START_TIME",
    time_step_reference=None,
)

# Add feature class alias for the hot spots (crashes, 150m bins, 2km neighbors) feature class

# Define the crashes find hot spots layer alias and modify the feature class alias
crashesFindHotspots150m2kmAlias = "OCSWITRS Crashes Find Hot Spots 150m 2km"
arcpy.AlterAliasName(crashesFindHotspots150m2km, crashesFindHotspots150m2kmAlias)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (crashes, 150m bins, 2km neighbors) feature class
crashesFindHotspots150m2kmFields = [
    f.name for f in arcpy.ListFields(crashesFindHotspots150m2km)
]  # crashesFindHotspots150m2km field list

# Field Aliases for the crashes find hot spots feature class
for f in arcpy.ListFields(crashesFindHotspots150m2km):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Find Hot Spots (Crashes, 100m bins, 5km neighbors)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Find Hot Spots (Crashes, 100m bins, 5km neighbors)")

# Find hot spots for the crash collision data using 100 m bins and 5 km neighborhood radius (328 ft/ 3.11 mi)

# Create a path for the new crashes find hot spots feature class
crashesFindHotspots100m5km = os.path.join(gdbHotspotData, "crashesFindHotspots100m5km")

# Find the hot spots within the crashes data
arcpy.gapro.FindHotSpots(
    point_layer=crashes,
    out_feature_class=crashesFindHotspots100m5km,
    bin_size="100 Meters",
    neighborhood_size="5 Kilometers",
    time_step_interval=None,
    time_step_alignment="START_TIME",
    time_step_reference=None,
)

# Add feature class alias for the hot spots (crashes, 100m bins, 5km neighbors) feature class

# Define the crashes find hot spots layer alias and modify the feature class alias
crashesFindHotspots100m5kmAlias = "OCSWITRS Crashes Find Hot Spots 100m 5km"
arcpy.AlterAliasName(crashesFindHotspots100m5km, crashesFindHotspots100m5kmAlias)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (crashes, 100m bins, 5km neighbors) feature class
crashesFindHotspots100m5kmFields = [
    f.name for f in arcpy.ListFields(crashesFindHotspots100m5km)
]  # crashesFindHotspots100m5km field list

# Field Aliases for the crashes find hot spots feature class
for f in arcpy.ListFields(crashesFindHotspots100m5km):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Hot Spots (Proximity to Major Roads, 500ft)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Hot Spots (Proximity to Major Roads, 500ft)")

# Hot spot points within 500 feet of major roads

# Create a path for the new hot spots within 500 mt from major roads feature class
crashesHotspots500ftFromMajorRoads = os.path.join(
    gdbHotspotData, "crashesHotspots500ftFromMajorRoads"
)

arcpy.stats.HotSpots(
    Input_Feature_Class=crashes500ftFromMajorRoads,
    Input_Field="collSeverityNum",
    Output_Feature_Class=crashesHotspots500ftFromMajorRoads,
    Conceptualization_of_Spatial_Relationships="FIXED_DISTANCE_BAND",
    Distance_Method="EUCLIDEAN_DISTANCE",
    Standardization="ROW",
    Distance_Band_or_Threshold_Distance=None,
    Self_Potential_Field=None,
    Weights_Matrix_File=None,
    Apply_False_Discovery_Rate__FDR__Correction="NO_FDR",
    number_of_neighbors=None,
)

# Add feature class alias for the hot spots (proximity to major roads, 500ft) feature class

# Define the crashes hot spots 500 feet from major roads layer alias and modify the feature class alias
crashesHotspots500ftFromMajorRoadsAlias = (
    "OCSWITRS Crashes Hot Spots 500 Feet from Major Roads"
)
arcpy.AlterAliasName(
    crashesHotspots500ftFromMajorRoads, crashesHotspots500ftFromMajorRoadsAlias
)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (proximity to major roads, 500ft) feature class
crashesHotspots500ftFromMajorRoadsFields = [
    f.name for f in arcpy.ListFields(crashesHotspots500ftFromMajorRoads)
]  # crashesHotspots500ftFromMajorRoads field list

# Field Aliases for the crashes hot spots 500 feet from major roads feature class
for f in arcpy.ListFields(crashesHotspots500ftFromMajorRoads):
    print(f"{f.name} ({f.aliasName})")

# endregion


# region Find Hot Spots (Proximity to Major Roads, 500ft)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Find Hot Spots (Proximity to Major Roads, 500ft)")

# Find hot spots within 500 feet from major roads

# Create a path for the new hot spots within 500 ft from major roads feature class
crashesFindHotspots500ftMajorRoads500ft1mi = os.path.join(
    gdbHotspotData, "crashesFindHotspots500ftMajorRoads500ft1mi"
)

arcpy.gapro.FindHotSpots(
    point_layer=crashes500ftFromMajorRoads,
    out_feature_class=crashesFindHotspots500ftMajorRoads500ft1mi,
    bin_size="500 Feet",
    neighborhood_size="1 Miles",
    time_step_interval=None,
    time_step_alignment="START_TIME",
    time_step_reference=None,
)

# Add feature class alias for the hot spots (proximity to major roads, 500ft) feature class

# Define the crashes find hot spots 500 feet from major roads layer alias and modify the feature class alias
crashesFindHotspots500ftMajorRoads500ft1miAlias = (
    "OCSWITRS Crashes Find Hot Spots 500 Feet from Major Roads 500ft 1mi"
)
arcpy.AlterAliasName(
    crashesFindHotspots500ftMajorRoads500ft1mi,
    crashesFindHotspots500ftMajorRoads500ft1miAlias,
)
print(arcpy.GetMessages())

# Obtain the fields for the hot spots (proximity to major roads, 500ft) feature class
crashesFindHotspots500ftMajorRoads500ft1miFields = [
    f.name for f in arcpy.ListFields(crashesFindHotspots500ftMajorRoads500ft1mi)
]  # crashesFindHotspots500ftMajorRoads500ft1mi field list

# Field Aliases for the crashes find hot spots 500 feet from major roads feature class
for f in arcpy.ListFields(crashesFindHotspots500ftMajorRoads500ft1mi):
    print(f"{f.name} ({f.aliasName})")

# endregion
# endregion 2.5
# endregion 2
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3. Geodatabase, Feature Dataset and Feature Class Metadata Processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3. Geodatabase, Feature Dataset and Feature Class Metadata Processing")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.1. Project Geodatabase Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.1. Project Geodatabase Metadata")

# Create a metadata object for the project geodatabase

# Define key metadata attributes for the AGPSWITRS geodatabase
mdoGdb = md.Metadata()
mdoGdb.title = "AGPSWITRS Historical Traffic Collisions"
mdoGdb.tags = "Orange County, California, OCSWITRS, Traffic, Traffic Conditions, Crashes, Collisions, Parties, Victims, Injuries, Fatalities, Hot Spots, Road Safety, Accidents, SWITRS, Transportation"
mdoGdb.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoGdb.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoGdb.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoGdb.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoGdb.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the geodatabase metadata object to the project geodatabase

# Apply the metadata object to the project geodatabase
mdGdb = md.Metadata(gdbPath)
if not mdGdb.isReadOnly:
    mdGdb.copy(mdoGdb)
    mdGdb.save()
    print(f"Metadata updated for {gdbName} geodatabase.")

# endregion 3.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.2. Feature Dataset Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.2. Analysis Data Feature Dataset Metadata")


# region Analysis Feature Dataset Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Analysis Feature Dataset Metadata")

# Create a new metadata object for the analysis feature dataset
mdoAnalysis = md.Metadata()
mdoAnalysis.title = "OCSWITRS Traffic Collisions Analysis Dataset"
mdoAnalysis.tags = "Orange County, California, OCSWITRS, Traffic, Traffic Conditions, Crashes, Collisions, Parties, Victims, Injuries, Fatalities, Hot Spots, Road Safety, Accidents, SWITRS, Transportation"
mdoAnalysis.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoAnalysis.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoAnalysis.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoAnalysis.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoAnalysis.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the metadata object to the analysis feature dataset

# Apply the metadata object to the analysis feature dataset
mdAnalysis = md.Metadata(gdbAnalysisData)
if not mdAnalysis.isReadOnly:
    mdAnalysis.copy(mdoAnalysis)
    mdAnalysis.save()
    print(f"Metadata updated for the analysis feature dataset.")

# endregion


# region HotSpots Feature Dataset Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- HotSpots Feature Dataset Metadata")

# Create a new metadata object for the hotspots feature dataset
mdoHotspots = md.Metadata()
mdoHotspots.title = "OCSWITRS Traffic Collisions Hotspots Dataset"
mdoHotspots.tags = "Orange County, California, OCSWITRS, Traffic, Traffic Conditions, Crashes, Collisions, Parties, Victims, Injuries, Fatalities, Hot Spots, Road Safety, Accidents, SWITRS, Transportation"
mdoHotspots.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoHotspots.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoHotspots.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoHotspots.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoHotspots.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the metadata object to the hotspots feature dataset

# Apply the metadata object to the hotspots feature dataset
mdHotspots = md.Metadata(gdbHotspotData)
if not mdHotspots.isReadOnly:
    mdHotspots.copy(mdoHotspots)
    mdHotspots.save()
    print(f"Metadata updated for the hotspots feature dataset.")

# endregion


# region Raw Feature Dataset Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Raw Feature Dataset Metadata")

# Create a new metadata object for the raw feature dataset
mdoRaw = md.Metadata()
mdoRaw.title = "OCSWITRS Traffic Collisions Raw Data Dataset"
mdoRaw.tags = "Orange County, California, OCSWITRS, Traffic, Traffic Conditions, Crashes, Collisions, Parties, Victims, Injuries, Fatalities, Hot Spots, Road Safety, Accidents, SWITRS, Transportation"
mdoRaw.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoRaw.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoRaw.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoRaw.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoRaw.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the metadata object to the raw feature dataset

# Apply the metadata object to the raw data feature dataset
mdRaw = md.Metadata(gdbRawData)
if not mdRaw.isReadOnly:
    mdRaw.copy(mdoRaw)
    mdRaw.save()
    print(f"Metadata updated for the raw data feature dataset.")

# endregion


# region Supporting Feature Dataset Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Supporting Feature Dataset Metadata")

# Create a new metadata object for the supporting feature dataset
mdoSupporting = md.Metadata()
mdoSupporting.title = "OCSWITRS Traffic Collisions Supporting Data Dataset"
mdoSupporting.tags = "Orange County, California, OCSWITRS, Traffic, Traffic Conditions, Crashes, Collisions, Parties, Victims, Injuries, Fatalities, Hot Spots, Road Safety, Accidents, SWITRS, Transportation"
mdoSupporting.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoSupporting.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoSupporting.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoSupporting.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoSupporting.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the metadata object to the supporting feature dataset

# Apply the metadata object to the supporting data feature dataset
mdSupporting = md.Metadata(gdbSupportingData)
if not mdSupporting.isReadOnly:
    mdSupporting.copy(mdoSupporting)
    mdSupporting.save()
    print(f"Metadata updated for the supporting data feature dataset.")

# endregion
# endregion 3.2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.3. Feature Class Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.3. Feature Class Metadata")


# region Collisions Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Collisions Metadata")

# Create a new metadata object for the collisions feature class

# Define key metadata attributes for the Collisions feature class
mdoCollisions = md.Metadata()
mdoCollisions.title = "OCSWITRS Combined Collisions Points"
mdoCollisions.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoCollisions.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdYears})"
mdoCollisions.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoCollisions.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCollisions.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCollisions.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the collisions metadata object to the collisions feature class

# Apply the metadata object to the collisions feature class
mdCollisions = md.Metadata(collisions)
if not mdCollisions.isReadOnly:
    mdCollisions.copy(mdoCollisions)
    mdCollisions.save()
    print(f"Metadata updated for {collisionsAlias} feature class.")

# endregion


# region Crashes Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Crashes Metadata")

# Create a new metadata object for the crashes feature class

# Define key metadata attributes for the Crashes feature class
mdoCrashes = md.Metadata()
mdoCrashes.title = "OCSWITRS Crashes Points"
mdoCrashes.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoCrashes.summary = f"Statewide Integrated Traffic Records System (SWITRS) Crash Data for Orange County, California ({mdYears})"
mdoCrashes.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on crashes</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoCrashes.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCrashes.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCrashes.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Assign the crashes metadata object to the crashes feature class

# Apply the metadata object to the crashes feature class
mdCrashes = md.Metadata(crashes)
if not mdCrashes.isReadOnly:
    mdCrashes.copy(mdoCrashes)
    mdCrashes.save()
    print(f"Metadata updated for {crashesAlias} feature class.")

# endregion


# region Parties Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Parties Metadata")

# Create a new metadata object for the parties feature class

# Define key metadata attributes for the Parties feature class
mdoParties = md.Metadata()
mdoParties.title = "OCSWITRS Parties Points"
mdoParties.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Parties, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoParties.summary = f"Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Parties Data for Orange County, California ({mdYears})"
mdoParties.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on parties involved in crash incidents</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoParties.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoParties.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoParties.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/1e07bb1002f9457fa6fd3540fdb08e29/data"

# Assign the parties metadata object to the parties feature class

# Apply the metadata object to the parties feature class
mdParties = md.Metadata(parties)
if not mdParties.isReadOnly:
    mdParties.copy(mdoParties)
    mdParties.save()
    print(f"Metadata updated for {partiesAlias} feature class.")

# endregion


# region Victims Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Victims Metadata")

# Create a new metadata object for the victims feature class

# Define key metadata attributes for the Victims feature class
mdoVictims = md.Metadata()
mdoVictims.title = "OCSWITRS Victims Points"
mdoVictims.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Victims, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoVictims.summary = f"Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Victims Data for Orange County, California ({mdYears})"
mdoVictims.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on victims/persons involved in crash incidents</span><span> in Orange County, California for {mdYears} ({mdDates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{dateUpdated}</b></span></p></div></div></div>"""
mdoVictims.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoVictims.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoVictims.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/78682395df4744009c58625f1db0c25b/data"

# Assign the victims metadata object to the victims feature class

# Apply the metadata object to the victims feature class
mdVictims = md.Metadata(victims)
if not mdVictims.isReadOnly:
    mdVictims.copy(mdoVictims)
    mdVictims.save()
    print(f"Metadata updated for {victimsAlias} feature class.")

# endregion
# endregion 3.3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.4. Supporting Features Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.10. Roads Metadata")


# region Roads Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Roads Metadata")

# Create a new metadata object for the roads feature class

# Define key metadata attributes for the Roads feature class
mdoRoads = md.Metadata()
mdoRoads.title = "OCSWITRS Roads Network"
mdoRoads.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoRoads.summary = "All roads for Orange County, California (Primary roads and highways, secondary roads, and local roads)"
mdoRoads.description = """<div style="text-align:Left;"><div><div><p><span>The Orange County Roads Network is a comprehensive representation of all roads in the area, including primary roads and highways, secondary roads, and local roads. The data are sourced from the Orange County Department of Public Works and are updated regularly to reflect the most current road network configuration.</span></p></div></div></div>"""
mdoRoads.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoRoads.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoRoads.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"

# Assign the roads metadata object to the roads feature class

# Apply the metadata object to the roads feature class
mdRoads = md.Metadata(roads)
if not mdRoads.isReadOnly:
    mdRoads.copy(mdoRoads)
    mdRoads.save()
    print(f"Metadata updated for {roadsAlias} feature class.")

# endregion


# region Census Blocks Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Census Blocks Metadata")

# Create a new metadata object for the census blocks feature class

# Define key metadata attributes for the US Census 2020 Blocks feature class
mdoBlocks = md.Metadata()
mdoBlocks.title = "OCSWITRS US Census 2020 Blocks"
mdoBlocks.tags = "Orange County, California, US Census 2020, Blocks, Census, Demographics, Population"
mdoBlocks.summary = "US Census 2020 Blocks for Orange County, California"
mdoBlocks.description = """<div style="text-align:Left;"><div><div><p><span>The US Census 2020 Blocks feature class provides a comprehensive representation of the 2020 Census Blocks for Orange County, California. The data are sourced from the US Census Bureau and are updated regularly to reflect the most current demographic and population data.</span></p></div></div></div>"""
mdoBlocks.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoBlocks.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoBlocks.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/e2c4cd39783a4d1bb0925ead15a23cdc/data"

# Assign the census blocks metadata object to the census blocks feature class

# Apply the metadata object to the US Census 2020 Blocks feature class
mdBlocks = md.Metadata(blocks)
if not mdBlocks.isReadOnly:
    mdBlocks.copy(mdoBlocks)
    mdBlocks.save()
    print(f"Metadata updated for {blocksAlias} feature class.")

# endregion


# region Cities Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Cities Metadata")

# Create a new metadata object for the cities feature class

# Define key metadata attributes for the Cities feature class
mdoCities = md.Metadata()
mdoCities.title = "OCSWITRS Cities Boundaries"
mdoCities.tags = "Orange County, California, Cities, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoCities.summary = "Orange County City and Unincorporated Areas Land Boundaries, enriched with geodemographic characteristics"
mdoCities.description = """<div style="text-align:Left;"><div><div><p><span>The Orange County City and Unincorporated Areas Land Boundaries are enriched with a comprehensive set of geodemographic characteristics from OC ACS 2021 data. These characteristics span across demographic, housing, economic, and social aspects, providing a holistic view of the area. </span></p><p><span>The geodemographic data originate from the US Census American Community Survey (ACS) 2021, a 5-year estimate of the key Characteristics of Cities' geographic level in Orange County, California. The data contains:</span></p><ul><li><span>Total population and housing counts for each area;</span></li><li><span>Population and housing density measurements (per square mile);</span></li><li><span>Race counts for Asian, Black or African American, Hispanic and White groups;</span></li><li><span>Aggregate values for the number of vehicles commuting and travel time to work;</span></li></ul></div></div></div>"""
mdoCities.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCities.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCities.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/ffe4a73307a245eda7dc7eaffe1db6d2/data"

# Assign the cities metadata object to the cities feature class

# Apply the metadata object to the Cities feature class
mdCities = md.Metadata(cities)
if not mdCities.isReadOnly:
    mdCities.copy(mdoCities)
    mdCities.save()
    print(f"Metadata updated for {citiesAlias} feature class.")

# endregion


# region Boundaries Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("- Boundaries Metadata")

# Create a new metadata object for the boundaries feature class

# Define key metadata attributes for the Boundaries feature class
mdoBoundaries = md.Metadata()
mdoBoundaries.title = "OC Land Boundaries"
mdoBoundaries.tags = "Orange County, California, Boundaries, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoBoundaries.summary = (
    "Land boundaries for Orange County, cities, and unincorporated areas"
)
mdoBoundaries.description = """<div style="text-align:Left;"><div><div><p><span>Land boundaries for Orange County, cities, and unincorporated areas (based on the five supervisorial districts). Contains additional geodemographic data on population and housing from the US Census 2021 American Community Survey (ACS).</span></p></div></div></div>"""
mdoBoundaries.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoBoundaries.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoBoundaries.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/4041c4b1f4234218a4ce654e5d22f176/data"

# Assign the boundaries metadata object to the boundaries feature class

# Apply the metadata object to the Boundaries feature class
mdBoundaries = md.Metadata(boundaries)
if not mdBoundaries.isReadOnly:
    mdBoundaries.copy(mdoBoundaries)
    mdBoundaries.save()
    print(f"Metadata updated for {boundariesAlias} feature class.")

# endregion
# endregion 3.4


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region 3.5. Save Project
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\n3.5. Save Project")
# Save the project
aprx.save()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# region End of Script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("\nEnd of Script")
