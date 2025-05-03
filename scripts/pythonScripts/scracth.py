# Collisions
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Collisions",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Collisions.lyrx",
    symbology_fields = "VALUE_FIELD collSeverity collSeverity",
    update_symbology = "MAINTAIN"
)

# Collisions Fatalities
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Collisions",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Collisions Fatalities.lyrx",
    symbology_fields = "VALUE_FIELD numberKilled numberKilled",
    update_symbology = "MAINTAIN"
)

# Crashes
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Crashes",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Crashes.lyrx",
    symbology_fields = "VALUE_FIELD collSeverity collSeverity",
    update_symbology = "MAINTAIN"
)

# Crashes Killed Victims
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Crashes",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Crashes Killed Victims.lyrx",
    symbology_fields = "VALUE_FIELD numberKilled numberKilled",
    update_symbology = "MAINTAIN"
)

# Parties
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Parties",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Parties.lyrx",
    symbology_fields = "VALUE_FIELD collSeverity collSeverity",
    update_symbology = "MAINTAIN"
)

# Victims
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Victims",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Victims.lyrx",
    symbology_fields = "VALUE_FIELD collSeverity collSeverity",
    update_symbology = "MAINTAIN"
)


# Roads
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Roads",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Roads.lyrx",
    symbology_fields = "VALUE_FIELD roadCat roadCat",
    update_symbology = "MAINTAIN"
)

# Major Roads
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Major Roads",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Major Roads.lyrx",
    symbology_fields = "VALUE_FIELD roadCat roadCat",
    update_symbology = "MAINTAIN"
)

# Major Road Buffers
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Major Roads Buffers",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Major Roads Buffers.lyrx",
    symbology_fields = None,
    update_symbology = "MAINTAIN"
)

# Major Road Buffers Summary
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Major Roads Buffers Summary",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Major Roads Buffers Summary.lyrx",
    symbology_fields = None,
    update_symbology = "MAINTAIN"
)

# Major Road Split Buffers Summary
arcpy.management.ApplySymbologyFromLayer(
    in_layer="OCSWITRS Major Roads Split Buffer Summary",
    in_symbology_layer=r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Major Roads Split Buffer Summary.lyrx",
    symbology_fields="VALUE_FIELD sum_victimCount sum_victimCount",
    update_symbology="MAINTAIN"
)

# Census Blocks
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Census Blocks",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Census Blocks.lyrx",
    symbology_fields = "VALUE_FIELD populationDensity populationDensity;EXCLUSION_CLAUSE_FIELD populationDensity populationDensity",
    update_symbology = "MAINTAIN"
)

# Census Blocks Summary
arcpy.management.ApplySymbologyFromLayer(
    in_layer="OCSWITRS Census Blocks Summary",
    in_symbology_layer=r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Census Blocks Summary.lyrx",
    symbology_fields="VALUE_FIELD sum_victimCount sum_victimCount",
    update_symbology="MAINTAIN"
)

# Population Density (Census Blocks)
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Census Blocks",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Population Density.lyrx",
    symbology_fields = "VALUE_FIELD populationDensity populationDensity;EXCLUSION_CLAUSE_FIELD populationDensity populationDensity",
    update_symbology = "MAINTAIN"
)

# Housing Density (Census Blocks)
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Census Blocks",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Housing Density.lyrx",
    symbology_fields = "VALUE_FIELD housingDensity housingDensity;EXCLUSION_CLAUSE_FIELD housingDensity housingDensity",
    update_symbology = "MAINTAIN"
)


# Cities
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Cities",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Cities.lyrx",
    symbology_fields = "VALUE_FIELD cityPopDens cityPopDens",
    update_symbology = "MAINTAIN"
)

# Cities Summary
arcpy.management.ApplySymbologyFromLayer(
    in_layer="OCSWITRS Cities Summary",
    in_symbology_layer=r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Cities Summary.lyrx",
    symbology_fields="VALUE_FIELD sum_victimCount sum_victimCount",
    update_symbology="MAINTAIN"
)

# Boundaries
arcpy.management.ApplySymbologyFromLayer(
    in_layer = "OCSWITRS Boundaries",
    in_symbology_layer = r"C:\Users\ktalexan\OneDrive - County of Orange\Documents\OCSWITRS\Layers\Templates\OCSWITRS Boundaries.lyrx",
    symbology_fields = None,
    update_symbology = "MAINTAIN"
)


lytDict = {
    "single": {
        "pageWidth": 11.0,
        "pageHeight": 8.5,
        "rows": 1,
        "cols": 1,
        "nmf": 1,
        "mf1": {
            "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
            "coordX": 0.0,
            "coordY": 0.0,
            "width": 11.0,
            "height": 8.5
            }
        },
    "double": {
        "pageWidth": 22.0,
        "pageHeight": 8.5,
        "rows": 1,
        "cols": 2,
        "nmf": 2,
        "mf1": {
            "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
            "coordX": 0.0,
            "coordY": 0.0,
            "width": 11.0,
            "height": 8.5
            },
        "mf2": {
            "coords": [(11.0, 8.25), (22.0, 8.5), (11.0, 0.0), (22.0, 0.0)],
            "coordX": 11.0,
            "coordY": 0.0,
            "width": 11.0,
            "height": 8.5
            }
        },
    "quad": {
        "pageWidth": 22.0,
        "pageHeight": 17.0,
        "rows": 2,
        "cols": 2,
        "nmf": 4,
        "mf1": {
            "coords": [(0.0, 17.0), (11.0, 17.0), (0.0, 8.5), (11.0, 8.5)],
            "coordX": 0.0,
            "coordY": 8.5,
            "width": 11.0,
            "height": 8.5
            },
        "mf2": {
            "coords": [(11.0, 17.0), (22.0, 17.0), (11.0, 8.5), (22.0, 8.5)],
            "coordX": 11.0,
            "coordY": 8.5,
            "width": 11.0,
            "height": 8.5
            },
        "mf3": {
            "coords": [(0.0, 8.5), (11.0, 8.5), (0.0, 0.0), (11.0, 0.0)],
            "coordX": 0.0,
            "coordY": 0.0,
            "width": 11.0,
            "height": 8.5
            },
        "mf4": {
            "coords": [(11.0, 8.5), (22.0, 8.5), (11.0, 0.0), (22.0, 0.0)],
            "coordX": 11.0,
            "coordY": 0.0,
            "width": 11.0,
            "height": 8.5
        }
    }
}