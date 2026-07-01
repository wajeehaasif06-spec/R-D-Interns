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