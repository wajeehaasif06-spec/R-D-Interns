# Real-Time Audio Recording and Codec2 Processing

## Project Overview

This project implements a real-time audio processing pipeline using Python and the Codec2 speech codec. The application captures live audio from a microphone, stores it in fixed-size buffers, converts the captured audio into RAW PCM format, compresses it using Codec2, and finally decodes it back into an audio waveform for playback and evaluation.

The objective of this project is to understand the complete workflow of low-bitrate speech compression while working with real-time audio streams, buffering techniques, multithreading, and audio file processing.

---

# Objectives

* Capture live microphone audio in real time.
* Process audio using fixed-size buffers.
* Implement a producer-consumer architecture using multithreading.
* Store recorded audio as 16-bit PCM RAW data.
* Encode speech using the Codec2 speech codec.
* Decode the compressed speech back into PCM audio.
* Generate a playable WAV file for evaluating the decoded speech quality.

---

# Features

* Real-time microphone recording
* Fixed-size audio buffering
* Thread-safe producer-consumer queue
* Multithreaded audio processing
* Codec2 speech compression
* Codec2 speech decompression
* Automatic RAW and WAV file generation
* Cross-platform Python implementation (tested on WSL)

---

# System Workflow

The application follows the sequence below:

1. Capture live audio from the microphone.
2. Divide the incoming audio into fixed-size buffers.
3. Store each audio buffer in a thread-safe queue.
4. A worker thread retrieves buffered audio data.
5. Buffered audio is written into a RAW PCM file.
6. The RAW audio is compressed using Codec2.
7. The compressed Codec2 bitstream is decoded back into RAW PCM audio.
8. The decoded audio is converted into a WAV file for playback and evaluation.

---

# Technologies Used

* Python 3
* NumPy
* SoundDevice
* SoundFile
* Codec2
* Multithreading
* Queue
* WSL (Windows Subsystem for Linux)

---

# Output Files

The program generates the following files:

* **microphone.raw** – Recorded microphone audio in 16-bit PCM RAW format.
* **microphone.codec2** – Codec2 encoded compressed speech.
* **microphone_decoded.raw** – Decoded PCM audio produced by Codec2.
* **microphone_decoded.wav** – Final decoded audio in WAV format.
* **microphone_original.wav** – Original recorded audio converted from RAW for comparison.

---

# Learning Outcomes

This project demonstrates practical understanding of:

* Real-time audio acquisition
* Buffer-based audio processing
* Producer-consumer multithreading
* PCM audio representation
* Speech compression using Codec2
* Audio encoding and decoding workflows
* Handling real-time audio streams in Python

---

# Future Improvements

Possible enhancements include:

* True real-time frame-by-frame Codec2 encoding and decoding.
* Live playback of decoded audio.
* Configurable Codec2 bitrate selection.
* Voice Activity Detection (VAD).
* Noise suppression and audio preprocessing.
* Graphical user interface for recording and playback.
* Performance monitoring for latency and throughput.

---

# Conclusion

This project successfully demonstrates a complete real-time speech processing pipeline from microphone capture to Codec2 compression and decompression. It combines real-time audio buffering, multithreaded processing, and speech codec integration to provide practical experience with low-bitrate speech communication systems and digital signal processing concepts.
