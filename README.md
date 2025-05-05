# :vertical_traffic_light: OCSWITRS: Orange County Traffic Collisions Analysis


:label: Historical Traffic Collisions in Orange County, California. Analysis of the SWITRS (Statewide Integrated Traffic Records System) data.

<div align="center">

**:bust_in_silhouette: Kostas Alexandridis, PhD, GISP** | *:label: v.2.1, May 2025*

![Static Badge](https://img.shields.io/badge/OCSWITRS-GitHub?style=plastic&logo=github&logoSize=auto&label=GitHub&labelColor=navy) 
![GitHub License](https://img.shields.io/github/license/ktalexan/PolicyAnalysis?style=plastic&labelColor=black) 
![Shield Badge: Language-R](https://img.shields.io/static/v1?style=plastic&label=language&message=R&logo=R&color=blue&logoColor=blue&labelColor=black)
![Shield Badge: Language-Python](https://img.shields.io/static/v1?style=plastic&label=language&message=Python&logo=python&color=forestgreen&logoColor=blue&labelColor=black)

</div>

----


This repository contains the analysis of traffic collisions in Orange County, California, using the SWITRS (Statewide Integrated Traffic Records System) data. The analysis includes data cleaning, visualization, and modeling to understand the factors contributing to traffic collisions in the region.
The analysis is conducted using Python, R, and Stata, and the results are presented in Jupyter notebooks and scripts. The repository also includes metadata files, graphics, and presentation content.
The resulting OCSWITRS data are spatially geocoded, imported into ArcGIS project geodatabase, and used for spatial analysis and visualization. Furthermore, the data are published as feature services and maps and shared publicly both on ArcGIS online, and in the Orange County Open GIS Portal: https://ocgis.com.

Below the main project folder structure is provided and described. The project is organized into several folders, each containing specific types of files related to the analysis.

## Folder Structure

### Synced Folders

- :file_folder: [**analysis**](analysis): Contains the analysis files, including graphics and presentation content.
  - :file_folder: [**graphics**](analysis/graphics): Contains the graphics files used in the analysis.
- :file_folder: [**metadata**](metadata): Contains the metadata files for the project.
- :file_folder: [**notebooks**](notebooks): Contains the Jupyter notebooks used in the analysis.
  - :file_folder: [**archived**](notebooks/archived): Contains the archived Jupyter notebooks used in the analysis.
  - :file_folder: [**custom**](notebooks/custom): Contains the custom Jupyter notebooks used in the analysis.
- :file_folder: [**scripts**](scripts): Contains the scripts used in the analysis including Python, R, and Stata scripts.
  - :file_folder: [**codebook**](scripts/codebook): Contains the codebook files used in the analysis.
  - :file_folder: [**other**](scripts/other): Contains other scripts used in the analysis.
  - :file_folder: [**pythonScripts**](scripts/pythonScripts): Contains the Python scripts used in the analysis.
  - :file_folder: [**rData**](scripts/rData): Contains the R data files used in the analysis.
  - :file_folder: [**rScripts**](scripts/rScripts): Contains the R scripts used in the analysis.
  - :file_folder: [**stataScripts**](scripts/stataScripts): Contains the Stata scripts used in the analysis.

### Not Synced Folders[^1]

[^1]: The data, AGPSWITRS, layers, maps, layouts, and styles folders are not synced to the repository due to their large size. The content in these folders can, for the most part, be recreated from the scripts and notebooks in the repository. Instructions for setting up the project structure and folders are provided in the [Getting Started](#getting-started) section.

- :file_folder: **data**: Contains the raw data files, including the original SWITRS raw data files, and data in different formats (codebook, python, R, Stata).
- :file_folder: **AGPSWITRS**: Contains the ArcGIS Pro project data files.
- :file_folder: **layers**: Contains the layers used in the ArcGIS Pro project.
- :file_folder: **maps**: Contains the maps generated in the ArcGIS Pro project.
- :file_folder: **layouts**: Contains the layouts used in the ArcGIS Pro project.
- :file_folder: **styles**: Contains the styles used in the ArcGIS Pro project.


## Getting Started

If you are creating a project from scratch, and need to setup the project structure for the non-synced folders, please follow the following instructions.

### Setting up the Default ArcGIS Pro Project

1. Create a new ArcGIS Pro project named `AGPSWITRS`. The ArcGIS Pro project should be created in the root folder of the repository. 
   - Use the 'create folder' option in ArcGIS pro to create the project inside its own folder. The folder name should be `AGPSWITRS`.
   - The folder structure should look like this (for ArcGIS Pro 3.4.x, currently using 3.4.3):
     ```
     /OCSWITRS
       ├── AGPSWITRS
       │   ├── .backups
       │   ├── AGPSWITRS.gdb
       │   ├── GpMessages
       │   ├── ImportLog
       │   ├── Index
       │   ├── AGPSWITRS.aprx
       │   └── AGPSWITRS.atbx
     ```
2. Once the ArcGIS pro project is created, open the project in ArcGIS Pro, and create four new feature datasets in the geodatabase. The feature datasets should be named `analysis`, `hotspots`, `raw`, and `supporting`. The feature datasets should be created in the `AGPSWITRS.gdb` geodatabase. Each of the feature datasets should use the [WGS 1984 Web Mercator (auxiliary sphere)](https://pro.arcgis.com/en/pro-app/latest/help/mapping/properties/mercator.htm) cooordinate system [(EPSG:3857)](https://epsg.io/3857) - default for ArcGIS online integration. The folder structure should look like this:
   ```
   /OCSWITRS
     ├── AGPSWITRS
     │   ├── (...)
     │   ├── AGPSWITRS.gdb
     │   │   ├── analysis
     │   │   ├── hotspots
     │   │   ├── raw
     │   │   └── supporting
     |   ├── (...)
   ```
3. (Optional) Add the OCSWITRS root repository folder to the ArcGIS Pro project (from the `Catalog` pane, right click on `Folders`, and select `Add Folder Connection`). This will allow you to easily access the repository files from within ArcGIS Pro.
4. Add the notebooks Part1, Part2 and Part 3 from the `notebooks` folder to the ArcGIS Pro project. Instructions: right click any empty space in the `Catalog` pane, and select `Add` > `Add and Open Notebook`. Then find the notebooks folder in the OCSWITRS repository, and select the notebooks to add. The notebooks should be added to the `Notebooks` folder in the `Catalog` pane.
5. Save and close the ArcGIS Pro project. The project is now ready to be used with the OCSWITRS repository.

### Setting up the supporting ArcGIS Pro Project folders

Add the `layers`, `maps`, `layouts`, and `styles` folders to the `AGPSWITRS` folder root. The folder structure should look like this:
```
/OCSWITRS
  ├── (...)
  ├── layers
  ├── maps
  ├── layouts
  ├── styles
  ├── (...)
```
These folders are used by the project scripts to store the layers, maps, layouts, and styles used in the ArcGIS Pro project. The folders are empty by default, and will be populated with files as the project is developed.

### Setting up the Data Folder Structure

Create the following folder structure in the `data` folder. The folder structure should look like this:
```
/OCSWITRS
  ├── data
  │   ├── gis
  │   ├── python
  │   └── raw
```
The SWITRS raw data files should be placed in the `raw` folder. The `gis` folder is used for the GIS data files stored by the scripts, and the `python` folder is used for the Python data files used in the project.
The raw OCSWITRS data files are raw csv files organized by type and year, in the format `<type>_<year>.csv` (e.g., `Crashes_2020.csv`, `Parties_2020.csv`, `Victims_2020.csv`, etc.). If you download the data from the TIMS website, you have to run the query for each year separately (dates from 01/01/YYYY to 12/31/YYYY). Then download each of the crashes, parties and victims csv files, and rename them to the aforementioned format inside the `raw` data subfolder. Already prepared data files for the years 2012-2024, are available for download in a zip file here: [OCSWITRS Raw Data 2012-2024.zip](https://ocgov.box.com/s/gj2d1n66f8o8vcdidgkmlmnpgzzbi9y6).





## Processing Steps

The following mermaid diagram illustrates the processing steps of the project. The diagram shows the flow of data from the raw data files to the final analysis and visualization. The diagram contains two main sections: the R scripts and the Python Jupyter notebooks. 

The R scripts are used for data preparation and processing. The R scripts are organized into three main sections: preparation, processing, and analyzing. The preparation section includes the merging of raw data and project functions. The processing section includes the import of raw data and the creation of time series data. The analyzing section includes the analysis of crash data and time series data analysis. 

The Python Jupyter notebooks are used for analysis and visualization of spatial data. The notebooks are organized into five main sections: part 1, part 2, part 3, part 4, and part 5. Part 1 includes feature processing, part 2 includes map processing, part 3 includes layout processing, part 4 includes importing GIS data, and part 5 includes hot spot analysis.

```mermaid
---
config:
  layout: dagre
---
flowchart TD
 subgraph sr1["Preparation"]
        r2("Merging Raw Data")
        r1("Project Functions")
  end
 subgraph sr2["Processing"]
        r4("Create Time Series")
        r3("Import Raw Data")
  end
 subgraph sr3["Analyzing"]
        r6("Time Series Data Analysis")
        r5("Analyze Crash Data")
  end
 subgraph sp1["Part 1"]
        p1("Feture Processing")
   end
 subgraph sp2["Part 2"]
        p2("Map Processing")
  end
 subgraph sp3["Part 3"]
        p3("Layout Processing")
  end
 subgraph sp4["Part 4"]
        p4("Importing GIS Data")
  end
 subgraph sp5["Part 5"]
        p5("Hot Spot Analysis")
  end
 subgraph sr["R Scripts"]
    direction LR
        sr1
        sr2
        sr3
  end
 subgraph sp["Python Jupyter Notebooks"]
    direction LR
        sp1
        sp2
        sp3
        sp4
        sp5
  end
    r1 --> r2
    r3 --> r4
    r5 --> r6
    sr1 --> sr2
    sr2 --> sr3
    sp1 --> sp2
    sp2 --> sp3
    sp3 --> sp4
    sp4 --> sp5
    sr --> sp
    style sr1 fill:#004040
    style sr2 fill:#002e63
    style sr3 fill:#4b0082
    style sp1 fill:#0000FF
    style sp2 fill:#008080
    style sp3 fill:#800080
    style sp4 fill:#7d6608
    style sp5 fill:#641e16
```

To understand the project process and analysis, please review the documentation in this project. The two major code sections are the R scripts and the Python Jupyter notebooks. The R scripts are used for data preparation and processing, while the Python Jupyter notebooks are used for analysis and visualization of spatial data. The following sections provide an overview of the R scripts and Python Jupyter notebooks used in the project.

### R Scripts Sequence

The starting point is the [**R Scripts**](scripts/rScripts) folder, where the data is cleaned and prepared for analysis. The [README.md](scripts/rScripts/README.md) file in this folder provides an overview of the data processing steps, and the sequence of the scripts to be applied. The scripts are organized in a way that allows for easy navigation and understanding of the data processing steps.

### Python Jupyter Notebooks Sequence

The [**Python Jupyter Notebooks**](notebooks) folder contains the notebooks used for analysis and visualization of spatial data. The notebooks are organized into five main sections: part 1, part 2, part 3, part 4, and part 5. Review the [README.md](notebooks/README.md) section file that provides an overview of the spatial analysis and visualization process sequence. The notebooks are organized in a way that allows for easy navigation and understanding of the analysis steps.
