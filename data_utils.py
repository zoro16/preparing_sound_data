import os
import argparse
from scipy.io import wavfile
from pydub import AudioSegment
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
    # Set frame rate to 16000
    segment = segment.set_frame_rate(16000)
    # segment = segment.set_channels(1)

    return segment

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
    nchannels = data.ndim
    pxx, freqs, bins, im = plt.specgram(data, nfft, fs)
    plt.axis('off')
    save_spectrogram_as_jpg(plt, filename)    

def save_spectrogram_as_jpg(plt, wav_filename):
    _, tail = os.path.split(wav_filename)
    png_filename = "{}.png".format(tail[:-4])
    plt.savefig(png_filename,
                dpi=100,  # Dots per inch
                frameon='false',
                aspect='normal',
                bbox_inches='tight',
                pad_inches=0)

    # convert_to_jpg(png_filename)

def convert_to_jpg(filename):
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    rgb_im.save("{}.jpg".format(filename[:-4]))
    if os.path.exists(filename):
        os.remove(filename)

# Load a wav file
def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

# Used to standardize volume of audio clip
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path",
                        help="Set this flag to specfiy the input path")
    parser.add_argument("--output_path",
                        help="Set this flag to specfiy the output path")
    parser.add_argument("--chunks",
                        help="Set this flag if you want to make chunks of waves",
                        action="store_true")
    parser.add_argument("--spectrogram",
                        help="Set this flags  to create spectrograms",
                        action="store_true",
                        default=True)
    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    if args.chunks:
        print("start slicing audio files")
        audio_to_chunks(input_path, output_path)
        print("Done slicing")
    if args.spectrogram:
        wav_to_jpg(input_path)
