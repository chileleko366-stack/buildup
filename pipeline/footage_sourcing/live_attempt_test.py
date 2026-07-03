"""Real (not fixture-substituted) run of the 30 sample beats through
resolve.resolve_keyword() -- makes an ACTUAL client.search() network call
per keyword, unlike gate_test.py (which deliberately uses hand-authored
FIXTURE_RESULTS because the module's author already knew every host was
blocked, per that file's own docstring).

This script exists to prove that claim directly through the real code
path this pipeline would use in production, not just via a standalone
curl check -- if egress or a key situation ever changes, re-running this
is how you'd find out (every row would flip from a client-error reason to
a real accept/reject).

Run: python3 -m pipeline.footage_sourcing.live_attempt_test
"""

from __future__ import annotations

from .cache import AssetCache, DEFAULT_CACHE_PATH
from .resolve import resolve_keyword
from .sample_beats import SAMPLE_BEATS

COLUMNS = ["beat_text", "keyword", "domain", "decision", "reason"]


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> None:
    cache = AssetCache(path=DEFAULT_CACHE_PATH.parent / "live_attempt_cache.json")
    rows: list[dict] = []

    for beat in SAMPLE_BEATS:
        for keyword in beat.visual_keywords:
            result = resolve_keyword(keyword, cache=cache)
            if result.match is not None:
                decision = "ACCEPT" + (" [needs review]" if result.flagged_for_review else "")
                reason = result.match.reason
            else:
                decision = "REJECT (real network attempt failed)"
                reason = result.flag_reason or "unknown"
            rows.append(
                {
                    "beat_text": _truncate(beat.text, 40),
                    "keyword": keyword.text,
                    "domain": keyword.domain.value,
                    "decision": decision,
                    "reason": _truncate(reason, 90),
                }
            )

    widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in COLUMNS}
    print(" | ".join(h.ljust(widths[h]) for h in COLUMNS))
    print("-+-".join("-" * widths[h] for h in COLUMNS))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(widths[h]) for h in COLUMNS))

    accepted = [r for r in rows if r["decision"].startswith("ACCEPT")]
    rejected = [r for r in rows if r["decision"].startswith("REJECT")]
    print(f"\n{len(accepted)} accepted, {len(rejected)} rejected, out of {len(rows)} real network attempts.")
    if rejected and all("blocked" in r["reason"].lower() or "connect" in r["reason"].lower()
                         or "proxy" in r["reason"].lower() or "not set" in r["reason"].lower()
                         or "notconfigurederror" in r["reason"].lower() for r in rejected):
        print("All rejections are real network/auth failures (egress block or missing key), "
              "not scoring rejections -- confirms this session genuinely cannot reach any source.")


if __name__ == "__main__":
    main()
