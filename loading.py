from common import CLEAN_DATASET_PATH, NOISY_DATASET_PATH
import numpy as np

def rot180(array: np.array) -> np.array:
  return np.rot90(np.rot90(array))

def splitRoomWifiData(array: np.array) -> np.array:
  grouped = {}
  for d in array:
    label = int(d[7])
    if not label in grouped:
      grouped[label] = []
    grouped[label].append(d[:7])
  return grouped

def loadData():
  clean = np.loadtxt(CLEAN_DATASET_PATH)
  noisy = np.loadtxt(NOISY_DATASET_PATH)
  return splitRoomWifiData(clean), splitRoomWifiData(noisy)
