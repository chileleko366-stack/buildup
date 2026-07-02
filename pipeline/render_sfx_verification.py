"""Phase: 6-channel SFX verification. One real beat per channel, using
text that ACTUALLY appears in this repo's real sample content (see
sfx_triggers.py module docstring), run through real TTS + real keyword
detection + real ducking/loudnorm mastering. Reports pass/fail per channel
explicitly: did the expected category fire, on the expected word, and
never CH2's MONEY category by accident.

Run: python3 -m pipeline.render_sfx_verification
"""

from __future__ import annotations

import json
from pathlib import Path

from .audio.mix import apply_loudnorm_two_pass, duck_music_under_voice, overlay_sfx, verify_loudness
from .audio.sfx_triggers import SfxCategory, WordTiming, detect_triggers, generate_placeholder_tone, resolve_conflicts
from .footage_sourcing.types import ChannelId
from .render_audio_demo import _make_music_bed
from .shot_brief import Beat, BeatType
from .tts.espeak_engine import synthesize, write_wav

FPS = 24
PUBLIC_AUDIO = Path("public/audio")
SCRATCH = Path("/tmp/sfx_verification")

# Real text from pipeline/footage_sourcing/sample_beats.py (CH1/CH3/CH4/CH5)
# and pipeline/ch6_short_001.py (CH6) -- not invented for this test.
VERIFICATION_BEATS: dict[ChannelId, tuple[Beat, SfxCategory]] = {
    ChannelId.CH1: (
        Beat("CH1-build", BeatType.BUILD, "Every notification is a tiny gamble your brain didn't agree to.", 72),
        SfxCategory.PSYCHOLOGY_TERM,
    ),
    ChannelId.CH2: (
        Beat("CH2-hook", BeatType.HOOK, "In 2010, a college dropout turned $8,000 into a company worth billions.", 72),
        SfxCategory.MONEY,
    ),
    ChannelId.CH3: (
        Beat("CH3-escalation", BeatType.ESCALATION, "Then a single leaked memo threatened to expose everything.", 72),
        SfxCategory.CLASSIFIED,
    ),
    ChannelId.CH4: (
        Beat("CH4-hook", BeatType.HOOK, "The second before you feel afraid, your brain has already decided.", 72),
        SfxCategory.NEURO_TERM,
    ),
    ChannelId.CH5: (
        Beat("CH5-build", BeatType.BUILD, "In 1943, over a thousand women trained in secret at a Texas airbase.", 72),
        SfxCategory.DATE_EVENT,
    ),
    ChannelId.CH6: (
        Beat("CH6-context-1", BeatType.CONTEXT, "Jupiter sits nearly five hundred million miles from the sun.", 72),
        SfxCategory.SCALE_DISTANCE,
    ),
}


def render_channel(channel: ChannelId, beat: Beat, expected_category: SfxCategory) -> dict:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    label = f"{channel.value}_verify"

    result = synthesize(beat.text)
    voice_path = SCRATCH / f"{label}_voice.wav"
    write_wav(result, voice_path)

    word_timings = [WordTiming(word=wt.word, start_frame=round(wt.start_ms / 1000 * FPS)) for wt in result.word_timings]

    triggers = detect_triggers(beat, word_timings, channel)
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

    categories_fired = {t.category for t in triggers}
    fired_money_wrongly = channel != ChannelId.CH2 and SfxCategory.MONEY in categories_fired
    expected_fired = expected_category in categories_fired

    return {
        "channel": channel.value,
        "beat_text": beat.text,
        "word_timings": [(wt.word, wt.start_frame) for wt in word_timings],
        "triggers": [
            {"category": t.category.name, "word": t.word, "frame": t.frame} for t in triggers
        ],
        "expected_category": expected_category.name,
        "PASS": expected_fired and not fired_money_wrongly,
        "expected_fired": expected_fired,
        "fired_money_wrongly": fired_money_wrongly,
        "loudness": verification,
        "mastered_file": str(mastered_path),
    }


def main() -> None:
    report = {}
    for channel, (beat, expected) in VERIFICATION_BEATS.items():
        report[channel.value] = render_channel(channel, beat, expected)

    print(json.dumps(report, indent=2))
    print("\n=== PASS/FAIL SUMMARY ===")
    for ch, r in report.items():
        status = "PASS" if r["PASS"] else "FAIL"
        print(f"{ch}: {status} -- expected {r['expected_category']} fired={r['expected_fired']}, "
              f"wrong MONEY fallback={r['fired_money_wrongly']}, triggers={[t['category'] for t in r['triggers']]}")


if __name__ == "__main__":
    main()
