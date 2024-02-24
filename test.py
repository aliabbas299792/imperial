import imageio
import os

dir1 = "coursework_02/Task01_BrainTumour_2D/test_labels/"
dir2 = "coursework_02/Task01_BrainTumour_2D/training_labels/"
vals = set()

def get_val_set(dir: str):
  vals = set()
  for f in os.listdir(dir):
    im = imageio.imread(f"{dir}/{f}")
    for y in range(im.shape[0]):
      for x in range(im.shape[1]):
        vals.add(im[y, x])
  return vals
        
print(get_val_set(dir1).union(get_val_set(dir2)))
