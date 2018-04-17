import os
from preprocess_audio_utils import *


# filename = "AirportJetRumbles.L.wav"

save_as = "testing_dir"
main_dir = "main"
for dirs in os.listdir(main_dir):
    for filename in os.listdir("{}/{}".format(main_dir, dirs)):
        path = "./{}/{}/{}".format(main_dir, dirs, filename)
        print(path)
        audio_to_chunks(path, save_as)
