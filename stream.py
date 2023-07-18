import asyncio
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from sys import exit
import os
# import ssqueezepy as ss
# from ssqueezepy import cwt, icwt
# from ssqueezepy.ssqueezing import ssqueeze
# from ssqueezepy.visuals import imshow
import pywt


async def audio_read():
  """Generator that yields blocks of input data as NumPy arrays."""
  async_queue_input = asyncio.Queue()
  async_queue_output = asyncio.Queue()
  input_loop = asyncio.get_event_loop()

  def outputCallback(indata, _frame_count, _time_info, status):
    while True:
      try:
        indata[:] = async_queue_output.get_nowait()
      except asyncio.QueueEmpty:
        print(1)

  def inputCallback(indata, _frame_count, _time_info, status):
    input_loop.call_soon_threadsafe(async_queue_input.put_nowait, (indata.copy(), status))

  input_stream = sd.InputStream(
      callback=inputCallback,
      device=sd.default.device,
      channels=1,
      blocksize=4410,
      samplerate=44100,
  )

  output_stream = sd.OutputStream(
      callback=outputCallback,
      device=sd.default.device,
      channels=1,
      blocksize=4410,
      samplerate=44100,
  )

  with input_stream and output_stream:
    while True:
      data, _ = await async_queue_input.get()
      # Vocular’s database
      data = np.ndarray.flatten(data)
      # os.system("clear")
      discrete = pywt.dwt(data, pywt.Wavelet("db38"))  # type: ignore
      data2 = pywt.idwt(discrete[0], discrete[1], pywt.Wavelet("db38"))  # type: ignore
      # print(np.sum(data))
      # print(np.sum(data2))
      # print(np.sum(data2 - data))
      async_queue_output.put_nowait(data2)


asyncio.run(audio_read())
# print(pywt.wavelist(kind='discrete'))
# https://ieeexplore.ieee.org/document/8256514
