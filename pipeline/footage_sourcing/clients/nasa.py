"""NASA Image and Video Library client -- REAL implementation, keyless,
confirmed working against a real CI run (2026-07-03): real accepted
PIA*/GSFC* asset URLs across CH6.

Per 04_ASSET_ACCURACY_BIBLE.md §2, this is CH6's only allowed source ("Any
general stock photo site for planetary/astronomical imagery" is explicitly
forbidden). The search endpoint (images-api.nasa.gov) doesn't require an
API key at all -- NASA's `api.nasa.gov` key (default "DEMO_KEY", rate-limited
per NASA's own published limits) is only needed for other NASA APIs (APOD,
etc.), not this one, so no key gating is needed here.

Real, observed quality bug from that same run: `links[0]["href"]` on the
SEARCH endpoint's response is a real, but real-LOW-resolution, preview --
the actual accepted URLs from that run were literally suffixed
`~thumb.jpg` / `~small.jpg` / `~medium.jpg` (NASA's own real naming
convention for its resolution tiers), never the full-size original.
NASA's own real API separates "search" (metadata + a low-res preview
link only) from "asset" (`images-api.nasa.gov/asset/{nasa_id}`, which
returns EVERY real file variant for that item, including `~orig`). Added
`_best_resolution_url()`, one extra real HTTP call per accepted-search
result, to fetch and prefer the real `~orig`/`~large` variant over
whatever preview tier the search endpoint happened to return -- falling
back to the original search-returned href if the asset call fails for
any reason (fail-soft here specifically, not fail-loud, since a lower-res
real photo is still a real photo, unlike a sourcing rejection).
"""

from __future__ import annotations

import requests

from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

NASA_IMAGES_SEARCH_URL = "https://images-api.nasa.gov/search"
NASA_ASSET_URL_TEMPLATE = "https://images-api.nasa.gov/asset/{nasa_id}"

# Real NASA suffix convention (confirmed from real search-result URLs),
# highest resolution first.
_PREFERRED_SUFFIXES = ("~orig", "~large")


def _best_resolution_url(nasa_id: str, fallback_url: str) -> str:
    if not nasa_id:
        return fallback_url
    try:
        resp = requests.get(NASA_ASSET_URL_TEMPLATE.format(nasa_id=nasa_id), timeout=15)
        resp.raise_for_status()
        hrefs = [item["href"] for item in resp.json().get("collection", {}).get("items", []) if "href" in item]
    except Exception:
        return fallback_url
    for suffix in _PREFERRED_SUFFIXES:
        for href in hrefs:
            if suffix in href:
                return href
    return fallback_url


class NasaClient(AssetClient):
    name = "nasa"

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        resp = requests.get(
            NASA_IMAGES_SEARCH_URL,
            params={"q": keyword.text, "media_type": "image"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("collection", {}).get("items", [])
        assets: list[SourcedAsset] = []
        for item in items:
            meta = (item.get("data") or [{}])[0]
            links = item.get("links") or []
            preview_href = links[0]["href"] if links else ""
            nasa_id = meta.get("nasa_id", "")
            href = _best_resolution_url(nasa_id, preview_href)
            assets.append(
                SourcedAsset(
                    source=self.name,
                    asset_id=nasa_id,
                    title=meta.get("title", ""),
                    description=meta.get("description", ""),
                    url=href,
                    api_relevance_score=None,
                    catalog_id=nasa_id,
                )
            )
        return assets
