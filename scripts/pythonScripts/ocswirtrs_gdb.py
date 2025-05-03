#############################################
#   SWITRS R DATA PROCESSING PROJECT        #
#   ArcGIS and Spatial Geoprocessing        #
#   version 1.0, January 2025               #
#############################################


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Instantiating python libraries for the project

# Import Python libraries
import os
import json
import pytz
import math
import arcpy
import arcgis
from datetime import date, time, datetime, timedelta, tzinfo, timezone
from tqdm.notebook import trange, tqdm, tqdm_notebook
import pandas as pd
import numpy as np
from arcpy import metadata as md

# important as it "enhances" Pandas by importing these classes (from ArcGIS API for Python)
from arcgis.features import GeoAccessor, GeoSeriesAccessor


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Project and Workspace Variables
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define and maintain project, workspace, ArcGIS, and data-related variables

# 2.1. Project and ArcGIS Pro project paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Environment variables for OneDrive path
oneDrivePath = os.getenv("OneDriveCommercial")

# OC Switrs project path
projectPath = os.path.join(oneDrivePath, "Documents", "OCSWITRS")

# OC Switrs ArcGIS Pro project path
agpPath = os.path.join(projectPath, "OCSWITRSAGP")


# 2.2. ArcGIS Pro related paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ArcGIS Pro project name and path
aprx = "OCSWITRSAGP.aprx"
aprxPath = os.path.join(agpPath, aprx)

# ArcGIS Pro project geodatabase and path
gdb = "OCSWITRSAGP.gdb"
gdbPath = os.path.join(agpPath, gdb)

# Current ArcGIS workspace (arcpy)
arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace

# Enable overwriting existing outputs
arcpy.env.overwriteOutput = True


# 2.3. Project folder paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~

# Raw data folder path
rawDataPath = os.path.join(projectPath, "Data", "Raw")

# Layers folder path
layersPath = os.path.join(projectPath, "Layers")

# Notebooks folder path
notebooksPath = os.path.join(projectPath, "Notebooks")

# Supporting data path on the project geodatabase (feature directory)
gdbSupportingDataPath = os.path.join(workspace, "SupportingData")

# Raw data path on the project geodatabase (feature directory)
gdbRawDataPath = os.path.join(workspace, "RawData")

# Codebook Json folder path
codebookPath = os.path.join(projectPath, "Data", "codebook", "cb.json")


# 2.4. Data folder paths and contents
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The most current raw data files cover the periods from 01/01/2013 to 09/30/2024. The data files are already processed in the R scripts and imported into the project's geodatabase.

# add the date 01/01/2013 to a new python datetime object named 'rawDateStart'
rawDateStart = datetime(2013, 1, 1)

# add the date 06/30/2024 to a new python datetime object named 'rawDateEnd'
rawDateEnd = datetime(2024, 9, 30)

# Define time and date variables
timeZone = pytz.timezone("US/Pacific")
today = datetime.now(timeZone)
lastUpdateDate = today.strftime("%B %d, %Y")
lastUpdateDatetime = today.strftime("%A %B %d, %Y, %I:%M %p (%Z)")


# 2.5. Geodatabase feature class paths
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Paths to raw data feature classes
crashesPath = os.path.join(gdbRawDataPath, "crashes")
partiesPath = os.path.join(gdbRawDataPath, "parties")
victimsPath = os.path.join(gdbRawDataPath, "victims")
collisionsPath = os.path.join(gdbRawDataPath, "collisions")

# Paths to supporting data feature classes
boundariesPath = os.path.join(gdbSupportingDataPath, "boundaries")
citiesPath = os.path.join(gdbSupportingDataPath, "cities")
roadsPath = os.path.join(gdbSupportingDataPath, "roads")


# Display all information
print("Key Project Information")
print(f"\n\t- Name {aprx}\n\t- Path: {aprxPath}\n\t- Project Path: {projectPath}\n\t- Workspace: {workspace}\n\t- Geodatabase: {gdb}\n\t- Geodatabase Path: {gdbPath}")
print("\nProject Directories:")
print(f"\n\t- Raw Data: {rawDataPath}\n\t- Layers: {layersPath}\n\t- Notebooks: {notebooksPath}")
print("\nRaw Feature Classes:")
print(f"\n\t- Crashes: {crashesPath}\n\t- Parties: {partiesPath}\n\t- Victims: {victimsPath}\n\t- Collisions: {collisionsPath}")
print("\nSupporting Feature Classes:")
print(f"\n\t- Boundaries: {boundariesPath}\n\t- Cities: {citiesPath}\n\t- Roads: {roadsPath}")
print("\nOther Supporting Data")
print(f"\n\t- Codebook: {codebookPath}")

# Current ArcGIS pro project
aprx = arcpy.mp.ArcGISProject(aprxPath)

# Current ArcGIS pro project map
map = aprx.listMaps()[0]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Functions and Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The definitions include: Dictionary Definitions (JSON)

# Load the JSON file from directory and store it in a variable
with open(codebookPath) as json_file:
    codebook = json.load(json_file)

arcpy.env.workspace = gdbRawDataPath
workspace = arcpy.env.workspace
arcpy.ListFeatureClasses()

arcpy.env.workspace = gdbPath
workspace = arcpy.env.workspace


# Get all the feature classes by name
crashesFc = os.path.join(gdbRawDataPath, arcpy.ListFeatureClasses("crashes", feature_dataset="RawData")[0])
victimsFc = os.path.join(gdbRawDataPath, arcpy.ListFeatureClasses("victims", feature_dataset="RawData")[0])
partiesFc = os.path.join(gdbRawDataPath, arcpy.ListFeatureClasses("parties", feature_dataset="RawData")[0])
collisionsFc = os.path.join(gdbRawDataPath, arcpy.ListFeatureClasses("collisions", feature_dataset="RawData")[0])
citiesFc = os.path.join(gdbSupportingDataPath, arcpy.ListFeatureClasses("cities", feature_dataset="SupportingData")[0])
boundariesFc = os.path.join(gdbSupportingDataPath, arcpy.ListFeatureClasses("boundaries", feature_dataset="SupportingData")[0])
roadsFc = os.path.join(gdbSupportingDataPath, arcpy.ListFeatureClasses("roads", feature_dataset="SupportingData")[0])

# Obtain the list fields of the geodatabase data

# Field lists for each of the geodatabase raw data feature classes
fieldsCrashes = arcpy.ListFields(crashesPath)
fieldsParties = arcpy.ListFields(partiesPath)
fieldsVictims = arcpy.ListFields(victimsPath)
fieldsCollisions = arcpy.ListFields(collisionsPath)

# Field lists for each of the geodatabase supporting data feature classes
fieldsBoundaries = arcpy.ListFields(boundariesPath)
fieldsCities = arcpy.ListFields(citiesPath)
fieldsRoads = arcpy.ListFields(roadsPath)

# Count rows in each of the geodatabase feature classes

# Get the count for each of the feature classes
countCrashes = int(arcpy.management.GetCount(crashesFc)[0])
countVictims = int(arcpy.management.GetCount(victimsFc)[0])
countParties = int(arcpy.management.GetCount(partiesFc)[0])
countCollisions = int(arcpy.management.GetCount(collisionsFc)[0])
countCities = int(arcpy.management.GetCount(citiesFc)[0])
countBoundaries = int(arcpy.management.GetCount(boundariesFc)[0])
countRoads = int(arcpy.management.GetCount(roadsFc)[0])

print(f"Counts:\n- Crashes: {countCrashes:,}\n- Parties: {countParties:,}\n- Victims: {countVictims:,}\n- Collisions: {countCollisions:,}\n- Cities: {countCities:,}\n- Boundaries: {countBoundaries:,}\n- Roads: {countRoads:,}")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. Codebook for Field Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 4.1. Assigning field aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Creating and assigning field aliases for the geodatabase feature classes using the JSON codebook dictionary

# 4.1.1. Crashes Feature Class

# Field aliases for the crashes geodatabase feature class
for field in fieldsCrashes:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = crashesFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


# 4.1.2. Parties Feature Class

# Field aliases for the parties geodatabase feature class
for field in fieldsParties:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = partiesFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


# 4.1.3. Victims Feature Class

# Field aliases for the victims geodatabase feature class
for field in fieldsVictims:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = victimsFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


# 4.1.4. Collisions Feature Class

# Field aliases for the collisions geodatabase feature class
for field in fieldsCollisions:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = collisionsFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


# 4.1.5. Cities Feature Class

# Field aliases for the cities geodatabase feature class
for field in fieldsCities:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = citiesFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


# 4.1.6. Roads Feature Class

# Field aliases for the roads geodatabase feature class
for field in fieldsRoads:
    if field.name in list(codebook.keys()):
        print(f"\tMatch {codebook[field.name]['var_order']}: {field.name} ({codebook[field.name]['label']}): {codebook[field.name]['description']}")
        arcpy.management.AlterField(
            in_table = roadsFc,
            field = field.name,
            new_field_alias = codebook[field.name]['label']
        )
print(arcpy.GetMessages())


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 5. Geodatabase Metadata Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 5.1. Feature Class Aliases
#~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define aliases for each of the feature classes
aliasCrashes = "OCSWITRS Crashes"
aliasParties = "OCSWITRS Parties"
aliasVictims = "OCSWITRS Victims"
aliasCollisions = "OCSWITRS Collisions"
aliasCities = "OCSWITRS Cities"
aliasRoads = "OCSWITRS Roads"
aliasBoundaries = "OCSWITRS Boundaries"

# Assign alias operations to each of the feature classes
arcpy.AlterAliasName(crashesPath, aliasCrashes)
arcpy.AlterAliasName(partiesPath, aliasParties)
arcpy.AlterAliasName(victimsPath, aliasVictims)
arcpy.AlterAliasName(collisionsPath, aliasCollisions)
arcpy.AlterAliasName(citiesPath, aliasCities)
arcpy.AlterAliasName(roadsPath, aliasRoads)
arcpy.AlterAliasName(boundariesPath, aliasBoundaries)

# Save the project
aprx.save()



# 5.2. Crashes Metadata
#~~~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Crashes feature class
mdoCrashes = md.Metadata()
mdoCrashes.title = "OCSWITRS Crashes Points"
mdoCrashes.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoCrashes.summary = "Statewide Integrated Traffic Records System (SWITRS) Crash Data for Orange County, California (2013-2024)"
mdoCrashes.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on crashes</span><span> in Orange County, California for 2013-2024 (December 31, 2012 to June 30, 2024). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{
    lastUpdateDate}</b></span></p></div></div></div>"""
mdoCrashes.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCrashes.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCrashes.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"

# Apply the metadata object to the crashes feature class
mdCrashes = md.Metadata(crashesFc)
if not mdCrashes.isReadOnly:
    mdCrashes.copy(mdoCrashes)
    mdCrashes.save()


# 5.3. Parties Metadata
#~~~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Parties feature class
mdoParties = md.Metadata()
mdoParties.title = "OCSWITRS Parties Points"
mdoParties.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Parties, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoParties.summary = "Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Parties Data for Orange County, California (2013-2024)"
mdoParties.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on parties involved in crash incidents</span><span> in Orange County, California for 2013-2024 (December 31, 2012 to June 30, 2024). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{
    lastUpdateDate}</b></span></p></div></div></div>"""
mdoParties.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoParties.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoParties.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/1e07bb1002f9457fa6fd3540fdb08e29/data"


# Apply the metadata object to the parties feature class
mdParties = md.Metadata(partiesFc)
if not mdParties.isReadOnly:
    mdParties.copy(mdoParties)
    mdParties.save()


# 5.4. Victims Metadata
#~~~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Victims feature class
mdoVictims = md.Metadata()
mdoVictims.title = "OCSWITRS Victims Points"
mdoVictims.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Victims, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoVictims.summary = "Statewide Integrated Traffic Records System (SWITRS) Incident-Involved Victims Data for Orange County, California (2013-2024)"
mdoVictims.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">reports on victims/persons involved in crash incidents</span><span> in Orange County, California for 2013-2024 (December 31, 2012 to June 30, 2024). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{
    lastUpdateDate}</b></span></p></div></div></div>"""
mdoVictims.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoVictims.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoVictims.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/78682395df4744009c58625f1db0c25b/data"


# Apply the metadata object to the victims feature class
mdVictims = md.Metadata(victimsFc)
if not mdVictims.isReadOnly:
    mdVictims.copy(mdoVictims)
    mdVictims.save()


# 5.5. Collisions Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~

mdyears = f"{rawDateStart.strftime('%Y')}-{rawDateEnd.strftime('%Y')}"

# write string rawDateStart in format mont, date, year
mddates = f"{rawDateStart.strftime('%B %d, %Y')} to {rawDateEnd.strftime('%B %d, %Y')}"

# Define key metadata attributes for the Collisions feature class
mdoCollisions = md.Metadata()
mdoCollisions.title = "OCSWITRS Combined Collisions Points"
mdoCollisions.tags = "Orange County, California, Traffic, Traffic Conditions, Crashes, Collisions, Road Safety, Accidents, SWITRS, OCSWITRS, Transportation"
mdoCollisions.summary = f"Statewide Integrated Traffic Records System (SWITRS) Combined Collisions Data for Orange County, California ({mdyears})"
mdoCollisions.description = f"""<div style="text-align:Left;"><div><div><p><span style="font-weight:bold;">Statewide Integrated Traffic Records System (SWITRS)</span><span> location point data, containing </span><span style="font-weight:bold;">combined reports on collision crashes, parties, and victims</span><span> in Orange County, California for {mdyears} ({mddates}). The data are collected and maintained by the </span><a href="https://www.chp.ca.gov:443/" style="text-decoration:underline;"><span>California Highway Patrol (CHP)</span></a><span>, from incidents reported by local and government agencies. Original tabular datasets are provided by the </span><a href="https://tims.berkeley.edu:443/" style="text-decoration:underline;"><span>Transportation Injury Mapping System (TIMS)</span></a><span>. Only records with reported locational GPS attributes in Orange County are included in the spatial database (either from X and Y geocoded coordinates, or the longitude and latitude coordinates generated by the CHP officer on site). Incidents without valid coordinates are omitted from this spatial dataset representation. Last Updated on <b>{lastUpdateDate}</b></span></p></div></div></div>"""
mdoCollisions.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCollisions.accessConstraints = """<div style="text-align:Left;"><p><span>The SWITRS data displayed are provided by the California Highway Patrol (CHP) reports through the Transportation Injury Mapping System (TIMS) of the University of California, Berkeley. Issues of report accuracy should be addressed to CHP.</span></p><p>The displayed mapped data can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to TIMS, CHP, and OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCollisions.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/6b96b7d6d5394cbb95aa2fae390503a9/data"


# Apply the metadata object to the collisions feature class
mdCollisions = md.Metadata(collisionsFc)
if not mdCollisions.isReadOnly:
    mdCollisions.copy(mdoCollisions)
    mdCollisions.save()


# 5.6. Cities Metadata
#~~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Cities feature class
mdoCities = md.Metadata()
mdoCities.title = "OCSWITRS Cities Boundaries"
mdoCities.tags = "Orange County, California, Cities, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoCities.summary = "Orange County City and Unincorporated Areas Land Boundaries, enriched with geodemographic characteristics"
mdoCities.description = """<div style="text-align:Left;"><div><div><p><span>The Orange County City and Unincorporated Areas Land Boundaries are enriched with a comprehensive set of geodemographic characteristics from OC ACS 2021 data. These characteristics span across demographic, housing, economic, and social aspects, providing a holistic view of the area. </span></p><p><span>The geodemographic data originate from the US Census American Community Survey (ACS) 2021, a 5-year estimate of the key Characteristics of Cities' geographic level in Orange County, California. The data contains:</span></p><ul><li><p><span>Total population and housing counts for each area;</span></p></li><li><p><span>Population and housing density measurements (per square mile);</span></p></li><li><p><span>Race counts for Asian, Black or African American, Hispanic and White groups;</span></p></li><li><p><span>Aggregate values for the number of vehicles commuting and travel time to work;</span></p></li></ul></div></div></div>"""
mdoCities.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoCities.accessConstraints = """<div style="text-align:Left;"><div><div><p><span>The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoCities.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/ffe4a73307a245eda7dc7eaffe1db6d2/data"


# Apply the metadata object to the cities feature class
mdCities = md.Metadata(citiesFc)
if not mdCities.isReadOnly:
    mdCities.copy(mdoCities)
    mdCities.save()


# 5.7. Roads Metadata
#~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Roads feature class
mdoRoads = md.Metadata()
mdoRoads.title = "OCSWITRS Roads Network"
mdoRoads.tags = "Orange County, California, Roads, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoRoads.summary = "All roads for Orange County, California (Primary roads and highways, secondary roads, and local roads)"
mdoRoads.description = """<div style="text-align:Left;"><div><div><p><span>The Orange County Roads Network is a comprehensive representation of all roads in the area, including primary roads and highways, secondary roads, and local roads. The data are sourced from the Orange County Department of Public Works and are updated regularly to reflect the most current road network configuration.</span></p></div></div></div>"""
mdoRoads.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoRoads.accessConstraints = """<div style="text-align:Left;"><div><div><p><span>The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoRoads.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/76f6fbe9acbb482c9684307854d6352b/data"


# Apply the metadata object to the roads feature class
mdRoads = md.Metadata(roadsFc)
if not mdRoads.isReadOnly:
    mdRoads.copy(mdoRoads)
    mdRoads.save()


# 5.8. Boundaries Metadata
#~~~~~~~~~~~~~~~~~~~~~~~~~

# Define key metadata attributes for the Boundaries feature class
mdoBoundaries = md.Metadata()
mdoBoundaries.title = "OC Land Boundaries"
mdoBoundaries.tags = "Orange County, California, Boundaries, Traffic, Road Safety, Transportation, Collisions, Crashes, SWITRS, OCSWITRS"
mdoBoundaries.summary = "Land boundaries for Orange County, cities, and unincorporated areas"
mdoBoundaries.description = """<div style="text-align:Left;"><div><div><p><span>Land boundaries for Orange County, cities, and unincorporated areas (based on the five supervisorial districts). Contains additional geodemographic data on population and housing from the US Census 2021 American Community Survey (ACS).</span></p></div></div></div>"""
mdoBoundaries.credits = "Dr. Kostas Alexandridis, GISP, Data Scientist, OC Public Works, OC Survey Geospatial Services"
mdoBoundaries.accessConstraints = """<div style="text-align:Left;"><div><div><p><span>The feed data and associated resources (maps, apps, endpoints) can be used under a <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">Creative Commons CC-SA-BY</a> License, providing attribution to OC Public Works, OC Survey Geospatial Services. </p><div>We make every effort to provide the most accurate and up-to-date data and information. Nevertheless, the data feed is provided, 'as is' and OC Public Work's standard <a href="https://www.ocgov.com/contact-county/disclaimer" target="_blank">Disclaimer</a> applies.<br /></div><div><br /></div><div>For any inquiries, suggestions or questions, please contact:</div><div><br /></div><div style="text-align:center;"><a href="https://www.linkedin.com/in/ktalexan/" target="_blank"><b>Dr. Kostas Alexandridis, GISP</b></a><br /></div><div style="text-align:center;">GIS Analyst | Spatial Complex Systems Scientist</div><div style="text-align:center;">OC Public Works/OC Survey Geospatial Applications</div><div style="text-align:center;"><div>601 N. Ross Street, P.O. Box 4048, Santa Ana, CA 92701</div><div>Email: <a href="mailto:kostas.alexandridis@ocpw.ocgov.com" target="_blank">kostas.alexandridis@ocpw.ocgov.com</a> | Phone: (714) 967-0826</div><div><br /></div></div></div>"""
mdoBoundaries.thumbnailUri = "https://ocpw.maps.arcgis.com/sharing/rest/content/items/4041c4b1f4234218a4ce654e5d22f176/data"


# Apply the metadata object to the boundaries feature class
mdBoundaries = md.Metadata(boundariesFc)
if not mdBoundaries.isReadOnly:
    mdBoundaries.copy(mdoBoundaries)
    mdBoundaries.save()


# Save the project
aprx.save()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 6. Map Layer Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 6.1. Visual Layer Operations
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add and rename layers in contents view, using their aliases
for lyr in map.listLayers():
    if "OCSWITRS" in lyr.name:
        map.removeLayer(lyr)
        print(arcpy.GetMessages())

# Add the four feature classes (Crashes Points, Parties Points, Victims Points, Collisions Points) from the geodatabase to the map
crashesLyrName = map.addDataFromPath(crashesFc)
partiesLyrName = map.addDataFromPath(partiesFc)
victimsLyrName = map.addDataFromPath(victimsFc)
collisionsLyrName = map.addDataFromPath(collisionsFc)

# Add the supporting data Cities and Roads layers to the map
citiesLyrName = map.addDataFromPath(citiesFc)
roadsLyrName = map.addDataFromPath(roadsFc)
boundariesLyrName = map.addDataFromPath(boundariesFc)

print(
    f"Added layers to the map:\n\t- {crashesLyrName}\n\t- {partiesLyrName}\n\t- {victimsLyrName}\n\t- {collisionsLyrName}\n\t- {citiesLyrName}\n\t- {roadsLyrName}\n\t- {boundariesLyrName}")

# Save the project
aprx.save()

# Define layers in the current map

# Store the current list of layers to a new variable
mapLyrs = map.listLayers()
# Store the names of the layers in a list
mapLyrsList = [mlyr.name for mlyr in mapLyrs]

print("Active Map Layers:")
# Loop through the list of layers in the map, and print their names
for mlyr in mapLyrs:
    print(f" - {mlyr.name}")

# Define individual layers for each of the SWITRS feature classes

# Identify each of the Crashes, Parties, Victim and Collisions layers
crashesLyr = next(
    (mlyr for mlyr in mapLyrs if mlyr.name == aliasCrashes), False)
partiesLyr = next(
    (mlyr for mlyr in mapLyrs if mlyr.name == aliasParties), False)
victimsLyr = next(
    (mlyr for mlyr in mapLyrs if mlyr.name == aliasVictims), False)
collisionsLyr = next(
    (mlyr for mlyr in mapLyrs if mlyr.name == aliasCollisions), False)
citiesLyr = next((mlyr for mlyr in mapLyrs if mlyr.name == aliasCities), False)
roadsLyr = next((mlyr for mlyr in mapLyrs if mlyr.name == aliasRoads), False)
boundariesLyr = next((mlyr for mlyr in mapLyrs if mlyr.name == aliasBoundaries), False)

# Define a list of the four layers, and a list of supporting data layers
dataLyrsList = [crashesLyr, partiesLyr, victimsLyr, collisionsLyr]
suppLyrsList = [citiesLyr, roadsLyr, boundariesLyr]

# Turn off the initial visibility of layers in the map

# Iterate through the data layers list
for lyr in dataLyrsList:
    # If the layer is not False
    if lyr:
        # Set the visibility of the layer to True
        lyr.visible = False

# Iterate through the supporting data layers list
for lyr in suppLyrsList:
    # If the layer is not False
    if lyr:
        # Set the visibility of the layer to True
        lyr.visible = False

# Save the project
aprx.save()


# 6.2. Map Layer Time Settings Configuration
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# In this subsection we will configure the time settings for the map layers, so that the map view will be time-enabled

# Reminder: When doing an update on the raw data, make sure you update the the end-time date for the project (this changes with each update).
# Current End Date: 9/30/2024, thus the time settings for the map layers will be set to the end of this date (9/30/2024, 23: 59:59, or better, 10/1/2024, 00:00:00).

# Set time settings configuration for the map layers

# Define the key time parameters for the layers using a dictionary
timeSettings = {
    "st": datetime(2013, 1, 1, 0, 0),
    "et": datetime(2024, 10, 1, 0, 0),
    "td": datetime(2024, 10, 1, 0, 0) - datetime(2013, 1, 1, 0, 0),
    "stf": "date_datetime",
    "tsi": 1.0,
    "tsiu": "months",
    "tz": arcpy.mp.ListTimeZones("*Pacific*")[0]
}  # where, st: start time, et: end time, td: time extent, stf: time field, tsi: time interval, tsiu: time units, tz: time zone

# Enable layer time if needed

# Iterate through the data layer list and enable time
for mylyr in dataLyrsList:
    # if the layer is not time-enabled
    if not mylyr.isTimeEnabled:
        # Enable time for the layer
        mylyr.enableTime("date_datetime", "", "TRUE", None)
        # Set the start time for the layer
        mylyr.time.startTime = timeSettings["st"]
        # Set the end time for the layer
        mylyr.time.endTime = timeSettings["et"]
        # Set the time field for the layer
        mylyr.time.startTimeField = timeSettings["stf"]
        # Set the time step interval for the layer
        mylyr.time.timeStepInterval = timeSettings["tsi"]
        # Set the time step interval units for the layer
        mylyr.time.timeStepIntervalUnits = timeSettings["tsiu"]
        # Set the time zone for the layer
        mylyr.time.timeZone = timeSettings["tz"]

# Reset time step interval parameters (seems to be a problem showing 10 months instead of 1 month)

# Iterate through the data layer list and manually change the time's time step interval
for mylyr in dataLyrsList:
    if mylyr.isTimeEnabled:
        mylyr.time.timeStepInterval = 1.0
        mylyr.time.timeStepIntervalUnits = "months"

# Read and display the current time settings of the layers

# Iterate through the data layer list and display the time settings
for mylyr in dataLyrsList:
    print(mylyr.name)
    print(
        f" - Time Field: {codebook[timeSettings['stf']]['label']} ({timeSettings['stf']})")
    print(
        f" - Time Step Intervals: {int(mylyr.time.timeStepInterval)} {mylyr.time.timeStepIntervalUnits}")
    print(
        f" - Start Time: {str(timeSettings['st'].strftime('%m/%d/%Y %H:%M %p'))}")
    print(
        f" - End Time: {str(timeSettings['et'].strftime('%m/%d/%Y %H:%M %p'))}")
    print(
        f" - Time Extent: {int(timeSettings['td'].days):,} days ({int((timeSettings['td'].days/365)*12)} months)")
    print(f" - Time Zone: {timeSettings['tz']}")


# Save the project
aprx.save()
