"""Pixabay client -- STUB, same rationale as pexels.py.

No PIXABAY_API_KEY is available in the environment this module was built in.

Real, observed bug (2026-07-03 CI run): Pixabay's search endpoint returns
photos, illustrations, AND vectors together unless told otherwise, and
this client never told it otherwise -- a real cartoon vector illustration
("Every notification" beat) came back through Pixabay this way, mixed in
with real photos from other beats in the same rendered short. Pixabay's
API docs (pixabay.com/api/docs/) document a real `image_type` param with
values `all` (default) / `photo` / `illustration` / `vector`. Pinned to
`photo` here so this client can never again hand back an illustration or
vector graphic -- see content_type_filter.py for the second, source-
agnostic layer of defense that also covers Pexels/NASA/Wikimedia/LOC,
none of which expose an equivalent param.
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
            params={"key": self.api_key, "q": keyword.text, "per_page": 5, "image_type": "photo"},
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
