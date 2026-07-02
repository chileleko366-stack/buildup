"""Real audio-mixing chain: sidechain ducking + two-pass loudness mastering.

Every numeric value below is sourced from a real, working repository --
verified by fetching its actual source file, not a tutorial snippet.
Where no real reference could be found, that's stated explicitly rather
than filled with a guess (see module-level NOT_SOURCED notes).

## Ducking (sidechaincompress)

Source: github.com/Upload-Post/avatar-mix, `scripts/composite.py`,
`mix_audio()` function (fetched directly, not paraphrased from docs).
This is real, executable Python in a repo with actual commit history --
not a gist, not a tutorial. Verbatim from that function:

    thr = a.get("duck_threshold", 0.05)
    ratio = a.get("duck_ratio", 8)
    ...
    fc.append(f"[{mi}:a]volume={vol}dB[m]")   # vol default: -22 (music_volume_db)
    fc.append(f"[m]{voice_key}sidechaincompress=threshold={thr}:ratio={ratio}:"
              f"attack=20:release=400[duck]")
    ...
    # elsewhere in the same file: final limiter = "alimiter=limit=0.95"

So: music pre-attenuated -22dB, sidechaincompress threshold=0.05 ratio=8
attack=20ms release=400ms, final alimiter=limit=0.95.

NOT_SOURCED: avatar-mix's exact final-mix filter (how [va] and [duck] get
merged, e.g. amix vs amerge, and its exact parameters) was not visible in
what was fetched -- the function was truncated after the sidechaincompress
line in the tool output. This module uses `amix=inputs=N:duration=longest
:normalize=0` for the merge step -- `normalize=0` is added here because
ffmpeg's amix defaults to `normalize=1`, which auto-attenuates as more
inputs join and would undo the levels this chain just carefully set; this
is standard, widely-documented amix behavior, not a value pulled from
avatar-mix's own (unseen) merge line.

Cross-check: github.com/SimpelMe/ffmpeg-leveler (real, 47 commits, a repo
dedicated to ducking) does NOT use sidechaincompress at all -- it achieves
ducking via `compand` gating + `dynaudnorm` leveling instead. Worth
knowing if sidechaincompress ever behaves oddly on a given input; not
implemented here since avatar-mix's sidechaincompress approach is what
this module follows.

## EQ "pocket cut" for vocal presence ahead of ducking

NOT_SOURCED as asked for. Searched specifically for a real repo doing a
music-side EQ dip to carve space for vocal presence before ducking; found
none with verifiable exact values. The closest real, verified reference is
github.com/brolnickij/yt-dbl (real, 222 commits, real releases),
`src/yt_dbl/utils/audio_processing.py`, but that's a VOICE-side de-esser,
not a music-side pocket cut:

    "highshelf=gain=-3:frequency=4500:width_type=q:width=0.7,"
    "compand=attacks=0.005:decays=0.05:points=-80/-80|-6/-8|0/-3:volume=0"

This module does not apply a music-bed pocket EQ cut. If you want one
added, it needs either a real sourced reference or an explicit decision to
design it without one (same "flag, don't invent" rule as everything else
in this repo).

## Two-pass loudness mastering (loudnorm)

Two independent real repos converge on -16 LUFS integrated:
- github.com/brolnickij/yt-dbl: `loudnorm=I=-16:TP=-1.5:LRA=11` (single-pass
  in their code, not two-pass -- see below)
- github.com/SimpelMe/ffmpeg-leveler: `loudnorm=i=-16.0:lra=12.0:tp=-3.0`
  (also not shown as two-pass in what was fetched)

NOT_SOURCED: "-14 LUFS for YouTube" is commonly repeated online but this
session could not verify it as an actual value used in any real repo's
working code -- neither of the two real repos found uses it. Using -16
LUFS / -1.5 dBTP / 11 LRA instead (yt-dbl's exact values -- chosen over
ffmpeg-leveler's because yt-dbl is the more actively-maintained, larger
repo: 222 commits and real tagged releases vs. 47 commits).

The TWO-PASS MECHANISM itself (measure with print_format=json, then apply
with measured_I/measured_TP/measured_LRA/measured_thresh + linear=true) is
FFmpeg's own documented technique for the loudnorm filter, and is what
several dedicated real repos automate by name (github.com/Piklesh/auto-
loudnorm, github.com/indiscipline/ffmpeg-loudnorm-helper,
github.com/lbcard/2pass_loudnorm) -- their existence as real, single-
purpose, GPL-licensed-sounding tools was confirmed, but this session did
not independently pull their exact source code to re-verify the mechanism
byte-for-byte (only their README descriptions). The mechanism implemented
below matches those descriptions and FFmpeg's own filter semantics.

## Voice "de-robotify" compression (`apply_naturalness_processing`)

Source: github.com/nodeblackbox/Kokoro-Voice-Api (real repo, 7 commits,
single contributor -- thin history, flagged as such, but its documented
API parameters are concrete and directly usable, not paraphrased). Its
documented dynamic-range-compression defaults:

    "ratio": 4.0, "threshold": -20.0, "attack": 0.003, "release": 0.1

(threshold in dB, attack/release in seconds per that repo's own docs --
i.e. 3ms attack, 100ms release). Converted here to ffmpeg's `acompressor`
filter, whose `threshold` argument is LINEAR amplitude (0-1), not dB --
standard dB-to-linear conversion `10**(dB/20)`, so -20dB -> 0.1 exactly,
not an invented number:

    acompressor=threshold=0.1:ratio=4:attack=3:release=100:makeup=1

That repo also documents a reverb step (`room_size=0.3, damping=0.5,
wet_level=0.2`), which is NOT applied here: those three parameters name a
different DSP algorithm (a Schroeder/Freeverb-style room-simulation reverb,
the same parameter shape as the `pedalboard` Python library's `Reverb`
class) with no documented 1:1 mapping to ffmpeg's own reverb-adjacent
filters (`aecho`, `afir`). Approximating one from the other would be
inventing a value, not sourcing one -- so only the compression step (a
direct, exact filter match) is applied. NOT_SOURCED: the reverb step.

This does not make espeak-ng sound like Kokoro or a human recording --
espeak-ng's own project documentation states its formant-synthesis
approach is "not as natural or smooth as larger [sample-based]
synthesizers," which compression alone cannot fix. What compression does,
verified by real use in vocal-processing chains, is even out the flat,
uniformly-loud quality of raw synthesized speech, which reads as part of
"robotic" alongside the pitch-flatness handled separately in
`pipeline/tts/voice_profiles.py`.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .ffmpeg_bin import ffmpeg_path

DUCK_MUSIC_VOLUME_DB = -22.0  # avatar-mix composite.py: music_volume_db default
DUCK_THRESHOLD = 0.05  # avatar-mix composite.py: duck_threshold default
DUCK_RATIO = 8  # avatar-mix composite.py: duck_ratio default
DUCK_ATTACK_MS = 20  # avatar-mix composite.py: hardcoded in sidechaincompress call
DUCK_RELEASE_MS = 400  # avatar-mix composite.py: hardcoded in sidechaincompress call
FINAL_LIMITER_CEILING = 0.95  # avatar-mix composite.py: "alimiter=limit=0.95"

LOUDNORM_TARGET_I = -16.0  # yt-dbl audio_processing.py: loudnorm=I=-16
LOUDNORM_TARGET_TP = -1.5  # yt-dbl audio_processing.py: TP=-1.5
LOUDNORM_TARGET_LRA = 11.0  # yt-dbl audio_processing.py: LRA=11

# nodeblackbox/Kokoro-Voice-Api documented compressor defaults: ratio=4.0,
# threshold=-20dB (-> 0.1 linear, standard dB-to-linear conversion),
# attack=3ms, release=100ms. See module docstring's "de-robotify" section.
NATURALNESS_COMPRESSOR_THRESHOLD = 0.1
NATURALNESS_COMPRESSOR_RATIO = 4.0
NATURALNESS_COMPRESSOR_ATTACK_MS = 3.0
NATURALNESS_COMPRESSOR_RELEASE_MS = 100.0


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def duck_music_under_voice(voice_path: Path, music_path: Path, out_path: Path) -> None:
    """Sidechain-ducks `music_path` under `voice_path`, per avatar-mix's
    mix_audio() chain (see module docstring for the exact sourced filter
    string)."""
    filter_complex = (
        "[0:a]asplit=2[va][vk];"
        f"[1:a]volume={DUCK_MUSIC_VOLUME_DB}dB[m];"
        f"[m][vk]sidechaincompress=threshold={DUCK_THRESHOLD}:ratio={DUCK_RATIO}:"
        f"attack={DUCK_ATTACK_MS}:release={DUCK_RELEASE_MS}[duck];"
        "[va][duck]amix=inputs=2:duration=longest:normalize=0[mixed];"
        f"[mixed]alimiter=limit={FINAL_LIMITER_CEILING}[out]"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = _run(
        [
            ffmpeg_path(), "-y",
            "-i", str(voice_path),
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[out]",
            str(out_path),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg ducking mix failed:\n{result.stderr}")


def apply_naturalness_processing(voice_path: Path, out_path: Path) -> None:
    """Applies the sourced de-robotify compressor (see module docstring)
    to a raw synthesized voice track, before ducking/SFX/mastering."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    filter_str = (
        f"acompressor=threshold={NATURALNESS_COMPRESSOR_THRESHOLD}:"
        f"ratio={NATURALNESS_COMPRESSOR_RATIO}:"
        f"attack={NATURALNESS_COMPRESSOR_ATTACK_MS}:"
        f"release={NATURALNESS_COMPRESSOR_RELEASE_MS}:makeup=1"
    )
    result = _run([ffmpeg_path(), "-y", "-i", str(voice_path), "-af", filter_str, str(out_path)])
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg naturalness compression failed:\n{result.stderr}")


def overlay_sfx(base_audio: Path, events: list[tuple[float, Path]], out_path: Path) -> None:
    """Overlays one-shot SFX cues onto `base_audio` at real timestamps.

    `events` is (start_seconds, sfx_wav_path) pairs -- mirrors the shape of
    avatar-mix composite.py's own `events = [(time_seg, ruta_sfx, gain_db)]`
    parameter (that function signature was confirmed in the fetched source;
    its internal event-mixing implementation was truncated in what was
    fetched, so this is this module's own construction of the same idea
    using `adelay` + `amix`, not a byte-for-byte copy of unseen code).

    NOT_SOURCED: gain_db per event (avatar-mix takes one) is not applied
    here -- every event plays at the SFX asset's own recorded level. Add a
    per-event gain filter if/when real SFX assets with inconsistent levels
    are sourced.
    """
    if not events:
        import shutil

        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(base_audio, out_path)
        return

    inputs: list[str] = ["-i", str(base_audio)]
    filter_parts: list[str] = []
    mix_labels = ["[0:a]"]
    for i, (start_s, sfx_path) in enumerate(events, start=1):
        inputs += ["-i", str(sfx_path)]
        delay_ms = round(start_s * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay_ms}:all=1[sfx{i}]")
        mix_labels.append(f"[sfx{i}]")
    filter_parts.append(f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:normalize=0[out]")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = _run(
        [ffmpeg_path(), "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[out]", str(out_path)]
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg SFX overlay failed:\n{result.stderr}")


@dataclass(frozen=True)
class LoudnormMeasurement:
    input_i: float
    input_tp: float
    input_lra: float
    input_thresh: float
    target_offset: float


def _measure_loudnorm(path: Path, target_i: float, target_tp: float, target_lra: float) -> LoudnormMeasurement:
    result = _run(
        [
            ffmpeg_path(), "-hide_banner",
            "-i", str(path),
            "-af", f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:print_format=json",
            "-f", "null", "-",
        ]
    )
    matches = re.findall(r"\{[^{}]*\}", result.stderr, re.DOTALL)
    if not matches:
        raise RuntimeError(f"Could not parse loudnorm measurement JSON from ffmpeg stderr:\n{result.stderr}")
    data = json.loads(matches[-1])
    return LoudnormMeasurement(
        input_i=float(data["input_i"]),
        input_tp=float(data["input_tp"]),
        input_lra=float(data["input_lra"]),
        input_thresh=float(data["input_thresh"]),
        target_offset=float(data["target_offset"]),
    )


def apply_loudnorm_two_pass(
    in_path: Path,
    out_path: Path,
    target_i: float = LOUDNORM_TARGET_I,
    target_tp: float = LOUDNORM_TARGET_TP,
    target_lra: float = LOUDNORM_TARGET_LRA,
) -> LoudnormMeasurement:
    """Genuine two-pass loudnorm: pass 1 measures (print_format=json), pass
    2 applies using the measured values with linear=true, per FFmpeg's own
    documented technique for this filter (see module docstring)."""
    measurement = _measure_loudnorm(in_path, target_i, target_tp, target_lra)

    filter_str = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:"
        f"measured_I={measurement.input_i}:measured_TP={measurement.input_tp}:"
        f"measured_LRA={measurement.input_lra}:measured_thresh={measurement.input_thresh}:"
        f"offset={measurement.target_offset}:linear=true:print_format=summary"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = _run([ffmpeg_path(), "-y", "-i", str(in_path), "-af", filter_str, str(out_path)])
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg loudnorm second pass failed:\n{result.stderr}")
    return measurement


def verify_loudness(path: Path, target_i: float = LOUDNORM_TARGET_I, target_tp: float = LOUDNORM_TARGET_TP, target_lra: float = LOUDNORM_TARGET_LRA) -> dict:
    """Re-measures the OUTPUT file the same way the two-pass tools verify
    their own result (a loudnorm print_format=json pass against the
    already-normalized file), plus astats for a broader traditional read
    -- both explicitly named as acceptable by the user's own request."""
    post = _measure_loudnorm(path, target_i, target_tp, target_lra)

    astats_result = _run(
        [ffmpeg_path(), "-hide_banner", "-i", str(path), "-af", "astats=metadata=0", "-f", "null", "-"]
    )
    astats_text = astats_result.stderr

    def _grab(label: str) -> str | None:
        m = re.search(rf"{re.escape(label)}:\s*(-?[\d.]+)", astats_text)
        return m.group(1) if m else None

    return {
        "loudnorm_remeasure": {
            "input_i_lufs": post.input_i,
            "input_tp_dbtp": post.input_tp,
            "input_lra_lu": post.input_lra,
        },
        "astats": {
            "peak_level_db": _grab("Peak level dB"),
            "rms_level_db": _grab("RMS level dB"),
        },
    }
