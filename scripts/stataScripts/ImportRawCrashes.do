// OCSWITS Import Raw Crashes Data Processing
// Version 1, Date: 2024-11-30

clear all

// Import crashes raw data
import delimited D:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\RawData\Crashes_20130101_20240630.csv, delimiter(comma) bindquote(strict) varnames(1)

label data "OCSWITRS Raw Crashes Stata Dataset"

// Case ID variable operations
ren case_id caseID
label var caseID "Case ID"
notes caseID : Unique Identifier of the crash case

// Create new CaseID (CID) variable
tostring caseID, generate(cid)
order cid, after(caseID)
label var cid "Crash ID"
notes cid : Unique identifier of the crash case

// Crashes indicator variable operations
egen byte crashes_indicator = tag(cid)
order crashes_indicator, after(cid)
label define crashes_indicator 1 "Crash" 0 ""
label values crashes_indicator crashes_indicator
label var crashes_indicator "Crashes Binary Indicator"
notes crashes_indicator : Binary flag, 1 if the record is a crash, 0 if not

// Accident year variable operations
ren accident_year accidentYear
label var accidentYear "Crash Year"
notes accidentYear : The year when the crash occurred

// Process date variable operations
ren proc_date procDate
label var procDate "Processing Date"
notes procDate : The date that the crash case was last changed

// Create new date variable from process date
gen dprocDate = date(procDate, "YMD")
format dprocDate %td
order dprocDate, before(procDate)
label var dprocDate "Processing Date (Stata Date)"
notes dprocDate : The date that the crash case was last changed (Stata date format)

// Jurisdiction variable operations
label var juris "Jurisdiction"
notes juris : Law enforcement agency that has jurisdiction over the crash
order juris, after(officer_id)

// collision date variable operations
ren collision_date collisionDate
label var collisionDate "Crash Date"
notes collisionDate : The date when the crash occurred

// Create new date variable from collision date
gen dcollisionDate = date(collisionDate, "YMD")
format dcollisionDate %td
order dcollisionDate, before(collisionDate)
label var dcollisionDate "Crash Date (Stata Date)"
notes dcollisionDate : The date when the crash occured (Stata date format)

// Crash time only variable operations
ren collision_time collisionTime
label var collisionTime "Crash Time"
notes collisionTime : The time when the crash occurred in 24h format


tostring collisionTime, generate(t0)
generate t1 = substr(t0, 1, 2)+":"+substr(t0,-2,2)+":00" if strlen(t0) == 4
replace t1 = "0"+substr(t0, 1, 1)+":"+substr(t0,-2,2)+":00" if strlen(t0) == 3
replace t1 = "00:" + t0 + ":00" if strlen(t0) == 2
replace t1 = "00:0" + t0 + ":00" if strlen(t0) == 1
generate t2 = collisionDate + " " + t1
generate t3 = clock(t2, "YMDhms")
format t3 %tc
drop t0 t1 t2
ren t3 collisionDatetime
order collisionDatetime, after(collisionTime)
label var collisionDatetime "Crash Date and Time (Stata Datetime)"
notes collisionDatetime : The date and time when the crash occured in 24h format (Stata datetime format)

// Officer id variable operations
ren officer_id officerID
label var officerID "Officer ID"
notes officerID : The badge number of the officer who wrote the crash report

// Reporting district variable operations
ren reporting_district reportingDistrict
label var reportingDistrict "Reporting District"
notes reportingDistrict : Reporting District on the crash report

// Day of the week variable operations
ren day_of_week weekDay
label define weekDay  1 "Monday" 2 "Tuesday" 3 "Wednesday" 4 "Thursday" 5 "Friday" 6 "Saturday" 7 "Sunday"
label values weekDay weekDay
label var weekDay "Day of Week"
notes weekDay : Code for the day of the week when the crash occurred
order weekDay, after(collisionDatetime)

// Crash month only variable operations
gen collisionMonth = month(dcollisionDate)
label define collisionMonth  1 "January" 2 "February" 3 "March" 4 "April" 5 "May" 6 "June" 7 "July" 8 "August" 9 "September" 10 "October" 11 "November" 12 "December"
label values collisionMonth collisionMonth
label var collisionMonth "Crash Month"
notes collisionMonth : Month number from crash date
order collisionMonth, before(weekDay)

// Crash time intervals variable operations
gen byte collisionTimeIntervals = 1 if collisionTime <= 600
replace collisionTimeIntervals = 2 if collisionTime > 600 & collisionTime <= 1200
replace collisionTimeIntervals = 3 if collisionTime > 1200 & collisionTime <= 1800
replace collisionTimeIntervals = 4 if collisionTime > 1800 & collisionTime <= 2400
replace collisionTimeIntervals = 9 if collisionTime > 2400
label define collisionTimeIntervals  1 "Night (00:00am to 06:00am)" 2 "Morning (06:00am to 12:00pm)" 3 "Afternoon (12:00pm to 06:00pm)" 4 "Evening (06:00pm to 00:00am)" 9 "Unknown Time"
label values collisionTimeIntervals collisionTimeIntervals
label var collisionTimeIntervals "Crash Time Intervals"
notes collisionTimeIntervals : Crash time interval ranges classification
order collisionTimeIntervals, after(collisionTime)

// Rush hours variable operations
gen byte rushHours

label define collision_time_rush_hours  1 "Rush Hours (Morning)" 2 "Rush Hours (Evening)" 3 "Non-Rush Hours" 999 "Unknown Time"
label values collision_time_rush_hours collision_time_rush_hours
label var collision_time_rush_hours "Rush Hours"
notes collision_time_rush_hours : Rush hours interval ranges (Mon-Fri mornings and evenings)







