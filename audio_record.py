from time import time_ns, sleep
import numpy as np
import pywt
import sounddevice as sd
import socket
from scipy.io import wavfile
import sys

# Control program functions
streamed = True
mic_input = False
spectrogram = False
num_frames = 90 * 20
wav_file = "./output/merged-audio.wav"

# Program variables
rate = 48000
blocksize = 2400
curr_key_idx = 0
frames = 0

enc_bin = b""
time_stats = []

xor_keys = np.array([])
before = np.array([])
mid = np.array([])
after = np.array([])

# Streaming variables
packet_size = 1024
# 4 bytes per data point, using float32
num_packet = (blocksize * 4 - 1) // packet_size + 1

# Read audio file
if not mic_input:
  wav_rate, file_audio_data = wavfile.read(wav_file)

  if len(file_audio_data.shape) == 2:
    file_audio_data = np.average(file_audio_data, axis=1)
  file_audio_data = np.reshape(file_audio_data, (file_audio_data.shape[0], 1))

  match file_audio_data.dtype:
    case np.float32:
      file_audio_data = np.array(file_audio_data * 2147483647, dtype=np.int32)
    case np.int16:
      file_audio_data = np.array(file_audio_data * 65538, dtype=np.int32)
    case np.uint8:
      file_audio_data = np.array(file_audio_data * 16777216 - 2147483648, dtype=np.int32)

# If streaming, set up connections
if streamed:
  user_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  addr = ("127.0.0.1", 8080)
  user_2.connect(addr)

  # Send basic data across
  user_2.sendall(num_packet.to_bytes(2))

  # 4 bytes per data point, using float32
  user_2.sendall((blocksize * 4 % packet_size).to_bytes(2))

async def run(chaos_keys):
  global xor_keys
  xor_keys = np.array(chaos_keys, dtype=np.uint8)
  input_stream = sd.InputStream(
      callback=callback,
      device=sd.default.device,
      channels=1,
      blocksize=blocksize,
      samplerate=rate,
      latency="low",
      dtype=np.int32
  )

  with input_stream:
    print("Input started, press enter to exit.")
    input()
    if not streamed:
      save()

def callback(indata, _frame_count, _time_info, _status):
  global file_audio_data, enc_bin, frames, before, mid, after

  # Start timestamp
  start = time_ns()

  if mic_input:
    raw_data = indata
  else:
    # "Pad" WAV file to ensure everything doesn't crash
    raw_data = np.zeros_like(indata)
    raw_data[:min(file_audio_data.shape[0], blocksize)] = file_audio_data[:blocksize]

    # If end of audio file, exit
    if file_audio_data.size == 0:
      print(np.average(time_stats))
      print(np.std(time_stats))
      exit()

    # Remove streamed data from array
    file_audio_data = file_audio_data[blocksize:]

  # DWT audio
  audio_dwt = pywt.dwt(raw_data, pywt.Wavelet("db1"))[0]  # type: ignore

  # Ensure in int32
  audio_dwt = np.array(audio_dwt, dtype=np.int32)
  wrapped_keys = wrap_keys()
  a = np.ndarray.tobytes(audio_dwt)
  audio_enc = byte_xor(a, wrapped_keys)

  # Generating spectrogram
  if spectrogram:
    # Before encryption
    before = audio_dwt.T if frames == 0 else np.vstack((before, audio_dwt.T))

    # After encryption, before decryption
    int32_arr = np.frombuffer(audio_enc, dtype=np.int32)
    mid = int32_arr if frames == 0 else np.vstack((mid, int32_arr))

    # After decryption
    int32_arr = byte_xor(audio_enc, wrapped_keys)
    int32_arr = np.frombuffer(int32_arr, dtype=np.int32)
    after = int32_arr if frames == 0 else np.vstack((after, int32_arr))
  # Exit when enough data (timestamps or spectrograms)
  if frames >= num_frames:
    # Save spectrograms
    if spectrogram:
      np.save("./output/spectrogram_before.npy", before, allow_pickle=False)
      np.save("./output/spectrogram_mid.npy", mid, allow_pickle=False)
      np.save("./output/spectrogram_after.npy", after, allow_pickle=False)
    print(np.average(time_stats))
    print(np.std(time_stats))
    np.save("./output/temp.npy", time_stats, allow_pickle=False)
    sys.exit()

  frames += 1

  # Stream or save
  if streamed:
    stream(audio_enc, start)
  else:
    enc_bin += audio_enc.replace(b"\x00", b"\x00\x01") + b"\x00\x00"
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

# XOR two bytes strings
def byte_xor(ba1, ba2):
  int1 = int.from_bytes(ba1)
  int2 = int.from_bytes(ba2)
  return (int1 ^ int2).to_bytes(blocksize * 4)

# Save binary file when not streaming
def save():
  with open("./output/output.bin", "wb") as f:
    f.write(enc_bin)
  print(np.average(time_stats))
  print(np.std(time_stats))

# Stream to localhost port
def stream(data, timestamp):
  try:
    # Simulate latency
    sleep(0.075)

    # Actual data
    for i in range(num_packet - 1):
      user_2.sendall(data[packet_size * i:packet_size * (i + 1)])
    user_2.sendall(data[packet_size * (num_packet - 1):])

    # Associated start timestamp
    user_2.sendall(timestamp.to_bytes(16))

  # Relatively clean exit if program fails
  except BrokenPipeError as e:
    # FIX ERROR TYPE
    raise ValueError("Unable to connect") from e
