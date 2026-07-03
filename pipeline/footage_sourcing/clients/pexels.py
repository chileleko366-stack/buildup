"""Pexels client -- REAL, confirmed working against a real CI run
(2026-07-03): real accepted photo URLs returned for CH1/CH2/CH4.

Real, observed quality bug from that same run: `photo["src"]["large"]` is
Pexels' ~940x650 landscape-cropped size (per Pexels' own documented `src`
size variants) -- for this repo's 720x1280 PORTRAIT canvas,
SourcedBackground.tsx renders it with `object-fit: cover`, which means a
~650px-tall source gets upscaled roughly 2x to fill a 1280px-tall frame,
producing visible softness regardless of the original photo's quality.
Switched to `large2x` (Pexels' next tier up, ~1880x1250) so the source
is taller than the canvas instead of needing to be stretched past its
native resolution. `original` (full uploaded resolution) was considered
and rejected: it's unbounded in size per photo, which would add
unpredictable download/render time for no guaranteed quality gain over
large2x's already-portrait-covering height.
"""

from __future__ import annotations

import os

import requests

from ..errors import NotConfiguredError
from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"


class PexelsClient(AssetClient):
    name = "pexels"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("PEXELS_API_KEY")

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        if not self.api_key:
            raise NotConfiguredError(
                "PEXELS_API_KEY is not set. Not falling back to a placeholder "
                "image -- per the fail-loud rule, this beat must be flagged, "
                "not silently filled with a generic asset."
            )
        resp = requests.get(
            PEXELS_SEARCH_URL,
            headers={"Authorization": self.api_key},
            params={"query": keyword.text, "per_page": 5},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            SourcedAsset(
                source=self.name,
                asset_id=str(photo["id"]),
                title=photo.get("alt", ""),
                description=photo.get("alt", ""),
                url=photo["src"]["large2x"],
                api_relevance_score=None,  # Pexels doesn't return a relevance score
            )
            for photo in data.get("photos", [])
        ]
