
// OCSWITS Collisions Data Processing
// Version 2, Date: 2024-11-26

clear all

// Importing dfCollisions row data
import delimited D:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfCollisions_final.csv, delimiter(comma) bindquote(strict) varnames(1) stripquote(yes)
label data "OCSWITRS Collisions Stata Dataset"

// Case ID variable operations
label var case_id "Case ID"
notes case_id : Unique Identifier of the crash case

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
label var party_number "Party Number"

// Victim Number variable operations
label var victim_number "Victim Number"

// Crashes indicator variable operations
egen byte crashes_indicator = tag(cid)
order crashes_indicator, after(victim_number)
label define crashes_indicator 1 "Crash" 0 ""
label values crashes_indicator crashes_indicator
label var crashes_indicator "Crashes Binary Indicator"
notes crashes_indicator : Binary flag, 1 if the record is a crash, 0 if not

// Parties indicator variable operations
egen byte parties_indicator = tag(pid)
order parties_indicator, after(crashes_indicator)
label define parties_indicator 1 "Party" 0 ""
label values parties_indicator parties_indicator
label var parties_indicator "Parties Binary Indicator"
notes parties_indicator : Binary flag, 1 if the record is a party, 0 if not

// Victims indicator variable operations
egen byte victims_indicator = tag(vid)
order victims_indicator, after(parties_indicator)
label define victims_indicator 1 "Victim" 0 ""
label values victims_indicator victims_indicator
label var victims_indicator "Victims Binary Indicator"
notes victims_indicator : Binary flag, 1 if the record is a victim, 0 if not

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

// Party type variable operations
ren party_type temp
gen byte party_type = 0 if temp == "-"
replace party_type = 1 if temp == "1"
replace party_type = 2 if temp == "2"
replace party_type = 3 if temp == "3"
replace party_type = 4 if temp == "4"
replace party_type = 5 if temp == "5"
replace party_type = 6 if temp == "6"
order party_type, before(temp)
drop temp
label define party_type 0 "Not stated" 1 "Driver (including hit and run)" 2 "Pedestrian" 3 "Parked vehicle" 4 "Bicyclist" 5 "Other" 6 "Operator"
label values party_type party_type
label var party_type "Party Type"
notes party_type : Involved party type

// At fault variable operations
ren at_fault temp
gen byte at_fault = 0 if temp == "N"
replace at_fault = 1 if temp == "Y"
order at_fault, before(temp)
drop temp
label define at_fault 0 "No" 1 "Yes"
label values at_fault at_fault
label var at_fault "At Fault"
notes at_fault : Indicates whether the party was at fault in the crash

// Party sex variable operations
ren party_sex temp
gen byte party_sex = 0 if temp == "-"
replace party_sex = 1 if temp == "M"
replace party_sex = 2 if temp == "F"
replace party_sex = 3 if temp == "X"
order party_sex, before(temp)
drop temp
label define party_sex 0 "Not stated" 1 "Male" 2 "Female" 3 "Nonbinary"
label values party_sex party_sex
label var party_sex "Party Sex"
notes party_sex : The gender of the party

// Party age variable operations
label define party_age 998 "Unknown"
label values party_age party_age
label var party_age "Party Age"
notes party_age : The age of the party at the time of the crash

// Party race variable operations
ren race temp
gen byte race = 1 if temp == "A"
replace race = 2 if temp == "B"
replace race = 3 if temp == "H"
replace race = 4 if temp == "W"
replace race = 5 if temp == "O"
order race, before(temp)
drop temp
label define race 1 "Asian" 2 "Black" 3 "Hispanic" 4 "White" 5 "Other"
label values race race
label var race "Party Race"
notes race : The party's race based on the reporting officer's judgment

// Party number killed variable operations
label var party_number_killed "Party Number Killed"
notes party_number_killed : Number of killed victims in the party

// Party number injured variable operations
label var party_number_injured "Party Number Injured"
notes party_number_injured : Number of injured victims in the party

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
ren party_sobriety temp
gen byte party_sobriety = 0 if temp == "-"
replace party_sobriety = 1 if temp == "A"
replace party_sobriety = 2 if temp == "B"
replace party_sobriety = 3 if temp == "C"
replace party_sobriety = 4 if temp == "D"
replace party_sobriety = 5 if temp == "G"
replace party_sobriety = 6 if temp == "H"
order party_sobriety, before(temp)
drop temp
label define party_sobriety 0 "Not Stated" 1 "Had not been drinking" 2 "Had been drinking under influence" 3 "Had been drinking, not under influence" 4 "Had been drinking, impairment unknown" 5 "Impairment unknown" 6 "Not applicable"
label values party_sobriety party_sobriety
label var party_sobriety "Party Sobriety"
notes party_sobriety : The state of sobriety of the party

// Party drug physical variable operations
ren party_drug_physical temp
gen byte party_drug_physical = 0 if temp == "-"
replace party_drug_physical = 1 if temp == "E"
replace party_drug_physical = 2 if temp == "F"
replace party_drug_physical = 3 if temp == "G"
replace party_drug_physical = 4 if temp == "H"
replace party_drug_physical = 5 if temp == "I"
order party_drug_physical, before(temp)
drop temp
label define party_drug_physical 0 "Not stated" 1 "Under drug influence" 2 "Impairment - physical" 3 "Impairment unknown" 4 "Not applicable" 5 "Sleepy or fatigued"
label values party_drug_physical party_drug_physical
label var party_drug_physical "Party Drug Physical"
notes party_drug_physical : The state of the party with regard to drugs and physical condition

// Direction of travel variable operations
ren dir_of_travel temp
gen byte dir_of_travel = 0 if temp == "-"
replace dir_of_travel = 1 if temp == "N"
replace dir_of_travel = 2 if temp == "S"
replace dir_of_travel = 3 if temp == "E"
replace dir_of_travel = 4 if temp == "W"
order dir_of_travel, before(temp)
drop temp
label define dir_of_travel 0 "Not stated" 1 "North" 2 "South" 3 "East" 4 "West"
label values dir_of_travel dir_of_travel
label var dir_of_travel "Direction of Travel"
notes dir_of_travel : Direction that the party was traveling at the time of the crash. The direction is the direction of the highway, not the compass direction

// Party safety equipment 1  variable operations
ren party_safety_equip_1 temp
gen byte party_safety_equip1 = 0 if temp == "-"
replace party_safety_equip1 = 1 if temp == "A"
replace party_safety_equip1 = 2 if temp == "B"
replace party_safety_equip1 = 3 if temp == "C"
replace party_safety_equip1 = 4 if temp == "D"
replace party_safety_equip1 = 5 if temp == "E"
replace party_safety_equip1 = 6 if temp == "F"
replace party_safety_equip1 = 7 if temp == "G"
replace party_safety_equip1 = 8 if temp == "H"
replace party_safety_equip1 = 9 if temp == "J"
replace party_safety_equip1 = 10 if temp == "K"
replace party_safety_equip1 = 11 if temp == "L"
replace party_safety_equip1 = 12 if temp == "M"
replace party_safety_equip1 = 13 if temp == "N"
replace party_safety_equip1 = 14 if temp == "P"
replace party_safety_equip1 = 15 if temp == "Q"
replace party_safety_equip1 = 16 if temp == "R"
replace party_safety_equip1 = 17 if temp == "S"
replace party_safety_equip1 = 18 if temp == "T"
replace party_safety_equip1 = 19 if temp == "U"
replace party_safety_equip1 = 20 if temp == "V"
replace party_safety_equip1 = 21 if temp == "W"
replace party_safety_equip1 = 22 if temp == "X"
replace party_safety_equip1 = 23 if temp == "Y"
order party_safety_equip1, before(temp)
drop temp
label define party_safety_equip1 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values party_safety_equip1 party_safety_equip1
label var party_safety_equip1 "Party Safety Equipment 1"
notes party_safety_equip1 : The safety equipment of the party


// Party safety equipment 2  variable operations
ren party_safety_equip_2 temp
gen byte party_safety_equip2 = 0 if temp == "-"
replace party_safety_equip2 = 1 if temp == "A"
replace party_safety_equip2 = 2 if temp == "B"
replace party_safety_equip2 = 3 if temp == "C"
replace party_safety_equip2 = 4 if temp == "D"
replace party_safety_equip2 = 5 if temp == "E"
replace party_safety_equip2 = 6 if temp == "F"
replace party_safety_equip2 = 7 if temp == "G"
replace party_safety_equip2 = 8 if temp == "H"
replace party_safety_equip2 = 9 if temp == "J"
replace party_safety_equip2 = 10 if temp == "K"
replace party_safety_equip2 = 11 if temp == "L"
replace party_safety_equip2 = 12 if temp == "M"
replace party_safety_equip2 = 13 if temp == "N"
replace party_safety_equip2 = 14 if temp == "P"
replace party_safety_equip2 = 15 if temp == "Q"
replace party_safety_equip2 = 16 if temp == "R"
replace party_safety_equip2 = 17 if temp == "S"
replace party_safety_equip2 = 18 if temp == "T"
replace party_safety_equip2 = 19 if temp == "U"
replace party_safety_equip2 = 20 if temp == "V"
replace party_safety_equip2 = 21 if temp == "W"
replace party_safety_equip2 = 22 if temp == "X"
replace party_safety_equip2 = 23 if temp == "Y"
order party_safety_equip2, before(temp)
drop temp
label define party_safety_equip2 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values party_safety_equip2 party_safety_equip2
label var party_safety_equip2 "Party Safety Equipment 2"
notes party_safety_equip2 : The safety equipment of the party

// Financial responsibility  variable operations
ren finan_respons temp
gen byte finan_respons = 1 if temp == "N"
replace finan_respons = 2 if temp == "Y"
replace finan_respons = 3 if temp == "O"
replace finan_respons = 4 if temp == "E"
order finan_respons, before(temp)
drop temp
label define finan_respons 1 "No proof of insurance obtained" 2 "Yes, proof of insurance obtained" 3 "Not applicable (used for parked cars, bicyclists, pedestrians, and party type others)" 4 "Used if the officer is called away from the scene of the crash prior to obtaining the insurance information"
label values finan_respons finan_respons
label var finan_respons "Financial Responsibility"
notes finan_respons : Financial responsibility of the party

// Special information 1 variable operations
ren sp_info_1 temp
gen byte sp_info1 = 0 if temp == "-"
replace sp_info1 = 1 if temp == "A"
order sp_info1, before(temp)
drop temp
label define sp_info1 0 "Not stated" 1 "Hazardous material"
label values sp_info1 sp_info1
label var sp_info1 "Special Information 1"
notes sp_info1 : Value A indicates that the crash involved in a vehicle known to be, or believed to be, transporting a hazardous material as defined in CVC Section 353, whether or not the crash involved a hazardous material incident

// Special information 2 variable operations
ren sp_info_2 temp
gen byte sp_info2 = 0 if temp == "-"
replace sp_info2 = 1 if temp == "1"
replace sp_info2 = 2 if temp == "2"
replace sp_info2 = 3 if temp == "3"
replace sp_info2 = 4 if temp == "4"
replace sp_info2 = 5 if temp == "B"
replace sp_info2 = 6 if temp == "C"
replace sp_info2 = 7 if temp == "D"
order sp_info2, before(temp)
drop temp
label define sp_info2 0 "Not stated" 1 "Cell phone handheld in use" 2 "Cell phone hands-free in use" 3 "Cell phone not in use" 4 "Cell phone use unknown" 5 "Cell phone in use" 6 "Cell phone not in use" 7 "No cell phone/unknown"
label values sp_info2 sp_info2
label var sp_info2 "Special Information 2"
notes sp_info2 : Cell Phone Information

// Special information 3 variable operations
ren sp_info_3 temp
gen byte sp_info3 = 0 if temp == "-"
replace sp_info3 = 1 if temp == "E"
order sp_info3, before(temp)
drop temp
label define sp_info3 0 "Not stated" 1 "School bus related"
label values sp_info3 sp_info3
label var sp_info3 "Special Information 3"
notes sp_info3 : Value E indicates that the crash involved a motor vehicle in-transport passing a stopped school bus with its red signal lamps in operation pursuant to CVC Section 22112, or reacting to, pursuant to CVC Section 22454

// OAF violation code variable operations
ren oaf_violation_code temp
gen byte oaf_violation_code = 0 if temp == "-"
replace oaf_violation_code = 1 if temp == "B"
replace oaf_violation_code = 2 if temp == "C"
replace oaf_violation_code = 3 if temp == "H"
replace oaf_violation_code = 4 if temp == "I"
replace oaf_violation_code = 5 if temp == "P"
replace oaf_violation_code = 6 if temp == "S"
replace oaf_violation_code = 7 if temp == "W"
order oaf_violation_code, before(temp)
drop temp
label define oaf_violation_code 0 "Not stated" 1 "Business and professions" 2 "Vehicle" 3 "City health and safety" 4 "City ordinance" 5 "Penal" 6 "Streets and highways" 7 "Welfare and institutions"
label values oaf_violation_code oaf_violation_code
label var oaf_violation_code "OAF Violation Code"
notes oaf_violation_code : Other associated factor law code violated

// OAF violation category variable operations
ren oaf_viol_cat temp
gen byte oaf_viol_cat = 0 if temp == "0"
replace oaf_viol_cat = 1 if temp == "1"
replace oaf_viol_cat = 2 if temp == "2"
replace oaf_viol_cat = 3 if temp == "3"
replace oaf_viol_cat = 5 if temp == "5"
replace oaf_viol_cat = 6 if temp == "6"
replace oaf_viol_cat = 8 if temp == "8"
replace oaf_viol_cat = 9 if temp == "9"
replace oaf_viol_cat = 10 if temp == "10"
replace oaf_viol_cat = 11 if temp == "11"
replace oaf_viol_cat = 13 if temp == "13"
replace oaf_viol_cat = 15 if temp == "15"
replace oaf_viol_cat = 16 if temp == "16"
replace oaf_viol_cat = 17 if temp == "17"
replace oaf_viol_cat = 18 if temp == "18"
replace oaf_viol_cat = 19 if temp == "19"
replace oaf_viol_cat = 20 if temp == "20"
replace oaf_viol_cat = 21 if temp == "21"
replace oaf_viol_cat = 22 if temp == "22"
replace oaf_viol_cat = 23 if temp == "23"
replace oaf_viol_cat = 24 if temp == "24"
replace oaf_viol_cat = 25 if temp == "25"
replace oaf_viol_cat = 26 if temp == "26"
replace oaf_viol_cat = 27 if temp == "27"
replace oaf_viol_cat = 28 if temp == "28"
replace oaf_viol_cat = 29 if temp == "29"
replace oaf_viol_cat = 30 if temp == "30"
replace oaf_viol_cat = 31 if temp == "31"
replace oaf_viol_cat = 33 if temp == "33"
replace oaf_viol_cat = 34 if temp == "34"
replace oaf_viol_cat = 35 if temp == "35"
replace oaf_viol_cat = 38 if temp == "38"
replace oaf_viol_cat = 39 if temp == "39"
replace oaf_viol_cat = 40 if temp == "40"
replace oaf_viol_cat = 43 if temp == "43"
replace oaf_viol_cat = 44 if temp == "44"
replace oaf_viol_cat = 46 if temp == "46"
replace oaf_viol_cat = 47 if temp == "47"
replace oaf_viol_cat = 48 if temp == "48"
replace oaf_viol_cat = 49 if temp == "49"
replace oaf_viol_cat = 50 if temp == "50"
replace oaf_viol_cat = 51 if temp == "51"
replace oaf_viol_cat = 52 if temp == "52"
replace oaf_viol_cat = 53 if temp == "53"
replace oaf_viol_cat = 60 if temp == "60"
replace oaf_viol_cat = 61 if temp == "61"
replace oaf_viol_cat = 62 if temp == "62"
replace oaf_viol_cat = 63 if temp == "63"
replace oaf_viol_cat = 99 if temp == "-"
order oaf_viol_cat, before(temp)
drop temp
label define oaf_viol_cat 0 "Not stated" 1 "Under influence in public" 2 "County ordinance" 3 "City ordinance" 5 "Business/professions code" 6 "Felony penal code" 8 "Controlled substances (felony health and safety)" 9 "Health/safety code (misdemeanor)" 10 "Penal code (misdemeanor)" 11 "Streets/highways code" 13 "Welfare/institutions code" 15 "Manslaughter" 16 "Non-vehicle code not specified above" 17 "Fish and game code" 18 "Agriculture code" 19 "Hit and run" 20 "Driving or bicycling under the influence of alcohol or drug" 21 "Improper lane change" 22 "Impeding traffic" 23 "Failure to heed stop signal" 24 "Failure to heed stop sign" 25 "Unsafe speed" 26 "Reckless driving" 27 "Wrong side of road" 28 "Unsafe lane change" 29 "Improper passing" 30 "Following too closely" 31 "Improper turning" 33 "Automobile right-of-way" 34 "Pedestrian right-of-way" 35 "Pedestrian violation" 38 "Hazardous parking" 39 "Lights" 40 "Brakes" 43 "Other equipment" 44 "Other hazardous movement" 46 "Improper registration" 47 "Other non-moving violation" 48 "Excessive smoke" 49 "Excessive noise" 50 "Overweight" 51 "Oversize" 52 "Over maximum speed" 53 "Unsafe starting or backing" 60 "Off-highway vehicle violation" 61 "Child restraint" 62 "Seat belt" 63 "Seat belt (equipment)" 99 "Not Stated"
label values oaf_viol_cat oaf_viol_cat
label var oaf_viol_cat "OAF Violation Category"
notes oaf_viol_cat : Category of the factor that contributed to the crash but was not the primary cause of the crash

// OAF violation section variable operations
label var oaf_viol_section "OAF Violation Section"
notes oaf_viol_section : The CVC section of the secondary violation that contributed to the crash

// OAF violation suffix variable operations
label var oaf_violation_suffix "OAF Violation Suffix"
notes oaf_violation_suffix : the subsection of the CVC section of the secondary violation that contributed to the crash

// Other associated factor 1 variable operations
ren oaf_1 temp
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
ren oaf_2 temp
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
ren move_pre_acc temp
gen byte move_pre_acc = 0 if temp == "-"
replace move_pre_acc = 1 if temp == "A"
replace move_pre_acc = 2 if temp == "B"
replace move_pre_acc = 3 if temp == "C"
replace move_pre_acc = 4 if temp == "D"
replace move_pre_acc = 5 if temp == "E"
replace move_pre_acc = 6 if temp == "F"
replace move_pre_acc = 7 if temp == "G"
replace move_pre_acc = 8 if temp == "H"
replace move_pre_acc = 9 if temp == "I"
replace move_pre_acc = 10 if temp == "J"
replace move_pre_acc = 11 if temp == "K"
replace move_pre_acc = 12 if temp == "L"
replace move_pre_acc = 13 if temp == "M"
replace move_pre_acc = 14 if temp == "N"
replace move_pre_acc = 15 if temp == "O"
replace move_pre_acc = 16 if temp == "P"
replace move_pre_acc = 17 if temp == "Q"
replace move_pre_acc = 18 if temp == "R"
replace move_pre_acc = 19 if temp == "S"
order move_pre_acc, before(temp)
drop temp
label define move_pre_acc 0 "Not stated" 1 "Stopped" 2 "Proceeding straight" 3 "Ran off road" 4 "Making right turn" 5 "Making left turn" 6 "Making U-turn" 7 "Backing" 8 "Slowing/stopping" 9 "Passing other vehicle" 10 "Changing lanes" 11 "Parking maneuver" 12 "entering traffic" 13 "Other unsafe turning" 14 "Crossed into opposing lane" 15 "Parked" 16 "Merging" 17 "Traveling wrong way" 18 "Other" 19 "Lane splitting"
label values move_pre_acc move_pre_acc
label var move_pre_acc "Movement Preceding Crash"
notes move_pre_acc : The action of the vehicle prior to the crash and before evasive action. This movement does not have to correspond with the PCF

// Vehicle year variable operations
// Corrections
replace vehicle_year = 2001 if vehicle_year == 2101
replace vehicle_year = 2002 if vehicle_year == 2102
replace vehicle_year = 2008 if vehicle_year == 2108
replace vehicle_year = 2003 if vehicle_year == 2203
replace vehicle_year = 2016 if vehicle_year == 2916
replace vehicle_year = 2003 if vehicle_year == 2203
replace vehicle_year = 2017 if vehicle_year == 2047
replace vehicle_year = 2001 if vehicle_year == 1201
label var vehicle_year "Vehicle Year"
notes vehicle_year : The model year of the party's vehicle

// Vehicle make variable operations
label var vehicle_make "Vehicle Make"
notes vehicle_make : The make of the party's vehicle

// Statewide vehicle type variable operations
ren stwd_vehicle_type temp
gen byte stwd_vehicle_type = 0 if temp == "-"
replace stwd_vehicle_type = 1 if temp == "A"
replace stwd_vehicle_type = 2 if temp == "B"
replace stwd_vehicle_type = 3 if temp == "C"
replace stwd_vehicle_type = 4 if temp == "D"
replace stwd_vehicle_type = 5 if temp == "E"
replace stwd_vehicle_type = 6 if temp == "F"
replace stwd_vehicle_type = 7 if temp == "G"
replace stwd_vehicle_type = 8 if temp == "H"
replace stwd_vehicle_type = 9 if temp == "I"
replace stwd_vehicle_type = 10 if temp == "J"
replace stwd_vehicle_type = 11 if temp == "K"
replace stwd_vehicle_type = 12 if temp == "L"
replace stwd_vehicle_type = 13 if temp == "M"
replace stwd_vehicle_type = 14 if temp == "N"
replace stwd_vehicle_type = 15 if temp == "O"
order stwd_vehicle_type, before(temp)
drop temp
label define stwd_vehicle_type 0 "Not stated" 1 "Passenger car/station wagon" 2 "Passenger car with trailer" 3 "Motorcycle/scooter" 4 "Pickup or panel truck" 5 "Pickup or panel truck with trailer" 6 "Truck or truck tractor" 7 "Truck or truck tractor with trailer" 8 "School bus" 9 "Other bus" 10 "Emergency vehicle" 11 "Highway construction equipment" 12 "Bicycle" 13 "Other vehicle" 14 "Pedestrian" 15 "Moped"
label values stwd_vehicle_type stwd_vehicle_type
label var stwd_vehicle_type "Statewide Vehicle Type"
notes stwd_vehicle_type : Type of the party's vehicle according to a list called statewide vehicle type

// CHP vehicle type towing variable operations
ren chp_veh_type_towing temp
gen byte chp_veh_type_towing = 0 if temp == "-"
replace chp_veh_type_towing = 1 if temp == "1"
replace chp_veh_type_towing = 2 if temp == "2"
replace chp_veh_type_towing = 3 if temp == "3"
replace chp_veh_type_towing = 4 if temp == "4"
replace chp_veh_type_towing = 5 if temp == "5"
replace chp_veh_type_towing = 6 if temp == "6"
replace chp_veh_type_towing = 7 if temp == "7"
replace chp_veh_type_towing = 8 if temp == "8"
replace chp_veh_type_towing = 9 if temp == "9"
replace chp_veh_type_towing = 10 if temp == "10"
replace chp_veh_type_towing = 11 if temp == "11"
replace chp_veh_type_towing = 12 if temp == "12"
replace chp_veh_type_towing = 13 if temp == "13"
replace chp_veh_type_towing = 14 if temp == "14"
replace chp_veh_type_towing = 15 if temp == "15"
replace chp_veh_type_towing = 16 if temp == "16"
replace chp_veh_type_towing = 17 if temp == "17"
replace chp_veh_type_towing = 18 if temp == "18"
replace chp_veh_type_towing = 19 if temp == "19"
replace chp_veh_type_towing = 20 if temp == "20"
replace chp_veh_type_towing = 21 if temp == "21"
replace chp_veh_type_towing = 22 if temp == "22"
replace chp_veh_type_towing = 23 if temp == "23"
replace chp_veh_type_towing = 24 if temp == "24"
replace chp_veh_type_towing = 25 if temp == "25"
replace chp_veh_type_towing = 26 if temp == "26"
replace chp_veh_type_towing = 27 if temp == "27"
replace chp_veh_type_towing = 28 if temp == "28"
replace chp_veh_type_towing = 29 if temp == "29"
replace chp_veh_type_towing = 30 if temp == "30"
replace chp_veh_type_towing = 31 if temp == "31"
replace chp_veh_type_towing = 32 if temp == "32"
replace chp_veh_type_towing = 33 if temp == "33"
replace chp_veh_type_towing = 34 if temp == "34"
replace chp_veh_type_towing = 35 if temp == "35"
replace chp_veh_type_towing = 36 if temp == "36"
replace chp_veh_type_towing = 37 if temp == "37"
replace chp_veh_type_towing = 38 if temp == "38"
replace chp_veh_type_towing = 39 if temp == "39"
replace chp_veh_type_towing = 40 if temp == "40"
replace chp_veh_type_towing = 41 if temp == "41"
replace chp_veh_type_towing = 42 if temp == "42"
replace chp_veh_type_towing = 43 if temp == "43"
replace chp_veh_type_towing = 44 if temp == "44"
replace chp_veh_type_towing = 45 if temp == "45"
replace chp_veh_type_towing = 46 if temp == "46"
replace chp_veh_type_towing = 47 if temp == "47"
replace chp_veh_type_towing = 48 if temp == "48"
replace chp_veh_type_towing = 49 if temp == "49"
replace chp_veh_type_towing = 50 if temp == "50"
replace chp_veh_type_towing = 51 if temp == "51"
replace chp_veh_type_towing = 52 if temp == "52"
replace chp_veh_type_towing = 53 if temp == "53"
replace chp_veh_type_towing = 54 if temp == "54"
replace chp_veh_type_towing = 55 if temp == "55"
replace chp_veh_type_towing = 56 if temp == "56"
replace chp_veh_type_towing = 57 if temp == "57"
replace chp_veh_type_towing = 58 if temp == "58"
replace chp_veh_type_towing = 59 if temp == "59"
replace chp_veh_type_towing = 60 if temp == "60"
replace chp_veh_type_towing = 61 if temp == "61"
replace chp_veh_type_towing = 62 if temp == "62"
replace chp_veh_type_towing = 63 if temp == "63"
replace chp_veh_type_towing = 64 if temp == "64"
replace chp_veh_type_towing = 65 if temp == "65"
replace chp_veh_type_towing = 66 if temp == "66"
replace chp_veh_type_towing = 71 if temp == "71"
replace chp_veh_type_towing = 72 if temp == "72"
replace chp_veh_type_towing = 73 if temp == "73"
replace chp_veh_type_towing = 75 if temp == "75"
replace chp_veh_type_towing = 76 if temp == "76"
replace chp_veh_type_towing = 77 if temp == "77"
replace chp_veh_type_towing = 78 if temp == "78"
replace chp_veh_type_towing = 79 if temp == "79"
replace chp_veh_type_towing = 81 if temp == "81"
replace chp_veh_type_towing = 82 if temp == "82"
replace chp_veh_type_towing = 83 if temp == "83"
replace chp_veh_type_towing = 85 if temp == "85"
replace chp_veh_type_towing = 86 if temp == "86"
replace chp_veh_type_towing = 87 if temp == "87"
replace chp_veh_type_towing = 88 if temp == "88"
replace chp_veh_type_towing = 89 if temp == "89"
replace chp_veh_type_towing = 91 if temp == "91"
replace chp_veh_type_towing = 93 if temp == "93"
replace chp_veh_type_towing = 94 if temp == "94"
replace chp_veh_type_towing = 95 if temp == "95"
replace chp_veh_type_towing = 96 if temp == "96"
replace chp_veh_type_towing = 97 if temp == "97"
replace chp_veh_type_towing = 98 if temp == "98"
replace chp_veh_type_towing = 99 if temp == "99"
order chp_veh_type_towing, before(temp)
drop temp
label define chp_veh_type_towing 0 "Not stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 3 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chp_veh_type_towing chp_veh_type_towing
label var chp_veh_type_towing "CHP Vehicle Type Towing"
notes chp_veh_type_towing : The type of the solitary vehicle or the tractor unit according to the CHP manual HPM 110.5 Chapter 3 Annex F vehicle type codes


// CHP vehicle type towed variable operations
ren chp_veh_type_towed temp
gen byte chp_veh_type_towed = 0 if temp == "-"
replace chp_veh_type_towed = 1 if temp == "1"
replace chp_veh_type_towed = 2 if temp == "2"
replace chp_veh_type_towed = 3 if temp == "3"
replace chp_veh_type_towed = 4 if temp == "4"
replace chp_veh_type_towed = 5 if temp == "5"
replace chp_veh_type_towed = 6 if temp == "6"
replace chp_veh_type_towed = 7 if temp == "7"
replace chp_veh_type_towed = 8 if temp == "8"
replace chp_veh_type_towed = 9 if temp == "9"
replace chp_veh_type_towed = 10 if temp == "10"
replace chp_veh_type_towed = 11 if temp == "11"
replace chp_veh_type_towed = 12 if temp == "12"
replace chp_veh_type_towed = 13 if temp == "13"
replace chp_veh_type_towed = 14 if temp == "14"
replace chp_veh_type_towed = 15 if temp == "15"
replace chp_veh_type_towed = 16 if temp == "16"
replace chp_veh_type_towed = 17 if temp == "17"
replace chp_veh_type_towed = 18 if temp == "18"
replace chp_veh_type_towed = 19 if temp == "19"
replace chp_veh_type_towed = 20 if temp == "20"
replace chp_veh_type_towed = 21 if temp == "21"
replace chp_veh_type_towed = 22 if temp == "22"
replace chp_veh_type_towed = 23 if temp == "23"
replace chp_veh_type_towed = 24 if temp == "24"
replace chp_veh_type_towed = 25 if temp == "25"
replace chp_veh_type_towed = 26 if temp == "26"
replace chp_veh_type_towed = 27 if temp == "27"
replace chp_veh_type_towed = 28 if temp == "28"
replace chp_veh_type_towed = 29 if temp == "29"
replace chp_veh_type_towed = 30 if temp == "30"
replace chp_veh_type_towed = 31 if temp == "31"
replace chp_veh_type_towed = 32 if temp == "32"
replace chp_veh_type_towed = 33 if temp == "33"
replace chp_veh_type_towed = 34 if temp == "34"
replace chp_veh_type_towed = 35 if temp == "35"
replace chp_veh_type_towed = 36 if temp == "36"
replace chp_veh_type_towed = 37 if temp == "37"
replace chp_veh_type_towed = 38 if temp == "38"
replace chp_veh_type_towed = 39 if temp == "39"
replace chp_veh_type_towed = 40 if temp == "40"
replace chp_veh_type_towed = 41 if temp == "41"
replace chp_veh_type_towed = 42 if temp == "42"
replace chp_veh_type_towed = 43 if temp == "43"
replace chp_veh_type_towed = 44 if temp == "44"
replace chp_veh_type_towed = 45 if temp == "45"
replace chp_veh_type_towed = 46 if temp == "46"
replace chp_veh_type_towed = 47 if temp == "47"
replace chp_veh_type_towed = 48 if temp == "48"
replace chp_veh_type_towed = 49 if temp == "49"
replace chp_veh_type_towed = 50 if temp == "50"
replace chp_veh_type_towed = 51 if temp == "51"
replace chp_veh_type_towed = 52 if temp == "52"
replace chp_veh_type_towed = 53 if temp == "53"
replace chp_veh_type_towed = 54 if temp == "54"
replace chp_veh_type_towed = 55 if temp == "55"
replace chp_veh_type_towed = 56 if temp == "56"
replace chp_veh_type_towed = 57 if temp == "57"
replace chp_veh_type_towed = 58 if temp == "58"
replace chp_veh_type_towed = 59 if temp == "59"
replace chp_veh_type_towed = 60 if temp == "60"
replace chp_veh_type_towed = 61 if temp == "61"
replace chp_veh_type_towed = 62 if temp == "62"
replace chp_veh_type_towed = 63 if temp == "63"
replace chp_veh_type_towed = 64 if temp == "64"
replace chp_veh_type_towed = 65 if temp == "65"
replace chp_veh_type_towed = 66 if temp == "66"
replace chp_veh_type_towed = 71 if temp == "71"
replace chp_veh_type_towed = 72 if temp == "72"
replace chp_veh_type_towed = 73 if temp == "73"
replace chp_veh_type_towed = 75 if temp == "75"
replace chp_veh_type_towed = 76 if temp == "76"
replace chp_veh_type_towed = 77 if temp == "77"
replace chp_veh_type_towed = 78 if temp == "78"
replace chp_veh_type_towed = 79 if temp == "79"
replace chp_veh_type_towed = 81 if temp == "81"
replace chp_veh_type_towed = 82 if temp == "82"
replace chp_veh_type_towed = 83 if temp == "83"
replace chp_veh_type_towed = 85 if temp == "85"
replace chp_veh_type_towed = 86 if temp == "86"
replace chp_veh_type_towed = 87 if temp == "87"
replace chp_veh_type_towed = 88 if temp == "88"
replace chp_veh_type_towed = 89 if temp == "89"
replace chp_veh_type_towed = 91 if temp == "91"
replace chp_veh_type_towed = 93 if temp == "93"
replace chp_veh_type_towed = 94 if temp == "94"
replace chp_veh_type_towed = 95 if temp == "95"
replace chp_veh_type_towed = 96 if temp == "96"
replace chp_veh_type_towed = 97 if temp == "97"
replace chp_veh_type_towed = 98 if temp == "98"
replace chp_veh_type_towed = 99 if temp == "99"
order chp_veh_type_towed, before(temp)
drop temp
label define chp_veh_type_towed 0 "Not stated" 1 "Passenger car station Wagon or Jeep" 2 "Motorcycle" 3 "Motor-driven cycle (<15 hp)" 4 "Bicycle" 5 "Motorized vehicle" 6 "All-terrain vehicle (ATV)" 7 "Sport utility vehicle" 8 "Minivan" 9 "Paratransit bus" 10 "Tour bus" 11 "Other commercial bus" 12 "Non-commercial bus" 13 "Schoolbus public I" 14 "Schoolbus public II" 15 "Schoolbus private I" 16 "Schoolbus private II" 17 "Schoolbus contractual I" 18 "Schoolbus contractual II" 19 "General public paratransit vehicle" 20 "Public transit authority" 21 "Two-axle tank truck" 22 "Pickup or panel truck" 23 "Pickup truck with camper" 24 "Three-axle tank truck" 25 "Truck tractor" 26 "Two-axle truck" 27 "Three-axle truck" 28 "Semi-tank trailer" 29 "Pull-tank trailer" 30 "Two-tank trailer" 31 "Semi-trailer" 32 "Pull trailer (includes dolly)" 33 "Two trailers (includes semi and trailer)" 34 "Boat trailer" 35 "Utility trailer" 36 "Trailer coach" 37 "Oversize vehicle/load" 38 "Pole pipe or logging dolly" 39 "Three trailers (includes semi and two trailers)" 40 "Semi 48 or less with king pin to trailer axle of over 38" 41 "Ambulance" 42 "Dune buggy" 43 "Fire truck (not rescue)" 44 "Forklift" 45 "Highway construction equipment (only while not in construction area)" 46 "Implement of husbandry" 47 "Motor home (40 ft or less)" 48 "CHP police or sheriff car (emergency service or not)" 49 "CHP police or sheriff motorcycle (emergency service or not)" 50 "Mobile equipment" 51 "Farm labor vehicle (certified)" 52 "Federally legal double cargo combo over 75ft" 53 "5th wheel trailer" 54 "Container chassis" 55 "Two-axle tow truck" 56 "Three-axle tow truck" 57 "Farm labor vehicle (non-certified)" 58 "Farm labor transporter" 59 "Motorhome (over 40ft)" 60 "Pedestrian (includes motorized wheelchair)" 61 "School pupil activity bus I (prior to 2002)" 62 "School pupil activity bus II (prior to 2002)" 63 "Youth bus" 64 "School pupil activity bus I (eff 2002)" 65 "School pupil activity bus II (eff 2002)" 66 "School bus Without pupil passengers (eff 2002)" 71 "Passenger car - hazardous materials only" 72 "Pickups and panels - hazardous materials only" 73 "Pickups and campers - hazardous materials only" 75 "Truck tractor - hazardous materials only" 76 "Two-axle truck - hazardous materials only" 77 "Three or more axle truck - hazardous materials only" 78 "Two-axle tank truck - hazardous materials only" 79 "Three axle tank truck - hazardous materials only" 81 "Passenger car - hazardous waste or waste-material combo" 82 "Pickups and panels - hazardous waste or waste-material combo" 83 "Pickups and campers - hazardous waste or waste-material combo" 85 "Truck tractor - hazardous waste or waste-material combo" 86 "Two-axle truck - hazardous waste or waste-material combo" 87 "Three or more axle truck - hazardous waste or waste-material combo" 88 "Two-axle tank truck - hazardous waste or waste-material combo" 89 "Three-axle tank truck - hazardous waste or waste-material combo" 91 "Electric bicycle (class 123)" 93 "Electrically motorized board" 94 "Motorized transportation device" 95 "Miscellaneous non-motorized vehicle (ridden animal animal-drawn conveyance train or building) with victim" 96 "Miscellaneous motorized vehicle (golf cart)" 97 "Low speed vehicle" 98 "Emergency vehicle on an emergency run" 99 "Not stated or unknown (hit and run)"
label values chp_veh_type_towed chp_veh_type_towed
label var chp_veh_type_towed "CHP Vehicle Type Towed"
notes chp_veh_type_towed : The type of the first trailer unit according to the CHP manual HPM 110.5 Chapter 3 Annex F vehicle type codes

// Special info F variable operations
ren special_info_f temp
gen byte special_info_f = 0 if temp == "-"
replace special_info_f = 1 if temp == "F"
order special_info_f, before(temp)
drop temp
label define special_info_f 0 "Not stated" 1 "75ft motor truck combo"
label values special_info_f special_info_f
label var special_info_f "Special Info F"
notes special_info_f : The value F indicate that the party's vehicle is a 75ft motor truck combo

// Special info G variable operations
ren special_info_g temp
gen byte special_info_g = 0 if temp == "-"
replace special_info_g = 1 if temp == "G"
order special_info_g, before(temp)
drop temp
label define special_info_g 0 "Not stated" 1 "32ft trailer combo"
label values special_info_g special_info_g
label var special_info_g "Special Info G"
notes special_info_g : The value G indicates that the party's vehicle is a 32ft trailer combo

// Victim role variable operations
label define victim_role 1 "Driver" 2 "Passenger" 3 "Pedestrian" 4 "Bicyclist" 5 "Other (single victim on/in non-motor vehicle)" 6 "Non-injured party"
label values victim_role victim_role
label var victim_role "Victim Role"
notes victim_role : The role of the victim (passenger (includes non-operator on bicycle or any victim on/in parked vehicle or multiple victims on/in non-motor vehicle)

// Victim sex variable operations
ren victim_sex temp
gen byte victim_sex = 0 if temp == "-"
replace victim_sex = 1 if temp == "M"
replace victim_sex = 2 if temp == "F"
replace victim_sex = 3 if temp == "X"
order victim_sex, before(temp)
drop temp
label define victim_sex 0 "Not stated" 1 "Male" 2 "Female" 3 "Nonbinary"
label values victim_sex victim_sex
label var victim_sex "Victim Sex"
notes victim_sex : The gender of the victim

// Victim age variable operations
label define victim_age 998 "Not stated" 999 "Fatal fetus"
label values victim_age victim_age
label var victim_age "Victim Age"
notes victim_age : The age of the victim at the time of the crash

// Victim degree of injury variable operations
label define victim_degree_of_injury 0 "No injury" 1 "Killed" 2 "Severe injury" 3 "Other visible injury" 4 "Complaint of pain" 5 "Suspected serious injury" 6 "Suspected minor injury" 7 "Possible injury"
label values victim_degree_of_injury victim_degree_of_injury
label var victim_degree_of_injury "Victim Degree of Injury"
notes victim_degree_of_injury : The severity of the injury to the victim

// Victim degree of injury (binary) variable operations
label define victim_degree_of_injury_binary 0 "Minor (minor injury, pain, or no injury)" 1 "Severe (killed or serious injury)"
label values victim_degree_of_injury_binary victim_degree_of_injury_binary
label var victim_degree_of_injury_binary "Victim Degree of Injury (binary)"
notes victim_degree_of_injury_binary : Binary classification of the severity of the injury to the victim

// Victim seating position variable operations
ren victim_seating_position temp
gen byte victim_seating_position = 0 if temp == "0"
replace victim_seating_position = 1 if temp == "1"
replace victim_seating_position = 2 if temp == "2"
replace victim_seating_position = 3 if temp == "3"
replace victim_seating_position = 4 if temp == "4"
replace victim_seating_position = 5 if temp == "5"
replace victim_seating_position = 6 if temp == "6"
replace victim_seating_position = 7 if temp == "7"
replace victim_seating_position = 8 if temp == "8"
replace victim_seating_position = 9 if temp == "9"
replace victim_seating_position = 10 if temp == "-"
order victim_seating_position, before(temp)
drop(temp)
label define victim_seating_position 0 "Other occupants" 1 "Driver" 2 "Passenger 1" 3 "Passenger 2" 4 "Passenger 3" 5 "Passenger 4" 6 "Passenger 5" 7 "Station  wagon rear" 8 "Rear occupant of truck or van" 9 "Position unknown" 10 "Not stated"
label values victim_seating_position victim_seating_position
label var victim_seating_position "Victim Seating Position"
notes victim_seating_position : The seating position of the victim

// Victim safety equipment 1 variable operations
ren victim_safety_equip_1 temp
gen byte victim_safety_equip1 = 0 if temp == "-"
replace victim_safety_equip1 = 1 if temp == "A"
replace victim_safety_equip1 = 2 if temp == "B"
replace victim_safety_equip1 = 3 if temp == "C"
replace victim_safety_equip1 = 4 if temp == "D"
replace victim_safety_equip1 = 5 if temp == "E"
replace victim_safety_equip1 = 6 if temp == "F"
replace victim_safety_equip1 = 7 if temp == "G"
replace victim_safety_equip1 = 8 if temp == "H"
replace victim_safety_equip1 = 9 if temp == "J"
replace victim_safety_equip1 = 10 if temp == "K"
replace victim_safety_equip1 = 11 if temp == "L"
replace victim_safety_equip1 = 12 if temp == "M"
replace victim_safety_equip1 = 13 if temp == "N"
replace victim_safety_equip1 = 14 if temp == "P"
replace victim_safety_equip1 = 15 if temp == "Q"
replace victim_safety_equip1 = 16 if temp == "R"
replace victim_safety_equip1 = 17 if temp == "S"
replace victim_safety_equip1 = 18 if temp == "T"
replace victim_safety_equip1 = 19 if temp == "U"
replace victim_safety_equip1 = 20 if temp == "V"
replace victim_safety_equip1 = 21 if temp == "W"
replace victim_safety_equip1 = 22 if temp == "X"
replace victim_safety_equip1 = 23 if temp == "Y"
order victim_safety_equip1, before(temp)
drop temp
label define victim_safety_equip1 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values victim_safety_equip1 victim_safety_equip1
label var victim_safety_equip1 "Victim Safety Equipment 1"
notes victim_safety_equip1 : The safety equipment of the victim

// Victim safety equipment 2 variable operations
ren victim_safety_equip_2 temp
gen byte victim_safety_equip2 = 0 if temp == "-"
replace victim_safety_equip2 = 1 if temp == "A"
replace victim_safety_equip2 = 2 if temp == "B"
replace victim_safety_equip2 = 3 if temp == "C"
replace victim_safety_equip2 = 4 if temp == "D"
replace victim_safety_equip2 = 5 if temp == "E"
replace victim_safety_equip2 = 6 if temp == "F"
replace victim_safety_equip2 = 7 if temp == "G"
replace victim_safety_equip2 = 8 if temp == "H"
replace victim_safety_equip2 = 9 if temp == "J"
replace victim_safety_equip2 = 10 if temp == "K"
replace victim_safety_equip2 = 11 if temp == "L"
replace victim_safety_equip2 = 12 if temp == "M"
replace victim_safety_equip2 = 13 if temp == "N"
replace victim_safety_equip2 = 14 if temp == "P"
replace victim_safety_equip2 = 15 if temp == "Q"
replace victim_safety_equip2 = 16 if temp == "R"
replace victim_safety_equip2 = 17 if temp == "S"
replace victim_safety_equip2 = 18 if temp == "T"
replace victim_safety_equip2 = 19 if temp == "U"
replace victim_safety_equip2 = 20 if temp == "V"
replace victim_safety_equip2 = 21 if temp == "W"
replace victim_safety_equip2 = 22 if temp == "X"
replace victim_safety_equip2 = 23 if temp == "Y"
order victim_safety_equip2, before(temp)
drop temp
label define victim_safety_equip2 0 "Not stated" 1 "None in vehicle" 2 "Unknown" 3 "Lap belt used" 4 "Lap belt not used" 5 "Shoulder harness used" 6 "Shoulder harness not used" 7 "Lap/shoulder harness used" 8 "Lap/shoulder harness not used" 9 "Passive restraint used" 10 "Passive restraint not used" 11 "Air bag deployed" 12 "Air bag not deployed" 13 "Other" 14 "Not required" 15 "Child restraint in vehicle used" 16 "Child restraint in vehicle not used" 17 "Child restraint in vehicle, use unknown" 18 "Child restraint in vehicle, improper use" 19 "No child restraint in vehicle" 20 "Driver, motorcycle helmet not used" 21 "Driver, motorcycle helmet used" 22 "Passenger, motorcycle helmet not used" 23 "Passenger, motorcycle helmet used"
label values victim_safety_equip2 victim_safety_equip2
label var victim_safety_equip2 "Victim Safety Equipment 2"
notes victim_safety_equip2 : The safety equipment of the victim

// Victim ejected variable operations
ren victim_ejected temp
gen byte victim_ejected = 0 if temp == "0"
replace victim_ejected = 1 if temp == "1"
replace victim_ejected = 2 if temp == "2"
replace victim_ejected = 3 if temp == "3"
replace victim_ejected = 9 if temp == "-"
order victim_ejected, before(temp)
drop temp
label define victim_ejected 0 "Not ejected" 1 "Fully ejected" 2 "Partially ejected" 3 "Unknown" 9 "Not stated"
label values victim_ejected victim_ejected
label var victim_ejected "Victim Ejected"
notes victim_ejected : Indicates whether the victim was ejected from the vehicle

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
save "D:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\stCollisions.dta", replace
