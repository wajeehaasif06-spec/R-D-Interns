import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 48000
DURATION = 10

# Set microphone and speaker
sd.default.device = (9, 8)

print("Recording for 10 seconds...")

audio = sd.rec(
    int(SAMPLE_RATE * DURATION),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='int16'
)

sd.wait()

print("Recording complete!")

# Save recording
sf.write(
    "original_realtime.wav",
    audio,
    SAMPLE_RATE
)

print("Playing back recording...")

sd.play(audio, SAMPLE_RATE)
sd.wait()

print("Done!")