from time import time_ns
import numpy as np
import sounddevice as sd
import pywt

blocksize = 2400
rate = 48000

streamed_data = []

xor_keys = np.array([])
curr_key_idx = 0

time_stats = []


def run(chaos_keys):
  global xor_keys
  xor_keys = np.array(chaos_keys)

  with open("output.bin", "rb") as f:
    bin_str = f.read()

  for bin_data in bin_str.split(b"\x00\x00"):
    streamed_data.append(bin_data.replace(b"\x00\x01", b"\x00"))

  output_stream = sd.OutputStream(
      callback=callback,
      device=sd.default.device,
      channels=1,
      blocksize=blocksize,
      samplerate=rate,
      latency="low",
      dtype=np.float32
  )

  with output_stream:
    print("Output started")
    input()


def callback(outdata, _frame_count, _time_info, _status):
  if len(streamed_data) == 0:
    outdata[:] = 0
    return

  start = time_ns()
  enc_data = streamed_data.pop(0)
  bin_data = byte_xor(enc_data, np.ndarray.tobytes(wrap_keys()))
  wavelet_data = np.frombuffer(bin_data, dtype=np.float32, count=-1)
  wavelet_data = np.reshape(wavelet_data, (blocksize, 1))
  audio_data = pywt.idwt(wavelet_data, None, pywt.Wavelet("db1"))  # type: ignore
  audio_data = np.average(audio_data, axis=1)
  audio_data = audio_data.reshape((blocksize, 1)).astype(np.float32)

  # Stream padded data
  outdata[:] = audio_data
  time_stats.append(time_ns() - start)

  if len(streamed_data) == 0:
    print(np.average(time_stats))
    print(np.std(time_stats))


def wrap_keys():
  global curr_key_idx
  keys = np.array([])
  keys = xor_keys[curr_key_idx:]
  while keys.size < blocksize:
    keys = np.append(keys, xor_keys)
  curr_key_idx += blocksize
  curr_key_idx %= xor_keys.size
  return keys[:blocksize]


def byte_xor(ba1, ba2):
  return bytes(_a ^ _b for _a, _b in zip(ba1, ba2))
