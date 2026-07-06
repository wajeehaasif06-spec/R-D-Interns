import sounddevice as sd
import soundfile as sf
import numpy as np
import subprocess
import threading
import queue
import os

# ==========================
# Configuration
# ==========================

SAMPLE_RATE = 8000
CHANNELS = 1
BUFFER_SIZE = 160          # 20 ms
DURATION = 10              # seconds

OUTPUT_FOLDER = "output"

RAW_FILE = os.path.join(OUTPUT_FOLDER, "microphone.raw")
CODEC_FILE = os.path.join(OUTPUT_FOLDER, "microphone.codec2")
DECODED_RAW = os.path.join(OUTPUT_FOLDER, "microphone_decoded.raw")
DECODED_WAV = os.path.join(OUTPUT_FOLDER, "microphone_decoded.wav")

audio_queue = queue.Queue()
stop_event = threading.Event()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# =====================================================
# Audio Callback
# =====================================================

def audio_callback(indata, frames, time, status):

    if status:
        print(status)

    pcm_buffer = (np.squeeze(indata) * 32767).astype(np.int16)

    audio_queue.put(pcm_buffer)

    print(f"Buffer Received : {frames} samples")
    # =====================================================
# Worker Thread
# =====================================================

def codec2_worker():

    print("Worker Thread Started...")

    with open(RAW_FILE, "wb") as raw_file:

        while True:

            # Stop only when recording has ended
            # and there are no more buffers left
            if stop_event.is_set() and audio_queue.empty():
                break

            try:
                pcm_buffer = audio_queue.get(timeout=0.1)

            except queue.Empty:
                continue

            # Save current buffer into RAW file
            raw_file.write(np.asarray(pcm_buffer, dtype="<i2").tobytes())

            print(f"Processed Buffer : {len(pcm_buffer)} samples")

            audio_queue.task_done()

    print("RAW file completed.")
    # =====================================================
# Main Function
# =====================================================

def main():

    print("\nAvailable Audio Devices:\n")
    print(sd.query_devices())

    # Start worker thread
    worker = threading.Thread(
        target=codec2_worker,
        daemon=True
    )

    worker.start()

    print("\nRecording Started...")
    print(f"Recording Duration : {DURATION} seconds\n")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=BUFFER_SIZE,
        callback=audio_callback
    ):
        sd.sleep(DURATION * 1000)

    print("\nRecording Finished.")

    # Tell worker no more buffers are coming
    stop_event.set()

    # Wait until queue becomes empty
    audio_queue.join()

    # Wait for worker to finish
    worker.join()

    # Save original RAW as WAV for checking
    raw_audio = np.fromfile(RAW_FILE, dtype=np.int16)

    sf.write(
        os.path.join(OUTPUT_FOLDER, "microphone_original.wav"),
        raw_audio,
        SAMPLE_RATE,
        subtype="PCM_16"
    )

    print("\nEncoding with Codec2...")

    subprocess.run(
        [
            "c2enc",
            "2400",
            RAW_FILE,
            CODEC_FILE
        ],
        check=True
    )

    print("Decoding with Codec2...")

    subprocess.run(
        [
            "c2dec",
            "2400",
            CODEC_FILE,
            DECODED_RAW
        ],
        check=True
    )

    # Read decoded RAW
    decoded_audio = np.fromfile(
        DECODED_RAW,
        dtype=np.int16
    )

    # Save decoded WAV
    sf.write(
        DECODED_WAV,
        decoded_audio,
        SAMPLE_RATE,
        subtype="PCM_16"
    )

    print("\n===================================")
    print("Processing Complete")
    print("===================================")
    print(f"RAW File      : {RAW_FILE}")
    print(f"Codec File    : {CODEC_FILE}")
    print(f"Decoded WAV   : {DECODED_WAV}")
if __name__ == "__main__":
        main()