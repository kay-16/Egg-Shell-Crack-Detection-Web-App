import librosa
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def convert_audio_to_logmel_npy(audio_path, npy_output_path):
    # 1. Load the audio file
    # sr=None preserves the original sample rate. 
    # Alternatively, set sr=22050 to resample everything to a standard rate.
    y, sr = librosa.load(audio_path, sr=None)
    
    # 2. Extract Mel Spectrogram
    # n_fft: length of the FFT window
    # hop_length: number of samples between successive frames
    # n_mels: number of Mel bands to generate
    mel_spectrogram = librosa.feature.melspectrogram(
        y=y, 
        sr=sr, 
        n_fft=2048, 
        hop_length=512, 
        n_mels=128
    )

    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
    
    np.save(npy_output_path, log_mel_spectrogram)
    print(f"Successfully saved {npy_output_path} with shape {log_mel_spectrogram.shape}")
    return log_mel_spectrogram, sr
    

def visualize_npy_spectrogram(log_mel_spectrogram, filename, sr=44100, hop_length=512): 
    name = Path(filename).stem  
    plt.figure(figsize=(10, 4))
    
    librosa.display.specshow(
        log_mel_spectrogram, 
        sr=sr, 
        hop_length=hop_length, 
        x_axis='time', 
        y_axis='mel'
    )
    
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-Mel Spectrogram')
    plt.tight_layout()
    plt.savefig(f'{name}.png')
    plt.show()

# log_mel, sr = convert_audio_to_logmel_npy('UNCRACKED/04-10-26/egg39-1-uncracked-0-p4-sv0-cleaned.wav','cleaned_test.npy')
# print(sr)