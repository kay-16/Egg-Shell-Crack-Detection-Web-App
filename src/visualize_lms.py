import librosa
import librosa.display
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
    

# In your visualize python file:

def visualize_npy_spectrogram(log_mel_spectrogram, filename, sr=44100, hop_length=512): 
    name = Path(filename).stem  
    
    # Explicitly capture the figure object and axis bounds containers
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Bind specshow directly to the local axis 
    img = librosa.display.specshow(
        log_mel_spectrogram, 
        sr=sr, 
        hop_length=hop_length, 
        x_axis='time', 
        y_axis='mel',
        ax=ax
    )
    
    # Route colorbar and titles through the local objects
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set_title(f'Log-Mel Spectrogram: {name}')
    plt.tight_layout()
        
    # Save the file using the figure object
    fig.savefig(f'{name}.png')
    
    # Return figure object back to app workflow
    return fig
