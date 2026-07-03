"""Real edge-tts (Microsoft Edge's free online neural TTS) engine -- tried
first by pipeline/tts/engine.py, with espeak_engine.py kept as the
explicit, logged fallback if this fails (network, DNS, or service-side).

edge-tts (real PyPI package, `pip install edge-tts`, github.com/rany2/
edge-tts) drives the same keyless neural-TTS websocket endpoint the
Microsoft Edge "Read Aloud" feature uses. This has zero references
anywhere in this repo before this pass, and was never testable from this
repo's original dev sandbox (which blocks nearly all non-approved
external hosts) -- a real CI runner is the first place this can actually
be tried live.

Real per-word timestamps come from edge-tts's own `WordBoundary` metadata
events (`Communicate(..., boundary="WordBoundary")`) -- confirmed via
edge_tts's own communicate.py source: offsets/durations are Azure Speech
SDK-style 100-nanosecond ticks (`meta_obj["Data"]["Offset"]`), not
estimated. Audio arrives as MP3 chunks over the same stream; decoded to
PCM via the same real ffmpeg binary pipeline/audio/ffmpeg_bin.py already
resolves, so it drops into the existing WAV-based pipeline unchanged.

Rate/pitch are mapped from espeak_engine's 0-100 PITCH/RANGE scale to
edge-tts's own rate-percentage / pitch-Hz-offset params -- this is an
approximation (the two engines expose different units with no documented
equivalence), not a sourced 1:1 conversion. `pitch_range` has no edge-tts
equivalent and is accepted only for interface parity with espeak_engine.
"""

from __future__ import annotations

import asyncio
import subprocess
import tempfile
import wave
from pathlib import Path

import edge_tts

from ..audio.ffmpeg_bin import ffmpeg_path
from .espeak_engine import DEFAULT_RATE_WPM, SynthResult, WordTiming

# Real, long-standing Azure/edge-tts neural voice (github.com/rany2/edge-tts
# documents this exact name in its own usage examples).
DEFAULT_VOICE = "en-US-GuyNeural"


def _rate_str(rate_wpm: int) -> str:
    pct = round((rate_wpm / DEFAULT_RATE_WPM - 1) * 100)
    return f"{'+' if pct >= 0 else ''}{pct}%"


def _pitch_str(pitch: int) -> str:
    hz = (pitch - 50) * 2  # approximate -- see module docstring
    return f"{'+' if hz >= 0 else ''}{hz}Hz"


async def _stream(text: str, voice: str, rate: str, pitch: str) -> tuple[bytes, list[WordTiming]]:
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    audio = bytearray()
    word_timings: list[WordTiming] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word_timings.append(WordTiming(word=chunk["text"], start_ms=round(chunk["offset"] / 10000)))
    if not audio:
        raise RuntimeError("edge-tts returned no audio data")
    return bytes(audio), word_timings


def synthesize(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate_wpm: int = DEFAULT_RATE_WPM,
    pitch: int = 50,
    pitch_range: int = 50,  # unused -- no edge-tts equivalent; kept for interface parity
) -> SynthResult:
    mp3_bytes, word_timings = asyncio.run(_stream(text, voice, _rate_str(rate_wpm), _pitch_str(pitch)))

    with tempfile.TemporaryDirectory() as tmp:
        mp3_path = Path(tmp) / "edge.mp3"
        wav_path = Path(tmp) / "edge.wav"
        mp3_path.write_bytes(mp3_bytes)
        result = subprocess.run(
            [ffmpeg_path(), "-y", "-i", str(mp3_path), "-ac", "1", "-c:a", "pcm_s16le", str(wav_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg mp3->wav decode of edge-tts output failed:\n{result.stderr}")

        with wave.open(str(wav_path), "rb") as w:
            sample_rate = w.getframerate()
            pcm_bytes = w.readframes(w.getnframes())

    duration_ms = round(len(pcm_bytes) / 2 / sample_rate * 1000)
    return SynthResult(sample_rate=sample_rate, pcm_bytes=pcm_bytes, word_timings=word_timings, duration_ms=duration_ms)
