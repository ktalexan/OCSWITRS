#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data ANALYSIS #
# PART 4: TIME SERIES DATA ANALYSIS AND VISUALIZATION ####
# v 2.1, May 2025
# Dr. Kostas Alexandridis, GISP
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Preliminaries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 1.1. Environment Setup ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Empty the R environment before running the code
rm(list = ls())


## 1.2. Import Libraries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Open the R Libraries master file (located in Obsidian's library folder) - Already defined in the project_directories function
#libmaster = file.path(Sys.getenv("HOME"), "Knowledge Management", "Documents", "Data Science", "RPackagesInstallation.R")
#file.edit(libmaster)

# Load the pacman library. If not installed, install it first.
if (!requireNamespace("pacman", quietly = TRUE)) {
    install.packages("pacman")
}
library(pacman)

# Load the required libraries using pacman
pacman::p_load(RColorBrewer, lubridate, jsonlite, dplyr, magrittr, R6, haven, labelr, plyr, stringr, purrr, glue, Hmisc, psych, tibble, here, tidyr, chattr, knitr, labelled, ggplot2, ggthemes, gtsummary, gt, vtable, stargazer, scales, pastecs, collapse, formattable, xtable, forecast, ggpubr, stlplus, sf, sp, leaflet, rnaturalearth, rnaturalearthdata, reshape2, gridExtra, arcgisutils, cowplot)


## 1.3. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

getwd()

# Load the project functions from the RData file located in the /Data/R directory
load(file = file.path(getwd(), "scripts", "rData", "projectFunctions.RData"))


## 1.4. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- projectMetadata(part = 4)

# Get the project directories
prjDirs <- projectDirectories()


## 1.5. Set the working directory ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the working directory to the data directory
setwd(prjDirs$rDataPath)
getwd()


## 1.6. Load Data Frames ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the OCSWITRS data from the RData file
sapply(c("collisions.RData", "collisions.agp.RData", "crashes.RData", "crashes.agp.RData", "parties.RData", "parties.agp.RData", "victims.RData", "victims.agp.RData", "cities.RData", "cities.agp.RData", "roads.RData", "roads.agp.RData", "boundaries.RData", "boundaries.agp.RData"), load, .GlobalEnv)

# Load the time series RData files
sapply(c("tsYear.RData", "tsQuarter.RData", "tsMonth.RData", "tsWeek.RData", "tsDay.RData"), load, .GlobalEnv)

# load the graphics list RData file
load(file = "graphicsList.RData")

# load the codebook file
load(file = file.path(prjDirs$codebookPath, "cb.RData"))

### Set Graphics Directory ####

# Set the working directory to the graphics folder
setwd(prjDirs$graphicsPath)
getwd()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Seasonal Time Series Analysis ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# See: https://www.geeksforgeeks.org/stl-trend-of-time-series-using-r/


## 2.1. Create Time Series Objects ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Number of Crashes ####

tslistCrashes <- list(
    "quarter" = ts(tsQuarter$crashTagSum, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$crashTagSum, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$crashTagSum, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$crashTagSum, frequency = 365, start = c(2012, 1))
)

### Number of Victims ####

tslistVictims <- list(
    "quarter" = ts(tsQuarter$victimCountSum, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$victimCountSum, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$victimCountSum, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$victimCountSum, frequency = 365, start = c(2012, 1))
)

### Number of fatal accidents ####

tslistFatal <- list(
    "quarter" = ts(tsQuarter$numberKilledSum, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$numberKilledSum, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$numberKilledSum, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$numberKilledSum, frequency = 365, start = c(2012, 1))
)


### Fatal or Severe Accidents ####

tslistFatalSevere <- list(
    "quarter" = ts(tsQuarter$countFatalSevereSum, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$countFatalSevereSum, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$countFatalSevereSum, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$countFatalSevereSum, frequency = 365, start = c(2012, 1))
)


### Number of injuries ####

tslistInj <- list(
    "quarter" = ts(tsQuarter$numberInjSum, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$numberInjSum, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$numberInjSum, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$numberInjSum, frequency = 365, start = c(2012, 1))
)

### Mean collision severity ####

tslistSev <- list(
    "quarter" = ts(tsQuarter$collSeverityMean, frequency = 4, start = c(2012, 1)),
    "month" = ts(tsMonth$collSeverityMean, frequency = 12, start = c(2012, 1)),
    "week" = ts(tsWeek$collSeverityMean, frequency = 53, start = c(2012, 1)),
    "day" = ts(tsDay$collSeverityMean, frequency = 365, start = c(2012, 1))
)


## 2.2. Decompose Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Number of Crashes ####

# Create the STL decomposition for the monthly crashes time series using stlplus object
stl.m.crashes <- createStlPlot(
    tslistCrashes$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly crashes time series using stl object
stl.w.crashes <- createStlPlot(
    tslistCrashes$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


### Number of Victims ####

# Create the STL decomposition for the monthly victims time series using stl object
stl.m.victims <- createStlPlot(
    tslistVictims$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly victims time series using stl object
stl.w.victims <- createStlPlot(
    tslistVictims$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


### Fatal Accidents ####

# Create the STL decomposition for the monthly fatal accidents time series using stl object
stl.m.fatal <- createStlPlot(
    tslistFatal$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly fatal accidents time series using stl object
stl.w.fatal <- createStlPlot(
    tslistFatal$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


### Fatal or Severe Accidents ####

# Create the STL decomposition for the monthly fatal or severe accidents time series using stl object
stl.m.fatalSevere <- createStlPlot(
    tslistFatalSevere$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly fatal or severe accidents time series using stl object
stl.w.fatal_severe <- createStlPlot(
    tslistFatalSevere$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


### Number of Injuries ####

# Create the STL decomposition for the monthly injury accidents time series using stl object
stl.m.inj <- createStlPlot(
    tslistInj$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly injury accidents time series using stl object
stl.w.inj <- createStlPlot(
    tslistInj$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


### Mean Collision Severity ####

# Create the STL decomposition for the monthly mean collision severity time series using stl object
stl.m.sev <- createStlPlot(
    tslistSev$month,
    tscale = "month",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)

# Create the STL decomposition for the weekly mean collision severity time series using stl object
stl.w.sev <- createStlPlot(
    tslistSev$week,
    tscale = "week",
    type = "stlplus",
    lcolors = c("royalblue3", "darkolivegreen4", "brown", "mediumorchid"),
    tcolors = c("royalblue4", "darkolivegreen", "brown4", "mediumorchid4")
)


## 2.3. Figure 4 - monthly Fatalities Time Series ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 4 (monthly fatalities time series)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 4, listattr = list(category = "time series", name = "Monthly Fatalities Time Series", description = "Time series plot of the number of fatal accidents in monthly data", caption = paste("Display of the monthly time series data for the number of killed victims, along with a local LOESS regression trend fit with its 95% confidence intervals. The data are reported over", nrow(tsMonth), "months time period, between", format(min(as.Date(collisions$dateDatetime)), "%B %d, %Y"), "and", format(max(as.Date(collisions$dateDatetime)), "%B %d, %Y")), type = "time series", method = "ggplot2", fileformat = "png", file = "Time Series Monthly Fatalities", status = "final"))


### Definition ####

# Define the time series data for Figure 4 (monthly number of killed victims)
fig4data <- tsMonth[, c("dateMonth", "numberKilledSum")]
colnames(fig4data) <- c("time", "fatalities")

# Setting the plot parameters
options(repr.plot.width = 12, repr.plot.height = 8, repr.plot.res = 300, repr.plot.quality = 100, repr.plot.pointsize = 13, repr.plot.unit = "in")

# Create the time series ovelay plot for the monthly number of killed victims
fig4 <- ggplot(fig4data, aes(x = time, y = fatalities)) +
    # First, add the Covid-19 restrictions area of interest annotation layer (behind everything else)
    annotate(
        'rect', 
        xmin = as_date("2020-03-01"), xmax = as_date("2022-03-01"), 
        ymin = -Inf, ymax = Inf, 
        alpha =.2, fill = "green") +
    # Add the covid-19 reference lines (left and right)
    geom_vline(xintercept = c(as_date("2020-03-01"), as_date("2022-03-01")),
               linewidth = 0.5,
               linetype = "dashed",
               color = "darkgreen") +
    # Add the covid-19 reference text annotation
    annotate("text", x = as_date("2020-03-01") + (as_date("2022-03-01") - as_date("2020-03-01")) / 2,
             y = -2,
             label = "COVID-19 Restrictions",
             fontface = "bold.italic",
             color = "darkgreen",
             size = 3.5
    ) + 
    # Add the time series line for the number of killed victims
    geom_line(aes(y = fatalities, color = "navy"), linewidth = 1, alpha = 0.6) +
    # Add the smoothed LOESS trend line and 95% confidence intervals for the number of killed victims
    geom_smooth(method = "loess", se = TRUE, span = 0.2, formula = y ~ x, na.rm = TRUE, level = 0.95, aes(y = fatalities,  color = "red4"), fill = "darkorange", alpha = 0.4, linewidth = 2) +
    # Add the graph labels
    labs(x = "Date", y = "Number of Killed Victims") +
    # General graph theme
    theme_hc() +
    theme(
        # general text settings
        text = element_text(size = 13, vjust = 0.5, hjust = 0.5, face = "plain"),
        # time axis labels
        axis.text.x = element_text(color = "black", size = 13, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        # Time axis title
        axis.title.x = element_text(color = "black", size = 15, angle = 0, hjust = .5, vjust = -2, face = "plain"),
        # Y axis labels (both)
        axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        # Fatalities axis title (left axis)
        axis.title.y.left = element_text(color = "black", size = 15, angle = 90, hjust = .5, vjust = 1, face = "plain"),
        # Adjust the x axis ticks
        #axis.ticks.length = unit(5, "pt"),
        axis.line.x.bottom = element_line(color = "black", size = 0.5),
        # Legend settings
        legend.title = element_text(color = "gray10", size = 13, face = "bold", hjust = 0, vjust = 0.5),
        #legend.title = element_blank(),
        legend.position = "inside",
        legend.position.inside = c(.05, .12), 
        legend.justification = "left",
        legend.text=element_text(size = 12, face = "plain"),
        legend.direction = "vertical", 
        legend.box = "horizontal",
        legend.background = element_rect(linetype = "solid", linewidth = 0.5, color = "gray50", fill = "whitesmoke"),
        # Adjust the grid lines for the graph
        #panel.grid.major.x = element_line(color = "azure", linewidth = 0.5),
        #panel.grid.major.y = element_line(color = "azure", linewidth = 0.5)
    ) +
    scale_x_date(date_breaks = "1 year", date_labels = "%b\n%Y") +
    scale_color_identity(
        name = "Time Series Legend",
        breaks = c("navy", "red4"),
        labels = c("Number of Killed Victims", "Fatalities Loess Regression Trend (95% CI)"),
        guide = "legend"
    ) +
    # Adjust the rows of the legends
    guides(color = guide_legend(nrow = 2, byrow = TRUE))

# Display the time series plot for the monthly number of victims killed
fig4


### Storage ####

# Save Figure 4 (monthly fatalities time series) to disk
ggsave(filename = file.path(graphicsList$graphics$fig4$path, paste0(graphicsList$graphics$fig4$file, ".", graphicsList$graphics$fig4$fileformat)), plot = fig4, width = graphicsList$graphics$fig4$width, height = graphicsList$graphics$fig4$height, units = "in", dpi = graphicsList$graphics$fig4$resolution)


## 2.3. Figure 5 - Weekly Crashes Decomposition Plots ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 4 (weekly crashes STL decomposition)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 5, listattr = list(category = "stl decomposition", name = "STL decomposition of the number of crashes weekly data", description = "STL decomposition plot of the number of crash incidents in weekly time series data", caption = "STL decomposition of the number of collision incidents in the weekly time series data for Orange County, California", type = "decomposition", method = "ggplot2", fileformat = "png", file = "STL Plot Weekly Crashes", status = "final"))


### Definition ####

# Create the STL decomposition plot for the weekly crashes time series
fig5 <- stl.w.crashes$graphics$stl

# Display the stl plots
fig5


### Storage ####

# Save Figure 5 (weekly crashes STL decomposition) to disk
ggsave(filename = file.path(graphicsList$graphics$fig5$path, paste0(graphicsList$graphics$fig5$file, ".", graphicsList$graphics$fig5$fileformat)), plot = fig5, width = graphicsList$graphics$fig5$width, height = graphicsList$graphics$fig5$height, units = "in", dpi = graphicsList$graphics$fig5$resolution)


## 2.4. Figure 6 - Weekly Fatal Accidents Decomposition Plots ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 5 (weekly fatal accidents STL decomposition)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 6, listattr = list(category = "stl decomposition", name = "STL decomposition of the number of fatal accidents weekly data", description = "STL decomposition plot of the number of fatal accidents in weekly time series data", caption = "STL decomposition of the number of fatal accidents in the weekly time series data for Orange County, California", type = "decomposition", method = "ggplot2", fileformat = "png", file = "STL Plot Weekly Fatalities", status = "final"))


### Definition ####

# Create the STL decomposition plot for the weekly fatal accidents time series
fig6 <- stl.w.fatal$graphics$stl

# Display the stl plots
fig6


### Storage ####

# Save Figure 6 (weekly fatal accidents STL decomposition) to disk
ggsave(filename = file.path(graphicsList$graphics$fig6$path, paste0(graphicsList$graphics$fig6$file, ".", graphicsList$graphics$fig6$fileformat)), plot = fig6, width = graphicsList$graphics$fig6$width, height = graphicsList$graphics$fig6$height, units = "in", dpi = graphicsList$graphics$fig6$resolution)


## 2.5. Figure 7 - Mean Monthly Collision Severity Decomposition Plots ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 6 (weekly mean collision severity STL decomposition)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 7, listattr = list(category = "stl decomposition", name = "STL decomposition of the mean collision severity weekly data", description = "STL decomposition plot of the mean collision severity in weekly time series data", caption = "STL decomposition of the mean collision severity in the weekly time series data for Orange County, California", type = "decomposition", method = "ggplot2", fileformat = "png", file = "STL Plot Weekly Severity", status = "final"))


### Definition ####

# Create the STL decomposition plot for the weekly mean collision severity time series
fig7 <- stl.w.sev$graphics$stl

# Display the stl plots
fig7


### Storage ####

# Save Figure 7 (weekly mean collision severity STL decomposition) to disk
ggsave(filename = file.path(graphicsList$graphics$fig7$path, paste0(graphicsList$graphics$fig7$file, ".", graphicsList$graphics$fig7$fileformat)), plot = fig7, width = graphicsList$graphics$fig7$width, height = graphicsList$graphics$fig7$height, units = "in", dpi = graphicsList$graphics$fig7$resolution)


## 2.6. Figure 8 - Number of Victims vs. Mean Severity ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 7 (weekly mean collision severity vs. number of victims)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 8, listattr = list(category = "time series overlap", name = "", description = "Overlap plot of the number of victims vs. the mean severity rank in weekly time series data", caption = paste("Overlapping display of the weekly time series data for (a) the number of victims along with a Loess local regression trend line fit, and (b) the mean collision severity ordinal rank along with its Loess local regression trend line fit. Data was reported over 138 months of weekly time intervals, from", format(min(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), "to", format(max(as.Date(collisions$dateDatetime)), "%m/%d/%Y")), type = "time series", method = "ggplot2", fileformat = "png", file = "Overlap Victims vs Severity", status = "final"))


### Definition ####

# Define the time series data for Figure 7 (weekly number of victims vs. mean collision severity)
fig8data <- tsWeek[, c("dateWeek", "victimCountSum", "collSeverityMean")]
fig8data$zvictims <- scale(fig8data$victimCountSum)
fig8data$zseverity <- scale(fig8data$collSeverityMean)
colnames(fig8data) <- c("time", "victims", "severity", "zvictims", "zseverity")

# Note 1: The z-scores are calculated for the raw and trend values of the number of victims and mean collision severity. The reason is for enabling standardized scale comparison between the two variables in the plot.

# Note 2: We will use the z-score transformations both on the scaled (z = (x - mean(x)) / sd(x)) and inverse scaled (x = z * sd(x) + mean(x)) values of the raw and trend data for the number of victims and mean collision severity, in order to adjust the axes scales of the plot.

# Setting the plot parameters
options(repr.plot.width = 12, repr.plot.height = 8, repr.plot.res = 300, repr.plot.quality = 100, repr.plot.pointsize = 13, repr.plot.unit = "in")

# Create the time series ovelay plot for the weekly mean collision severity vs. number of victims
fig8 <- ggplot(fig8data, aes(x = time, y = victims)) +
    # First, add the Covid-19 restrictions area of interest annotation layer (behind everything else)
    annotate(
        'rect', 
        xmin = as_date("2020-03-01"), xmax = as_date("2022-03-01"), 
        ymin = -Inf, ymax = Inf, 
        alpha =.2, fill = "green") +
    # Add the covid-19 reference lines (left and right)
    geom_vline(xintercept = c(as_date("2020-03-01"), as_date("2022-03-01")),
               linewidth = 0.5,
               linetype = "dashed",
               color = "darkgreen") +
    # Add the covid-19 reference text annotation
    annotate("text", x = as_date("2020-03-01") + (as_date("2022-03-01") - as_date("2020-03-01")) / 2,
             y = -5,
             label = "COVID-19 Restrictions",
             fontface = "bold.italic",
             color = "darkgreen",
             size = 3.5
    ) + 
    # Add the time series line for the number of victims
    geom_line(aes(y = zvictims, color = "royalblue"), linewidth = 0.85, alpha = 0.4) +
    # Add the time series line for the mean severity rank
    geom_line(aes(y = zseverity, color = "darkorange"), linewidth = 0.85, alpha = 0.4) +
    # Add the smoothed LOESS trend line and 95% confidence intervals for the number of victims
    geom_smooth(method = "loess", se = TRUE, span = 0.2, formula = y ~ x, na.rm = TRUE, level = 0.95, aes(y = zvictims,  color = "navy"), fill = "royalblue", alpha = 0.4, linewidth = 1.5) +
    # Add the smoothed LOESS trend line and 95% confidence intervals for the mean severity rank
    geom_smooth(method = "loess", se = TRUE, span = 0.2, formula = y ~ x, na.rm = TRUE, level = 0.95, aes(y = zseverity, color = "red4"), fill = "darkorange", alpha = 0.4, linewidth = 1.5) +
    # Add the graph labels
    labs(x = "Date", y = "Number of Victims") +
    # General graph theme
    theme_hc() +
    #theme_economist() +
    theme(
        # general text settings
        text = element_text(size = 13, vjust = 0.5, hjust = 0.5, face = "plain"),
        # time axis labels
        axis.text.x = element_text(color = "black", size = 13, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        # Time axis title
        axis.title.x = element_text(color = "black", size = 15, angle = 0, hjust = .5, vjust = -2, face = "plain"),
        # Y axis labels (both)
        axis.text.y = element_text(color = "black", size = 13, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        # Victims axis title (left axis)
        axis.title.y.left = element_text(color = "navy", size = 15, angle = 90, hjust = .5, vjust = 1, face = "bold"),
        # Severity axis title (right axis)
        axis.title.y.right = element_text(color = "red4", size = 15, angle = 90, hjust = .5, vjust = 0, face = "bold"),
        # Adjust the x axis ticks
        #axis.ticks.length = unit(5, "pt"),
        axis.line.x.bottom = element_line(color = "black", size = 0.5),
        # Legend settings
        legend.title = element_text(color = "gray10", size = 13, face = "bold", hjust = 0, vjust = 0.5),
        #legend.title = element_blank(),
        legend.position = "inside",
        legend.position.inside = c(.03, .1), 
        legend.justification = "left",
        legend.text=element_text(size = 12, face = "plain"),
        legend.direction = "vertical", 
        legend.box = "horizontal",
        legend.background = element_rect(linetype = "solid", linewidth = 0.5, color = "gray50", fill = "whitesmoke"),
        # Adjust the grid lines for the graph
        #panel.grid.major.x = element_line(color = "azure", linewidth = 0.5),
        #panel.grid.major.y = element_line(color = "azure", linewidth = 0.5)
    ) +
    # Rescale the y-axis to the original scale (see Note 2 above)
    scale_y_continuous(
        labels = ~ round_any((. * sd(fig8data$victims)) + mean(fig8data$victims), 10) , 
        sec.axis = sec_axis(~ (. * sd(fig8data$severity)) + mean(fig8data$severity) , name = "Mean Severity Rank")) +
    scale_x_date(date_breaks = "1 year", date_labels = "%b\n%Y") +
    # Add and adjust options for the time series and trends legend
    scale_color_identity(
        name = "Time Series Legend",
        breaks = c("royalblue", "navy", "darkorange", "red4"),
        labels = c("Number of Victims", "Victims Loess Regression Trend (95% CI)", "Mean Severity Rank", "Severity Loess Regression Trend (95% CI)"),
        guide = "legend"
    ) +
    # Adjust the rows of the legends
    guides(color = guide_legend(nrow = 2, byrow = TRUE))

# Display figure 8
fig8


### Storage ####

# Save Figure 8 (weekly mean collision severity vs. number of victims) to disk
ggsave(filename = file.path(graphicsList$graphics$fig8$path, paste0(graphicsList$graphics$fig8$file, ".", graphicsList$graphics$fig8$fileformat)), plot = fig8, width = graphicsList$graphics$fig8$width, height = graphicsList$graphics$fig8$height, units = "in", dpi = graphicsList$graphics$fig8$resolution)


## 2.7. Figure 9 - Median Age for Parties and Victims ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 8 (weekly median age for parties and victims)
graphicsList <- graphicsEntry(listname = "graphicsList", type = 2, eid = 9, listattr = list(category = "Median Age Pyramid", name = "Median Age Pyramid and Correlation for Parties and Victims", description = "Pyramid plot and correlation matrix for median age for parties and victims in collision incidents", caption = "Visual representation of median age distribution for parties and victims of collision incidents. Left subgraph (a): median age pyramid plot for parties and victims of collision accidents. Right subgraph (b): Pearson correlation matrix between party and victim age groups in the collision incident data.", type = "time series", method = "ggplot2", fileformat = "png", file = "Median Age Distribution", status = "final"))


### Definition ####


# Left Subplot ~~~~~~~~~~~~~~~~~~~~~~

# Select the party and victim age from he collision data
fig9adata <- select(collisions, partyAge, victimAge)
# Create a table of the party and victim age
fig9adata <- data.frame(table(fig9adata$partyAge, fig9adata$victimAge))
# Change the column names
colnames(fig9adata) <- c("Party", "Victim", "Freq")
# Convert the party and victim columns to integers
fig9adata$Party <- as.integer(as.character(fig9adata$Party))
fig9adata$Victim <- as.integer(as.character(fig9adata$Victim))
# Remove all rows that are NA
fig9adata <- fig9adata[!is.na(fig9adata$Party),]
fig9adata <- fig9adata[!is.na(fig9adata$Victim),]
# Remove all rows with party or victim age > 100
fig9adata <- fig9adata[fig9adata$Party <= 100 | fig9adata$Victim <= 100,]

# Stack the party and victim columns into a single column with the type indicator
fig9adata <- melt(fig9adata, id.var = "Freq", variable.name = "Type")
# Change the column names
colnames(fig9adata) <- c("Freq", "Type", "Age")

abs_comma <- function (x, ...) {
    format(abs(x), ..., big.mark = ",", scientific = FALSE, trim = TRUE)
}

fig9a <- ggplot(
    fig9adata, 
    aes(
        x = Age, 
        fill = Type, 
        y = ifelse(
            test = Type == "Party", 
            yes = -Freq, 
            no = Freq
        )
    )
) + 
    geom_bar(stat = "identity") + 
    scale_y_continuous(
        labels = abs_comma,
        #limits = max(fig9adata$Freq) * c(-1,1)
    ) + 
    scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, by=20)) +
    coord_flip() + 
    theme_hc() +
    theme(
        text = element_text(color = "black", size = 12),
        plot.title = element_text(color = "black", size = 14, face = "plain", hjust = 0.5, vjust = 0.5),
        axis.text.x = element_text(color = "black", size = 12, angle = 0, hjust = 0.5, vjust = 0.5),
        axis.title.x = element_text(color = "black", size = 14, angle = 0, hjust = 0.5, vjust = 0.5),
        axis.text.y = element_text(color = "black", size = 12, angle = 0, hjust = 0.5, vjust = 0.5),
        axis.title.y = element_text(color = "black", size = 14, angle = 90, hjust = 0.5, vjust = 0.5),
        axis.line.x = element_line(color = "black", size = 0.5, linetype = "solid"),
        axis.line.y = element_blank(),
        legend.position = "inside",
        legend.position.inside = c(0.9, 0.9)
    ) +
    labs(
        x = "Age", 
        y = "Collisions", 
        fill = "Age", 
        title = "Median Age Pyramid for Parties and Victims of Collisions"
    ) +
    scale_color_identity(
        name = "Type",
        breaks = c("royalblue", "darkorange"),
        labels = c("Party Age", "VictimAge"),
        guide = "legend"
    )

fig9a


# Right Subplot ~~~~~~~~~~~~~~~~~~~~~~

# correlation matrix between partyAgeGroup and victimAgeGroup in the collisions data
fig9bdata <- data.frame(collisions.agp$partyAgeGroup, collisions.agp$victimAgeGroup)

# Change the column names
colnames(fig9bdata) <- c("party", "victim")

# Create a table of the party and victim age
fig9bdata <- table(fig9bdata$party, fig9bdata$victim)
head(fig9bdata)

# Get lower triangle of the correlation matrix
getLowerTri<-function(cormat){
    cormat[upper.tri(cormat)] <- NA
    return(cormat)
}

# Get upper triangle of the correlation matrix
getUpperTri <- function(cormat){
    cormat[lower.tri(cormat)]<- NA
    return(cormat)
}

# Create a correlation matrix
fig9bcormat <- round(cor(fig9bdata), 2)

# Melt the correlation matrix
fig9bmeltedCormat <- melt(getUpperTri(fig9bcormat), na.rm = TRUE)

# Change the column names
colnames(fig9bmeltedCormat) <- c("Party", "Victim", "Correlation")
head(fig9bmeltedCormat)


# Create a ggheatmap
fig9b <- ggplot(fig9bmeltedCormat, aes(x = Victim, Party, fill = Correlation))+
    geom_tile(color = "white")+
    labs(
        title = "Correlation Matrix of Party and Victim Age Groups",
         x = "Victim Age Group",
         y = "Party Age Group") +
    scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                         midpoint = 0, limit = c(-1,1), space = "Lab", 
                         name="Pearson\nCorrelation") +
    theme_hc()+
    coord_fixed() +
    geom_text(aes(x = Victim, y = Party, label = Correlation), color = "black", size = 4) +
    theme(
        text = element_text(color = "black", size = 11),
        plot.title = element_text(color = "black", size = 14, face = "plain", hjust = 0.5, vjust = 0.5),
        axis.text.x = element_text(color = "black", size = 12, angle = 45, hjust = 0.5, vjust = 0.8),
        axis.title.x = element_text(color = "black", size = 14, angle = 0, hjust = 0.5, vjust = 0.5),
        axis.text.y = element_text(color = "black", size = 12, angle = 0, hjust = 0.5, vjust = 0.5),
        axis.title.y = element_text(color = "black", size = 14, angle = 90, hjust = 0.5, vjust = 0.5),
        axis.line.x = element_blank(),
        axis.line.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.major.y = element_blank(),
        panel.border = element_blank(),
        panel.background = element_blank(),
        axis.ticks = element_blank(),
        legend.justification = c(1, 0),
        legend.position = "inside",
        legend.position.inside = c(0.6, 0.7),
        legend.direction = "horizontal") +
    guides(fill = guide_colorbar(barwidth = 7, barheight = 1, title.position = "top", title.hjust = 0.5))

fig9b


# Combined Plot ~~~~~~~~~~~~~~~~~~~~~~

# add fig8a and fig8b to a single plot, side by side
fig9 <- plot_grid(fig9a, fig9b, labels = c("(a)", "(b)"), ncol = 2, align = "h", axis = "t", label_size = 14, rel_widths = c(1.2, 1))


# Display the combined plot
fig9


### Storage ####

# Save Figure 9 (weekly median age for parties and victims) to disk
ggsave(filename = file.path(graphicsList$graphics$fig9$path, paste0(graphicsList$graphics$fig9$file, ".", graphicsList$graphics$fig9$fileformat)), plot = fig9, width = graphicsList$graphics$fig9$width, height = graphicsList$graphics$fig9$height, units = "in", dpi = graphicsList$graphics$fig9$resolution)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Saving the Data and Graphics ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Save the data and graphics list to the R data directory
saveToDisk()

setwd(prjDirs$prjPath)
getwd()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF SCRIPT ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
