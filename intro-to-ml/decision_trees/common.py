import numpy as np
from os import path

WIFI_DB = "Coursework Files/wifi_db"
DEFAULT_CLEAN_DATASET_PATH = path.join(WIFI_DB, "clean_dataset.txt")
DEFAULT_NOISY_DATASET_PATH = path.join(WIFI_DB, "noisy_dataset.txt")

NUM_CROSS_VALIDATION_FOLDS = 10
NUM_ROOMS = 4

def loadRawData(dataset_path: str) -> np.ndarray:
    return np.loadtxt(dataset_path)