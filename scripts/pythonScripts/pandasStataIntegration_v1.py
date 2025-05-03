############################################
# OCSWITRS - Pandas to Stata Integration   #
# Version 1                                #
# Date: 2024-11-20                         #
############################################


# Importing Libraries
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
# Import date and time library
from datetime import datetime
import os


# Get today's date
today = datetime.today().strftime('%Y-%m-%d')

# Paths to the Pickle Pandas Files
dfCollisions = pd.read_pickle(r'I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/RawData/dfCollisions.pkl')
dfCrashes = pd.read_pickle(r'I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/RawData/dfCrashes.pkl')
dfParties = pd.read_pickle(r'I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/RawData/dfParties.pkl')
dfVictims = pd.read_pickle(r'I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/RawData/dfVictims.pkl')

# read json file
codebook = pd.read_json('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/RawData/codebook.json')

# Send the dataframe data to csv
dfCollisions.to_csv('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfCollisions_final.csv', index=False)
dfCrashes.to_csv('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfCrashes_final.csv', index=False)
dfParties.to_csv('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfParties_final.csv', index=False)
dfVictims.to_csv('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfVictims_final.csv', index=False)


# COLLISIONS DATA IMPORT
#--------------------------------
f = open('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfCollisionsImport.do', 'w')
f.write("\n/* OCSWITS Collisions Data Processing */")
f.write(f"\n/* Version 1, Date: {today} */\n\n")
f.write("clear all\n")
f.write("\n/* Importing dfCollisions */\n")
f.write("import delimited I:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfCollisions_final.csv, case(preserve)\n")
# for each name of the codebook, read the name of the entry
for col in dfCollisions:
    f.write(f"\n/* {col} Variable Operations */")
    alias = f'''"{codebook[col]['alias']}"'''
    desc = codebook[col]['desc']
    f.write(f"\nlabel var {col} {alias} \nnotes {col} : {desc}\n")
    if codebook[col]["dbin"] == "Y":
        f.write("/* Defining Value Labels */\n")       
        if is_numeric_dtype(dfCollisions[col]):
            mystring = f"label define {col} "
            for x in codebook[col]["domain"]:
                mystring += ' ' + x + ' ' + f'''"{codebook[col]["domain"][x]}"'''
            f.write(mystring)
            f.write(f"\nlabel values {col} {col}\n")
        elif is_string_dtype(dfCollisions[col]):
            for y in codebook[col]["domain"]:
                f.write(f"\nreplace {col} = " + f'''"{codebook[col]["domain"][y]}"''' + f" if {col} == " + f'''"{y}"''')
            f.write(f"\nrename {col} {col}1")
            f.write(f"\nencode {col}1, generate({col})")
            f.write(f"\norder {col}, before({col}1)")
            f.write(f"\ndrop {col}1")
            f.write("\n")
f.write("\n/* Datetime Manipulations */")
f.write('\ngenerate double EVENTDATETIME = clock(COLLISION_DATETIME, "YMDhms")')
f.write('\nlabel var EVENTDATETIME "Crash Date and Time" \nnotes EVENTDATETIME : "The date and time of the crash"')
f.write("\nformat EVENTDATETIME %tc")
f.write("\norder EVENTDATETIME, before(COLLISION_DATETIME)\n")

f.write("\n/* Generate Indicator Variables for Severity Ranks */")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 3 6 = 0) (1 2 4 5 7 8 = 1) (missing=.), generate(IND_SEVERE)")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 1 2 = 0) (3 4 5 6 7 8 = 1) (missing=.), generate(IND_FATAL)")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 1 3 4 = 0) (2 5 6 7 8 = 1) (missing=.), generate(IND_MULTI)")

f.write("\n\n/* Severe Indicator Variable Operations */")
f.write('\nlabel var IND_SEVERE "Severe Injury Indicator" \nnotes IND_SEVERE : "Reclassified indicator variable from severity level where there exist severe injuries in the accident"')
f.write("\norder IND_SEVERE, after(COLLISION_SEVERITY_RANKED)")
f.write('\nlabel define IND_SEVERE 0 "Not a severe injury" 1 "Severe injury"')
f.write("\nlabel values IND_SEVERE IND_SEVERE")

f.write("\n\n/* Fatal Indicator Variable Operations */")
f.write('\nlabel var IND_FATAL "Fatal Injury Indicator" \nnotes IND_FATAL : "Reclassified indicator variable from severity level where there exist fatal injuries in the accident"')
f.write("\norder IND_FATAL, after(IND_SEVERE)")
f.write('\nlabel define IND_FATAL 0 "Not a fatal injury" 1 "Fatal injury"')
f.write("\nlabel values IND_FATAL IND_FATAL")

f.write("\n\n/* Multiple Indicator Variable Operations */")
f.write('\nlabel var IND_MULTI "Multiple Injury Indicator" \nnotes IND_MULTI : "Reclassified indicator variable from severity level where there exist multiple severe or fatal injuries in the accident"')
f.write("\norder IND_MULTI, after(IND_FATAL)")
f.write('\nlabel define IND_MULTI 0 "No multiple severe or fatal injuries present" 1 "Multiple severe or fatal injuries present"')
f.write("\nlabel values IND_MULTI IND_MULTI")


f.write("\n\n/* Saving Dataset */")
f.write(f'\nsave "I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/stCollisions.dta", replace\n')
f.close()


# CRASHES DATA IMPORT
#--------------------------------
f = open('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfCrashesImport.do', 'w')
f.write("\n/* OCSWITS Crashes Data Processing */")
f.write(f"\n/* Version 1, Date: {today} */\n\n")
f.write("clear all\n")
f.write("\n/* Importing dfCrashes */\n")
f.write("import delimited I:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfCrashes_final.csv, case(preserve)\n")
# for each name of the codebook, read the name of the entry
for col in dfCrashes:
    f.write(f"\n/* {col} Variable Operations */")
    alias = f'''"{codebook[col]['alias']}"'''
    desc = codebook[col]['desc']
    f.write(f"\nlabel var {col} {alias} \nnotes {col} : {desc}\n")
    if codebook[col]["dbin"] == "Y":
        f.write("/* Defining Value Labels */\n")       
        if is_numeric_dtype(dfCrashes[col]):
            mystring = f"label define {col} "
            for x in codebook[col]["domain"]:
                mystring += ' ' + x + ' ' + f'''"{codebook[col]["domain"][x]}"'''
            f.write(mystring)
            f.write(f"\nlabel values {col} {col}\n")
        elif is_string_dtype(dfCrashes[col]):
            for y in codebook[col]["domain"]:
                f.write(f"\nreplace {col} = " + f'''"{codebook[col]["domain"][y]}"''' + f" if {col} == " + f'''"{y}"''')
            f.write(f"\nrename {col} {col}1")
            f.write(f"\nencode {col}1, generate({col})")
            f.write(f"\norder {col}, before({col}1)")
            f.write(f"\ndrop {col}1")
            f.write("\n")
f.write("\n/* Datetime Manipulations */")
f.write('\ngenerate double EVENTDATETIME = clock(COLLISION_DATETIME, "YMDhms")')
f.write('\nlabel var EVENTDATETIME "Crash Date and Time" \nnotes EVENTDATETIME : "The date and time of the crash"')
f.write("\nformat EVENTDATETIME %tc")
f.write("\norder EVENTDATETIME, before(COLLISION_DATETIME)\n")

f.write("\n\n/* Generate Indicator Variables for Severity Ranks */")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 3 6 = 0) (1 2 4 5 7 8 = 1) (missing=.), generate(IND_SEVERE)")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 1 2 = 0) (3 4 5 6 7 8 = 1) (missing=.), generate(IND_FATAL)")
f.write("\nrecode COLLISION_SEVERITY_RANKED (0 1 3 4 = 0) (2 5 6 7 8 = 1) (missing=.), generate(IND_MULTI)")

f.write("\n\n/* Severe Indicator Variable Operations */")
f.write('\nlabel var IND_SEVERE "Severe Injury Indicator" \nnotes IND_SEVERE : "Reclassified indicator variable from severity level where there exist severe injuries in the accident"')
f.write("\norder IND_SEVERE, after(COLLISION_SEVERITY_RANKED)")
f.write('\nlabel define IND_SEVERE 0 "Not severe" 1 "Severe"')
f.write("\nlabel values IND_SEVERE IND_SEVERE")

f.write("\n\n/* Fatal Indicator Variable Operations */")
f.write('\nlabel var IND_FATAL "Fatal Injury Indicator" \nnotes IND_FATAL : "Reclassified indicator variable from severity level where there exist fatal injuries in the accident"')
f.write("\norder IND_FATAL, after(IND_SEVERE)")
f.write('\nlabel define IND_FATAL 0 "Not fatal" 1 "Fatal"')
f.write("\nlabel values IND_FATAL IND_FATAL")

f.write("\n\n/* Multiple Indicator Variable Operations */")
f.write('\nlabel var IND_MULTI "Multiple Injury Indicator" \nnotes IND_MULTI : "Reclassified indicator variable from severity level where there exist multiple severe or fatal injuries in the accident"')
f.write("\norder IND_MULTI, after(IND_FATAL)")
f.write('\nlabel define IND_MULTI 0 "Not multiple" 1 "Multiple"')
f.write("\nlabel values IND_MULTI IND_MULTI")

f.write("\n\n/* Saving Dataset */")
f.write(f'\nsave "I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/stCrashes.dta", replace\n')
f.close()



# PARTIES DATA IMPORT
#--------------------------------
f = open('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfPartiesImport.do', 'w')
f.write("\n/* OCSWITS Parties Data Processing */")
f.write(f"\n/* Version 1, Date: {today} */\n\n")
f.write("clear all\n")
f.write("\n/* Importing dfParties */\n")
f.write("import delimited I:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfParties_final.csv, case(preserve)\n")
# for each name of the codebook, read the name of the entry
for col in dfParties:
    f.write(f"\n/* {col} Variable Operations */")
    alias = f'''"{codebook[col]['alias']}"'''
    desc = codebook[col]['desc']
    f.write(f"\nlabel var {col} {alias} \nnotes {col} : {desc}\n")
    if codebook[col]["dbin"] == "Y":
        f.write("/* Defining Value Labels */\n")       
        if is_numeric_dtype(dfParties[col]):
            mystring = f"label define {col} "
            for x in codebook[col]["domain"]:
                mystring += ' ' + x + ' ' + f'''"{codebook[col]["domain"][x]}"'''
            f.write(mystring)
            f.write(f"\nlabel values {col} {col}\n")
        elif is_string_dtype(dfParties[col]):
            for y in codebook[col]["domain"]:
                f.write(f"\nreplace {col} = " + f'''"{codebook[col]["domain"][y]}"''' + f" if {col} == " + f'''"{y}"''')
            f.write(f"\nrename {col} {col}1")
            f.write(f"\nencode {col}1, generate({col})")
            f.write(f"\norder {col}, before({col}1)")
            f.write(f"\ndrop {col}1")
            f.write("\n")
f.write("\n/* Datetime Manipulations */")
f.write('\ngenerate double EVENTDATETIME = clock(COLLISION_DATETIME, "YMDhms")')
f.write('\nlabel var EVENTDATETIME "Crash Date and Time" \nnotes EVENTDATETIME : "The date and time of the crash"')
f.write("\nformat EVENTDATETIME %tc")
f.write("\norder EVENTDATETIME, before(COLLISION_DATETIME)\n")
f.write("\n/* Saving Dataset */")
f.write(f'\nsave "I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/stParties.dta", replace\n')
f.close()



# VICTIMS DATA IMPORT
#--------------------------------
f = open('I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/dfVictimsImport.do', 'w')
f.write("\n/* OCSWITS Crashes Data Processing */")
f.write(f"\n/* Version 1, Date: {today} */\n\n")
f.write("clear all\n")
f.write("\n/* Importing dfVictims */\n")
f.write("import delimited I:\Professional\Projects-OCPW\OCTraffic\OCSWITRS\Analysis\dfVictims_final.csv, case(preserve)\n")
# for each name of the codebook, read the name of the entry
for col in dfVictims:
    f.write(f"\n/* {col} Variable Operations */")
    alias = f'''"{codebook[col]['alias']}"'''
    desc = codebook[col]['desc']
    f.write(f"\nlabel var {col} {alias} \nnotes {col} : {desc}\n")
    if codebook[col]["dbin"] == "Y":
        f.write("/* Defining Value Labels */")       
        if is_numeric_dtype(dfVictims[col]):
            mystring = f"label define {col} "
            for x in codebook[col]["domain"]:
                mystring += ' ' + x + ' ' + f'''"{codebook[col]["domain"][x]}"'''
            f.write(mystring)
            f.write(f"\nlabel values {col} {col}\n")
        elif is_string_dtype(dfVictims[col]):
            for y in codebook[col]["domain"]:
                f.write(f"\nreplace {col} = " + f'''"{codebook[col]["domain"][y]}"''' + f" if {col} == " + f'''"{y}"''')
            f.write(f"\nrename {col} {col}1")
            f.write(f"\nencode {col}1, generate({col})")
            f.write(f"\norder {col}, before({col}1)")
            f.write(f"\ndrop {col}1")
            f.write("\n")
f.write("\n/* Datetime Manipulations */")
f.write('\ngenerate double EVENTDATETIME = clock(COLLISION_DATETIME, "YMDhms")')
f.write('\nlabel var EVENTDATETIME "Crash Date and Time" \nnotes EVENTDATETIME : "The date and time of the crash"')
f.write("\nformat EVENTDATETIME %tc")
f.write("\norder EVENTDATETIME, before(COLLISION_DATETIME)\n")
f.write("\n/* Saving Dataset */")
f.write(f'\nsave "I:/Professional/Projects-OCPW/OCTraffic/OCSWITRS/Analysis/stVictims.dta", replace\n')
f.close()
