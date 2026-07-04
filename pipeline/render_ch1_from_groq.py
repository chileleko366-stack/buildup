"""Proof-of-concept: generates a REAL CH1 script via Groq
(pipeline/script_generation.py) and renders it through the exact same
real per-beat pipeline (TTS + naturalness + real footage sourcing + real
per-beat timing + loudnorm mastering) that CH1-CH5's static scripts
already use -- pipeline/render_channel_short.py's render_beats(), not a
parallel reimplementation.

This is the "prove a generated script end-to-end" step
pipeline/script_generation.py's own docstring explicitly deferred ("does
NOT modify pipeline/channel_scripts.py... the static scripts stay in
place as the current production path until a generated script is proven
end-to-end and wired in deliberately"). Deliberately does NOT touch
pipeline/channel_scripts.py's committed CH1_BEATS or overwrite CH1's
existing static short -- this writes to a SEPARATE short_id
(`ch1-groq-generated-001`) with its own JSON/audio/Remotion composition,
so the static production CH1 short is completely unaffected.

Run: python3 -m pipeline.render_ch1_from_groq
"""

from __future__ import annotations

import json
import sys

from .channel_scripts import BeatSpec
from .footage_sourcing.types import ChannelId, Domain
from .render_channel_short import render_beats
from .script_generation import generate_channel_script
from .shot_brief import BeatType

SHORT_ID = "ch1-groq-generated-001"
_DEFAULT_CASCADE_BEAT_TYPE = BeatType.ESCALATION  # only matters as metadata; real timing comes from TTS either way


def _beat_specs_from_groq(beats: list[dict]) -> list[BeatSpec]:
    specs: list[BeatSpec] = []
    for b in beats:
        cascade = bool(b.get("cascade"))
        domain = Domain(b["domain"]) if b.get("domain") else None
        beat_type = BeatType(b["beat_type"]) if b.get("beat_type") else _DEFAULT_CASCADE_BEAT_TYPE
        specs.append(
            BeatSpec(
                beat_id=b["beat_id"],
                beat_type=beat_type,
                text=b["text"],
                domain=domain,
                keyword=b.get("keyword"),
                named_entity=b.get("named_entity"),
                cascade=cascade,
            )
        )
    return specs


def main() -> None:
    result = generate_channel_script(ChannelId.CH1)
    print(
        f"[render_ch1_from_groq] topic_summary={result['topic_summary']!r} "
        f"total_word_count={result['total_word_count']} "
        f"estimated_duration_s_range={result['estimated_duration_s_range']} "
        f"accepted_below_target_floor={result['accepted_below_target_floor']}",
        file=sys.stderr,
    )

    beat_specs = _beat_specs_from_groq(result["beats"])
    source_note = (
        f"Groq-generated (llama-3.3-70b-versatile), topic: {result['topic_summary']}. "
        f"Model's own confidence note: {result['source_confidence_note']}"
    )

    report = render_beats(ChannelId.CH1, beat_specs, source_note, SHORT_ID)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
