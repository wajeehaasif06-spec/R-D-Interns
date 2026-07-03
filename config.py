# config.py
"""
Central configuration for the real-time audio pipeline.
Sample rate is DERIVED from Nyquist theorem, not hardcoded blindly.
"""

# Step 1: highest frequency we care about capturing (speech intelligibility)
MAX_VOICE_FREQUENCY = 3400.0   # Hz


def calculate_min_sample_rate(max_freq):
    """Nyquist theorem: sample rate must be >= 2x highest signal frequency."""
    return 2 * max_freq


# Step 2: compute Nyquist minimum, then pick actual rate used
NYQUIST_MINIMUM = calculate_min_sample_rate(MAX_VOICE_FREQUENCY)  # 6800 Hz

# Codec2 3200bps mode requires exactly 8000 Hz input — this satisfies
# Nyquist (needs >= 6800) AND the codec's fixed requirement.
SAMPLE_RATE = 8000
CHANNELS = 1

# Bandpass filter settings
LOWCUT = 300.0
HIGHCUT = MAX_VOICE_FREQUENCY
FILTER_ORDER = 4

# Frame size locked to Codec2 3200bps requirement (20ms @ 8kHz)
FRAME_SIZE = 160
CODEC2_MODE_BPS = 3200


if __name__ == "__main__":
    print(f"Max voice frequency targeted : {MAX_VOICE_FREQUENCY} Hz")