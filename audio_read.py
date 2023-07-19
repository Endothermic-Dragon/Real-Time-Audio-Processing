import numpy as np
from scipy.io import wavfile
import sounddevice as sd

rate = 48000
blocksize = 2400

res = sd.query_devices(kind="input")
if isinstance(res, sd.DeviceList):
  channels = res[0]["max_input_channels"]
else:
  channels = res["max_input_channels"]  # type: ignore

audio_data = np.array([], dtype=np.float32)
audio_data = np.reshape(audio_data, (0, channels))


def callback(indata, _frame_count, _time_info):
  global audio_data
  audio_data = np.append(audio_data, indata, axis=0)


input_stream = sd.InputStream(
    callback=callback,
    device=sd.default.device,
    channels=channels,
    blocksize=blocksize,
    samplerate=rate,
    latency="low",
    dtype=np.float32
)

with input_stream:
  print("Input started")
  input()
  wavfile.write("output.wav", rate, audio_data)
