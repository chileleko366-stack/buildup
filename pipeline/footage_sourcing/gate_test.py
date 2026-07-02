"""Phase 2 gate: run the footage-sourcing module against the 30 sample
beats and print the table required by 07_REVIEW_GATE_PROTOCOL.md Gate 2:
"beat text -> extracted keywords -> domain tag -> source used -> matched
asset (thumbnail or filename) -> confidence score -> accept/reject", run
against 5 beats/channel (30 rows total), with rejected/flagged rows shown
explicitly rather than hidden.

IMPORTANT CAVEAT (read before trusting this output as "the module works
against real data"): this session cannot reach any asset-source API --
Pexels/Pixabay have no configured keys, and api.nasa.gov,
commons.wikimedia.org, and www.loc.gov are all denied by this session's
egress policy (confirmed via direct curl, not assumed). So this script does
NOT call client.search() over the network. It calls source_router.route()
to get the real routing decision (which client, in which order, for each
keyword's channel+domain), then feeds each keyword's FIXTURE_RESULTS
(hand-authored, see fixture_results.py) through the real confidence.score()
and cache.AssetCache -- exactly the same code path a live run would use
past the network call. "Extracted keywords" here are likewise hand-authored
(see sample_beats.py's module docstring) since keyword_extraction.py is
stub-gated without an LLM key. What's demonstrated as real: domain routing,
confidence scoring/rejection, domain-specific hard verification, and
caching. What's NOT demonstrated: an actual API/LLM call.

Run: python3 -m pipeline.footage_sourcing.gate_test
"""

from __future__ import annotations

from . import confidence, source_router
from .cache import AssetCache
from .errors import DomainRoutingViolation
from .fixture_results import FIXTURE_RESULTS
from .sample_beats import SAMPLE_BEATS
from .types import ChannelId, Domain, VisualKeyword

COLUMNS = [
    "beat_text",
    "keyword",
    "domain",
    "source_used",
    "matched_asset",
    "confidence",
    "decision",
]


def _print_routing_guard_proof() -> None:
    """Prove the hard geocoding guard from §1 actually raises, not just
    that it's documented as raising."""
    from .clients.nominatim import NominatimClient

    forbidden = VisualKeyword(
        text="Jupiter", domain=Domain.SPACE, channel=ChannelId.CH6, beat_id="guard-proof"
    )
    try:
        NominatimClient().search(forbidden)
        print("!! GUARD FAILED: Nominatim accepted a `space` domain keyword")
    except DomainRoutingViolation as e:
        print(f"Geocoding guard proof: PASS -- {e}")


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def build_rows() -> list[dict]:
    cache = AssetCache()
    rows: list[dict] = []

    for beat in SAMPLE_BEATS:
        for keyword in beat.visual_keywords:
            clients = source_router.route(keyword)
            candidates = FIXTURE_RESULTS.get(beat.beat_id, [])
            match = confidence.best_match(keyword, candidates)

            if match is None:
                all_scored = [confidence.score(keyword, a) for a in candidates]
                reason = all_scored[0].reason if all_scored else "no candidates returned"
                rows.append(
                    {
                        "beat_text": beat.text,
                        "keyword": keyword.text,
                        "domain": keyword.domain.value,
                        "source_used": " -> ".join(c.name for c in clients) + " (none accepted)",
                        "matched_asset": "-",
                        "confidence": "-",
                        "decision": "REJECT",
                        "reason": reason,
                    }
                )
                continue

            cache.put(match)
            review_suffix = " [needs manual review before reuse]" if match.requires_manual_review else ""
            rows.append(
                {
                    "beat_text": beat.text,
                    "keyword": keyword.text,
                    "domain": keyword.domain.value,
                    "source_used": match.asset.source,
                    "matched_asset": f"{match.asset.source}#{match.asset.asset_id} ({match.asset.title})",
                    "confidence": f"{match.confidence:.2f}",
                    "decision": f"ACCEPT{review_suffix}",
                    "reason": match.reason,
                }
            )
    return rows


def print_table(rows: list[dict]) -> None:
    display_cols = COLUMNS
    printable = [{**r, "beat_text": _truncate(r["beat_text"], 40), "matched_asset": _truncate(r["matched_asset"], 45)} for r in rows]
    widths = {h: max(len(h), max(len(str(r[h])) for r in printable)) for h in display_cols}
    print(" | ".join(h.ljust(widths[h]) for h in display_cols))
    print("-+-".join("-" * widths[h] for h in display_cols))
    for r in printable:
        print(" | ".join(str(r[h]).ljust(widths[h]) for h in display_cols))


def main() -> None:
    rows = build_rows()
    print_table(rows)

    accepted = [r for r in rows if r["decision"].startswith("ACCEPT")]
    needs_review = [r for r in accepted if "needs manual review" in r["decision"]]
    rejected = [r for r in rows if r["decision"] == "REJECT"]

    print(
        f"\n{len(accepted)} accepted ({len(needs_review)} of those need manual review "
        f"before reuse, per §4's first-use rule for historical entities), "
        f"{len(rejected)} rejected, out of {len(rows)} keywords."
    )

    print("\nRejected rows, shown explicitly per Gate 2 ('not hidden'):")
    for r in rejected:
        print(f"  - [{r['domain']}] \"{_truncate(r['beat_text'], 60)}\" / '{r['keyword']}' -- {r['reason']}")

    print()
    _print_routing_guard_proof()


if __name__ == "__main__":
    main()
