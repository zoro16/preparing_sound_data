import os
from data_utils import audio_to_chunks
from tqdm import tqdm
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--main_dir",
                    help="Path for the main directory",
                    action="store_true")
parser.add_argument("--save_as",
                    help="Path to save out put",
                    action="store_true")
args = parser.parse_args()
save_as = args.save_as
main_dir = args.main_dir

for dirs in tqdm(os.listdir(main_dir), desc='Categories', leave=True):
    for filename in tqdm(os.listdir("{}/{}".format(main_dir, dirs)),
                         desc='Audio File'
                         leave=True):
        path = "./{}/{}/{}".format(main_dir, dirs, filename)
        # print('{} in {}'.format(filename, dirs))
        audio_to_chunks(path, save_as)
