*==================================================
* STATA OCSWITRS DATA PROCESSING
* Step 2: Processing Combined Collisions Dataset
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
	global projectTitle "Step 2: Processing Combined Collisions Dataset"
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



*************** Load Data and Directories ***************

// Set Stata Working Directory to raw data
cd "$dataDir"

// Load the collisions raw data file
clear
use "collisionsRaw.dta"
label data "OCSWITRS Collisions Stata Dataset"



*************** Basic Labeling Operations ***************

// Case ID variable operations
label var caseid "Case ID"
notes caseid : Unique Identifier of the crash case

// CID variable operations
label var cid "Crash ID"
notes cid : Unique identifier of the crash case

// PID variable operations
label var pid "Party ID"
notes pid : Unique identifier for the party case

// VID variable operations
label var vid "Victim ID"
notes vid : Unique identifier of the victim case

// Party Number variable operations
label var partynumber "Party Number"
notes partynumber: Unique identifier of the party number in the crash

// Victim Number variable operations
label var victimnumber "Victim Number"
notes victimnumber: Unique identifier of the victim number in the crash

// Total Crashes variable operations
label var crashestag "Total number of crashes per case"
notes crashestag: Count of crashes per case

// Total Parties variable operations
label var partiestag "Total number of parties per case"
notes partiestag: Count of parties per case

// Total Victims variable operations
replace victimstag = 0 if victimstag == .
label var victimstag "Total number of victims per case"
notes victimstag: Count of victims per case



*************** Creating Indicator Variables ***************

// first, sort the dataset observations by cid, pid and vid
sort cid pid vid

// generate crashes indicator variable
egen crashesind = tag(cid)
label var crashesind "Crashes Indicator"
note crashesind: Indicator variable for the unique crashes in the dataset
label define crashesind 1 "Crash" 0 ""
label values crashesind crashesind
order crashesind, after(victimstag)

// generate parties indicator variable
egen partiesind = tag(pid)
label var partiesind "Parties Indicator"
note partiesind: Indicator variable for the unique parties in the dataset
label define partiesind 1 "Parties" 0 ""
label values partiesind partiesind
order partiesind, after(crashesind)

// generate victims indicator variable
egen victimsind = tag(vid)
label var victimsind "Victims Indicator"
note victimsind: Indicator variable for the unique victims in the dataset
label define victimsind 1 "Victims" 0 ""
label values victimsind victimsind
order victimsind, after(partiesind)

// re-sort the data by date and time
sort colldate colltime cid pid vid

// create combined indicator variable
egen temp = concat(crashesind partiesind victimsind)
gen byte combinedind = 1 if temp == "111"
replace combinedind = 2 if temp == "110"
replace combinedind = 3 if temp == "101"
replace combinedind = 4 if temp == "011"
replace combinedind = 5 if temp == "100"
replace combinedind = 6 if temp == "010"
replace combinedind = 7 if temp == "001"
label var combinedind "Combined Indicator"
note combinedind: Indicator variable for the unique combinations of crashes, parties and victims in the dataset
label define combinedind 1 "crashes with parties and victims" 2 "crashes with parties, no victims" 3 "crashes with victims, no parties" 4 "parties with victims" 5 "crashes only" 6 "parties only" 7 "victims only"
label values combinedind combinedind
order combinedind, after(victimsind)
drop temp



*************** Place and Dates Variables ***************

// City variable operations
label var city "City"
notes city : Reported city of the crash

// City name (encoded from string city) variable operations
encode city, generate(cityname) label(cityname)
order cityname, after(city)
label var cityname "City Name"
notes cityname: Reported city of the crash (encoded)

// Place type variable operations
label var placetype "Place Type"
notes placetype : City or Unincorporated Area

// Crash Date (reported) variable operations
label var colldate "Collision Date (reported"
notes colldate: Collision date reported and recorded at the scene of the accident

// Crash date and time variable operations
tostring colltime, gen(t1)
gen t2 = substr(t1, 1, 2) + ":" + substr(t1, -2, .) if strlen(t1) == 4
replace t2 = "0" + substr(t1, 1, 1) + ":" + substr(t1, -2, .) if strlen(t1) == 3
replace t2 = "00:" + substr(t1, -2, .) if strlen(t1) == 2
replace t2 = "00:0" + t1 if strlen(t1) == 1
replace t2 = "" if colltime > 2400
gen t3 = substr(colldate, 6, 2) + "/" + substr(colldate, 9, 2) + "/" + substr(colldate, 1, 4)
egen colldatetime = concat(t3 t2), punct(" ")
replace colldatetime = colldate if colltime > 2400
gen stcolldatetime = clock(colldatetime, "MDYhm")
format stcolldatetime %tcNN/DD/CCYY_hh:MM_AM
order stcolldatetime colldatetime, before(colldate)
drop t1 t2 t3
label var colldatetime "Crash Date and Time"
notes colldatetime : Full date and time string of the crash
label var stcolldatetime "Crash Date and Time (stata)"
notes stcolldatetime: Full date and time stata date time variable

// Convert collision date string to date
gen stcolldate = date(colldate, "YMD")
format stcolldate %tdNN/DD/CCYY
order stcolldate, before(colldate)
label var stcolldate "Crash Date (stata)"
notes stcolldate : The date when the crash occurred stata date variable

// Crash time only variable operations
label var colltime "Crash Time"
notes colltime : The time when the crash occurred in 24h format

// Crash year only variable operations
label var accidentyear "Crash Year"
notes accidentyear : The year when the crash occurred

// Crash quarter only variable operations
gen accidentquarter = quarter(stcolldate)
order accidentquarter, after(accidentyear)
label define accidentquarter 1 "Q1" 2 "Q2" 3 "Q3" 4 "Q4"
label values accidentquarter accidentquarter
label var accidentquarter "Crash Quarter"
notes accidentquarter: Quarter number from crash date

// Crash month only variable operations
gen accidentmonth = month(stcolldate)
order accidentmonth, after(accidentquarter)
label define accidentmonth  1 "January" 2 "February" 3 "March" 4 "April" 5 "May" 6 "June" 7 "July" 8 "August" 9 "September" 10 "October" 11 "November" 12 "December"
label values accidentmonth accidentmonth
label var accidentmonth "Crash Month"
notes accidentmonth : Month number from crash date

// Crash week only variable operations
gen accidentweek = week(stcolldate)
order accidentweek, after(accidentmonth)
label var accidentweek "Crash Week Number"
notes accidentweek: Week number from crash date

// Crash day only variable operations
gen accidentday = day(stcolldate)
order accidentday, after(accidentweek)
label var accidentday "Crash Day Number of month"
notes accidentday: Day number from crash date

// Day of the week variable operations
ren weekday accidentdayweek
label define accidentdayweek  1 "Monday" 2 "Tuesday" 3 "Wednesday" 4 "Thursday" 5 "Friday" 6 "Saturday" 7 "Sunday"
label values accidentdayweek accidentdayweek
label var accidentdayweek "Day of Week"
notes accidentdayweek : Code for the day of the week when the crash occurred

// Crash day of year only variable operations
gen accidentdayyear = mdy(accidentmonth, accidentday, accidentyear)
order accidentdayyear, after(accidentdayweek)
label var accidentdayyear "Crash Day Number of year"
notes accidentdayyear: Day number (of year) from crash date

// Create time series Year date variable
gen tsyear = year(stcolldate)
format tsyear %ty
order tsyear, after(accidentday)
label var tsyear "Crash Year"
notes tsyear: Year of the crash case (stata date)

// Create time series Year-Quarter date variable
gen tsquarter = yq(accidentyear, accidentquarter)
format tsquarter %tq
order tsquarter, after(tsyear)
label var tsquarter "Crash Year and Quarter"
notes tsquarter: Year and Quarter of the crash case (stata date)

// Create time series Year-Month date variable
gen tsmonth = ym(accidentyear, accidentmonth)
format tsmonth %tm
order tsmonth, after(tsquarter)
label var tsmonth "Crash Year and Month"
notes tsmonth: Year and Month of the crash case (stata date)

// Create time series Year-Week date variable
gen tsweek = yw(accidentyear, accidentweek)
format tsweek %tw
order tsweek, after(tsmonth)
label var tsweek "Crash Year and Week"
notes tsweek: Year and Week of the crash case (stata date)

// Create time series Year-Day date variable
gen tsday = mdy(accidentmonth, accidentday, accidentyear)
format tsday %td
order tsday, after(tsweek)
label var tsday "Crash Year and Day"
notes tsday: Year and Day of the crash case (stata date)

// Convert processing date string to date
gen stprocdate = date(procdate, "YMD")
format stprocdate %tdNN/DD/CCYY
order stprocdate, before(procdate)
label var stprocdate "Processing Date (stata)"
notes stprocdate : The date that the crash case was last changed (stata date variable)

// Processing date variable operations
label var procdate "Processing Date"
notes procdate: The date that the crash case was last changed

// Create time intervals variable operations
gen colltimeintervals = 1 if colltime >= 0 & colltime < 600
replace colltimeintervals = 2 if colltime >= 600 & colltime < 1200
replace colltimeintervals = 3 if colltime >= 1200 & colltime < 1800
replace colltimeintervals = 4 if colltime >= 1800 & colltime < 2400
replace colltimeintervals = 9 if colltime >= 2400
label define colltimeintervals  1 "Night (00:00am to 06:00am)" 2 "Morning (06:00am to 12:00pm)" 3 "Afternoon (12:00pm to 06:00pm)" 4 "Evening (06:00pm to 00:00am)" 9 "Unknown Time"
label values colltimeintervals colltimeintervals
label var colltimeintervals "Crash Time Intervals"
notes colltimeintervals : Crash time interval ranges classification
order colltimeintervals, after(procdate)

// create rush hours variable operations
gen rushhours = 3
replace rushhours = 1 if accidentday >- 1 & accidentday < 6 & colltime >= 700 & colltime < 1000
replace rushhours = 2 if accidentday >- 1 & accidentday < 6 & colltime >= 1600 & colltime < 1900
replace rushhours = 9 if colltime > 2400
label define rushhours  1 "Rush Hours (Morning)" 2 "Rush Hours (Evening)" 3 "Non-Rush Hours" 9 "Unknown Time"
label values rushhours rushhours
label var rushhours "Rush Hours"
notes rushhours : Rush hours interval ranges (Mon-Fri mornings and evenings)
order rushhours, after(colltimeintervals)



*************** Collision Severity Operations ***************

// Crash severity variable operations
label define collseverity  0 "No injury, aka property damage only or PDO" 1 "Fatal injury" 2 "Suspected serous injury or severe injury" 3 "Suspected minor injury or visible injury" 4 "Possible injury or complaint of pain"
label values collseverity collseverity
label var collseverity "Crash Severity"
notes collseverity : The worst injury suffered by any victim in the crash

// Binary crash severity variable operations
gen byte collseveritybin = 1 if collseverity == 1 | collseverity == 2
replace collseveritybin = 0 if collseverity == 0 | collseverity == 3 | collseverity == 4
label define collseveritybin  0 "Minor (minor injury, pain, or no injury)" 1 "Severe (killed or serious injury)"
label values collseveritybin collseveritybin
label var collseveritybin "Crash Severity (binary)"
notes collseveritybin : Binary classification of the worst injury suffered by any victim in the crash
order collseveritybin, after(collseverity)

// Reclassified crash severity variable operations
gen byte collseverityreclass = 0 if collseverity == 0
replace collseverityreclass = 1 if collseverity == 4
replace collseverityreclass = 2 if collseverity == 3
replace collseverityreclass = 3 if collseverity == 2
replace collseverityreclass = 4 if collseverity == 1
label define collseverityreclass  0 "None" 1 "Possible Injury or Pain" 2 "Minor or Visible Injury" 3 "Serious or Severe Injury" 4 "Fatal Injury"
label values collseverityreclass collseverityreclass
label var collseverityreclass "Crash Severity Reclassified"
notes collseverityreclass : Reclassified crash severity based on the worst injury suffered by any victim in the crash
order collseverityreclass, after(collseveritybin)

// Ranked crash severity variable operations
gen byte collseverityrank = 0 if numberkilled == 0 & countsevereinj == 0
replace collseverityrank = 1 if numberkilled == 0 & countsevereinj == 1
replace collseverityrank = 2 if numberkilled == 0 & countsevereinj > 1
replace collseverityrank = 3 if numberkilled == 1 & countsevereinj == 0
replace collseverityrank = 4 if numberkilled == 1 & countsevereinj == 1
replace collseverityrank = 5 if numberkilled == 0 & countsevereinj > 1
replace collseverityrank = 6 if numberkilled > 1 & countsevereinj == 0
replace collseverityrank = 7 if numberkilled > 1 & countsevereinj == 1
replace collseverityrank = 8 if numberkilled > 1 & countsevereinj > 1
label define collseverityrank  0 "None or Minor Injuries" 1 "Single Injury (Severe)" 2 "Multiple Injuries (Severe)" 3 "Single Fatality, No Injuries (Fatal)" 4 "Single Fatality, Single Injury (Fatal)" 5 "Single Fatality, Multiple Injuries (Fatal)" 6 "Multiple Fatalities, No Injuries (Fatal)" 7 "Multiple Fatalities, Single Injury (Fatal)" 8 "Multiple Fatalities, Multiple Injuries (Fatal)"
label values collseverityrank collseverityrank
label var collseverityrank "Crash Severity Ranked"
notes collseverityrank : Ranked crash severity based on the worst injury suffered by any victim in the crash
order collseverityrank, after(collseverityreclass)

// Generate indicator variables for severity ranks (NEW)
recode collseverityrank (0 3 6 = 0) (1 2 4 5 7 8 = 1) (missing=.), generate(indsevere)
recode collseverityrank (0 1 2 = 0) (3 4 5 6 7 8 = 1) (missing=.), generate(indfatal)
recode collseverityrank (0 1 3 4 = 0) (2 5 6 7 8 = 1) (missing=.), generate(indmulti)

// Severe indicator variable operations (NEW)
order indsevere, after(collseverityrank)
label define indsevere 0 "Not a severe injury" 1 "Severe injury"
label values indsevere indsevere
label var indsevere "Severe Injury Indicator"
notes indsevere: Reclassified indicator variable from severity level where there exist severe injuries in the accident

// Fatal indicator variable operations (NEW)
order indfatal, after(indsevere)
label define indfatal 0 "Not a fatal injury" 1 "Fatal injury"
label values indfatal indfatal
label var indfatal "Fatal Injury Indicator"
notes indfatal: Reclassified indicator variable from severity level where there exist fatal injuries in the accident

// Multiple indicator variable operations (NEW)
order indmulti, after(indfatal)
label define indmulti 0 "No multiple severe or fatal injuries present" 1 "Multiple severe or fatal injuries present"
label values indmulti indmulti
label var indmulti "Multiple Injury Indicator"
notes indmulti: Reclassified indicator variable from severity level where there exist multiple severe or fatal injuries in the accident



*************** Count Variables (Multi-Level) ***************

// Party count variable operations
label var partycount "Party Count"
notes partycount : Number of parties involved in the crash

// Victim count variable operations
gen byte victimcount = numberkilled + numberinjured
order victimcount, after(partycount)
label var victimcount "Victim Count"
notes victimcount : Number of victims involved in each party

// Killed victims variable operations
label var numberkilled "Killed Victims"
notes numberkilled : Number of killed victims

// Injured victims variable operations
label var numberinjured "Injured Victims"
notes numberinjured : Number of injured victims

// Severe injury count variable operations
label var countsevereinj "Severe Injury Count"
notes countsevereinj : Number of victims in the crash with suspected serous injury or severe injury

// Other visible injury count variable operations
label var countvisibleinj "Other Visible Injury Count"
notes countvisibleinj : Number of victims in the crash with suspected minor injury or visible injury

// Complaint of pain injury count variable operations
label var countcomplaintpain "Complaint of Pain Injury Count"
notes countcomplaintpain : Number of victims in the crash with possible injury or complaint of pain

// Car passengers killed (new variable)
gen countcarkilled = numberkilled - countpedkilled - countbickilled - countmckilled
order countcarkilled, after(countcomplaintpain)
label var countcarkilled "Number of killed car victims"
notes countcarkilled: Number of killed car victims (drivers or passengers)

// Car passengers injured (new variable)
gen countcarinj = numberinjured - countpedinj - countbicinj - countmcinj
order countcarinj, after(countcarkilled)
label var countcarinj "Number of killed car victims"
notes countcarinj: Number of killed car victims (drivers or passengers)

// Pedestrians killed variable operations
label var countpedkilled "Pedestrian Killed Count"
notes countpedkilled : Number of killed pedestrian victims

// Pedestrians injured variable operations
label var countpedinj "Pedestrian Injured Count"
notes countpedinj : Number of injured pedestrian victims

// Bicyclists killed variable operations
label var countbickilled "Bicyclists Killed Count"
notes countbickilled : Number of killed bicyclists

// Bicyclists injured variable operations
label var countbicinj "Bicyclists Injured Count"
notes countbicinj : Number of injured bicyclists

// Motorcyclists killed variable operations
label var countmckilled "Motorcyclist Killed Count"
notes countmckilled : Number of killed motorcyclists

// Motorcyclists injured variable operations
label var countmcinj "Motorcyclist Injured Count"
notes countmcinj : Number of injured motorcyclists



*************** Collision Characteristics (Crash Level) ***************

// Primary crash factor variable operations
ren primarycollfactor temp
gen byte primarycollfactor = 0 if temp == "-"
replace primarycollfactor = 1 if temp == "A"
replace primarycollfactor = 2 if temp == "B"
replace primarycollfactor = 3 if temp == "C"
replace primarycollfactor = 4 if temp == "D"
replace primarycollfactor = 5 if temp == "E"
order primarycollfactor, before(temp)
drop temp
label define primarycollfactor 0 "Not Stated" 1 "Vehicle Code Violation" 2 "Other Improper Driving" 3 "Other than Driver" 4 "Unknown" 5 "Fell Asleep"
label values primarycollfactor primarycollfactor
label var primarycollfactor "Primary Crash Factor"
notes primarycollfactor : The primary cause of the crash

// Type of crash variable operations
ren typeofcoll temp
gen byte typeofcoll = 0 if temp == "-"
replace typeofcoll = 1 if temp == "A"
replace typeofcoll = 2 if temp == "B"
replace typeofcoll = 3 if temp == "C"
replace typeofcoll = 4 if temp == "D"
replace typeofcoll = 5 if temp == "E"
replace typeofcoll = 6 if temp == "F"
replace typeofcoll = 7 if temp == "G"
replace typeofcoll = 8 if temp == "H"
order typeofcoll, before(temp)
drop temp
label define typeofcoll 0 "Not Stated" 1 "Head-on" 2 "Sideswipe" 3 "Rear-end" 4 "Broadside" 5 "Hit object" 6 "Overturned" 7 "Vehicle/pedestrian" 8 "Other"
label values typeofcoll typeofcoll
label var typeofcoll "Type of Crash"
notes typeofcoll : The general type of crash as determined by the first injury or damage-causing event

// Pedestrian crash variable operations
ren pedaccident temp
gen byte pedaccident = 1 if temp == "Y"
replace pedaccident = 0 if temp == ""
order pedaccident, before(temp)
drop temp
label define pedaccident 0 "No" 1 "Yes"
label values pedaccident pedaccident
label var pedaccident "Pedestrian Crash"
notes pedaccident : Indicates whether the crash involved a pedestrian

// Bicycle crash variable operations
ren bicaccident temp
gen byte bicaccident = 1 if temp == "Y"
replace bicaccident = 0 if temp == ""
order bicaccident, before(temp)
drop temp
label define bicaccident 0 "No" 1 "Yes"
label values bicaccident bicaccident
label var bicaccident "Bicycle Crash"
notes bicaccident : Indicates whether the crash involved a bicycle

// Motorcycle accident variable operations
ren mcaccident temp
gen byte mcaccident = 1 if temp == "Y"
replace mcaccident = 0 if temp == ""
order mcaccident, before(temp)
drop temp
label define mcaccident 0 "No" 1 "Yes"
label values mcaccident mcaccident
label var mcaccident "Motorcycle Crash"
notes mcaccident : Indicates whether the crash involved a motorcycle

// Truck accident variable operations
ren truckaccident temp
gen byte truckaccident = 1 if temp == "Y"
replace truckaccident = 0 if temp == ""
order truckaccident, before(temp)
drop temp
label define truckaccident 0 "No" 1 "Yes"
label values truckaccident truckaccident
label var truckaccident "Truck Crash"
notes truckaccident : Indicates whether the crash involved a big truck

// Hit and run variable operations
ren hitandrun temp
gen byte hitandrun = 0 if temp == "N"
replace hitandrun = 1 if temp == "M"
replace hitandrun = 2 if temp == "F"
order hitandrun, before(temp)
drop temp
label define hitandrun 0 "Not Hit and Run" 1 "Misdemeanor" 2 "Felony"
label values hitandrun hitandrun
label var hitandrun "Hit and Run"
notes hitandrun : A flag to indicate the severity of hit-and-run crash. Felony hit-and-run resulted in injury or death to other parties. Misdemeanor hit-and-run did not result in injury or death to other parties

// Alcohol involved variable operations
ren alcoholinvolved temp
gen byte alcoholinvolved = 1 if temp == "Y"
replace alcoholinvolved = 0 if temp == ""
order alcoholinvolved, before(temp)
drop temp
label define alcoholinvolved 0 "No" 1 "Yes"
label values alcoholinvolved alcoholinvolved
label var alcoholinvolved "Alcohol Inovlved"
notes alcoholinvolved : Indicates whether the crash involved a party that had been drinking. Note - a passenger does not count as a party



*************** Police Response Operations (Crash Level) ***************

// Jurisdiction variable operations
label var juris "Jurisdiction"
notes juris : Law enforcement agency that has jurisdiction over the crash

// Officer id variable operations
label var officerid "Officer ID"
notes officerid : The badge number of the officer who wrote the crash report

// Reporting district variable operations
label var reportingdistrict "Reporting District"
notes reportingdistrict : Reporting District on the crash report

// chp shift variable operations
label define chpshift  1 "0600 thru 1359" 2 "1400 thru 2159" 3 "2200 thru 0559" 4 "CHP Not Stated" 5 "Not CHP"
label values chpshift chpshift
label var chpshift "CHP Shift"
notes chpshift : CHP shift at the time of the crash

// County city location
label var cntycityloc "County City Location"
notes cntycityloc : The city or unincorporated county where the crash occurred

// Special condition variable operations
label define specialcond  0 "Not Above" 1 "Schoolbus on Public Roadway" 2 "State University (Also SFIA)" 3 "Schoolbus Not on Public Roadway" 4 "Offroad (Unimproved)" 5 "Vista Point or Rest Area or Sales or Inspection Facility" 6 "Other Public Access (Improved)"
label values specialcond specialcond
label var specialcond "Special Condition"
notes specialcond : A computed value. O means not private property

// Beat type variable operations
label define beattype  0 "Not CHP" 1 "CHP State Highway" 2 "CHP County RoadLine" 3 "CHP County RoadArea" 4 "Schoolbus on City Roadway" 5 "Schoolbus not on Public Roadway" 6 "Offroad (Unimproved)" 7 "Vista Point or Rest Area or Scales or Inspection Facility" 8 "Other Public Access (Improved)"
label values beattype beattype
label var beattype "Beat Type"
notes beattype : Location of crash based on beat

//chp beat type variable operations
ren chpbeattype temp
gen byte chpbeattype = 0 if temp == "0"
replace chpbeattype = 1 if temp == "1"
replace chpbeattype = 2 if temp == "2"
replace chpbeattype = 3 if temp == "3"
replace chpbeattype = 4 if temp == "4"
replace chpbeattype = 5 if temp == "5"
replace chpbeattype = 6 if temp == "6"
replace chpbeattype = 7 if temp == "7"
replace chpbeattype = 8 if temp == "8"
replace chpbeattype = 0 if temp == "9"
order chpbeattype, before(temp)
drop temp
label define chpbeattype 0 "Not CHP" 1 "Interstate" 2 "US Highway" 3 "State Route" 4 "County Road Line" 5 "County Road Area" 6 "US Highway" 7 "State Route" 8 "County RoadLine" 9 "County RoadArea"
label values chpbeattype chpbeattype
label var chpbeattype "CHP Beat Type"
notes chpbeattype : Location of crash based on beat

// chp beat class variable operations
label define chpbeatclass  0 "Not CHP" 1 "CHP Primary" 2 "CHP Other"
label values chpbeatclass chpbeatclass
label var chpbeatclass "CHP Beat Class"
notes chpbeatclass : Location of crash based on beat

// Beat number variable operations
label var beatnumber "Beat Number"
notes beatnumber : Beat of the officer who reported the crash



*************** Site Characteristics and Conditions (Crash Level) ***************

// Primary road variable operations
label var primaryrd "Primary Road"
notes primaryrd : The name of the roadway on which the crash occurred

// Secondary road variable operations
label var secondaryrd "Secondary Road"
notes secondaryrd : The name of the roadway that intersects the primary roadway

// Distance operations
label var distance "Distance"
notes distance : Distance of the crash from the intersection with the secondary roadway in ft

// Direction variable operations
ren direction temp
gen byte direction = 0 if temp == ""
replace direction = 1 if temp == "N"
replace direction = 2 if temp == "S"
replace direction = 3 if temp == "E"
replace direction = 4 if temp == "W"
order direction, before(temp)
drop temp
label define direction 0 "Not Defined" 1 "North" 2 "South" 3 "East" 4 "West"
label values direction direction
label var direction "Direction"
notes direction : Direction of the crash from the intersection with the secondary roadway

// Intersection variable operations
ren intersection temp
gen byte intersection = 0 if temp == "N"
replace intersection = 1 if temp == "Y"
replace intersection = . if temp == "-"
order intersection, before(temp)
drop temp
label define intersection 0 "Not intersection" 1 "Intersection"
label values intersection intersection
label var intersection "Intersection"
notes intersection : A flag that denotes if the crash occurred at the intersection with the secondary roadway

// Weather1 variable operations
ren weather1 temp
gen byte weather1 = 0 if temp == "-"
replace weather1 = 1 if temp == "A"
replace weather1 = 2 if temp == "B"
replace weather1 = 3 if temp == "C"
replace weather1 = 4 if temp == "D"
replace weather1 = 5 if temp == "E"
replace weather1 = 6 if temp == "G"
replace weather1 = 7 if temp == "F"
order weather1, before(temp)
drop temp
label define weather1 0 "Not Stated" 1 "Clear" 2 "Cloudy" 3 "Raining" 4 "Snowing" 5 "Fog" 6 "Wind" 7 "Other"
label values weather1 weather1
label var weather1 "Weather 1"
notes weather1 : Weather condition at the time of the crash

// Weather2 variable operations
ren weather2 temp
gen byte weather2 = 0 if temp == "-"
replace weather2 = 1 if temp == "A"
replace weather2 = 2 if temp == "B"
replace weather2 = 3 if temp == "C"
replace weather2 = 4 if temp == "D"
replace weather2 = 5 if temp == "E"
replace weather2 = 6 if temp == "G"
replace weather2 = 7 if temp == "F"
order weather2, before(temp)
drop temp
label define weather2 0 "Not Stated" 1 "Clear" 2 "Cloudy" 3 "Raining" 4 "Snowing" 5 "Fog" 6 "Wind" 7 "Other"
label values weather2 weather2
label var weather2 "Weather 2"
notes weather2 : Additional weather condition at the time of the crash

// Combined weather variable operations
gen byte weathercombined = weather1 * 10 + weather2
order weathercombined, after(weather2)
label define weathercombined  0 "Not Stated" 10 "Clear" 12 "Clear Cloudy" 13 "Clear Other" 14 "Clear Wind" 15 "Clear Raining" 16 "Clear Snowing" 17 "Clear Fog" 20 "Cloudy" 21 "Cloudy Clear" 23 "Cloudy Other" 24 "Cloudy Wind" 25 "Cloudy Raining" 26 "Cloudy Snowing" 27 "Cloudy Fog" 30 "Other" 31 "Other Clear" 32 "Other Cloudy" 34 "Other Wind" 35 "Other Raining" 36 "Other Snowing" 37 "Other Fog" 40 "Wind" 41 "Wind Clear" 42 "Wind Cloudy" 43 "Wind Other" 45 "Wind Raining" 46 "Wind Snowing" 47 "Wind Fog" 50 "Raining" 51 "Raining Clear" 52 "Raining Cloudy" 53 "Raining Other" 54 "Raining Wind" 56 "Raining Snowing" 57 "Raining Fog" 60 "Snowing" 61 "Snowing Clear" 62 "Snowing Cloudy" 63 "Snowing Other" 64 "Snowing Wind" 65 "Snowing Raining" 67 "Snowing Fog" 70 "Fog" 71 "Fog Clear" 72 "Fog Cloudy" 73 "Fog Other" 74 "Fog Wind" 75 "Fog Raining" 76 "Fog Snowing"
label values weathercombined weathercombined
label var weathercombined "Combined Weather Conditions"
notes weathercombined : Combined Weather Conditions from WEATHER_1 and WEATHER_2 fields in numeric codes by weather conditions severity

// Road surface variable operations
ren roadsurface temp
gen byte roadsurface = 0 if temp == "-"
replace roadsurface = 1 if temp == "A"
replace roadsurface = 2 if temp == "B"
replace roadsurface = 3 if temp == "C"
replace roadsurface = 4 if temp == "D"
replace roadsurface = 5 if temp == "O"
order roadsurface, before(temp)
drop temp
label define roadsurface 0 "Not Stated" 1 "Dry" 2 "Wet" 3 "Snowy or Icy" 4 "Slippery (muddy, oily, etc)" 5 "Other"
label values roadsurface roadsurface
label var roadsurface "Road Surface"
notes roadsurface : Roadway surface condition at the time of the crash in the traffic lane(s) involved

// Road conditions 1 variable operations
ren roadcond1 temp
gen byte roadcond1 = 0 if temp == "-"
replace roadcond1 = 1 if temp == "A"
replace roadcond1 = 2 if temp == "B"
replace roadcond1 = 3 if temp == "C"
replace roadcond1 = 4 if temp == "D"
replace roadcond1 = 5 if temp == "E"
replace roadcond1 = 6 if temp == "F"
replace roadcond1 = 7 if temp == "G"
replace roadcond1 = 8 if temp == "H"
order roadcond1, before(temp)
drop temp
label define roadcond1 0 "Not Stated" 1 "Holes, deep ruts" 2 "Loose material on roadway" 3 "obstruction on roadway" 4 "Construction or repair zone" 5 "Reduced roadaway width" 6 "Flooded" 7 "Other" 8 "No unusual condition"
label values roadcond1 roadcond1
label var roadcond1 "Road Condition 1"
notes roadcond1 : Roadway condition at the time of the crash in the traffic lane(s) involved

// Road conditions 2 variable operations
ren roadcond2 temp
gen byte roadcond2 = 0 if temp == "-"
replace roadcond2 = 1 if temp == "A"
replace roadcond2 = 2 if temp == "B"
replace roadcond2 = 3 if temp == "C"
replace roadcond2 = 4 if temp == "D"
replace roadcond2 = 5 if temp == "E"
replace roadcond2 = 6 if temp == "F"
replace roadcond2 = 7 if temp == "G"
replace roadcond2 = 8 if temp == "H"
order roadcond2, before(temp)
drop temp
label define roadcond2 0 "Not Stated" 1 "Holes, deep ruts" 2 "Loose material on roadway" 3 "obstruction on roadway" 4 "Construction or repair zone" 5 "Reduced roadaway width" 6 "Flooded" 7 "Other" 8 "No unusual condition"
label values roadcond2 roadcond2
label var roadcond2 "Road Condition 2"
notes roadcond2 : Second roadway condition at the time of the crash in the traffic lane(s) involved

// Lighting conditions variable operations
ren lighting temp
gen byte lighting = 0 if temp == "-"
replace lighting = 1 if temp == "A"
replace lighting = 2 if temp == "B"
replace lighting = 3 if temp == "C"
replace lighting = 4 if temp == "D"
replace lighting = 5 if temp == "E"
order lighting, before(temp)
drop temp
label define lighting 0 "Not stated" 1 "Daylight" 2 "Dusk-dawn" 3 "Dark-street lights" 4 "Dark-no street lights" 5 " Dark-street lights not functioning"
label values lighting lighting
label var lighting "Lighting"
notes lighting : Lighting conditions at the crash location and the time of the crash

// Control device variable operations
ren controldevice temp
gen byte controldevice = 0 if temp == "-"
replace controldevice = 1 if temp == "A"
replace controldevice = 2 if temp == "B"
replace controldevice = 3 if temp == "C"
replace controldevice = 4 if temp == "D"
order controldevice, before(temp)
drop temp
label define controldevice 0 "Not Stated" 1 "Functioning" 2 "Not functioning" 3 "Obscured" 4 "None"
label values controldevice controldevice
label var controldevice "Control Device"
notes controldevice : Presence and condition of crash related traffic control devices at the time of the crash. Control devices include regulatory, warning, and construction sings. This excludes striping and officers or other persons directing traffic

// State highway indicator variable operations
ren statehwyind temp
gen byte statehwyind = 0 if temp=="N"
replace statehwyind = 1 if temp=="Y"
replace statehwyind = . if temp==""
order statehwyind, before(temp)
drop temp
label define statehwyind 0 "No" 1 "Yes"
label values statehwyind statehwyind
label var statehwyind "State Highway Indicator"
notes statehwyind : A flag to indicate whether the crash is on or near a state highway

// Side of highway variable operations
ren sideofhwy temp
gen byte sideofhwy = 0 if temp == ""
replace sideofhwy = 1 if temp == "N"
replace sideofhwy = 2 if temp == "S"
replace sideofhwy = 3 if temp == "E"
replace sideofhwy = 4 if temp == "W"
replace sideofhwy = 5 if temp == "L"
replace sideofhwy = 6 if temp == "R"
order sideofhwy, before(temp)
drop temp
label define sideofhwy 0 "Not Stated" 1 "North" 2 "South" 3 "East" 4 "West" 5 "Left" 6 "Right"
label values sideofhwy sideofhwy
label var sideofhwy "Side of Highway"
notes sideofhwy : Code provided by Caltrans Coders, applies to divided highway, based on nominal direction of route, for single vehicle is same as nominal direction of travel, overruled by impact with second vehicle after crossing median

// Tow away variable operations
ren towaway temp
gen byte towaway = 0 if temp == "N"
replace towaway = 1 if temp == "Y"
replace towaway = . if temp ==""
order towaway, before(temp)
drop temp
label define towaway 0 "No" 1 "Yes"
label values towaway towaway
label var towaway "Tow Away"
notes towaway : A flag to indicate whether the vehicle was towed away from the crash scene



*************** Causal Characteristics (Crash Level) ***************

// PCF violation code variable operations
ren pcfcodeofviol temp
gen byte pcfcodeofviol = 0 if temp == "-"
replace pcfcodeofviol = 1 if temp == "B"
replace pcfcodeofviol = 2 if temp == "C"
replace pcfcodeofviol = 3 if temp == "H"
replace pcfcodeofviol = 4 if temp == "I"
replace pcfcodeofviol = 5 if temp == "O"
replace pcfcodeofviol = 6 if temp == "P"
replace pcfcodeofviol = 7 if temp == "S"
replace pcfcodeofviol = 8 if temp == "W"
replace pcfcodeofviol = . if temp == ""
order pcfcodeofviol, before(temp)
drop temp
label define pcfcodeofviol 0 "Not Stated" 1 "Business and Professions" 2 "Vehicle" 3 "City Health and Safety" 4 "City Ordinance" 5 "County Ordinance" 6 "Penal" 7 "Streets and Highways" 8 "Welfare and Institutions"
label values pcfcodeofviol pcfcodeofviol
label var pcfcodeofviol "PCF Violation Code"
notes pcfcodeofviol : The law code that was violated and was the primary cause of the crash

// PCF violation category variable operations
ren pcfviolcategory temp
gen byte pcfviolcategory = 0 if temp == "0"
replace pcfviolcategory = 1 if temp == "1"
replace pcfviolcategory = 2 if temp == "2"
replace pcfviolcategory = 3 if temp == "3"
replace pcfviolcategory = 4 if temp == "4"
replace pcfviolcategory = 5 if temp == "5"
replace pcfviolcategory = 6 if temp == "6"
replace pcfviolcategory = 7 if temp == "7"
replace pcfviolcategory = 8 if temp == "8"
replace pcfviolcategory = 9 if temp == "9"
replace pcfviolcategory = 10 if temp == "10"
replace pcfviolcategory = 11 if temp == "11"
replace pcfviolcategory = 12 if temp == "12"
replace pcfviolcategory = 13 if temp == "13"
replace pcfviolcategory = 14 if temp == "14"
replace pcfviolcategory = 15 if temp == "15"
replace pcfviolcategory = 16 if temp == "16"
replace pcfviolcategory = 17 if temp == "17"
replace pcfviolcategory = 18 if temp == "18"
replace pcfviolcategory = 21 if temp == "21"
replace pcfviolcategory = 22 if temp == "22"
replace pcfviolcategory = 23 if temp == "23"
replace pcfviolcategory = 24 if temp == "24"
replace pcfviolcategory = 99 if temp == "-"
order pcfviolcategory, before(temp)
drop temp
label define pcfviolcategory 0 "Unknown" 1 "Driving or bicycling under the influence of alcohol or drugs" 2 "Impeding traffic" 3 "Unsafe speed" 4 "Following too closely" 5 "Wrong side of the road" 6 "Improper passing" 7 "Unsafe lane change" 8 "Improper turning" 9 "Automobile right of way" 10 "Pedestrian right of way" 11 "Pedestrian violation" 12 "Traffic signals and signs" 13 "hazardous parking" 14 "Lights" 15 "Brakes" 16 "Other equipment" 17 "Othe hazardous violation" 18 "Other than driver or pedestrian" 21 "Unsafe starting or backing" 22 "Other improper driving" 23 "Pedestrian or other under the influence of alcohol or drugs" 24 "Fell asleep" 99 "Not Stated"
label values pcfviolcategory pcfviolcategory
label var pcfviolcategory "PCF Violation Category"
notes pcfviolcategory : A value computed from the law section that was given as the primary cause of the crash

// PCF violation variable operations
label var pcfviolation "PCF Violation"
notes pcfviolation : The law section given as the primary cause of the crash. The subsection is in the data element pcf_viol_subsection

// PCF violation subsection variable operations
label var pcfviolsubsection "PCF Violation Subsection"
notes pcfviolsubsection : The subsection of the law section given as the primary cause of the crash in the data element pcf_violation

// MVIW variable operations
ren mviw temp
gen byte mviw = 0 if temp == "0"
replace mviw = 1 if temp == "1"
replace mviw = 2 if temp == "2"
replace mviw = 3 if temp == "3"
replace mviw = 4 if temp == "4"
replace mviw = 5 if temp == "5"
replace mviw = 6 if temp == "6"
replace mviw = 7 if temp == "7"
replace mviw = 8 if temp == "8"
replace mviw = 9 if temp == "9"
replace mviw = 10 if temp == "A"
replace mviw = 11 if temp == "B"
replace mviw = 12 if temp == "C"
replace mviw = 13 if temp == "D"
replace mviw = 14 if temp == "E"
replace mviw = 15 if temp == "F"
replace mviw = 16 if temp == "G"
replace mviw = 17 if temp == "H"
replace mviw = 18 if temp == "I"
replace mviw = 19 if temp == "J"
replace mviw = 99 if temp == "-"
order mviw, before(temp)
drop temp
label define mviw 0 "Non-collision and additional object" 1 "Pedestrian and additional object" 2 "Other motor vehicle and additional object" 3 "Motor vehicle on other roadway and additional object" 4 "Parked motor vehicle and additional object" 5 "Train and additional object" 6 "Bicycle and additional object" 7 "Animal and additional object" 8 "Fixed object and additional object" 9 "Other object and additional object" 10 "Non-collision" 11 "Pedestrian" 12 "Other motor vehicle" 13 "Motor vehicle on other roadway" 14 "Parked motor vehicle" 15 "Train" 16 "Bicycle" 17 "Animal" 18 "Fixed object" 19 "Other object" 99 "Not stated"
label values mviw mviw
label var mviw "Motor Vehicle Involved With"
notes mviw : Describes what, in conjunction with a motor vehicle in-transport, produced the first injury or damage-causing event, on or off the road

// Ped action variable operations
ren pedaction temp
gen byte pedaction = 0 if temp == "-"
replace pedaction = 1 if temp == "A"
replace pedaction = 2 if temp == "B"
replace pedaction = 3 if temp == "C"
replace pedaction = 4 if temp == "D"
replace pedaction = 5 if temp == "E"
replace pedaction = 6 if temp == "F"
replace pedaction = 7 if temp == "G"
order pedaction, before(temp)
drop temp
label define pedaction 0 "Not stated" 1 "No pedestrian involved" 2 "Crossing in crosswalk at intersection" 3 "Crossing in crosswalk not at intersection" 4 "Crossing not in crosswalk" 5 "In road, including shoulder" 6 "Not in road" 7 "Approaching or leaving school bus"
label values pedaction pedaction
label var pedaction "Ped Action"
notes pedaction : The action just prior to the crash of the first pedestrian injured or otherwise involved

// Not private property variable operations
ren notprivateproperty temp
gen byte notprivateproperty = 0 if (temp == "" | temp == "N")
replace notprivateproperty = 1 if temp == "Y"
order notprivateproperty, before(temp)
drop temp
label define notprivateproperty 0 "No" 1 "Yes"
label values notprivateproperty notprivateproperty
label var notprivateproperty "Not Private Property"
notes notprivateproperty : Y indicates that the crash did not occur on private property

// Statewide veiche type at fault variable operations
ren stwdvehtypeatfault temp
gen byte stwdvehtypeatfault = 0 if temp == "-"
replace stwdvehtypeatfault = 1 if temp == "A"
replace stwdvehtypeatfault = 2 if temp == "B"
replace stwdvehtypeatfault = 3 if temp == "C"
replace stwdvehtypeatfault = 4 if temp == "D"
replace stwdvehtypeatfault = 5 if temp == "E"
replace stwdvehtypeatfault = 6 if temp == "F"
replace stwdvehtypeatfault = 7 if temp == "G"
replace stwdvehtypeatfault = 8 if temp == "H"
replace stwdvehtypeatfault = 9 if temp == "I"
replace stwdvehtypeatfault = 10 if temp == "J"
replace stwdvehtypeatfault = 11 if temp == "K"
replace stwdvehtypeatfault = 12 if temp == "L"
replace stwdvehtypeatfault = 13 if temp == "M"
replace stwdvehtypeatfault = 14 if temp == "N"
replace stwdvehtypeatfault = 15 if temp == "O"
order stwdvehtypeatfault, before(temp)
drop temp
label define stwdvehtypeatfault 0 "Not stated" 1 "Passenger car/station wagon" 2 "Passenger car with trailer" 3 "Motorcycle/scooter" 4 "pickup or panel truck" 5 "Pickup or panel truck with trailer" 6 "Truck or truck tractor" 7 "Truck or truck tractor with trrailer" 8 "School bus" 9 "Other bus" 10 "Emergency vehicle" 11 "Highway construction equipment" 12 "Bicycle" 13 "Other vehicle" 14 "Pedestrian" 15 "Moped"
label values stwdvehtypeatfault stwdvehtypeatfault
label var stwdvehtypeatfault "Statewide Vehicle Type at Fault"
notes stwdvehtypeatfault : Indicates the Statewide Vehicle Type of the party who is at fault

// CHP vehicle type at fault variable operations
ren chpvehtypeatfault temp
gen byte chpvehtypeatfault = 0 if temp == "-"
replace chpvehtypeatfault = 1 if temp == "1"
replace chpvehtypeatfault = 2 if temp == "2"
replace chpvehtypeatfault = 3 if temp == "3"
replace chpvehtypeatfault = 4 if temp == "4"
replace chpvehtypeatfault = 5 if temp == "5"
replace chpvehtypeatfault = 6 if temp == "6"
replace chpvehtypeatfault = 7 if temp == "7"
replace chpvehtypeatfault = 8 if temp == "8"
replace chpvehtypeatfault = 9 if temp == "9"
replace chpvehtypeatfault = 10 if temp == "10"
replace chpvehtypeatfault = 11 if temp == "11"
replace chpvehtypeatfault = 12 if temp == "12"
replace chpvehtypeatfault = 13 if temp == "13"
replace chpvehtypeatfault = 14 if temp == "14"
replace chpvehtypeatfault = 15 if temp == "15"
replace chpvehtypeatfault = 16 if temp == "16"
replace chpvehtypeatfault = 17 if temp == "17"
replace chpvehtypeatfault = 18 if temp == "18"
replace chpvehtypeatfault = 19 if temp == "19"
replace chpvehtypeatfault = 20 if temp == "20"
replace chpvehtypeatfault = 21 if temp == "21"
replace chpvehtypeatfault = 22 if temp == "22"
replace chpvehtypeatfault = 23 if temp == "23"
replace chpvehtypeatfault = 24 if temp == "24"
replace chpvehtypeatfault = 25 if temp == "25"
replace chpvehtypeatfault = 26 if temp == "26"
replace chpvehtypeatfault = 27 if temp == "27"
replace chpvehtypeatfault = 28 if temp == "28"
replace chpvehtypeatfault = 29 if temp == "29"
replace chpvehtypeatfault = 30 if temp == "30"
replace chpvehtypeatfault = 31 if temp == "31"
replace chpvehtypeatfault = 32 if temp == "32"
replace chpvehtypeatfault = 33 if temp == "33"
replace chpvehtypeatfault = 34 if temp == "34"
replace chpvehtypeatfault = 35 if temp == "35"
replace chpvehtypeatfault = 36 if temp == "36"
replace chpvehtypeatfault = 37 if temp == "37"
replace chpvehtypeatfault = 38 if temp == "38"
replace chpvehtypeatfault = 39 if temp == "39"
replace chpvehtypeatfault = 40 if temp == "40"
replace chpvehtypeatfault = 41 if temp == "41"
replace chpvehtypeatfault = 42 if temp == "42"
replace chpvehtypeatfault = 43 if temp == "43"
replace chpvehtypeatfault = 44 if temp == "44"
replace chpvehtypeatfault = 45 if temp == "45"
replace chpvehtypeatfault = 46 if temp == "46"
replace chpvehtypeatfault = 47 if temp == "47"
replace chpvehtypeatfault = 48 if temp == "48"
replace chpvehtypeatfault = 49 if temp == "49"
replace chpvehtypeatfault = 50 if temp == "50"
replace chpvehtypeatfault = 51 if temp == "51"
replace chpvehtypeatfault = 52 if temp == "52"
replace chpvehtypeatfault = 53 if temp == "53"
replace chpvehtypeatfault = 54 if temp == "54"
replace chpvehtypeatfault = 55 if temp == "55"
replace chpvehtypeatfault = 56 if temp == "56"
replace chpvehtypeatfault = 57 if temp == "57"
replace chpvehtypeatfault = 58 if temp == "58"
replace chpvehtypeatfault = 59 if temp == "59"
replace chpvehtypeatfault = 60 if temp == "60"
replace chpvehtypeatfault = 61 if temp == "61"
replace chpvehtypeatfault = 62 if temp == "62"
replace chpvehtypeatfault = 63 if temp == "63"
replace chpvehtypeatfault = 64 if temp == "64"
replace chpvehtypeatfault = 65 if temp == "65"
replace chpvehtypeatfault = 66 if temp == "66"
replace chpvehtypeatfault = 71 if temp == "71"
replace chpvehtypeatfault = 72 if temp == "72"
replace chpvehtypeatfault = 73 if temp == "73"
replace chpvehtypeatfault = 75 if temp == "75"
replace chpvehtypeatfault = 76 if temp == "76"
replace chpvehtypeatfault = 77 if temp == "77"
replace chpvehtypeatfault = 78 if temp == "78"
replace chpvehtypeatfault = 79 if temp == "79"
replace chpvehtypeatfault = 81 if temp == "81"
replace chpvehtypeatfault = 82 if temp == "82"
replace chpvehtypeatfault = 83 if temp == "83"
replace chpvehtypeatfault = 85 if temp == "85"
replace chpvehtypeatfault = 86 if temp == "86"
replace chpvehtypeatfault = 87 if temp == "87"
replace chpvehtypeatfault = 88 if temp == "88"
replace chpvehtypeatfault = 89 if temp == "89"
replace chpvehtypeatfault = 91 if temp == "91"
replace chpvehtypeatfault = 93 if temp == "93"
replace chpvehtypeatfault = 94 if temp == "94"
replace chpvehtypeatfault = 95 if temp == "95"
replace chpvehtypeatfault = 96 if temp == "96"
replace chpvehtypeatfault = 97 if temp == "97"
replace chpvehtypeatfault = 98 if temp == "98"
replace chpvehtypeatfault = 99 if temp == "99"
order chpvehtypeatfault, before(temp)
drop temp
label define chpvehtypeatfault 0 "Not Stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 83 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chpvehtypeatfault chpvehtypeatfault
label var chpvehtypeatfault "CHP Vehicle Type at Fault"
notes chpvehtypeatfault : Indicates the CHP Vehicle Type of the party whi is at fault

// Primary ramp variable operations
ren primaryramp temp
gen byte primaryramp = 0 if temp == "-"
replace primaryramp = 1 if temp == "TO"
replace primaryramp = 2 if temp == "FR"
replace primaryramp = 3 if temp == "NF"
replace primaryramp = 4 if temp == "SF"
replace primaryramp = 5 if temp == "EF"
replace primaryramp = 6 if temp == "WF"
replace primaryramp = 7 if temp == "NO"
replace primaryramp = 8 if temp == "SO"
replace primaryramp = 9 if temp == "EO"
replace primaryramp = 10 if temp == "WO"
replace primaryramp = 11 if temp == "TR"
replace primaryramp = 12 if temp == "CO"
replace primaryramp = 13 if temp == "CN"
order primaryramp, before(temp)
drop temp
label define primaryramp 0 "Not stated" 1 "To" 2 "From" 3 "North off ramp" 4 "South off ramp" 5 "East off ramp" 6 "West off ramp" 7 "North on ramp" 8 "South on ramp" 9 "East on ramp" 10 "West on ramp" 11 "Transition" 12 "Collector" 13 "Connector"
label values primaryramp primaryramp
label var primaryramp "Primary Ramp"
notes primaryramp : A description of the ramp, if any, on primary roadway. This value is computed by the key operator from information on the crash report

// Secondary ramp variable operations
ren secondaryramp temp
gen byte secondaryramp = 0 if temp == "-"
replace secondaryramp = 1 if temp == "TO"
replace secondaryramp = 2 if temp == "FR"
replace secondaryramp = 3 if temp == "NF"
replace secondaryramp = 4 if temp == "SF"
replace secondaryramp = 5 if temp == "EF"
replace secondaryramp = 6 if temp == "WF"
replace secondaryramp = 7 if temp == "NO"
replace secondaryramp = 8 if temp == "SO"
replace secondaryramp = 9 if temp == "EO"
replace secondaryramp = 10 if temp == "WO"
replace secondaryramp = 11 if temp == "TR"
replace secondaryramp = 12 if temp == "CO"
replace secondaryramp = 13 if temp == "CN"
order secondaryramp, before(temp)
drop temp
label define secondaryramp 0 "Not stated" 1 "To" 2 "From" 3 "North off ramp" 4 "South off ramp" 5 "East off ramp" 6 "West off ramp" 7 "North on ramp" 8 "South on ramp" 9 "East on ramp" 10 "West on ramp" 11 "Transition" 12 "Collector" 13 "Connector"
label values secondaryramp secondaryramp
label var secondaryramp "Secondary Ramp"
notes secondaryramp : A description of the ramp, if any, on secondary roadway. This value is computed by the key operator from information on the crash report



*************** Basic Party Characteristics (Party Level) ***************

// Party type variable operations
ren partytype temp
gen byte partytype = 0 if temp == "-"
replace partytype = 1 if temp == "1"
replace partytype = 2 if temp == "2"
replace partytype = 3 if temp == "3"
replace partytype = 4 if temp == "4"
replace partytype = 5 if temp == "5"
replace partytype = 6 if temp == "6"
order partytype, before(temp)
drop temp
label define partytype 0 "Not stated" 1 "Driver (including hit and run)" 2 "Pedestrian" 3 "Parked vehicle" 4 "Bicyclist" 5 "Other" 6 "Operator"
label values partytype partytype
label var partytype "Party Type"
notes partytype : Involved party type

// At fault variable operations
ren atfault temp
gen byte atfault = 0 if temp == "N"
replace atfault = 1 if temp == "Y"
order atfault, before(temp)
drop temp
label define atfault 0 "No" 1 "Yes"
label values atfault atfault
label var atfault "At Fault"
notes atfault : Indicates whether the party was at fault in the crash

// Party sex variable operations
ren partysex temp
gen byte partysex = 0 if temp == "-"
replace partysex = 1 if temp == "M"
replace partysex = 2 if temp == "F"
replace partysex = 3 if temp == "X"
order partysex, before(temp)
drop temp
label define partysex 0 "Not stated" 1 "Male" 2 "Female" 3 "Nonbinary"
label values partysex partysex
label var partysex "Party Sex"
notes partysex : The gender of the party

// Party age variable operations
label define partyage 998 "Unknown"
label values partyage party_age
label var partyage "Party Age"
notes partyage : The age of the party at the time of the crash

// Party race variable operations
ren partyrace temp
gen byte partyrace = 1 if temp == "A"
replace partyrace = 2 if temp == "B"
replace partyrace = 3 if temp == "H"
replace partyrace = 4 if temp == "W"
replace partyrace = 5 if temp == "O"
order partyrace, before(temp)
drop temp
label define partyrace 1 "Asian" 2 "Black" 3 "Hispanic" 4 "White" 5 "Other"
label values partyrace partyrace
label var partyrace "Party Race"
notes partyrace : The party's race based on the reporting officer's judgment

// Party number killed variable operations
label var partynumberkilled "Party Number Killed"
notes partynumberkilled : Number of killed victims in the party

// Party number injured variable operations
label var partynumberinj "Party Number Injured"
notes partynumberinj : Number of injured victims in the party



*************** Collision Factors (Party Level) ***************

// Inattention variable operations
ren inattention temp
gen byte inattention = 0 if temp == "-"
replace inattention = 1 if temp == "A"
replace inattention = 2 if temp == "B"
replace inattention = 3 if temp == "C"
replace inattention = 4 if temp == "D"
replace inattention = 5 if temp == "E"
replace inattention = 6 if temp == "F"
replace inattention = 7 if temp == "G"
replace inattention = 8 if temp == "H"
replace inattention = 9 if temp == "I"
replace inattention = 10 if temp == "J"
replace inattention = 11 if temp == "K"
replace inattention = 12 if temp == "P"
order inattention, before(temp)
drop temp
label define inattention 0 "Not stated" 1 "Cell phone handheld" 2 "Cell phone hands-free" 3 "Electronic equipment" 4 "Radio/CD" 5 "Smoking" 6 "Eating" 7 "Children" 8 "Animal" 9 "Personal hygiene" 10 "Reading" 11 "Other" 12 "Cell phone"
label values inattention inattention
label var inattention "Inattention"
notes inattention : Type of inattention

// Party sobriety variable operations
ren partysobriety temp
gen byte partysobriety = 0 if temp == "-"
replace partysobriety = 1 if temp == "A"
replace partysobriety = 2 if temp == "B"
replace partysobriety = 3 if temp == "C"
replace partysobriety = 4 if temp == "D"
replace partysobriety = 5 if temp == "G"
replace partysobriety = 6 if temp == "H"
order partysobriety, before(temp)
drop temp
label define partysobriety 0 "Not Stated" 1 "Had not been drinking" 2 "Had been drinking under influence" 3 "Had been drinking, not under influence" 4 "Had been drinking, impairment unknown" 5 "Impairment unknown" 6 "Not applicable"
label values partysobriety partysobriety
label var partysobriety "Party Sobriety"
notes partysobriety : The state of sobriety of the party

// Party drug physical variable operations
ren partydrugphysical temp
gen byte partydrugphysical = 0 if temp == "-"
replace partydrugphysical = 1 if temp == "E"
replace partydrugphysical = 2 if temp == "F"
replace partydrugphysical = 3 if temp == "G"
replace partydrugphysical = 4 if temp == "H"
replace partydrugphysical = 5 if temp == "I"
order partydrugphysical, before(temp)
drop temp
label define partydrugphysical 0 "Not stated" 1 "Under drug influence" 2 "Impairment - physical" 3 "Impairment unknown" 4 "Not applicable" 5 "Sleepy or fatigued"
label values partydrugphysical partydrugphysical
label var partydrugphysical "Party Drug Physical"
notes partydrugphysical : The state of the party with regard to drugs and physical condition



*************** Party Conditions (Party Level) ***************

// Direction of travel variable operations
ren diroftravel temp
gen byte diroftravel = 0 if temp == "-"
replace diroftravel = 1 if temp == "N"
replace diroftravel = 2 if temp == "S"
replace diroftravel = 3 if temp == "E"
replace diroftravel = 4 if temp == "W"
order diroftravel, before(temp)
drop temp
label define diroftravel 0 "Not stated" 1 "North" 2 "South" 3 "East" 4 "West"
label values diroftravel diroftravel
label var diroftravel "Direction of Travel"
notes diroftravel : Direction that the party was traveling at the time of the crash. The direction is the direction of the highway, not the compass direction

// Party safety equipment 1  variable operations
ren partysafetyeq1 temp
gen byte partysafetyeq1 = 0 if temp == "-"
replace partysafetyeq1 = 1 if temp == "A"
replace partysafetyeq1 = 2 if temp == "B"
replace partysafetyeq1 = 3 if temp == "C"
replace partysafetyeq1 = 4 if temp == "D"
replace partysafetyeq1 = 5 if temp == "E"
replace partysafetyeq1 = 6 if temp == "F"
replace partysafetyeq1 = 7 if temp == "G"
replace partysafetyeq1 = 8 if temp == "H"
replace partysafetyeq1 = 9 if temp == "J"
replace partysafetyeq1 = 10 if temp == "K"
replace partysafetyeq1 = 11 if temp == "L"
replace partysafetyeq1 = 12 if temp == "M"
replace partysafetyeq1 = 13 if temp == "N"
replace partysafetyeq1 = 14 if temp == "P"
replace partysafetyeq1 = 15 if temp == "Q"
replace partysafetyeq1 = 16 if temp == "R"
replace partysafetyeq1 = 17 if temp == "S"
replace partysafetyeq1 = 18 if temp == "T"
replace partysafetyeq1 = 19 if temp == "U"
replace partysafetyeq1 = 20 if temp == "V"
replace partysafetyeq1 = 21 if temp == "W"
replace partysafetyeq1 = 22 if temp == "X"
replace partysafetyeq1 = 23 if temp == "Y"
order partysafetyeq1, before(temp)
drop temp
label define partysafetyeq1 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values partysafetyeq1 partysafetyeq1
label var partysafetyeq1 "Party Safety Equipment 1"
notes partysafetyeq1 : The safety equipment of the party

// Party safety equipment 2  variable operations
ren partysafetyeq2 temp
gen byte partysafetyeq2 = 0 if temp == "-"
replace partysafetyeq2 = 1 if temp == "A"
replace partysafetyeq2 = 2 if temp == "B"
replace partysafetyeq2 = 3 if temp == "C"
replace partysafetyeq2 = 4 if temp == "D"
replace partysafetyeq2 = 5 if temp == "E"
replace partysafetyeq2 = 6 if temp == "F"
replace partysafetyeq2 = 7 if temp == "G"
replace partysafetyeq2 = 8 if temp == "H"
replace partysafetyeq2 = 9 if temp == "J"
replace partysafetyeq2 = 10 if temp == "K"
replace partysafetyeq2 = 11 if temp == "L"
replace partysafetyeq2 = 12 if temp == "M"
replace partysafetyeq2 = 13 if temp == "N"
replace partysafetyeq2 = 14 if temp == "P"
replace partysafetyeq2 = 15 if temp == "Q"
replace partysafetyeq2 = 16 if temp == "R"
replace partysafetyeq2 = 17 if temp == "S"
replace partysafetyeq2 = 18 if temp == "T"
replace partysafetyeq2 = 19 if temp == "U"
replace partysafetyeq2 = 20 if temp == "V"
replace partysafetyeq2 = 21 if temp == "W"
replace partysafetyeq2 = 22 if temp == "X"
replace partysafetyeq2 = 23 if temp == "Y"
order partysafetyeq2, before(temp)
drop temp
label define partysafetyeq2 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values partysafetyeq2 partysafetyeq2
label var partysafetyeq2 "Party Safety Equipment 2"
notes partysafetyeq2 : The safety equipment of the party

// Financial responsibility  variable operations
ren finanrespons temp
gen byte finanrespons = 1 if temp == "N"
replace finanrespons = 2 if temp == "Y"
replace finanrespons = 3 if temp == "O"
replace finanrespons = 4 if temp == "E"
order finanrespons, before(temp)
drop temp
label define finanrespons 1 "No proof of insurance obtained" 2 "Yes, proof of insurance obtained" 3 "Not applicable (used for parked cars, bicyclists, pedestrians, and party type others)" 4 "Used if the officer is called away from the scene of the crash prior to obtaining the insurance information"
label values finanrespons finanrespons
label var finanrespons "Financial Responsibility"
notes finanrespons : Financial responsibility of the party

// Special information 1 variable operations
ren spinfo1 temp
gen byte spinfo1 = 0 if temp == "-"
replace spinfo1 = 1 if temp == "A"
order spinfo1, before(temp)
drop temp
label define spinfo1 0 "Not stated" 1 "Hazardous material"
label values spinfo1 spinfo1
label var spinfo1 "Special Information 1"
notes spinfo1 : Value A indicates that the crash involved in a vehicle known to be, or believed to be, transporting a hazardous material as defined in CVC Section 353, whether or not the crash involved a hazardous material incident

// Special information 2 variable operations
ren spinfo2 temp
gen byte spinfo2 = 0 if temp == "-"
replace spinfo2 = 1 if temp == "1"
replace spinfo2 = 2 if temp == "2"
replace spinfo2 = 3 if temp == "3"
replace spinfo2 = 4 if temp == "4"
replace spinfo2 = 5 if temp == "B"
replace spinfo2 = 6 if temp == "C"
replace spinfo2 = 7 if temp == "D"
order spinfo2, before(temp)
drop temp
label define spinfo2 0 "Not stated" 1 "Cell phone handheld in use" 2 "Cell phone hands-free in use" 3 "Cell phone not in use" 4 "Cell phone use unknown" 5 "Cell phone in use" 6 "Cell phone not in use" 7 "No cell phone/unknown"
label values spinfo2 spinfo2
label var spinfo2 "Special Information 2"
notes spinfo2 : Cell Phone Information

// Special information 3 variable operations
ren spinfo3 temp
gen byte spinfo3 = 0 if temp == "-"
replace spinfo3 = 1 if temp == "E"
order spinfo3, before(temp)
drop temp
label define spinfo3 0 "Not stated" 1 "School bus related"
label values spinfo3 spinfo3
label var spinfo3 "Special Information 3"
notes spinfo3 : Value E indicates that the crash involved a motor vehicle in-transport passing a stopped school bus with its red signal lamps in operation pursuant to CVC Section 22112, or reacting to, pursuant to CVC Section 22454



*************** Party Causal Characteristics (Party Level) ***************

// OAF violation code variable operations
ren oafviolcode temp
gen byte oafviolcode = 0 if temp == "-"
replace oafviolcode = 1 if temp == "B"
replace oafviolcode = 2 if temp == "C"
replace oafviolcode = 3 if temp == "H"
replace oafviolcode = 4 if temp == "I"
replace oafviolcode = 5 if temp == "P"
replace oafviolcode = 6 if temp == "S"
replace oafviolcode = 7 if temp == "W"
order oafviolcode, before(temp)
drop temp
label define oafviolcode 0 "Not stated" 1 "Business and professions" 2 "Vehicle" 3 "City health and safety" 4 "City ordinance" 5 "Penal" 6 "Streets and highways" 7 "Welfare and institutions"
label values oafviolcode oafviolcode
label var oafviolcode "OAF Violation Code"
notes oafviolcode : Other associated factor law code violated

// OAF violation category variable operations
ren oafviolcat temp
gen byte oafviolcat = 0 if temp == "0"
replace oafviolcat = 1 if temp == "1"
replace oafviolcat = 2 if temp == "2"
replace oafviolcat = 3 if temp == "3"
replace oafviolcat = 5 if temp == "5"
replace oafviolcat = 6 if temp == "6"
replace oafviolcat = 8 if temp == "8"
replace oafviolcat = 9 if temp == "9"
replace oafviolcat = 10 if temp == "10"
replace oafviolcat = 11 if temp == "11"
replace oafviolcat = 13 if temp == "13"
replace oafviolcat = 15 if temp == "15"
replace oafviolcat = 16 if temp == "16"
replace oafviolcat = 17 if temp == "17"
replace oafviolcat = 18 if temp == "18"
replace oafviolcat = 19 if temp == "19"
replace oafviolcat = 20 if temp == "20"
replace oafviolcat = 21 if temp == "21"
replace oafviolcat = 22 if temp == "22"
replace oafviolcat = 23 if temp == "23"
replace oafviolcat = 24 if temp == "24"
replace oafviolcat = 25 if temp == "25"
replace oafviolcat = 26 if temp == "26"
replace oafviolcat = 27 if temp == "27"
replace oafviolcat = 28 if temp == "28"
replace oafviolcat = 29 if temp == "29"
replace oafviolcat = 30 if temp == "30"
replace oafviolcat = 31 if temp == "31"
replace oafviolcat = 33 if temp == "33"
replace oafviolcat = 34 if temp == "34"
replace oafviolcat = 35 if temp == "35"
replace oafviolcat = 38 if temp == "38"
replace oafviolcat = 39 if temp == "39"
replace oafviolcat = 40 if temp == "40"
replace oafviolcat = 43 if temp == "43"
replace oafviolcat = 44 if temp == "44"
replace oafviolcat = 46 if temp == "46"
replace oafviolcat = 47 if temp == "47"
replace oafviolcat = 48 if temp == "48"
replace oafviolcat = 49 if temp == "49"
replace oafviolcat = 50 if temp == "50"
replace oafviolcat = 51 if temp == "51"
replace oafviolcat = 52 if temp == "52"
replace oafviolcat = 53 if temp == "53"
replace oafviolcat = 60 if temp == "60"
replace oafviolcat = 61 if temp == "61"
replace oafviolcat = 62 if temp == "62"
replace oafviolcat = 63 if temp == "63"
replace oafviolcat = 99 if temp == "-"
order oafviolcat, before(temp)
drop temp
label define oafviolcat 0 "Not stated" 1 "Under influence in public" 2 "County ordinance" 3 "City ordinance" 5 "Business/professions code" 6 "Felony penal code" 8 "Controlled substances (felony health and safety)" 9 "Health/safety code (misdemeanor)" 10 "Penal code (misdemeanor)" 11 "Streets/highways code" 13 "Welfare/institutions code" 15 "Manslaughter" 16 "Non-vehicle code not specified above" 17 "Fish and game code" 18 "Agriculture code" 19 "Hit and run" 20 "Driving or bicycling under the influence of alcohol or drug" 21 "Improper lane change" 22 "Impeding traffic" 23 "Failure to heed stop signal" 24 "Failure to heed stop sign" 25 "Unsafe speed" 26 "Reckless driving" 27 "Wrong side of road" 28 "Unsafe lane change" 29 "Improper passing" 30 "Following too closely" 31 "Improper turning" 33 "Automobile right-of-way" 34 "Pedestrian right-of-way" 35 "Pedestrian violation" 38 "Hazardous parking" 39 "Lights" 40 "Brakes" 43 "Other equipment" 44 "Other hazardous movement" 46 "Improper registration" 47 "Other non-moving violation" 48 "Excessive smoke" 49 "Excessive noise" 50 "Overweight" 51 "Oversize" 52 "Over maximum speed" 53 "Unsafe starting or backing" 60 "Off-highway vehicle violation" 61 "Child restraint" 62 "Seat belt" 63 "Seat belt (equipment)" 99 "Not Stated"
label values oafviolcat oafviolcat
label var oafviolcat "OAF Violation Category"
notes oafviolcat : Category of the factor that contributed to the crash but was not the primary cause of the crash

// OAF violation section variable operations
label var oafviolsection "OAF Violation Section"
notes oafviolsection : The CVC section of the secondary violation that contributed to the crash

// OAF violation suffix variable operations
label var oafviolsuffix "OAF Violation Suffix"
notes oafviolsuffix : the subsection of the CVC section of the secondary violation that contributed to the crash

// Other associated factor 1 variable operations
ren oaf1 temp
gen byte oaf1 = 0 if temp == "-"
replace oaf1 = 1 if temp == "A"
replace oaf1 = 2 if temp == "E"
replace oaf1 = 3 if temp == "F"
replace oaf1 = 4 if temp == "G"
replace oaf1 = 5 if temp == "H"
replace oaf1 = 6 if temp == "I"
replace oaf1 = 7 if temp == "J"
replace oaf1 = 8 if temp == "K"
replace oaf1 = 9 if temp == "L"
replace oaf1 = 10 if temp == "M"
replace oaf1 = 11 if temp == "N"
replace oaf1 = 12 if temp == "O"
replace oaf1 = 13 if temp == "P"
replace oaf1 = 14 if temp == "Q"
replace oaf1 = 15 if temp == "R"
replace oaf1 = 16 if temp == "S"
replace oaf1 = 17 if temp == "T"
replace oaf1 = 18 if temp == "U"
replace oaf1 = 19 if temp == "V"
replace oaf1 = 20 if temp == "W"
replace oaf1 = 21 if temp == "X"
replace oaf1 = 22 if temp == "Y"
order oaf1, before(temp)
drop temp
label define oaf1 0 "Not stated" 1 "Violation" 2 "Vision obsurements" 3 "Inattention" 4 "Stop and go traffic" 5 "Entering/leaving ramp" 6 "Previous collision" 7 "Unfamiliar with road" 8 "Defective vehicle equipment" 9 "Uninvolved vehicle" 10 "Other" 11 "None apparent" 12 "Runaway vehicle" 13 "Inattention, cell phone" 14 "Inattention, electronic equipment" 15 "Inattention, radio/cd" 16 "Innatention, smoking" 17 "Inattention, eating" 18 "Inattention, children" 19 "Inattention, animal" 20 "Inattention, personal hygiene" 21 "Inattention, reading" 22 "Inattention, other"
label values oaf1 oaf1
label var oaf1 "Other Associated Factor 1"
notes oaf1 : A factor that contributed to the crash but was not the primary cause of the crash

// Other associated factor 2 variable operations
ren oaf2 temp
gen byte oaf2 = 0 if temp == "-"
replace oaf2 = 1 if temp == "A"
replace oaf2 = 2 if temp == "E"
replace oaf2 = 3 if temp == "F"
replace oaf2 = 4 if temp == "G"
replace oaf2 = 5 if temp == "H"
replace oaf2 = 6 if temp == "I"
replace oaf2 = 7 if temp == "J"
replace oaf2 = 8 if temp == "K"
replace oaf2 = 9 if temp == "L"
replace oaf2 = 10 if temp == "M"
replace oaf2 = 11 if temp == "N"
replace oaf2 = 12 if temp == "O"
replace oaf2 = 13 if temp == "P"
replace oaf2 = 14 if temp == "Q"
replace oaf2 = 15 if temp == "R"
replace oaf2 = 16 if temp == "S"
replace oaf2 = 17 if temp == "T"
replace oaf2 = 18 if temp == "U"
replace oaf2 = 19 if temp == "V"
replace oaf2 = 20 if temp == "W"
replace oaf2 = 21 if temp == "X"
replace oaf2 = 22 if temp == "Y"
order oaf2, before(temp)
drop temp
label define oaf2 0 "Not stated" 1 "Violation" 2 "Vision obsurements" 3 "Inattention" 4 "Stop and go traffic" 5 "Entering/leaving ramp" 6 "Previous collision" 7 "Unfamiliar with road" 8 "Defective vehicle equipment" 9 "Uninvolved vehicle" 10 "Other" 11 "None apparent" 12 "Runaway vehicle" 13 "Inattention, cell phone" 14 "Inattention, electronic equipment" 15 "Inattention, radio/cd" 16 "Innatention, smoking" 17 "Inattention, eating" 18 "Inattention, children" 19 "Inattention, animal" 20 "Inattention, personal hygiene" 21 "Inattention, reading" 22 "Inattention, other"
label values oaf2 oaf2
label var oaf2 "Other Associated Factor 2"
notes oaf2 : A factor that contributed to the crash but was not the primary cause of the crash

// Movement preceding crash variable operations
ren movepreacc temp
gen byte movepreacc = 0 if temp == "-"
replace movepreacc = 1 if temp == "A"
replace movepreacc = 2 if temp == "B"
replace movepreacc = 3 if temp == "C"
replace movepreacc = 4 if temp == "D"
replace movepreacc = 5 if temp == "E"
replace movepreacc = 6 if temp == "F"
replace movepreacc = 7 if temp == "G"
replace movepreacc = 8 if temp == "H"
replace movepreacc = 9 if temp == "I"
replace movepreacc = 10 if temp == "J"
replace movepreacc = 11 if temp == "K"
replace movepreacc = 12 if temp == "L"
replace movepreacc = 13 if temp == "M"
replace movepreacc = 14 if temp == "N"
replace movepreacc = 15 if temp == "O"
replace movepreacc = 16 if temp == "P"
replace movepreacc = 17 if temp == "Q"
replace movepreacc = 18 if temp == "R"
replace movepreacc = 19 if temp == "S"
order movepreacc, before(temp)
drop temp
label define movepreacc 0 "Not stated" 1 "Stopped" 2 "Proceeding straight" 3 "Ran off road" 4 "Making right turn" 5 "Making left turn" 6 "Making U-turn" 7 "Backing" 8 "Slowing/stopping" 9 "Passing other vehicle" 10 "Changing lanes" 11 "Parking maneuver" 12 "entering traffic" 13 "Other unsafe turning" 14 "Crossed into opposing lane" 15 "Parked" 16 "Merging" 17 "Traveling wrong way" 18 "Other" 19 "Lane splitting"
label values movepreacc movepreacc
label var movepreacc "Movement Preceding Crash"
notes movepreacc : The action of the vehicle prior to the crash and before evasive action. This movement does not have to correspond with the PCF



*************** Vehicle Characteristics (Party Level) ***************

// Vehicle year variable operations
// Corrections
replace vehicleyear = 2001 if vehicleyear == 2101
replace vehicleyear = 2002 if vehicleyear == 2102
replace vehicleyear = 2008 if vehicleyear == 2108
replace vehicleyear = 2003 if vehicleyear == 2203
replace vehicleyear = 2016 if vehicleyear == 2916
replace vehicleyear = 2003 if vehicleyear == 2203
replace vehicleyear = 2017 if vehicleyear == 2047
replace vehicleyear = 2001 if vehicleyear == 1201
label var vehicleyear "Vehicle Year"
notes vehicleyear : The model year of the party's vehicle

// Vehicle make variable operations
label var vehiclemake "Vehicle Make"
notes vehiclemake : The make of the party's vehicle

// Statewide vehicle type variable operations
ren stwdvehicletype temp
gen byte stwdvehicletype = 0 if temp == "-"
replace stwdvehicletype = 1 if temp == "A"
replace stwdvehicletype = 2 if temp == "B"
replace stwdvehicletype = 3 if temp == "C"
replace stwdvehicletype = 4 if temp == "D"
replace stwdvehicletype = 5 if temp == "E"
replace stwdvehicletype = 6 if temp == "F"
replace stwdvehicletype = 7 if temp == "G"
replace stwdvehicletype = 8 if temp == "H"
replace stwdvehicletype = 9 if temp == "I"
replace stwdvehicletype = 10 if temp == "J"
replace stwdvehicletype = 11 if temp == "K"
replace stwdvehicletype = 12 if temp == "L"
replace stwdvehicletype = 13 if temp == "M"
replace stwdvehicletype = 14 if temp == "N"
replace stwdvehicletype = 15 if temp == "O"
order stwdvehicletype, before(temp)
drop temp
label define stwdvehicletype 0 "Not stated" 1 "Passenger car/station wagon" 2 "Passenger car with trailer" 3 "Motorcycle/scooter" 4 "Pickup or panel truck" 5 "Pickup or panel truck with trailer" 6 "Truck or truck tractor" 7 "Truck or truck tractor with trailer" 8 "School bus" 9 "Other bus" 10 "Emergency vehicle" 11 "Highway construction equipment" 12 "Bicycle" 13 "Other vehicle" 14 "Pedestrian" 15 "Moped"
label values stwdvehicletype stwdvehicletype
label var stwdvehicletype "Statewide Vehicle Type"
notes stwdvehicletype : Type of the party's vehicle according to a list called statewide vehicle type



*************** Special Characteristics (Party Level) ***************

// CHP vehicle type towing variable operations
ren chpvehtypetowing temp
gen byte chpvehtypetowing = 0 if temp == "-"
replace chpvehtypetowing = 1 if temp == "1"
replace chpvehtypetowing = 2 if temp == "2"
replace chpvehtypetowing = 3 if temp == "3"
replace chpvehtypetowing = 4 if temp == "4"
replace chpvehtypetowing = 5 if temp == "5"
replace chpvehtypetowing = 6 if temp == "6"
replace chpvehtypetowing = 7 if temp == "7"
replace chpvehtypetowing = 8 if temp == "8"
replace chpvehtypetowing = 9 if temp == "9"
replace chpvehtypetowing = 10 if temp == "10"
replace chpvehtypetowing = 11 if temp == "11"
replace chpvehtypetowing = 12 if temp == "12"
replace chpvehtypetowing = 13 if temp == "13"
replace chpvehtypetowing = 14 if temp == "14"
replace chpvehtypetowing = 15 if temp == "15"
replace chpvehtypetowing = 16 if temp == "16"
replace chpvehtypetowing = 17 if temp == "17"
replace chpvehtypetowing = 18 if temp == "18"
replace chpvehtypetowing = 19 if temp == "19"
replace chpvehtypetowing = 20 if temp == "20"
replace chpvehtypetowing = 21 if temp == "21"
replace chpvehtypetowing = 22 if temp == "22"
replace chpvehtypetowing = 23 if temp == "23"
replace chpvehtypetowing = 24 if temp == "24"
replace chpvehtypetowing = 25 if temp == "25"
replace chpvehtypetowing = 26 if temp == "26"
replace chpvehtypetowing = 27 if temp == "27"
replace chpvehtypetowing = 28 if temp == "28"
replace chpvehtypetowing = 29 if temp == "29"
replace chpvehtypetowing = 30 if temp == "30"
replace chpvehtypetowing = 31 if temp == "31"
replace chpvehtypetowing = 32 if temp == "32"
replace chpvehtypetowing = 33 if temp == "33"
replace chpvehtypetowing = 34 if temp == "34"
replace chpvehtypetowing = 35 if temp == "35"
replace chpvehtypetowing = 36 if temp == "36"
replace chpvehtypetowing = 37 if temp == "37"
replace chpvehtypetowing = 38 if temp == "38"
replace chpvehtypetowing = 39 if temp == "39"
replace chpvehtypetowing = 40 if temp == "40"
replace chpvehtypetowing = 41 if temp == "41"
replace chpvehtypetowing = 42 if temp == "42"
replace chpvehtypetowing = 43 if temp == "43"
replace chpvehtypetowing = 44 if temp == "44"
replace chpvehtypetowing = 45 if temp == "45"
replace chpvehtypetowing = 46 if temp == "46"
replace chpvehtypetowing = 47 if temp == "47"
replace chpvehtypetowing = 48 if temp == "48"
replace chpvehtypetowing = 49 if temp == "49"
replace chpvehtypetowing = 50 if temp == "50"
replace chpvehtypetowing = 51 if temp == "51"
replace chpvehtypetowing = 52 if temp == "52"
replace chpvehtypetowing = 53 if temp == "53"
replace chpvehtypetowing = 54 if temp == "54"
replace chpvehtypetowing = 55 if temp == "55"
replace chpvehtypetowing = 56 if temp == "56"
replace chpvehtypetowing = 57 if temp == "57"
replace chpvehtypetowing = 58 if temp == "58"
replace chpvehtypetowing = 59 if temp == "59"
replace chpvehtypetowing = 60 if temp == "60"
replace chpvehtypetowing = 61 if temp == "61"
replace chpvehtypetowing = 62 if temp == "62"
replace chpvehtypetowing = 63 if temp == "63"
replace chpvehtypetowing = 64 if temp == "64"
replace chpvehtypetowing = 65 if temp == "65"
replace chpvehtypetowing = 66 if temp == "66"
replace chpvehtypetowing = 71 if temp == "71"
replace chpvehtypetowing = 72 if temp == "72"
replace chpvehtypetowing = 73 if temp == "73"
replace chpvehtypetowing = 75 if temp == "75"
replace chpvehtypetowing = 76 if temp == "76"
replace chpvehtypetowing = 77 if temp == "77"
replace chpvehtypetowing = 78 if temp == "78"
replace chpvehtypetowing = 79 if temp == "79"
replace chpvehtypetowing = 81 if temp == "81"
replace chpvehtypetowing = 82 if temp == "82"
replace chpvehtypetowing = 83 if temp == "83"
replace chpvehtypetowing = 85 if temp == "85"
replace chpvehtypetowing = 86 if temp == "86"
replace chpvehtypetowing = 87 if temp == "87"
replace chpvehtypetowing = 88 if temp == "88"
replace chpvehtypetowing = 89 if temp == "89"
replace chpvehtypetowing = 91 if temp == "91"
replace chpvehtypetowing = 93 if temp == "93"
replace chpvehtypetowing = 94 if temp == "94"
replace chpvehtypetowing = 95 if temp == "95"
replace chpvehtypetowing = 96 if temp == "96"
replace chpvehtypetowing = 97 if temp == "97"
replace chpvehtypetowing = 98 if temp == "98"
replace chpvehtypetowing = 99 if temp == "99"
order chpvehtypetowing, before(temp)
drop temp
label define chpvehtypetowing 0 "Not stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 3 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chpvehtypetowing chpvehtypetowing
label var chpvehtypetowing "CHP Vehicle Type Towing"
notes chpvehtypetowing : The type of the solitary vehicle or the tractor unit according to the CHP manual HPM 110.5 Chapter 3 Annex F vehicle type codes

// CHP vehicle type towed variable operations
ren chpvehtypetowed temp
gen byte chpvehtypetowed = 0 if temp == "-"
replace chpvehtypetowed = 1 if temp == "1"
replace chpvehtypetowed = 2 if temp == "2"
replace chpvehtypetowed = 3 if temp == "3"
replace chpvehtypetowed = 4 if temp == "4"
replace chpvehtypetowed = 5 if temp == "5"
replace chpvehtypetowed = 6 if temp == "6"
replace chpvehtypetowed = 7 if temp == "7"
replace chpvehtypetowed = 8 if temp == "8"
replace chpvehtypetowed = 9 if temp == "9"
replace chpvehtypetowed = 10 if temp == "10"
replace chpvehtypetowed = 11 if temp == "11"
replace chpvehtypetowed = 12 if temp == "12"
replace chpvehtypetowed = 13 if temp == "13"
replace chpvehtypetowed = 14 if temp == "14"
replace chpvehtypetowed = 15 if temp == "15"
replace chpvehtypetowed = 16 if temp == "16"
replace chpvehtypetowed = 17 if temp == "17"
replace chpvehtypetowed = 18 if temp == "18"
replace chpvehtypetowed = 19 if temp == "19"
replace chpvehtypetowed = 20 if temp == "20"
replace chpvehtypetowed = 21 if temp == "21"
replace chpvehtypetowed = 22 if temp == "22"
replace chpvehtypetowed = 23 if temp == "23"
replace chpvehtypetowed = 24 if temp == "24"
replace chpvehtypetowed = 25 if temp == "25"
replace chpvehtypetowed = 26 if temp == "26"
replace chpvehtypetowed = 27 if temp == "27"
replace chpvehtypetowed = 28 if temp == "28"
replace chpvehtypetowed = 29 if temp == "29"
replace chpvehtypetowed = 30 if temp == "30"
replace chpvehtypetowed = 31 if temp == "31"
replace chpvehtypetowed = 32 if temp == "32"
replace chpvehtypetowed = 33 if temp == "33"
replace chpvehtypetowed = 34 if temp == "34"
replace chpvehtypetowed = 35 if temp == "35"
replace chpvehtypetowed = 36 if temp == "36"
replace chpvehtypetowed = 37 if temp == "37"
replace chpvehtypetowed = 38 if temp == "38"
replace chpvehtypetowed = 39 if temp == "39"
replace chpvehtypetowed = 40 if temp == "40"
replace chpvehtypetowed = 41 if temp == "41"
replace chpvehtypetowed = 42 if temp == "42"
replace chpvehtypetowed = 43 if temp == "43"
replace chpvehtypetowed = 44 if temp == "44"
replace chpvehtypetowed = 45 if temp == "45"
replace chpvehtypetowed = 46 if temp == "46"
replace chpvehtypetowed = 47 if temp == "47"
replace chpvehtypetowed = 48 if temp == "48"
replace chpvehtypetowed = 49 if temp == "49"
replace chpvehtypetowed = 50 if temp == "50"
replace chpvehtypetowed = 51 if temp == "51"
replace chpvehtypetowed = 52 if temp == "52"
replace chpvehtypetowed = 53 if temp == "53"
replace chpvehtypetowed = 54 if temp == "54"
replace chpvehtypetowed = 55 if temp == "55"
replace chpvehtypetowed = 56 if temp == "56"
replace chpvehtypetowed = 57 if temp == "57"
replace chpvehtypetowed = 58 if temp == "58"
replace chpvehtypetowed = 59 if temp == "59"
replace chpvehtypetowed = 60 if temp == "60"
replace chpvehtypetowed = 61 if temp == "61"
replace chpvehtypetowed = 62 if temp == "62"
replace chpvehtypetowed = 63 if temp == "63"
replace chpvehtypetowed = 64 if temp == "64"
replace chpvehtypetowed = 65 if temp == "65"
replace chpvehtypetowed = 66 if temp == "66"
replace chpvehtypetowed = 71 if temp == "71"
replace chpvehtypetowed = 72 if temp == "72"
replace chpvehtypetowed = 73 if temp == "73"
replace chpvehtypetowed = 75 if temp == "75"
replace chpvehtypetowed = 76 if temp == "76"
replace chpvehtypetowed = 77 if temp == "77"
replace chpvehtypetowed = 78 if temp == "78"
replace chpvehtypetowed = 79 if temp == "79"
replace chpvehtypetowed = 81 if temp == "81"
replace chpvehtypetowed = 82 if temp == "82"
replace chpvehtypetowed = 83 if temp == "83"
replace chpvehtypetowed = 85 if temp == "85"
replace chpvehtypetowed = 86 if temp == "86"
replace chpvehtypetowed = 87 if temp == "87"
replace chpvehtypetowed = 88 if temp == "88"
replace chpvehtypetowed = 89 if temp == "89"
replace chpvehtypetowed = 91 if temp == "91"
replace chpvehtypetowed = 93 if temp == "93"
replace chpvehtypetowed = 94 if temp == "94"
replace chpvehtypetowed = 95 if temp == "95"
replace chpvehtypetowed = 96 if temp == "96"
replace chpvehtypetowed = 97 if temp == "97"
replace chpvehtypetowed = 98 if temp == "98"
replace chpvehtypetowed = 99 if temp == "99"
order chpvehtypetowed, before(temp)
drop temp
label define chpvehtypetowed 0 "Not stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 83 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chpvehtypetowed chpvehtypetowed
label var chpvehtypetowed "CHP Vehicle Type Towed"
notes chpvehtypetowed : The type of the first trailer unit according to the CHP manual HPM 110.5 Chapter 3 Annex F vehicle type codes

// Special info F variable operations
ren specialinfof temp
gen byte specialinfof = 0 if temp == "-"
replace specialinfof = 1 if temp == "F"
order specialinfof, before(temp)
drop temp
label define specialinfof 0 "Not stated" 1 "75ft motor truck combo"
label values specialinfof specialinfof
label var specialinfof "Special Info F"
notes specialinfof : The value F indicate that the party's vehicle is a 75ft motor truck combo

// Special info G variable operations
ren specialinfog temp
gen byte specialinfog = 0 if temp == "-"
replace specialinfog = 1 if temp == "G"
order specialinfog, before(temp)
drop temp
label define specialinfog 0 "Not stated" 1 "32ft trailer combo"
label values specialinfog specialinfog
label var specialinfog "Special Info G"
notes specialinfog : The value G indicates that the party's vehicle is a 32ft trailer combo



*************** Basic Victim Characteristics (Victim Level) ***************

// Victim role variable operations
label define victimrole 1 "Driver" 2 "Passenger" 3 "Pedestrian" 4 "Bicyclist" 5 "Other (single victim on/in non-motor vehicle)" 6 "Non-injured party"
label values victimrole victimrole
label var victimrole "Victim Role"
notes victimrole : The role of the victim (passenger (includes non-operator on bicycle or any victim on/in parked vehicle or multiple victims on/in non-motor vehicle)

// Victim sex variable operations
ren victimsex temp
gen byte victimsex = 0 if temp == "-"
replace victimsex = 1 if temp == "M"
replace victimsex = 2 if temp == "F"
replace victimsex = 3 if temp == "X"
order victimsex, before(temp)
drop temp
label define victimsex 0 "Not stated" 1 "Male" 2 "Female" 3 "Nonbinary"
label values victimsex victimSex
label var victimsex "Victim Sex"
notes victimsex : The gender of the victim

// Victim age variable operations
label define victimage 998 "Not stated" 999 "Fatal fetus"
label values victimage victim_age
label var victimage "Victim Age"
notes victimage : The age of the victim at the time of the crash

// Victim degree of injury variable operations
label define victimdegreeofinjury 0 "No injury" 1 "Killed" 2 "Severe injury" 3 "Other visible injury" 4 "Complaint of pain" 5 "Suspected serious injury" 6 "Suspected minor injury" 7 "Possible injury"
label values victimdegreeofinjury victimdegreeofinjury
label var victimdegreeofinjury "Victim Degree of Injury"
notes victimdegreeofinjury : The severity of the injury to the victim

// Victim degree of injury (binary) variable operations
gen byte victimdegreeofinjurybin = 0 if victimdegreeofinjury == 0 | victimdegreeofinjury == 4 | victimdegreeofinjury == 6 | victimdegreeofinjury == 7
replace victimdegreeofinjurybin = 1 if victimdegreeofinjury == 1 | victimdegreeofinjury == 2 | victimdegreeofinjury == 3 | victimdegreeofinjury == 5
order victimdegreeofinjurybin, after(victimdegreeofinjury)
label define victimdegreeofinjurybin 0 "Minor (minor injury, pain, or no injury)" 1 "Severe (killed or serious injury)"
label values victimdegreeofinjurybin victimdegreeofinjurybin
label var victimdegreeofinjurybin "Victim Degree of Injury (binary)"
notes victimdegreeofinjurybin : Binary classification of the severity of the injury to the victim

// Victim seating position variable operations
ren victimseatingposition temp
gen byte victimseatingposition = 0 if temp == "0"
replace victimseatingposition = 1 if temp == "1"
replace victimseatingposition = 2 if temp == "2"
replace victimseatingposition = 3 if temp == "3"
replace victimseatingposition = 4 if temp == "4"
replace victimseatingposition = 5 if temp == "5"
replace victimseatingposition = 6 if temp == "6"
replace victimseatingposition = 7 if temp == "7"
replace victimseatingposition = 8 if temp == "8"
replace victimseatingposition = 9 if temp == "9"
replace victimseatingposition = 10 if temp == "-"
order victimseatingposition, before(temp)
drop(temp)
label define victimseatingposition 0 "Other occupants" 1 "Driver" 2 "Passenger 1" 3 "Passenger 2" 4 "Passenger 3" 5 "Passenger 4" 6 "Passenger 5" 7 "Station  wagon rear" 8 "Rear occupant of truck or van" 9 "Position unknown" 10 "Not stated"
label values victimseatingposition victimseatingposition
label var victimseatingposition "Victim Seating Position"
notes victimseatingposition : The seating position of the victim



*************** Victim Conditions (Victim Level) ***************

// Victim safety equipment 1 variable operations
ren victimsafetyeq1 temp
gen byte victimsafetyeq1 = 0 if temp == "-"
replace victimsafetyeq1 = 1 if temp == "A"
replace victimsafetyeq1 = 2 if temp == "B"
replace victimsafetyeq1 = 3 if temp == "C"
replace victimsafetyeq1 = 4 if temp == "D"
replace victimsafetyeq1 = 5 if temp == "E"
replace victimsafetyeq1 = 6 if temp == "F"
replace victimsafetyeq1 = 7 if temp == "G"
replace victimsafetyeq1 = 8 if temp == "H"
replace victimsafetyeq1 = 9 if temp == "J"
replace victimsafetyeq1 = 10 if temp == "K"
replace victimsafetyeq1 = 11 if temp == "L"
replace victimsafetyeq1 = 12 if temp == "M"
replace victimsafetyeq1 = 13 if temp == "N"
replace victimsafetyeq1 = 14 if temp == "P"
replace victimsafetyeq1 = 15 if temp == "Q"
replace victimsafetyeq1 = 16 if temp == "R"
replace victimsafetyeq1 = 17 if temp == "S"
replace victimsafetyeq1 = 18 if temp == "T"
replace victimsafetyeq1 = 19 if temp == "U"
replace victimsafetyeq1 = 20 if temp == "V"
replace victimsafetyeq1 = 21 if temp == "W"
replace victimsafetyeq1 = 22 if temp == "X"
replace victimsafetyeq1 = 23 if temp == "Y"
order victimsafetyeq1, before(temp)
drop temp
label define victimsafetyeq1 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values victimsafetyeq1 victimsafetyeq1
label var victimsafetyeq1 "Victim Safety Equipment 1"
notes victimsafetyeq1 : The safety equipment of the victim

// Victim safety equipment 2 variable operations
ren victimsafetyeq2 temp
gen byte victimsafetyeq2 = 0 if temp == "-"
replace victimsafetyeq2 = 1 if temp == "A"
replace victimsafetyeq2 = 2 if temp == "B"
replace victimsafetyeq2 = 3 if temp == "C"
replace victimsafetyeq2 = 4 if temp == "D"
replace victimsafetyeq2 = 5 if temp == "E"
replace victimsafetyeq2 = 6 if temp == "F"
replace victimsafetyeq2 = 7 if temp == "G"
replace victimsafetyeq2 = 8 if temp == "H"
replace victimsafetyeq2 = 9 if temp == "J"
replace victimsafetyeq2 = 10 if temp == "K"
replace victimsafetyeq2 = 11 if temp == "L"
replace victimsafetyeq2 = 12 if temp == "M"
replace victimsafetyeq2 = 13 if temp == "N"
replace victimsafetyeq2 = 14 if temp == "P"
replace victimsafetyeq2 = 15 if temp == "Q"
replace victimsafetyeq2 = 16 if temp == "R"
replace victimsafetyeq2 = 17 if temp == "S"
replace victimsafetyeq2 = 18 if temp == "T"
replace victimsafetyeq2 = 19 if temp == "U"
replace victimsafetyeq2 = 20 if temp == "V"
replace victimsafetyeq2 = 21 if temp == "W"
replace victimsafetyeq2 = 22 if temp == "X"
replace victimsafetyeq2 = 23 if temp == "Y"
order victimsafetyeq2, before(temp)
drop temp
label define victimsafetyeq2 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values victimsafetyeq2 victimsafetyeq2
label var victimsafetyeq2 "Victim Safety Equipment 2"
notes victimsafetyeq2 : The safety equipment of the victim

// Victim ejected variable operations
ren victimejected temp
gen byte victimejected = 0 if temp == "0"
replace victimejected = 1 if temp == "1"
replace victimejected = 2 if temp == "2"
replace victimejected = 3 if temp == "3"
replace victimejected = 9 if temp == "-"
order victimejected, before(temp)
drop temp
label define victimejected 0 "Not ejected" 1 "Fully ejected" 2 "Partially ejected" 3 "Unknown" 9 "Not stated"
label values victimejected victimejected
label var victimejected "Victim Ejected"
notes victimejected : Indicates whether the victim was ejected from the vehicle



*************** City Characteristics (City Level) ***************

// City area variable operations
label var areasqmi "City Area (sq. miles)"
notes areasqmi : City Area in Square Miles

// City population density variable operations
label var popdens "City Population Density (per sq. mi)"
notes popdens : City population density, population per square mile

// City housing density variable operations
label var hudens "City Housing Density (per sq. mi)"
notes hudens : City housing density, houses per square mile

// City total population variable operations
label var popt "City Total Population"
notes popt : Total population in the city's area

// City total housing units variable operations
label var hut "City Total Housing Units"
notes hut : Total housing units in the city's area

// City Asian population variable operations
label var popa "City Asian Population"
notes popa : Total Asian population in the city's area

// City Black population variable operations
label var popb "City Black Population"
notes popb : Total Black or African American population in the city's area

// City Hispanic population variable operations
label var poph "City Hispanic Population"
notes poph : Total Hispanic population in the city's area

// City White population variable operations
label var popw "City White Population"
notes popw : Total White population in the city's area

// City aggregate number of vehicles variable operations
label var vehicles "City Aggregate Number of Vehicles Commutting"
notes vehicles : Aggregate number of vehicles used in commuting in the city's area

// City aggregate travel time to work variable operations
label var traveltime "City Aggregate Travel Time to Work (min)"
notes traveltime : Aggregate travel time to work (in minutes) in the city's area

// Calculate travel time per vehicle
gen mtraveltime = traveltime / vehicles
order mtraveltime, after(traveltime)
label var mtraveltime "Mean Travel Time to work Per Vehicle (min)"
notes mtraveltime: Average travel time to work per vehicles (in minutes) - calculated by divinding aggregate travel time by aggregate commutting vehicles



*************** Positioning and Location Characteristics (Crash Level) ***************

// GPS latitude variable operations
label var latitude "GPS Latitude"
notes latitude : Latitude of the crash location in decimal degrees. The decimal point is included. LATITUDE and LONGITUDE are from the crash report

// GPS Longitude variable operations
label var longitude "GPS Longitude"
notes longitude : Longitude of the crash location in decimal degrees. The decimal point is included. There is no minus sign. The longitude is understood to be West of Meridian. LATITUDE and LONGITUDE are from the crash report

// X coordinate location variable operations
label var pointx "X Coordinate Location"
notes pointx : The longitude of the geocoded location, uses the World Geodetic System from 1984 (WGS84). POINT_X and POINT_Y are generated using the geociding process by UC Berkeley Safe TREC

// Y coordinate location variable operations
label var pointy "Y Coordinate Location"
notes pointy : The latitude of the geocoded location, uses the World Geodetic System from 1984 (WGS84). POINT_X and POINT_Y are generated using the geociding process by UC Berkeley Safe TREC



*************** Save Results to New Collisions Dataset ***************

// save the results into a new collisions dataset
save "stCollisions.dta", replace



*************** Creating Crashes Sub-Dataset ***************

// Preserve the data in memory (collisions)
preserve

// Only keep observations for crashes
keep if crashesind == 1
summarize caseid

// Label dataset
label data "OCSWITRS Crashes Stata Dataset"

// Save the crashes into a new dataset
save "stCrashes.dta", replace

// Restore the original collisions data
restore



*************** Creating Parties Sub-Dataset ***************

// Preserve the data in memory (collisions)
preserve

// Only keep observations for parties
keep if partiesind == 1

// Label dataset
label data "OCSWITRS Parties Stata Dataset"
summarize caseid

// Save the parties into a new dataset
save "stParties.dta", replace

// Restore the original collisions data
restore



*************** Creating Victims Sub-Dataset ***************

// Preserve the data in memory (collisions)
preserve

// Only keep observations for victims
keep if victimsind == 1

// Label dataset
label data "OCSWITRS Victims Stata Dataset"
summarize caseid

// Save the victims into a new datasset
save "stVictims.dta", replace

// restore the original collisions data
restore



*************** Creating Monthly Time Series ***************

// Preserve the data in memory (crashes)
preserve

// only keep observations for crashes
keep if crashesind == 1
summarize caseid

// Collapse the dataset using sum, mean and median values of selected variables
collapse (sum) crashes = crashesind parties = partycount victims = victimcount fatal = indfatal severe = indsevere multi = indmulti pedacc = pedaccident bicacc = bicaccident mcacc = mcaccident truckacc = truckaccident killed = numberkilled  injured = numberinjured severeinj = countsevereinj visibleinj = countvisibleinj paininj = countcomplaintpain killedcars = countcarkilled killedped = countpedkilled killedbic = countbickilled killedmc = countmckilled injcars = countcarinj injped = countpedinj injbic = countbicinj injmc = countmcinj alcohol = alcoholinvolved towaway = towaway atfault = atfault partykilled = partynumberkilled partyinj = partynumberinj (mean) mseverity = collseverityrank mparties = partycount mvictims = victimcount mkilled = numberkilled minjured = numberinjured msevereinj = countsevereinj mvisibleinj = countvisibleinj mpaininj = countcomplaintpain mkilledcars = countcarkilled mkilledped = countpedkilled mkilledbic = countbickilled mkilledmc = countmckilled minjcars = countcarinj minjped = countpedinj minjbic = countbicinj minjmc = countmcinj mhitrun = hitandrun mlighting = lighting mpartykilled = partynumberkilled mpartyinj = partynumberinj marea = areasqmi mpopdens = popdens mhudens = hudens mpopt =  popt mhut = hut mpopa = popa mpopb = popb mpoph = poph mpopw = popw mvehicles = vehicles mtraveltime = mtraveltime (median) mdpartyage = partyage mdvictimage = victimage, by(tsmonth)

// Label dataset
label data "OCSWITRS Crashes Monthly Time Series"

// Setup timeseries
tsset tsmonth

// Label summarized (collapsed) variables
label var crashes "Number of crashes"
label var parties "Number of parties"
label var victims "Number of victims"
label var fatal "Fatal crashes"
label var severe "Severe crashes"
label var multi "Crashes with multiple victims"
label var pedacc "Pedestrian accidents"
label var bicacc "Bicycle accidents"
label var mcacc "Motorcycle accidents"
label var truckacc "Truck accidents"
label var killed "Killed"
label var injured "Injured"
label var severeinj "Severe injures"
label var visibleinj "Visible injures"
label var paininj "Pain injuries"
label var killedcars "Killed in cars" 
label var killedped "Killed pedestrians"
label var killedbic "Killed bicyclists"
label var killedmc "Killed motorcyclists"
label var injcars "Injured in cars"
label var injped "Injured pedestrians"
label var injbic "Injured bicyclists"
label var injmc "Injured motorcyclists"
label var alcohol "Alcohol involved"
label var towaway "Towed away"
label var atfault "At fault"
label var partykilled "Killed parties"
label var partyinj "Injured parties"
label var mseverity "Mean ranked severity"
label var mparties "Mean number of parties"
label var mvictims "mean number of victims"
label var mkilled "Mean killed"
label var minjured "Mean injured"
label var msevereinj "Mean severe injures"
label var mvisibleinj "Mean visible injures"
label var mpaininj "Mean pain injuries"
label var mkilledcars "Mean killed in cars"
label var mkilledped "Mean killed pedestrians"
label var mkilledbic "Mean killed bicyclists"
label var mkilledmc "Mean killed motorcyclists"
label var minjped "Mean injured pedestrians"
label var minjbic "Mean injured bicyclists"
label var minjmc "Mean injured motorcyclists"
label var mhitrun "Mean hit-and-run severity"
label var mlighting "Mean lighting intensity"
label var mpartykilled "Mean killed parties"
label var mpartyinj "Mean injured parties"
label var marea "Mean city area (sq miles)"
label var mpopdens "Mean population density (sq miles)"
label var mhudens "Mean city housing density"
label var mpopt "Mean city population"
label var mhut "Mean city housing units"
label var mpopa "Mean city Asian population"
label var mpopb "Mean city Black population"
label var mpoph "Mean city Hispanic population"
label var mpopw "Mean city White population"
label var mvehicles "Mean number of commuting vehicles in city"
label var mtraveltime "Mean travel time per vehicle in city"
label var mdpartyage "Median party age"
label var mdvictimage "Median victim age"

// generate binary accident counts
gen fatalsevere = killed + severeinj
gen minorpain = visibleinj + paininj
label var fatalsevere "Fatal or severe accidents"
label var minorpain "Minor or pain accidents"
order fatalsevere minorpain, after(injmc)

// generate local polynomial smoothed line coordinates (and CI) for fatal/severe and minor/pain accidents respectively
lpoly fatalsevere tsmonth, generate(fatalseverelps) at(tsmonth) se(fatalseverelpci) nograph
lpoly minorpain tsmonth, generate(minorpainlps) at(tsmonth) se(minorpainlpci) nograph
label var fatalseverelps "LPS coordinates of fatal or severe accident counts"
label var fatalseverelpci "LPS 95% SE coordinates of fatal or severe accident counts"
label var minorpainlps "LPS coordinates of minor or pain accident counts"
label var minorpainlpci "LPS 95% SE coordinates of minor or pain accident counts"
order fatalseverelps minorpainlps fatalseverelpci minorpainlpci, after(minorpain)

// Standardize the LPS and LPCI variables to have the same mean and standard deviation
egen float zfatalseverelps = std(fatalseverelps), mean(0) std(1)
egen float zfatalseverelpci = std(fatalseverelpci), mean(0) std(1)
egen float zminorpainlps = std(minorpainlps), mean(0) std(1)
egen float zminorpainlpci = std(minorpainlpci), mean(0) std(1)
label var zfatalseverelps "Standardized LPS coordinates of fatal or severe accident counts"
label var zfatalseverelpci "Standardized LPS 95% SE coodrinates of fatal or severe accident counts"
label var zminorpainlps "Standardized LPS coordinates of minor or pain accident counts"
label var zminorpainlpci "Standardized 95% SE coordinates of minor or pain accident counts"
order zfatalseverelps zminorpainlps zfatalseverelpci zminorpainlpci, after(minorpainlpci)

// Save the time series into a new datasset
save "stTsMonthCrashes.dta", replace

// restore the original collisions data
restore



*************** Creating Weekly Time Series ***************

// Preserve the data in memory (crashes)
preserve

// only keep observations for crashes
keep if crashesind == 1
summarize caseid

// Collapse the dataset using sum, mean and median values of selected variables
collapse (sum) crashes = crashesind parties = partycount victims = victimcount fatal = indfatal severe = indsevere multi = indmulti pedacc = pedaccident bicacc = bicaccident mcacc = mcaccident truckacc = truckaccident killed = numberkilled  injured = numberinjured severeinj = countsevereinj visibleinj = countvisibleinj paininj = countcomplaintpain killedcars = countcarkilled killedped = countpedkilled killedbic = countbickilled killedmc = countmckilled injcars = countcarinj injped = countpedinj injbic = countbicinj injmc = countmcinj alcohol = alcoholinvolved towaway = towaway atfault = atfault partykilled = partynumberkilled partyinj = partynumberinj (mean) mseverity = collseverityrank mparties = partycount mvictims = victimcount mkilled = numberkilled minjured = numberinjured msevereinj = countsevereinj mvisibleinj = countvisibleinj mpaininj = countcomplaintpain mkilledcars = countcarkilled mkilledped = countpedkilled mkilledbic = countbickilled mkilledmc = countmckilled minjcars = countcarinj minjped = countpedinj minjbic = countbicinj minjmc = countmcinj mhitrun = hitandrun mlighting = lighting mpartykilled = partynumberkilled mpartyinj = partynumberinj marea = areasqmi mpopdens = popdens mhudens = hudens mpopt =  popt mhut = hut mpopa = popa mpopb = popb mpoph = poph mpopw = popw mvehicles = vehicles mtraveltime = mtraveltime (median) mdpartyage = partyage mdvictimage = victimage, by(tsweek)

 // Label dataset
label data "OCSWITRS Crashes Weekly Time Series"

// Setup timeseries
tsset tsweek

// Label summarized (collapsed) variables
label var crashes "Number of crashes"
label var parties "Number of parties"
label var victims "Number of victims"
label var fatal "Fatal crashes"
label var severe "Severe crashes"
label var multi "Crashes with multiple victims"
label var pedacc "Pedestrian accidents"
label var bicacc "Bicycle accidents"
label var mcacc "Motorcycle accidents"
label var truckacc "Truck accidents"
label var killed "Killed"
label var injured "Injured"
label var severeinj "Severe injures"
label var visibleinj "Visible injures"
label var paininj "Pain injuries"
label var killedcars "Killed in cars" 
label var killedped "Killed pedestrians"
label var killedbic "Killed bicyclists"
label var killedmc "Killed motorcyclists"
label var injcars "Injured in cars"
label var injped "Injured pedestrians"
label var injbic "Injured bicyclists"
label var injmc "Injured motorcyclists"
label var alcohol "Alcohol involved"
label var towaway "Towed away"
label var atfault "At fault"
label var partykilled "Killed parties"
label var partyinj "Injured parties"
label var mseverity "Mean ranked severity"
label var mparties "Mean number of parties"
label var mvictims "mean number of victims"
label var mkilled "Mean killed"
label var minjured "Mean injured"
label var msevereinj "Mean severe injures"
label var mvisibleinj "Mean visible injures"
label var mpaininj "Mean pain injuries"
label var mkilledcars "Mean killed in cars"
label var mkilledped "Mean killed pedestrians"
label var mkilledbic "Mean killed bicyclists"
label var mkilledmc "Mean killed motorcyclists"
label var minjped "Mean injured pedestrians"
label var minjbic "Mean injured bicyclists"
label var minjmc "Mean injured motorcyclists"
label var mhitrun "Mean hit-and-run severity"
label var mlighting "Mean lighting intensity"
label var mpartykilled "Mean killed parties"
label var mpartyinj "Mean injured parties"
label var marea "Mean city area (sq miles)"
label var mpopdens "Mean population density (sq miles)"
label var mhudens "Mean city housing density"
label var mpopt "Mean city population"
label var mhut "Mean city housing units"
label var mpopa "Mean city Asian population"
label var mpopb "Mean city Black population"
label var mpoph "Mean city Hispanic population"
label var mpopw "Mean city White population"
label var mvehicles "Mean number of commuting vehicles in city"
label var mtraveltime "Mean travel time per vehicle in city"
label var mdpartyage "Median party age"
label var mdvictimage "Median victim age"

// generate binary accident counts
gen fatalsevere = killed + severeinj
gen minorpain = visibleinj + paininj
label var fatalsevere "Fatal or severe accidents"
label var minorpain "Minor or pain accidents"
order fatalsevere minorpain, after(injmc)

// generate local polynomial smoothed line coordinates (and CI) for fatal/severe and minor/pain accidents respectively
lpoly fatalsevere tsweek, generate(fatalseverelps) at(tsweek) se(fatalseverelpci) nograph
lpoly minorpain tsweek, generate(minorpainlps) at(tsweek) se(minorpainlpci) nograph
label var fatalseverelps "LPS coordinates of fatal or severe accident counts"
label var fatalseverelpci "LPS 95% SE coordinates of fatal or severe accident counts"
label var minorpainlps "LPS coordinates of minor or pain accident counts"
label var minorpainlpci "LPS 95% SE coordinates of minor or pain accident counts"
order fatalseverelps minorpainlps fatalseverelpci minorpainlpci, after(minorpain)

// Standardize the LPS and LPCI variables to have the same mean and standard deviation
egen float zfatalseverelps = std(fatalseverelps), mean(0) std(1)
egen float zfatalseverelpci = std(fatalseverelpci), mean(0) std(1)
egen float zminorpainlps = std(minorpainlps), mean(0) std(1)
egen float zminorpainlpci = std(minorpainlpci), mean(0) std(1)
label var zfatalseverelps "Standardized LPS coordinates of fatal or severe accident counts"
label var zfatalseverelpci "Standardized LPS 95% SE coodrinates of fatal or severe accident counts"
label var zminorpainlps "Standardized LPS coordinates of minor or pain accident counts"
label var zminorpainlpci "Standardized 95% SE coordinates of minor or pain accident counts"
order zfatalseverelps zminorpainlps zfatalseverelpci zminorpainlpci, after(minorpainlpci)

// Save the time series into a new datasset
save "stTsWeekCrashes.dta", replace

// restore the original collisions data
restore



*************** Creating Daily Time Series ***************

// Preserve the data in memory (crashes)
preserve

// only keep observations for crashes
keep if crashesind == 1
summarize caseid

// Collapse the dataset using sum, mean and median values of selected variables
collapse (sum) crashes = crashesind parties = partycount victims = victimcount fatal = indfatal severe = indsevere multi = indmulti pedacc = pedaccident bicacc = bicaccident mcacc = mcaccident truckacc = truckaccident killed = numberkilled  injured = numberinjured severeinj = countsevereinj visibleinj = countvisibleinj paininj = countcomplaintpain killedcars = countcarkilled killedped = countpedkilled killedbic = countbickilled killedmc = countmckilled injcars = countcarinj injped = countpedinj injbic = countbicinj injmc = countmcinj alcohol = alcoholinvolved towaway = towaway atfault = atfault partykilled = partynumberkilled partyinj = partynumberinj (mean) mseverity = collseverityrank mparties = partycount mvictims = victimcount mkilled = numberkilled minjured = numberinjured msevereinj = countsevereinj mvisibleinj = countvisibleinj mpaininj = countcomplaintpain mkilledcars = countcarkilled mkilledped = countpedkilled mkilledbic = countbickilled mkilledmc = countmckilled minjcars = countcarinj minjped = countpedinj minjbic = countbicinj minjmc = countmcinj mhitrun = hitandrun mlighting = lighting mpartykilled = partynumberkilled mpartyinj = partynumberinj marea = areasqmi mpopdens = popdens mhudens = hudens mpopt =  popt mhut = hut mpopa = popa mpopb = popb mpoph = poph mpopw = popw mvehicles = vehicles mtraveltime = mtraveltime (median) mdpartyage = partyage mdvictimage = victimage, by(tsday)

 // Label dataset
label data "OCSWITRS Crashes Daily Time Series"

// Setup timeseries
tsset tsday

// Label summarized (collapsed) variables
label var crashes "Number of crashes"
label var parties "Number of parties"
label var victims "Number of victims"
label var fatal "Fatal crashes"
label var severe "Severe crashes"
label var multi "Crashes with multiple victims"
label var pedacc "Pedestrian accidents"
label var bicacc "Bicycle accidents"
label var mcacc "Motorcycle accidents"
label var truckacc "Truck accidents"
label var killed "Killed"
label var injured "Injured"
label var severeinj "Severe injures"
label var visibleinj "Visible injures"
label var paininj "Pain injuries"
label var killedcars "Killed in cars" 
label var killedped "Killed pedestrians"
label var killedbic "Killed bicyclists"
label var killedmc "Killed motorcyclists"
label var injcars "Injured in cars"
label var injped "Injured pedestrians"
label var injbic "Injured bicyclists"
label var injmc "Injured motorcyclists"
label var alcohol "Alcohol involved"
label var towaway "Towed away"
label var atfault "At fault"
label var partykilled "Killed parties"
label var partyinj "Injured parties"
label var mseverity "Mean ranked severity"
label var mparties "Mean number of parties"
label var mvictims "mean number of victims"
label var mkilled "Mean killed"
label var minjured "Mean injured"
label var msevereinj "Mean severe injures"
label var mvisibleinj "Mean visible injures"
label var mpaininj "Mean pain injuries"
label var mkilledcars "Mean killed in cars"
label var mkilledped "Mean killed pedestrians"
label var mkilledbic "Mean killed bicyclists"
label var mkilledmc "Mean killed motorcyclists"
label var minjped "Mean injured pedestrians"
label var minjbic "Mean injured bicyclists"
label var minjmc "Mean injured motorcyclists"
label var mhitrun "Mean hit-and-run severity"
label var mlighting "Mean lighting intensity"
label var mpartykilled "Mean killed parties"
label var mpartyinj "Mean injured parties"
label var marea "Mean city area (sq miles)"
label var mpopdens "Mean population density (sq miles)"
label var mhudens "Mean city housing density"
label var mpopt "Mean city population"
label var mhut "Mean city housing units"
label var mpopa "Mean city Asian population"
label var mpopb "Mean city Black population"
label var mpoph "Mean city Hispanic population"
label var mpopw "Mean city White population"
label var mvehicles "Mean number of commuting vehicles in city"
label var mtraveltime "Mean travel time per vehicle in city"
label var mdpartyage "Median party age"
label var mdvictimage "Median victim age"

// generate binary accident counts
gen fatalsevere = killed + severeinj
gen minorpain = visibleinj + paininj
label var fatalsevere "Fatal or severe accidents"
label var minorpain "Minor or pain accidents"
order fatalsevere minorpain, after(injmc)

// generate local polynomial smoothed line coordinates (and CI) for fatal/severe and minor/pain accidents respectively
lpoly fatalsevere tsday, generate(fatalseverelps) at(tsday) se(fatalseverelpci) nograph
lpoly minorpain tsday, generate(minorpainlps) at(tsday) se(minorpainlpci) nograph
label var fatalseverelps "LPS coordinates of fatal or severe accident counts"
label var fatalseverelpci "LPS 95% SE coordinates of fatal or severe accident counts"
label var minorpainlps "LPS coordinates of minor or pain accident counts"
label var minorpainlpci "LPS 95% SE coordinates of minor or pain accident counts"
order fatalseverelps minorpainlps fatalseverelpci minorpainlpci, after(minorpain)

// Standardize the LPS and LPCI variables to have the same mean and standard deviation
egen float zfatalseverelps = std(fatalseverelps), mean(0) std(1)
egen float zfatalseverelpci = std(fatalseverelpci), mean(0) std(1)
egen float zminorpainlps = std(minorpainlps), mean(0) std(1)
egen float zminorpainlpci = std(minorpainlpci), mean(0) std(1)
label var zfatalseverelps "Standardized LPS coordinates of fatal or severe accident counts"
label var zfatalseverelpci "Standardized LPS 95% SE coodrinates of fatal or severe accident counts"
label var zminorpainlps "Standardized LPS coordinates of minor or pain accident counts"
label var zminorpainlpci "Standardized 95% SE coordinates of minor or pain accident counts"
order zfatalseverelps zminorpainlps zfatalseverelpci zminorpainlpci, after(minorpainlpci)

// Save the time series into a new datasset
save "stTsDayCrashes.dta", replace

// restore the original collisions data
restore


*************** End of Processing ***************
