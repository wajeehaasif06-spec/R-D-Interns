# Phase 0 – WAV Audio Analysis

## Overview

This project was completed as part of the **R&D Internship – Phase 0**. The objective was to build a Python program that reads a WAV audio file, extracts its metadata, and performs basic audio signal analysis. The program also visualizes the audio signal in both the **time domain** and the **frequency domain** using waveform and Fast Fourier Transform (FFT) plots.

---

## What I Did

During this task, I:

- Read a WAV audio file using the `soundfile` library.
- Extracted and displayed important audio metadata, including:
  - Sample Rate
  - Bit Depth
  - Number of Channels
  - Data Type
  - Duration
- Generated a waveform to visualize the audio signal over time.
- Performed a Fast Fourier Transform (FFT) to analyze the frequency components of the audio.
- Saved both graphs inside the `plots/` directory.
- Used Git for version control by creating a dedicated branch, making meaningful commits, and pushing the changes to GitHub.

---

## What I Learned

This task helped me understand several fundamental concepts of digital signal processing and software development, including:

- The structure and properties of WAV audio files.
- The meaning and importance of sample rate and bit depth.
- The difference between mono and stereo audio.
- How a waveform represents an audio signal in the time domain.
- How the Fast Fourier Transform (FFT) converts a signal from the time domain to the frequency domain.
- Why only the positive frequencies are plotted after performing FFT.
- Basic visualization of audio signals using Matplotlib.
- Using Git branches, commits, and GitHub for version control and collaboration.

---

## How the Graphs Were Plotted

### Waveform

The waveform was created by generating a time axis using the sample rate and plotting the audio sample amplitudes against time using Matplotlib.

```python
time = np.arange(len(audio_data)) / sample_rate
plt.plot(time, audio_data)
```

This produces a graph showing how the amplitude of the audio changes throughout the recording.

### Frequency Spectrum (FFT)

The frequency spectrum was generated using NumPy's Fast Fourier Transform (FFT).

```python
fft_result = np.fft.fft(audio_data)
frequencies = np.fft.fftfreq(len(audio_data), d=1/sample_rate)
```

The magnitude of the positive frequency components was then plotted using Matplotlib.

---

## Graph Explanation

### 1. Waveform

The waveform is a **time-domain representation** of the audio signal.

- **X-axis:** Time (seconds)
- **Y-axis:** Amplitude

#### Key Insights

- Shows how the audio signal changes over time.
- Identifies louder and quieter portions of the recording.
- Helps visualize pauses, peaks, and overall signal behavior.

---

### 2. Frequency Spectrum

The frequency spectrum is a **frequency-domain representation** of the audio signal obtained using FFT.

- **X-axis:** Frequency (Hz)
- **Y-axis:** Magnitude

#### Key Insights

- Shows which frequencies are present in the audio.
- Identifies dominant frequency components.
- Helps understand the frequency distribution of the signal.
- Commonly used in speech processing, audio analysis, filtering, and signal processing applications.

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

## Prerequisites

- Python 3.x
- Git
- Virtual Environment (recommended)

### Required Python Libraries

- NumPy
- Matplotlib
- SoundFile
- SciPy

Install all dependencies using:

```bash
pip install -r requirements.txt
```

or

```bash
pip install numpy matplotlib soundfile scipy
```

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Navigate to the project folder

```bash
cd R-D-Interns
```

### 3. (Optional) Create and activate a virtual environment

Linux / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Ensure the WAV file (`loud.wav`) is present in the project directory.

### 6. Run the script

```bash
python audio_analysis.py
```

---

## Output

Running the script will:

- Display audio metadata in the terminal.
- Generate the waveform plot.
- Generate the frequency spectrum plot.
- Save both graphs inside the `plots/` folder as:

```
plots/
├── waveform.png
└── frequency_spectrum.png
```

---

## Technologies Used

- Python
- NumPy
- SoundFile
- Matplotlib
- SciPy
- Git
- GitHub

---

## Author

**Bashair Talib**

R&D Internship – Phase 0