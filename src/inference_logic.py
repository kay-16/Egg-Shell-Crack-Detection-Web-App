import torch
import torch.nn as nn
from torchvision import models, transforms
import librosa
import numpy as np

def get_model(model_name, num_classes=2, pretrained=True):
    # 'DEFAULT' fetches the best available weights (IMAGENET1K_V1 or V2)
    weights = 'DEFAULT' if pretrained else None
        
    if model_name == 'mobilenet_v2':
        model = models.mobilenet_v2(weights=weights)
        # MobileNetV2 classifier: (0): Dropout, (1): Linear
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    
    elif model_name == 'mobilenet_v3':
        # FIX: Must specify 'large' or 'small'. Defaulting to large.
        model = models.mobilenet_v3_large(weights=weights)
        # FIX: MobileNetV3 classifier is: Linear -> Hardswish -> Dropout -> Linear
        # The final layer is at index 3 (or -1)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)

    elif model_name == 'shufflenet_v2':
        model = models.shufflenet_v2_x1_0(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        
    elif model_name == 'efficientnet_b0':
        model = models.efficientnet_b0(weights=weights)
        # EfficientNet classifier: (0): Dropout, (1): Linear
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

    elif model_name == 'regnet_y':
        model = models.regnet_y_800mf(weights=weights)
        # FIX: RegNet uses 'fc', not 'classifier'
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        
    else:
        raise ValueError(f"Model {model_name} not supported.")
        
    return model

def preprocess_audio(audio_file):
    # Load audio
    y, sr = librosa.load(audio_file, sr=44100)

    # Extract Mel Spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=1024,
        hop_length=512,
        n_mels=128
    )

    # Convert to Log Scate (Decibels)
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

    # Convert to Tensor
    spec_tensor = torch.from_numpy(log_mel_spectrogram).float()

    if spec_tensor.ndim == 2:
        spec_tensor = spec_tensor.unsqueeze(0)
    spec_rgb = spec_tensor.repeat(3, 1, 1)

    # Apply Official Transformation Pipline (Resize + IamgeNet Normalisation)
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Add batch dimenstion
    model_input = transform(spec_rgb).unsqueeze(0)

    # Return Both the model tensor and the raw log-mel numpy array for the plot
    return model_input, log_mel_spectrogram


def get_prediction(model_path, audio_data, model_name):
    # 1. Build the skeleton exactly like Mark's
    model = get_model(model_name, num_classes=1)
    
    # 2. Load the weights
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
    # 3. Predict
    with torch.no_grad():
        # Models expect 3 channels (RGB)
        # if audio_data.shape[1] == 1:
        #     audio_data = audio_data.repeat(1, 3, 1, 1)
            
        outputs = model(audio_data)
        
        # Mark's specific logic: Sigmoid -> Squeeze -> Threshold
        probs = torch.sigmoid(outputs.squeeze())
        
        # If probs is a 0-dim tensor (single value), .item() gets the float
        # prob_val = probs.item() if probs.dim() == 0 else probs[0].item()
        prob_val = (probs >= 0.5).long()
        
        # 1 is Cracked, 0 is Intact
        return "CRACKED" if prob_val == 1 else "UNCRACKED"
        # return probs
