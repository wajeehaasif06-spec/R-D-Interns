# Phase 0 - WAV Audio Analysis

## Overview

This project is part of the R&D Internship Phase 0 task.

The objective is to read a WAV audio file, extract its metadata, visualize the waveform, and analyze its frequency content using the Fast Fourier Transform (FFT).

---

## Features

- Read a WAV audio file
- Display audio metadata:
  - Sample Rate
  - Bit Depth
  - Number of Channels
  - Audio Duration
  - Data Type
- Generate and save the waveform
- Generate and save the frequency spectrum using FFT

---

## Project Structure

```
R-D-Interns/
│
├── audio_analysis.py
├── loud.wav
├── requirements.txt
├── README.md
└── plots/
    ├── waveform.png
    └── frequency_spectrum.png
```

---

## Requirements

- Python 3.x
- NumPy
- SciPy
- Matplotlib
- SoundFile

Install the dependencies using:

```bash
pip install -r requirements.txt
```

---

## How to Run

Execute the script using:

```bash
python audio_analysis.py
```

The program will:

1. Read the WAV file.
2. Display audio metadata.
3. Generate the waveform.
4. Generate the frequency spectrum.
5. Save the plots inside the `plots` folder.

---

## Example Output

```
Sample Rate: 8000 Hz
Bit Depth: 64 bits
Channels: Mono
Duration: 8.439125 seconds
```

Generated files:

- plots/waveform.png
- plots/frequency_spectrum.png

---

## Concepts Used

- WAV Audio Processing
- Digital Audio Sampling
- Sample Rate
- Bit Depth
- Mono vs Stereo Audio
- Waveform Visualization
- Fast Fourier Transform (FFT)
- Frequency Spectrum Analysis
- NumPy Arrays
- Matplotlib Visualization

---

## Git Workflow

The project was developed using Git by:

- Initializing the repository
- Creating a dedicated Phase 0 branch
- Making meaningful commits after each completed sub-task
- Pushing all changes to GitHub

---

## Author

**Bashair Talib**

R&D Internship - Phase 0