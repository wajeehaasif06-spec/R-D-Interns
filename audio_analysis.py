import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------
# Read the WAV file
# -----------------------------
audio_data, sample_rate = sf.read("loud.wav")

# Read file metadata
info = sf.info("loud.wav")

# -----------------------------
# Display Audio Metadata
# -----------------------------
print("Sample Rate:", info.samplerate, "Hz")
print("Shape:", audio_data.shape)
print("Data Type:", audio_data.dtype)

# Display channels
if info.channels == 1:
    print("Channels: Mono")
else:
    print("Channels: Stereo")

# Display file format
print("Format:", info.format)

# Display actual bit depth
if info.subtype.startswith("PCM_"):
    bit_depth = info.subtype.replace("PCM_", "")
    print("Bit Depth:", bit_depth, "bits")
else:
    print("Bit Depth:", info.subtype)

# Calculate duration
duration = len(audio_data) / sample_rate
print("Duration:", duration, "seconds")

# -----------------------------
# Create plots folder if needed
# -----------------------------
os.makedirs("plots", exist_ok=True)

# -----------------------------
# Waveform Visualization
# -----------------------------
time = np.arange(len(audio_data)) / sample_rate

plt.figure(figsize=(12, 4))
plt.plot(time, audio_data)

plt.title("Waveform of Audio Signal")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.savefig("plots/waveform.png")
plt.close()

# -----------------------------
# Frequency Spectrum (FFT)
# -----------------------------
fft_result = np.fft.fft(audio_data)

frequencies = np.fft.fftfreq(len(audio_data), d=1 / sample_rate)

# Keep only positive frequencies
positive_frequencies = frequencies[:len(frequencies) // 2]
positive_magnitude = np.abs(fft_result[:len(fft_result) // 2])

plt.figure(figsize=(12, 4))
plt.plot(positive_frequencies, positive_magnitude)

plt.title("Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.savefig("plots/frequency_spectrum.png")
plt.close()

print("\nWaveform saved to: plots/waveform.png")
print("Frequency Spectrum saved to: plots/frequency_spectrum.png")
print("\nAnalysis completed successfully!")