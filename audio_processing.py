import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import noisereduce as nr
import os
import subprocess
# ----------------------------------------
# Create Output Folder
# ----------------------------------------

os.makedirs("output", exist_ok=True)

# ----------------------------------------
# Read Audio File
# ----------------------------------------

audio_data, sample_rate = sf.read("noisy_audio.wav")

# Get Audio Information
info = sf.info("noisy_audio.wav")

# ----------------------------------------
# Print Audio Metadata
# ----------------------------------------

print("----- Audio Information -----")
print(f"Sample Rate : {sample_rate} Hz")
print(f"Shape       : {audio_data.shape}")
print(f"Data Type   : {audio_data.dtype}")

if len(audio_data.shape) == 1:
    print("Channels    : Mono")
else:
    print(f"Channels    : Stereo ({audio_data.shape[1]} channels)")

duration = len(audio_data) / sample_rate
print(f"Duration    : {duration:.2f} seconds")

print(f"Bit Depth   : {info.subtype}")

# ----------------------------------------
# Calculate DC Offset
# ----------------------------------------

dc_offset = np.mean(audio_data)

print(f"\nDC Offset : {dc_offset}")

# ----------------------------------------
# Remove DC Offset
# ----------------------------------------

audio_no_dc = audio_data - dc_offset

new_dc_offset = np.mean(audio_no_dc)

print(f"DC Offset After Removal : {new_dc_offset}")

# Save Audio After DC Offset Removal

sf.write(
    "output/audio_no_dc.wav",
    audio_no_dc,
    sample_rate
)

print("Audio after DC Offset removal saved.")

# ----------------------------------------
# Noise Reduction
# ----------------------------------------

reduced_noise = nr.reduce_noise(
    y=audio_no_dc,
    sr=sample_rate
)

print("Background noise reduced successfully.")

# Save Noise Reduced Audio

sf.write(
    "output/audio_noise_reduced.wav",
    reduced_noise,
    sample_rate
)

print("Noise reduced audio saved.")

# ----------------------------------------
# Normalize Audio
# ----------------------------------------

normalized_audio = reduced_noise / np.max(np.abs(reduced_noise))

print("Audio normalized successfully.")

# Save Normalized Audio

sf.write(
    "output/audio_normalized.wav",
    normalized_audio,
    sample_rate
)

print("Normalized audio saved.")

# ----------------------------------------
# Calculate Signal-to-Noise Ratio (SNR)
# ----------------------------------------

signal_power = np.mean(normalized_audio ** 2)

noise = audio_data - normalized_audio

noise_power = np.mean(noise ** 2)

snr = 10 * np.log10(signal_power / noise_power)

print(f"SNR : {snr:.2f} dB")
# ----------------------------------------
# Convert WAV to RAW PCM
# ----------------------------------------

normalized_int16 = (normalized_audio * 32767).astype(np.int16)

raw_file = "output/audio_normalized.raw"

normalized_int16.tofile(raw_file)

print("RAW audio created.")

# ----------------------------------------
# Encode using Codec2
# ----------------------------------------

codec2_file = "output/audio.codec2"

subprocess.run([
    "c2enc",
    "3200",
    raw_file,
    codec2_file
], check=True)

print("Codec2 encoding completed.")

# ----------------------------------------
# Decode using Codec2
# ----------------------------------------

decoded_raw = "output/audio_decoded.raw"

subprocess.run([
    "c2dec",
    "3200",
    codec2_file,
    decoded_raw
], check=True)

print("Codec2 decoding completed.")

# ----------------------------------------
# Convert RAW back to WAV
# ----------------------------------------

decoded_audio = np.fromfile(
    decoded_raw,
    dtype=np.int16
).astype(np.float32)

decoded_audio = decoded_audio / 32767

sf.write(
    "output/audio_decoded.wav",
    decoded_audio,
    sample_rate
)

print("Decoded WAV file saved.")
# ----------------------------------------
# Decoded Audio Waveform
# ----------------------------------------

time = np.arange(len(decoded_audio)) / sample_rate

plt.figure(figsize=(12,4))
plt.plot(time, decoded_audio)
plt.title("Decoded Audio Waveform")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.savefig("output/decoded_waveform.png")
plt.close()

# ----------------------------------------
# Decoded Audio Spectrum
# ----------------------------------------

fft = np.fft.fft(decoded_audio)
frequencies = np.fft.fftfreq(len(decoded_audio), d=1/sample_rate)

positive = frequencies >= 0

plt.figure(figsize=(12,4))
plt.plot(frequencies[positive], np.abs(fft[positive]))
plt.title("Decoded Audio Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.savefig("output/decoded_spectrum.png")
plt.close()

print("Decoded audio graphs saved.")

# ----------------------------------------
# Original Waveform
# ----------------------------------------

time = np.arange(len(audio_data)) / sample_rate

plt.figure(figsize=(12,4))
plt.plot(time, audio_data)

plt.title("Original Audio Waveform")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.savefig("output/original_waveform.png")
plt.close()

# ----------------------------------------
# Original Frequency Spectrum
# ----------------------------------------

fft = np.fft.fft(audio_data)
frequencies = np.fft.fftfreq(len(audio_data), d=1/sample_rate)

positive = frequencies >= 0

plt.figure(figsize=(12,4))
plt.plot(frequencies[positive], np.abs(fft[positive]))

plt.title("Original Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.savefig("output/original_spectrum.png")
plt.close()

# ----------------------------------------
# Noise Reduced Waveform
# ----------------------------------------

time = np.arange(len(reduced_noise)) / sample_rate

plt.figure(figsize=(12,4))
plt.plot(time, reduced_noise)

plt.title("Waveform After Noise Reduction")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.savefig("output/noise_reduced_waveform.png")
plt.close()

# ----------------------------------------
# Noise Reduced Spectrum
# ----------------------------------------

fft = np.fft.fft(reduced_noise)
frequencies = np.fft.fftfreq(len(reduced_noise), d=1/sample_rate)

positive = frequencies >= 0

plt.figure(figsize=(12,4))
plt.plot(frequencies[positive], np.abs(fft[positive]))

plt.title("Spectrum After Noise Reduction")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.savefig("output/noise_reduced_spectrum.png")
plt.close()

# ----------------------------------------
# Normalized Waveform
# ----------------------------------------

time = np.arange(len(normalized_audio)) / sample_rate

plt.figure(figsize=(12,4))
plt.plot(time, normalized_audio)

plt.title("Waveform After Normalization")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.savefig("output/normalized_waveform.png")
plt.close()

# ----------------------------------------
# Normalized Frequency Spectrum
# ----------------------------------------

fft = np.fft.fft(normalized_audio)
frequencies = np.fft.fftfreq(len(normalized_audio), d=1/sample_rate)

positive = frequencies >= 0

plt.figure(figsize=(12,4))
plt.plot(frequencies[positive], np.abs(fft[positive]))

plt.title("Spectrum After Normalization")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.savefig("output/normalized_spectrum.png")
plt.close()

print("\nAll processing completed successfully.")
print("All audio files and graphs are saved in the 'output' folder.")