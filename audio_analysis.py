import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

# Read the WAV file
audio_data, sample_rate = sf.read("loud.wav")

# Estimate bit depth from data type
if audio_data.dtype == "float64":
    bit_depth = 64
elif audio_data.dtype == "float32":
    bit_depth = 32
elif audio_data.dtype == "int16":
    bit_depth = 16
elif audio_data.dtype == "int32":
    bit_depth = 32
else:
    bit_depth = "Unknown"

print("Bit Depth:", bit_depth, "bits")

# Print basic information
print("Sample Rate:", sample_rate)
print("Shape:", audio_data.shape)
print("Data Type:", audio_data.dtype)

# Check if the audio is mono or stereo
if len(audio_data.shape) == 1:
    print("Channels: Mono")
else:
    print("Channels:", audio_data.shape[1])

# Calculate duration
duration = len(audio_data) / sample_rate
print("Duration:", duration, "seconds")
# Create a time axis
time = np.arange(len(audio_data)) / sample_rate

# Plot the waveform
plt.figure(figsize=(12, 4))
plt.plot(time, audio_data)

plt.title("Waveform of Audio Signal")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

# Save the waveform image
plt.savefig("plots/waveform.png")

# Display the graph
plt.show()
# Compute the Fast Fourier Transform (FFT)
fft_result = np.fft.fft(audio_data)

# Compute frequency values
frequencies = np.fft.fftfreq(len(audio_data), d=1/sample_rate)

# Keep only positive frequencies
positive_frequencies = frequencies[:len(frequencies)//2]
positive_magnitude = np.abs(fft_result[:len(fft_result)//2])

# Plot frequency spectrum
plt.figure(figsize=(12, 4))
plt.plot(positive_frequencies, positive_magnitude)

plt.title("Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

# Save the plot
plt.savefig("plots/frequency_spectrum.png")

# Optional in WSL
# plt.show()