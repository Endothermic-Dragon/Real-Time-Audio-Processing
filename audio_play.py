from time import time_ns, sleep
import numpy as np
import sounddevice as sd
import pywt
import socket

# Control program functions
stream = True
save_time_data = True

# Program variables
rate = 48000
blocksize = 2400
curr_key_idx = 0
frames = 0

xor_keys = np.array([])
streamed_data = []
audio_data = np.array([])
time_stats = []

if stream:
  user_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  addr = ('127.0.0.1', 8080)
  user_1.bind(addr)
  user_1.listen()
  user_1_conn, addr = user_1.accept()
  user_1_conn.settimeout(1)

  num_packets = int.from_bytes(user_1_conn.recv(2))
  extra = int.from_bytes(user_1_conn.recv(2))

async def run(chaos_keys):
  global xor_keys
  xor_keys = np.array(chaos_keys)

  if not stream:
    with open("./output/output.bin", "rb") as f:
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
      dtype=np.int32
  )

  with output_stream:
    print("Output started")
    input()
    forceTimeStats()

def callback(outdata, _frame_count, _time_info, _status):
  start = time_ns()

  if stream:
    enc_data, start = capture()
  else:
    if len(streamed_data) == 0:
      outdata[:] = 0
      return

    enc_data = streamed_data.pop(0)
  bin_data = byte_xor(enc_data, np.ndarray.tobytes(wrap_keys()))
  wavelet_data = np.frombuffer(bin_data, dtype=np.int32, count=-1)
  wavelet_data = np.reshape(wavelet_data, (blocksize, 1))
  audio_data = pywt.idwt(wavelet_data, None, pywt.Wavelet("db1"))  # type: ignore
  # Convert to int64 to not overflow
  audio_data = np.average(audio_data.astype(np.int64), axis=1)
  # Convert back to int32
  audio_data = audio_data.reshape((blocksize, 1)).astype(np.int32)

  # Stream padded data
  outdata[:] = 0#audio_data

  if not stream and len(streamed_data) == 0:
    print(np.average(time_stats))
    print(np.std(time_stats))
  time_stats.append(time_ns() - start)

# Wrapped chaos keys, returns size of one block
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

def capture():
  try:
    data = b""
    for _ in range(num_packets - 1):
      data += user_1_conn.recv(1024)
    data += user_1_conn.recv(extra)
    timestamp = int.from_bytes(user_1_conn.recv(16))
    return data, timestamp
  except Exception as e:  #BrokenPipeError or ValueError:
    forceTimeStats()
    import sys
    sys.exit()

def forceTimeStats():
  print(np.average(time_stats))
  print(np.std(time_stats))
  if save_time_data:
    np.save("./output/time_data.npy", time_stats, allow_pickle=False)
