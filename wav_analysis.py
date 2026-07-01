import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq

# Load WAV file
filename = "loud.wav"

# Read the WAV file
sample_rate, data = wavfile.read(filename)

# Print audio information
print(f"Sample Rate: {sample_rate} Hz")
print(f"Bit Depth: {data.dtype.itemsize * 8} bits")

# Check if audio is mono or stereo
if len(data.shape) > 1:
    print(f"Channels: {data.shape[1]} (Stereo)")
    data = data[:, 0]  # Take only the first channel
else:
    print("Channels: 1 (Mono)")

# Calculate duration
duration = len(data) / sample_rate
print(f"Duration: {duration:.2f} seconds")

# ==========================================
# Plot and save waveform
# ==========================================
time = np.linspace(0, duration, len(data))

plt.figure(figsize=(12, 4))
plt.plot(time, data)
plt.title("Waveform")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

# Save waveform plot
plt.savefig("plots/waveform.png")
plt.close()

# ==========================================
# Plot and save frequency spectrum
# ==========================================
N = len(data)

# Compute FFT
yf = fft(data)
xf = fftfreq(N, 1 / sample_rate)

plt.figure(figsize=(12, 4))
plt.plot(xf[:N // 2], np.abs(yf[:N // 2]))
plt.title("Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

# Save spectrum plot
plt.savefig("plots/spectrum.png")
plt.close()

print("\nPlots saved successfully!")
print("Waveform: plots/waveform.png")
print("Frequency Spectrum: plots/spectrum.png")