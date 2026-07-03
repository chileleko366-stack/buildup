"""Library of Congress client -- REAL implementation, keyless.

Per 04_ASSET_ACCURACY_BIBLE.md §2, secondary source for CH3/CH5. Public
loc.gov/search JSON API, no key required.

Real, observed behavior (2026-07-03 CI run, first time this ever reached a
real network path): loc.gov returned a real HTTP 403 with a Cloudflare
"Just a moment..." bot-challenge page body -- not a loc.gov application
error. This request previously sent no User-Agent header at all (the
default `python-requests/X` UA is a well-documented Cloudflare
bot-management trigger); added a descriptive one, matching the same
convention wikimedia.py already uses. If Cloudflare's challenge here is a
real JS/browser-fingerprint check (not just a UA check), this will not be
enough to pass it -- a plain HTTP client fundamentally cannot execute
Cloudflare's JS challenge; confirm via a fresh run rather than assume
either way.
"""

from __future__ import annotations

import requests

from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

LOC_SEARCH_URL = "https://www.loc.gov/search/"
USER_AGENT = "DopamineStudiosFootageSourcing/0.1 (build pipeline; contact via repo)"


class LocClient(AssetClient):
    name = "loc"

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        query = keyword.named_entity or keyword.text
        resp = requests.get(
            LOC_SEARCH_URL,
            params={"q": query, "fo": "json", "c": 5, "fa": "online-format:image"},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        assets: list[SourcedAsset] = []
        for item in results:
            image_urls = item.get("image_url") or []
            url = image_urls[-1] if image_urls else ""
            assets.append(
                SourcedAsset(
                    source=self.name,
                    asset_id=str(item.get("id", "")),
                    title=item.get("title", ""),
                    description=(item.get("description") or [""])[0]
                    if isinstance(item.get("description"), list)
                    else (item.get("description") or ""),
                    url=url,
                    api_relevance_score=None,
                )
            )
        return assets
