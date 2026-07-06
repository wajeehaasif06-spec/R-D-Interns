import sounddevice as sd

SAMPLE_RATE = 48000
CHANNELS = 1
BLOCKSIZE = 960  # 20 ms


def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)

    print("Frames:", frames)

    outdata[:] = indata


print("================================")
print(" Real-Time Microphone Loopback ")
print(" Press Ctrl+C to stop")
print("================================")

try:
    with sd.Stream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCKSIZE,
        callback=audio_callback,
    ):
        while True:
            sd.sleep(1000)

except KeyboardInterrupt:
    print("\nStopped.")
