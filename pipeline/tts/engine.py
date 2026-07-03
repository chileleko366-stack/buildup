"""Unified TTS entry point: tries edge_engine.py (real online neural voice)
first, falls back to espeak_engine.py (this repo's original, robotic,
network-independent engine) if edge-tts fails for any reason. The
fallback is explicit and logged to stderr -- never silent -- and
espeak-ng itself is kept, not removed, per the fail-loud rule this repo
follows elsewhere (e.g. footage_sourcing's NotConfiguredError pattern).
"""

from __future__ import annotations

import sys

from . import edge_engine, espeak_engine
from .espeak_engine import SynthResult


def synthesize(
    text: str,
    rate_wpm: int = espeak_engine.DEFAULT_RATE_WPM,
    pitch: int = espeak_engine.DEFAULT_PITCH,
    pitch_range: int = espeak_engine.DEFAULT_PITCH_RANGE,
) -> tuple[SynthResult, str]:
    """Returns (result, engine_name) so callers can log/record which engine
    actually produced the audio for this beat."""
    try:
        result = edge_engine.synthesize(text, rate_wpm=rate_wpm, pitch=pitch, pitch_range=pitch_range)
        return result, "edge-tts"
    except Exception as e:
        print(f"edge-tts FAILED ({type(e).__name__}: {e}) -- falling back to espeak-ng", file=sys.stderr)
        result = espeak_engine.synthesize(text, rate_wpm=rate_wpm, pitch=pitch, pitch_range=pitch_range)
        return result, "espeak-ng"
