from time import time_ns, sleep
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import pywt
import socket
import sys

# Control program functions
stream = True
save_time_data = False

# Program variables
rate = 48000
blocksize = 2400
curr_key_idx = 0
frames = 0

xor_keys = np.array([])
streamed_data = []
audio_data = np.array([])
time_stats = []
wav_data = np.array([])

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
  xor_keys = np.array(chaos_keys, dtype=np.uint8)

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
    wavfile.write("./output/output.wav", 48000, wav_data)
    forceTimeStats()

def callback(outdata, _frame_count, _time_info, _status):
  global wav_data
  start = time_ns()

  if stream:
    enc_data, start = capture()
  else:
    if len(streamed_data) == 0:
      outdata[:] = 0
      return

    enc_data = streamed_data.pop(0)

  bin_data = byte_xor(enc_data, np.ndarray.tobytes(wrap_keys()))
  wavelet_data = np.frombuffer(bin_data, dtype=np.int32)
  wavelet_data = np.reshape(wavelet_data, (blocksize, 1))
  audio_data = pywt.idwt(wavelet_data, None, pywt.Wavelet("db1"))  # type: ignore
  # Convert to int64 to not overflow
  audio_data = np.average(audio_data.astype(np.int64), axis=1)
  # Convert back to int32
  audio_data = audio_data.reshape((blocksize, 1)).astype(np.int32)

  # Stream
  # outdata[:] = audiodata

  # Save to file
  outdata[:] = 0
  wav_data = audio_data.flatten() if wav_data.size == 0 else np.concatenate(
      (wav_data, audio_data.flatten()), axis=0
  )

  if not stream and len(streamed_data) == 0:
    print(np.average(time_stats))
    print(np.std(time_stats))
    wavfile.write("./output/output.wav", 48000, wav_data)
    sys.exit()
  time_stats.append(time_ns() - start)

# Wrapped chaos keys, returns size of one block
def wrap_keys():
  global curr_key_idx
  keys = xor_keys[curr_key_idx:]
  while keys.size < blocksize * 4:
    keys = np.concatenate((keys, xor_keys), 0)
  curr_key_idx += blocksize * 4
  curr_key_idx %= xor_keys.size
  keys = keys[:blocksize * 4]
  return keys

def byte_xor(ba1, ba2):
  int1 = int.from_bytes(ba1)
  int2 = int.from_bytes(ba2)
  return (int1 ^ int2).to_bytes(blocksize * 4)

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
    wavfile.write("./output/output.wav", 48000, wav_data)
    sys.exit()

def forceTimeStats():
  print(np.average(time_stats))
  print(np.std(time_stats))
  if save_time_data:
    np.save("./output/time_data.npy", time_stats, allow_pickle=False)
