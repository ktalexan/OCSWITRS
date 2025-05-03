import json
import os


path = r"e:\SWITRS\RawData\codebook.json"


def renumber_codebook(my_path):
    """Reads a JSON file and renumbers the "no" key in the dictionary."""
    # load the json file
    print("Opening dictionary from file...")
    with open(my_path, "r") as json_file:
        # load the json data into dictionary
        dict_formatted_data = json.load(json_file)
    counter = 1 # start the counter
    # loop through the dictionary and update the "no" key
    print("Renumbering the dictionary...")
    for key in dict_formatted_data:
        if "no" in dict_formatted_data[key]:
            dict_formatted_data[key]["no"] = counter
            counter += 1 # increment the counter
    # reopen the json data file for wrting
    print("Writing the updated dictionary to file...")
    with open(my_path, "w") as json_file:
        # write the updated dictionary to the file
        json.dump(dict_formatted_data, json_file, indent=4)
    print(f"Total records: {counter-1}\nOutput file: {my_path}")
    return dict_formatted_data


path = r"e:\SWITRS\RawData\codebook2.json"
      