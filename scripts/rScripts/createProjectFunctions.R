#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data Processing #
# PROJECT FUNCTIONS ####
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Empty the R environment before running the code
rm(list = ls())

library(glue)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Metadata ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define the global project settings by creating a function that returns a list of the project's metadata
projectMetadata <- function(part) {
    # Set the title based on the part
    if (part == 1) {
        step = "Part 1: Merging and Combining Datasets"
    } else if (part == 2) {
        step = "Part 2: Creating Time Series Data"
    } else if (part == 3) {
        step = "Part 3: Analyzing and Visualizing Main Data"
    } else if (part == 4) {
        step = "Part 4: Time Series Data Analysis and Visualization"
    }
    
    # create a new list
    data <- list(
        "name" = "Stata OCSWITRS Data Processing",
        "title" = step,
        "version" = "Version 2.1, May 2025",
        "author" = "Dr. Kostas Alexandridis, GISP",
        "projectYears" = 2012:2024,
        "startDate" = "2012-01-01",
        "endDate" = "2024-12-31"
    )
    # Set this program's metadata
    cat("Project Global Settings:\n")
    print(glue("\r\tName: \t{data$name}\n\r\tTitle: \t{data$title} \n\r\tVersion: {data$version} \n\r\tAuthor: {data$author}\n"))
    cat("Data Dates:\n")
    print(glue("\r\tStart Date: \t{data$startDate}\n\r\tEnd Date: \t{data$endDate}"))
    # List the data$projectYears as a sting, separated by commas
    cat("\r\tProject Years: ", paste(data$projectYears, collapse = ", "), "\n")
    # Return the data list
    return(data)
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define the global directory settings using the following function that returns a list of the project's directories
projectDirectories <- function() {
    # Get the basic project directory on the OneDrive Documents directory
    # Create a new data list
    data <- list(
        "prjPath" = getwd(),
        "rawDataPath" = file.path(getwd(), "data", "raw"),
        "codebookPath" = file.path(getwd(), "scripts", "codebook"),
        "rDataPath" = file.path(getwd(), "scripts", "rData"),
        "pyDataPath" = file.path(getwd(), "data", "python"),
        "stataDataPath" = file.path(getwd(), "data", "stata"),
        "analysisPath" = file.path(getwd(), "analysis"),
        "graphicsPath" = file.path(getwd(), "analysis", "graphics"),
        "layersPath" = file.path(getwd(), "layers"),
        "metadataPath" = file.path(getwd(), "metadata"),
        "notebooksPath" = file.path(getwd(), "notebooks"),
        "scriptsPath" = file.path(getwd(), "scripts"),
        "rScriptsPath" = file.path(getwd(), "scripts", "rScripts"),
        "pyScriptsPath" = file.path(getwd(), "scripts", "pythonScripts"),
        "stataScriptsPath" = file.path(getwd(), "scripts", "stataScripts"),
        "agpPath" = file.path(getwd(), "AGPSWITRS"),
        "masterLibPath" = file.path(Sys.getenv("HOME"), "Knowledge Management", "Documents", "Data Science", "RPackagesInstallation.R")
    )
    # Print output in console
    cat("Directory Global Settings:\n")
    print(glue(
        "\nGeneral:",
        "\n\tDefault: \t{data$rScriptsPath}",
        "\n\tProject: \t{data$prjPath}",
        "\nData: ",
        "\n\tRaw Data: \t{data$rawDataPath}",
        "\n\tCodebook: \t{data$codebookPath}",
        "\n\tR Data: \t{data$rDataPath}",
        "\n\tPython Data: \t{data$pyDataPath}",
        "\n\tStata Data: \t{data$stataDataPath}",
        "\nAnalysis: ",
        "\n\tAnalysis: \t{data$analysisPath}",
        "\n\tGraphics: \t{data$graphicsPath}",
        "\nScripts: ",
        "\n\tR Scripts: \t{data$rScriptsPath}",
        "\n\tPython Scripts: {data$pyScriptsPath}",
        "\n\tStata Scripts: \t{data$stataScriptsPath}",
        "\nGIS: ",
        "\n\tAGPSWITRS: \t{data$agpPath}",
        "\n\tLayers: \t{data$layersPath}",
        "\nOther: ",
        "\n\tMetadata: \t{data$metadataPath}",
        "\n\tNotebooks: \t{data$notebooksPath}",
        "\n\tMaster Library: {data$masterLibPath}"
    ))
    # Return the data list
    return(data)
}

# check if a file in the global environment
if (!exists("prjDirs")) {
    # if not, load the project directories
    prjDirs <- projectDirectories()
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Column Attributes ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a new function that adds column attributes to a data frame based on a codebook
addAttributes <- function(df, codebook) {
    for (cname in names(df)) {
        attr(df[[cname]], "label") <- codebook[[cname]][["label"]]
        attr(df[[cname]], "description") <- codebook[[cname]][["description"]]
        attr(df[[cname]], "varClass") <- codebook[[cname]][["varClass"]]
        attr(df[[cname]], "varCategory") <- codebook[[cname]][["varCategory"]]
        attr(df[[cname]], "varType") <- codebook[[cname]][["varType"]]
        attr(df[[cname]], "hasSource") <- codebook[[cname]][["hasSource"]]
        attr(df[[cname]], "isLabeled") <- ifelse(
            codebook[[cname]][["isLabeled"]] == 1, "Yes", "No"
        )
        attr(df[[cname]], "tsAggr") <- codebook[[cname]][["tsAggr"]]
        attr(df[[cname]], "varNotes") <- codebook[[cname]][["varNotes"]]
    }
    return(df)
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. Time Series Attributes ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define a function that adds attributes to the time series data frames
addTsAttributes <- function(tsFile, codebook) {
    for (i in names(tsFile)) {
        j = sub("^[^_]*_", "", i)
        k = sub("_.*", "", i)
        if (j %in% names(codebook)) {
            if (k == "sum") {
                attr(tsFile[[i]], "label") <- paste("Sum of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Sum of", codebook[[j]][["description"]])
            } else if (k == "min") {
                attr(tsFile[[i]], "label") <- paste("Minimum of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Minimum of", codebook[[j]][["description"]])
            } else if (k == "max") {
                attr(tsFile[[i]], "label") <- paste("Maximum of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Maximum of", codebook[[j]][["description"]])
            } else if (k == "mean") {
                attr(tsFile[[i]], "label") <- paste("Mean of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Mean of", codebook[[j]][["description"]])
            } else if (k == "sd") {
                attr(tsFile[[i]], "label") <- paste("Standard Deviation of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Standard Deviation of", codebook[[j]][["description"]])
            } else if (k == "median") {
                attr(tsFile[[i]], "label") <- paste("Median of", codebook[[j]][["label"]])
                attr(tsFile[[i]], "description") <- paste("Median of", codebook[[j]][["description"]])
            }
        } else if (i %in% names(codebook)) {
            attr(tsFile[[i]], "label") <- codebook[[i]][["label"]]
            attr(tsFile[[i]], "description") <- codebook[[i]][["description"]]
        }
    }
    rm(i, j, k)
    return(tsFile)
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 5. Graphics and Tables ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

graphicsEntry <- function(listname, type, eid, listattr, ...) {
    # Arguments:
    #   listname: The name of the list to add the entry to
    #   type: The type of entry (1=Table, 2=Graphic)
    #   listattr: A list of attributes for the entry (depends on the type)
    
    # Check if the list exists.
    if (!exists(listname)) {
        # If it does not exist, add a new list
        listname <- list(
            "tables" = list(),
            "graphics" = list()
        )
        # Reset the counters
        n = 0
        nt = 0
        ng = 0
    } else {
        # If it exists, get the list and row counters
        listname <- get(listname)
        nt <- length(listname$tables)
        ng <- length(listname$graphics)
    }
    # Get the type from the user
    t <- as.integer(type)
    # get the entry id from the user
    eid <- as.integer(eid)
    # Check if the entry is a table
    if (t == 1) {
        # check if eid is smaller or equal to nt
        if (eid <= nt) {
            cat("Table", eid, "already exists. Exiting function...")
            # exit the function
            return(listname)
        } else {
            # If it is a table, create a new table entry
            entryname = paste("Table", glue("tbl{nt + 1}"))
            # Add the table fields from the attributes list provided
            # for the table entry the attributes must have the following entries provided: name, description, caption, method, fileformat, file, status
            listname$tables[[glue("tbl{nt + 1}")]] = list(
                # ID (auto from the length of the list)
                "id" = as.character(glue("Tbl{nt + 1}")),
                # Category (auto as "Table")
                "category" = "Table",
                # Category Number (auto from the length of the tables list)
                "categoryNo" = as.integer(nt + 1),
                # Name (text from attributes)
                "name" = as.character(listattr$name),
                # Description (text from attributes)
                "description" = as.character(listattr$description),
                # Caption (text from attributes)
                "caption" = as.character(listattr$caption),
                "type" = "Table",
                # Method (from attributes any of: describe, summary, gtsummary, stat.desc, table.Stats, other)
                "method" = as.character(listattr$method),
                # Path (auto as "Overleaf - LaTeX")
                "path" = "Overleaf - LaTeX",
                # File Format (from attributes any of: native, tabular, latex, other)
                "fileformat" = as.character(listattr$fileformat),
                # File (text from attributes)
                "file" = as.character(paste0("Tbl", nt + 1, "-", listattr$file)),
                # Status (from attributes any of: draft, final, archived)
                "status" = as.character(listattr$status),
                # Date (auto as the current date)
                "date" = as.character(Sys.Date())
            )
        }
    }
    
    # Check if the entry is a graphic
    # For the graphic entry the attributes must have the following entries provided: category, name, description, caption, type, method, path, fileformat, file, resolution, width, height, status
    else if (t == 2) {
        # check if eid is smaller or equal to ng
        if (eid <= ng) {
            cat("Figure", eid, "already exists. Exiting function...")
            # exit the function
            return(listname)
        } else {
            # If it is a graphic, create a new graphic entry
            entryname = paste("Graphic", glue("fig{ng + 1}"))
            listname$graphics[[glue("fig{ng + 1}")]] = list(
                # ID (auto from the length of the graphics list)
                "id" = as.character(glue("Fig{ng + 1}")),
                # Category (from attributes any of: histogram, bar, line, scatter, box, pie, heatmap, bubble, map, other)
                "category" = as.character(listattr$category),
                # Category Number (auto from the length of the graphics list)
                "categoryNo" = as.integer(ng + 1),
                # Name (text from attributes)
                "name" = as.character(listattr$name),
                # Description (text from attributes)
                "description" = as.character(listattr$description),
                # Caption (text from attributes)
                "caption" = as.character(listattr$caption),
                # Type (from attributes any of: frequency, distribution, trend, forecast, correlation, comparison, composition, relationship, spatial, other)
                "type" = as.character(listattr$type),
                # Method (from attributes any of: ggplot2, plotly, base, lattice, other)
                "method" = as.character(listattr$method),
                # Path (auto from graphics project path)
                "path" = as.character(prjDirs$graphicsPath),
                # File Format (from attributes any of: png, jpg, tif, pdf, svg, other)
                "fileformat" = as.character(listattr$fileformat),
                # File (text from attributes)
                "file" = as.character(paste0("Fig", ng + 1, "-", listattr$file)),
                # Resolution (auto integer 300)
                "resolution" = as.integer(300),
                # Width (auto integer 12)
                "width" = as.integer(12),
                # Height (auto integer 8)
                "height" = as.integer(8),
                # Status (from attributes any of: draft, final, archived)
                "status" = as.character(listattr$status),
                # Date (auto as the current date)
                "date" = as.character(Sys.Date())
            )
        }
    }
    print(entryname)
    return(listname)
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 6. P-Value Display ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define a function to display p-values in a more readable format
pvalueDisplay <- function(pvalue) {
    if (pvalue < 0.001) {
        return("<0.001")
    } else if (pvalue >= 0.001 & pvalue < 0.01) {
        return("<0.01")
    } else if (pvalue >= 0.01 & pvalue < 0.05) {
        return("<0.05")
    } else {
        return(pvalue)
    }
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 7. STL Decomposition Graphs ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create a function to plot the STL decomposition
createStlPlot <- function(tsdata, tscale = "month", type = "stlplus", lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"), tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")) {
    
    # Determine the scale of the sub-labels
    if (tscale == "quarter") {
        sublab = paste("Quarter", 1:4)
    } else if (tscale == "month") {
        sublab = substr(month.name, 1, 3)
    } else if (tscale == "week") {
        sublab = paste("Week", 1:53)
    } else if (tscale == "day") {
        sublab = paste("Day", 1:365)
    }
    
    # Create the stl object
    if (type == "stlplus") {
        # create the stlplus object
        stldata <- stlplus(tsdata, s.window = "periodic", sub.labels = sublab)
        stlraw <- data.frame(time = time(stldata), value = getraw(stldata))
        stlseasonal <- data.frame(time = time(stldata), value = seasonal(stldata))
        stltrend <- data.frame(time = time(stldata), value = trend(stldata))
        stlremainder <- data.frame(time = time(stldata), value = remainder(stldata))
    } else if (type == "stl") {
        stldata <- stl(tsdata, s.window = "periodic")
        stlraw <- data.frame(time = time(tsdata), value = tsdata)
        stlseasonal <- data.frame(time = time(stldata), value = stldata$time.series[, "seasonal"])
        stltrend <- data.frame(time = time(stldata), value = stldata$time.series[, "trend"])
        stlremainder <- data.frame(time = time(stldata), value = stldata$time.series[, "remainder"])
    }
    
    # create the raw subplot
    praw <- ggplot(
        stlraw,
        aes(x = time, y = value)) +
        geom_line(color = lcolors[1], linewidth = 0.75) +
        labs(x = "Time", y = "Raw") +
        theme_hc() +
        theme(
            text = element_text(color = "black", size = 13, vjust = 0.5, hjust = 0.5, face = "bold"),
            axis.text.x = element_blank(),
            axis.title.x = element_blank(),
            axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 1, vjust = 0, face = "plain"),
            axis.title.y = element_text(color = tcolors[1], size = 15, angle = 90, hjust = 0.5, vjust = 1, face = "bold"),
            axis.line.x = element_blank(),
            axis.ticks.x = element_blank()
        )
    
    # Create the seasonal subplot
    pseasonal <- ggplot(
        stlseasonal,
        aes(x = time, y = value)) +
        geom_line(color = lcolors[2], linewidth = 0.75) +
        labs(x = "Time", y = "Seasonal") +
        theme_hc() +
        theme(
            text = element_text(color = "black", size = 13, vjust = 0.5, hjust = 0.5, face = "bold"),
            axis.text.x = element_blank(),
            axis.title.x = element_blank(),
            axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 1, vjust = 0, face = "plain"),
            axis.title.y = element_text(color = tcolors[2], size = 15, angle = 90, hjust = .5, vjust = 1, face = "bold"),
            axis.line.x = element_blank(),
            axis.ticks.x = element_blank()
        )
    
    # Create the trend subplot
    ptrend <- ggplot(
        stltrend,
        aes(x = time, y = value)) +
        geom_line(color = lcolors[3], linewidth = 1.5) +
        labs(x = "Time", y = "Trend") +
        theme_hc() +
        theme(
            text = element_text(color = "black", size = 13, vjust = 0.5, hjust = 0.5, face = "bold"),
            axis.text.x = element_blank(),
            axis.title.x = element_blank(),
            axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 1, vjust = 0, face = "plain"),
            axis.title.y = element_text(color = tcolors[3], size = 15, angle = 90, hjust = .5, vjust = 1, face = "bold"),
            axis.line.x = element_blank(),
            axis.ticks.x = element_blank()
        )
    
    # Create the remainder subplot
    premainder <- ggplot(
        stlremainder,
        aes(x = time, y = value)) +
        geom_line(color = lcolors[4], linewidth = 0.75) +
        labs(x = "Time", y = "Remainder") +
        theme_hc() +
        theme(
            text = element_text(color = "black", size = 13, vjust = 0.5, hjust = 0.5, face = "bold"),
            axis.text.x = element_text(color = "black", size = 13, angle = 0, hjust = 1, vjust = 0, face = "plain"),
            axis.title.x = element_text(color = "black", size = 15, angle = 0, hjust = .5, vjust = -0.5, face = "plain"),
            axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 1, vjust = 0, face = "plain"),
            axis.title.y = element_text(color = tcolors[4], size = 15, angle = 90, hjust = .5, vjust = 1, face = "bold"),
            axis.line.x.bottom = element_line(color = "black", size = 0.5)
        ) +
        scale_x_continuous(breaks = seq(floor(min(time(stldata))), ceiling(max(time(stldata))), by = 1))
    
    # combine the subplots
    pcombined <- ggarrange(
        praw, pseasonal, ptrend, premainder, 
        ncol = 1, nrow = 4, align = "v", 
        widths = c(0.5, 0.5, 0.5, 0.5), heights = c(1, 1, 1, 1.35), 
        hjust = 0, vjust = -5) + 
        theme_hc() +
        theme(
            axis.title = element_blank(),
            axis.text = element_blank(),
            axis.line = element_blank(),
            axis.ticks = element_blank(),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.border = element_blank()
        ) + 
        geom_segment(aes(x=0.637, y=0.02, xend=0.637, yend=1), linetype = "dashed", color = "forestgreen", linewidth = 0.7) +
        geom_segment(aes(x=0.78, y=0.02, xend=0.78, yend=1), linetype = "dashed", color = "forestgreen", linewidth = 0.7) +
        annotate('rect', xmin = 0.637, xmax = 0.78, ymin = 0.02, ymax = Inf, alpha =.2, fill = "green") +
        annotate("text", x = 0.71, y = 0.01, label = "COVID-19 Restrictions", fontface = "italic", color = "darkgreen", size = 3.5)
    
    # Create the final output object
    result <- list(
        "data" = list("stl" = stldata, "raw" = stlraw, "seasonal" = stlseasonal, "trend" = stltrend, "remainder" = stlremainder),
        "graphics" = list("stl" = pcombined, "raw" = praw, "seasonal" = pseasonal, "trend" = ptrend, "remainder" = premainder)
    )
    # return the combined plot
    return(result)
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 8. Save to Disk ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define a function to save the data frames and data to disk so it can be called at different points in the script
saveToDisk <- function() {
    cat("1. Saving the data frames to disk", "\n")

    # Save the raw data frames to disk
    for (i in c("crashes", "crashes.agp", "parties", "parties.agp", "victims", "victims.agp", "collisions", "collisions.agp", "cities", "cities.agp", "roads", "roads.agp",  "boundaries",  "boundaries.agp")) {
        if (exists(i)) {
            cat("  ", "- Saving the", i, "data frame:", paste0(i, ".RData"), "\n")
            save(list = i, file = file.path(prjDirs$rDataPath, paste0(i, ".RData")))
        }
    }
    rm(i)

    # Save the codebook and reference table
    flist <- c()
    for (i in c("cb", "cbTable")) {
        if (exists(i)) {
            # add i to flist
            flist <- c(flist, i)
        }
    }
    if (length(flist) > 0) {
        cat("  ", "- Saving the codebook and reference table to cb.RData", "\n")
        save(list = flist, file = file.path(prjDirs$codebookPath, "cb.RData"))
    }
    rm(i, flist)

    # Export and save the codebook to disk as a JSON file
    if (exists("cb")) {
        cat("  ", "- Exporting the codebook to a JSON file:", "cb.json", "\n")
        cb.json <- toJSON(cb, pretty = TRUE, auto_unbox = TRUE)
        write(cb.json, file = file.path(prjDirs$codebookPath, "cb.json"))
        rm(cb.json)
    }

    # Save the functions to disk
    flist <- c()
    for (i in c("projectMetadata", "projectDirectories", "addAttributes", "addTsAttributes", "graphicsEntry", "pvalueDisplay", "createStlPlot", "saveToDisk")) {
        if (exists(i)) {
            # add i to flist
            flist <- c(flist, i)
        }
    }
    if (length(flist) > 0) {
        cat("  ", "- Saving the project functions to project_functions.RData", "\n")
        save(list = flist, file = file.path(prjDirs$rDataPath, "projectFunctions.RData"))
    }
    rm(i, flist)

    # Save the time series data frames to disk
    for (i in c("tsYear", "tsQuarter", "tsMonth", "tsWeek", "tsDay")) {
        if (exists(i)) {
            cat("  ", "- Saving the", i, "data frame:", paste0(i, ".RData"), "\n")
            save(list = i, file = file.path(prjDirs$rDataPath, paste0(i, ".RData")))
        }
    }
    rm(i)

    # Save the graphics list to disk
    if (exists("graphicsList")) {
        cat("  ", "- Saving the graphics list to graphicsList.RData", "\n")
        save(graphicsList, file = file.path(prjDirs$rDataPath, "graphicsList.RData"))
    }
}


# Save the data to disk
saveToDisk()

setwd(prjDirs$prjPath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

