import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import subprocess
import os

print("="*50)
print("PHASE 2: BUFFERED REAL-TIME CODEC2")
print("="*50)

# =====================================================
# PARAMETERS
# =====================================================

FRAME_DURATION = 0.02        # 20 ms
FRAME_SIZE = 160             # 160 samples @ 8 kHz

# =====================================================
# PATHS
# =====================================================

input_wav = "recordings/codec_input.wav"

raw_input = "codec/codec_input.raw"
encoded = "codec/encoded.c2"
decoded_raw = "codec/decoded.raw"
decoded_wav = "recordings/decoded_realtime.wav"

os.makedirs("codec", exist_ok=True)
os.makedirs("analysis", exist_ok=True)

# =====================================================
# LOAD INPUT AUDIO
# =====================================================

sample_rate, data = wavfile.read(input_wav)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Total Samples : {len(data)}")

# =====================================================
# CREATE 20 ms BUFFERS
# =====================================================

print("\nCreating 20 ms buffers...")

frames = []

for i in range(0, len(data), FRAME_SIZE):

    frame = data[i:i+FRAME_SIZE]

    if len(frame) == FRAME_SIZE:
        frames.append(frame)

print(f"Frame duration : {FRAME_DURATION*1000:.0f} ms")
print(f"Frame size     : {FRAME_SIZE} samples")
print(f"Total frames   : {len(frames)}")

# =====================================================
# CODEC2 PROCESSING (WHOLE STREAM)
# =====================================================

print("\nProcessing complete audio stream through Codec2...")

# save entire audio as raw PCM
data.astype(np.int16).tofile(raw_input)

print("Raw PCM created")

# encode
print("Encoding with Codec2...")

subprocess.run(
    [
        "c2enc",
        "3200",
        raw_input,
        encoded,
        "--natural"
    ],
    check=True
)

print("Encoding complete")

# decode
print("Decoding with Codec2...")

subprocess.run(
    [
        "c2dec",
        "3200",
        encoded,
        decoded_raw
    ],
    check=True
)

print("Decoding complete")

# reconstruct audio
decoded = np.fromfile(
    decoded_raw,
    dtype=np.int16
)

wavfile.write(
    decoded_wav,
    sample_rate,
    decoded
)

print("Decoded WAV saved")
# =====================================================
# COMPRESSION RATIO
# =====================================================

original_size = len(data)*2

encoded_size = os.path.getsize(
    encoded
)

compression_ratio = (
    original_size / encoded_size
)

print("\nCompression Results")
print("-------------------")
print(f"Original size : {original_size} bytes")
print(f"Encoded frame : {encoded_size} bytes")
print(f"Compression ratio : {compression_ratio:.2f}:1")

# =====================================================
# SNR
# =====================================================

min_len = min(
    len(data),
    len(decoded)
)

original = data[:min_len].astype(np.float32)
decoded = decoded[:min_len].astype(np.float32)

signal_power = np.mean(
    original**2
)

noise_power = np.mean(
    (original-decoded)**2
)

snr = 10*np.log10(
    signal_power /
    (noise_power+1e-10)
)

print(f"SNR : {snr:.2f} dB")

# =====================================================
# DECODED WAVEFORM
# =====================================================

time = np.arange(
    len(decoded)
)/sample_rate

plt.figure(figsize=(12,4))
plt.plot(
    time,
    decoded,
    linewidth=0.5
)
plt.title(
    "Decoded Waveform"
)
plt.xlabel(
    "Time (s)"
)
plt.ylabel(
    "Amplitude"
)
plt.grid(True)
plt.savefig(
    "analysis/decoded_waveform.png",
    dpi=150
)
plt.close()

# =====================================================
# DECODED SPECTRUM
# =====================================================

N = len(decoded)

yf = np.fft.fft(decoded)
xf = np.fft.fftfreq(
    N,
    1/sample_rate
)

plt.figure(figsize=(12,4))
plt.plot(
    xf[:N//2],
    np.abs(yf[:N//2]),
    linewidth=0.5
)
plt.title(
    "Decoded Spectrum"
)
plt.xlabel(
    "Frequency (Hz)"
)
plt.ylabel(
    "Magnitude"
)
plt.grid(True)
plt.savefig(
    "analysis/decoded_spectrum.png",
    dpi=150
)
plt.close()

# =====================================================
# ERROR SIGNAL
# =====================================================

error = original - decoded

time = np.arange(
    len(error)
)/sample_rate

plt.figure(figsize=(12,4))
plt.plot(
    time,
    error,
    linewidth=0.5
)
plt.title(
    "Error Signal"
)
plt.xlabel(
    "Time (s)"
)
plt.ylabel(
    "Error"
)
plt.grid(True)
plt.savefig(
    "analysis/error_signal.png",
    dpi=150
)
plt.close()

print("\nAnalysis plots created")

print("\nGenerated files:")
print("----------------")
print(decoded_wav)
print("analysis/decoded_waveform.png")
print("analysis/decoded_spectrum.png")
print("analysis/error_signal.png")