"""
Real-time Codec2 audio chain (v2)
==================================

Mic -> [Audio callback] -> input queue -> [Codec thread] -> output queue -> [Audio callback] -> Speaker
                                                |
                                                +-> UART tap (PCM or Codec2 bits) -> Logic analyzer

Changes from v1, based on review feedback:
  - Queue depth dropped to 2 (was 4) -> caps worst-case queue latency at ~40ms instead of ~80ms.
  - Warm-up: first WARMUP_FRAMES output frames are forced to silence to avoid a startup
    noise burst while the codec/queues are still filling.
  - Per-frame timestamps -> real capture-to-playback latency measurement, not just an estimate.
  - Explicit overrun/underrun/dropped-frame counters, printed periodically instead of
    silently swallowed.
  - Logic analyzer: RTS toggling only marked frame *timing*, not content. This version can
    instead stream the actual PCM samples or the actual Codec2 bitstream out over a UART,
    so the logic analyzer's protocol decoder shows you the real transmitted bytes.
  - Optional manual resample path (48000 -> 8000 via scipy resample_poly) for deterministic
    control instead of relying on the OS/driver to silently resample.
  - UART tap now also reads back anything the STM32 sends (e.g. frame/crc_errors/timing
    stats from its report_stats()) via a background reader thread, printed as [stm32] lines.

Install
-------
    pip install sounddevice numpy pyserial scipy --break-system-packages
    pip install pycodec2 --break-system-packages   # needs libcodec2:
        sudo apt install libcodec2-dev             # Linux/WSL

Run
---
    python codec2_audio_chain.py
    python codec2_audio_chain.py --native-rate 48000        # manual resample path
    python codec2_audio_chain.py --uart-port COM5 --uart-mode bits   # stream Codec2 bits to analyzer
    python codec2_audio_chain.py --uart-port COM5 --uart-mode pcm    # stream raw PCM to analyzer
"""

import argparse
import queue
import sys
import threading
import time
from dataclasses import dataclass

import numpy as np
import sounddevice as sd

try:
    import pycodec2
except ImportError:
    pycodec2 = None

try:
    import serial
except ImportError:
    serial = None

try:
    from scipy.signal import resample_poly
except ImportError:
    resample_poly = None


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CODEC_RATE = 8000            # Codec2's native rate -- always 8000 regardless of native_rate
FRAME_SAMPLES = 160           # 20 ms at 8000 Hz -> one Codec2 3200bps frame
DTYPE = "int16"
QUEUE_DEPTH = 2               # ~40ms worst-case queue latency (was 4 / ~80ms)
WARMUP_FRAMES = 5             # force silence for the first N output frames
STATS_INTERVAL_S = 2.0        # how often to print latency/overrun stats


@dataclass
class Packet:
    samples: np.ndarray
    capture_t: float          # time.perf_counter() at the moment this frame was captured


# ---------------------------------------------------------------------------
# Stats (single writer per counter is fine for println-only usage; not
# hardened for high-contention use, just for visibility while developing)
# ---------------------------------------------------------------------------
class Stats:
    def __init__(self):
        self.input_overruns = 0
        self.output_underruns = 0
        self.dropped_frames = 0
        self.last_latency_ms = 0.0
        self.last_codec_ms = 0.0

    def report(self):
        print(f"[stats] latency={self.last_latency_ms:6.1f}ms  "
              f"codec={self.last_codec_ms:5.2f}ms  "
              f"input_overruns={self.input_overruns}  "
              f"output_underruns={self.output_underruns}  "
              f"dropped={self.dropped_frames}")


# ---------------------------------------------------------------------------
# Logic analyzer tap: stream ACTUAL content over UART, not just a timing pulse.
# Wire the analyzer's RX-decode channel to this adapter's TX pin (+ GND) and
# use its UART protocol decoder to read the bytes back out.
# ---------------------------------------------------------------------------
PACKET_START_BYTE = 0x55


def crc8(data: bytes) -> int:
    """CRC-8, poly 0x07, init 0x00 -- must match the C implementation on
    the STM32 exactly, byte for byte, or every packet will be rejected."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


class UartTap:
    def __init__(self, port: str | None, mode: str, baud: int = 115200):
        self.ser = None
        self.mode = mode
        if port and serial is not None:
            self.ser = serial.Serial(port, baudrate=baud)
        elif port:
            print("pyserial not installed; UART tap disabled.", file=sys.stderr)

    def start_reader(self, stop_event: threading.Event):
        """Background thread: print any lines the STM32 sends back
        (e.g. frame/crc_errors/timing stats from report_stats())."""
        if not self.ser:
            return

        def _reader():
            while not stop_event.is_set():
                try:
                    line = self.ser.readline()
                except Exception:
                    break
                if line:
                    try:
                        text = line.decode("utf-8", errors="replace").strip()
                    except Exception:
                        continue
                    if text:
                        print(f"[stm32] {text}")

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

    def send_pcm(self, frame: np.ndarray):
        if self.ser and self.mode == "pcm":
            self.ser.write(frame.tobytes())

    def send_bits(self, bits: bytes):
        """Frame the Codec2 bitstream as: START | LEN | payload | CRC8.
        LEN carries the payload length explicitly so the STM32 side isn't
        hardcoded to one Codec2 mode's frame size (3200bps=8 bytes,
        2400bps=6 bytes, etc.), and CRC8 lets it detect a corrupted or
        desynced packet and resync on the next START byte instead of
        silently misreading frame boundaries forever."""
        if self.ser and self.mode == "bits":
            packet = bytes([PACKET_START_BYTE, len(bits)]) + bits + bytes([crc8(bits)])
            self.ser.write(packet)


# ---------------------------------------------------------------------------
# Codec2 wrapper
# ---------------------------------------------------------------------------
class Codec2Frame:
    def __init__(self):
        if pycodec2 is None:
            raise RuntimeError("pycodec2 not installed (needs libcodec2 on the system).")
        self.c2 = pycodec2.Codec2(3200)  # bitrate in bps, plain int -- no mode constant in this binding
        assert self.c2.samples_per_frame() == FRAME_SAMPLES

    def encode(self, frame: np.ndarray) -> bytes:
        return self.c2.encode(frame)

    def decode(self, bits: bytes) -> np.ndarray:
        return self.c2.decode(bits)


# ---------------------------------------------------------------------------
# Optional manual resampler (native_rate -> 8000 -> native_rate), used when
# --native-rate is passed instead of opening the stream at 8000 directly.
# ---------------------------------------------------------------------------
class Resampler:
    def __init__(self, native_rate: int):
        self.native_rate = native_rate
        if native_rate == CODEC_RATE:
            self.up = self.down = 1
        else:
            if resample_poly is None:
                raise RuntimeError("scipy not installed; required for --native-rate resampling.")
            # Reduce native_rate/8000 to a small integer ratio.
            from math import gcd
            g = gcd(native_rate, CODEC_RATE)
            self.up = CODEC_RATE // g
            self.down = native_rate // g

    def to_codec_rate(self, block: np.ndarray) -> np.ndarray:
        if self.up == self.down == 1:
            return block
        return resample_poly(block, self.up, self.down).astype(np.int16)

    def from_codec_rate(self, block: np.ndarray) -> np.ndarray:
        if self.up == self.down == 1:
            return block
        return resample_poly(block, self.down, self.up).astype(np.int16)


# ---------------------------------------------------------------------------
# Codec thread
# ---------------------------------------------------------------------------
def codec_worker(in_q: "queue.Queue[Packet]",
                  out_q: "queue.Queue[Packet]",
                  uart: UartTap,
                  stats: Stats,
                  stop_event: threading.Event):
    c2 = Codec2Frame()

    while not stop_event.is_set():
        try:
            pkt = in_q.get(timeout=0.5)
        except queue.Empty:
            continue

        t0 = time.perf_counter()
        bits = c2.encode(pkt.samples)
        uart.send_bits(bits)          # actual Codec2 bitstream out, if enabled
        decoded = c2.decode(bits)
        uart.send_pcm(decoded)        # actual reconstructed PCM out, if enabled
        t1 = time.perf_counter()
        stats.last_codec_ms = (t1 - t0) * 1000.0

        out_pkt = Packet(samples=decoded, capture_t=pkt.capture_t)
        try:
            out_q.put_nowait(out_pkt)
        except queue.Full:
            stats.dropped_frames += 1
            try:
                out_q.get_nowait()
            except queue.Empty:
                pass
            out_q.put_nowait(out_pkt)


# ---------------------------------------------------------------------------
# Audio callback -- never blocks
# ---------------------------------------------------------------------------
def make_callback(in_q: "queue.Queue[Packet]",
                   out_q: "queue.Queue[Packet]",
                   resampler: Resampler,
                   stats: Stats,
                   frame_samples_native: int):
    silence = np.zeros((frame_samples_native, 1), dtype=np.int16)
    warmup_remaining = [WARMUP_FRAMES]

    def callback(indata, outdata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)

        t_capture = time.perf_counter()
        codec_rate_frame = resampler.to_codec_rate(indata.copy().reshape(-1))
        pkt = Packet(samples=codec_rate_frame, capture_t=t_capture)

        try:
            in_q.put_nowait(pkt)
        except queue.Full:
            stats.input_overruns += 1
            try:
                in_q.get_nowait()
            except queue.Empty:
                pass
            in_q.put_nowait(pkt)

        if warmup_remaining[0] > 0:
            warmup_remaining[0] -= 1
            outdata[:] = silence
            return

        try:
            out_pkt = out_q.get_nowait()
            stats.last_latency_ms = (time.perf_counter() - out_pkt.capture_t) * 1000.0
            native_frame = resampler.from_codec_rate(out_pkt.samples)
            outdata[:] = native_frame.reshape(-1, 1)
        except queue.Empty:
            stats.output_underruns += 1
            outdata[:] = silence

    return callback


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-rate", type=int, default=CODEC_RATE,
                         help="Open the audio stream at this rate and manually "
                              "resample to/from 8000 Hz (e.g. 48000). Defaults "
                              "to 8000 (no resampling, let the OS handle it).")
    parser.add_argument("--uart-port", default=None,
                         help="Serial port to stream real audio content to a "
                              "logic analyzer, e.g. COM5 or /dev/ttyUSB0.")
    parser.add_argument("--uart-mode", choices=["pcm", "bits"], default="bits",
                         help="What to stream over --uart-port: reconstructed "
                              "PCM samples, or the raw Codec2 bitstream.")
    parser.add_argument("--input-device", type=int, default=None)
    parser.add_argument("--output-device", type=int, default=None)
    args = parser.parse_args()

    resampler = Resampler(args.native_rate)
    frame_samples_native = int(round(FRAME_SAMPLES * args.native_rate / CODEC_RATE))

    in_q: "queue.Queue[Packet]" = queue.Queue(maxsize=QUEUE_DEPTH)
    out_q: "queue.Queue[Packet]" = queue.Queue(maxsize=QUEUE_DEPTH)
    uart = UartTap(args.uart_port, args.uart_mode)
    stats = Stats()
    stop_event = threading.Event()
    uart.start_reader(stop_event)

    worker = threading.Thread(
        target=codec_worker, args=(in_q, out_q, uart, stats, stop_event), daemon=True
    )
    worker.start()

    callback = make_callback(in_q, out_q, resampler, stats, frame_samples_native)

    print(f"Native stream rate: {args.native_rate} Hz, "
          f"{frame_samples_native} samples/block "
          f"({frame_samples_native / args.native_rate * 1000:.0f} ms/block)")
    print(f"Codec rate: {CODEC_RATE} Hz, {FRAME_SAMPLES} samples/frame")
    if args.uart_port:
        print(f"UART tap: {args.uart_port} streaming {args.uart_mode}")
    print("Ctrl+C to stop.\n")

    try:
        with sd.Stream(samplerate=args.native_rate,
                        blocksize=frame_samples_native,
                        channels=1,
                        dtype=DTYPE,
                        device=(args.input_device, args.output_device),
                        callback=callback):
            while True:
                time.sleep(STATS_INTERVAL_S)
                stats.report()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        stop_event.set()
        worker.join(timeout=2)


if __name__ == "__main__":
    main()