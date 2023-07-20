from time import time_ns
import numpy as np
import pywt
import sounddevice as sd

rate = 48000
blocksize = 2400

wavelet_data = []

xor_keys = np.array([])
curr_key_idx = 0

time_stats = []


def run(chaos_keys):
  global xor_keys
  xor_keys = np.array(chaos_keys)
  input_stream = sd.InputStream(
      callback=callback,
      device=sd.default.device,
      channels=1,
      blocksize=blocksize,
      samplerate=rate,
      latency="low",
      dtype=np.float32
  )

  with input_stream:
    print("Input started, press enter to exit.")
    input()
    save()


def callback(indata, _frame_count, _time_info, _status):
  start = time_ns()
  new_data = pywt.dwt(indata, pywt.Wavelet("db1"))[0]  # type: ignore

  new_data = byte_xor(np.ndarray.tobytes(new_data), np.ndarray.tobytes(wrap_keys()))
  new_data = new_data.replace(b"\x00", b"\x00\x01")
  wavelet_data.append(new_data)

  time_stats.append(time_ns() - start)


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


def save():
  bin_str = b"\x00\x00".join(wavelet_data)
  with open("./output.bin", "wb") as f:
    f.write(bin_str)
  print(np.average(time_stats))
  print(np.std(time_stats))
