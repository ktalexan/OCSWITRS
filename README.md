# :vertical_traffic_light: Orange County Traffic Collisions Analysis (OCSWITRS)

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

[^1]: The data, AGPSWITRS, layers, maps, layouts, and styles folders are not synced to the repository due to their large size. The content in these folders can, for the most part, be recreated from the scripts and notebooks in the repository.

- :file_folder: **data**: Contains the raw data files, including the original SWITRS raw data files, and data in different formats (codebook, python, R, Stata).
- :file_folder: **AGPSWITRS**: Contains the ArcGIS Pro project data files.
- :file_folder: **layers**: Contains the layers used in the ArcGIS Pro project.
- :file_folder: **maps**: Contains the maps generated in the ArcGIS Pro project.
- :file_folder: **layouts**: Contains the layouts used in the ArcGIS Pro project.
- :file_folder: **styles**: Contains the styles used in the ArcGIS Pro project.

## Getting Started

To understand the project process and analysis, please review the documentation in this project. The starting point is the [**R Scripts**](scripts/rScripts) folder, where the data is cleaned and prepared for analysis. The [README.md](scripts/rScripts/README.md) file in this folder provides an overview of the data processing steps, and the sequence of the scripts to be applied. The scripts are organized in a way that allows for easy navigation and understanding of the data processing steps.

