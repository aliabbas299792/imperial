from common import CLEAN_DATASET_PATH, NOISY_DATASET_PATH
import numpy as np

LabelDataTuple = tuple[np.array, np.array]
NoisyCleanTuple = tuple[LabelDataTuple, LabelDataTuple]

def splitRoomWifiData(ldTuple: LabelDataTuple) -> dict:
  """
  Groups the WiFi signal data by the room numbers attached to it
  """

  # assumes each row is structured as such:
  # [s1, s2, s3, s4, s5, s6, s7, roomNum] where
  grouped = {}
  label, data = ldTuple
  for l, d in zip(label, data):
    roomNum = l[0]
    if not roomNum in grouped:
      grouped[roomNum] = []
    grouped[roomNum].append(d)

  for g in grouped:
    grouped[g] = np.array(grouped[g])
  return grouped

def loadRawData() -> tuple[np.array, np.array]:
  """
  Loads the raw data from the text file
  """
  return np.loadtxt(CLEAN_DATASET_PATH), np.loadtxt(NOISY_DATASET_PATH)

def loadSplitData() -> NoisyCleanTuple:
  """
  Splits the datasets into tuples of the label column, and the data columns
  """
  def splitDataset(data: np.array) -> LabelDataTuple:
    """
    Partitions the data as in the comment above
    """
    return (data[:, 7:].astype(int), data[:, :7])

  clean, noisy = loadRawData()
  return splitDataset(clean), splitDataset(noisy)

def groupedData() -> tuple[dict, dict]:
  """
  Groups both datasets by room number
  """
  clean, noisy = loadSplitData()
  return splitRoomWifiData(clean), splitRoomWifiData(noisy)
