*==================================================
* STATA OCSWITRS DATA PROCESSING
* Step 1: Merging and Combining Datasets
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
	global projectTitle "Step 1: Merging and Combining Datasets"
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
	global projectDir = "${projectDisk}:/Professional/Projects-OCPW/OCTraffic/OCSWITRS"
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


*************** Program for cleaning string data ***************

capture program drop removeSpaces
program removeSpaces
	// List all the string variables in the dataset
	ds, has(type string)
	local stringVars = r(varlist)
	// For each of the string variable in the list, remove all leading and trailing spaces
	foreach var of local stringVars {
		di "`var'"
		di "- Removing leading blanks:"
		replace `var' = strltrim(`var')
		di "- Removing trailing blanks:"
		replace `var' = strrtrim(`var')
		di
	}
end


*************** Import the Crashes Raw Dataset ***************

// Import crashes raw data (80 vars, 152,992 obs)
clear
import delimited "Crashes_${dataStart}_${dataEnd}.csv", delimiter(comma) bindquote(strict) varnames(1)

// Remove all leading and trailing spaces (running the custom program)
removeSpaces

// Generate CID
tostring case_id, gen(cid)
order cid, before(case_id)

// Drop deprecated variables
drop population city_division_lapd caltrans_county caltrans_district state_route route_suffix postmile_prefix postmile location_type ramp_intersection chp_road_type county

// Convert the city variable to proper case
replace city = strproper(city)

// Create count of crashes per case
duplicates tag cid, gen(crashestag)
replace crashestag = crashestag + 1
order crashestag, after(case_id)

// Save the crashes raw data as a stata dateset
save "crashesRaw.dta", replace



*************** Import the Parties Raw Dataset ***************


// Import parties raw data (34 vars, 330,193 obs)
clear
import delimited "Parties_${dataStart}_${dataEnd}.csv", delimiter(comma) bindquote(strict) varnames(1)

// Remove all leading and trailing spaces (running the custom program)
removeSpaces

// Generate CID
tostring case_id, gen(cid)
order cid, before(case_id)

// Generate PID
egen pid = concat(cid party_number), punct(-)
order pid, after(cid)

// Create count of parties per case
duplicates tag cid, gen(partiestag)
replace partiestag = partiestag + 1
order partiestag, after(party_number)

// Save the parties raw data as a stata dataset
save "partiesRaw.dta", replace



*************** Import the Victims Raw Dataset ***************


// Import victims raw data (14 vars, 265,194 obs)
clear
import delimited "Victims_${dataStart}_${dataEnd}.csv", delimiter(comma) bindquote(strict) varnames(1)

// Remove all leading and trailing spaces (running the custom program)
removeSpaces

// Generate CID
tostring case_id, gen(cid)
order cid, before(case_id)

// Generate PID
egen pid = concat(cid party_number), punct(-)
order pid, after(cid)

// Generate VID
egen vid = concat(pid victim_number), punct(-)
order vid, after(pid)

// Drop deprecated variables
drop city county

// create count of victims per case
duplicates tag cid, gen(victimstag)
replace victimstag = victimstag + 1
order victimstag, after(victim_number)

// Save the victims raw data as a stata dataset
save "victimsRaw.dta", replace



*************** Import Supporting Datasets ***************


// Import the cities dataset (20 vars, 46 obs)
clear
import delimited "Cities.csv", delimiter(comma) bindquote(strict) varnames(1)

// Correct improper name
ren ïname name

// Only keep the vars we want to use
keep name placetype areasqmi popt hut popdens hudens popa popb poph popw vehicles_commuting travel_time

//Rename some variables
ren name city
ren vehicles_commuting vehicles
ren travel_time traveltime

// Convert the city variable to proper case
replace city = strproper(city)

// Save the cities raw data as a stata dataset
save "cities.dta", replace


// Import the roads dataset
clear
import delimited "Roads.csv", delimiter(comma) bindquote(strict) varnames(1)

// Correct improper name
ren ïbasename basename

// only keep the variables we need
keep name rid roadcat rlength

// Save the roads raw data as a stata dataset
save "roads.dta", replace



*************** Merge the Datasets ***************


// Load crashes raw data file
clear
use "crashesRaw.dta"

// merge the crashes data to the parties data (based on crash id)
merge 1:m cid using "partiesRaw.dta", generate(merged1)
label var merged1 "Crashes-Parties Merged (1:m on CID)"

// merge the collisions data with the victims data (based on party id)
merge m:m cid pid using "victimsRaw.dta", generate(merged2)
label var merged2 "Crashes-Parties-Victims Merged (m:m on CID PID)"
sort collision_date collision_time vid
order pid vid, after(cid)

// merge the collisions data with the city supporting data (based on city name)
merge m:1 city using "cities.dta", generate(merged3)
label var merged3 "Cities Merged (m:1 on city city)
drop if case_id == .


// Rename variables
ren ///
(cid pid vid case_id crashestag accident_year proc_date juris collision_date collision_time officer_id reporting_district day_of_week chp_shift cnty_city_loc special_cond beat_type chp_beat_type chp_beat_class beat_number primary_rd secondary_rd distance direction intersection weather_1 weather_2 state_hwy_ind side_of_hwy tow_away collision_severity number_killed number_injured party_count primary_coll_factor pcf_code_of_viol pcf_viol_category pcf_violation pcf_viol_subsection hit_and_run type_of_collision mviw ped_action road_surface road_cond_1 road_cond_2 lighting control_device pedestrian_accident bicycle_accident motorcycle_accident truck_accident not_private_property alcohol_involved stwd_vehtype_at_fault chp_vehtype_at_fault count_severe_inj count_visible_inj count_complaint_pain count_ped_killed count_ped_injured count_bicyclist_killed count_bicyclist_injured count_mc_killed count_mc_injured primary_ramp secondary_ramp latitude longitude city point_x point_y party_number partiestag party_type at_fault party_sex party_age party_sobriety party_drug_physical dir_of_travel party_safety_equip_1 party_safety_equip_2 finan_respons sp_info_1 sp_info_2 sp_info_3 oaf_violation_code oaf_viol_cat oaf_viol_section oaf_violation_suffix oaf_1 oaf_2 party_number_killed party_number_injured move_pre_acc vehicle_year vehicle_make stwd_vehicle_type chp_veh_type_towing chp_veh_type_towed race inattention special_info_f special_info_g merged1 victim_number victimstag victim_role victim_sex victim_age victim_degree_of_injury victim_seating_position victim_safety_equip_1 victim_safety_equip_2 victim_ejected merged2 placetype areasqmi popt hut popdens hudens popa popb poph popw vehicles traveltime merged3) ///
(cid pid vid caseid crashestag accidentyear procdate juris colldate colltime officerid reportingdistrict weekday chpshift cntycityloc specialcond beattype chpbeattype chpbeatclass beatnumber primaryrd secondaryrd distance direction intersection weather1 weather2 statehwyind sideofhwy towaway collseverity numberkilled numberinjured partycount primarycollfactor pcfcodeofviol pcfviolcategory pcfviolation pcfviolsubsection hitandrun typeofcoll mviw pedaction roadsurface roadcond1 roadcond2 lighting controldevice pedaccident bicaccident mcaccident truckaccident notprivateproperty alcoholinvolved stwdvehtypeatfault chpvehtypeatfault countsevereinj countvisibleinj countcomplaintpain countpedkilled countpedinj countbickilled countbicinj countmckilled countmcinj primaryramp secondaryramp latitude longitude city pointx pointy partynumber partiestag partytype atfault partysex partyage partysobriety partydrugphysical diroftravel partysafetyeq1 partysafetyeq2 finanrespons spinfo1 spinfo2 spinfo3 oafviolcode oafviolcat oafviolsection oafviolsuffix oaf1 oaf2 partynumberkilled partynumberinj movepreacc vehicleyear vehiclemake stwdvehicletype chpvehtypetowing chpvehtypetowed partyrace inattention specialinfof specialinfog merged1 victimnumber victimstag victimrole victimsex victimage victimdegreeofinjury victimseatingposition victimsafetyeq1 victimsafetyeq2 victimejected merged2 placetype areasqmi popt hut popdens hudens popa popb poph popw vehicles traveltime merged3)

// Order variables
order caseid cid pid vid partynumber victimnumber crashestag partiestag victimstag merged1 merged2 merged3 city placetype colldate colltime accidentyear weekday procdate collseverity partycount numberkilled numberinjured countsevereinj countvisibleinj countcomplaintpain countpedkilled countpedinj countbickilled countbicinj countmckilled countmcinj primarycollfactor typeofcoll pedaccident bicaccident mcaccident truckaccident hitandrun alcoholinvolved juris officerid reportingdistrict chpshift cntycityloc specialcond beattype chpbeattype chpbeatclass beatnumber primaryrd secondaryrd distance direction intersection weather1 weather2 roadsurface roadcond1 roadcond2 lighting controldevice statehwyind sideofhwy towaway pcfcodeofviol pcfviolcategory pcfviolation pcfviolsubsection mviw pedaction notprivateproperty stwdvehtypeatfault chpvehtypeatfault primaryramp secondaryramp partytype atfault partysex partyage partyrace partynumberkilled partynumberinj inattention partysobriety partydrugphysical diroftravel partysafetyeq1 partysafetyeq2 finanrespons spinfo1 spinfo2 spinfo3 oafviolcode oafviolcat oafviolsection oafviolsuffix oaf1 oaf2 movepreacc vehicleyear vehiclemake stwdvehicletype chpvehtypetowing chpvehtypetowed specialinfof specialinfog victimrole victimsex victimage victimdegreeofinjury victimseatingposition victimsafetyeq1 victimsafetyeq2 victimejected areasqmi popdens hudens popt hut popa popb poph popw vehicles traveltime latitude longitude pointx pointy

// save the result into a new collisions dataset
save "collisionsRaw.dta", replace


*************** End of Processing ***************
