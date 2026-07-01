# R&D Interns - Phase 0
# Phase 0 — WAV File Analysis
**Branch:** RAYYAN_PHASE0_WAV_ANALYSIS  
**Intern:** Rayyan  
**Task:** Load and inspect a WAV audio file, print its PCM properties, and plot its waveform and frequency spectrum.

---

## What I Did
Wrote a Python script (`scripts/inspect_wav.py`) that:
- Reads a WAV file and extracts its metadata (sample rate, bit depth, channels, duration, bitrate, Nyquist frequency) directly from the file header
- Plots the time-domain waveform (amplitude vs. time)
- Plots the frequency-domain spectrum (magnitude in dB vs. frequency in Hz) using FFT
- Saves both plots as a single PNG image (`wav_analysis.png`)

---

## What I Learned
- A WAV file stores its metadata (sample rate, bit depth, channels) in a structured header before the actual audio data — the code just reads those pre-stored values
- The waveform shows how the signal's amplitude changes over time, which reveals loudness patterns and silence
- The FFT (Fast Fourier Transform) converts the time-domain signal into the frequency domain, showing which frequencies are present and how strong each one is
- The Nyquist frequency (half the sample rate) is the highest frequency a recording can capture — for our 8000 Hz clip, nothing above 4000 Hz can be represented
- A 16-bit, 8000 Hz mono recording has a PCM bitrate of 128,000 bps — this is the baseline before any compression is applied

---

## Graph Explanations

### Waveform (Time Domain)
The top graph plots amplitude (signal strength) against time in seconds. It shows the raw shape of the audio signal — louder sections appear as taller peaks, quieter sections appear flatter. This graph is useful for spotting loud/quiet regions, silence, and the overall duration of the clip. Our test clip (loud.wav) shows high-amplitude content throughout its 8.4 second duration.

### Frequency Spectrum (FFT)
The bottom graph plots frequency (Hz) against magnitude in decibels (dB). It shows which frequencies are present in the audio and how much energy each one carries. The x-axis goes from 0 Hz up to the Nyquist limit of 4000 Hz. Peaks in this graph indicate dominant frequencies in the signal — for voice audio, most energy sits between 300–3400 Hz, which matches the telephony-grade 8 kHz sample rate of this clip.

---

## How to Run

### Prerequisites
- Python 3.x installed in WSL/Linux
- Git

### Setup
```bash
# Clone the repo
git clone https://github.com/wajeehaasif06-spec/R-D-Interns.git
cd R-D-Interns
git checkout RAYYAN_PHASE0_WAV_ANALYSIS

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install numpy scipy matplotlib soundfile
```

### Run the script
```bash
python3 scripts/inspect_wav.py audio/test_clip.wav
```

### Output
- Prints WAV metadata to the terminal (sample rate, bit depth, channels, duration, bitrate, Nyquist frequency)
- Saves `wav_analysis.png` in the current directory containing both plots

### Dependencies
| Package | Purpose |
|----|----|
|  numpy  | FFT computation and array math |
|  scipy  | Signal processing (used in later phases) |
| matplotlib | Plotting waveform and spectrum |
| soundfile | Reading WAV audio sample data |