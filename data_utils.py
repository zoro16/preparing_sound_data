import os
import platform
import argparse
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.silence import split_on_silence
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from collections import OrderedDict
from subprocess import call
import pandas as pd
from functools import wraps



def validate_extension(fname):
    if fname.endswith("wav") or fname.endswith("mp3") or fname.endswith("jpg") or fname.endswith("png"):
        return True
    else:
        return False

def iter_dir(folder):
    folders = []
    root = os.getcwd()
    folder_path = os.path.join(root, folder)
    if os.path.isdir(folder_path):
        for sub_folder in os.listdir(folder_path):
            sub_folder_path = os.path.join(folder_path, sub_folder)
            if os.path.isdir(sub_folder_path):
                folders.append(sub_folder_path)
    return folders

def dir_loop_decorate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        root = os.getcwd()
        klasses = iter_dir(kwargs["main_dir"])
        for klass in klasses:
            for filename in os.listdir(klass):
                if validate_extension(filename):
                    path = os.path.join(klass, filename)
                    if func.__name__ == "audio_to_chunks":
                        kwargs["input_path"] = path
                        kwargs["output_path"] = None
                        func(*args, **kwargs)
                    if func.__name__ == "mp3_to_wav":
                        kwargs["input_path"] = path
                        func(*args, **kwargs)
                        full_list[klass] = temp
                    if func.__name__ == "check_inf_amplitude":
                        kwargs["input_path"] = path
                        func(*args, **kwargs)
                    if func.__name__ == "remove_silence_from_audio":
                        kwargs["input_path"] = path
                        func(*args, **kwargs)
                    if func.__name__ == "convert_to":
                        kwargs["input_path"] = path
                        func(*args, **kwargs)
    return wrapper

def audio_to_chunks(*args, **kwargs):
    temp = {"output_path": None, "input_path": None}
    if not kwargs["output_path"]:
        temp["output_path"] = os.path.dirname(kwargs["input_path"])
        temp["input_path"] = kwargs["input_path"]
    else:
        temp["output_path"] = kwargs["output_path"]
        temp["input_path"] = kwargs["input_path"]

    audio = preprocess_audio(temp["input_path"])
    name = os.path.basename(temp["input_path"])[:-4]

    # SPLIT SOUND IN 10-SECOND SLICES AND EXPORT
    for i, chunk in enumerate(audio[::10000]):
        with open("{}/{}_{:04d}.wav".format(temp["output_path"], name, i), "wb") as f:
            chunk.export(f, format="wav")


# PREPROCESS THE AUDIO TO THE CORRECT FORMAT
def preprocess_audio(filename):
    if filename.endswith("mp3"):
        mp3_to_wav(filename)
        filename = filename[:-3]
        filename += "wav"
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

def mp3_to_wav(*args, **kwargs):
    output_path = "{}.wav".format(kwargs["input_path"][:-4])
    sound = AudioSegment.from_mp3(kwargs["input_path"])
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

def wav_to_png(*args, **kwargs):
    rate, data = get_wav_info(kwargs["input_path"])
    nfft = 256 # LENGTH OF EACH WINDOW SEGMENT
    fs = 256 # SAMPLING FREQUENCIES
    pxx, freqs, bins, im = plt.specgram(data, nfft, fs)
    plt.axis('off')
    save_spectrogram_as_png(plt, kwargs["input_path"])

def save_spectrogram_as_png(plt, wav_filename):
    # mpl.rcParams["savefig.directory"] = os.chdir(output_path)
    png_filename = "{}.png".format(wav_filename[:-4])
    
    plt.savefig(png_filename,
                frameon='false',
                bbox_inches='tight',
                pad_inches=0)
    plt.gcf().clear()
    plt.close()
    # convert_to_jpg(png_filename)

def convert_to(*args, **kwargs):
    filename = kwargs["input_path"]
    ext= kwargs["ext"]
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    rgb_im.save("{}.{}".format(filename[:-4], ext))
    # if os.path.exists(filename):
    #     os.remove(filename)

# ImageMagick HAS TO BE INSTALLED
def png_to_jpg(*args, **kwargs):
    wd = os.getcwd()
    path = os.path.join(wd, kwargs["main_dir"])
    for klass in os.listdir(path):
        c_klass = os.path.join(path, klass)
        os.chdir(c_klass)
        call(["mogrify", "-format", "jpg", "*.png"])

# USED TO STANDARDIZE VOLUME OF AUDIO CLIP
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

# CHECK FOR SILENT FILES OR dBFS IS -INF
def check_inf_amplitude(*args, **kwargs):
    f = open("silent_files00.txt", "w")
    if kwargs["input_path"].endswith("wav"):
        segment = AudioSegment.from_wav(kwargs["input_path"])
        if segment.dBFS == -float("inf"):
            print(kwargs["input_path"])
            f.write(kwargs["input_path"])

def remove_silent_files(path, ext):
    df = None
    try:
        os.path.isfile("silent_files.tsv")
        df = pd.read_table("silent_files.tsv")
    except:
        return "File Does Not Exists"

    for i, k in zip(df["class"], df["filename"]):
        full_path = os.path.abspath("{}/{}/{}.{}".format(path, i, k, ext))
        try:
            os.remove(full_path)
            print(full_path)
        except FileNotFoundError:
            print("File {} does not exist".format(k))
            continue
    print("Done!")

def generate_labeled_data(filename, ext):
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

def check_beginning_to_ignore(current, check):
    clean_audio = None
    if current[:134] == check:
        clean_audio = current[135:]
    else:
        clean_audio = current
    return clean_audio

def combine_chunks(chunks, ignored_sound):
    combined = None
    if chunks:
        combined = check_beginning_to_ignore(chunks[0], ignored_sound)
        for chunk in chunks[1:]:
            if chunk == ignored_sound:
                continue
            else:
                combined += chunk
        return combined
    else:
        return []

def remove_silence_from_audio(*args, **kwargs):
    ignored_sound = AudioSegment.from_wav(kwargs["to_ignore"])
    sound = kwargs["input_path"]
    ext = kwargs["ext"]
    if "nosilence" in sound:
        return "File already processed!"
    else:
        output = "{}_nosilence.{}".format(sound[:-4], ext)
    if type(sound) is str:
        sound = AudioSegment.from_wav(sound)
        silence_chunks = split_on_silence(
            sound,
            min_silence_len=kwargs["min_silence_len"],
            silence_thresh=kwargs["silence_thresh"],
            keep_silence=kwargs["keep_silence"]
        )
        combined = combine_chunks(silence_chunks, ignored_sound)
        if combined:
            print(kwargs["input_path"])
            if os.path.isfile(output):
                return "File already exist"
            else:
                combined.export(output, format=ext)

    elif type(sound) is AudioSegment:
        silence_chunks = split_on_silence(
            sound,
            min_silence_len=kwargs["min_silence_len"],
            silence_thresh=kwargs["silence_thresh"],
            keep_silence=kwargs["keep_silence"]
        )
        combined = combine_chunks(silence_chunks, ignored_sound)
        if combined:
            print(kwargs["input_path"])
            if os.path.isfile(output):
                return "File already exist"
            else:
                combined.export(output, format=ext)

def combine_small_audio(main_dir):
    for klass in iter_dir(main_dir):
        all_sounds = None
        for fname in os.listdir(klass):
            sound_path = os.path.join(klass, fname)
            if sound_path.endswith("wav"):
                lenght = check_wave_lenght(sound_path)
                if lenght < 10:
                    sound = AudioSegment.from_wav(sound_path)
                    print("{}\t{}".format(fname, lenght))
                    if all_sounds:
                        all_sounds += sound
                    else:
                        all_sounds = sound
        if all_sounds:
            output = "all_{}.wav".format(os.path.basename(klass))
            output = os.path.join(klass, output)
            all_sounds.export(output, format="wav")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--main_dir",
        help="This flag to specify the main audio files directory path"\
        " e.g `/mountdir/data/civilization/`")
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
        type=int,
        default=50,
        help="Set this for `remove_silence_from_audio` command to set a differen "\
        "minimum silece length (in ms)")
    parser.add_argument(
        "--to_ignore",
        help="Set this for `remove_silence_from_audio` command to specify which sound to ignore")
    parser.add_argument(
        "--silence_thresh",
        type=int,
        default=-65,
        help="Set this for `remove_silence_from_audio` command to set silence thresh (in dBFS)")
    parser.add_argument(
        "--keep_silence",
        type=int,
        default=50,
        help="Set this for `remove_silence_from_audio` command to set the amount of "\
        "silence to leave at the beginning and end of the chunks (in ms)")
    parser.add_argument(
        "-e",
        "--extension",
        default="wav",
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
    parser.add_argument(
        "-c",
        "--combine_small_audio",
        action="store_true",
        help="Set this to combine all the small audio files in one class"\
        " to one audio file.")
    parser.add_argument(
        "-l",
        "--list_files_with_silence",
        action="store_true",
        help="This will check for the files that has been already processed and list them into text file.")


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
            temp = []
            for klass in iter_dir(main_dir):
                for filename in os.listdir(klass):
                    p = os.path.join(klass, filename)
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
                            wav_to_png(input_path=filename)

                    # TO CONVERT ONLY AUDIO FILES WITH NO SILENCE
                    # if filename.endswith("nosilence.wav"):
                    #        print(filename)
                    #        wav_to_png(input_path=filename)
        else:
            wav_to_png(input_path=input_path)
        
    if args.slice_audio:
        if main_dir:
            audio_to_chunks_for_all = dir_loop_decorate(audio_to_chunks)
            audio_to_chunks_for_all(main_dir=main_dir, output_path=output_path)
        else:
            audio_to_chunks(input_path, output_path)

    if args.png2jpg:
        if main_dir:
            if platform.system() == "Linux" or platform.system() == "Linux2":
                png_to_jpg(main_dir)
            else:
                convert_to_all = dir_loop_decorate(convert_to)
                convert_to_all(main_dir=main_dir, ext="jpg")
        else:
            convert_to(input_path=input_path, ext="jpg")

    if args.mp32wav:
        if main_dir:
            mp3_to_wav_for_all = dir_loop_decorate(mp3_to_wav)
            mp3_to_wav_for_all(main_dir=main_dir)
        else:
            mp3_to_wav(input_path=input_path)

    if args.check_inf:
        if main_dir:
            check_inf_amplitude_for_all = dir_loop_decorate(check_inf_amplitude)
            check_inf_amplitude_for_all(main_dir=main_dir)
        else:
            check_inf_amplitude(input_path=input_path)

    if args.remove_silent:
        if main_dir:        
            remove_silent_files(main_dir, ext)

    if args.generate_label:
        generate_labeled_data(input_path, ext)

    if args.remove_silence_from_audio:
        if main_dir:
            remove_silence_from_audio_for_all = dir_loop_decorate(remove_silence_from_audio)
            remove_silence_from_audio_for_all(main_dir=main_dir,
                                              ext=ext,
                                              min_silence_len=min_silence_len,
                                              silence_thresh=silence_thresh,
                                              keep_silence=keep_silence,
                                              to_ignore=to_ignore)
        else:
            remove_silence_from_audio(input_path=input_path,
                                      ext=ext,
                                      min_silence_len=min_silence_len,
                                      silence_thresh=silence_thresh,
                                      keep_silence=keep_silence,
                                      to_ignore=to_ignore)
    if args.combine_small_audio:
        if main_dir:
            combine_small_audio(main_dir)

    if args.list_files_with_silence:
        if main_dir:
            full_list = {}
            temp = []
            for klass in iter_dir(main_dir):
                for filename in os.listdir(klass):
                    p = os.path.join(klass, filename)
                    temp.append(p)
                full_list[klass] = temp

            full_list = OrderedDict(sorted(full_list.items(), key=lambda t: t[0]))
            f = open("to_delete_list.txt", "w")
            for key, files_list in full_list.items():
                files_list.sort()
                for index, filename in enumerate(files_list):
                    if files_list[index][:-14] == files_list[index-1][:-14]:
                        f.write("{}\n".format(filename[:-4]))
