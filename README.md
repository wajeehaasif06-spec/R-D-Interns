# Phase 1 — Software Audio Communication Chain

## Overview

This project implements a complete software-based audio communication chain using Python and Codec2 compression. The objective is to simulate a digital voice communication system by processing, compressing, reconstructing, and evaluating a speech signal.

The implemented chain follows:

```
Input Audio
     ↓
DC Offset Removal
     ↓
FIR Bandpass Filtering
     ↓
Gain Normalization
     ↓
Codec2 Encoding
     ↓
Codec2 Decoding
     ↓
Reconstructed Audio
     ↓
Performance Evaluation
```

---

## Objectives

- Read and analyze WAV audio files.
- Remove DC offset from the signal.
- Reduce background noise using FIR filtering.
- Normalize the signal amplitude.
- Compress speech using Codec2.
- Decode compressed speech back to PCM audio.
- Compare original and reconstructed signals.
- Evaluate compression ratio and signal quality.

---

## Audio Analysis

| Parameter | Value |
|-----------|--------|
| Sample Rate | 8000 Hz |
| Bit Depth | 16-bit |
| Channels | Mono |
| Audio Type | Speech |

---

## Signal Processing

### 1. DC Offset Removal

The average value of the signal is removed to center the waveform around zero:

```
x[n] = x[n] - mean(x)
```

---

### 2. FIR Bandpass Filtering

A 101-tap Hamming-window FIR filter was designed with a passband of:

```
300 Hz – 3400 Hz
```

This range corresponds to the frequency band used in conventional speech communication systems.

---

### 3. Gain Normalization

The filtered signal is normalized to 90% of the available 16-bit dynamic range to avoid clipping while maximizing signal amplitude.

---

## Codec2 Compression

Codec2 was used as the speech codec.

Configuration:

```
Codec Mode : 3200 bps
Input      : 16-bit PCM
Output     : Codec2 bitstream
```

The compressed signal was then decoded back into PCM audio for quality evaluation.

---

## Performance Evaluation

The following metrics were calculated:

### Compression Ratio

```
Compression Ratio =
Original File Size / Encoded File Size
```

---

### Signal-to-Noise Ratio (SNR)

```
SNR(dB) =
10 log10(Psignal / Pnoise)
```

where:

- Psignal = original signal power
- Pnoise = reconstruction error power

---

## Generated Plots

The project generates:

- Original waveform
- Original frequency spectrum
- Processed waveform
- Processed spectrum
- Decoded waveform
- Decoded spectrum
- Error signal
- FIR filter frequency response
- SNR comparison chart

---

## Technologies Used

- Python 3
- NumPy
- SciPy
- Matplotlib
- Codec2
- Git
- WSL (Ubuntu)

---

## Running the Project

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run the program:

```bash
python phase1.py
```

---

## Results

After processing and Codec2 reconstruction:

- Background noise was significantly reduced.
- Speech intelligibility was preserved.
- Compression was achieved while maintaining acceptable audio quality.
- Performance was evaluated using compression ratio and SNR measurements.

---
