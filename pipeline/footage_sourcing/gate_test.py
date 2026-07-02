"""Phase 2 gate: run the footage-sourcing module against the 30 sample
beats and print the required table (matched asset + confidence + source
per beat), per the master prompt's Phase 2 gate requirement.

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
past the network call. What's demonstrated as real: domain routing,
confidence scoring/rejection, domain-specific hard verification, and
caching. What's NOT demonstrated: an actual API returning real assets.

Run: python3 -m pipeline.footage_sourcing.gate_test
"""

from __future__ import annotations

from . import confidence, source_router
from .cache import AssetCache
from .errors import DomainRoutingViolation
from .fixture_results import FIXTURE_RESULTS
from .sample_beats import SAMPLE_BEATS
from .types import ChannelId, Domain, VisualKeyword


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


def main() -> None:
    cache = AssetCache()
    rows = []

    for beat in SAMPLE_BEATS:
        for keyword in beat.visual_keywords:
            clients = source_router.route(keyword)
            client_chain = " -> ".join(c.name for c in clients)

            candidates = FIXTURE_RESULTS.get(beat.beat_id, [])
            match = confidence.best_match(keyword, candidates)

            if match is None:
                # Show the rejection reason from whichever candidate scored
                # highest, even though nothing was accepted.
                all_scored = [confidence.score(keyword, a) for a in candidates]
                reason = all_scored[0].reason if all_scored else "no candidates returned"
                rows.append(
                    {
                        "beat": beat.beat_id,
                        "channel": beat.channel.value,
                        "keyword": keyword.text,
                        "domain": keyword.domain.value,
                        "routed_to": client_chain,
                        "result": "FLAGGED (no confident match)",
                        "confidence": "-",
                        "reason": reason,
                    }
                )
                continue

            cache.put(match)
            rows.append(
                {
                    "beat": beat.beat_id,
                    "channel": beat.channel.value,
                    "keyword": keyword.text,
                    "domain": keyword.domain.value,
                    "routed_to": client_chain,
                    "result": f"ACCEPTED ({match.asset.source}#{match.asset.asset_id})"
                    + (" [needs manual review]" if match.requires_manual_review else ""),
                    "confidence": f"{match.confidence:.2f}",
                    "reason": match.reason,
                }
            )

    headers = ["beat", "channel", "domain", "routed_to", "result", "confidence"]
    widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    print(" | ".join(h.ljust(widths[h]) for h in headers))
    print("-+-".join("-" * widths[h] for h in headers))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(widths[h]) for h in headers))

    accepted = sum(1 for r in rows if r["result"].startswith("ACCEPTED"))
    needs_review = sum(1 for r in rows if "[needs manual review]" in r["result"])
    rejected = len(rows) - accepted
    print(
        f"\n{accepted} accepted ({needs_review} of those need manual review before "
        f"reuse, per §4's first-use rule for historical entities), "
        f"{rejected} rejected/flagged (no confident match found), out of {len(rows)} keywords."
    )

    print()
    _print_routing_guard_proof()


if __name__ == "__main__":
    main()
