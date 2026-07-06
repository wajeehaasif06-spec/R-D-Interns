import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os
import pycodec2


print("="*50)
print("PHASE 2: BUFFERED REAL-TIME CODEC2")
print("="*50)

# =====================================================
# PATHS
# =====================================================
# NOTE: codec_input.wav is already downsampled to 8kHz by phase2.py
# decoded_realtime.wav is read back and upsampled to 48kHz by phase2.py
# This script only needs to run Codec2 encode/decode at 8kHz.

input_wav = "recordings/codec_input.wav"
decoded_wav = "recordings/decoded_realtime.wav"

os.makedirs("codec", exist_ok=True)
os.makedirs("analysis", exist_ok=True)

# =====================================================
# LOAD 8kHz INPUT AUDIO
# =====================================================

sample_rate, data = wavfile.read(input_wav)

if sample_rate != 8000:
    print(f"WARNING: expected 8000 Hz input, got {sample_rate} Hz")

codec = pycodec2.Codec2(1600)
FRAME_SIZE = codec.samples_per_frame()
FRAME_DURATION = FRAME_SIZE / sample_rate
print(f"Frame size: {FRAME_SIZE}")

data = data.astype(np.int16)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Total Samples : {len(data)}")

# =====================================================
# CREATE 20 ms BUFFERS
# =====================================================

print("\nCreating 20 ms buffers...")

frames = [
    data[i:i+FRAME_SIZE]
    for i in range(0, len(data) - FRAME_SIZE + 1, FRAME_SIZE)
]

print(f"Frame duration : {FRAME_DURATION*1000:.0f} ms")
print(f"Frame size     : {FRAME_SIZE} samples")
print(f"Total frames   : {len(frames)}")

# =====================================================
# CODEC2 ENCODE
# =====================================================
print("\nEncoding using pycodec2...")

encoded_frames = []
for frame in frames:
    encoded = codec.encode(frame)
    encoded_frames.append(encoded)

print(f"Frames encoded: {len(encoded_frames)}")

# =====================================================
# CODEC2 DECODE (stays at 8kHz — phase2.py upsamples afterward)
# =====================================================
print("\nDecoding...")

decoded = []
for frame in encoded_frames:
    decoded_frame = codec.decode(frame)
    decoded.extend(decoded_frame)

decoded = np.array(decoded, dtype=np.int16)

wavfile.write(decoded_wav, sample_rate, decoded)
print(f"Decoded 8kHz WAV saved: {decoded_wav}")

# =====================================================
# COMPRESSION RATIO
# =====================================================

original_size = len(data) * 2

encoded_size = (
    len(encoded_frames)
    * codec.bits_per_frame()
    / 8
)

compression_ratio = original_size / encoded_size

print("\nCompression Results")
print("-------------------")
print(f"Original size : {original_size} bytes")
print(f"Encoded size : {encoded_size:.0f} bytes")
print(f"Compression ratio : {compression_ratio:.2f}:1")

# =====================================================
# SNR
# =====================================================

min_len = min(len(data), len(decoded))

original = data[:min_len].astype(np.float32)
decoded_cmp = decoded[:min_len].astype(np.float32)

signal_power = np.mean(original**2)
noise_power = np.mean((original - decoded_cmp)**2)

snr = 10 * np.log10(signal_power / (noise_power + 1e-10))

print(f"SNR : {snr:.2f} dB")
print(f"Codec bitrate : 3200 bps")
print(f"Buffer latency : {FRAME_DURATION*1000:.0f} ms")

# =====================================================
# DECODED WAVEFORM
# =====================================================

time = np.arange(len(decoded)) / sample_rate

plt.figure(figsize=(12, 4))
plt.plot(time, decoded, linewidth=0.5)
plt.title("Decoded Waveform (8kHz)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.savefig("analysis/decoded_waveform.png", dpi=150)
plt.close()

# =====================================================
# DECODED SPECTRUM
# =====================================================

N = len(decoded)
yf = np.fft.fft(decoded)
xf = np.fft.fftfreq(N, 1/sample_rate)

plt.figure(figsize=(12, 4))
plt.plot(xf[:N//2], np.abs(yf[:N//2]), linewidth=0.5)
plt.title("Decoded Spectrum (8kHz)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.savefig("analysis/decoded_spectrum.png", dpi=150)
plt.close()

# =====================================================
# ERROR SIGNAL
# =====================================================

error = original - decoded_cmp
time_err = np.arange(len(error)) / sample_rate

plt.figure(figsize=(12, 4))
plt.plot(time_err, error, linewidth=0.5)
plt.title("Error Signal (8kHz)")
plt.xlabel("Time (s)")
plt.ylabel("Error")
plt.grid(True)
plt.savefig("analysis/error_signal.png", dpi=150)
plt.close()

print("\nAnalysis plots created")

print("\nGenerated files:")
print("----------------")
print(decoded_wav)
print("analysis/decoded_waveform.png")
print("analysis/decoded_spectrum.png")
print("analysis/error_signal.png")