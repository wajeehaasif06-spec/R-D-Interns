import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.signal import resample
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
# CONVERT TO 8 kHz
# ==================================================
audio_float = audio.astype(np.float32)

new_samples = int(
    len(audio_float)
    * CODEC_RATE
    / INPUT_RATE
)

audio_8k = resample(
    audio_float,
    new_samples
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

from scipy.signal import resample

decoded_audio, decoded_rate = sf.read(
    decoded_file,
    dtype='int16'
)

# convert back to 48 kHz for speaker playback
playback_rate = 48000

num_samples = int(
    len(decoded_audio)
    * playback_rate
    / decoded_rate
)

decoded_playback = resample(
    decoded_audio,
    num_samples
)

decoded_playback = decoded_playback.astype(np.int16)

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