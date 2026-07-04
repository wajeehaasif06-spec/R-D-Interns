import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.signal import resample
from pathlib import Path
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
# PLAYBACK
# ==================================================
print("\nPlaying recording...")

sd.play(audio, INPUT_RATE)
sd.wait()

print("Done!")

print("\nCreated:")
print(original_file)
print(codec_file)