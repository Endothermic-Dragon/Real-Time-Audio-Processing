import asyncio
import contextlib
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from sys import exit
import os
from skimage.restoration import denoise_wavelet
# import ssqueezepy as ss
# from ssqueezepy import cwt, icwt
# from ssqueezepy.ssqueezing import ssqueeze
# from ssqueezepy.visuals import imshow
import pywt
from time import sleep

async_queue_input = asyncio.Queue()
input_loop = asyncio.get_event_loop()
count = 0
blocksize = 240000
hist = np.empty((8, blocksize))

def callback(indata, outdata, _frame_count, _time_info, status):
  global count, hist
  count += 1
  data = np.ndarray.flatten(indata.copy())
  discrete = pywt.dwt(data, pywt.Wavelet("db38"))  # type: ignore
  # discrete = denoise_wavelet(discrete[0], wavelet="db38", mode="soft")
  data = pywt.idwt(discrete[0], discrete[1], pywt.Wavelet("db38"))  # type: ignore
  # print(data)
  # print(data_rec)
  # print(data_rec.shape)
  # data[data < 0.0005] = 0
  # data[data < 0.009] = 0
  # print(data[data > np.sort(data)[-1000]])
  # print(np.nonzero(data))
  # print(data)
  for s_hist in hist:
    print(data.shape)
    print(s_hist.shape)
    data -= s_hist
    data[data < 0] = 0
  hist[count % 8] = data
  data = np.reshape(data, (data.size, 1))
  outdata[:] = data
  if count == 2000:
    plt.plot(data)
    plt.show()
  input_loop.call_soon_threadsafe(async_queue_input.put_nowait, (indata.copy(), status))

input_stream = sd.Stream(
    callback=callback,
    device=sd.default.device,
    blocksize=blocksize,
    samplerate=48000,
    latency=("low", "low")
)

with input_stream:
  while True:
    sleep(1)

# print(pywt.wavelist(kind='discrete'))
# https://ieeexplore.ieee.org/document/8256514
