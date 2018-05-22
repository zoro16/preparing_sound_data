import os
import argparse
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.silence import split_on_silence
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import OrderedDict
from subprocess import call
import pandas as pd
# from pydub.utils import which
# AudioSegment.converter = which("ffmpeg")



def audio_to_chunks(path, save_as):
    audio = preprocess_audio(path)

    head, tail = os.path.split(path)
    name = tail[:-4]
    # SPLIT SOUND IN 10-SECOND SLICES AND EXPORT
    for i, chunk in enumerate(audio[::10000]):
        with open("{}/{}_{:04d}.wav".format(save_as, name, i), "wb") as f:
            chunk.export(f, format="wav")

# PREPROCESS THE AUDIO TO THE CORRECT FORMAT
def preprocess_audio(filename):
    # TRIM OR PAD AUDIO SEGMENT TO 10000MS
    # padding = AudioSegment.silent(duration=10000)
    segment = AudioSegment.from_wav(filename)
    # segment = padding.overlay(segment)
    segment = segment.set_sample_width(2)
    segment = segment.set_frame_rate(16000)
    # segment = segment.set_channels(1)
    # segment.export(filename, format='wav')

    return segment

# LOAD A WAV FILE
def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

def mp3_to_wav(input_path):
    output_path = "{}.wav".format(input_path[:-4])
    sound = AudioSegment.from_mp3(input_path)
    sound.export(output_path, format="wav")

# CALCULATE AND PLOT SPECTROGRAM FOR A WAV AUDIO FILE
def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    nfft = 200 # LENGTH OF EACH WINDOW SEGMENT
    fs = 8000 # SAMPLING FREQUENCIES
    noverlap = 120 # OVERLAP BETWEEN WINDOWS
    nchannels = data.ndim
    if nchannels == 1:
        pxx, freqs, bins, im = plt.specgram(data, nfft, fs, noverlap=noverlap)
    elif nchannels == 2:
        pxx, freqs, bins, im = plt.specgram(data[:,0], nfft, fs, noverlap=noverlap)

    return pxx

def wav_to_jpg(filename):
    rate, data = get_wav_info(filename)
    nfft = 256 # LENGTH OF EACH WINDOW SEGMENT
    fs = 256 # SAMPLING FREQUENCIES
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

# ImageMagick HAS TO BE INSTALLED
def png_to_jpg(main_dir):
    wd = os.getcwd()
    path = os.path.join(wd, main_dir)
    for klass in os.listdir(path):
        c_klass = os.path.join(path, klass)
        os.chdir(c_klass)
        call(["mogrify", "-format", "jpg", "*.png"])

# USED TO STANDARDIZE VOLUME OF AUDIO CLIP
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

# CHECK FOR SILENT FILES OR dBFS IS -INF
def check_for_inf_amplitude(main_dir):
    wd = os.getcwd()
    path = os.path.join(wd, main_dir)
    for klass in os.listdir(path):
        c_klass = os.path.join(path, klass)
        os.chdir(c_klass)
        for filename in os.listdir(c_klass):
            filename = os.path.join(c_klass, filename)
            segment = AudioSegment.from_wav(filename)
            if segment.dBFS == -float("inf"):
                print(filename)

def remove_silent_files(path, ext="wav"):
    # PRE-STEP
    # df = pd.read_csv("silent_files.txt", sep="/", header=None, names=["class", "filename"])
    # df["filename"] = df["filename"].str.replace(".wav", "")
    # df.to_csv("silent_files.tsv", sep="\t", index=None)

    df = pd.read_table("silent_files.tsv")

    for i, k in zip(df["class"], df["filename"]):
        full_path = "{}/{}/{}.{}".format(path, i, k, ext)
        print(full_path)
        os.remove(full_path)

def generate_labeled_data(filename, ext="wav"):
    df = pd.read_csv(filename, sep="\t")
    df["X"] = df["X"].astype(str) + "." + ext
    output = "labeled_{}.tsv".format(ext)
    df.to_csv(output, index=None, sep="\t")

def check_wave_lenght(sound):
    if type(sound) is str:
        sound = AudioSegment.from_wav(sound)
        return len(sound) / 1000  # sound.duration_seconds
    if type(sound) is AudioSegment:
        return len(sound) / 1000

def combine_audio_chunks(chunks):
    combined = [chunks[0]]
    for chunk in chunks[1:]:
        combined[-1] += chunk
    return combined

def remove_silence_from_audio(sound, ext,
                              min_silence_len,
                              silence_thresh,
                              keep_silence,
                              to_ignore):

    ignored_sound = AudioSegment.from_wav(to_ignore)
    output = "{}_nosilence.{}".format(sound[:-4], ext)

    if type(sound) is str:
        sound = AudioSegment.from_wav(sound)
        silance_chunk = split_on_silence(sound,
                                          min_silence_len=min_silence_len,
                                          silence_thresh=silence_thresh,
                                          keep_silence=keep_silence)
        combined = silance_chunk[0]
        for chunk in silance_chunk[1:]:
            if chunk == ignored_sound:
                continue
            else:
                combined += chunk
        combined.export(output, format=ext)

    elif type(sound) is AudioSegment:
        silance_chunk = split_on_silence(sound,
                                          min_silence_len=min_silence_len,
                                          silence_thresh=silence_thresh,
                                          keep_silence=keep_silence)
        combined = silance_chunk[0]
        for chunk in silance_chunk[1:]:
            if chunk == ignored_sound:
                continue
            else:
                combined += chunk
        combined.export(output, format="wav")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_path",
        help="Set this flag to specfiy the input path")
    parser.add_argument(
        "-o",
        "--output_path",
        help="Set this flag to specfiy the output path")
    parser.add_argument(
        "--min_silence_len",
        help="Set this for `remove_silence_from_audio` command to set a differen "\
        "minimum silece length (in ms)")
    parser.add_argument(
        "--to_ignore",
        help="Set this for `remove_silence_from_audio` command to specify which sound to ignore")
    parser.add_argument(
        "--silence_thresh",
        help="Set this for `remove_silence_from_audio` command to set silence thresh (in dBFS)")
    parser.add_argument(
        "--keep_silence",
        help="Set this for `remove_silence_from_audio` command to set the amount of "\
        "silence to leave at the beginning and end of the chunks (in ms)")
    parser.add_argument(
        "-p",
        "--main_dir",
        help="This flag to specify the main audio files directory path"\
        " e.g `/mountdir/data/civilization/`")
    parser.add_argument(
        "-e",
        "--extension",
        help="Set this to specfiy the file extension that you want to process on.")
    parser.add_argument(
        "-s",
        "--slice_audio",
        action="store_true",
        help="Set this flag if you want to slice the *.wav file into"
        "chunks of 10sec audio files")
    parser.add_argument(
        "-S",
        "--to_spectrogram",
        action="store_true",
        help="Set this flag  to create spectrograms images from *.wav files")
    parser.add_argument(
        "--png2jpg",
        action="store_true",
        help="Set this to convert *.png images to *.jpg, you need to install"\
        " imagmagick in you *inux machine")
    parser.add_argument(
        "--mp32wav",
        action="store_true",
        help="Set this to convert *.mp3 audio files to *.wav, you need to install"\
        " ffmpeg in you *inux machine")
    parser.add_argument(
        "--check_inf",
        action="store_true",
        help="Set this to check if audio files are silence")
    parser.add_argument(
        "-rsf",
        "--remove_silent",
        action="store_true",
        help="Set this to specfiy the file extension that you want to process on.")
    parser.add_argument(
        "-rsa",
        "--remove_silence_from_audio",
        action="store_true",
        help="Set this to remove silence from wave file then combine the chunks"\
        " with no silece in them.")
    parser.add_argument(
        "-g",
        "--generate_label",
        action="store_true",
        help="Set this to generate labeled data from existing.")


    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    main_dir = args.main_dir
    ext = args.extension
    min_silence_len = args.min_silence_len
    silence_thresh = args.silence_thresh
    keep_silence = args.keep_silence
    to_ignore = args.to_ignore


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
                    if path.endswith("mp3"):
                        mp3_to_wav(path)
                        audio_to_chunks(input_path, output_path)
                    if path.endswith("wav"):
                        audio_to_chunks(input_path, output_path)
        else:
            if path.endswith("mp3"):
                print("convert from mp3 to wav")
                mp3_to_wav(input_path)
                print("start slicing audio files")
                audio_to_chunks(input_path, output_path)
                print("Done!")
            if path.endswith("wav"):
                print("start slicing audio files")
                audio_to_chunks(input_path, output_path)
                print("Done!")

    if args.png2jpg:
        if main_dir:
            print("Start converting from png to jpg")
            png_to_jpg(main_dir)
            print("Done!")

    if args.mp32wav:
        print("convert from mp3 to wav")
        mp3_to_wav(input_path)
        print("Done!")

    if args.check_inf:
        if main_dir:
            check_for_inf_amplitude(main_dir)

    if args.remove_silent:
        if main_dir:        
            remove_silent_files(main_dir, ext)

    if args.generate_label:
        generate_labeled_data(input_path, ext)

    if args.remove_silence_from_audio:
        print("Start")
        remove_silence_from_audio(input_path, ext="wav",
                                  min_silence_len=50,
                                  silence_thresh=-65,
                                  keep_silence=50,
                                  to_ignore)
        print("Done!")
