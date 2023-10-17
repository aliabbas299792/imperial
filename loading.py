from common import CLEAN_DATASET_PATH, NOISY_DATASET_PATH
import numpy as np

def rot180(array: np.array) -> np.array:
  return np.rot90(np.rot90(array))

def splitRoomWifiData(array: np.array) -> np.array:
  # assumes each row is structured as such:
  # [s1, s2, s3, s4, s5, s6, s7, roomNum] where
  grouped = {}
  for d in array:
    label = int(d[7])
    if not label in grouped:
      grouped[label] = []
    grouped[label].append(d[:7])

  for g in grouped:
    grouped[g] = np.array(grouped[g])
  return grouped

def loadData():
  clean = np.loadtxt(CLEAN_DATASET_PATH)
  noisy = np.loadtxt(NOISY_DATASET_PATH)
  return splitRoomWifiData(clean), splitRoomWifiData(noisy)
