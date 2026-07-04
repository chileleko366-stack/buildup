"""Tiny, stateless ffmpeg wrappers shared by any real per-beat voice-track
assembly pipeline: generate a silence clip of an exact duration, and
concatenate a list of WAV files in order.

Extracted verbatim from pipeline/render_channel_short.py's original
private `_silence()`/`_concat_wavs()` helpers so pipeline/ch6_short_001.py
can reuse the identical, already-tested real audio assembly logic when
wiring CH6's own voiceover, instead of re-implementing the same two ffmpeg
calls a second time. Behavior is unchanged from the original -- this is
an extraction, not a rewrite.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .ffmpeg_bin import ffmpeg_path


def silence(duration_s: float, sample_rate: int, out_path: Path) -> None:
    duration_s = max(duration_s, 0.0)
    result = subprocess.run(
        [
            ffmpeg_path(), "-y", "-f", "lavfi",
            "-i", f"anullsrc=r={sample_rate}:cl=mono",
            "-t", f"{duration_s:.6f}",
            "-c:a", "pcm_s16le",
            str(out_path),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg silence generation failed:\n{result.stderr}")


def concat_wavs(parts: list[Path], out_path: Path) -> None:
    filelist = out_path.with_suffix(".filelist.txt")
    filelist.write_text("\n".join(f"file '{p.resolve()}'" for p in parts))
    result = subprocess.run(
        [ffmpeg_path(), "-y", "-f", "concat", "-safe", "0", "-i", str(filelist), "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed:\n{result.stderr}")
