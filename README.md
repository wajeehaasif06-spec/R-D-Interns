# Phase 1 — DSP Processing & Codec2 Encoding
**Branch:** RAYYAN_PHASE1_DSP_CODEC2  
**Intern:** Rayyan  
**Task:** Read and analyze noisy audio, apply DSP processing (DC removal, noise filtering, normalization), encode using Codec2, decode back to WAV, and evaluate results.

---

## What I Did

### Step 1: Analysis of Noisy Audio
- Loaded `noisy_audio.wav` and extracted metadata
- Plotted waveform and frequency spectrum as baseline
- Sample rate: 8000 Hz, 16-bit, mono, 8.439s, max amplitude 0.9997, DC offset ~0.000001

### Step 2: DC Offset Removal
- Subtracted the mean of the signal from every sample
- DC offset was 0.000001 — essentially zero for this clip
- Signal mean became exactly 0.00000000 after removal

### Step 3: Bandpass Filter (Noise Suppression)
- Applied Butterworth bandpass filter: 300–3400 Hz (telephone speech band)
- Removed low-frequency rumble (below 300 Hz) and high-frequency hiss (above 3400 Hz)
- Filter order: 5
- Max amplitude after filtering: 1.0949 (slight overshoot corrected by normalization)

### Step 4: Gain + Normalization
- Gain: 1.0 (no amplification needed)
- Normalized to [-1, 1] by dividing by peak value
- Peak after normalization: exactly 1.0000
- Saved as `audio/processed_audio.wav`

### Step 5: Codec2 Encoding & Decoding
- Encoded processed audio using Codec2 at 3200 bps
- Frame size: 160 samples (20ms per frame)
- Total frames encoded: 421
- Decoded back to WAV and saved as `audio/decoded_audio.wav`

### Step 6: Evaluation
- Verified results visually in Audacity (original vs processed vs decoded)
- Processed audio clearly cleaner than original
- Decoded audio has slight robotic quality — expected at 40:1 compression

---

## Results Summary

| Metric | Value |
|---|---|
| Sample rate | 8000 Hz |
| DC offset removed | 0.000001 |
| Filter passband | 300–3400 Hz |
| SNR after DSP processing | -4.11 dB |
| Codec2 mode | 3200 bps |
| Frame size | 160 samples (20ms) |
| Total frames encoded | 421 |
| Original size | 1,080,208 bits |
| Encoded size | 26,944 bits |
| **Compression ratio** | **40.09:1** |
| **SNR after Codec2** | **-3.48 dB** |

---

## Tweakable Settings
In `scripts/process_audio.py`:

| Setting | Current Value | Effect |
|---|---|---|
| `HIGHPASS_CUTOFF` | 300 Hz | Lower = keep more bass |
| `LOWPASS_CUTOFF` | 3400 Hz | Higher = keep more highs |
| `FILTER_ORDER` | 5 | Higher = sharper filter (3–8) |
| `GAIN` | 1.0 | Above 1.0 amplifies volume |
| Codec2 mode | 3200 bps | Lower bps = more compression, less quality |

---

## Output Files

| File | Description |
|---|---|
| `audio/noisy_audio.wav` | Original noisy input |
| `audio/processed_audio.wav` | After DC removal + filter + normalization |
| `audio/decoded_audio.wav` | After Codec2 encode → decode |
| `plots/1_noisy_waveform.png` | Waveform of noisy input |
| `plots/2_noisy_spectrum.png` | Spectrum of noisy input |
| `plots/3_processed_waveform.png` | Waveform after DSP processing |
| `plots/4_processed_spectrum.png` | Spectrum after DSP processing |
| `plots/5_decoded_waveform.png` | Waveform after Codec2 decode |
| `plots/6_decoded_spectrum.png` | Spectrum after Codec2 decode |
| `plots/audacity_comparison.png` | Audacity visual comparison |
| `plots/audacity_3way_comparison.png` | 3-way Audacity comparison |

---

## How to Run

### Prerequisites
- Python 3.x installed in WSL/Linux
- Git

### Setup
```bash
git clone https://github.com/wajeehaasif06-spec/R-D-Interns.git
cd R-D-Interns
git checkout RAYYAN_PHASE1_DSP_CODEC2
python3 -m venv venv
source venv/bin/activate
pip install numpy scipy matplotlib soundfile pycodec2
```

### Run
```bash
python3 scripts/process_audio.py
```

### Dependencies
| Package | Purpose |
|---|---|
| numpy | Array math and FFT |
| scipy | Butterworth filter design |
| matplotlib | Plotting waveforms and spectrums |
| soundfile | Reading and writing WAV files |
| pycodec2 | Codec2 encoding and decoding |

---

## What I Learned
- DC offset removal eliminates constant signal shift that causes filter distortion
- Butterworth bandpass filter effectively isolates the 300–3400 Hz speech band
- Normalization prevents clipping after filtering introduces amplitude overshoot
- Codec2 achieves 40:1 compression at 3200 bps — far beyond standard codecs like MP3
- SNR of -3.48 dB after Codec2 decode shows acceptable quality for voice at extreme compression
- Audacity is useful for visually and aurally verifying each processing stage