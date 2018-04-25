import os
import argparse
from scipy.io import wavfile
from pydub import AudioSegment
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import OrderedDict
from subprocess import call


def audio_to_chunks(path, save_as):
    audio = preprocess_audio(path)

    head, tail = os.path.split(path)
    name = tail[:-4]
    # split sound in 10-second slices and export
    for i, chunk in enumerate(audio[::10000]):
        with open("{}/{}_{:04d}.wav".format(save_as, name, i), "wb") as f:
            chunk.export(f, format="wav")

# Preprocess the audio to the correct format
def preprocess_audio(filename):
    # Trim or pad audio segment to 10000ms
    # padding = AudioSegment.silent(duration=10000)
    segment = AudioSegment.from_wav(filename)
    # segment = padding.overlay(segment)
    segment = segment.set_sample_width(2)
    segment = segment.set_frame_rate(16000)
    # segment = segment.set_channels(1)
    # segment.export(filename, format='wav')

    return segment

# Load a wav file
def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

# Calculate and plot spectrogram for a wav audio file
def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    nfft = 200 # Length of each window segment
    fs = 8000 # Sampling frequencies
    noverlap = 120 # Overlap between windows
    nchannels = data.ndim
    if nchannels == 1:
        pxx, freqs, bins, im = plt.specgram(data, nfft, fs, noverlap=noverlap)
    elif nchannels == 2:
        pxx, freqs, bins, im = plt.specgram(data[:,0], nfft, fs, noverlap=noverlap)

    return pxx

def wav_to_jpg(filename):
    rate, data = get_wav_info(filename)
    nfft = 256 # Length of each window segment
    fs = 256 # Sampling frequencies
    pxx, freqs, bins, im = plt.specgram(data, nfft, fs)
    plt.axis('off')
    save_spectrogram_as_jpg(plt, filename)

def save_spectrogram_as_jpg(plt, wav_filename):
    # mpl.rcParams["savefig.directory"] = os.chdir(output_path)
    png_filename = "{}.png".format(wav_filename[:-4])
    
    plt.savefig(png_filename,
                frameon='false',
                bbox_inches='tight',
                pad_inches=0)
    plt.gcf().clear()
    plt.close()
    # convert_to_jpg(png_filename)

def convert_to_jpg(filename):
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    rgb_im.save("{}.jpg".format(filename[:-4]))
    # if os.path.exists(filename):
    #     os.remove(filename)

# ImageMagic has to be installed
def png_to_jpg(main_dir):
    wd = os.getcwd()
    path = os.path.join(wd, main_dir)
    for klass in os.listdir(path):
        c_klass = os.path.join(path, klass)
        os.chdir(c_klass)
        call(["mogrify", "-format", "jpg", "*.png"])

# Used to standardize volume of audio clip
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        help="Set this flag to specfiy the input path")
    parser.add_argument(
        "--output_path",
        help="Set this flag to specfiy the output path")
    parser.add_argument(
        "--main_dir",
        help="This flag to specify the main audio files directory path e.g `/mountdir/data/civilization/`")
    parser.add_argument(
        "--slice_audio",
        action="store_true",
        help="Set this flag if you want to slice the *.wav file into chuncks of 10sec audio files")
    parser.add_argument(
        "--to_spectrogram",
        action="store_true",
        help="Set this flag  to create spectrograms images from *.wav files")
    parser.add_argument(
        "--png2jpg",
        action="store_true",
        help="Set this to convert *.png images to *.jpg, you need to install imagmagic in you *inux machine")


    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    main_dir = args.main_dir

    if args.to_spectrogram:
        if main_dir:
            full_list = {}
            for klass in os.listdir(main_dir):
                main_path = "{}/{}".format(main_dir, klass)
                temp = []
                for filename in os.listdir(main_path):
                    p = "{}/{}/{}".format(main_dir, klass, filename)
                    temp.append(p)
                full_list[klass] = temp

            full_list = OrderedDict(sorted(full_list.items(), key=lambda t: t[0]))

            for key, files_list in full_list.items():
                files_list.sort()
                for index, filename in enumerate(files_list):
                    if files_list[index][:-4] == files_list[index-1][:-4]:
                        # print("ALREADY CONVERTED TO PNG")
                        continue
                    else:
                        if filename.endswith(".wav"):
                            print(filename)
                            wav_to_jpg(filename)
        else:
            wav_to_jpg(input_path)
        
    if args.slice_audio:
        if main_dir:
            for dirs in tqdm(os.listdir(main_dir),
                             desc='Main Classes',
                             leave=True):
                main_path = "{}/{}".format(main_dir, dirs)
                list_of_files = os.listdir(main_path)
                for filename in tqdm(list_of_files,
                                     desc='File: ',
                                     leave=True):
                    path = "{}/{}".format(main_path, filename)
                    audio_to_chunks(input_path, output_path)
        else:
            print("start slicing audio files")
            audio_to_chunks(input_path, output_path)
            print("Done slicing")

    if args.png2jpg:
        if main_dir:
            png_to_jpg(main_dir)
