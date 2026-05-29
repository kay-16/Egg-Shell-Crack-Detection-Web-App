import librosa
import numpy as np 
from PIL import Image
import cv2
import torch

def prepare_audio(audio_file, target_sr=44100, target_size=(224, 224)):
    # Load audio with the specific sample rate
    y, sr = librosa.load(audio_file, sr=target_sr)

    # Generate Mel Spectogram
    # Using 128 mel bins (standard); will resize to 224 later
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)

    # Convert to Log Scale (decibels)
    S_db = librosa.power_to_db(S, ref=np.max)

    # Resize log mel spectrogram
    log_mel = cv2.resize(S_db, (224, 224), interpolation=cv2.INTER_LINEAR)

    spec_tensor = torch.from_numpy(log_mel).float()
    spec_rgb = spec_tensor.repeat(3, 1, 1)

    return spec_rgb.unsqueeze(0), log_mel




    # Convert to "Image" format (0-255) for resizing
    # rescale to use PIL resize, then Models ni Mark
    # img = Image.fromarray(S_db).convert('RGB')
    # img = img.resize(target_size, Image.Resampling.LANCZOS)

    # # Convert back to Numpy array
    # # Shape will be (224, 224, 3)
    # img_array = np.array(img).astype(np.float32)

    # return img_array

