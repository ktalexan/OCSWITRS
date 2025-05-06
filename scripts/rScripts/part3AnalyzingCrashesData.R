#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OCSWITRS R Data ANALYSIS #
# PART 3: ANALYZING AND VISUALIZING MAIN DATA ####
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

# Open the R Libraries master file (located in Obsidian's library folder) - Already defined in the project_directories function
#libMaster = file.path(Sys.getenv("HOME"), "Knowledge Management", "Documents", "Data Science", "RPackagesInstallation.R")
#file.edit(libMaster)


## 1.2. Import Libraries ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load the pacman library. If not installed, install it first.
if (!requireNamespace("pacman", quietly = TRUE)) {
    install.packages("pacman")
}
library(pacman)

# Load the required libraries using pacman
pacman::p_load(RColorBrewer, lubridate, jsonlite, dplyr, magrittr, R6, haven, labelr, plyr, stringr, purrr, glue, Hmisc, psych, tibble, here, tidyr, chattr, knitr, labelled, ggplot2, ggthemes, gtsummary, gt, vtable, stargazer, scales, pastecs, collapse, formattable, xtable, sf, sp, arcgisutils)


## 1.3. Load Project functions ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

getwd()

# Load the project functions from the RData file located in the /Data/R directory
load(file = file.path(getwd(), "scripts", "rData", "projectFunctions.RData"))


## 1.4. Load Metadata and Directories ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the metadata
metadata <- projectMetadata(part = 3)

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

# load the codebook file
load(file = file.path(prjDirs$codebookPath, "cb.RData"))

### Set Graphics Directory ####

# Set the working directory to the graphics folder
setwd(prjDirs$graphicsPath)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Data Analysis ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 2.1. Table 1 - Collision Severity Stats ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Table 1
graphicsList <- graphicsEntry(
    listName = "graphicsList",
    type = 1,
    eid = 1,
    listAttr = list(
        name = "Collision severity ordinal statistics",
        description = "Key statistics of the collision severity variable",
        caption = "Collision severity ordinal classification and OCSWITRS dataset counts",
        method = "gtsummary",
        fileFormat = ".tex",
        file = "Collision Severity Stats",
        status = "final"
    )
)


### Definition ####

# Create a summary table of the collision severity by parties and victims per crash

# Create a data frame for the crashes data by severity
df1 <- data.frame(Severity = as_factor(crashes$collSeverity), Crashes = crashes$crashTag)

# Create a summary table of the crashes by severity
x1 <- select(rbind(
    describeBy(Crashes ~ Severity, data = df1, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2),
    describeBy(df1$Crashes, group = df1$Crashes, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2)), item, group1, n)
# Rename the item value for the total
x1$item[x1$group1 == "1"] <- 5
# Rename the group value for the total
x1$group1[x1$group1 == "1"] <- "Total"
# Set the row names to the item value
rownames(x1) <- x1$item
# Set the column names
colnames(x1) <- c("Code", "Severity", "CrashesN")

# Create a data frame for the parties data by severity
df2 <- data.frame(
    Severity = as_factor(collisions$collSeverity[collisions$partyTag == 1]),
    Parties = collisions$partyTag[collisions$partyTag == 1],
    PartyCount = collisions$partyCount[collisions$partyTag == 1]
)

# Create a summary table of the parties by severity
x2 <- select(rbind(
    describeBy(PartyCount ~ Severity, data = df2, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2),
    describeBy(df2$PartyCount, group = df2$Parties, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2)), item, group1, n, mean, sd, min, max)
# Rename the item value for the total
x2$item[x2$group1 == "1"] <- 5
# Rename the group value for the total
x2$group1[x2$group1 == "1"] <- "Total"
# Set the row names to the item value
rownames(x2) <- x2$item
# Set the column names
colnames(x2) <- c("Code", "Severity", "PartiesN", "PartiesMean", "PartiesSD", "PartiesMin", "PartiesMax")

# Create a range column for the parties
x2$PartiesRange <- paste(x2$PartiesMin, x2$PartiesMax, sep = "--")
# Remove the min and max columns
x2$PartiesMin <- NULL
x2$PartiesMax <- NULL

# Create a data frame for the victims data by severity
df3 <- data.frame(
    Severity = as_factor(collisions$collSeverity[collisions$victimTag == 1]),
    Victims = collisions$victimTag[collisions$victimTag == 1],
    VictimCount = collisions$victimCount[collisions$victimTag == 1]
)

# Create a summary table of the victims by severity
x3 <- select(rbind(describeBy(VictimCount ~ Severity, data = df3, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2), describeBy(df3$VictimCount, group = df3$Victims, mat = TRUE, fast = TRUE, na.rm = TRUE, digits = 2)), item, group1, n, mean, sd, min, max)
# Rename the item value for the total
x3$item[x3$group1 == "1"] <- 5
# Rename the group value for the total
x3$group1[x3$group1 == "1"] <- "Total"
# Set the row names to the item value
rownames(x3) <- x3$item
# Set the column names
colnames(x3) <- c("Code", "Severity", "VictimsN", "VictimsMean", "VictimsSD", "VictimsMin", "VictimsMax")

# Create a range column for the victims
x3$VictimsRange <- paste(x3$VictimsMin, x3$VictimsMax, sep = "--")
# Remove the min and max columns
x3$VictimsMin <- NULL
x3$VictimsMax <- NULL

# Merge the tables into the final table
tbl1Data <- merge(merge(x1, x2, by = c("Code", "Severity"), all = TRUE), x3, by = c("Code", "Severity"), all = TRUE)
# Remove the code column
tbl1Data$Code <- NULL

# Conduct Nonparametric Rank Tests

# Perform the chi-square and Kruskal-Wallis tests for the crashes, parties, and victims by severity
tbl1Tests <- data.frame(
    list(
        "Severity" = "p-value",
        "Crashes" = pValueDisplay(chisq.test(table(df1$Crashes, df1$Severity))$p.value),
        "Parties" = pValueDisplay(chisq.test(table(df2$Parties, df2$Severity))$p.value),
        "Victims" = pValueDisplay(chisq.test(table(df3$Victims, df3$Severity))$p.value),
        "PartyCount" = pValueDisplay(kruskal.test(PartyCount ~ Severity, data = df2)$p.value),
        "VictimCount" = pValueDisplay(kruskal.test(VictimCount ~ Severity, data = df3)$p.value)
    )
)

# Remove the intermediary data frames and individual tables
rm(df1, df2, df3, x1, x2, x3)

# Move the Parties and Victims columns to the right of the Crashes column
tbl1Data <- tbl1Data %>% relocate(c(PartiesN, VictimsN), .after = CrashesN)

# Rename the columns of the final table
colnames(tbl1Data) <- c("Severity", "Crashes", "Parties", "Victims", "PartiesMean", "PartiesSD", "PartiesRange", "VictimsMean", "VictimsSD", "VictimsRange")

# Define the table headers
tbl1AddToRow <- list(pos = list(0, 4, 5), command = c(
    "\\multirow{2}{*}{Severity Level} & \\multicolumn{1}{c}{\\multirow{2}{*}{Crashes}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Parties}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Victims}} & \\multicolumn{3}{c}{Party Count\\footnotemark[1]} & \\multicolumn{3}{c}{Victim Count\\footnotemark[1]} \\\\ \n \\cmidrule{5-7}\\cmidrule{8-10} \n & & & & \\textit{mean} & \\textit{sd} & \\textit{range} & \\textit{mean} & \\textit{sd} & \\textit{range} \\\\ \n",
    "\\midrule \n",
    paste0("\\textit{", tbl1Tests$Severity[1], "} & $", tbl1Tests$Crashes[1], "$\\footnotemark[2] & $", tbl1Tests$Parties[1], "$\\footnotemark[2] & $", tbl1Tests$Victims[1], "$\\footnotemark[2] & \\multicolumn{3}{c}{$", tbl1Tests$PartyCount[1], "$\\footnotemark[3]} & \\multicolumn{3}{c}{$", tbl1Tests$VictimCount[1], "$\\footnotemark[3]} \\\\ \n"))
)

# Define footnotes for the table
tbl1Footnotes <- data.frame("footnotes" = c("\\footnotetext[1]{Per each collision: \\textit{mean, sd, range(min, max)}}", "\\footnotetext[2]{Pearson's Chi-Squared test}", "\\footnotetext[3]{Kruskal-Wallis rank sum test}"))


### Display and Storage ####

# Convert the table to a latex table and save it to disk
print(
    xtable(
        tbl1Data,
        caption = graphicsList$tables$tbl1$caption,
        label = graphicsList$tables$tbl1$id,
        digits = 2,
        auto = TRUE
    ),
    type = "latex",
    file = paste0(graphicsList$tables$tbl1$file, graphicsList$tables$tbl1$fileFormat),
    append = FALSE,
    floating = TRUE,
    floating.environment = 'table',
    table.placement = "h",
    caption.placement = "top",
    caption.width = NULL,
    latex.environments = "center",
    tabular.environment = "tabular",
    size = NULL,
    NA.string = "",
    include.rownames = FALSE,
    include.colnames = FALSE,
    only.contents = FALSE,
    add.to.row = tbl1AddToRow,
    sanitize.text.function = NULL,
    sanitize.rownames.function = NULL,
    sanitize.colnames.function = NULL,
    math.style.negative = FALSE,
    math.style.exponents = FALSE,
    print.results = TRUE,
    format.args = list(big.mark = ","),
    rotate.rownames = FALSE,
    rotate.colnames = FALSE,
    booktabs = TRUE,
    scalebox = NULL,
    width = NULL,
    comment = TRUE,
    timestamp = date()
)

# Convert the table 1 footnotes to a latex table and add it to disk
print(
    xtable(tbl1Footnotes),
    type = "latex",
    file = paste0(graphicsList$tables$tbl1$file, graphicsList$tables$tbl1$fileFormat),
    append = TRUE,
    include.rownames = FALSE,
    only.contents = TRUE,
    sanitize.text.function = identity,
    tabular.environment = "tabular",
    booktabs = TRUE,
    comment = FALSE,
    timestamp = NULL
)

# Save the table data frame to the rDataPath directory
save(tbl1Data, tbl1Tests, tbl1AddToRow, tbl1Footnotes, file = file.path(prjDirs$rDataPath, "tbl1Data.RData"))


## 2.2. Table 2 - Ranked Collision Severity Stats ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Table 2
graphicsList <- graphicsEntry(listName = "graphicsList", type = 1, eid = 2, listAttr =  list(name = "Collision severity rank classification statistics", description = "Key classification and statistics of the collision severity rank variable", caption = "Ranked collision severity ordinal classification, related parameters, and OCSWITRS dataset counts", method = "gtsummary", fileFormat = ".tex", file = "Collision Severity Rank Stats", status = "final"))


### Definition ####

# Select the variables for the table
tbl2Data <- data.frame(collisions[, c("crashTag", "partyTag", "victimTag", "collSeverityRank")])

# rename the column names
colnames(tbl2Data) <- c("Crashes", "Parties", "Victims", "Severity")

# Create a temp data frame for the total counts of crashes, parties, and victims
temp <- data.frame("Rank" = as.integer(10), "Level" = NA, "Crashes" = round(sum(tbl2Data$Crashes), 0), "Parties" = round(sum(tbl2Data$Parties), 0), "Victims" = round(sum(tbl2Data$Victims), 0))

# Loop through each of the ranked severity levels and add their sum of crashes, parties, and victims to the temp data frame
for (i in 0:8) {
    temp <- rbind(temp,
        list(
            "Rank" = as.integer(i),
            "Level" = as.character(levels(as_factor(tbl2Data$Severity))[i + 1]),
            "Crashes" = round(sum(tbl2Data[tbl2Data$Severity == i, ]$Crashes), 0),
            "Parties" = round(sum(tbl2Data[tbl2Data$Severity == i, ]$Parties), 0),
            "Victims" = round(sum(tbl2Data[tbl2Data$Severity == i, ]$Victims), 0)
        )
    )
}
rm(i)

# convert the temp data frame columns severity_rank, crashTag, partyTag, victimTag to integers
temp$Rank <- as.integer(temp$Rank)
temp$Crashes <- as.integer(temp$Crashes)
temp$Parties <- as.integer(temp$Parties)
temp$Victims <- as.integer(temp$Victims)

# sort the rows of temp data frame by the severity_rank column
temp <- temp[order(temp$Rank), ]

# reset the index of the temp data frame
rownames(temp) <- temp$Rank

# replace the value of
temp$Rank[10] <- "Total"

# Perform the chi-square and Kruskal-Wallis tests for the crashes, parties, and victims by severity
tbl2Tests <- data.frame(list(
    "Severity" = "p-value",
    "Crashes" = pValueDisplay(chisq.test(table(tbl2Data$Crashes, tbl2Data$Severity))$p.value),
    "Parties" = pValueDisplay(chisq.test(table(tbl2Data$Parties, tbl2Data$Severity))$p.value),
    "Victims" = pValueDisplay(chisq.test(table(tbl2Data$Victims, tbl2Data$Severity))$p.value)
))

# Replace the original tbl2Data with the temp data frame
tbl2Data <- temp

# Remove the temp data frame and the loop index
rm(temp)

tbl2Data$Fatalities <- NA
tbl2Data$Injuries <- NA
tbl2Data$Type <- NA

# if tbl2Data$rank is 0
tbl2Data$Fatalities[tbl2Data$Rank == 0] <- "None"
tbl2Data$Injuries[tbl2Data$Rank == 0] <- "None"
tbl2Data$Type[tbl2Data$Rank == 0] <- "Minor"

# if tbl2Data$rank is 1
tbl2Data$Fatalities[tbl2Data$Rank == 1] <- "None"
tbl2Data$Injuries[tbl2Data$Rank == 1] <- "Single"
tbl2Data$Type[tbl2Data$Rank == 1] <- "Severe"

# if tbl2Data$rank is 2
tbl2Data$Fatalities[tbl2Data$Rank == 2] <- "None"
tbl2Data$Injuries[tbl2Data$Rank == 2] <- "Multiple"
tbl2Data$Type[tbl2Data$Rank == 2] <- "Severe"

# if tbl2Data$rank is 3
tbl2Data$Fatalities[tbl2Data$Rank == 3] <- "Single"
tbl2Data$Injuries[tbl2Data$Rank == 3] <- "None"
tbl2Data$Type[tbl2Data$Rank == 3] <- "Fatal"

# if tbl2Data$rank is 4
tbl2Data$Fatalities[tbl2Data$Rank == 4] <- "Single"
tbl2Data$Injuries[tbl2Data$Rank == 4] <- "Single"
tbl2Data$Type[tbl2Data$Rank == 4] <- "Fatal"

# if tbl2Data$rank is 5
tbl2Data$Fatalities[tbl2Data$Rank == 5] <- "Single"
tbl2Data$Injuries[tbl2Data$Rank == 5] <- "Multiple"
tbl2Data$Type[tbl2Data$Rank == 5] <- "Fatal"

# if tbl2Data$rank is 6
tbl2Data$Fatalities[tbl2Data$Rank == 6] <- "Multiple"
tbl2Data$Injuries[tbl2Data$Rank == 6] <- "None"
tbl2Data$Type[tbl2Data$Rank == 6] <- "Fatal"

# if tbl2Data$rank is 7
tbl2Data$Fatalities[tbl2Data$Rank == 7] <- "Multiple"
tbl2Data$Injuries[tbl2Data$Rank == 7] <- "Single"
tbl2Data$Type[tbl2Data$Rank == 7] <- "Fatal"

# if tbl2Data$rank is 8
tbl2Data$Fatalities[tbl2Data$Rank == 8] <- "Multiple"
tbl2Data$Injuries[tbl2Data$Rank == 8] <- "Multiple"
tbl2Data$Type[tbl2Data$Rank == 8] <- "Fatal"

# Relocate the Fatalities, Injuries, and Type columns after the Level column
tbl2Data <- tbl2Data %>% relocate(c(Fatalities, Injuries, Type), .after = Level)

# Define the table headers
tbl2AddToRow <- list(pos = list(0, 9, 10), command = c(
    "\\multicolumn{2}{c}{Rank and Level} & Fatalities & Injuries & Type & Crashes & Parties & Victims \\\\ \n",
    "\\midrule \n",
    paste0("\\textit{", tbl2Tests$Severity[1], "}\\footnotemark[1] &  &  &  &  & $", tbl2Tests$Crashes[1], "$ & $", tbl2Tests$Parties[1], "$ & $", tbl2Tests$Victims[1], "$ \\\\ \n"))
)

# Define footnotes for the table
tbl2Footnotes <- data.frame("footnotes" = c("\\footnotetext[1]{Pearson's Chi-Squared test}"))


### Display and Storage ####

# Convert the table to a latex table and save it to disk
print(
    xtable(
        tbl2Data,
        caption = graphicsList$tables$tbl2$caption,
        label = graphicsList$tables$tbl2$id,
        digits = 0,
        auto = TRUE
    ),
    type = "latex",
    file = paste0(graphicsList$tables$tbl2$file, graphicsList$tables$tbl2$fileFormat),
    append = FALSE,
    floating = TRUE,
    floating.environment = 'table',
    table.placement = "h",
    caption.placement = "top",
    caption.width = NULL,
    latex.environments = "center",
    tabular.environment = "tabular",
    size = NULL,
    NA.string = "",
    include.rownames = FALSE,
    include.colnames = FALSE,
    only.contents = FALSE,
    add.to.row = tbl2AddToRow,
    sanitize.text.function = NULL,
    sanitize.rownames.function = NULL,
    sanitize.colnames.function = NULL,
    math.style.negative = FALSE,
    math.style.exponents = FALSE,
    print.results = TRUE,
    format.args = list(big.mark = ","),
    rotate.rownames = FALSE,
    rotate.colnames = FALSE,
    booktabs = TRUE,
    scalebox = NULL,
    width = NULL,
    comment = TRUE,
    timestamp = date()
)

# Convert the table 2 footnotes to a latex table and add it to disk
print(
    xtable(tbl2Footnotes),
    type = "latex",
    file = paste0(graphicsList$tables$tbl2$file, graphicsList$tables$tbl2$fileFormat),
    append = TRUE,
    include.rownames = FALSE,
    only.contents = TRUE,
    sanitize.text.function = identity,
    tabular.environment = "tabular",
    booktabs = TRUE,
    comment = FALSE,
    timestamp = NULL
)

# Save the table data frame to the rDataPath directory
save(tbl2Data, tbl2Tests, tbl2AddToRow, tbl2Footnotes, file = file.path(prjDirs$rDataPath, "tbl2Data.RData"))


## 2.3. Figure 1 - Histogram - Victim Count ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 1
graphicsList <- graphicsEntry(listName = "graphicsList", type = 2, eid = 1, listAttr = list(category = "histogram", name = "Histogram of victim count in crashes", description = "Histogram plot of the number of victims in crash incidents", caption = "Top-10 victim frequency counts of the number of victims in collision accidents", type = "frequency", method = "ggplot2", fileFormat = ".png", file = "Histogram Victim Count", status = "final"))


### Definition ####

# Define a histogram for the top 10 victim frequency counts
fig1 <- ggplot(
    data.frame(x = crashes$victimCount[crashes$victimCount >= 1 & crashes$victimCount <= 10]), aes(x)) +
    geom_histogram(binwidth = 1, center = 1, bins = 10, fill = "darkred", color = "white", linewidth = 1, na.rm = TRUE) +
    stat_bin(binwidth = 1, geom = "text", aes(label = format(after_stat(count), big.mark = ",")), vjust = -0.5, pad = TRUE, size = 5) +
    scale_y_continuous(labels = comma_format(accuracy = 1), breaks = seq(0, 120000, by = 20000)) +
    scale_x_continuous(breaks = seq(1, 10, by = 1)) +
    labs(x = "Victim Count", y = "Number of Victims in Crash Incidents", caption = "Note: Top 10 victim frequency counts") +
    theme_hc() +
    theme(
        text = element_text(size = 14, vjust = 0.5, hjust = 0.5, face = "plain"),
        axis.title.y = element_text(color = "black", size = 16, angle = 90, hjust = 0.5, vjust = 2, face = "plain"),
        axis.text.y = element_text(color = "black", size = 15, angle = 90, vjust = 0.5, hjust = 0.5, face = "plain"),
        axis.title.x = element_text(color = "black", size = 16, angle = 0, hjust = 0.5, vjust = 0, face = "plain"),
        axis.text.x = element_text(color = "black", size = 15, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        axis.line.x.bottom = element_line(color = "black", linewidth = 0.5),
        plot.caption = element_text(color = "black", hjust = 0, size = 13, face = "italic"),
        #panel.background = element_rect(fill = "#e1ecf4"),
        #panel.grid.major = element_line(color = "#e1ecf4")
    )


# Display the histogram
fig1


### Storage ####

# Save the histogram to a PNG file
ggsave(filename = file.path(graphicsList$graphics$fig1$path, paste0(graphicsList$graphics$fig1$file, graphicsList$graphics$fig1$fileFormat)), plot = fig1, width = graphicsList$graphics$fig1$width, height = graphicsList$graphics$fig1$height, units = "in", dpi = graphicsList$graphics$fig1$resolution)


## 2.4. Figure 2 - Bar Chart-Type of Collision ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 2
graphicsList <- graphicsEntry(listName = "graphicsList", type = 2, eid = 2, listAttr = list(category = "bar", name = "Bar graph of collision types", description = "Bar graph of the number of collisions by type of collision", caption = "Number of collisions by collision type", type = "distribution", method = "ggplot2", fileFormat = ".png", file = "Bar Type of Collision", status = "final"))


### Definition ####

# Create a table of the type of collision as a factor
fig2Data <- table(as_factor(crashes$typeOfColl))
# Convert the table to a data frame
fig2Data <- as.data.frame(fig2Data)
# Change the names of the columns
colnames(fig2Data) <- c("CollisionType", "Count")

# select all the categories for the typeOfCollision in test that they are not "Not Stated"
fig2Data[fig2Data$CollisionType != "Not Stated", ]

# create a bar graph of the test data
fig2 <- ggplot(fig2Data[fig2Data$CollisionType != "Not Stated", ], aes(x = CollisionType, y = Count, fill = CollisionType)) +
    geom_bar(stat = "identity") +
    geom_text(aes(label = format(Count, big.mark = ",")), vjust = -0.5, size = 5) +
    labs(
        x = "Crash Type",
        y = "Number of Collisions",
        title = "Type of Collision by Count"
    ) +
    theme_hc() +
    scale_fill_brewer(palette = "Dark2") +
    #scale_fill_wsj() +
    #scale_fill_economist() +
    theme(
        plot.title = element_text(color = "black", size = 16, face = "plain"),
        axis.title.y = element_text(color = "black", size = 16, hjust = 0.5, vjust = 2, face = "plain"),
        axis.text.y = element_text(color = "black", angle = 90, size = 14, vjust = 0.5, hjust = 0.5, face = "plain"),
        axis.title.x = element_text(color = "black", size = 16, hjust = 0.5, vjust = 0, face = "plain"),
        axis.text.x = element_text(color = "black", angle = 0, size = 14, hjust = 0.5, vjust = 0.5, face = "plain"),
        legend.title = element_blank(),
        legend.position = "inside",
        legend.position.inside = c(.98, .9),
        #legend.position = "top",
        legend.justification = "right",
        legend.text = element_text(color = "black", size = 13, face = "plain"),
        legend.background = element_rect(fill = "white", colour = 0.5)
    ) +
    guides(fill = guide_legend(nrow = 4, byrow = TRUE)) +
    scale_y_continuous(labels = comma_format(accuracy = 1), breaks = seq(0, 60000, by = 10000)) +
    scale_x_discrete(labels = function(x) str_wrap(x, width = 5)) +
    scale_color_brewer(palette = "Accent")
# if needed to wrap the labels on the x axis
# theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5))
# "#cae3eb", "#c0e1eb"
# Display the bar graph
fig2

### Storage ####

# Save the bar graph to a PNG file
ggsave(filename = file.path(graphicsList$graphics$fig2$path, paste0(graphicsList$graphics$fig2$file, graphicsList$graphics$fig2$fileFormat)), plot = fig2, width = graphicsList$graphics$fig2$width, height = graphicsList$graphics$fig2$height, units = "in", dpi = graphicsList$graphics$fig2$resolution)


## 2.5. Figure 3 - Bar Chart-Fatal Accidents ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Figure 3
graphicsList <- graphicsEntry(listName = "graphicsList", type = 2, eid = 3, listAttr = list(category = "bar", name = "Cumulative Bars of Number of Fatalities by Type ", description = "Cumulative Bar graph of the number of fatal collisions by type", caption = "Number of fatal collisions by type of fatality", type = "distribution", method = "ggplot2", fileFormat = ".png", file = "Cumulative Number of Fatalities", status = "final"))


### Definition ####

# convert tsYear$dateYear from date to year
as.numeric(format(tsYear$dateYear, "%Y"))


# from the tsYear data frame, select the dtYear, countCarKilledSum, countPedKilledSum, countBicKilledSum, and countMcKilledSum columns
fig3Data <- select(tsYear, dateYear, countCarKilledSum, countPedKilledSum, countBicKilledSum, countMcKilledSum)
fig3Data$dateYear <- as.numeric(format(tsYear$dateYear, "%Y"))
colnames(fig3Data) <- c("Year", "Car", "Pedestrian", "Bicycle", "Motorcycle")

# pivot_longer() function to convert the data frame from wide to long format
fig3Data <- fig3Data %>%
    pivot_longer(cols = -Year)

# Create a cumulative bar chart for the number of fatal accidents by type of collision
fig3 <- ggplot(fig3Data, aes(x = Year, y = value, fill = name)) +
    geom_col(position = position_stack(reverse = TRUE)) +
    geom_text(aes(label = value), position = position_stack(reverse = TRUE, vjust = 0.5), size = 5) +
    labs(x = "Year", y = "Number of Fatalities", title = "Number of Fatalities by Type and Year", caption = "Notes: (a) Stacked bars of number of fatal accidents; (b) bar labels represent category counts") +
    theme_hc() +
    theme(
        plot.title = element_text(size = 16, face = "plain"),
        text = element_text(color = "black", size = 13),
        axis.title.y = element_text(color = "black", size = 15, angle = 90, hjust = 0.5, vjust = 2, face = "plain"),
        axis.text.y = element_text(color = "black", size = 13, angle = 90, vjust = 0.5, hjust = 0.5, face = "plain"),
        axis.title.x = element_text(color = "black", size = 15, angle = 0, hjust = 0.5, vjust = 0, face = "plain"),
        axis.text.x = element_text(color = "black", size = 13, angle = 0, hjust = 0.5, vjust = 0.5, face = "plain"),
        axis.line.x.bottom = element_line(color = "black", size = 0.5),
        legend.title = element_blank(),
        legend.position = "top",
        legend.justification = "right",
        legend.text = element_text(color = "black", size = 13, face = "plain"),
        plot.caption = element_text(color = "black", hjust = 0, vjust = -2, size = 13, face = "italic")
    ) +
    scale_x_continuous(breaks = seq(2013, 2024, by = 1)) +
    scale_color_brewer(palette = "Accent")

# Display the bar chart
fig3


### Storage ####

# Save the bar graph to a PNG file
ggsave(filename = file.path(graphicsList$graphics$fig3$path, paste0(graphicsList$graphics$fig3$file, graphicsList$graphics$fig3$fileFormat)), plot = fig3, width = graphicsList$graphics$fig3$width, height = graphicsList$graphics$fig3$height, units = "in", dpi = graphicsList$graphics$fig3$resolution)


## 2.6. Tables 3-4 - Monthly Collision Stats ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Table 3
graphicsList <- graphicsEntry(listName = "graphicsList", type = 1, eid = 3, listAttr = list(name = "Monthly Accident Summary Statistics", description = "Key accident statistics for the summary variables in the OCSWITRS datasets", caption = "Summary total values for monthly time series of traffic accidents in Orange County (2012-2024)", method = "stat.desc", fileFormat = ".tex", file = "Monthly Summary Stats", status = "final"))

# Add graphics metadata for Table 4
graphicsList <- graphicsEntry(listName = "graphicsList", type = 1, eid = 4, listAttr = list(name = "Monthly Accident Average and Median Statistics", description = "Key statistics for the average and median variable values in the OCSWITRS datasets", caption = "Average and median values for monthly time series of traffic accidents in Orange County (2012-2024)", method = "stat.desc", fileFormat = ".tex", file = "Monthly Average Stats", status = "final"))


### Definition ####

# Create a data frame with monthly statistics
statsMonth <- data.frame(t(stat.desc(tsMonth, norm = TRUE, p = 0.95)))

# add a column in statsMonth with the row names
statsMonth$var.name <- rownames(statsMonth)

# add a column in stats month that has value of "mean" if the rowName ends with "Mean", "median" if the rowName ends with "Median", "sum" if the rowName ends with "Sum", "sd" if the rowName ends with "Sd", "min" if the rowName ends with "Min", "max" if the rowName ends with "Max"
statsMonth$stat.type <- ifelse(grepl("Mean$", statsMonth$var.name), "mean",
    ifelse(grepl("Median$", statsMonth$var.name), "median",
        ifelse(grepl("Sum$", statsMonth$var.name), "sum",
            ifelse(grepl("Sd$", statsMonth$var.name), "sd",
                ifelse(grepl("Min$", statsMonth$var.name), "min",
                    ifelse(grepl("Max$", statsMonth$var.name), "max",
                        ifelse(grepl("^dt_", statsMonth$var.name), "datetime", NA)
                    )
                )
            )
        )
    )
)

# remove everything before the first "_" in the rownames of statsMonth
statsMonth$var.name <- sub("^[^_]*_", "", statsMonth$var.name)

# order the columns in the statsMonth data frame using this order: stat.type, var.name, nbr.val, nbr.null, nbr.na, sum, min, max, range, median, mean, SE.mean, CI.mean.0.95, std.dev, var, coef.var, skewness, skew.2SE, kurtosis, kurt.2SE, normtest.W, normtest.p
statsMonth <- statsMonth[, c("stat.type", "var.name", "nbr.val", "nbr.null", "nbr.na", "sum", "min", "max", "range", "median", "mean", "SE.mean", "CI.mean.0.95", "std.dev", "var", "coef.var", "skewness", "skew.2SE", "kurtosis", "kurt.2SE", "normtest.W", "normtest.p")]


#### Table 3 ####

# Table 3 contains the statistics for the sum variables in the monthly time series data
# create a subset of the statsMonth that contains only the rows that end with "Sum"
tbl3Data <- statsMonth[grep("Sum$", rownames(statsMonth)), ]

# Keep only the columns sum, min, max, mean, std.dev, SE.mean, CI.mean.0.95
tbl3Data <- tbl3Data[, c("stat.type", "sum", "min", "max", "mean", "std.dev", "SE.mean", "CI.mean.0.95")]

# reorder the columns of the statsMonth_sum in this order: sum, min, max, mean, std.dev, SE.mean, CI.mean.0.95
tbl3Data <- tbl3Data[, c("stat.type", "sum", "min", "max", "mean", "std.dev", "SE.mean", "CI.mean.0.95")]

# round the values in the statsMonth data frame
# Integers, no decimal places
for (i in c("sum", "min", "max")) {
    tbl3Data[, i] <- round(tbl3Data[, i], 0)
}
# Decimals, 2 decimal places
for (i in c("mean", "std.dev", "SE.mean", "CI.mean.0.95")) {
    tbl3Data[, i] <- round(tbl3Data[, i], 2)
}

# Define the labels of the table rows
tbl3Data$label <- c("Crashes", "Rush Hours", "Severity", "Severe Crashes", "Fatal Crashes", "Multiple Victim Crashes", "Parties", "Victims", "Killed", "Injured", "Severe Injuries", "Fatal or Severe Injuries", "Visible Injuries", "Complaint of Pain", "Minor or Pain Injuries", "Killed in Cars", "Injured in Cars", "Killed Pedestrians", "Injured Pedestrians", "Killed Bicyclists", "Injured Bicyclists", "Killed Motorcyclists", "Injured Motorcyclists", "Pedestrian Accident", "Bicycle Accident", "Motorcycle Accident", "Truck Accident", "Hit and Run", "Alcohol Involved", "Distance", "Intersection", "Control Device", "State Highway", "Tow Away", "Party Tag", "At Fault", "Party Race", "Parties Killed", "Parties Injured", "Party Sobriety", "DUI Alcohol", "Party Drug Physical", "DUI Drugs", "Victim Tag", "Victim Degree of Injury")

# Define the order of display of the table rows
tbl3Data$order <- c(1, 31, 105, 5, 4, 6, 2, 3, 11, 12, 15, 13, 16, 17, 14, 18, 22, 19, 23, 20, 24, 21, 25, 7, 8, 9, 10, 27, 28, 111, 32, 110, 33, 34, 101, 26, 107, 103, 104, 108, 29, 109, 30, 102, 106)

# Relocate the order and label, after the stat.type column
tbl3Data <- tbl3Data %>% relocate(c(order, label), .after = stat.type)

# Sort the rows of the tbl3Data data frame by the order column
tbl3Data <- tbl3Data[order(tbl3Data$order), ]

# Remove rows in tbl3Data that have order >= 100
tbl3Data <- tbl3Data[tbl3Data$order < 100, ]

# Remove the stat.type and order columns
tbl3Data <- tbl3Data[, -c(1, 2)]

# Rename the columns of the tbl3Data
colnames(tbl3Data) <- c("Factor (Count or Bin)", "Total", "Min", "Max", "Mean", "SD", "SE", "CI")

# Define the table headers
tbl3AddToRow <- list(
    pos = list(0, 6, 10, 17, 25, 30),
    command = c(
        "Factor (Count or Bin) & Total\\footnotemark[2] & Min\\footnotemark[1] & Max\\footnotemark[1] & Mean\\footnotemark[1] & SD\\footnotemark[1] & SE\\footnotemark[1] & CI\\footnotemark[1] \\\\ \n",
        "\\midrule \n",
        "\\midrule \n",
        "\\midrule \n",
        "\\midrule \n",
        "\\midrule \n"
    )
)

# Define the table footnotes
tbl3Footnotes <- data.frame("footnotes" = c(
    paste0("\\footnotetext[1]{Monthly generated cumulative summary time series from ", format(min(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), " through ", format(max(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), " (n = ", nrow(tsMonth), ")}"),
    "\\footnotetext[2]{Over the entire time period (2012-2024)}"
))

#### Table 4 ####

# Table 4 contains the statistics for the mean and median variables in the monthly time series data
# create a subset of the statsMonth that contains only the rows that end with either "Mean" or "Median"
tbl4Data <- statsMonth[grep("Mean$|Median$", rownames(statsMonth)), ]

# Keep only the columns sum, mean, std.dev, min, max, median
tbl4Data <- tbl4Data[, c("stat.type", "mean", "std.dev", "min", "max", "median")]

# reorder the columns of the statsMonth_mean in this order: mean, std.dev, min, max, median
tbl4Data <- tbl4Data[, c("stat.type", "mean", "std.dev", "min", "max", "median")]

# round the values in the statsMonth_mean data frame
for (i in c("mean", "std.dev", "min", "max", "median")) {
    tbl4Data[, i] <- round(tbl4Data[, i], 3)
}

# If the row name of tbl4Data is collSeverityNumMean, delete the row
tbl4Data <- tbl4Data[!grepl("collSeverityNumMean", rownames(tbl4Data)), ]

# if the row name of tbl4Data is collSeverityRankNumMean, delete the row
tbl4Data <- tbl4Data[!grepl("collSeverityRankNumMean", rownames(tbl4Data)), ]

# Define the labels of the table rows
tbl4Data$label <- c("Severity", "Severity Rank", "Parties", "Victims", "Killed", "Injured", "Severe Injuries", "Fatal or Severe Injuries", "Visible Injuries", "Complaint of Pain Injuries", "Minor or Pain Injuries", "Killed in Cars", "Injured in Cars", "Killed Pedestrians", "Injured Pedestrians", "Killed Bicyclists", "Injured Bicyclists", "Killed Motorcyclists", "Injured Motorcyclists", "Hit and Run", "Distance", "Lighting", "Party Number", "Killed Parties", "Injured Parties", "Vehicle Year Group", "Median Party Age", "Victim Number", "Victim Degree of Injury", "Median Victim Age", "City Area (sq. mi)", "City Population Density", "City Housing Density", "City Population", "City Housing Units", "City Asian Population", "City Black Population", "City Hispanic Population", "City White Population", "City Vehicles", "City Travel Time", "City Mean Travel Time", "City Primary Roads", "City Secondary Roads", "City Local Roads", "City Mean Road Length", "City Total Road Length")

# Define the order of display of the table rows
tbl4Data$order <- c(8, 116, 1, 2, 3, 101, 4, 102, 5, 6, 103, 104, 105, 106, 107, 108, 109, 110, 111, 9, 10, 11, 112, 113, 114, 12, 13, 115, 7, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 117, 25, 26, 27, 28, 118, 29)

# Relocate the order and label, after the stat.type column
tbl4Data <- tbl4Data %>% relocate(c(order, label), .after = stat.type)

# Sort the rows of the tbl3Data data frame by the order column
tbl4Data <- tbl4Data[order(tbl4Data$order), ]

# Remove rows in tbl4Data that have order >= 100
tbl4Data <- tbl4Data[tbl4Data$order < 100, ]

# Remove the stat.type and order columns
tbl4Data <- tbl4Data[, -c(1, 2)]

# Rename the columns of the tbl3Data
colnames(tbl4Data) <- c("Factor (Mean or Median)", "Mean", "Min", "Max", "SD", "Median")

# Define the table headers
tbl4AddToRow <- list(
    pos = list(0, 7, 14, 25),
    command = c(
        "Factor (Mean or Median) & Mean\\footnotemark[1] & Min\\footnotemark[1] & Max\\footnotemark[1] & SD\\footnotemark[1] & Median\\footnotemark[1] \\\\ \n",
        "\\midrule \n",
        "\\midrule \n",
        "\\midrule \n"
    )
)

# Define the table footnotes
tbl4Footnotes <- data.frame(
    "footnotes" = c(
        paste0("\\footnotetext[1]{Monthly generated cumulative summary time series from ", format(min(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), " through ", format(max(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), " (n = ", nrow(tsMonth), ")}"),
        "\\footnotetext[2]{Increasing ordinal severity rank from 0 (no injury) to 4 (fatal)}",
        "\\footnotetext[3]{Ordinal hit-and-run classification: 0 (No), 1 (Misdemeanor), 2 (Felony)}",
        "\\footnotetext[4]{Decreasing lighting intensity (higher value is darker conditions), from 1 to 4}",
        "Severity\\footnotemark[2]", "Hit and Run\\footnotemark[3]", "Lighting\\footnotemark[4]"
    )
)


### Display and Storage ####

#### Table 3 ####

# Convert the table 3 to a latex table and save it to disk
print(
    xtable(
        tbl3Data,
        caption = graphicsList$tables$tbl3$caption,
        label = graphicsList$tables$tbl3$id,
        digits = 2,
        auto = TRUE
    ),
    type = "latex",
    file = paste0(graphicsList$tables$tbl3$file, graphicsList$tables$tbl3$fileFormat),
    append = FALSE,
    floating = TRUE,
    floating.environment = 'table',
    table.placement = "h",
    caption.placement = "top",
    caption.width = NULL,
    latex.environments = "center",
    tabular.environment = "tabular",
    size = NULL,
    NA.string = "",
    include.rownames = FALSE,
    include.colnames = FALSE,
    only.contents = FALSE,
    add.to.row = tbl3AddToRow,
    sanitize.text.function = NULL,
    sanitize.rownames.function = NULL,
    sanitize.colnames.function = NULL,
    math.style.negative = FALSE,
    math.style.exponents = FALSE,
    print.results = TRUE,
    format.args = list(big.mark = ","),
    rotate.rownames = FALSE,
    rotate.colnames = FALSE,
    booktabs = TRUE,
    scalebox = NULL,
    width = NULL,
    comment = TRUE,
    timestamp = date()
)

# Convert the table 3 footnotes to a latex table and add it to disk
print(
    xtable(tbl3Footnotes),
    type = "latex",
    file = paste0(graphicsList$tables$tbl3$file, graphicsList$tables$tbl3$fileFormat),
    append = TRUE,
    include.rownames = FALSE,
    only.contents = TRUE,
    sanitize.text.function = identity,
    tabular.environment = "tabular",
    booktabs = TRUE,
    comment = FALSE,
    timestamp = NULL
)

# Save the table 3 data frame to the rDataPath directory
save(tbl3Data, tbl3AddToRow, tbl3Footnotes, file = file.path(prjDirs$rDataPath, "tbl3Data.RData"))


#### Table 4 ####

# Convert the table 4 to a latex table and save it to disk
print(
    xtable(
        tbl4Data,
        caption = graphicsList$tables$tbl4$caption,
        label = graphicsList$tables$tbl4$id,
        digits = 2,
        auto = TRUE
    ),
    type = "latex",
    file = paste0(graphicsList$tables$tbl4$file, graphicsList$tables$tbl4$fileFormat),
    append = FALSE,
    floating = TRUE,
    floating.environment = 'table',
    table.placement = "h",
    caption.placement = "top",
    caption.width = NULL,
    latex.environments = "center",
    tabular.environment = "tabular",
    size = NULL,
    NA.string = "",
    include.rownames = FALSE,
    include.colnames = FALSE,
    only.contents = FALSE,
    add.to.row = tbl4AddToRow,
    sanitize.text.function = NULL,
    sanitize.rownames.function = NULL,
    sanitize.colnames.function = NULL,
    math.style.negative = FALSE,
    math.style.exponents = FALSE,
    print.results = TRUE,
    format.args = list(big.mark = ","),
    rotate.rownames = FALSE,
    rotate.colnames = FALSE,
    booktabs = TRUE,
    scalebox = NULL,
    width = NULL,
    comment = TRUE,
    timestamp = date()
)

# Convert the table 4 footnotes to a latex table and add it to disk
print(
    xtable(tbl4Footnotes),
    type = "latex",
    file = paste0(graphicsList$tables$tbl4$file, graphicsList$tables$tbl4$fileFormat),
    append = TRUE,
    include.rownames = FALSE,
    only.contents = TRUE,
    sanitize.text.function = identity,
    tabular.environment = "tabular",
    booktabs = TRUE,
    comment = FALSE,
    timestamp = NULL
)

# Save the table 4 data frame to the rDataPath directory
save(tbl4Data, tbl4AddToRow, tbl4Footnotes, file = file.path(prjDirs$rDataPath, "tbl4Data.RData"))


## 2.7. Table 5 - Collision Incidents by Year ####
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Metadata ####

# Add graphics metadata for Table 5
graphicsList <- graphicsEntry(listName = "graphicsList", type = 1, eid = 5, listAttr = list(name = "Collision Incidents by Year", description = "Key statistics for the collision incidents by year in the OCSWITRS datasets", caption = "Collision Incidents Categorization by Year in the OCSWITRS datasets", method = "collap", fileFormat = ".tex", file = "Collision Incidents by Year", status = "final"))


### Definition ####

# Create a summary table of the collision incidents by year
tbl5Data <- data.frame(tsYear[, c("crashTagSum", "partyTagSum", "victimTagSum", "numberKilledSum", "numberInjSum", "countSevereInjSum", "countVisibleInjSum", "countComplaintPainSum", "countCarKilledSum", "countCarInjSum", "countPedKilledSum", "countPedInjSum", "countBicKilledSum", "countBicInjSum", "countMcKilledSum", "countMcInjSum")])

# Add rownames to the tbl05 data frame using the dt_year column
rownames(tbl5Data) <- as.numeric(format(tsYear$dateYear, "%Y"))

# Add summary statistics rows (total, mean, sd) to the bottom of the tbl05 data frame
tbl5Data <- rbind(tbl5Data, "Total" = round(apply(tbl5Data, 2, sum), 0), "Mean" = round(apply(tbl5Data, 2, mean), 0), "SD" = round(apply(tbl5Data, 2, sd), 0))

# Rename the columns of the tbl5Data data frame
colnames(tbl5Data) <- c("Crashes", "Parties", "Victims", "Fatal", "Injuries Total", "Injuries Severe", "Injuries Visible", "Injuries Pain", "Cars Killed", "Cars Injured", "Pedestrians Killed", "Pedestrians Injured", "Bicyclists Killed", "Bicyclists Injured", "Motorcyclists Killed", "Motorcyclists Injured")

# Creating a latex custom column header for the table
tbl5AddToRow <- list(
    pos = list(0, 12),
    command = c(
        "\\multirow[c]{2}{*}{Year} & \\multicolumn{1}{c}{\\multirow{2}{*}{Crashes}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Parties}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Victims}} & \\multicolumn{1}{c}{\\multirow{2}{*}{Fatal}} & \\multicolumn{4}{c}{Injuries} & \\multicolumn{2}{c}{Cars} & \\multicolumn{2}{c}{Pedestrians} & \\multicolumn{2}{c}{Bicyclists} & \\multicolumn{2}{c}{Motorcyclists} \\\\\n \\cmidrule{6-9}\\cmidrule{10-11}\\cmidrule{12-13}\\cmidrule{14-15}\\cmidrule{16-17}%\n &  &  &  &  & {Total} & {Severe} & {Visible} & {Pain} & {Killed} & {Injured} & {Killed} & {Injured} & {Killed} & {Injured} & {Killed} & {Injured} \\\\ \n",
        "\\midrule\n",
    )
)

# Define the table footnotes
tbl5footnotes <- data.frame("footnotes" = c(
    paste0("\\footnotetext[1]{Covers time series from ", format(min(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), " through ", format(max(as.Date(collisions$dateDatetime)), "%m/%d/%Y"), "}")))


### Display and Storage ####

# Convert the table to latex
print(
    xtable(
        tbl5Data,
        caption = graphicsList$tables$tbl5$caption,
        label = graphicsList$tables$tbl5$id,
        digits = 2,
        auto = TRUE
    ),
    type = "latex",
    file = paste0(graphicsList$tables$tbl5$file, graphicsList$tables$tbl5$fileFormat),
    append = FALSE,
    floating = TRUE,
    floating.environment = 'sidewaystable',
    table.placement = "h",
    caption.placement = "top",
    caption.width = NULL,
    latex.environments = "center",
    tabular.environment = "tabular",
    size = NULL,
    NA.string = "",
    include.rownames = TRUE,
    include.colnames = FALSE,
    only.contents = FALSE,
    add.to.row = tbl5AddToRow,
    sanitize.text.function = NULL,
    sanitize.rownames.function = NULL,
    sanitize.colnames.function = NULL,
    math.style.negative = FALSE,
    math.style.exponents = FALSE,
    print.results = TRUE,
    format.args = list(big.mark = ","),
    rotate.rownames = FALSE,
    rotate.colnames = FALSE,
    booktabs = TRUE,
    scalebox = NULL,
    width = NULL,
    comment = TRUE,
    timestamp = date()
)

# Convert the table 4 footnotes to a latex table and add it to disk
print(
    xtable(tbl5footnotes),
    type = "latex",
    file = paste0(graphicsList$tables$tbl5$file, graphicsList$tables$tbl5$fileFormat),
    append = TRUE,
    include.rownames = FALSE,
    only.contents = TRUE,
    sanitize.text.function = identity,
    tabular.environment = "tabular",
    booktabs = TRUE,
    comment = FALSE,
    timestamp = NULL
)

# Save the table 5 data frame to the rDataPath directory
save(tbl5Data, tbl5AddToRow, tbl5footnotes, file = file.path(prjDirs$rDataPath, "tbl5Data.RData"))


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
