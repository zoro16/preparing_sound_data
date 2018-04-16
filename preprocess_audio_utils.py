import matplotlib.pyplot as plt
from scipy.io import wavfile
import os
from pydub import AudioSegment


# Preprocess the audio to the correct format
def preprocess_audio(filename, start, end, iter=1):
    # Trim or pad audio segment to 10000ms
    # padding = AudioSegment.silent(duration=10000)
    segment = AudioSegment.from_wav(filename)[start:end]
    # segment = padding.overlay(segment)
    # Set frame rate to 16000
    segment = segment.set_frame_rate(16000)
    # Export as wav
    segment.export("{}_{:04d}".format(filename, iter), format='wav')


# Calculate and plot spectrogram for a wav audio file
def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    nfft = 200 # Length of each window segment
    fs = 8000 # Sampling frequencies
    noverlap = 120 # Overlap between windows
    nchannels = data.ndim
    if nchannels == 1:
        pxx, freqs, bins, im = plt.specgram(data, nfft, fs, noverlap = noverlap)
    elif nchannels == 2:
        pxx, freqs, bins, im = plt.specgram(data[:,0], nfft, fs, noverlap = noverlap)
    # print("freqs: =>", freqs)
    # print("bins: =>", bins)
    # print("im: =>", im)
    # print("pxx: =>", pxx)
    save_spectrogram_as_png(plt, wav_file)
    return pxx

def save_spectrogram_as_png(plt, wav_filename):
    head, tail = os.path.split(wav_filename)
    output_filename = tail[:-4]
    plt.savefig("{}.png".format(output_filename))

# Load a wav file
def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

# Used to standardize volume of audio clip
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

# Load raw audio files for speech synthesis
def load_raw_audio():
    activates = []
    for filename in os.listdir("./raw_data/activates"):
        if filename.endswith("wav"):
            activate = AudioSegment.from_wav("./raw_data/activates/"+filename)
            activates.append(activate)
    return activates

