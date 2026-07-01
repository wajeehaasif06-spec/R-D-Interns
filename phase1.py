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
# DC Offset Removal
dc_offset = np.mean(data_float)
data_dc = data_float - dc_offset
print(f"DC Offset removed: {dc_offset:.4f}")

# FIR Bandpass Filter (300-3400 Hz speech band)
from scipy.signal import firwin, lfilter

nyq = sample_rate / 2
low  = 300  / nyq
high = 3400 / nyq

fir_coeff = firwin(101, [low, high], pass_zero=False, window='hamming')
data_filtered = lfilter(fir_coeff, 1.0, data_dc)
print("FIR bandpass filter applied (300-3400 Hz)")

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