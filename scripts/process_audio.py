import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os

# ─────────────────────────────────────────
# SETTINGS — tweak these to improve results
# ─────────────────────────────────────────
INPUT_FILE  = "audio/noisy_audio.wav"
OUTPUT_DIR  = "plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────
# STEP 1: Load and analyze the noisy audio
# ─────────────────────────────────────────
samples, sample_rate = sf.read(INPUT_FILE, dtype="float64")

# If stereo, take first channel only
if samples.ndim > 1:
    samples = samples[:, 0]

print("=== Noisy Audio Analysis ===")
print(f"Sample rate   : {sample_rate} Hz")
print(f"Total samples : {len(samples)}")
print(f"Duration      : {len(samples)/sample_rate:.3f} s")
print(f"Max amplitude : {np.max(np.abs(samples)):.4f}")
print(f"DC offset     : {np.mean(samples):.6f}")

# Plot waveform
time = np.arange(len(samples)) / sample_rate
plt.figure(figsize=(12, 4))
plt.plot(time, samples, linewidth=0.5)
plt.title("Waveform — Noisy Input")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/1_noisy_waveform.png", dpi=150)
plt.close()

# Plot frequency spectrum
fft_vals = np.fft.rfft(samples)
freqs    = np.fft.rfftfreq(len(samples), d=1/sample_rate)
mag_db   = 20 * np.log10(np.abs(fft_vals) + 1e-12)
plt.figure(figsize=(12, 4))
plt.plot(freqs, mag_db, linewidth=0.5)
plt.title("Frequency Spectrum — Noisy Input")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/2_noisy_spectrum.png", dpi=150)
plt.close()

print("\nPlots saved to plots/")
print("1_noisy_waveform.png")
print("2_noisy_spectrum.png")





from scipy.signal import butter, lfilter

# ─────────────────────────────────────────
# SETTINGS YOU CAN TWEAK
# ─────────────────────────────────────────
HIGHPASS_CUTOFF = 300    # Hz — frequencies below this are cut (removes rumble/noise)
LOWPASS_CUTOFF  = 3400   # Hz — frequencies above this are cut (removes hiss)
FILTER_ORDER    = 5      # Higher = sharper filter (try 3 to 8)
GAIN            = 1.0    # Increase above 1.0 to amplify, decrease to reduce volume

# ─────────────────────────────────────────
# STEP 2: DC offset removal
# ─────────────────────────────────────────
dc_offset = np.mean(samples)
samples_dc = samples - dc_offset
print(f"\n=== After DC Removal ===")
print(f"DC offset removed : {dc_offset:.6f}")
print(f"New mean          : {np.mean(samples_dc):.8f}")

# ─────────────────────────────────────────
# STEP 3: Bandpass filter (noise suppression)
# removes everything outside 300–3400 Hz
# ─────────────────────────────────────────
nyquist = sample_rate / 2
low  = HIGHPASS_CUTOFF / nyquist
high = LOWPASS_CUTOFF  / nyquist
b, a = butter(FILTER_ORDER, [low, high], btype="band")
samples_filtered = lfilter(b, a, samples_dc)

print(f"\n=== After Bandpass Filter ===")
print(f"Passband          : {HIGHPASS_CUTOFF}–{LOWPASS_CUTOFF} Hz")
print(f"Max amplitude     : {np.max(np.abs(samples_filtered)):.4f}")

# ─────────────────────────────────────────
# STEP 4: Gain + normalization
# ─────────────────────────────────────────
samples_gained = samples_filtered * GAIN
peak = np.max(np.abs(samples_gained))
samples_norm = samples_gained / peak  # normalize to [-1, 1]

print(f"\n=== After Gain + Normalization ===")
print(f"Gain applied      : {GAIN}")
print(f"Peak before norm  : {peak:.4f}")
print(f"Peak after norm   : {np.max(np.abs(samples_norm)):.4f}")

# ─────────────────────────────────────────
# STEP 5: Save processed audio
# ─────────────────────────────────────────
PROCESSED_FILE = "audio/processed_audio.wav"
sf.write(PROCESSED_FILE, samples_norm, sample_rate, subtype="PCM_16")
print(f"\nProcessed audio saved to: {PROCESSED_FILE}")

# ─────────────────────────────────────────
# STEP 6: Plot processed waveform + spectrum
# ─────────────────────────────────────────
plt.figure(figsize=(12, 4))
plt.plot(time, samples_norm, linewidth=0.5)
plt.title("Waveform — After DC Removal + Filter + Normalization")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/3_processed_waveform.png", dpi=150)
plt.close()

fft_proc = np.fft.rfft(samples_norm)
mag_proc_db = 20 * np.log10(np.abs(fft_proc) + 1e-12)
plt.figure(figsize=(12, 4))
plt.plot(freqs, mag_proc_db, linewidth=0.5)
plt.title("Frequency Spectrum — After Processing")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/4_processed_spectrum.png", dpi=150)
plt.close()

# ─────────────────────────────────────────
# STEP 7: Calculate SNR improvement
# ─────────────────────────────────────────
signal_power = np.mean(samples_norm ** 2)
noise        = samples[:len(samples_norm)] - samples_norm
noise_power  = np.mean(noise ** 2)
snr          = 10 * np.log10(signal_power / (noise_power + 1e-12))
print(f"\n=== SNR Estimate ===")
print(f"SNR after processing: {snr:.2f} dB")

print("\nPlots saved:")
print("3_processed_waveform.png")
print("4_processed_spectrum.png")







import pycodec2
import struct

# ─────────────────────────────────────────
# STEP 8: Codec2 Encode + Decode
# ─────────────────────────────────────────
print("\n=== Codec2 Encoding & Decoding ===")

# Codec2 requires 8000 Hz sample rate and 16-bit integer samples
# Convert normalized float samples to 16-bit integers
samples_int16 = (samples_norm * 32767).astype(np.int16)

# Initialize Codec2 at 3200 bps mode
c2 = pycodec2.Codec2(3200)
frame_size = c2.samples_per_frame()
print(f"Codec2 mode       : 3200 bps")
print(f"Frame size        : {frame_size} samples")

# Encode — split audio into frames and encode each one
encoded_frames = []
for i in range(0, len(samples_int16) - frame_size, frame_size):
    frame = samples_int16[i:i + frame_size]
    encoded = c2.encode(frame)
    encoded_frames.append(encoded)

print(f"Total frames encoded : {len(encoded_frames)}")

# Decode — decode each frame back to PCM
decoded_samples = []
for frame in encoded_frames:
    decoded = c2.decode(frame)
    decoded_samples.extend(decoded)

decoded_int16 = np.array(decoded_samples, dtype=np.int16)
decoded_float = decoded_int16.astype(np.float64) / 32767.0

# Save decoded audio
DECODED_FILE = "audio/decoded_audio.wav"
sf.write(DECODED_FILE, decoded_float, sample_rate, subtype="PCM_16")
print(f"Decoded audio saved to: {DECODED_FILE}")

# ─────────────────────────────────────────
# STEP 9: Compression ratio + SNR
# ─────────────────────────────────────────
original_bits = len(samples_norm) * 16
encoded_bits  = len(encoded_frames) * c2.bits_per_frame()
compression_ratio = original_bits / encoded_bits
print(f"\n=== Compression Results ===")
print(f"Original size     : {original_bits} bits")
print(f"Encoded size      : {encoded_bits} bits")
print(f"Compression ratio : {compression_ratio:.2f}:1")

# SNR between processed and decoded
min_len = min(len(samples_norm), len(decoded_float))
signal_power = np.mean(samples_norm[:min_len] ** 2)
noise_power  = np.mean((samples_norm[:min_len] - decoded_float[:min_len]) ** 2)
snr_codec    = 10 * np.log10(signal_power / (noise_power + 1e-12))
print(f"SNR (processed vs decoded) : {snr_codec:.2f} dB")

# ─────────────────────────────────────────
# STEP 10: Plot decoded waveform + spectrum
# ─────────────────────────────────────────
time_dec = np.arange(len(decoded_float)) / sample_rate

plt.figure(figsize=(12, 4))
plt.plot(time_dec, decoded_float, linewidth=0.5)
plt.title("Waveform — After Codec2 Decode")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/5_decoded_waveform.png", dpi=150)
plt.close()

fft_dec    = np.fft.rfft(decoded_float)
freqs_dec  = np.fft.rfftfreq(len(decoded_float), d=1/sample_rate)
mag_dec_db = 20 * np.log10(np.abs(fft_dec) + 1e-12)
plt.figure(figsize=(12, 4))
plt.plot(freqs_dec, mag_dec_db, linewidth=0.5)
plt.title("Frequency Spectrum — After Codec2 Decode")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/6_decoded_spectrum.png", dpi=150)
plt.close()

print("\nPlots saved:")
print("5_decoded_waveform.png")
print("6_decoded_spectrum.png")
print("\nAll done!")