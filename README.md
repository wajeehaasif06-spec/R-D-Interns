# Phase 0 - WAV Audio Analysis

## Task Description
In this task, I wrote a Python script that loads a WAV audio file and performs basic signal analysis. The script reads the file, prints its sample rate, bit depth, number of channels, and duration, and generates two plots: a waveform and a frequency spectrum. Both plots are saved as PNG files in the `plots/` folder.

## What I Learned
- What sample rate and bit depth represent in digital audio
- How audio data is stored as arrays of amplitude values in a WAV file
- How to use the FFT (Fast Fourier Transform) to convert a time-domain signal into the frequency domain
- How to use Python libraries (NumPy, SciPy, Matplotlib) for signal processing and visualization
- Git workflow: branching, committing incrementally with meaningful messages, and pushing to a remote repository

## How the Graphs Were Plotted

### Waveform
A time axis was created using `np.linspace()` spanning from 0 to the total duration of the audio. The amplitude values from the WAV data array were plotted against this time axis using Matplotlib to produce the waveform.

### Frequency Spectrum
The FFT was computed on the audio data using `scipy.fft.fft()`, which transforms the signal from the time domain to the frequency domain. The corresponding frequency values were generated using `fftfreq()`. Only the positive half of the FFT output was plotted (since FFT output is mirrored), with magnitude on the y-axis and frequency (Hz) on the x-axis.

## Graph Insights

### Waveform (Amplitude vs Time)
The waveform shows how the amplitude of the audio signal changes over time. It gives a visual sense of the loudness and dynamics of the sound — louder sections appear as taller peaks, quieter sections as flatter regions. It helps identify clipping, silence, or sudden bursts of energy in the audio.

### Frequency Spectrum (Magnitude vs Frequency)
The frequency spectrum shows which frequencies are present in the audio and how strong each one is. High magnitude at a particular frequency means that frequency is dominant in the sound. This is useful for understanding the tonal content of the audio — for example, whether it contains mostly low bass frequencies or high-pitched sounds.

## Prerequisites & Dependencies

- Python 3.x
- WSL (Ubuntu) or any Linux/Mac terminal
- The following Python libraries:
  - `numpy`
  - `scipy`
  - `matplotlib`

## How to Run

1. Clone the repository and navigate to the project folder: