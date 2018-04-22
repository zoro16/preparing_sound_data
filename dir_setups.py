import os
import json
from shutil import copyfile
import argparse

civilization_classes = ["Airport,Ambience",
                        "Bar,Ambience",
                        "Crowd,Applause",
                        "Industrial,Ambience",
                        "Rain",
                        "Theatre,Ambience",                
                        "Train,Interior",
                        "Wind",
                        "Alps,Ambience",
                        "Birds,Ambience",
                        "Crowd,Laughter",
                        "Museum,Ambience",
                        "Residential,Ambience",
                        "Thunder",
                        "War,Ambience",
                        "Auto,1973_Alfa_Romeo",
                        "Cafeteria,Ambience",
                        "Crowd,Murmur",
                        "Nature,Ambience",
                        "Restaurant,Ambience",
                        "Traffic",
                        "Water,Fall",
                        "Auto,1976_BMW_525",
                        "Canyon,Ambience",
                        "Crowd,Outdoor",
                        "Neighborhood,Ambience",
                        "RoomTone,Ambience",
                        "Traffic,Air",
                        "Water,Lake",
                        "Auto,1982_Citroen",
                        "City,Ambience",
                        "Elevator",
                        "OpenSpace,Ambience",
                        "Shopping,Ambience",
                        "Traffic,City",
                        "Water,Ocean",
                        "Auto,1994_Renault_Clio",
                        "Concert,Ambience",
                        "Forest,Ambience",
                        "Opera,Ambience",
                        "Station,Ambience",
                        "Traffic,Highway",
                        "Water,River",
                        "Auto,2006_Mini_Cooper",
                        "Construction,Ambience",
                        "Hall,Ambience",
                        "Park,Ambience",
                        "Subway,Ambience",
                        "Traffic,Rain",
                        "Water,Stream"]

industrial_classes = ["Assembly,Plant",
                      "Elevators",
                      "Hammer,Mill",
                      "Joinery",
                      "Mill,Old",
                      "Quarry,Mill",
                      "Saw,Mill,Old",
                      "Warehouse",
                      "Bottling,Plant",
                      "Extrusion,Press",
                      "Industrial,Grinding",
                      "Mechanical,Manufacturing",
                      "Paper,Plant",
                      "Recycling",
                      "Sewing",
                      "Weaving,Mill",
                      "Brewery",
                      "Food,Production",
                      "Industrial,Misc",
                      "Mill,Manufacturing",
                      "Printing",
                      "Room,Tones",
                      "Ship,Engine,Sulzer",
                      "Casting,House",
                      "Furnace",
                      "Industrial_Sound_Effects",
                      "Mill,Modern",
                      "Production,Hall",
                      "Saw,Mill",
                      "Steelworks"]
civilization_classes.sort()
industrial_classes.sort()
categories = {"civilization": civilization_classes,
              "industrial": industrial_classes}

def files_to_classes(klass, filename):
    return {klass: filename.split(".")[0]}

def remove_duplication(input_list):
    seen = set()
    new_l = []
    for d in input_list:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
            
    return new_l

def map_classes_to_files(main_path, folder):
    civilization_filenames_list = []
    industrial_filenames_list = []
    for key, category in categories.items():
        for klass in category:
            path = "{}/{}/{}/{}".format(main_path, key, folder, klass)
            os.chdir(path)
            for filename in os.listdir(os.getcwd()):
                path = "{}/{}/{}/{}/{}".format(main_path, key, folder, klass, filename)
                if key == "industrial":
                    industrial_filenames_list.append(files_to_classes(klass, filename))
                elif key == "civilization":
                    civilization_filenames_list.append(files_to_classes(klass, filename))

    full_list = {"civilization": civilization_filenames_list,
                  "industrial": industrial_filenames_list}
    data = json.dumps(full_list, ensure_ascii=False)
    with open('data.json', 'w') as f:
        f.write(data)

    return data

def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_dirs_for_preprocessed_data(main_path, category):
    for key, category in categories.items():
        for klass in category:
            path = "{}/{}/{}/{}".format(main_path, key, category, klass)
            create_folder(path)

def create_list_of_processed_files(main_path, category, folder):
    audio_data = []
    path = "{}/{}/{}".format(main_path, category, folder)
    os.chdir(path)
    for klass in os.listdir(os.getcwd()):
        for filename in os.listdir(klass):
            if filename.endswith(".wav"):
                audio_data.append(filename)
    filename = "{}/{}_list_files.py".format(main_path, category)
    _ , var = os.path.split(filename)
    with open(filename, 'w') as f:
        f.write("{} = {}".format(var[:-3], audio_data))

    return audio_data

def get_list_files(list_type):
    if list_type == "industrial":
        from industrial_list_files import industrial_list_files
        return industrial_list_files
    elif list_type == "civilization":
        from civilization_list_files import civilization_list_files
        return civilization_list_files

def map_processed_files_to_classes(main_path, folder, list_type):
    try:
        data = json.load(open('data.json'))
    except IOError:
        print("File doesn't exist")

    list_type = get_list_files(list_type)

    for key, classes_list in data.items():
        for file_maps in classes_list:
            for klass, filename in file_maps.items():
                if key == 'industrial':
                    for index, i in enumerate(list_type):
                        if i.startswith(filename):
                            src = "{}/{}/{}/{}".format(main_path, key, folder, i)
                            dst = "{}/{}/{}/{}/{}".format(main_path, key, folder, klass, i)
                            copyfile(src, dst)
                            print(src)
                            print(dst)
                            list_type.pop(index)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main_path",
        help="This is to set the absolute path to the main directory of our dataset")
    parser.add_argument(
        "--folder",
        help="This is to set the name of the main folder e.g. `original_data`",
        default="civil_audio_data")
    parser.add_argument(
        "--category",
        help="Set this to specify the e.g. `industrial` or `civilization`",
        default="civilization")
    parser.add_argument(
        "--list_type",
        help="Set this to specfiy the type of the processed audio files")
    parser.add_argument(
        "--classes_to_files",
        action="store_true",
        help="Set this flag to map the audio or other files to it's class",
        default=False)
    parser.add_argument(
        "--create_ready_data_dirs",
        action="store_true",
        help="Set this to create directories from classes we have for preprocess files",
        default=False)
    parser.add_argument(
        "--create_ready_files_list",
        action="store_true",
        help="Set this to create a list of all the processed files and put them in python file as list",
        default=False)
    parser.add_argument(
        "--files_to_classes",
        action="store_true",
        help="Set this to map all the processed files into their classes folders",
        default=False)

    args = parser.parse_args()
    main_path = args.main_path
    category = args.category
    folder = args.folder
    list_type = args.list_type

    if args.classes_to_files:
        map_classes_to_files(main_path, folder)
    
    if args.create_ready_data_dirs:
        create_dirs_for_preprocessed_data(main_path, category)
    
    if args.create_ready_files_list:
        create_list_of_processed_files(main_path, category, folder)

    if args.files_to_classes:        
        map_processed_files_to_classes(main_path, folder, list_type)
