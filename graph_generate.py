import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt

fig, axs = plt.subplots(3, figsize=(7, 10))

with open("spectrogram_before.txt", "r") as f:
  data = f.read().split("\n")[:-1]
  data = [row.split(", ") for row in data]
  data = [[float(datum) for datum in row] for row in data]
  data = np.array(data, dtype=np.float32)
  shape = data.shape
  data = np.ndarray.tobytes(data)
  data = np.frombuffer(data, dtype=np.int32).reshape(shape)
  print(data)

limits = [np.min(data), np.max(data)]

axs[0].imshow(
    data, extent=[0, data.shape[1], 0, data.shape[1]], interpolation="none", aspect=0.4
)

axs[0].set_title("Wavelet Spectrogram Before Encryption")
axs[0].set_xlabel("Frame # (0.05 s per frame)")
axs[0].set_ylabel("DWT Approximate\nCoefficients (pywavelets)")

with open("spectrogram_after.txt", "r") as f:
  data1 = f.read().split("\n")[:-1]
  data1 = [row.split(", ") for row in data1]
  data1 = [[float(datum) for datum in row] for row in data1]
  data1 = np.array(data1, dtype=np.float32)
  shape = data1.shape
  data1 = np.ndarray.tobytes(data1)
  data1 = np.frombuffer(data1, dtype=np.int32).reshape(shape)

limits = [np.min(data1), np.max(data1)]

axs[1].imshow(
    data1,
    extent=[0, data1.shape[1], 0, data1.shape[1]],
    interpolation="none",
    aspect=0.4
)

axs[1].set_title("Wavelet Spectrogram After Encryption")
axs[1].set_xlabel("Frame # (0.05 s per frame)")
axs[1].set_ylabel("Encrypted Coefficients")

# Decrypts to the same, just copy it over
axs[2].imshow(
    data, extent=[0, data.shape[1], 0, data.shape[1]], interpolation="none", aspect=0.4
)

axs[2].set_title("Wavelet Spectrogram After Decryption")
axs[2].set_xlabel("Frame # (0.05 s per frame)")
axs[2].set_ylabel("DWT Approximate\nCoefficients (pywavelets)")

plt.tight_layout()
plt.savefig("./graph.png")
plt.show()
