"""Shot brief schema + validator.

The audit protocol (01_REPO_AUDIT_PROTOCOL.md) expects `shot_brief.py` and
`_validate_shot_brief()` to already exist and asks to confirm their current
fields before touching them. This repo was empty at the start of this
build (see CLAUDE.md "Repo status") -- neither existed. This is a fresh
design, not a confirmed prior schema.

Fields below are only included where traceable to something already
confirmed in this session:
- `cascade: bool` on each beat, and the "exactly 2 per short" rule --
  03_SCRIPT_BIBLE.md §4 literally says `_validate_shot_brief()` "should be
  extended to reject any brief that doesn't mark exactly 2 beats as
  `cascade: true`" -- that is the field name and the rule, verbatim.
- `Composition.primary_anchor` -- 02_VISUAL_BIBLE.md §3 says WordCascade
  "must respect [the] same field" as a work-in-progress item described as
  `brief.composition.primaryAnchor`; `src/primitives/WordCascade.tsx`
  already has an `anchorYRatio` prop standing in for this exact field.
- Per-beat-type duration ranges and the "no shot exceeds ~4s" rule --
  05_PACING_MOVEMENT_BIBLE.md §2 and 02_VISUAL_BIBLE.md §7.
- `grading` variant -- 02_VISUAL_BIBLE.md §5's 3 named variants.
- `visual_keywords` -- reuses `VisualKeyword`/`Domain` from
  pipeline/footage_sourcing/types.py rather than duplicating (grep-before-
  create); the domain/named_entity requirement mirrors
  04_ASSET_ACCURACY_BIBLE.md §4's hard verification rules, checked here too
  so a brief fails at authoring time, not only at sourcing time.
- Overall 60-90s length target -- 03_SCRIPT_BIBLE.md §5.

NOT included, and deliberately not invented: a "typography" field/check --
01_REPO_AUDIT_PROTOCOL.md references one as a "prior fail-loud fix" to
confirm is "still in place," but that assumes the prior repo; there is no
spec anywhere available to this session for what it should validate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .footage_sourcing.types import ChannelId, Domain, VisualKeyword

FPS_DEFAULT = 24

# 03_SCRIPT_BIBLE.md §1: the 8-step blueprint arc. `cascade` beats are a
# timing property of a beat, not a distinct beat_type slot -- the bible's
# own arc lists "WordCascade tension beat #1/#2" as occurring between the
# named story beats, so cascade=True is set on whichever beat's text is the
# cascade fragment (e.g. an ESCALATION or RESOLUTION beat whose text is
# itself the short punchy cascade phrase).
class BeatType(str, Enum):
    HOOK = "hook"
    CONTEXT = "context"
    BUILD = "build"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    CLOSER = "closer"


class GradingVariant(str, Enum):
    NEUTRAL = "neutral"
    TEAL_ARCHIVAL = "teal-archival"
    WARM_SEPIA = "warm-sepia"


# 05_PACING_MOVEMENT_BIBLE.md §2, in frames at FPS_DEFAULT=24.
# Cascade beats are exempt -- their timing comes from wordCascadeDuration()
# on the JS side (per-word hold + final-phrase hold), not this table.
_DURATION_RANGE_SECONDS: dict[BeatType, tuple[float, float]] = {
    BeatType.HOOK: (2.0, 3.0),
    BeatType.CONTEXT: (1.5, 3.0),
    BeatType.BUILD: (1.5, 3.0),
    BeatType.ESCALATION: (1.0, 2.0),
    BeatType.RESOLUTION: (2.0, 4.0),
    BeatType.CLOSER: (2.0, 3.0),
}

MAX_SHOT_SECONDS = 4.0  # 02_VISUAL_BIBLE.md §7: "No shot ... exceeds ~4s"
TOTAL_LENGTH_RANGE_SECONDS = (60.0, 90.0)  # 03_SCRIPT_BIBLE.md §5
REQUIRED_CASCADE_COUNT = 2  # 03_SCRIPT_BIBLE.md §4

_GEOCODING_FORBIDDEN_NEEDS_NAMED_ENTITY = {
    Domain.SPACE,
    Domain.HISTORICAL_FIGURE,
    Domain.HISTORICAL_PLACE,
}


@dataclass(frozen=True)
class KenBurns:
    """05_PACING_MOVEMENT_BIBLE.md §3: zoom 1.0 -> 1.06-1.10, pan 2-6% of
    frame width/height, linear or gentle ease-in-out, direction alternated
    shot-to-shot (the "alternated" part is the caller's responsibility when
    building a beat list, not enforced here per-beat)."""

    zoom_start: float = 1.0
    zoom_end: float = 1.08
    pan_direction: str = "none"  # "left" | "right" | "up" | "down" | "none"
    pan_amount_ratio: float = 0.04  # 2-6% per the bible


@dataclass(frozen=True)
class Composition:
    primary_anchor: float = 0.5  # brief.composition.primaryAnchor, 0=top,1=bottom


@dataclass(frozen=True)
class Beat:
    beat_id: str
    beat_type: BeatType
    text: str
    duration_frames: int
    cascade: bool = False
    grading: GradingVariant = GradingVariant.NEUTRAL
    ken_burns: KenBurns = field(default_factory=KenBurns)
    visual_keywords: list[VisualKeyword] = field(default_factory=list)
    # Provenance for the factual claim(s) in `text`, per
    # 03_SCRIPT_BIBLE.md §4's "every factual claim ... must be traceable to
    # the source material." This field can only be checked for *presence*
    # here, not correctness -- there's no automated way to verify a claim
    # is actually true from this field alone; that's still a human/manual
    # review step.
    source_snippet: str | None = None


@dataclass(frozen=True)
class ShotBrief:
    channel: ChannelId
    short_id: str
    beats: list[Beat]
    composition: Composition = field(default_factory=Composition)
    fps: int = FPS_DEFAULT


class ShotBriefValidationError(Exception):
    """Raised by _validate_shot_brief(). Fail loud -- callers must not
    catch this and substitute a default brief; the whole point is that a
    malformed brief stops the pipeline for that short."""


def _validate_shot_brief(brief: ShotBrief) -> None:
    errors: list[str] = []

    cascade_count = sum(1 for b in brief.beats if b.cascade)
    if cascade_count != REQUIRED_CASCADE_COUNT:
        errors.append(
            f"expected exactly {REQUIRED_CASCADE_COUNT} beats with cascade=True "
            f"(03_SCRIPT_BIBLE.md §4), found {cascade_count}"
        )

    if not (0.0 <= brief.composition.primary_anchor <= 1.0):
        errors.append(
            f"composition.primary_anchor must be in [0, 1], got {brief.composition.primary_anchor}"
        )

    total_seconds = sum(b.duration_frames for b in brief.beats) / brief.fps
    lo, hi = TOTAL_LENGTH_RANGE_SECONDS
    if not (lo <= total_seconds <= hi):
        errors.append(
            f"total length {total_seconds:.1f}s outside 03_SCRIPT_BIBLE.md §5's "
            f"{lo:.0f}-{hi:.0f}s target range"
        )

    for beat in brief.beats:
        beat_seconds = beat.duration_frames / brief.fps

        if not beat.cascade:
            if beat_seconds > MAX_SHOT_SECONDS:
                errors.append(
                    f"beat '{beat.beat_id}': {beat_seconds:.1f}s exceeds "
                    f"02_VISUAL_BIBLE.md §7's ~{MAX_SHOT_SECONDS:.0f}s max shot length"
                )
            lo_s, hi_s = _DURATION_RANGE_SECONDS[beat.beat_type]
            if not (lo_s <= beat_seconds <= hi_s):
                errors.append(
                    f"beat '{beat.beat_id}' ({beat.beat_type.value}): {beat_seconds:.1f}s "
                    f"outside 05_PACING_MOVEMENT_BIBLE.md §2's {lo_s:.1f}-{hi_s:.1f}s range"
                )

        if not beat.text.strip():
            errors.append(f"beat '{beat.beat_id}': empty text")

        for kw in beat.visual_keywords:
            if kw.domain in _GEOCODING_FORBIDDEN_NEEDS_NAMED_ENTITY and not kw.named_entity:
                errors.append(
                    f"beat '{beat.beat_id}': keyword '{kw.text}' has domain "
                    f"'{kw.domain.value}' but no named_entity -- "
                    "04_ASSET_ACCURACY_BIBLE.md §4 requires this for verification, "
                    "and confidence.py will reject it anyway; failing at brief "
                    "validation time instead of sourcing time"
                )

    if errors:
        raise ShotBriefValidationError(
            f"shot brief '{brief.short_id}' failed validation ({len(errors)} issue(s)):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
