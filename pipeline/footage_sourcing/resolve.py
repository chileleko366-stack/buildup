"""Real end-to-end asset resolution: routes a keyword to its real client(s)
(source_router.route()), ACTUALLY CALLS client.search() over the network,
scores results (confidence.py), and returns a SourcingResult -- the one
piece of Phase 2 that gate_test.py deliberately did NOT do (it fed
hand-authored FIXTURE_RESULTS through confidence/cache instead, since this
session's egress blocks every real host). This module makes the real call
and lets it fail for real, per the fail-loud rule -- no fixture
substitution here.

Used by two things:
1. `pipeline/footage_sourcing/live_attempt_test.py` -- the "did the real
   network call actually work" proof, run against the same 30 sample
   beats gate_test.py uses.
2. `pipeline/resolve_beat_backgrounds.py` -- attaches (or fails to attach)
   a real background asset to each beat of a real channel's shot brief,
   feeding the render path (SourcedBackground.tsx).
"""

from __future__ import annotations

from . import confidence, source_router
from .cache import AssetCache
from .errors import DomainRoutingViolation, FootageSourcingError
from .types import ScoredMatch, SourcingResult, VisualKeyword


def resolve_keyword(keyword: VisualKeyword, cache: AssetCache | None = None) -> SourcingResult:
    """Resolves one keyword to a real accepted asset, or a flagged failure.

    Cache is checked first (§5: avoid re-fetching, reuse a verified
    match). DomainRoutingViolation is NOT caught here -- that's a hard
    structural bug (a forbidden domain reaching a geocoder), not a normal
    sourcing failure, and must propagate per errors.py's own docstring.
    """
    cache = cache or AssetCache()

    cached = cache.get(keyword.channel, keyword.text, keyword.domain)
    if cached is not None and cached.get("verified", False):
        return SourcingResult(keyword=keyword, match=None, flagged_for_review=False, cache_hit=True)

    clients = source_router.route(keyword)  # raises DomainRoutingViolation uncaught -- see docstring

    all_candidates = []
    client_errors: list[str] = []
    for client in clients:
        try:
            candidates = client.search(keyword)
            all_candidates.extend(candidates)
            if candidates:
                break  # primary yielded results; per §2's primary/secondary ordering, don't also hit secondary
        except DomainRoutingViolation:
            raise
        except FootageSourcingError as e:
            client_errors.append(f"{client.name}: {type(e).__name__}: {e}")
        except Exception as e:  # real network/HTTP errors -- requests.RequestException etc.
            client_errors.append(f"{client.name}: {type(e).__name__}: {e}")

    if not all_candidates:
        reason = "; ".join(client_errors) if client_errors else "no candidates returned by any configured source"
        return SourcingResult(keyword=keyword, match=None, flagged_for_review=True, flag_reason=reason)

    match: ScoredMatch | None = confidence.best_match(keyword, all_candidates)
    if match is None:
        scored = [confidence.score(keyword, a) for a in all_candidates]
        best_reason = max(scored, key=lambda m: m.confidence).reason if scored else "no candidates"
        return SourcingResult(
            keyword=keyword,
            match=None,
            flagged_for_review=True,
            flag_reason=f"no candidate cleared confidence threshold -- {best_reason}",
        )

    cache.put(match)
    return SourcingResult(
        keyword=keyword,
        match=match,
        flagged_for_review=match.requires_manual_review,
        flag_reason="first use of this historical entity -- needs manual review before reuse" if match.requires_manual_review else None,
    )
