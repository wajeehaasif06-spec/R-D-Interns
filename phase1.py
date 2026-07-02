import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import firwin, lfilter
import os

filename = "noisy__Audio.wav"

# ============================================================
# STEP 1: Load and analyze audio
# ============================================================
sample_rate, data = wavfile.read(filename)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Bit Depth   : {data.dtype.itemsize * 8} bits")
print(f"Channels    : {'Mono' if data.ndim == 1 else 'Stereo'}")
print(f"Duration    : {len(data)/sample_rate:.3f} seconds")

os.makedirs("plots", exist_ok=True)
os.makedirs("processed_audio", exist_ok=True)

data_float = data.astype(np.float32)
time = np.linspace(0, len(data_float)/sample_rate, len(data_float))

# ============================================================
# STEP 2: Original plots
# ============================================================
N = len(data_float)
yf = np.fft.fft(data_float)
xf = np.fft.fftfreq(N, 1/sample_rate)

plt.figure(figsize=(12, 4))
plt.plot(time, data_float, color='steelblue', linewidth=0.5)
plt.title("Original Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.savefig("plots/original_waveform.png", dpi=150)
plt.close()

plt.figure(figsize=(12, 4))
plt.plot(xf[:N//2], np.abs(yf[:N//2]), color='steelblue', linewidth=0.5)
plt.title("Original Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.savefig("plots/original_spectrum.png", dpi=150)
plt.close()

# ============================================================
# STEP 3: DC Offset Removal
# ============================================================
dc_offset = np.mean(data_float)
data_dc = data_float - dc_offset
print(f"DC Offset removed: {dc_offset:.4f}")

# ============================================================
# STEP 4: FIR Bandpass Filter (300-3400 Hz)
# ============================================================
nyq = sample_rate / 2
low  = 300  / nyq
high = 3400 / nyq

fir_coeff = firwin(101, [low, high], pass_zero=False, window='hamming')
data_filtered = lfilter(fir_coeff, 1.0, data_dc)
print("FIR bandpass filter applied (300-3400 Hz)")

# ============================================================
# STEP 5: Gain Normalization
# ============================================================
max_val = np.max(np.abs(data_filtered))
gain_factor = (0.9 * 32767) / max_val
data_gained = np.clip(data_filtered * gain_factor, -32768, 32767).astype(np.int16)
print(f"Gain factor applied: {gain_factor:.4f}")

wavfile.write("processed_audio/processed.wav", sample_rate, data_gained)
print("Processed WAV saved!")

# ============================================================
# STEP 6: Before/After Comparison Plots
# ============================================================
time_proc = np.linspace(0, len(data_gained)/sample_rate, len(data_gained))

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Waveforms
axes[0][0].plot(time, data_float, color='steelblue', linewidth=0.5)
axes[0][0].set_title("Original — Waveform")
axes[0][0].set_xlabel("Time (s)")
axes[0][0].set_ylabel("Amplitude")
axes[0][0].grid(True)

axes[0][1].plot(time_proc, data_gained, color='green', linewidth=0.5)
axes[0][1].set_title("Processed — Waveform")
axes[0][1].set_xlabel("Time (s)")
axes[0][1].set_ylabel("Amplitude")
axes[0][1].grid(True)

# Spectrums
N2 = len(data_gained)
yf2 = np.fft.fft(data_gained.astype(np.float32))
xf2 = np.fft.fftfreq(N2, 1/sample_rate)

axes[1][0].plot(xf[:N//2], np.abs(yf[:N//2]), color='steelblue', linewidth=0.5)
axes[1][0].set_title("Original — Spectrum")
axes[1][0].set_xlabel("Frequency (Hz)")
axes[1][0].set_ylabel("Magnitude")
axes[1][0].grid(True)

axes[1][1].plot(xf2[:N2//2], np.abs(yf2[:N2//2]), color='green', linewidth=0.5)
axes[1][1].set_title("Processed — Spectrum")
axes[1][1].set_xlabel("Frequency (Hz)")
axes[1][1].set_ylabel("Magnitude")
axes[1][1].grid(True)

plt.tight_layout()
plt.savefig("plots/before_after_comparison.png", dpi=150)
plt.close()

print("All plots saved in plots/ folder!")

# ============================================================
# STEP 7: Codec2 Encode → Decode
# ============================================================
import subprocess

os.makedirs("codec", exist_ok=True)

raw_input   = "codec/processed.raw"
raw_encoded = "codec/encoded.c2"
raw_decoded = "codec/decoded.raw"
output_wav  = "processed_audio/output_decoded.wav"

# Save processed audio as raw 16-bit PCM (Codec2 needs raw, not WAV)
data_gained.tofile(raw_input)
print("Raw PCM file saved!")

# Encode with Codec2 at 3200 bps
print("Encoding with Codec2...")
subprocess.run(["c2enc", "3200", raw_input, raw_encoded], check=True)
print("Encoding done!")

# Decode back
print("Decoding with Codec2...")
subprocess.run(["c2dec", "3200", raw_encoded, raw_decoded], check=True)
print("Decoding done!")

# Read decoded raw PCM and save as WAV
decoded_data = np.frombuffer(open(raw_decoded, 'rb').read(), dtype=np.int16)
wavfile.write(output_wav, sample_rate, decoded_data)
print(f"Output WAV saved: {output_wav}")

# ============================================================
# STEP 8: Compression Ratio
# ============================================================
original_size = os.path.getsize(raw_input)
encoded_size  = os.path.getsize(raw_encoded)
compression_ratio = original_size / encoded_size

print("\n" + "=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Original raw size : {original_size} bytes")
print(f"Encoded size      : {encoded_size} bytes")
print(f"Compression Ratio : {compression_ratio:.2f}:1")

# ============================================================
# STEP 9: SNR Calculation
# ============================================================
min_len = min(len(data_gained), len(decoded_data))
original_seg = data_gained[:min_len].astype(np.float32)
decoded_seg  = decoded_data[:min_len].astype(np.float32)

signal_power = np.mean(original_seg ** 2)
noise_power  = np.mean((original_seg - decoded_seg) ** 2)
snr_db = 10 * np.log10(signal_power / (noise_power + 1e-10))

print(f"SNR               : {snr_db:.2f} dB")

# SNR bar chart
plt.figure(figsize=(6, 4))
plt.bar(["SNR (processed vs decoded)"], [snr_db], color='teal')
plt.ylabel("dB")
plt.title(f"SNR after Codec2: {snr_db:.2f} dB")
plt.grid(True, axis='y')
plt.savefig("plots/snr_chart.png", dpi=150)
plt.close()
print("SNR chart saved!")

# decoded waveform
decoded_time = np.linspace(0, len(decoded_data)/sample_rate, len(decoded_data))

plt.figure(figsize=(12,4))
plt.plot(decoded_time, decoded_data, linewidth=0.5)
plt.title("Decoded Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.savefig("plots/decoded_waveform.png", dpi=150)
plt.close()

#decoded spectrum
Nd = len(decoded_data)

yf_dec = np.fft.fft(decoded_data)
xf_dec = np.fft.fftfreq(Nd, 1/sample_rate)

plt.figure(figsize=(12,4))
plt.plot(xf_dec[:Nd//2], np.abs(yf_dec[:Nd//2]), linewidth=0.5)
plt.title("Decoded Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.savefig("plots/decoded_spectrum.png", dpi=150)
plt.close()