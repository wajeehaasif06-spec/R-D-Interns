import numpy as np
from scipy.io import wavfile
import os
import pycodec2

print("="*50)
print("DIAGNOSTIC: RAW CODEC2 (NO PREPROCESSING)")
print("="*50)

# =====================================================
# PATHS
# =====================================================

input_wav = "recordings/codec_input.wav"
decoded_wav = "recordings/decoded_raw_test.wav"

os.makedirs("recordings", exist_ok=True)

# =====================================================
# LOAD INPUT AUDIO (already resampled to 8kHz by phase2.py)
# =====================================================

sample_rate, data = wavfile.read(input_wav)

print(f"Sample Rate : {sample_rate} Hz")
print(f"Total Samples : {len(data)}")

# make sure it's int16 mono, nothing else touched
data = data.astype(np.int16)

# =====================================================
# CODEC2 INIT
# =====================================================

codec = pycodec2.Codec2(3200)
FRAME_SIZE = codec.samples_per_frame()

print(f"Frame size : {FRAME_SIZE}")

# =====================================================
# FRAME SPLIT — NO filtering, NO normalization, NO gain, NO clipping
# =====================================================

frames = [
    data[i:i+FRAME_SIZE]
    for i in range(0, len(data)-FRAME_SIZE+1, FRAME_SIZE)
]

print(f"Total frames : {len(frames)}")

# =====================================================
# ENCODE / DECODE
# =====================================================

print("\nEncoding...")
encoded_frames = [codec.encode(frame) for frame in frames]

print("Decoding...")
decoded = []
for frame in encoded_frames:
    decoded.extend(codec.decode(frame))

decoded = np.array(decoded, dtype=np.int16)

wavfile.write(decoded_wav, sample_rate, decoded)

print(f"\nSaved: {decoded_wav}")
print("Play this file and compare it to your normal decoded_realtime.wav")