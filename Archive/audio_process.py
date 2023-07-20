import numpy as np
from scipy.io import wavfile
from skimage.restoration import denoise_wavelet
import pywt

rate = 48000
blocksize = 2400

wav_rate, audio_data = wavfile.read("input_earbuds.wav")
if len(audio_data.shape) == 1:
  audio_data = np.reshape(audio_data, (audio_data.shape[0], 1))
channels = audio_data.shape[1]

# audio_data_old = audio_data

w_audio = pywt.dwt(audio_data, pywt.Wavelet("db38"))  # type: ignore

# avg = np.average(w_audio[0], axis=1)
# avg = avg.reshape(avg.shape[0], 1)
# std = np.std(w_audio[0], axis=1)
# std = std.reshape(std.shape[0], 1)
# w_audio[0][w_audio[0] < avg - std * 3] = 0

# bound = 0.005
# vec = np.power(w_audio[0][np.abs(w_audio[0]) < bound], 2)
# vec /= np.linalg.norm(vec)*1.5
# w_audio[0][np.abs(w_audio[0]) < bound] = w_audio[0][np.abs(w_audio[0]) < bound]*vec
# print(w_audio[1])

print(np.sort(w_audio[0], axis=0).shape)
w_audio[0][w_audio[0] < np.sort(w_audio[0], axis=0)[-50000]] = 0
w_audio[1][w_audio[1] < np.sort(w_audio[1], axis=0)[-100000]] = 0

audio_data = pywt.idwt(w_audio[0], w_audio[1], pywt.Wavelet("db38"))  # type: ignore
audio_data = np.average(
    audio_data, axis=1
).reshape((audio_data.shape[0], 1)).astype(np.float32)

# print(audio_data.dtype)
# print(audio_data.shape)
# print(audio_data[0:10, :])

# print(np.sum(np.abs(audio_data_old - audio_data)))

wavfile.write("output.wav", rate, audio_data)
