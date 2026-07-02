"""Generates the real audio assets for the full-chain SFX/ducking/loudnorm
demo: synthesizes voice via espeak_engine (real TTS, real word timestamps),
detects SFX triggers, overlays placeholder SFX tones at their real
timestamps, ducks a synthetic placeholder music bed under the result, and
masters with two-pass loudnorm. Prints real measurements at each stage.

Run: python3 -m pipeline.render_audio_demo
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .audio.ffmpeg_bin import ffmpeg_path
from .audio.mix import apply_loudnorm_two_pass, duck_music_under_voice, overlay_sfx, verify_loudness
from .audio.sfx_triggers import (
    SfxCategory,
    WordTiming,
    detect_triggers,
    generate_placeholder_tone,
    resolve_conflicts,
)
from .footage_sourcing.types import ChannelId
from .shot_brief import Beat, BeatType
from .tts.espeak_engine import synthesize, write_wav

FPS = 24
PUBLIC_AUDIO = Path("public/audio")
SCRATCH = Path("/tmp/audio_demo")


def _make_music_bed(out_path: Path, duration_s: float) -> None:
    """Synthetic placeholder music bed -- NOT real music. Two detuned sine
    tones, purely so the ducking chain has something audible to duck."""
    subprocess.run(
        [
            ffmpeg_path(), "-y",
            "-f", "lavfi", "-i", f"sine=frequency=220:duration={duration_s}",
            "-f", "lavfi", "-i", f"sine=frequency=330:duration={duration_s}",
            "-filter_complex", "amix=inputs=2:duration=longest",
            str(out_path),
        ],
        capture_output=True, text=True, check=True,
    )


def render_beat(beat: Beat, channel: ChannelId, label: str) -> dict:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    result = synthesize(beat.text)
    voice_path = SCRATCH / f"{label}_voice.wav"
    write_wav(result, voice_path)

    word_timings = [WordTiming(word=wt.word, start_frame=round(wt.start_ms / 1000 * FPS)) for wt in result.word_timings]
    audio_end_frame = round(result.duration_ms / 1000 * FPS)

    cascade_final_frame = audio_end_frame if beat.cascade else None
    triggers = detect_triggers(beat, word_timings, channel, cascade_final_frame=cascade_final_frame)
    triggers = resolve_conflicts(triggers, fps=FPS)

    sfx_events: list[tuple[float, Path]] = []
    for i, trig in enumerate(triggers):
        tone_path = SCRATCH / f"{label}_sfx_{i}_{trig.category.name}.wav"
        generate_placeholder_tone(trig.category, tone_path)
        sfx_events.append((trig.frame / FPS, tone_path))

    voice_with_sfx = SCRATCH / f"{label}_voice_sfx.wav"
    overlay_sfx(voice_path, sfx_events, voice_with_sfx)

    duration_s = max(result.duration_ms / 1000, 0.5) + 0.5
    music_path = SCRATCH / f"{label}_music.wav"
    _make_music_bed(music_path, duration_s)

    ducked_path = SCRATCH / f"{label}_ducked.wav"
    duck_music_under_voice(voice_with_sfx, music_path, ducked_path)

    mastered_path = PUBLIC_AUDIO / f"{label}_mastered.wav"
    measurement = apply_loudnorm_two_pass(ducked_path, mastered_path)
    verification = verify_loudness(mastered_path)

    return {
        "beat_id": beat.beat_id,
        "text": beat.text,
        "word_timings": [(wt.word, wt.start_frame) for wt in word_timings],
        "audio_end_frame": audio_end_frame,
        "triggers": [
            {"category": t.category.name, "word": t.word, "frame": t.frame, "flavor": t.channel_flavor}
            for t in triggers
        ],
        "first_pass_measurement": {
            "input_i": measurement.input_i,
            "input_tp": measurement.input_tp,
            "input_lra": measurement.input_lra,
        },
        "final_verification": verification,
        "mastered_file": str(mastered_path),
    }


def main() -> None:
    cascade_beat = Beat("cascade-1", BeatType.ESCALATION, "A storm that never stops", 43, cascade=True)
    money_beat = Beat(
        "CH2-hook", BeatType.HOOK,
        "In 2010, a college dropout turned $8,000 into a company worth billions.",
        72,
    )

    report = {
        "cascade1": render_beat(cascade_beat, ChannelId.CH6, "cascade1_full_chain"),
        "ch2_money": render_beat(money_beat, ChannelId.CH2, "ch2_money_sfx_demo"),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
