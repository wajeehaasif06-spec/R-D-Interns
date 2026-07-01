import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

filename = "noisy__Audio.wav"

sample_rate, data = wavfile.read(filename)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Bit Depth   : {data.dtype.itemsize * 8} bits")
print(f"Channels    : {'Mono' if data.ndim == 1 else 'Stereo'}")
print(f"Duration    : {len(data)/sample_rate:.3f} seconds")