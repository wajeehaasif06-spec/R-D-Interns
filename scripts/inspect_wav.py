import sys
import wave
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf


def load_wav(path):
    with wave.open(path, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width_bytes = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()

    bit_depth = sample_width_bytes * 8
    duration_sec = n_frames / sample_rate

    samples, sr_check = sf.read(path, dtype="float64")
    assert sr_check == sample_rate

    return {
        "samples": samples,
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "n_channels": n_channels,
        "n_frames": n_frames,
        "duration_sec": duration_sec,
    }


def print_summary(info, path):
    print(f"--- WAV summary: {path} ---")
    print(f"Sample rate     : {info['sample_rate']} Hz")
    print(f"Bit depth       : {info['bit_depth']}-bit")
    print(f"Channels        : {info['n_channels']}")
    print(f"Total frames    : {info['n_frames']}")
    print(f"Duration        : {info['duration_sec']:.3f} s")
    print(f"Bitrate (PCM)   : {info['sample_rate'] * info['bit_depth'] * info['n_channels']} bps")
    print(f"Nyquist freq    : {info['sample_rate'] / 2} Hz")


def plot_waveform_and_spectrum(info, out_path="wav_analysis.png"):
    samples = info["samples"]
    sample_rate = info["sample_rate"]

    mono = samples[:, 0] if samples.ndim > 1 else samples
    t = np.arange(len(mono)) / sample_rate

    n = len(mono)
    fft_vals = np.fft.rfft(mono)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitude_db = 20 * np.log10(np.abs(fft_vals) + 1e-12)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    axes[0].plot(t, mono, linewidth=0.7)
    axes[0].set_title("Waveform (time domain)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Amplitude")

    axes[1].plot(fft_freqs, magnitude_db, linewidth=0.7)
    axes[1].set_title("Frequency Spectrum (FFT)")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Magnitude (dB)")
    axes[1].set_xlim(0, sample_rate / 2)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_wav.py path/to/file.wav")
        sys.exit(1)

    wav_path = sys.argv[1]
    info = load_wav(wav_path)
    print_summary(info, wav_path)
    plot_waveform_and_spectrum(info)