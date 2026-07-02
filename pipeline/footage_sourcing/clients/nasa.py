"""NASA Image and Video Library client -- REAL implementation, keyless.

Per 04_ASSET_ACCURACY_BIBLE.md §2, this is CH6's only allowed source ("Any
general stock photo site for planetary/astronomical imagery" is explicitly
forbidden). The search endpoint (images-api.nasa.gov) doesn't require an
API key at all -- NASA's `api.nasa.gov` key (default "DEMO_KEY", rate-limited
per NASA's own published limits) is only needed for other NASA APIs (APOD,
etc.), not this one, so no key gating is needed here.

NOTE: this session's egress policy denies api.nasa.gov and images-api.nasa.gov
(confirmed via a direct curl during this build -- 403 from the proxy, an org
policy denial, not a missing-key issue). This code is real and untested live
in this session; it should work as-is once run somewhere with network access
to NASA's API (e.g. a GitHub Actions runner, once Phase 5 wires that up).
"""

from __future__ import annotations

import requests

from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

NASA_IMAGES_SEARCH_URL = "https://images-api.nasa.gov/search"


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
            href = links[0]["href"] if links else ""
            assets.append(
                SourcedAsset(
                    source=self.name,
                    asset_id=meta.get("nasa_id", ""),
                    title=meta.get("title", ""),
                    description=meta.get("description", ""),
                    url=href,
                    api_relevance_score=None,
                    catalog_id=meta.get("nasa_id"),
                )
            )
        return assets
