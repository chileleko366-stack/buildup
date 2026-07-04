"""CH6 (Red Space Facts) shot brief: "Jupiter's centuries-long storm".

HAND-AUTHORED, NOT LLM OUTPUT -- no LLM provider key is configured in this
environment (see keyword_extraction.py), so there is no script-generation
step to run. This stands in for what that step would eventually produce,
same pattern as pipeline/footage_sourcing/sample_beats.py in Phase 2.

Every factual claim below is a well-established, generally-known
astronomical fact about Jupiter (size, rotation period, composition, the
Great Red Spot's observed history). `source_snippet` notes this honestly --
it is NOT a citation to a specific fetched source document, because no
such document was fed to an LLM here. 03_SCRIPT_BIBLE.md §4's "every
factual claim must be traceable to the source material fed to the LLM" is
a rule for the real pipeline (LLM + source documents); it doesn't apply
literally to hand-authored content with no LLM in the loop, but the honesty
principle behind it still does -- so this is flagged rather than presented
as if it went through that verification step.

Follows 03_SCRIPT_BIBLE.md §3's CH6 arc: "Hook (an object/phenomenon in
space) -> what it looks like from Earth -> scale-context build -> cascade
-> the reveal of true scale/distance/violence of the phenomenon -> cascade
-> the number (distance, temperature, force) -> what it means for context."
Grading stays `neutral` throughout -- 02_VISUAL_BIBLE.md §5 doesn't call
out CH6 for either non-neutral variant (those are named for CH3/CH4's
tension beats and CH5's history niche), and CH6's own tone
("awe-inspiring, precise, cosmic" per channelConfigs.py) reads as letting
real space imagery carry the shot rather than grading it -- a design
choice, not a bible-confirmed rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .audio.mix import apply_loudnorm_two_pass, apply_naturalness_processing, verify_loudness
from .audio.wav_utils import concat_wavs, silence
from .footage_sourcing.attach_background import resolve_beat_background
from .footage_sourcing.types import ChannelId, Domain, VisualKeyword
from .shot_brief import Beat, BeatType, Composition, KenBurns, ShotBrief, WordTiming
from .tts.engine import synthesize
from .tts.espeak_engine import write_wav
from .tts.voice_profiles import VOICE_PROFILES

CH = ChannelId.CH6
SHORT_ID = "ch6-jupiter-red-spot-001"
FPS = 24
TAIL_FRAMES = 18  # matches WordCascade/KineticCaption's own default tail-hold -- same constant render_channel_short.py uses
PUBLIC_AUDIO = Path("public/audio")
SCRATCH_ROOT = Path("/tmp/channel_shorts") / CH.value
SOURCE_NOTE = (
    "General astronomical knowledge (Jupiter's size, rotation, composition, "
    "and the Great Red Spot's continuous observation since the 1830s) -- "
    "not a fetched/cited source document; no LLM+source-material step ran."
)


def _kw(text: str, named_entity: str, beat_id: str) -> list[VisualKeyword]:
    return [VisualKeyword(text=text, domain=Domain.SPACE, channel=CH, beat_id=beat_id, named_entity=named_entity)]


def _kb(pan_direction: str, zoom_end: float = 1.35) -> KenBurns:
    return KenBurns(zoom_start=1.0, zoom_end=zoom_end, pan_direction=pan_direction, pan_amount_ratio=0.08)


_PANS = ["left", "right", "up", "down"]


def _alternating_pan(i: int) -> str:
    return _PANS[i % len(_PANS)]


def build_brief() -> ShotBrief:
    """Builds CH6's shot brief with REAL TTS-driven per-beat timing --
    previously this called synthesize() for NOTHING (CLAUDE.md/task
    history: "ch6_short_001.py never calls synthesize()"), using fixed
    pacing-bible placeholder `seconds` per beat instead, including for the
    2 cascade beats via a separate wordCascadeDuration()-mirroring formula
    that had nothing to do with real speech length.

    Wiring approach: CH6 absorbs the real TTS/audio-assembly logic
    directly (same real functions render_channel_short.py calls --
    tts.engine.synthesize(), voice_profiles.VOICE_PROFILES[CH6],
    audio.mix.apply_naturalness_processing()/apply_loudnorm_two_pass(),
    audio.wav_utils.silence()/concat_wavs()) rather than converting CH6
    onto render_channel_short.py's shared CHANNEL_SCRIPTS/
    GenericChannelShort path. Reason: CH6 has its own bespoke Remotion
    composition (AmbientBackground/Starfield/HardCutFlash -- CH6's
    distinct space visual identity, not shared with any other channel)
    and its own bespoke shot-brief-building script (per-beat named_entity/
    keyword shape, always Domain.SPACE) -- moving CH6 onto
    GenericChannelShort would mean dropping that bespoke composition
    entirely, which is out of scope for "add the missing voiceover."
    Sharing the underlying real TTS/audio PRIMITIVES (not the whole
    render_channel_short() function) gets CH6 the same real voice
    pipeline CH1-CH5 use without touching its visual identity.

    Real, flagged consequence: every beat (including the 2 cascade
    beats, exactly like CH1-CH5's real render path already does -- see
    render_channel_short.py, which synthesizes cascade beats' punchy
    phrases as real speech too, not a silent WordCascade-only visual)
    now gets duration_frames = real audio_end_frame + TAIL_FRAMES,
    replacing BOTH the old fixed `seconds` argument for normal beats AND
    the old _word_cascade_duration_frames() placeholder formula for
    cascade beats -- consistent with the established real-TTS-driven
    pattern, not a new one invented here.
    """
    profile = VOICE_PROFILES[CH]
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)

    beats: list[Beat] = []
    voice_parts: list[Path] = []
    sample_rate: int | None = None
    i = 0

    def add(beat_id: str, beat_type: BeatType, text: str, entity: str | None, keyword: str | None, cascade: bool = False) -> None:
        nonlocal i, sample_rate
        result, engine_name = synthesize(text, pitch=profile.pitch, pitch_range=profile.pitch_range)
        print(f"[CH6] {beat_id}: TTS engine = {engine_name}", file=sys.stderr)
        sample_rate = result.sample_rate
        raw_path = SCRATCH_ROOT / f"{beat_id}_raw.wav"
        write_wav(result, raw_path)

        natural_path = SCRATCH_ROOT / f"{beat_id}_natural.wav"
        apply_naturalness_processing(raw_path, natural_path)

        word_timings_local = [
            WordTiming(word=wt.word, start_frame=round(wt.start_ms / 1000 * FPS)) for wt in result.word_timings
        ]
        audio_end_frame = round(result.duration_ms / 1000 * FPS)
        duration_frames = audio_end_frame + TAIL_FRAMES

        visual_keywords = [] if cascade else _kw(keyword, entity, beat_id)
        bg_url, bg_status = resolve_beat_background(visual_keywords)
        print(f"[CH6] {beat_id}: footage = {bg_url or 'NONE'} ({bg_status})", file=sys.stderr)

        beats.append(
            Beat(
                beat_id=beat_id,
                beat_type=beat_type,
                text=text,
                duration_frames=duration_frames,
                cascade=cascade,
                ken_burns=_kb(_alternating_pan(i)),
                visual_keywords=visual_keywords,
                source_snippet=SOURCE_NOTE,
                word_timings=word_timings_local,
                audio_end_frame=audio_end_frame,
                background_asset_url=bg_url,
                background_sourcing_status=bg_status,
            )
        )
        i += 1

        actual_voice_s = result.duration_ms / 1000
        pad_s = duration_frames / FPS - actual_voice_s
        pad_path = SCRATCH_ROOT / f"{beat_id}_pad.wav"
        silence(pad_s, sample_rate, pad_path)

        voice_parts.append(natural_path)
        voice_parts.append(pad_path)

    add("hook", BeatType.HOOK,
        "This point of light in your night sky is thirteen hundred times bigger than Earth.",
        "Jupiter", "Jupiter full disk true color")

    add("context-1", BeatType.CONTEXT,
        "Jupiter sits nearly five hundred million miles from the sun.",
        "Jupiter", "Jupiter distance from sun")
    add("context-2", BeatType.CONTEXT,
        "It's the largest planet in our solar system, by a massive margin.",
        "Jupiter", "Jupiter scale comparison planets")

    add("build-1", BeatType.BUILD,
        "But Jupiter isn't solid at all. It's almost entirely gas.",
        "Jupiter", "Jupiter gas giant clouds")
    add("build-2", BeatType.BUILD,
        "Beneath the clouds, pressure crushes hydrogen into a strange metallic liquid.",
        "Jupiter", "Jupiter interior cutaway diagram")
    add("build-3", BeatType.BUILD,
        "And it spins faster than any other planet -- one full day in under ten hours.",
        "Jupiter", "Jupiter rotation")
    add("build-5", BeatType.BUILD,
        "Somewhere in all that motion, one feature has outlasted everything else on the planet.",
        "Jupiter", "Jupiter Great Red Spot wide view")

    add("cascade-1", BeatType.ESCALATION, "A STORM THAT NEVER STOPS", None, None, cascade=True)

    add("escalation-1", BeatType.ESCALATION,
        "That's the Great Red Spot -- a storm wide enough to swallow Earth whole.",
        "Great Red Spot", "Great Red Spot closeup")
    add("escalation-2", BeatType.ESCALATION,
        "It's been raging, continuously, since at least the 1830s.",
        "Great Red Spot", "Great Red Spot historical observation")
    add("escalation-3", BeatType.ESCALATION,
        "No pause. No calm center. Just one uninterrupted storm, for generations.",
        "Great Red Spot", "Great Red Spot storm detail")

    add("cascade-2", BeatType.RESOLUTION, "NEARLY TWO HUNDRED YEARS", None, None, cascade=True)

    add("resolution-1", BeatType.RESOLUTION,
        "Scientists have tracked it shrinking for over a century of observation.",
        "Great Red Spot", "Great Red Spot size comparison over time")
    add("resolution-2", BeatType.RESOLUTION,
        "It used to be wide enough to fit three Earths side by side. Now it's closer to one.",
        "Great Red Spot", "Great Red Spot enhanced color")
    add("resolution-3", BeatType.RESOLUTION,
        "Even shrinking, it's still one of the most violent storms anywhere in the solar system.",
        "Great Red Spot", "Great Red Spot Juno flyby")

    add("closer-1", BeatType.CLOSER,
        "Jupiter has been called a failed star -- but nothing about it has ever stopped moving.",
        "Jupiter", "Jupiter full disk with Great Red Spot")
    add("closer-2", BeatType.CLOSER,
        "Astronomers still don't fully agree on what's fueling it, or when it will finally end.",
        "Great Red Spot", "Great Red Spot mystery close detail")
    add("closer-3", BeatType.CLOSER,
        "It's still out there tonight, exactly where you last looked for it.",
        "Jupiter", "night sky planet viewing wide")

    concatenated_path = SCRATCH_ROOT / "voice_concat.wav"
    concat_wavs(voice_parts, concatenated_path)

    mastered_path = PUBLIC_AUDIO / f"{SHORT_ID}.wav"
    measurement = apply_loudnorm_two_pass(concatenated_path, mastered_path)
    verification = verify_loudness(mastered_path)
    print(f"[CH6] mastered audio -> {mastered_path} (first-pass I={measurement.input_i}, "
          f"final verification={verification})", file=sys.stderr)

    return ShotBrief(
        channel=CH,
        short_id=SHORT_ID,
        beats=beats,
        composition=Composition(primary_anchor=0.5),
        fps=FPS,
    )


if __name__ == "__main__":
    import json
    from dataclasses import asdict

    from .shot_brief import _validate_shot_brief

    brief = build_brief()
    _validate_shot_brief(brief)
    total_seconds = sum(b.duration_frames for b in brief.beats) / brief.fps
    print(f"{len(brief.beats)} beats, {total_seconds:.1f}s total")

    sourced = sum(1 for b in brief.beats if b.background_asset_url)
    print(f"{sourced}/{len(brief.beats)} beats have a real accepted background asset")

    brief_dict = asdict(brief)
    brief_dict["channel"] = brief.channel.value
    for b in brief_dict["beats"]:
        b["beat_type"] = b["beat_type"].value if hasattr(b["beat_type"], "value") else b["beat_type"]
        b["grading"] = b["grading"].value if hasattr(b["grading"], "value") else b["grading"]
        for kw in b["visual_keywords"]:
            kw["domain"] = kw["domain"].value if hasattr(kw["domain"], "value") else kw["domain"]
            kw["channel"] = kw["channel"].value if hasattr(kw["channel"], "value") else kw["channel"]

    out_path = Path("src/remotion/data") / f"{brief.short_id}.json"
    out_path.write_text(json.dumps(brief_dict, indent=2))
    print(f"wrote {out_path}")
