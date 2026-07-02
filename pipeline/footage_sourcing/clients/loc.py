"""Library of Congress client -- REAL implementation, keyless.

Per 04_ASSET_ACCURACY_BIBLE.md §2, secondary source for CH3/CH5. Public
loc.gov/search JSON API, no key required.

NOTE: this session's egress policy denies www.loc.gov (confirmed via direct
curl -- 403 from the proxy). Code is real, untested live here.
"""

from __future__ import annotations

import requests

from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

LOC_SEARCH_URL = "https://www.loc.gov/search/"


class LocClient(AssetClient):
    name = "loc"

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        query = keyword.named_entity or keyword.text
        resp = requests.get(
            LOC_SEARCH_URL,
            params={"q": query, "fo": "json", "c": 5, "fa": "online-format:image"},
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
