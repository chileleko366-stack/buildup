"""Keyword-triggered SFX detection, timed to real per-word timestamps.

Categories, keyword lists, minimum-gap value, and cascade-only-on-final-
word rule are transcribed directly from the user's own request -- not
independently sourced, since they're explicit product requirements, not
audio-engineering facts to verify against real repos.

NOT SOURCED, FLAGGED PER THE USER'S OWN INSTRUCTION: no SFX asset library
exists anywhere in this repo (confirmed by `find` before writing this file
-- only public/audio/ch6-cascade-1-espeak.wav, a TTS test file, exists).
There is no cash-register/coin cue, no riser, no tension hit, no
notification pop. `PLACEHOLDER_TONES` below are synthesized sine beeps
(via ffmpeg's own `sine` source filter) used ONLY to prove the trigger
detection/timing/priority/mixing mechanism end-to-end -- they are not
real SFX and must not be mistaken for them. Sourcing real, licensed SFX
assets is unresolved work, not done here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from .ffmpeg_bin import ffmpeg_path
from ..footage_sourcing.types import ChannelId
from ..shot_brief import Beat

MIN_GAP_MS = 175  # midpoint of the user's specified 150-200ms range; not
# independently sourced from a bible or repo -- the user asked for
# "minimum 150-200ms," not one exact number, so this is a documented choice
# within that range, not outside it.


class SfxCategory(IntEnum):
    """Ordered by priority, per the user's request: "if two keywords land
    close together, only the higher-priority one fires (money/number >
    generic)." Lower value = higher priority."""

    BIG_NUMBER = 0  # cascade outro payoff
    MONEY = 1
    TWIST = 2
    HOOK_OPENER = 3


_MONEY_KEYWORDS = {
    # "million"/"billion" were the exact words in the user's spec (singular
    # only) -- added the plural forms too since natural sentences commonly
    # use them ("turned into billions") and missing them silently would
    # defeat the point of a keyword trigger; noted here rather than left
    # unstated, per the same disclosure standard as everything else.
    "$", "dollar", "dollars", "million", "millions", "billion", "billions",
    "cost", "price", "paid", "worth", "richest", "fortune",
}
_TWIST_KEYWORDS = {"but", "then", "immediately", "suddenly"}
_HOOK_OPENER_KEYWORDS = {"what", "why", "how", "did", "do", "does", "imagine"}


@dataclass(frozen=True)
class WordTiming:
    word: str
    start_frame: int


@dataclass(frozen=True)
class SfxTrigger:
    category: SfxCategory
    word: str
    frame: int
    channel_flavor: str


def _normalize(word: str) -> str:
    return re.sub(r"[^\w$]", "", word).lower()


def _channel_flavor(channel: ChannelId) -> str:
    """Per-channel variant selection. NOT bible-sourced -- new design work,
    using channelConfigs.ts's existing `scriptTone` strings as the "genre/
    mood config" the user referred to, since that's the only per-channel
    tone/genre data that already exists in this repo. Simple keyword match
    against the tone description; not a confirmed taxonomy."""
    tones = {
        ChannelId.CH1: "punchy, direct, mind-bending",
        ChannelId.CH2: "analytical, shocking, authoritative",
        ChannelId.CH3: "conspiratorial, terse, urgent",
        ChannelId.CH4: "scientific, vivid, revelatory",
        ChannelId.CH5: "measured, evocative, archival",
        ChannelId.CH6: "awe-inspiring, precise, cosmic",
    }
    tone = tones.get(channel, "")
    if "punchy" in tone or "shocking" in tone or "urgent" in tone:
        return "snappy"
    if "cosmic" in tone or "measured" in tone or "archival" in tone:
        return "deep"
    return "neutral"


def detect_triggers(
    beat: Beat,
    word_timings: list[WordTiming],
    channel: ChannelId,
    *,
    cascade_final_frame: int | None = None,
) -> list[SfxTrigger]:
    """Scans a beat's words for trigger keywords.

    For cascade beats, per the user's explicit rule ("SFX hit only on the
    final word/phrase-hold, not every hard-cut word"), this only considers
    the beat's FULL TEXT for a keyword match and -- if found -- fires
    exactly once, at `cascade_final_frame` (the phrase-hold start), never
    per-word.
    """
    flavor = _channel_flavor(channel)

    if beat.cascade:
        if cascade_final_frame is None:
            raise ValueError("cascade_final_frame is required for cascade beats")
        full_text_words = {_normalize(w) for w in beat.text.split()}
        category = _classify(full_text_words, beat.text)
        if category is None:
            return []
        return [SfxTrigger(category=category, word=beat.text, frame=cascade_final_frame, channel_flavor=flavor)]

    triggers: list[SfxTrigger] = []
    for wt in word_timings:
        norm = _normalize(wt.word)
        category = _classify({norm}, wt.word)
        if category is not None:
            triggers.append(SfxTrigger(category=category, word=wt.word, frame=wt.start_frame, channel_flavor=flavor))
    return triggers


def _classify(normalized_words: set[str], raw_text: str) -> SfxCategory | None:
    if "$" in raw_text or normalized_words & _MONEY_KEYWORDS:
        return SfxCategory.MONEY
    if normalized_words & _TWIST_KEYWORDS:
        return SfxCategory.TWIST
    if normalized_words & _HOOK_OPENER_KEYWORDS:
        return SfxCategory.HOOK_OPENER
    return None


def resolve_conflicts(triggers: list[SfxTrigger], fps: int, min_gap_ms: int = MIN_GAP_MS) -> list[SfxTrigger]:
    """Enforces the minimum gap between cues; when two triggers land within
    the gap, keeps only the higher-priority one (lower SfxCategory value)."""
    min_gap_frames = round(min_gap_ms / 1000 * fps)
    ordered = sorted(triggers, key=lambda t: t.frame)

    kept: list[SfxTrigger] = []
    for trigger in ordered:
        conflict_idx = None
        for i, existing in enumerate(kept):
            if abs(trigger.frame - existing.frame) < min_gap_frames:
                conflict_idx = i
                break
        if conflict_idx is None:
            kept.append(trigger)
            continue
        if trigger.category < kept[conflict_idx].category:  # lower value = higher priority
            kept[conflict_idx] = trigger
    return sorted(kept, key=lambda t: t.frame)


# --- Placeholder tones -- NOT real SFX, see module docstring ---

_PLACEHOLDER_TONE_HZ = {
    SfxCategory.MONEY: 1200,
    SfxCategory.BIG_NUMBER: 400,  # riser is swept, not a fixed tone; see generate_placeholder_riser
    SfxCategory.TWIST: 220,
    SfxCategory.HOOK_OPENER: 1800,
}


def generate_placeholder_tone(category: SfxCategory, out_path: Path, duration_s: float = 0.25) -> None:
    """Synthesizes a labeled placeholder beep via ffmpeg's `sine` source --
    NOT a real SFX asset. See module docstring."""
    import subprocess

    freq = _PLACEHOLDER_TONE_HZ[category]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            ffmpeg_path(), "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={freq}:duration={duration_s}",
            "-af", "afade=t=out:st=0:d=" + str(duration_s * 0.6),
            str(out_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg placeholder tone generation failed:\n{result.stderr}")
