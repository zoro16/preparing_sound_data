import os
import json
from pprint import pprint
from shutil import copyfile
from ind_list_files import ind_list
from civil_list_files import civil_list

civilization = ["Airport,Ambience",
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

industrial = ["Assembly,Plant",
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
civilization.sort()
industrial.sort()
categories = {"civilization": civilization,
              "industrial": industrial
}

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

def map_classes_to_files():
    civilization_ready_data = []
    industrial_ready_data = []

    for key, category in categories.items():
        # print("===================={}=======================".format(key))
        for klass in category:
            path = "/mountdir/data/{}/original_data/{}".format(key, klass)
            os.chdir(path)
            for filename in os.listdir(os.getcwd()):
                path = "/mountdir/data/{}/original_data/{}/{}".format(key, klass, filename)
                if key == "industrial":
                    industrial_ready_data.append(files_to_classes(klass, filename))
                elif key == "civilization":
                    civilization_ready_data.append(files_to_classes(klass, filename))

    ready_data = {"civilization": civilization_ready_data,
                  "industrial": industrial_ready_data
    }

    return json.dumps(ready_data, ensure_ascii=False)

# print(map_classes_to_files())

####################################################################

def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_dirs_for_preprocessed_data(category):
    for key, category in categories.items():
        for klass in category:
            path = "/mountdir/data/{}/{}/{}".format(key, category, klass)
            create_folder(path)

#create_dirs_for_preprocessed_data("industrial")
####################################################################
audio_data = []

def get_list_of_processed_files(category, folder):
    path = "/mountdir/data/{}/{}".format(category, folder)
    os.chdir(path)
    for filename in os.listdir(os.getcwd()):
        if filename.endswith(".wav"):
            audio_data.append(filename)
    
# get_list_of_processed_files("civilization", "civil_audio_data")
#get_list_of_processed_files("industrial", "industrial_audio_data")
#print("data = {}".format(audio_data))

####################################################################
def map_processed_files_to_classes(folder, list_type):
    data = json.load(open('data.json'))
    for key, classes_list in data.items():
        for file_maps in classes_list:
            for klass, filename in file_maps.items():
                if key == 'industrial':
                    for index, i in enumerate(list_type):
                        if i.startswith(filename):
                            src = "/mountdir/data/{}/{}/{}".format(key, folder, i)
                            dst = "/mountdir/data/{}/{}/{}/{}".format(key, folder, klass, i)
                            copyfile(src, dst)
                            print(src)
                            print(dst)
                            list_type.pop(index)

map_processed_files_to_classes("industrial_audio_data", ind_list)
# map_processed_files_to_classes("civil_audio_data", civil_list)

####################################################################
