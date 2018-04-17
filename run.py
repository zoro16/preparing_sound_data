import os
from preprocess_audio_utils import *


# filename = "AirportJetRumbles.L.wav"

save_at = "../../preprocessed_data"
main_dir = "original_data"
for dirs in os.listdir(main_dir):
    try:
        for filename in os.listdir("{}/{}".format(main_dir, dirs)):
            print(filename)
            audio_to_chunks(filename, save_at)
    except:
        pass
