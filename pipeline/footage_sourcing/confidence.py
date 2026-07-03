"""Confidence scoring + accept/reject + domain-specific verification.

Per 04_ASSET_ACCURACY_BIBLE.md §3 points 4-5 and §4's per-domain checks.
"""

from __future__ import annotations

import re

from . import content_type_filter
from .config import CONFIDENCE_THRESHOLD
from .types import Domain, ScoredMatch, SourcedAsset, VisualKeyword


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _keyword_overlap_score(keyword: VisualKeyword, asset: SourcedAsset) -> float:
    """§3 point 4 fallback scorer: keyword-overlap against title/description."""
    kw_tokens = _tokenize(keyword.text)
    if keyword.named_entity:
        kw_tokens |= _tokenize(keyword.named_entity)
    asset_tokens = _tokenize(f"{asset.title} {asset.description}")
    if not kw_tokens or not asset_tokens:
        return 0.0
    overlap = kw_tokens & asset_tokens
    return len(overlap) / len(kw_tokens)


def _verify_domain_specific(keyword: VisualKeyword, asset: SourcedAsset) -> str | None:
    """Returns a rejection reason string if a domain-specific hard check
    fails, else None. These are §4's rules, applied before generic scoring
    can rubber-stamp a mismatched asset."""

    if keyword.domain == Domain.SPACE:
        if not asset.catalog_id:
            return "space domain requires a real NASA catalog ID; asset has none"
        entity = keyword.named_entity or keyword.text
        if entity.lower() not in asset.title.lower():
            return (
                f"space domain: object name '{entity}' not found in NASA "
                f"asset title '{asset.title}' -- exact-match required, rejecting"
            )

    if keyword.domain in (Domain.HISTORICAL_FIGURE, Domain.HISTORICAL_PLACE):
        if not keyword.named_entity:
            return "historical domain requires a named_entity to verify against"
        haystack = f"{asset.title} {asset.description}".lower()
        if keyword.named_entity.lower() not in haystack:
            return (
                f"historical domain: named entity '{keyword.named_entity}' not "
                f"found in asset title/description -- thematic similarity is "
                "not enough, rejecting"
            )

    if keyword.domain == Domain.EARTHLY_PLACE and keyword.expected_region_hint:
        haystack = f"{asset.title} {asset.description}".lower()
        if keyword.expected_region_hint.lower() not in haystack:
            return (
                f"earthly-place: expected region hint "
                f"'{keyword.expected_region_hint}' not corroborated by asset "
                f"title/description '{asset.title}' -- rejecting rather than "
                "assuming the geocoder matched the right real-world place"
            )

    return None


def score(keyword: VisualKeyword, asset: SourcedAsset) -> ScoredMatch:
    # Applied before anything else, for every source: a visually
    # inconsistent illustration/vector/craft-photo substitute is rejected
    # outright, regardless of how well its title/description otherwise
    # overlaps the keyword -- see content_type_filter.py's module
    # docstring for the real CH1 evidence this closes.
    non_photo_rejection = content_type_filter.reject_reason(asset)
    if non_photo_rejection:
        return ScoredMatch(
            asset=asset,
            keyword=keyword,
            confidence=0.0,
            accepted=False,
            reason=non_photo_rejection,
        )

    domain_rejection = _verify_domain_specific(keyword, asset)
    if domain_rejection:
        return ScoredMatch(
            asset=asset,
            keyword=keyword,
            confidence=0.0,
            accepted=False,
            reason=domain_rejection,
        )

    confidence = (
        asset.api_relevance_score
        if asset.api_relevance_score is not None
        else _keyword_overlap_score(keyword, asset)
    )
    confidence = max(0.0, min(1.0, confidence))

    accepted = confidence >= CONFIDENCE_THRESHOLD
    requires_review = keyword.domain in (Domain.HISTORICAL_FIGURE, Domain.HISTORICAL_PLACE)

    reason = (
        f"confidence {confidence:.2f} >= threshold {CONFIDENCE_THRESHOLD}"
        if accepted
        else f"confidence {confidence:.2f} < threshold {CONFIDENCE_THRESHOLD} -- rejected, not substituted"
    )

    return ScoredMatch(
        asset=asset,
        keyword=keyword,
        confidence=confidence,
        accepted=accepted,
        reason=reason,
        requires_manual_review=accepted and requires_review,
    )


def best_match(keyword: VisualKeyword, candidates: list[SourcedAsset]) -> ScoredMatch | None:
    """Score all candidates, return the best ACCEPTED match, or None if
    nothing cleared the bar. Never returns a below-threshold match."""
    scored = [score(keyword, asset) for asset in candidates]
    accepted = [m for m in scored if m.accepted]
    if not accepted:
        return None
    return max(accepted, key=lambda m: m.confidence)
