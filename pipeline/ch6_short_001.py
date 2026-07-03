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

from .footage_sourcing.attach_background import resolve_beat_background
from .footage_sourcing.types import ChannelId, Domain, VisualKeyword
from .shot_brief import Beat, BeatType, Composition, KenBurns, ShotBrief

CH = ChannelId.CH6
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


def _word_cascade_duration_frames(text: str, frames_per_word: int = 5, final_hold_frames: int = 18) -> int:
    """Mirrors src/primitives/WordCascade.tsx's wordCascadeDuration() --
    a cascade beat's duration_frames MUST equal this, or BeatCompositor's
    per-beat Sequence will cut WordCascade off before its final-phrase hold
    finishes (or leave dead frames after it ends)."""
    word_count = len(text.strip().split())
    return word_count * frames_per_word + final_hold_frames


def build_brief() -> ShotBrief:
    beats: list[Beat] = []
    i = 0

    def add(beat_id: str, beat_type: BeatType, text: str, seconds: float, entity: str, keyword: str, cascade: bool = False) -> None:
        nonlocal i
        visual_keywords = [] if cascade else _kw(keyword, entity, beat_id)
        bg_url, bg_status = resolve_beat_background(visual_keywords)
        print(f"[CH6] {beat_id}: footage = {bg_url or 'NONE'} ({bg_status})", file=sys.stderr)
        beats.append(
            Beat(
                beat_id=beat_id,
                beat_type=beat_type,
                text=text,
                duration_frames=round(seconds * 24),
                cascade=cascade,
                ken_burns=_kb(_alternating_pan(i)),
                visual_keywords=visual_keywords,
                source_snippet=SOURCE_NOTE,
                background_asset_url=bg_url,
                background_sourcing_status=bg_status,
            )
        )
        i += 1

    add("hook", BeatType.HOOK,
        "This point of light in your night sky is thirteen hundred times bigger than Earth.",
        2.5, "Jupiter", "Jupiter full disk true color")

    add("context-1", BeatType.CONTEXT,
        "Jupiter sits nearly five hundred million miles from the sun.",
        2.25, "Jupiter", "Jupiter distance from sun")
    add("context-2", BeatType.CONTEXT,
        "It's the largest planet in our solar system, by a massive margin.",
        2.25, "Jupiter", "Jupiter scale comparison planets")
    add("context-3", BeatType.CONTEXT,
        "From here, it just looks like a steady, bright star.",
        2.25, "Jupiter", "night sky planet viewing")
    add("context-4", BeatType.CONTEXT,
        "It has at least ninety-five known moons orbiting it.",
        2.25, "Jupiter", "Jupiter moons Galilean")
    add("context-5", BeatType.CONTEXT,
        "Two of them, Io and Europa, are worlds all their own.",
        2.25, "Io", "Io volcanic moon")
    add("context-6", BeatType.CONTEXT,
        "Some nights, even a basic backyard telescope is enough to make out its cloud bands.",
        2.25, "Jupiter", "Jupiter cloud bands telescope view")

    add("build-1", BeatType.BUILD,
        "But Jupiter isn't solid at all. It's almost entirely gas.",
        2.25, "Jupiter", "Jupiter gas giant clouds")
    add("build-2", BeatType.BUILD,
        "Beneath the clouds, pressure crushes hydrogen into a strange metallic liquid.",
        2.5, "Jupiter", "Jupiter interior cutaway diagram")
    add("build-3", BeatType.BUILD,
        "And it spins faster than any other planet -- one full day in under ten hours.",
        2.5, "Jupiter", "Jupiter rotation")
    add("build-4", BeatType.BUILD,
        "Its magnetic field is so strong it would be visible from Earth, if we could see magnetism.",
        2.5, "Jupiter", "Jupiter magnetosphere aurora")
    add("build-5", BeatType.BUILD,
        "Somewhere in all that motion, one feature has outlasted everything else on the planet.",
        2.25, "Jupiter", "Jupiter Great Red Spot wide view")
    add("build-6", BeatType.BUILD,
        "Jupiter even has faint rings of its own, too dim to see without a spacecraft nearby.",
        2.25, "Jupiter", "Jupiter faint ring system")

    cascade1_text = "A STORM THAT NEVER STOPS"
    beats.append(Beat("cascade-1", BeatType.ESCALATION, cascade1_text,
                       _word_cascade_duration_frames(cascade1_text),
                       cascade=True, source_snippet=SOURCE_NOTE,
                       background_sourcing_status="cascade beat -- no keyword to source"))
    i += 1

    add("escalation-1", BeatType.ESCALATION,
        "That's the Great Red Spot -- a storm wide enough to swallow Earth whole.",
        1.75, "Great Red Spot", "Great Red Spot closeup")
    add("escalation-2", BeatType.ESCALATION,
        "It's been raging, continuously, since at least the 1830s.",
        1.75, "Great Red Spot", "Great Red Spot historical observation")
    add("escalation-3", BeatType.ESCALATION,
        "No pause. No calm center. Just one uninterrupted storm, for generations.",
        1.75, "Great Red Spot", "Great Red Spot storm detail")

    cascade2_text = "NEARLY TWO HUNDRED YEARS"
    beats.append(Beat("cascade-2", BeatType.RESOLUTION, cascade2_text,
                       _word_cascade_duration_frames(cascade2_text),
                       cascade=True, source_snippet=SOURCE_NOTE,
                       background_sourcing_status="cascade beat -- no keyword to source"))
    i += 1

    add("resolution-1", BeatType.RESOLUTION,
        "Scientists have tracked it shrinking for over a century of observation.",
        3.0, "Great Red Spot", "Great Red Spot size comparison over time")
    add("resolution-2", BeatType.RESOLUTION,
        "It used to be wide enough to fit three Earths side by side. Now it's closer to one.",
        3.25, "Great Red Spot", "Great Red Spot enhanced color")
    add("resolution-3", BeatType.RESOLUTION,
        "Even shrinking, it's still one of the most violent storms anywhere in the solar system.",
        3.0, "Great Red Spot", "Great Red Spot Juno flyby")
    add("resolution-4", BeatType.RESOLUTION,
        "Winds inside it reach speeds no storm on Earth has ever recorded.",
        3.0, "Great Red Spot", "Great Red Spot wind speed visualization")
    add("resolution-5", BeatType.RESOLUTION,
        "The storm itself rotates counterclockwise, completing a full turn every six Earth days.",
        3.0, "Great Red Spot", "Great Red Spot rotation timelapse")

    add("closer-1", BeatType.CLOSER,
        "Jupiter has been called a failed star -- but nothing about it has ever stopped moving.",
        2.5, "Jupiter", "Jupiter full disk with Great Red Spot")
    add("closer-2", BeatType.CLOSER,
        "Astronomers still don't fully agree on what's fueling it, or when it will finally end.",
        2.5, "Great Red Spot", "Great Red Spot mystery close detail")
    add("closer-3", BeatType.CLOSER,
        "It's still out there tonight, exactly where you last looked for it.",
        2.75, "Jupiter", "night sky planet viewing wide")

    return ShotBrief(
        channel=CH,
        short_id="ch6-jupiter-red-spot-001",
        beats=beats,
        composition=Composition(primary_anchor=0.5),
    )


if __name__ == "__main__":
    import json
    from dataclasses import asdict
    from pathlib import Path

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
