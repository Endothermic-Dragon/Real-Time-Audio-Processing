import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd
from diffie_hellman import DiffieHellman

# Chaos-based pseudorandom number generation
# See https://doi.org/10.3390/electronics9010104

# Implementation of "Modified Robust Logistic Map"
class ChaosKeys:

  def __init__(self, min_key_length, max_key_length, mod, secret1, secret2, secret3):
    self.key_gen = DiffieHellman()

    # Decide on gamma and find etas
    self.gamma = 31 - 27 * secret1 / mod
    self.eta1 = 0.5 - np.sqrt(0.25 - np.floor(self.gamma / 4) / self.gamma)
    self.eta2 = 0.5 + np.sqrt(0.25 - np.floor(self.gamma / 4) / self.gamma)

    # Decide on x
    self.x = secret2 / mod
    self.keys = []

    # Decide on key list length
    if min_key_length != max_key_length:
      self.key_length = min_key_length + secret3 % (max_key_length - min_key_length)
    else:
      self.key_length = min_key_length

  # Use chaos maps to generate keys
  # Read into research article (at the top) for more info
  def generage_keys(self):
    bytestream = []
    bitcount = 8

    # Slightly modified to output bytes instead of bits
    while len(bytestream) < self.key_length:
      if self.eta1 <= self.x <= self.eta2:
        self.x = (self.gamma * self.x * (1 - self.x) % 1) / (self.gamma / 4 % 1)
      else:
        self.x = self.gamma * self.x * (1 - self.x) % 1
      if 0.1 <= self.x <= 0.6:
        bit = 1 if self.x * 10**10 % 1 > 0.5 else 0
        if bitcount < 8:
          bitcount += 1
          bytestream[-1] = bytestream[-1] * 2 + bit
        else:
          bitcount = 1
          bytestream.append(bit)

    self.keys = bytestream
    return self.keys

  # Plot key values
  def plot_keys(self):
    plt.plot(self.keys, "o")
    plt.xlabel("Keys Index")
    plt.ylabel("Key Value")
    plt.show()
