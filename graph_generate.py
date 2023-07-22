import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt

with open("spectrogram_before.txt", "r") as f:
  data = f.read().split("\n")[:-1]
  data = [row.split(", ") for row in data]
  data = [[float(datum) for datum in row] for row in data]
  data = np.array(data)

data *= 50
limits = [np.min(data), np.max(data)]
print(data)
plt.imshow(data, extent=[0, data.shape[0], limits[0], limits[1]], interpolation="none")
plt.show()

with open("spectrogram_after.txt", "r") as f:
  data = f.read().split("\n")[:-1]
  data = [row.split(", ") for row in data]
  data = [[float(datum) for datum in row] for row in data]
  data = np.array(data)

data *= 25
limits = [np.min(data), np.max(data)]
print(data)

fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(data, extent=[0, data.shape[0], limits[0], limits[1]], interpolation="none")
# ax.set_aspect()
plt.show()