import os


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
              "Production,Hall"
              "Saw,Mill",
              "Steelworks"]
civilization.sort()
industrial.sort()

categories = {"civilization": civilization,
              "industrial": industrial}

for key, category in categories.items():
    print("===================={}=======================".format(key))
    for klass in category:
        for filename in os.lisdir(klass):
            path = "{}/{}/{}".format(key, klass, filename)
            print(path)
        

