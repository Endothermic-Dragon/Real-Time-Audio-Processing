import os

with open("./audio_merge.txt", "r") as f:
  files = f.read().split(" ")

os.system(f"sox {' '.join(files[:25])} output0.wav")

for i in range(len(files) // 25):
  os.system(
      f"sox output{i}.wav {' '.join(files[25+i*25 : min(50+i*25, len(files))])} output{i+1}.wav"
  )

print(len(files))
