
// OCSWITS Crashes Data Processing
// Version 2, Date: 2024-11-27

clear all

// Importing dfCrashes row data
import delimited D:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfCrashes_final.csv, delimiter(comma) bindquote(strict) varnames(1) stripquote(yes)

label data "OCSWITRS Crashes Stata Dataset"

// Case ID variable operations
label var case_id "Case ID"
notes case_id : Unique Identifier of the crash case

// CID variable operations
label var cid "Crash ID"
notes cid : Unique identifier of the crash case

// Crashes indicator variable operations
egen byte crashes_indicator = tag(cid)
order crashes_indicator, after(cid)
label define crashes_indicator 1 "Crash" 0 ""
label values crashes_indicator crashes_indicator
label var crashes_indicator "Crashes Binary Indicator"
notes crashes_indicator : Binary flag, 1 if the record is a crash, 0 if not

// City variable operations
label var city "City"
notes city : Reported City of the crash

// City name variable operations
label var city_name "City Name"
notes city_name : City name from locational query

// Place type variable operations
label var place_type "Place Type"
notes place_type : City or Unincorporated Area

// Crash date and time variable operations
label var collision_datetime "Crash Date and Time"
notes collision_datetime : Full date and time string of the crash

// Create new datetime variable from string (NEW)
gen datetime_crash = clock(collision_datetime, "YMDhms")
format datetime_crash %tc
order datetime_crash, after(collision_datetime)
label var datetime_crash "Crash Datetime (formatted)"
notes datetime_crash: Converted datetime formatted variable for Stata

// Crash date only variable operations
label var collision_date "Crash Date"
notes collision_date : The date when the crash occurred

// Create new date variable from string (NEW)
gen date_crash = date(collision_date, "YMD")
format date_crash %td
order date_crash, after(collision_date)
label var date_crash "Crash Date (formatted)"
notes date_crash: Converted data formatted variable for Stata

// Crash time only variable operations
label var collision_time "Crash Time"
notes collision_time : The time when the crash occurred in 24h format

// Crash year only variable operations
label var accident_year "Crash Year"
notes accident_year : The year when the crash occurred

// Crash month only variable operations
label define collision_month  1 "January" 2 "February" 3 "March" 4 "April" 5 "May" 6 "June" 7 "July" 8 "August" 9 "September" 10 "October" 11 "November" 12 "December"
label values collision_month collision_month
label var collision_month "Crash Month"
notes collision_month : Month number from crash date

// Day of the week variable operations
label define day_of_week  1 "Monday" 2 "Tuesday" 3 "Wednesday" 4 "Thursday" 5 "Friday" 6 "Saturday" 7 "Sunday"
label values day_of_week day_of_week
label var day_of_week "Day of Week"
notes day_of_week : Code for the day of the week when the crash occurred

// Processing date variable operations
label var proc_date "Processing Date"
notes proc_date : The date that the crash case was last changed

// Crash time intervals variable operations
label define collision_time_intervals  1 "Night (00:00am to 06:00am)" 2 "Morning (06:00am to 12:00pm)" 3 "Afternoon (12:00pm to 06:00pm)" 4 "Evening (06:00pm to 00:00am)" 999 "Unknown Time"
label values collision_time_intervals collision_time_intervals
label var collision_time_intervals "Crash Time Intervals"
notes collision_time_intervals : Crash time interval ranges classification

// Rush hours variable operations
label define collision_time_rush_hours  1 "Rush Hours (Morning)" 2 "Rush Hours (Evening)" 3 "Non-Rush Hours" 999 "Unknown Time"
label values collision_time_rush_hours collision_time_rush_hours
label var collision_time_rush_hours "Rush Hours"
notes collision_time_rush_hours : Rush hours interval ranges (Mon-Fri mornings and evenings)

// Crash severity variable operations
label define collision_severity  0 "No injury, aka property damage only or PDO" 1 "Fatal injury" 2 "Suspected serous injury or severe injury" 3 "Suspected minor injury or visible injury" 4 "Possible injury or complaint of pain"
label values collision_severity collision_severity
label var collision_severity "Crash Severity"
notes collision_severity : The worst injury suffered by any victim in the crash

// Binary crash severity variable operations
label define collision_severity_binary  0 "Minor (minor injury, pain, or no injury)" 1 "Severe (killed or serious injury)"
label values collision_severity_binary collision_severity_binary
label var collision_severity_binary "Crash Severity (binary)"
notes collision_severity_binary : Binary classification of the worst injury suffered by any victim in the crash

// Reclassified crash severity variable operations
label define collision_severity_reclass  0 "None" 1 "Possible Injury or Pain" 2 "Minor or Visible Injury" 3 "Serious or Severe Injury" 4 "Fatal Injury"
label values collision_severity_reclass collision_severity_reclass
label var collision_severity_reclass "Crash Severity Reclassified"
notes collision_severity_reclass : Reclassified crash severity based on the worst injury suffered by any victim in the crash

// Ranked crash severity variable operations
label define collision_severity_ranked  0 "None or Minor Injuries" 1 "Single Injury (Severe)" 2 "Multiple Injuries (Severe)" 3 "Single Fatality, No Injuries (Fatal)" 4 "Single Fatality, Single Injury (Fatal)" 5 "Single Fatality, Multiple Injuries (Fatal)" 6 "Multiple Fatalities, No Injuries (Fatal)" 7 "Multiple Fatalities, Single Injury (Fatal)" 8 "Multiple Fatalities, Multiple Injuries (Fatal)"
label values collision_severity_ranked collision_severity_ranked
label var collision_severity_ranked "Crash Severity Ranked"
notes collision_severity_ranked : Ranked crash severity based on the worst injury suffered by any victim in the crash

// Generate indicator variables for severity ranks (NEW)
recode collision_severity_ranked (0 3 6 = 0) (1 2 4 5 7 8 = 1) (missing=.), generate(ind_severe)
recode collision_severity_ranked (0 1 2 = 0) (3 4 5 6 7 8 = 1) (missing=.), generate(ind_fatal)
recode collision_severity_ranked (0 1 3 4 = 0) (2 5 6 7 8 = 1) (missing=.), generate(ind_multi)

// Severe indicator variable operations (NEW)
order ind_severe, after(collision_severity_ranked)
label define ind_severe 0 "Not a severe injury" 1 "Severe injury"
label values ind_severe ind_severe
label var ind_severe "Severe Injury Indicator"
notes ind_severe: Reclassified indicator variable from severity level where there exist severe injuries in the accident

// Fatal indicator variable operations (NEW)
order ind_fatal, after(ind_severe)
label define ind_fatal 0 "Not a fatal injury" 1 "Fatal injury"
label values ind_fatal ind_fatal
label var ind_fatal "Fatal Injury Indicator"
notes ind_fatal: Reclassified indicator variable from severity level where there exist fatal injuries in the accident

// Multiple indicator variable operations (NEW)
order ind_multi, after(ind_fatal)
label define ind_multi 0 "No multiple severe or fatal injuries present" 1 "Multiple severe or fatal injuries present"
label values ind_multi ind_multi
label var ind_multi "Multiple Injury Indicator"
notes ind_multi: Reclassified indicator variable from severity level where there exist multiple severe or fatal injuries in the accident

// Party count variable operations
label var party_count "Party Count"
notes party_count : Number of parties involved in the crash

// Victim count variable operations
label var victim_count "Victim Count"
notes victim_count : Number of victims involved in each party

// Killed victims variable operations
label var number_killed "Killed Victims"
notes number_killed : Number of killed victims

// Injured victims variable operations
label var number_injured "Injured Victims"
notes number_injured : Number of injured victims

// Severe injury count variable operations
label var count_severe_inj "Severe Injury Count"
notes count_severe_inj : Number of victims in the crash with suspected serous injury or severe injury

// Other visible injury count variable operations
label var count_visible_inj "Other Visible Injury Count"
notes count_visible_inj : Number of victims in the crash with suspected minor injury or visible injury

// Complaint of pain injury count variable operations
label var count_complaint_pain "Complaint of Pain Injury Count"
notes count_complaint_pain : Number of victims in the crash with possible injury or complaint of pain

// Pedestrians killed variable operations
label var count_ped_killed "Pedestrian Killed Count"
notes count_ped_killed : Number of killed pedestrian victims

// Pedestrians injured variable operations
label var count_ped_injured "Pedestrian Injured Count"
notes count_ped_injured : Number of injured pedestrian victims

// Bicyclists killed variable operations
label var count_bicyclist_killed "Bicyclists Killed Count"
notes count_bicyclist_killed : Number of killed bicyclists

// Bicyclists injured variable operations
label var count_bicyclist_injured "Bicyclists Injured Count"
notes count_bicyclist_injured : Number of injured bicyclists

// Motorcyclists killed variable operations
label var count_mc_killed "Motorcyclist Killed Count"
notes count_mc_killed : Number of killed motorcyclists

// Motorcyclists injured variable operations
label var count_mc_injured "Motorcyclist Injured Count"
notes count_mc_injured : Number of injured motorcyclists

// Primary crash factor variable operations
ren primary_coll_factor temp
gen byte primary_coll_factor = 0 if temp == "-"
replace primary_coll_factor = 1 if temp == "A"
replace primary_coll_factor = 2 if temp == "B"
replace primary_coll_factor = 3 if temp == "C"
replace primary_coll_factor = 4 if temp == "D"
replace primary_coll_factor = 5 if temp == "E"
order primary_coll_factor, before(temp)
drop temp
label define primary_coll_factor 0 "Not Stated" 1 "Vehicle Code Violation" 2 "Other Improper Driving" 3 "Other than Driver" 4 "Unknown" 5 "Fell Asleep"
label values primary_coll_factor primary_coll_factor
label var primary_coll_factor "Primary Crash Factor"
notes primary_coll_factor : The primary cause of the crash

// Type of crash variable operations
ren type_of_collision temp
gen byte type_of_collision = 0 if temp == "-"
replace type_of_collision = 1 if temp == "A"
replace type_of_collision = 2 if temp == "B"
replace type_of_collision = 3 if temp == "C"
replace type_of_collision = 4 if temp == "D"
replace type_of_collision = 5 if temp == "E"
replace type_of_collision = 6 if temp == "F"
replace type_of_collision = 7 if temp == "G"
replace type_of_collision = 8 if temp == "H"
order type_of_collision, before(temp)
drop temp
label define type_of_collision 0 "Not Stated" 1 "Head-on" 2 "Sideswipe" 3 "Rear-end" 4 "Broadside" 5 "Hit object" 6 "Overturned" 7 "Vehicle/pedestrian" 8 "Other"
label values type_of_collision type_of_collision
label var type_of_collision "Type of Crash"
notes type_of_collision : The general type of crash as determined by the first injury or damage-causing event

// Pedestrian crash variable operations
ren pedestrian_accident temp
gen byte pedestrian_accident = 1 if temp == "Y"
replace pedestrian_accident = 0 if temp == ""
order pedestrian_accident, before(temp)
drop temp
label define pedestrian_accident 0 "No" 1 "Yes"
label values pedestrian_accident pedestrian_accident
label var pedestrian_accident "Pedestrian Crash"
notes pedestrian_accident : Indicates whether the crash involved a pedestrian

// Bicycle crash variable operations
ren bicycle_accident temp
gen byte bicycle_accident = 1 if temp == "Y"
replace bicycle_accident = 0 if temp == ""
order bicycle_accident, before(temp)
drop temp
label define bicycle_accident 0 "No" 1 "Yes"
label values bicycle_accident bicycle_accident
label var bicycle_accident "Bicycle Crash"
notes bicycle_accident : Indicates whether the crash involved a bicycle

// motorcycle accident variable operations
ren motorcycle_accident temp
gen byte motorcycle_accident = 1 if temp == "Y"
replace motorcycle_accident = 0 if temp == ""
order motorcycle_accident, before(temp)
drop temp
label define motorcycle_accident 0 "No" 1 "Yes"
label values motorcycle_accident motorcycle_accident
label var motorcycle_accident "Motorcycle Crash"
notes motorcycle_accident : Indicates whether the crash involved a motorcycle

// truck accident variable operations
ren truck_accident temp
gen byte truck_accident = 1 if temp == "Y"
replace truck_accident = 0 if temp == ""
order truck_accident, before(temp)
drop temp
label define truck_accident 0 "No" 1 "Yes"
label values truck_accident truck_accident
label var truck_accident "Truck Crash"
notes truck_accident : Indicates whether the crash involved a big truck

// hit and run variable operations
ren hit_and_run temp
gen byte hit_and_run = 0 if temp == "N"
replace hit_and_run = 1 if temp == "M"
replace hit_and_run = 2 if temp == "F"
order hit_and_run, before(temp)
drop temp
label define hit_and_run 0 "Not Hit and Run" 1 "Misdemeanor" 2 "Felony"
label values hit_and_run hit_and_run
label var hit_and_run "Hit and Run"
notes hit_and_run : A flag to indicate the severity of hit-and-run crash. Felony hit-and-run resulted in injury or death to other parties. Misdemeanor hit-and-run did not result in injury or death to other parties

// Alcohol involved variable operations
ren alcohol_involved temp
gen byte alcohol_involved = 1 if temp == "Y"
replace alcohol_involved = 0 if temp == ""
order alcohol_involved, before(temp)
drop temp
label define alcohol_involved 0 "No" 1 "Yes"
label values alcohol_involved alcohol_involved
label var alcohol_involved "Alcohol Inovlved"
notes alcohol_involved : Indicates whether the crash involved a party that had been drinking. Note - a passenger does not count as a party

// Jurisdiction variable operations
label var juris "Jurisdiction"
notes juris : Law enforcement agency that has jurisdiction over the crash

// Officer id variable operations
label var officer_id "Officer ID"
notes officer_id : The badge number of the officer who wrote the crash report

// Reporting district variable operations
label var reporting_district "Reporting District"
notes reporting_district : Reporting District on the crash report

// chp shift variable operations
label define chp_shift  1 "0600 thru 1359" 2 "1400 thru 2159" 3 "2200 thru 0559" 4 "CHP Not Stated" 5 "Not CHP"
label values chp_shift chp_shift
label var chp_shift "CHP Shift"
notes chp_shift : CHP shift at the time of the crash

// County city location
label var cnty_city_loc "County City Location"
notes cnty_city_loc : The city or unincorporated county where the crash occurred

// Special condition variable operations
label define special_cond  0 "Not Above" 1 "Schoolbus on Public Roadway" 2 "State University (Also SFIA)" 3 "Schoolbus Not on Public Roadway" 4 "Offroad (Unimproved)" 5 "Vista Point or Rest Area or Sales or Inspection Facility" 6 "Other Public Access (Improved)"
label values special_cond special_cond
label var special_cond "Special Condition"
notes special_cond : A computed value. O means not private property

// Beat type variable operations
label define beat_type  0 "Not CHP" 1 "CHP State Highway" 2 "CHP County RoadLine" 3 "CHP County RoadArea" 4 "Schoolbus on City Roadway" 5 "Schoolbus not on Public Roadway" 6 "Offroad (Unimproved)" 7 "Vista Point or Rest Area or Scales or Inspection Facility" 8 "Other Public Access (Improved)"
label values beat_type beat_type
label var beat_type "Beat Type"
notes beat_type : Location of crash based on beat

//chp beat type variable operations
ren chp_beat_type temp
gen byte chp_beat_type = 0 if temp == "0"
replace chp_beat_type = 1 if temp == "1"
replace chp_beat_type = 2 if temp == "2"
replace chp_beat_type = 3 if temp == "3"
replace chp_beat_type = 4 if temp == "4"
replace chp_beat_type = 5 if temp == "5"
replace chp_beat_type = 6 if temp == "6"
replace chp_beat_type = 7 if temp == "7"
replace chp_beat_type = 8 if temp == "8"
replace chp_beat_type = 0 if temp == "9"
order chp_beat_type, before(temp)
drop temp
label define chp_beat_type 0 "Not CHP" 1 "Interstate" 2 "US Highway" 3 "State Route" 4 "County Road Line" 5 "County Road Area" 6 "US Highway" 7 "State Route" 8 "County RoadLine" 9 "County RoadArea"
label values chp_beat_type chp_beat_type
label var chp_beat_type "CHP Beat Type"
notes chp_beat_type : Location of crash based on beat

// chp beat class variable operations
label define chp_beat_class  0 "Not CHP" 1 "CHP Primary" 2 "CHP Other"
label values chp_beat_class chp_beat_class
label var chp_beat_class "CHP Beat Class"
notes chp_beat_class : Location of crash based on beat

// Beat number variable operations
label var beat_number "Beat Number"
notes beat_number : Beat of the officer who reported the crash

// Primary road variable operations
label var primary_rd "Primary Road"
notes primary_rd : The name of the roadway on which the crash occurred

// Secondary road variable operations
label var secondary_rd "Secondary Road"
notes secondary_rd : The name of the roadway that intersects the primary roadway

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
ren weather_1 temp
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
ren weather_2 temp
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
label define weather_combined  0 "Not Stated" 10 "Clear" 12 "Clear Cloudy" 13 "Clear Other" 14 "Clear Wind" 15 "Clear Raining" 16 "Clear Snowing" 17 "Clear Fog" 20 "Cloudy" 21 "Cloudy Clear" 23 "Cloudy Other" 24 "Cloudy Wind" 25 "Cloudy Raining" 26 "Cloudy Snowing" 27 "Cloudy Fog" 30 "Other" 31 "Other Clear" 32 "Other Cloudy" 34 "Other Wind" 35 "Other Raining" 36 "Other Snowing" 37 "Other Fog" 40 "Wind" 41 "Wind Clear" 42 "Wind Cloudy" 43 "Wind Other" 45 "Wind Raining" 46 "Wind Snowing" 47 "Wind Fog" 50 "Raining" 51 "Raining Clear" 52 "Raining Cloudy" 53 "Raining Other" 54 "Raining Wind" 56 "Raining Snowing" 57 "Raining Fog" 60 "Snowing" 61 "Snowing Clear" 62 "Snowing Cloudy" 63 "Snowing Other" 64 "Snowing Wind" 65 "Snowing Raining" 67 "Snowing Fog" 70 "Fog" 71 "Fog Clear" 72 "Fog Cloudy" 73 "Fog Other" 74 "Fog Wind" 75 "Fog Raining" 76 "Fog Snowing"
label values weather_combined weather_combined
label var weather_combined "Combined Weather Conditions"
notes weather_combined : Combined Weather Conditions from WEATHER_1 and WEATHER_2 fields in numeric codes by weather conditions severity

// Road surface variable operations
ren road_surface temp
gen byte road_surface = 0 if temp == "-"
replace road_surface = 1 if temp == "A"
replace road_surface = 2 if temp == "B"
replace road_surface = 3 if temp == "C"
replace road_surface = 4 if temp == "D"
replace road_surface = 5 if temp == "O"
order road_surface, before(temp)
drop temp
label define road_surface 0 "Not Stated" 1 "Dry" 2 "Wet" 3 "Snowy or Icy" 4 "Slippery (muddy, oily, etc)" 5 "Other"
label values road_surface road_surface
label var road_surface "Road Surface"
notes road_surface : Roadway surface condition at the time of the crash in the traffic lane(s) involved

// Road conditions 1 variable operations
ren road_cond_1 temp
gen byte road_cond1 = 0 if temp == "-"
replace road_cond1 = 1 if temp == "A"
replace road_cond1 = 2 if temp == "B"
replace road_cond1 = 3 if temp == "C"
replace road_cond1 = 4 if temp == "D"
replace road_cond1 = 5 if temp == "E"
replace road_cond1 = 6 if temp == "F"
replace road_cond1 = 7 if temp == "G"
replace road_cond1 = 8 if temp == "H"
order road_cond1, before(temp)
drop temp
label define road_cond1 0 "Not Stated" 1 "Holes, deep ruts" 2 "Loose material on roadway" 3 "obstruction on roadway" 4 "Construction or repair zone" 5 "Reduced roadaway width" 6 "Flooded" 7 "Other" 8 "No unusual condition"
label values road_cond1 road_cond1
label var road_cond1 "Road Condition 1"
notes road_cond1 : Roadway condition at the time of the crash in the traffic lane(s) involved

// Road conditions 2 variable operations
ren road_cond_2 temp
gen byte road_cond2 = 0 if temp == "-"
replace road_cond2 = 1 if temp == "A"
replace road_cond2 = 2 if temp == "B"
replace road_cond2 = 3 if temp == "C"
replace road_cond2 = 4 if temp == "D"
replace road_cond2 = 5 if temp == "E"
replace road_cond2 = 6 if temp == "F"
replace road_cond2 = 7 if temp == "G"
replace road_cond2 = 8 if temp == "H"
order road_cond2, before(temp)
drop temp
label define road_cond2 0 "Not Stated" 1 "Holes, deep ruts" 2 "Loose material on roadway" 3 "obstruction on roadway" 4 "Construction or repair zone" 5 "Reduced roadaway width" 6 "Flooded" 7 "Other" 8 "No unusual condition"
label values road_cond2 road_cond2
label var road_cond2 "Road Condition 2"
notes road_cond2 : Second roadway condition at the time of the crash in the traffic lane(s) involved

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
ren control_device temp
gen byte control_device = 0 if temp == "-"
replace control_device = 1 if temp == "A"
replace control_device = 2 if temp == "B"
replace control_device = 3 if temp == "C"
replace control_device = 4 if temp == "D"
order control_device, before(temp)
drop temp
label define control_device 0 "Not Stated" 1 "Functioning" 2 "Not functioning" 3 "Obscured" 4 "None"
label values control_device control_device
label var control_device "Control Device"
notes control_device : Presence and condition of crash related traffic control devices at the time of the crash. Control devices include regulatory, warning, and construction sings. This excludes striping and officers or other persons directing traffic

// State highway indicator variable operations
ren state_hwy_ind temp
gen byte state_hwy_ind = 0 if temp=="N"
replace state_hwy_ind = 1 if temp=="Y"
replace state_hwy_ind = . if temp==""
order state_hwy_ind, before(temp)
drop temp
label define state_hwy_ind 0 "No" 1 "Yes"
label values state_hwy_ind state_hwy_ind
label var state_hwy_ind "State Highway Indicator"
notes state_hwy_ind : A flag to indicate whether the crash is on or near a state highway

// Side of highway variable operations
ren side_of_hwy temp
gen byte side_of_hwy = 0 if temp == ""
replace side_of_hwy = 1 if temp == "N"
replace side_of_hwy = 2 if temp == "S"
replace side_of_hwy = 3 if temp == "E"
replace side_of_hwy = 4 if temp == "W"
replace side_of_hwy = 5 if temp == "L"
replace side_of_hwy = 6 if temp == "R"
order side_of_hwy, before(temp)
drop temp
label define side_of_hwy 0 "Not Stated" 1 "North" 2 "South" 3 "East" 4 "West" 5 "Left" 6 "Right"
label values side_of_hwy side_of_hwy
label var side_of_hwy "Side of Highway"
notes side_of_hwy : Code provided by Caltrans Coders, applies to divided highway, based on nominal direction of route, for single vehicle is same as nominal direction of travel, overruled by impact with second vehicle after crossing median

// Tow away variable operations
ren tow_away temp
gen byte tow_away = 0 if temp == "N"
replace tow_away = 1 if temp == "Y"
replace tow_away = . if temp ==""
order tow_away, before(temp)
drop temp
label define tow_away 0 "No" 1 "Yes"
label values tow_away tow_away
label var tow_away "Tow Away"
notes tow_away : A flag to indicate whether the vehicle was towed away from the crash scene

// PCF violation code variable operations
ren pcf_code_of_viol temp
gen byte pcf_code_of_viol = 0 if temp == "-"
replace pcf_code_of_viol = 1 if temp == "B"
replace pcf_code_of_viol = 2 if temp == "C"
replace pcf_code_of_viol = 3 if temp == "H"
replace pcf_code_of_viol = 4 if temp == "I"
replace pcf_code_of_viol = 5 if temp == "O"
replace pcf_code_of_viol = 6 if temp == "P"
replace pcf_code_of_viol = 7 if temp == "S"
replace pcf_code_of_viol = 8 if temp == "W"
replace pcf_code_of_viol = . if temp == ""
order pcf_code_of_viol, before(temp)
drop temp
label define pcf_code_of_viol 0 "Not Stated" 1 "Business and Professions" 2 "Vehicle" 3 "City Health and Safety" 4 "City Ordinance" 5 "County Ordinance" 6 "Penal" 7 "Streets and Highways" 8 "Welfare and Institutions"
label values pcf_code_of_viol pcf_code_of_viol
label var pcf_code_of_viol "PCF Violation Code"
notes pcf_code_of_viol : The law code that was violated and was the primary cause of the crash

// PCF violation category variable operations
ren pcf_viol_category temp
gen byte pcf_viol_category = 0 if temp == "0"
replace pcf_viol_category = 1 if temp == "1"
replace pcf_viol_category = 2 if temp == "2"
replace pcf_viol_category = 3 if temp == "3"
replace pcf_viol_category = 4 if temp == "4"
replace pcf_viol_category = 5 if temp == "5"
replace pcf_viol_category = 6 if temp == "6"
replace pcf_viol_category = 7 if temp == "7"
replace pcf_viol_category = 8 if temp == "8"
replace pcf_viol_category = 9 if temp == "9"
replace pcf_viol_category = 10 if temp == "10"
replace pcf_viol_category = 11 if temp == "11"
replace pcf_viol_category = 12 if temp == "12"
replace pcf_viol_category = 13 if temp == "13"
replace pcf_viol_category = 14 if temp == "14"
replace pcf_viol_category = 15 if temp == "15"
replace pcf_viol_category = 16 if temp == "16"
replace pcf_viol_category = 17 if temp == "17"
replace pcf_viol_category = 18 if temp == "18"
replace pcf_viol_category = 21 if temp == "21"
replace pcf_viol_category = 22 if temp == "22"
replace pcf_viol_category = 23 if temp == "23"
replace pcf_viol_category = 24 if temp == "24"
replace pcf_viol_category = 99 if temp == "-"
order pcf_viol_category, before(temp)
drop temp
label define pcf_viol_category 0 "Unknown" 1 "Driving or bicycling under the influence of alcohol or drugs" 2 "Impeding traffic" 3 "Unsafe speed" 4 "Following too closely" 5 "Wrong side of the road" 6 "Improper passing" 7 "Unsafe lane change" 8 "Improper turning" 9 "Automobile right of way" 10 "Pedestrian right of way" 11 "Pedestrian violation" 12 "Traffic signals and signs" 13 "hazardous parking" 14 "Lights" 15 "Brakes" 16 "Other equipment" 17 "Othe hazardous violation" 18 "Other than driver or pedestrian" 21 "Unsafe starting or backing" 22 "Other improper driving" 23 "Pedestrian or other under the influence of alcohol or drugs" 24 "Fell asleep" 99 "Not Stated"
label values pcf_viol_category pcf_viol_category
label var pcf_viol_category "PCF Violation Category"
notes pcf_viol_category : A value computed from the law section that was given as the primary cause of the crash

// PCF violation variable operations
label var pcf_violation "PCF Violation"
notes pcf_violation : The law section given as the primary cause of the crash. The subsection is in the data element pcf_viol_subsection

// PCF violation subsection variable operations
label var pcf_viol_subsection "PCF Violation Subsection"
notes pcf_viol_subsection : The subsection of the law section given as the primary cause of the crash in the data element pcf_violation

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
ren ped_action temp
gen byte ped_action = 0 if temp == "-"
replace ped_action = 1 if temp == "A"
replace ped_action = 2 if temp == "B"
replace ped_action = 3 if temp == "C"
replace ped_action = 4 if temp == "D"
replace ped_action = 5 if temp == "E"
replace ped_action = 6 if temp == "F"
replace ped_action = 7 if temp == "G"
order ped_action, before(temp)
drop temp
label define ped_action 0 "Not stated" 1 "No pedestrian involved" 2 "Crossing in crosswalk at intersection" 3 "Crossing in crosswalk not at intersection" 4 "Crossing not in crosswalk" 5 "In road, including shoulder" 6 "Not in road" 7 "Approaching or leaving school bus"
label values ped_action ped_action
label var ped_action "Ped Action"
notes ped_action : The action just prior to the crash of the first pedestrian injured or otherwise involved

// Not private property variable operations
ren not_private_property temp
gen byte not_private_property = 0 if (temp == "" | temp == "N")
replace not_private_property = 1 if temp == "Y"
order not_private_property, before(temp)
drop temp
label define not_private_property 0 "No" 1 "Yes"
label values not_private_property not_private_property
label var not_private_property "Not Private Property"
notes not_private_property : Y indicates that the crash did not occur on private property

// Statewide veiche type at fault variable operations
ren stwd_vehtype_at_fault temp
gen byte stwd_vehtype_at_fault = 0 if temp == "-"
replace stwd_vehtype_at_fault = 1 if temp == "A"
replace stwd_vehtype_at_fault = 2 if temp == "B"
replace stwd_vehtype_at_fault = 3 if temp == "C"
replace stwd_vehtype_at_fault = 4 if temp == "D"
replace stwd_vehtype_at_fault = 5 if temp == "E"
replace stwd_vehtype_at_fault = 6 if temp == "F"
replace stwd_vehtype_at_fault = 7 if temp == "G"
replace stwd_vehtype_at_fault = 8 if temp == "H"
replace stwd_vehtype_at_fault = 9 if temp == "I"
replace stwd_vehtype_at_fault = 10 if temp == "J"
replace stwd_vehtype_at_fault = 11 if temp == "K"
replace stwd_vehtype_at_fault = 12 if temp == "L"
replace stwd_vehtype_at_fault = 13 if temp == "M"
replace stwd_vehtype_at_fault = 14 if temp == "N"
replace stwd_vehtype_at_fault = 15 if temp == "O"
order stwd_vehtype_at_fault, before(temp)
drop temp
label define stwd_vehtype_at_fault 0 "Not stated" 1 "Passenger car/station wagon" 2 "Passenger car with trailer" 3 "Motorcycle/scooter" 4 "pickup or panel truck" 5 "Pickup or panel truck with trailer" 6 "Truck or truck tractor" 7 "Truck or truck tractor with trrailer" 8 "School bus" 9 "Other bus" 10 "Emergency vehicle" 11 "Highway construction equipment" 12 "Bicycle" 13 "Other vehicle" 14 "Pedestrian" 15 "Moped"
label values stwd_vehtype_at_fault stwd_vehtype_at_fault
label var stwd_vehtype_at_fault "Statewide Vehicle Type at Fault"
notes stwd_vehtype_at_fault : Indicates the Statewide Vehicle Type of the party who is at fault

// CHP vehicle type at fault variable operations
ren chp_vehtype_at_fault temp
gen byte chp_vehtype_at_fault = 0 if temp == "-"
replace chp_vehtype_at_fault = 1 if temp == "1"
replace chp_vehtype_at_fault = 2 if temp == "2"
replace chp_vehtype_at_fault = 3 if temp == "3"
replace chp_vehtype_at_fault = 4 if temp == "4"
replace chp_vehtype_at_fault = 5 if temp == "5"
replace chp_vehtype_at_fault = 6 if temp == "6"
replace chp_vehtype_at_fault = 7 if temp == "7"
replace chp_vehtype_at_fault = 8 if temp == "8"
replace chp_vehtype_at_fault = 9 if temp == "9"
replace chp_vehtype_at_fault = 10 if temp == "10"
replace chp_vehtype_at_fault = 11 if temp == "11"
replace chp_vehtype_at_fault = 12 if temp == "12"
replace chp_vehtype_at_fault = 13 if temp == "13"
replace chp_vehtype_at_fault = 14 if temp == "14"
replace chp_vehtype_at_fault = 15 if temp == "15"
replace chp_vehtype_at_fault = 16 if temp == "16"
replace chp_vehtype_at_fault = 17 if temp == "17"
replace chp_vehtype_at_fault = 18 if temp == "18"
replace chp_vehtype_at_fault = 19 if temp == "19"
replace chp_vehtype_at_fault = 20 if temp == "20"
replace chp_vehtype_at_fault = 21 if temp == "21"
replace chp_vehtype_at_fault = 22 if temp == "22"
replace chp_vehtype_at_fault = 23 if temp == "23"
replace chp_vehtype_at_fault = 24 if temp == "24"
replace chp_vehtype_at_fault = 25 if temp == "25"
replace chp_vehtype_at_fault = 26 if temp == "26"
replace chp_vehtype_at_fault = 27 if temp == "27"
replace chp_vehtype_at_fault = 28 if temp == "28"
replace chp_vehtype_at_fault = 29 if temp == "29"
replace chp_vehtype_at_fault = 30 if temp == "30"
replace chp_vehtype_at_fault = 31 if temp == "31"
replace chp_vehtype_at_fault = 32 if temp == "32"
replace chp_vehtype_at_fault = 33 if temp == "33"
replace chp_vehtype_at_fault = 34 if temp == "34"
replace chp_vehtype_at_fault = 35 if temp == "35"
replace chp_vehtype_at_fault = 36 if temp == "36"
replace chp_vehtype_at_fault = 37 if temp == "37"
replace chp_vehtype_at_fault = 38 if temp == "38"
replace chp_vehtype_at_fault = 39 if temp == "39"
replace chp_vehtype_at_fault = 40 if temp == "40"
replace chp_vehtype_at_fault = 41 if temp == "41"
replace chp_vehtype_at_fault = 42 if temp == "42"
replace chp_vehtype_at_fault = 43 if temp == "43"
replace chp_vehtype_at_fault = 44 if temp == "44"
replace chp_vehtype_at_fault = 45 if temp == "45"
replace chp_vehtype_at_fault = 46 if temp == "46"
replace chp_vehtype_at_fault = 47 if temp == "47"
replace chp_vehtype_at_fault = 48 if temp == "48"
replace chp_vehtype_at_fault = 49 if temp == "49"
replace chp_vehtype_at_fault = 50 if temp == "50"
replace chp_vehtype_at_fault = 51 if temp == "51"
replace chp_vehtype_at_fault = 52 if temp == "52"
replace chp_vehtype_at_fault = 53 if temp == "53"
replace chp_vehtype_at_fault = 54 if temp == "54"
replace chp_vehtype_at_fault = 55 if temp == "55"
replace chp_vehtype_at_fault = 56 if temp == "56"
replace chp_vehtype_at_fault = 57 if temp == "57"
replace chp_vehtype_at_fault = 58 if temp == "58"
replace chp_vehtype_at_fault = 59 if temp == "59"
replace chp_vehtype_at_fault = 60 if temp == "60"
replace chp_vehtype_at_fault = 61 if temp == "61"
replace chp_vehtype_at_fault = 62 if temp == "62"
replace chp_vehtype_at_fault = 63 if temp == "63"
replace chp_vehtype_at_fault = 64 if temp == "64"
replace chp_vehtype_at_fault = 65 if temp == "65"
replace chp_vehtype_at_fault = 66 if temp == "66"
replace chp_vehtype_at_fault = 71 if temp == "71"
replace chp_vehtype_at_fault = 72 if temp == "72"
replace chp_vehtype_at_fault = 73 if temp == "73"
replace chp_vehtype_at_fault = 75 if temp == "75"
replace chp_vehtype_at_fault = 76 if temp == "76"
replace chp_vehtype_at_fault = 77 if temp == "77"
replace chp_vehtype_at_fault = 78 if temp == "78"
replace chp_vehtype_at_fault = 79 if temp == "79"
replace chp_vehtype_at_fault = 81 if temp == "81"
replace chp_vehtype_at_fault = 82 if temp == "82"
replace chp_vehtype_at_fault = 83 if temp == "83"
replace chp_vehtype_at_fault = 85 if temp == "85"
replace chp_vehtype_at_fault = 86 if temp == "86"
replace chp_vehtype_at_fault = 87 if temp == "87"
replace chp_vehtype_at_fault = 88 if temp == "88"
replace chp_vehtype_at_fault = 89 if temp == "89"
replace chp_vehtype_at_fault = 91 if temp == "91"
replace chp_vehtype_at_fault = 93 if temp == "93"
replace chp_vehtype_at_fault = 94 if temp == "94"
replace chp_vehtype_at_fault = 95 if temp == "95"
replace chp_vehtype_at_fault = 96 if temp == "96"
replace chp_vehtype_at_fault = 97 if temp == "97"
replace chp_vehtype_at_fault = 98 if temp == "98"
replace chp_vehtype_at_fault = 99 if temp == "99"
order chp_vehtype_at_fault, before(temp)
drop temp
label define chp_vehtype_at_fault 0 "Not Stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 83 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chp_vehtype_at_fault chp_vehtype_at_fault
label var chp_vehtype_at_fault "CHP Vehicle Type at Fault"
notes chp_vehtype_at_fault : Indicates the CHP Vehicle Type of the party whi is at fault

// Primary ramp variable operations
ren primary_ramp temp
gen byte primary_ramp = 0 if temp == "-"
replace primary_ramp = 1 if temp == "TO"
replace primary_ramp = 2 if temp == "FR"
replace primary_ramp = 3 if temp == "NF"
replace primary_ramp = 4 if temp == "SF"
replace primary_ramp = 5 if temp == "EF"
replace primary_ramp = 6 if temp == "WF"
replace primary_ramp = 7 if temp == "NO"
replace primary_ramp = 8 if temp == "SO"
replace primary_ramp = 9 if temp == "EO"
replace primary_ramp = 10 if temp == "WO"
replace primary_ramp = 11 if temp == "TR"
replace primary_ramp = 12 if temp == "CO"
replace primary_ramp = 13 if temp == "CN"
order primary_ramp, before(temp)
drop temp
label define primary_ramp 0 "Not stated" 1 "To" 2 "From" 3 "North off ramp" 4 "South off ramp" 5 "East off ramp" 6 "West off ramp" 7 "North on ramp" 8 "South on ramp" 9 "East on ramp" 10 "West on ramp" 11 "Transition" 12 "Collector" 13 "Connector"
label values primary_ramp primary_ramp
label var primary_ramp "Primary Ramp"
notes primary_ramp : A description of the ramp, if any, on primary roadway. This value is computed by the key operator from information on the crash report

// Secondary ramp variable operations
ren secondary_ramp temp
gen byte secondary_ramp = 0 if temp == "-"
replace secondary_ramp = 1 if temp == "TO"
replace secondary_ramp = 2 if temp == "FR"
replace secondary_ramp = 3 if temp == "NF"
replace secondary_ramp = 4 if temp == "SF"
replace secondary_ramp = 5 if temp == "EF"
replace secondary_ramp = 6 if temp == "WF"
replace secondary_ramp = 7 if temp == "NO"
replace secondary_ramp = 8 if temp == "SO"
replace secondary_ramp = 9 if temp == "EO"
replace secondary_ramp = 10 if temp == "WO"
replace secondary_ramp = 11 if temp == "TR"
replace secondary_ramp = 12 if temp == "CO"
replace secondary_ramp = 13 if temp == "CN"
order secondary_ramp, before(temp)
drop temp
label define secondary_ramp 0 "Not stated" 1 "To" 2 "From" 3 "North off ramp" 4 "South off ramp" 5 "East off ramp" 6 "West off ramp" 7 "North on ramp" 8 "South on ramp" 9 "East on ramp" 10 "West on ramp" 11 "Transition" 12 "Collector" 13 "Connector"
label values secondary_ramp secondary_ramp
label var secondary_ramp "Secondary Ramp"
notes secondary_ramp : A description of the ramp, if any, on secondary roadway. This value is computed by the key operator from information on the crash report

// City area variable operations
label var city_area_sqmi "City Area (sq. miles)"
notes city_area_sqmi : City Area in Square Miles

// City population density variable operations
label var city_popdens "City Population Density (per sq. mi)"
notes city_popdens : City population density, population per square mile

// City housing density variable operations
label var city_hudens "City Housing Density (per sq. mi)"
notes city_hudens : City housing density, houses per square mile

// City total population variable operations
label var city_popt "City Total Population"
notes city_popt : Total population in the city's area

// City total housing units variable operations
label var city_hut "City Total Housing Units"
notes city_hut : Total housing units in the city's area

// City Asian population variable operations
label var city_popa "City Asian Population"
notes city_popa : Total Asian population in the city's area

// City Black population variable operations
label var city_popb "City Black Population"
notes city_popb : Total Black or African American population in the city's area

// City Hispanic population variable operations
label var city_poph "City Hispanic Population"
notes city_poph : Total Hispanic population in the city's area

// City White population variable operations
label var city_popw "City White Population"
notes city_popw : Total White population in the city's area

// City aggregate number of vehicles variable operations
label var city_vehicles "City Aggregate Number of Vehicles Commutting"
notes city_vehicles : Aggregate number of vehicles used in commuting in the city's area

// City aggregate travel time to work variable operations
label var city_travel_time "City Aggregate Travel Time to Work (min)"
notes city_travel_time : Aggregate travel time to work (in minutes) in the city's area

// Road ID variable operations
label var rid "Road ID"
notes rid : Road ID matching from the road's layer

// Road Name variable operations
label var rname "Road Name"
notes rname : Road name from the OC Tiger/Lines layer

// Road category variable operations
ren rcat temp
gen byte rcat = 1 if temp == "Primary"
replace rcat = 2 if temp == "Secondary"
replace rcat = 3 if temp == "Local"
order rcat, before(temp)
drop temp
label define rcat 1 "Primary" 2 "Secondary" 3 "Local"
label values rcat rcat
label var rcat "Road Category"
notes rcat : Road category from the OC Tiger/Lines layer

// Road length variable operations
label var rlength "Road Length"
notes rlength : Road length from the OC Tiger/Lines layer

// GPS latitude variable operations
label var latitude "GPS Latitude"
notes latitude : Latitude of the crash location in decimal degrees. The decimal point is included. LATITUDE and LONGITUDE are from the crash report

// GPS Longitude variable operations
label var longitude "GPS Longitude"
notes longitude : Longitude of the crash location in decimal degrees. The decimal point is included. There is no minus sign. The longitude is understood to be West of Meridian. LATITUDE and LONGITUDE are from the crash report

// X coordinate location variable operations
label var point_x "X Coordinate Location"
notes point_x : The longitude of the geocoded location, uses the World Geodetic System from 1984 (WGS84). POINT_X and POINT_Y are generated using the geociding process by UC Berkeley Safe TREC

// Y coordinate location variable operations
label var point_y "Y Coordinate Location"
notes point_y : The latitude of the geocoded location, uses the World Geodetic System from 1984 (WGS84). POINT_X and POINT_Y are generated using the geociding process by UC Berkeley Safe TREC


// Save dataset to disk
save "D:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\stCrashes.dta", replace
