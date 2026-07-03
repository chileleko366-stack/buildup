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
from .types import ScoredMatch, SourcedAsset, SourcingResult, VisualKeyword


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

    # Real, observed coverage bug (2026-07-03): the old version broke out of
    # this loop the moment the PRIMARY client returned any candidates at all,
    # even if every one of them scored below CONFIDENCE_THRESHOLD -- meaning
    # the secondary client (pixabay for CH1/CH2/CH4, loc for CH3/CH5) never
    # got a chance whenever the primary returned weak-but-nonzero results,
    # which real CI logs showed was most of the time. Now: a client's own
    # candidates are scored immediately: if they clear the threshold on their
    # own, accept and stop (skip the secondary call entirely -- this still
    # saves an extra real network call in the common case, and avoids adding
    # load to hosts like wikimedia that are known to rate-limit). Only when
    # a client's candidates DON'T individually clear the bar do we fall
    # through and also try the next client, then re-score everything pooled.
    all_candidates: list[SourcedAsset] = []
    client_errors: list[str] = []
    for client in clients:
        try:
            candidates = client.search(keyword)
        except DomainRoutingViolation:
            raise
        except FootageSourcingError as e:
            client_errors.append(f"{client.name}: {type(e).__name__}: {e}")
            continue
        except Exception as e:  # real network/HTTP errors -- requests.RequestException etc.
            # requests.HTTPError carries the real response on .response -- surface
            # its body (the actual API error message), not just the status code.
            resp = getattr(e, "response", None)
            if resp is not None:
                client_errors.append(f"{client.name}: HTTP {resp.status_code}: {resp.text[:500]}")
            else:
                client_errors.append(f"{client.name}: {type(e).__name__}: {e}")
            continue

        all_candidates.extend(candidates)
        if candidates:
            immediate_match = confidence.best_match(keyword, candidates)
            if immediate_match is not None:
                cache.put(immediate_match)
                return SourcingResult(
                    keyword=keyword,
                    match=immediate_match,
                    flagged_for_review=immediate_match.requires_manual_review,
                    flag_reason="first use of this historical entity -- needs manual review before reuse" if immediate_match.requires_manual_review else None,
                )

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
