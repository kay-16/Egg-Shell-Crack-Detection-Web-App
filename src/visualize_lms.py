import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit as st 

def visualize_npy_spectrogram(audio_data, filename, sr=44100, hop_length=512): 
    name = Path(filename).stem  

    # Create an explicit figure and axis object
    fig, ax = plt.subplots(figsize=(10, 4))

    # Plot onto the specific axis (ax=ax)
    img = librosa.display.specshow(
        audio_data,
        sr=sr,
        hop_length=hop_length,
        x_axis='time',
        y_axis='mel',
        ax=ax
    )
    
    # Pass img directly to colorbar so it knows what data to map
    fig.colorbar(img, format='%+2.0f dB', ax=ax)

    
    ax.set_title(f'Log-Mel Spectrogram: {name}')
    plt.tight_layout()

    # Render directly to Streamlit webapp main page
    st.pyplot(fig)
    plt.close(fig)


    # 1. Load the npy file
    # audio_data = np.load(log_mel_spectrogram, allow_pickle=True)
    # sample_rate = 44100  # 44.1k Hz

    # # 2. Define your target time slot (in seconds)
    # start_time = 0
    # end_time = 0.5

    # # 3. Calculate start and end sample indices
    # start_sample = int(start_time * sample_rate)
    # end_sample = int(end_time * sample_rate)

    # # 4. Extract the specific time slot
    # time_slotted_audio = audio_data[start_sample:end_sample]


# log_mel, sr = convert_audio_to_logmel_npy(r'thesis_models\data\all_data\train\audio_aug\egg2-1-cracked-1-p2-cleaned_gaussian_noise.wav',r'log_mel_outputs\aud_aug.npy')
# visualize_npy_spectrogram(r"thesis_models\data\all_data\train\log-mel_spectrograms\hybrid_aug\egg2-5-uncracked-0-p1-cleaned_gaussian_noise_time_mask.npy", "aud_aug")