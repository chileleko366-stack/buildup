"""Pixabay client -- STUB, same rationale as pexels.py.

No PIXABAY_API_KEY is available in the environment this module was built in.
"""

from __future__ import annotations

import os

import requests

from ..errors import NotConfiguredError
from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

PIXABAY_SEARCH_URL = "https://pixabay.com/api/"


class PixabayClient(AssetClient):
    name = "pixabay"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("PIXABAY_API_KEY")

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        if not self.api_key:
            raise NotConfiguredError(
                "PIXABAY_API_KEY is not set. Not falling back to a placeholder "
                "image -- per the fail-loud rule, this beat must be flagged, "
                "not silently filled with a generic asset."
            )
        resp = requests.get(
            PIXABAY_SEARCH_URL,
            params={"key": self.api_key, "q": keyword.text, "per_page": 5},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            SourcedAsset(
                source=self.name,
                asset_id=str(hit["id"]),
                title=hit.get("tags", ""),
                description=hit.get("tags", ""),
                url=hit["largeImageURL"],
                api_relevance_score=None,
            )
            for hit in data.get("hits", [])
        ]
