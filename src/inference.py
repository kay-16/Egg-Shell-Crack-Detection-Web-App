import tensorflow as tf
import torch
import torch.nn as nn
from torchvision import models

def load_model_h5(model_path):
    return tf.keras.models.load_model(model_path)

def load_model_pth(model_path, architecture="regnet"):
    # since PyToch models usually need the architecture defined first,
    # use simplified placeholder for now, then adjust later based on Mark's archi
    if "regnet" in architecture:
        model = models.regnet_y_800mf()

        # Change last layer to 2 classes (Cracked/Intact)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 2)

    model.load_state_dict(torch.load(model_path, map_location=torch.edvice('cpu')))
    model.eval()
    return model