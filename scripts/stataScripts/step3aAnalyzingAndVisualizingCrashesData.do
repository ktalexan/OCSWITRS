*==================================================
* STATA OCSWITRS DATA ANALYSIS
* Step 3a: Analyzing and Visualizing Crashes Data
* version 1, December 2024
* Dr. Kostas Alexandridis, GISP
*==================================================


clear all
macro drop _all
cls
*macro list



*************** Stata Preliminaries ***************

// Define the global project settings
capture program drop projectGlobals
quietly: program projectGlobals
	// Set this program's metadata
	global projectName "Stata OCSWITRS Data Processing"
	global projectTitle "Step 3a: Analyzing and Visualizing Crashes Data"
	global projectVersion "Version 1, December 2024"
	global projectAuthor "Dr. Kostas Alexandridis, GISP"
	// Set the raw data start and end dates
	global dataStart = "20130101"
	global dataEnd = "20240630"
	di "Project Global Settings:"
	macro list projectName projectTitle projectVersion projectAuthor
	di "Data Dates:"
	macro list dataStart dataEnd
end
// Execute the global project settings
projectGlobals



*************** Global Directory Settings ***************

// Define the global directory settings
capture program drop projectDirs
quietly: program projectDirs
	// Set the project's directories
	global projectDisk "F"
	global projectDir = "${projectDisk}:\Professional\Projects-OCPW\OCTraffic\OCSWITRS"
	global dataDir = "${projectDir}\RawData"
	global analysisDir = "${projectDir}\Analysis"
	global graphicsDir = "${analysisDir}\Graphics"
	di "Directory Global Settings:"
	macro list projectDir dataDir analysisDir graphicsDir
end
// Execute the global directory settings
projectDirs



*************** Generating globals for key graph variables ***************

// Define program for key time series settings and configuration
capture program drop timeGlobals
quietly: program timeGlobals
	// Monthly time series configuration
	global timeStart = 636 //time start
	global timeEnd = 773	//time end
	global covidStart = 722 //covid start period
	global covidEnd = 745 //covid end period
	// Covid label positioning
	global covidLabel = ceil(${covidStart} + (${covidEnd} - ${covidStart}) / 2)
	// Globals for graph display
	global graphRegion "graphregion(fcolor(white) lcolor(white) ifcolor(white) ilcolor(white))" // graphics region settings
	global graphScheme "scheme(s2color)" //graphic scheme
	global graphSize "ysize(4) xsize(6)" //standard graphic size
	di
	di "Time Series Settings:"
	macro list timeStart timeEnd covidStart covidEnd covidLabel graphRegion graphScheme graphSize
end
// Execute the time series global configuration
timeGlobals


*************** Load Data and Directories ***************

// Set Stata Working Directory to raw data
cd "$dataDir"

// Load OCSWITRS Crashes Data
clear
use "stCrashes.dta"

// Switch to the graphics working directory
cd "$graphicsDir"







*************** Histogram = Victim Count ***************

// Create a histogram of victim count (top 10 frequencies)
#d;
histogram 
	victimcount if victimcount <= 10,
	discrete width(1) start(1) frequency
	fcolor(navy) lcolor(navy) gap(5)
	addlabel addlabopts(mlabsize(medsmall) yvarformat(%9.0gc))
	ytitle(Crash Frequency Prevalence)
	ylabel(, labsize(medsmall) format(%9.0gc))
	ytitle(Number of Victims in Crash Incident)
	xlabel(1(1)10, labsize(medsmall))
	note("Top-10 Victim Frequency Counts", span)
	${graphRegion} ${graphScheme} ${graphSize}
	name(graph3a01, replace)
;
#d cr

// Save the graph and export to png
graph save graph3a01 "graph3a01.gph", replace
graph export "graph3a01.png", name(graph3a01) as(png) replace
graph close



*************** Bar Graph - Collision Type ***************

// Graph type of collisions by number of crashes
#d;
graph bar (count),
	over(typeofcoll) asyvars
	blabel(bar, format(%9.0gc))
	ytitle(Number of Collisions)
	legend(cols(3) size(small) span)
	${graphRegion} ${graphScheme} ${graphSize}
	name(graph3a02, replace)
;
#d cr

// Save the graph and export to png
graph save graph3a02 "graph3a02.gph", replace
graph export "graph3a02.phg", name(graph3a02) as(png) replace
graph close



*************** Bar Graph - Fatal Accidents ***************

// Create a cumulative bar chart for the number of fatal accidents by type
#d;
graph bar
	(sum) countcarkilled
	(sum) countpedkilled
	(sum) countbickilled
	(sum) countmckilled,
	over(accidentyear, gap(10) label(labsize(small))) 
	stack
		bar(1, fcolor(ebg))
		bar(2, fcolor(sandb))
		bar(3, fcolor(sunflowerlime))
		bar(4, fcolor(khaki))
	blabel(total, size(vsmall))
	ytitle(Number Killed, size(small) justification(center) alignment(middle))
	ylabel(0(50)260, labsize(small))
	note("Notes: (a) Stacked bars of number of fatal accidents; (b) bar labels represent cumulative values", size(small) span)
	legend(order(1 "Cars" 2 "Pedestrians" 3 "Bicyclists"  4 "Motorcyclists") textfirst stack rows(1) size(small) region(lcolor(%0)) position(11) ring(0))
	${graphRegion} ${graphScheme} ${graphSize}
	name(graph3a03, replace)
;
#d cr

// save the graph and export to png
graph save graph3a03 "graph3a03.gph", replace
graph export "graph3a03.png", name(graph3a03) as(png) replace
graph close



*************** Histogram - Victims by Year (top-10) ***************

// Create a histogram of Victim count (top 10 frequencies by Year)
#d;
histogram
	victimcount if victimcount <= 10,
	discrete kdensity 
		kdenopts(lwidth(medthick) lcolor(dkgreen) width(0.5) gaussian)
	fcolor(orange) lcolor(orange) gap(10)
	ytitle(Density, size(small))
	xtitle(Number of Victims in Crashes, size(small))
	legend(order(1 "Density" 2 "Gaussian Kernel (Victim Count)") rows(1) size(small))
	by(accidentyear, style(default) imargin(vsmall) ${graphRegion})
	${graphRegion} ${graphScheme} ${graphSize}
	name(graph3a04, replace)
;
#d cr

// Save the graph and export to png
graph save graph3a04 "graph3a04.gph", replace
graph export "graph3a04.png", name(graph3a04) as(png) replace
graph close


// Open anova dialog
db anova

//Open one-way anova dialog
db oneway

// Create One-Way anova for the number of people killed by accident year
oneway numberkilled accidentyear, tabulate

// Create one-way anova for the number of people killed by collision severity rank
oneway numberkilled collseverityrank, tabulate

// Create one-way anova for the number of people killed by type of collision
oneway numberkilled typeofcoll, tabulate
oneway numberkilled primarycollfactor, tabulate


*************** End of Processing ***************
