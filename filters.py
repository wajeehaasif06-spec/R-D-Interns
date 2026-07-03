# filters.py
"""
Bandpass filter for real-time audio.

Unlike Phase 1 (where you filtered one full WAV array at once),
real-time processing filters small chunks continuously. The filter
must carry its internal "memory" (state) from one chunk to the next,
otherwise each chunk boundary produces an audible click.
"""

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
import config


def design_bandpass_filter():
    """
    Designs the Butterworth bandpass filter coefficients.
    Returns (b, a) — the filter's numerator/denominator coefficients.
    Runs ONCE, not per-chunk — the design itself doesn't change.
    """
    nyquist = 0.5 * config.SAMPLE_RATE
    low = config.LOWCUT / nyquist
    high = config.HIGHCUT / nyquist
    b, a = butter(config.FILTER_ORDER, [low, high], btype="band")
    return b, a


class StatefulBandpassFilter:
    """
    Wraps the filter + its persistent state together, so each new
    chunk continues smoothly from where the last chunk left off.
    """

    def __init__(self):
        self.b, self.a = design_bandpass_filter()
        # zi = initial filter state, scaled to zero (silence) at start
        self.zi = lfilter_zi(self.b, self.a) * 0.0

    def process(self, chunk):
        """
        Filters one chunk of audio, updating internal state
        so the NEXT call continues seamlessly.
        """
        filtered_chunk, self.zi = lfilter(self.b, self.a, chunk, zi=self.zi)
        return filtered_chunk

    def reset(self):
        """Resets filter memory — call this if audio stream restarts."""
        self.zi = lfilter_zi(self.b, self.a) * 0.0


# ----------------------------------------------------------------------
# Quick test — run this file directly to verify the filter works
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Generate a fake test signal: a 1000 Hz tone (within our passband)
    duration = 0.02  # 20ms, matches FRAME_SIZE at 8000 Hz
    t = np.linspace(0, duration, config.FRAME_SIZE, endpoint=False)
    test_tone = np.sin(2 * np.pi * 1000 * t)

    filt = StatefulBandpassFilter()
    output = filt.process(test_tone)

    print(f"Filter designed for band: {config.LOWCUT}-{config.HIGHCUT} Hz")
    print(f"Input chunk size  : {len(test_tone)} samples")
    print(f"Output chunk size : {len(output)} samples")
    print(f"Output sample (first 5): {output[:5]}")