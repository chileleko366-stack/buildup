"""Pexels client -- STUB.

No PEXELS_API_KEY is available in the environment this module was built in
(confirmed by checking `env` during this build -- not assumed absent).
Per the explicit build decision, this is a real interface with a real HTTP
call path, gated behind a clear NotConfiguredError rather than mock data,
so wiring in a real key later requires no code changes -- just setting the
env var.
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
                url=photo["src"]["large"],
                api_relevance_score=None,  # Pexels doesn't return a relevance score
            )
            for photo in data.get("photos", [])
        ]
