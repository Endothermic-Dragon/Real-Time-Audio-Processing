import numpy as np
from scipy.io import wavfile
import sounddevice as sd

blocksize = 2400
rate = 48000

wav_rate, data = wavfile.read("uwu.wav")
channels = data.shape[1]


def callback(outdata, _frame_count, _time_info):
  global data

  # Pad data to fit output format
  pad = np.zeros((blocksize, channels))
  pad[:min(data.shape[0], blocksize), :channels] = data[:blocksize]

  # Stream padded data
  outdata[:] = pad

  # Remove streamed data from array
  data = data[blocksize:]

  # print(outdata.shape)
  # data = np.ndarray.flatten(indata.copy())
  # discrete = pywt.dwt(data, pywt.Wavelet("db38"))  # type: ignore
  # # discrete = denoise_wavelet(discrete[0], wavelet="db38", mode="soft")
  # data = pywt.idwt(discrete[0], discrete[1], pywt.Wavelet("db38"))  # type: ignore
  # print(data)
  # print(data_rec)
  # print(data_rec.shape)
  # data[data < 0.0005] = 0
  # data[data < 0.009] = 0
  # print(data[data > np.sort(data)[-1000]])
  # print(np.nonzero(data))
  # print(data)


output_stream = sd.OutputStream(
    callback=callback,
    device=sd.default.device,
    channels=channels,
    blocksize=blocksize,
    samplerate=rate,
    dtype=data.dtype,
    latency="low"
)

if wav_rate == rate:
  with output_stream:
    print("Output started")
    input()
else:
  print("Incorrect bitrate")
