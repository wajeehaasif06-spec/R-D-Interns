import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os

filename = "noisy__Audio.wav"

sample_rate, data = wavfile.read(filename)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Bit Depth   : {data.dtype.itemsize * 8} bits")
print(f"Channels    : {'Mono' if data.ndim == 1 else 'Stereo'}")
print(f"Duration    : {len(data)/sample_rate:.3f} seconds")

os.makedirs("plots", exist_ok=True)

data_float = data.astype(np.float32)
time = np.linspace(0, len(data_float)/sample_rate, len(data_float))

# Waveform
plt.figure(figsize=(12, 4))
plt.plot(time, data_float, color='steelblue', linewidth=0.5)
plt.title("Original Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.savefig("plots/original_waveform.png", dpi=150)
plt.close()

# Spectrum
N = len(data_float)
yf = np.fft.fft(data_float)
xf = np.fft.fftfreq(N, 1/sample_rate)
plt.figure(figsize=(12, 4))
plt.plot(xf[:N//2], np.abs(yf[:N//2]), color='steelblue', linewidth=0.5)
plt.title("Original Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.savefig("plots/original_spectrum.png", dpi=150)
plt.close()

print("Plots saved in plots/ folder!")