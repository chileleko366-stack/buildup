"""TEMPORARY test entry point, added only to prove pipeline/script_generation.py
actually works against the real Groq API from a real CI runner (this
sandbox's own egress blocks api.groq.com, confirmed via curl -- same
situation as pexels/pixabay/nasa before them). Generates one real script
for CH1 and one other channel and prints the full text, word count, and
estimated duration to the CI log. Does NOT render video, per explicit
instruction this pass stops at generation + reporting.

Run via: python3 -m pipeline.test_script_generation
Remove once the generation step is reviewed and either wired in for real
or reworked.
"""

from __future__ import annotations

import sys

from .footage_sourcing.types import ChannelId
from .script_generation import generate_channel_script

_TEST_CHANNELS = [ChannelId.CH1, ChannelId.CH5]


def _print_result(result: dict) -> None:
    lo, hi = result["estimated_duration_s_range"]
    print(f"\n{'=' * 70}", file=sys.stderr)
    print(f"CHANNEL: {result['channel']}", file=sys.stderr)
    print(f"TOPIC SUMMARY: {result['topic_summary']}", file=sys.stderr)
    print(f"SOURCE CONFIDENCE NOTE: {result['source_confidence_note']}", file=sys.stderr)
    print(f"TOTAL WORD COUNT: {result['total_word_count']}", file=sys.stderr)
    print(f"ESTIMATED DURATION: {lo}s - {hi}s (at {160}-{175} WPM)", file=sys.stderr)
    print("BEATS:", file=sys.stderr)
    for b in result["beats"]:
        wc = len((b.get("text") or "").split())
        print(
            f"  [{b.get('beat_id')}] ({b.get('beat_type')}, cascade={b.get('cascade')}, "
            f"domain={b.get('domain')}, keyword={b.get('keyword')!r}, "
            f"named_entity={b.get('named_entity')!r}, words={wc}) "
            f"{b.get('text')!r}",
            file=sys.stderr,
        )
    print(f"{'=' * 70}\n", file=sys.stderr)


def main() -> None:
    exit_code = 0
    for channel in _TEST_CHANNELS:
        try:
            result = generate_channel_script(channel)
        except Exception as e:
            print(f"FAILED for {channel.value}: {type(e).__name__}: {e}", file=sys.stderr)
            exit_code = 1
            continue
        _print_result(result)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
