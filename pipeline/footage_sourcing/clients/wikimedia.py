"""Wikimedia Commons client -- REAL implementation, keyless.

Per 04_ASSET_ACCURACY_BIBLE.md §2, primary source for CH3/CH5. Public API,
no key required (User-Agent recommended per Wikimedia's usage policy).

NOTE: this session's egress policy denies commons.wikimedia.org (confirmed
via direct curl -- 403 from the proxy). Code is real, untested live here.
"""

from __future__ import annotations

import requests

from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "DopamineStudiosFootageSourcing/0.1 (build pipeline; contact via repo)"


class WikimediaClient(AssetClient):
    name = "wikimedia"

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        query = keyword.named_entity or keyword.text
        resp = requests.get(
            COMMONS_API_URL,
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": f"{query} filetype:bitmap",
                "gsrnamespace": 6,  # File namespace
                "gsrlimit": 5,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        pages = (data.get("query") or {}).get("pages") or {}
        assets: list[SourcedAsset] = []
        for page in pages.values():
            imageinfo = (page.get("imageinfo") or [{}])[0]
            extmeta = imageinfo.get("extmetadata", {})
            description = extmeta.get("ImageDescription", {}).get("value", "")
            assets.append(
                SourcedAsset(
                    source=self.name,
                    asset_id=str(page.get("pageid", "")),
                    title=page.get("title", ""),
                    description=description,
                    url=imageinfo.get("url", ""),
                    api_relevance_score=None,
                )
            )
        return assets
