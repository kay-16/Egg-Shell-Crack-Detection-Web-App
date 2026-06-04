import numpy as np
import soundfile as sf
# import librosa
from scipy.signal import butter, filtfilt
# WAVE_OUTPUT_FILENAME = "test5.wav"

def highpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high')
    return filtfilt(b, a, data)

def run_filtering(input_file, output_file, cutoff=1500):
    try:
        source = input_file
        audio, sr = sf.read(source)
        filtered = highpass_filter(audio, cutoff, sr)
        sf.write(output_file, filtered, sr)
        print(f"Filtered audio saved to {output_file}.")
    except Exception as e:
        print(f"✗ Unexpected error in filtering: {e}. Source: {source}.")

# run_filtering(WAVE_OUTPUT_FILENAME, "cleaned5.wav")
