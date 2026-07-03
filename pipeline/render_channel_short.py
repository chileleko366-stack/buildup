"""Phase 4: shared renderer that turns one channel's BeatSpec list
(pipeline/channel_scripts.py) into a real, fully-mastered audio track and a
real ShotBrief JSON with real per-beat timing -- reusing every already-
built, already-tested system from prior passes (this is composition, not a
new engineering system per channel, per the user's explicit instruction):

- pipeline/tts/espeak_engine.py + voice_profiles.py: real TTS + real
  per-word timestamps + this channel's real pitch/range profile.
- pipeline/audio/mix.py's apply_naturalness_processing(): the same
  de-robotify compressor proven on the cascade-1 gate.
- pipeline/audio/sfx_triggers.py's detect_triggers()/resolve_conflicts():
  the same real per-channel keyword detection proven in
  render_sfx_verification.py, now applied to every beat in a full short,
  not just one verification beat per channel.
- pipeline/audio/music.py's real per-channel CC0 track.
- pipeline/audio/mix.py's duck_music_under_voice() / apply_loudnorm_two_pass():
  the SAME chain every prior audio gate has used, unchanged.

## Beat-duration / audio-sync design (new for this pass)

Each beat's `duration_frames` is set from that beat's OWN real measured
audio length (audio_end_frame) plus a fixed nominal 18-frame tail hold
(matching WordCascade's `finalHoldFrames` / KineticCaption's
`kineticCaptionDurationFromTimings` tail default of 18 -- both primitives
already use 18 as their default, not a new number invented here). To keep
the audio track and the video's per-beat Sequence boundaries EXACTLY in
sync with zero cumulative drift across ~16 beats, the silence gap
appended after each beat's voice clip is NOT a fixed 0.75s -- it's
computed per beat as `duration_frames/fps - actual_voice_duration_s`,
i.e. whatever's needed to make that beat's audio segment occupy exactly
`duration_frames` worth of time, matching the video Sequence's length
exactly. Rounding error is corrected per-beat instead of accumulating.

Run: python3 -m pipeline.render_channel_short CH1
(or import render_channel_short() directly for all channels)
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from .audio.ffmpeg_bin import ffmpeg_path
from .audio.mix import apply_loudnorm_two_pass, apply_naturalness_processing, duck_music_under_voice, verify_loudness
from .audio.music import get_channel_music_clip
from .audio.sfx_triggers import WordTiming as SfxWordTiming, detect_triggers, generate_placeholder_tone, resolve_conflicts
from .channel_scripts import CHANNEL_SCRIPTS, SHORT_IDS, BeatSpec
from .footage_sourcing.attach_background import resolve_beat_background
from .footage_sourcing.types import ChannelId, VisualKeyword
from .shot_brief import Beat, Composition, GradingVariant, KenBurns, ShotBrief, WordTiming, _validate_shot_brief
from .tts.engine import synthesize
from .tts.espeak_engine import write_wav
from .tts.voice_profiles import VOICE_PROFILES

FPS = 24
TAIL_FRAMES = 18  # matches WordCascade/KineticCaption's own default tail-hold
PUBLIC_AUDIO = Path("public/audio")
DATA_DIR = Path("src/remotion/data")
SCRATCH_ROOT = Path("/tmp/channel_shorts")

_PANS = ["left", "right", "up", "down"]


def _alternating_pan(i: int) -> str:
    return _PANS[i % len(_PANS)]


def _kb(i: int) -> KenBurns:
    return KenBurns(zoom_start=1.0, zoom_end=1.08, pan_direction=_alternating_pan(i), pan_amount_ratio=0.04)


def _silence(duration_s: float, sample_rate: int, out_path: Path) -> None:
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


def _concat_wavs(parts: list[Path], out_path: Path) -> None:
    filelist = out_path.with_suffix(".filelist.txt")
    filelist.write_text("\n".join(f"file '{p.resolve()}'" for p in parts))
    result = subprocess.run(
        [ffmpeg_path(), "-y", "-f", "concat", "-safe", "0", "-i", str(filelist), "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed:\n{result.stderr}")


def render_channel_short(channel: ChannelId) -> dict:
    beat_specs, source_note = CHANNEL_SCRIPTS[channel]
    short_id = SHORT_IDS[channel]
    profile = VOICE_PROFILES[channel]

    scratch = SCRATCH_ROOT / channel.value
    scratch.mkdir(parents=True, exist_ok=True)

    beats: list[Beat] = []
    voice_parts: list[Path] = []
    global_events: list[tuple[float, Path]] = []
    cursor_frame = 0
    sample_rate: int | None = None
    tts_engines_used: list[str] = []

    for i, spec in enumerate(beat_specs):
        result, engine_name = synthesize(spec.text, pitch=profile.pitch, pitch_range=profile.pitch_range)
        print(f"[{channel.value}] {spec.beat_id}: TTS engine = {engine_name}", file=sys.stderr)
        tts_engines_used.append(engine_name)
        sample_rate = result.sample_rate
        raw_path = scratch / f"{spec.beat_id}_raw.wav"
        write_wav(result, raw_path)

        natural_path = scratch / f"{spec.beat_id}_natural.wav"
        apply_naturalness_processing(raw_path, natural_path)

        word_timings_local = [
            SfxWordTiming(word=wt.word, start_frame=round(wt.start_ms / 1000 * FPS)) for wt in result.word_timings
        ]
        audio_end_frame = round(result.duration_ms / 1000 * FPS)
        duration_frames = audio_end_frame + TAIL_FRAMES

        visual_keywords: list[VisualKeyword] = []
        if not spec.cascade and spec.domain is not None and spec.keyword is not None:
            visual_keywords = [
                VisualKeyword(
                    text=spec.keyword, domain=spec.domain, channel=channel,
                    beat_id=spec.beat_id, named_entity=spec.named_entity,
                )
            ]

        bg_url, bg_status = resolve_beat_background(visual_keywords)

        beat = Beat(
            beat_id=spec.beat_id,
            beat_type=spec.beat_type,
            text=spec.text,
            duration_frames=duration_frames,
            cascade=spec.cascade,
            grading=GradingVariant.NEUTRAL,
            ken_burns=_kb(i),
            visual_keywords=visual_keywords,
            source_snippet=source_note,
            word_timings=[WordTiming(word=w.word, start_frame=w.start_frame) for w in word_timings_local],
            audio_end_frame=audio_end_frame,
            background_asset_url=bg_url,
            background_sourcing_status=bg_status,
        )
        beats.append(beat)

        # SFX detection -- same real detect_triggers()/resolve_conflicts()
        # every prior audio gate used, scoped to this one beat's local
        # timeline, then placed at its GLOBAL position below.
        cascade_final_frame = audio_end_frame if spec.cascade else None
        triggers = detect_triggers(beat, word_timings_local, channel, cascade_final_frame=cascade_final_frame)
        triggers = resolve_conflicts(triggers, fps=FPS)
        for j, trig in enumerate(triggers):
            tone_path = scratch / f"{spec.beat_id}_sfx_{j}_{trig.category.name}.wav"
            generate_placeholder_tone(trig.category, tone_path)
            global_seconds = (cursor_frame + trig.frame) / FPS
            global_events.append((global_seconds, tone_path))

        # Per-beat silence pad, computed (not fixed) so this beat's audio
        # segment occupies EXACTLY duration_frames/FPS seconds -- see
        # module docstring's sync-design section.
        actual_voice_s = result.duration_ms / 1000
        pad_s = duration_frames / FPS - actual_voice_s
        pad_path = scratch / f"{spec.beat_id}_pad.wav"
        _silence(pad_s, sample_rate, pad_path)

        voice_parts.append(natural_path)
        voice_parts.append(pad_path)

        cursor_frame += duration_frames

    concatenated_path = scratch / "voice_concat.wav"
    _concat_wavs(voice_parts, concatenated_path)

    voice_with_sfx_path = scratch / "voice_sfx.wav"
    if global_events:
        from .audio.mix import overlay_sfx
        overlay_sfx(concatenated_path, global_events, voice_with_sfx_path)
    else:
        voice_with_sfx_path = concatenated_path

    total_duration_s = cursor_frame / FPS
    music_path = scratch / "music.wav"
    get_channel_music_clip(channel, total_duration_s, music_path)

    ducked_path = scratch / "ducked.wav"
    duck_music_under_voice(voice_with_sfx_path, music_path, ducked_path)

    mastered_path = PUBLIC_AUDIO / f"{short_id}.wav"
    measurement = apply_loudnorm_two_pass(ducked_path, mastered_path)
    verification = verify_loudness(mastered_path)

    brief = ShotBrief(
        channel=channel,
        short_id=short_id,
        beats=beats,
        composition=Composition(primary_anchor=0.5),
        fps=FPS,
    )
    _validate_shot_brief(brief)

    brief_dict = asdict(brief)
    brief_dict["channel"] = channel.value
    for b in brief_dict["beats"]:
        b["beat_type"] = b["beat_type"].value if hasattr(b["beat_type"], "value") else b["beat_type"]
        b["grading"] = b["grading"].value if hasattr(b["grading"], "value") else b["grading"]
        for kw in b["visual_keywords"]:
            kw["domain"] = kw["domain"].value if hasattr(kw["domain"], "value") else kw["domain"]
            kw["channel"] = kw["channel"].value if hasattr(kw["channel"], "value") else kw["channel"]

    data_path = DATA_DIR / f"{short_id}.json"
    data_path.write_text(json.dumps(brief_dict, indent=2))

    total_seconds = sum(b.duration_frames for b in beats) / FPS
    report = {
        "channel": channel.value,
        "short_id": short_id,
        "beat_count": len(beats),
        "total_seconds": round(total_seconds, 2),
        "audio_file": f"audio/{mastered_path.name}",
        "data_file": str(data_path),
        "tts_engines_used": tts_engines_used,
        "first_pass_measurement": {
            "input_i": measurement.input_i, "input_tp": measurement.input_tp, "input_lra": measurement.input_lra,
        },
        "final_verification": verification,
    }
    return report


def main() -> None:
    if len(sys.argv) > 1:
        channels = [ChannelId(sys.argv[1])]
    else:
        channels = list(CHANNEL_SCRIPTS.keys())

    reports = {}
    for channel in channels:
        print(f"--- Rendering {channel.value} ---", file=sys.stderr)
        reports[channel.value] = render_channel_short(channel)

    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
