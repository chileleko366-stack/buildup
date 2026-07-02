"""Local cache layer, keyed by (channel, keyword, domain).

Per 04_ASSET_ACCURACY_BIBLE.md §5:
- Cache accepted assets to avoid re-fetching and build a verified library
  over time.
- Never cache a below-threshold/rejected match.
- Manually-reviewed historical assets get `verified: true` and can be
  reused without re-review; unreviewed ones cannot (§4: "don't
  auto-cache-and-reuse an unreviewed match").

Backed by a flat JSON file rather than a database -- this is a Phase 2
gate-test scale concern (30 sample beats), not a production-scale decision;
revisit storage choice if/when real run volume justifies it.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .types import ChannelId, Domain, ScoredMatch

DEFAULT_CACHE_PATH = Path(__file__).parent / ".cache" / "asset_cache.json"


def _cache_key(channel: ChannelId, keyword_text: str, domain: Domain) -> str:
    return f"{channel.value}::{domain.value}::{keyword_text.lower().strip()}"


class AssetCache:
    def __init__(self, path: Path = DEFAULT_CACHE_PATH):
        self.path = path
        self._data: dict[str, dict] = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text())

    def get(self, channel: ChannelId, keyword_text: str, domain: Domain) -> dict | None:
        """Returns the cached entry only if it's reusable without review:
        entries needing manual review (verified=False) are visible for
        inspection but callers must check `verified` before treating a hit
        as safe to auto-reuse, per §4."""
        return self._data.get(_cache_key(channel, keyword_text, domain))

    def put(self, match: ScoredMatch) -> None:
        if not match.accepted:
            raise ValueError(
                "Refusing to cache a rejected match -- §5 explicitly forbids "
                "caching below-threshold results."
            )
        key = _cache_key(match.keyword.channel, match.keyword.text, match.keyword.domain)
        self._data[key] = {
            "asset": asdict(match.asset),
            "confidence": match.confidence,
            "verified": not match.requires_manual_review,
            "reason": match.reason,
        }
        self._save()

    def mark_verified(self, channel: ChannelId, keyword_text: str, domain: Domain) -> None:
        """Called once a human has manually reviewed a flagged historical
        asset match -- only then may it be reused without re-review."""
        key = _cache_key(channel, keyword_text, domain)
        if key not in self._data:
            raise KeyError(f"No cache entry for {key} to verify")
        self._data[key]["verified"] = True
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True))
