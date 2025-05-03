*==================================================
* STATA OCSWITRS DATA ANALYSIS
* Step 3c: Analyzing Crashes Weekly Time Series
* version 1, December 2024
* Dr. Kostas Alexandridis, GISP
*==================================================

// Use the crashes monthly time series dataset
clear all
use "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\RawData\stTsWeekCrashes.dta"

summarize

// Globals
global greg = "graphregion(fcolor(white) lcolor(white) ifcolor(white) ilcolor(white))"
global gsch = "scheme(s2color)"
global gsize = "ysize(4) xsize(6)"



* Time segments
* 2756 - start
* 2990 - inflection point
* 3129 - start of covid restrictions
* 3232 - end of covid restrictions
* 3353 - end



*************** Generating LPS Coordinates for Severity ***************


// Generate local polynomial smoothing coordinates and save them in new variables
lpoly zaccsevere tsweek, generate(zaccseverelps) at(tsweek) se(zaccseverelpci)
lpoly zaccminor tsweek, generate(zaccminorlps) at(tsweek) se(zaccminorlpci)

// label and format the new vars
label var zaccseverelps "LPS Z-score of the fatal or severe accident count"
label var zaccseverelpci "LPS SEs Z-score of the fatal or severe accident count"
label var zaccminorlps "LPS Z-score of the minor or pain accident count"
label var zaccminorlpci "LPS SEs Z-score of the minor or pain accident count"
format (zaccseverelps zaccseverelpci zaccminorlps zaccminorlpci) %9.3g
graph close



*************** Generating globals for key graph variables ***************


// Weekly time series variable globals
global tstart = 2756 
global tend = 3353
global covidstartx = 3129
global covidendx = 3232
global covidlabx = ceil($covidstartx + ($covidendx - $covidstartx) / 2)



*************** Multi Graph - Killed or Severely Injured Victims ***************


*Create multi-graph of monthly time series for killed or severely injured victims along with local polynomial interpolation smoothed line with 95% confidence intervals
twoway ///
(function y = 50, range($covidstartx $covidendx) base(5) color(sunflowerlime%75) recast(area) droplines($covidstartx $covidendx)) ///
(tsline accsevere, lwidth(thin)) ///
(pci 5 $covidstartx 50 $covidstartx, lcolor(green) lpattern(shortdash)) ///
(pci 5 $covidendx 50 $covidendx, lcolor(green) lpattern(shortdash)) ///
(lpolyci accsevere tsweek, lcolor(navy) clwidth(medthick) fcolor(ebg%70) alcolor(navy%50) alwidth(thin)), ///
ytitle(Killed or Severely Injured) ///
yscale(extend fextend) ///
ylabel(5(5)50) ///
xtitle(Collision Time) ///
xlabel($tstart(52)$tend, format(%twCCYY) labsize(medsmall)) ///
ttext(47 $covidlabx "CA COVID-19" "Restrictions", size(small) color(dkgreen)) ///
legend(order(2 "Monthly Killed" 5 "95% CI" 6 "Local Polynomial Smoothed" ) cols(1) size(small) ring(0) position(10) symxsize(8) keygap(1.5) symysize(3) region(fcolor(white) lcolor(white))) ///
$greg $gsch $dsize ///
name(graph3c01, replace)

*Save the graph, and export to png
graph save graph3c01 "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c01.gph", replace
graph export "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c01.png", name(graph3c01) as(png) replace
graph close



*************** Overlapped Victims-Severity Time Series ***************


sum victims
global rmin1 = floor(r(min)/100)*100 
global rmax1 = ceil(r(max)/100)*100
global rfrac1 = round(($rmax1 - $rmin1)/4, 1)
sum mseverity
global rmin2 = floor(r(min)*100)/100
global rmax2 = ceil(r(max)*100)/100
global rfrac2 = round(($rmax2 - $rmin2)/4, 0.001)
global covidlaby = $rmax1 - 20

// Create overlapping time series graph with their local polynomial smoother interpolation lines for the number of victims and the mean severity ranking
twoway ///
(function y = $rmax1, range($covidstartx $covidendx) base($rmin1) color(sunflowerlime%75) recast(area) droplines($covidstartx $covidendx)) ///
(pci $rmin1 $covidstartx $rmax1 $covidstartx, lcolor(green) lpattern(shortdash)) ///
(pci $rmin1 $covidendx $rmax1 $covidendx, lcolor(green) lpattern(shortdash)) ///
(tsline victims, lcolor(navy%50) lwidth(thin) tlabel($tstart(52)$tend) ytitle(Number of Victims, axis(1) size(medsmall)) ylabel($rmin1($rfrac1)$rmax1, labsize(medsmall) format(%9.0gc) axis(1)) yscale(titlegap(1) axis(1))) ///
(tsline mseverity, yaxis(2) lcolor(maroon%50) lwidth(thin) tlabel($tstart(52)$tend) ytitle(Mean Severity, axis(2) size(medsmall)) ylabel($rmin2($rfrac2)$rmax2, labsize(medsmall) format(%9.2g) axis(2)) yscale(titlegap(1) axis(2))) ///
(lpolyci victims tsweek, lcolor(dknavy) clwidth(medthick) fcolor(navy%50)) ///
(lpolyci mseverity tsweek, yaxis(2) lcolor(maroon) clwidth(medthick) fcolor(maroon%50)), ///
xtitle(Collision Time, size(medsmall)) ///
xlabel($tstart(52)$tend, format(%twCCYY) labsize(medsmall)) ///
ttext($covidlaby $covidlabx "CA COVID-19" "Restrictions", size(small) color(dkgreen)) ///
legend(order(4 "Victims" 7 "Mean Severity" 5 "95% CI (Victims)" 8 "95% CI (Severity)" 6 "LPS (Victims)" 9 "LPS (Severity)" ) rows(3) size(small) symxsize(8) keygap(1.5) symysize(3) ring(0) position(10) region(fcolor(white) lcolor(white))) ///
$greg $gsch $gsize ///
name(graph3c02, replace)

// Save the graph, and export to png
graph save graph3c02 "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c02.gph", replace
graph export "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c02.png", name(graph3c02) as(png) replace
graph close



*************** Stacked Victims-Severity Time Series ***************


sum victims
global rmin1 = floor(r(min)/100)*100 
global rmax1 = ceil(r(max)/100)*100
global rfrac1 = round(($rmax1 - $rmin1)/4, 1)
sum mseverity
global rmin2 = floor(r(min)*100)/100
global rmax2 = ceil(r(max)*100)/100
global rfrac2 = round(($rmax2 - $rmin2)/4, 0.001)

global covidlaby1 = $rmax1 - 30
global covidlaby2 = $rmax2 - 0.02


// Create overlapping time series graph with their local polynomial smoother interpolation lines for the number of victims and the mean severity ranking (separate but combined graphs)
twoway ///
(function y = $rmax1, range($covidstartx $covidendx) base($rmin1) color(sunflowerlime%75) recast(area) droplines($covidstartx $covidendx)) ///
(pci $rmin1 $covidstartx $rmax1 $covidstartx, lcolor(green) lpattern(shortdash)) ///
(pci $rmin1 $covidendx $rmax1 $covidendx, lcolor(green) lpattern(shortdash)) ///
(tsline victims, lcolor(navy%50) lwidth(medium)) ///
(lpolyci victims tsweek, lcolor(navy) clwidth(medthick) fcolor(ebg%70) alcolor(navy%50) alwidth(thin)), ///
ytitle(Number of Victims, size(medsmall)) ///
ylabel($rmin1($rfrac1)$rmax1, labsize(medsmall) format(%9.0gc)) ///
xtitle(Collision Time, size(medsmall)) ///
xlabel($tstart(52)$tend, format(%twCCYY) labsize(medsmall)) ///
xscale(off) ///
ttext($covidlaby $covidlabx "CA COVID-19" "Restrictions", size(medsmall) color(dkgreen)) ///
ttext($covidlaby1 $tend "(a)", size(large)) ///
legend(order(4 "Victims" 5 "95% CI (Victims)" 6 "LPS (Victims)") cols(1) ring(0) position(10) symxsize(8) keygap(1.5) symysize(3) region(fcolor(white) lcolor(white))) ///
plotregion(margin(zero)) ///
$greg $gsch ///
ysize(2.5) xsize(6) ///
name(temp1, replace)


twoway ///
(function y = $rmax2, range($covidstartx $covidendx) base($rmin2) color(sunflowerlime%75) recast(area) droplines($covidstartx $covidendx)) ///
(pci $rmin2 $covidstartx $rmax2 $covidstartx, lcolor(green) lpattern(shortdash)) ///
(pci $rmin2 $covidendx $rmax2 $covidendx, lcolor(green) lpattern(shortdash)) ///
(tsline mseverity, lcolor(maroon%50) lwidth(medium)) ///
(lpolyci mseverity tsweek, lcolor(maroon) clwidth(medthick) fcolor(orange%30) alcolor(maroon%50) alwidth(thin)), ///
ytitle(Mean Severity, size(medsmall)) ///
ylabel($rmin2($rfrac2)$rmax2, labsize(medsmall) format(%9.0gc)) ///
xtitle(Collision Time, size(medsmall)) ///
xlabel($tstart(52)$tend, format(%twCCYY) labsize(medsmall)) ///
ttext($covidlaby $covidlabx "CA COVID-19" "Restrictions", size(medsmall) color(dkgreen)) ///
ttext($covidlaby2 $tend "(b)", size(large)) ///
legend(order(4 "Mean Severity" 5 "95% CI (Severity)" 6 "LPS (Severity)") cols(1) ring(0) position(10) symxsize(8) keygap(1.5) symysize(3) region(fcolor(white) lcolor(white))) ///
plotregion(margin(zero)) ///
$greg $gsch ///
ysize(2.5) xsize(6) ///
name(temp2, replace)

graph close

// Combine the two subgraohs using a table of graphs
graph combine temp1 temp2, ///
rows(2) commonscheme xsize(6) ysize(5.5) scale(0.9) ///
graphregion(margin(zero) fcolor(white) lcolor(white)) plotregion(margin(zero)) ///
scheme(s2color) ///
name(graph3c03, replace)

// Save the graph, and export to png
graph save graph3c03 "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c03.gph", replace
graph export "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c03.png", name(graph3c03) as(png) replace
graph close



*************** Visualizing Accident Severity Overlap ***************


// globals for fatal/severe accidents
sum zaccseverelps
global rmin1 = floor(r(min)*100)/100
global rmax1 = ceil(r(max)*100)/100
global rfrac1 = round(($rmax1 - $rmin1)/4, 0.001)

// globals for minor/pain accidents
sum zaccminorlps
global rmin2 = floor(r(min)*100)/100
global rmax2 = ceil(r(max)*100)/100
global rfrac2 = round(($rmax2 - $rmin2)/4, 0.001)

// Selecting the max and min between the two classes
global rmin = min($rmin1, $rmin2)
global rmax = max($rmax1, $rmax2)
global rfrac = round(($rmax - $rmin)/4, 0.001)

// Placement of the covid label (y-coordinate)
global covidlaby = $rmax - 0.15

// where the two lines cross (x-coordinate)
global crossx = 3060

// crossing lines for fatal/severe y-coordinate
sum zaccseverelps if tsweek == $crossx
global crosssy1 = round(r(max), 0.001)

// crossing lines for minor/pain y-coordinate
sum zaccminorlps if tsweek == $crossx
global crossy2 = round(r(max), 0.001)
di $crossy1, $crossy2

// covid start labels y-coordinates for the two classes
sum zaccseverelps if tsweek == $covidstartx
global covidstarty1 = round(r(max), 0.001)
sum zaccminorlps if tsweek == $covidstartx
global covidstarty2 = round(r(max), 0.001)

// covid end labels y-coordinates for the two classes
sum zaccseverelps if tsweek == $covidendx
global covidendy1 = round(r(max), 0.001)
sum zaccminorlps if tsweek == $covidendx
global covidendy2 = round(r(max), 0.001)


// Visualize the z-score variation between fatal/sever and minor/pain accidents by month. Generate an overlapping graph with the two severity classes, their positive or negative areas (colorcoded) and timeline configurations
twoway ///
(function y = $rmax, range($covidstartx $covidendx) base($rmin) color(sunflowerlime%75) recast(area) droplines($covidstartx $covidendx)) ///
(rarea zaccseverelps zaccminorlps tsweek if tsweek <= $crossx, fcolor(ebg%50) lcolor(%0)) ///
(rarea zaccseverelps zaccminorlps tsweek if tsweek > $crossx, fcolor(orange%30) lcolor(%0)) ///
(line zaccseverelps tsweek, lcolor(red) lwidth(medthick)) ///
(line zaccminorlps tsweek, lcolor(blue) lwidth(medthick)) ///
(scatteri $crossy1 $crossx $covidstarty1 $covidstartx $covidendy1 $covidendx, msymbol(smcircle) color(red)) ///
(scatteri $crossy2 $crossx $covidstarty2 $covidstartx $covidendy2 $covidendx, msymbol(smcircle) color(blue)) ///
(pci $rmin $crossx $crossy1 $crossx, lcolor(green) lpattern(shortdash)) ///
(pci $rmin $covidstartx $rmax $covidstartx, lcolor(green) lpattern(shortdash)) ///
(pci $rmin $covidendx $rmax $covidendx, lcolor(green) lpattern(shortdash)) ///
(pcarrowi -.15 3020 .02 3055 (9) "(Nov 2018)", lcolor(green) lwidth(medium) mcolor(green) msize(large) barbsize(medium) mlabcolor(green)), ///
ytitle(LPS Severity z-score) ///
ylabel($rmin($rfrac)$rmax, axis(1) format(%9.0g)) ///
xtitle(Collision Time) ///
xlabel($tstart(52)$tend, format(%twCCYY)) ///
ttext($covidlaby $covidlabx "CA COVID-19" "Restrictions", size(small) color(green)) ///
legend(order(4 "LPS Fatal or Severe" 5 "LPS Minor or Pain" 2 "Minor/Pain > Fatal/Severe" 3 "Fatal/Severe > Minor/Pain") cols(1) size(small) region(fcolor(none) lcolor(%0)) position(7) ring(0)) ///
$greg $gsch $gsize ///
name(graph3c04, replace)

// Save the graph, and export to png
graph save graph3c04 "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c04.gph", replace
graph export "E:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\Graphics\graph3c04.png", name(graph3c04) as(png) replace
graph close

* Note1: there are five distinct areas recognizable in the graph. Specifically,
* 1 - start of 2013 to mid 2016. Both trends increase, but the minor are significanlty large proportion of the fatal;
* 2 - mid 2016 to Nov 2018 (crossing threshold). Both trends decrease over this period, albeit the fatal more slowly.
* 3 - Nov 2018 to march 2020 (beginning of COVID). Both trends significantly and relatively decreas. The minor accidents particularly are declining rapidly. But unlikely any past trends, this period, the fatal accidents suppercede their minor for the first time.
* 4 - March 2020 to Feb 2022 (Covid restrictions period). Both trends significantly rising, with the minor accidents more rapidly. Consistently and persistently, the fatal rates are more prevalent than the minor accident rates.
* 6 March 2022 to 2024. Relatively steady slowing and declining of both trends and slightly converging. As since 2019, again, the relative rates of the fatal supercede those of the minor accidetns.






// generate local polynomial smoothed line coordinates (and CI) for fatal/severe and minor/pain accidents respectively
lpoly accsevere tsweek, generate(sevlps) at(tsweek) se(sevlpci)
lpoly accminor tsweek, generate(minlps) at(tsweek) se(minlpci)

// standardize the LPS and LPCI variables to have the same mean and standard deviation
egen float stdsevlps = std(sevlps), mean(0) std(1)
egen float stdsevlpci = std(sevlpci), mean(0) std(1)
egen float stdminlps = std(minlps), mean(0) std(1)
egen float stdminlpci = std(minlpci), mean(0) std(1)





twoway ///
(function y=2.5, range(2756 2990) recast(area) color(lime%10) base(-2.5) ttext(2.25 2873 "Period 1" "(2013-2017)", size(small) color(green))) ///
(function y=2.5, range(2990 3129) recast(area) color(purple%10) base(-2.5) ttext(2.25 3060 "Period 2" "(2017-2020)", size(small) color(green))) ///
(function y=2.5, range(3129 3232) recast(area) color(orange%20) base(-2.5) ttext(2.25 3181 "Covid-19" "(2020-2022)", size(small) color(green))) ///
(function y=2.5, range(3232 3353) recast(area) color(blue%10) base(-2.5) ttext(2.25 3293 "Period 4" "(2022-2024)", size(small) color(green))) ///
(tsline stdsevlps, lcolor(red) lwidth(medthick)) ///
(tsline stdminlps, lcolor(blue) lwidth(medthick)), ///
xline(2990 3129 3232, lwidth(medthin) lpattern(shortdash) lcolor(green) extend) ///
yline(0, lwidth(medthin) lpattern(shortdash) lcolor(green) extend) ///
ytitle(Standardized Severity LPS) ///
ylabel(-2.5(0.5)2.5, format(%9.0gc)) ///
xtitle(Collision Time) ///
xlabel(2756(52)3353, format(%twCCYY)) ///
legend(order(5 "LPS Fatal or Severe" 6 "LPS Minor or Pain") cols(1) size(small) region(fcolor(none) lcolor(%0)) position(7) ring(0) symxsize(7) keygap(1.5)) ///
$greg $gsch $gsize ///
name(graph3c05, replace)



*************** End of Processing ***************
