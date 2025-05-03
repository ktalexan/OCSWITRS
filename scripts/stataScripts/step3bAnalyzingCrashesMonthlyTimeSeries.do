*==================================================
* STATA OCSWITRS DATA ANALYSIS
* Step 3b: Analyzing Crashes Monthly Time Series
* version 1, December 2024
* Dr. Kostas Alexandridis, GISP
*==================================================


clear all
macro drop _all
cls


*************** Stata Preliminaries ***************

// Define the global project settings
capture program drop projectGlobals
quietly: program projectGlobals
	// Set this program's metadata
	global projectName "Stata OCSWITRS Data Processing"
	global projectTitle "Step 3b: Analyzing Crashes Monthly Time Series"
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

* Set Stata Working Directory to raw data
cd "$dataDir"

* Use the crashes monthly time series dataset
clear all
use "stTsMonthCrashes.dta"

summarize

* Set Stata Working Directory to raw data
cd "$graphicsDir"






capture program drop graph1
program graph1
	args v1 v2
	confirm variable `v1'
	if `v2' {
	confirm variable `v2'
	}
end

graph1 victims

* Program that dynamically updates y variable min and max coordinates, and forms the covid box and reference lines for two way graphs
capture program drop graphConfig
quietly: program graphConfig
	* Summarize the key y-axis variable
	di
	di "Summarized variable:"
	sum `1', format
	* Minimum value
	global varMin = r(min)
	* Maximum value
	global varMax = r(max)
	* Mean value
	global varMean = r(mean)
	* Range (absolute) value
	global varRange = max(abs(r(max)), abs(r(min))) - min(abs(r(max)), abs(r(min)))
	* Interval value
	global varInterval = ${varRange}/5
	* Adjusted minimum if absolute variable minimum < 1
	if abs(${varMin}) < 1 {
		global yMin = floor(${varMin} * 100) / 100
	}
	* Adjusted minimim if variable minimum > 1
	else {
		global yMin = round((${varMin} - (${varMax} - ${varMin}) / 10), 1)
	}
	* Adjusted maximum if absolute variable maximum < 1
	if abs(${varMax}) < 1 {
		global yMax = ceil(${varMax} * 100) / 100
	}
	* Adjusted maximum if variable maximum > 1
	else {
		global yMax = round((${varMax} + (${varMax} - ${varMin}) / 10), 1)
	}
	* Adjusted interval if absolute variable interval < 1
	if abs($varInterval) < 1 {
		global yInterval = ($yMax - $yMin) / 5
	}
	* Adjusted interval if variable interval > 1
	else {
		global yInterval = round(($yMax - $yMin) / 5, 1)
	}
	* Compile the covid box two way graph script
	global covidBox = `"(function y = ${yMax}, range(${covidStart} ${covidEnd}) base(${yMin}) color(sunflowerlime%75) recast(area))"'
	* Compile the covid lines and label for the two way graph script
	global covidLines = `"(pci ${yMin} ${covidStart} ${yMax} ${covidStart} ${yMin} ${covidEnd} ${yMax} ${covidEnd}, lcolor(green) lpattern(shortdash) text(${yMax} ${covidLabel} "Covid-19" "Restrictions", placement(s) size(small) color(dkgreen)))"'	
	* Display the settings
	di
	di "Variable Settings:"
	macro list varMin varMax varMean varRange yMin yMax yInterval covidBox covidLines 
end

*global yvar = "mdvictimage"
*graphsettings $yvar
*twoway $covidbox $covidlines (tsline $yvar, ylabel($yMin($yInterval)$yMax) xlabel($tstart(12)$tend, format(%tmCCYY) labsize(medsmall)))


*************** Multi Graph - Killed Victims ***************

* Create multi-graph of monthly time series for killed victims along with local polynomial interpolation smoothed line with 95% confidence intervals
graphConfig fatalsevere
#d;
twoway 
	${covidBox} ${covidLines} 
	(tsline fatalsevere, lwidth(medium) lcolor(navy))
	(lpolyci fatalsevere tsmonth, lcolor(dkorange) clwidth(thick) fcolor(navy%25) acolor(navy%25) alwidth(none)),
	ytitle(Killed or Severely Injured per Month)
	yscale(extend fextend)
	ylabel(${yMin}(${yInterval})${yMax})
	xtitle(Collision Time)
	xlabel(${timeStart}(12)${timeEnd}, format(%tmCCYY) labsize(medsmall))
	legend(
		order(3 "Monthly Kiled" 4 "95% CI" 5 "Local Polynomial Smoothed")
		cols(1) size(small) ring(0) position(10) 
		symxsize(8) keygap(1.5) symysize(3)
		region(fcolor(white) lcolor(white))
	) 
	${graphRegion} ${graphScheme} ${graphSize}
	name(graph3b01, replace)
;
#d cr

// Save the graph, and export to png
graph save graph3b01 "graph3b01.gph", replace
graph export "graph3b01.png", name(graph3b01) as(png) replace
graph close



*************** Overlapped Victims-Severity Time Series ***************


// Create overlapping time series graph with their local polynomial smoother interpolation lines for the number of victims and the mean severity ranking
graphConfig victims
#d;
twoway
	$covidbox $covidlines
	(tsline victims, 
		lcolor(navy) 
		tlabel(${timeStart}(12)${timeEnd}) 
		ytitle(Number of Victims per Month, axis(1) size(medsmall)) 
		ylabel(${yMin}(${yInterval}){$yMax}, labsize(medsmall) format(%9.0gc) axis(1)) 
		yscale(titlegap(1) axis(1)))
	(tsline mseverity, 
		yaxis(2) 
		lcolor(maroon) 
		tlabel(${timeStart}(12)${timeEnd}, format(%tmCCYY)) 
		ytitle(Mean Severity, axis(2) size(medsmall)) 
		ylabel(0.05(0.05)0.21, labsize(medsmall) format(%9.2g) axis(2)) 
		yscale(titlegap(1) axis(2)))
	(lpolyci victims tsmonth, 
		lcolor(dknavy) 
		clwidth(medthick) 
		fcolor(navy%50))
	(lpolyci mseverity tsmonth, 
		yaxis(2) 
		lcolor(maroon) 
		clwidth(medthick) 
		fcolor(maroon%50)),
	legend(
		order(3 "Victims" 6 "Mean Severity" 4 "95% CI (Victims)" 7 "95% CI (Severity)" 5 "LPS (Victims)" 8 "LPS (Severity)") 
		rows(3) size(small) symxsize(8) keygap(1.5) 
		symysize(3) ring(0) position(8) colgap(4) 
		region(fcolor(none) lcolor(none))) 	
	$greg $gsch $gsize 
	name(graph3b02, replace)
;
#d cr


// Save the graph, and export to png
graph save graph3b02 "graph3b02.gph", replace
graph export "graph3b02.png", name(graph3b02) as(png) replace
graph close



*************** Stacked Victims-Severity Time Series ***************


// Create overlapping time series graph with their local polynomial smoother interpolation lines for the number of victims and the mean severity ranking (separate but combined graphs)
graphsettings victims
local toff = $tend - 5
twoway ///
$covidbox ///
$covidlines ///
(tsline victims, lcolor("75 75 150") lwidth(medthick)) ///
(lpolyci victims tsmonth, lcolor("0 0 100") clwidth(thick) fcolor(navy%25)), ytitle(Number of Victims) ///
ylabel($yMin($yInterval)$yMax, labsize(medsmall) format(%9.0fc) angle(horizontal)) ///
xlabel($tstart(12)$tend, format(%tmCCYY) labsize(medsmall)) ///
xscale(off) ///
ttext($yMax `toff' "(a)", size(large)) ///
legend(order(3 "Victims" 4 "95% CI (Victims)" 5 "LPS (Victims)") cols(1) ring(0) position(7) symxsize(8) keygap(1.5) symysize(3) region(fcolor(white) lcolor(white))) ///
graphregion(margin(medium)) plotregion(margin(none)) ///
$greg $gsch ysize(2.5) xsize(6) ///
name(temp1, replace)

graphsettings mseverity
twoway ///
$covidbox ///
(pci ${yMin} ${covidstartx} ${yMax} ${covidstartx} ${yMin} ${covidendx} ${yMax} ${covidendx}, lcolor(green) lpattern(shortdash)) ///
(tsline mseverity, lcolor("150 75 75") lwidth(medthick)) ///
(lpolyci mseverity tsmonth, lcolor("100 0 0") clwidth(thick) fcolor(maroon%25)), ///
ytitle(Mean Severity) ///
ylabel($yMin($yInterval)$yMax, labsize(medsmall) format(%9.3fc) angle(horizontal)) ///
xtitle(Collision Time) ///
xlabel($tstart(12)$tend, format(%tmCCYY) labsize(medsmall)) ///
ttext($yMax `toff' "(b)", size(large)) ///
legend(order(3 "Mean Severity" 4 "95% CI (Severity)" 3 "LPS (Severity)") cols(1) ring(0) position(10) symxsize(8) keygap(1.5) symysize(3) region(fcolor(white) lcolor(white))) ///
note("Data: OCSWITRS (2013-2024); LPS: Local Polynomial Smoothed Interpolation", size(small) span) ///
graphregion(margin(medium)) plotregion(margin(none)) ///
$greg $gsch ysize(2.5) xsize(6) ///
name(temp2, replace)


graph close

// Combine the two subgraohs using a table of graphs
graph combine temp1 temp2, ///
rows(2) commonscheme xsize(6) ysize(5.5) scale(0.9) imargin(none) graphregion(color(white)) plotregion(color(white)) ///
name(graph3b03, replace)

// Save the graph, and export to png
graph save graph3b03 "graph3b03.gph", replace
graph export "graph3b03.png", name(graph3b03) as(png) replace
graph close



*************** Analyzing Accident Severity ***************


// Visualize the z-score variation between fatal/sever and minor/pain accidents by month
#d;
twoway 
	(lpoly zfatalseverelps tsmonth, lwidth(thick)) 
	(lpoly zminorpainlps tsmonth, lwidth(thick)), 
	ytitle(z-score variation) 
	ytitle() 
	yscale(titlegap(1)) 
	xtitle(collision time) 
	xline(723 746, lcolor(dkgreen) lpattern(shortdash) extend) 
	xlabel(636(12)773, labels labsize(small) format(%tmCCYY)) 
	legend(order(1 "Fatal or Severe" 2 "Minor or Pain") size(small)) scheme(s2color) 
	graphregion(fcolor(white) lcolor(white) ifcolor(white) ilcolor(white))
;
#d cr



#d;
twoway 
	(pcspike zfatalseverelps tsmonth zminorpainlps tsmonth) 
	(line zfatalseverelps tsmonth, lcolor(maroon) lwidth(thick)) 
	(line zminorpainlps tsmonth, lcolor(forest_green) lwidth(thick)), 
	legend(order(1 "Diff" 2 "Fatal or Severe" 3 "Minor") rows(1)) 
	graphregion(fcolor(white) lcolor(white) ifcolor(white) ilcolor(white))
;
#d cr

#d;
twoway 
	(pcspike zaccseverelps tsmonth zaccminorlps tsmonth) 
	(line zaccseverelps tsmonth, lcolor(maroon) lwidth(thick)) 
	(line zaccminorlps tsmonth, lcolor(forest_green) lwidth(thick)), 
	xlabel(636(12)773, format(%tmCCYY)) 
	legend(order(1 "Diff" 2 "Fatal or Severe" 3 "Minor") rows(1)) 
	graphregion(fcolor(white) lcolor(white) ifcolor(white) ilcolor(white))
;
#d cr


*************** End of Processing ***************
