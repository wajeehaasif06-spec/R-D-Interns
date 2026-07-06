import sounddevice as sd
import soundfile as sf
import numpy as np
import soxr
from pathlib import Path
import subprocess
import os


# ==================================================
# PATHS
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
RECORDINGS = BASE_DIR / "recordings"

RECORDINGS.mkdir(exist_ok=True)

# ==================================================
# PARAMETERS
# ==================================================
INPUT_RATE = 48000
CODEC_RATE = 8000
DURATION = 10

# Your microphone and speaker IDs
sd.default.device = (9, 8)

# ==================================================
# RECORD AUDIO
# ==================================================
print("=" * 50)
print("RECORDING AUDIO")
print("=" * 50)

print(f"Recording for {DURATION} seconds...")

audio = sd.rec(
    int(INPUT_RATE * DURATION),
    samplerate=INPUT_RATE,
    channels=1,
    dtype='int16'
)

sd.wait()

print("Recording complete!")

print("Max:", np.max(audio))
print("Min:", np.min(audio))
print("Mean:", np.mean(audio))

# ==================================================
# SAVE ORIGINAL AUDIO
# ==================================================
original_file = RECORDINGS / "original_realtime.wav"

sf.write(
    original_file,
    audio,
    INPUT_RATE
)

print("Saved original recording")

# ==================================================
# CONVERT TO 8 kHz (using soxr)
# ==================================================
audio_float = audio.astype(np.float32)
audio_float = audio_float.squeeze()

audio_8k = soxr.resample(
    audio_float,
    INPUT_RATE,
    CODEC_RATE,
    quality='HQ'
)

audio_8k = np.clip(
    audio_8k,
    -32768,
    32767
).astype(np.int16)

codec_file = RECORDINGS / "codec_input.wav"

sf.write(
    codec_file,
    audio_8k,
    CODEC_RATE
)

print("Saved Codec2 input")

# ==================================================
# FILE INFORMATION
# ==================================================
print("\nFILE INFORMATION")
print("----------------")

print(
    f"Original size: "
    f"{os.path.getsize(original_file)} bytes"
)

print(
    f"Codec input size: "
    f"{os.path.getsize(codec_file)} bytes"
)

# ==================================================
# RUN CODEC2 IN WSL
# ==================================================
print("\nLaunching Codec2 processing...")

subprocess.run(
    [
        "wsl",
        "bash",
        "-c",
        "cd ~/R-D-Interns && source venv/bin/activate && python phase2_codec.py"
    ],
    check=True
)

print("Codec2 processing complete!")

# ==================================================
# PLAY DECODED AUDIO
# ==================================================
decoded_file = (
    r"\\wsl.localhost\Ubuntu\home\aymen\R-D-Interns"
    r"\recordings\decoded_realtime.wav"
)

print("\nPlaying decoded audio...")

decoded_audio, decoded_rate = sf.read(
    decoded_file,
    dtype='int16'
)

# convert back to 48 kHz for speaker playback (using soxr)
playback_rate = 48000

decoded_audio_float = decoded_audio.astype(np.float32)

decoded_playback = soxr.resample(
    decoded_audio_float,
    decoded_rate,
    playback_rate,
    quality='HQ'
)

decoded_playback = np.clip(decoded_playback, -32768, 32767).astype(np.int16)

sd.play(
    decoded_playback,
    playback_rate
)

sd.wait()

print("Decoded playback complete!")

# ==================================================
# SUMMARY
# ==================================================
print("\nCreated:")
print(original_file)
print(codec_file)
print(decoded_file)