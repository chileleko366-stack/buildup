"""Shared data types for the footage-sourcing module.

Field names/domains are taken directly from 04_ASSET_ACCURACY_BIBLE.md §2-3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Domain(str, Enum):
    """The 7 domains named in 04_ASSET_ACCURACY_BIBLE.md §2 point 2.

    This is the field that determines routing -- it's the mechanism that
    makes it structurally impossible for a space keyword to reach a
    geocoding API (the exact bug class this bible exists to prevent).
    """

    EARTHLY_PLACE = "earthly-place"
    PERSON = "person"
    OBJECT = "object"
    SPACE = "space"
    HISTORICAL_FIGURE = "historical-figure"
    HISTORICAL_PLACE = "historical-place"
    ABSTRACT = "abstract"


class ChannelId(str, Enum):
    CH1 = "CH1"  # Dopamine Loop (psychology)
    CH2 = "CH2"  # FinanceFiction
    CH3 = "CH3"  # Redacted (declassified history)
    CH4 = "CH4"  # The Grey Matter (neuroscience)
    CH5 = "CH5"  # The Quiet Record (history)
    CH6 = "CH6"  # Red Space Facts


@dataclass(frozen=True)
class VisualKeyword:
    """One of the 2-4 visual keywords extracted per script beat.

    Per 04_ASSET_ACCURACY_BIBLE.md §3 point 1: "concrete nouns: subject,
    setting, object -- not abstract concepts" (ABSTRACT domain exists for
    when the LLM can't avoid one, but concrete keywords are preferred).
    """

    text: str
    domain: Domain
    channel: ChannelId
    beat_id: str
    named_entity: str | None = None  # required for historical-* verification, §4
    expected_region_hint: str | None = None  # earthly-place §4: "France vs. Texas vs. Ontario"


@dataclass(frozen=True)
class SourcedAsset:
    """A single candidate asset returned by a source client, pre-scoring."""

    source: str  # e.g. "pexels", "wikimedia", "nasa"
    asset_id: str
    title: str
    description: str
    url: str
    api_relevance_score: float | None  # source's own score, if it provides one
    catalog_id: str | None = None  # NASA catalog ID, for CH6 §4 verification


@dataclass(frozen=True)
class ScoredMatch:
    """A SourcedAsset after confidence scoring, accept/reject decided."""

    asset: SourcedAsset
    keyword: VisualKeyword
    confidence: float
    accepted: bool
    reason: str
    requires_manual_review: bool = False


@dataclass
class SourcingResult:
    """Final outcome for one beat's one keyword -- what gets written to the
    shot brief, or the flag surfaced to a human if nothing qualified."""

    keyword: VisualKeyword
    match: ScoredMatch | None
    flagged_for_review: bool
    flag_reason: str | None = None
    cache_hit: bool = False
