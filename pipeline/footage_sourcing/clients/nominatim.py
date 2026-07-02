"""Nominatim (OpenStreetMap) geocoder client -- REAL implementation, keyless.

This is the client class involved in the prior bug 04_ASSET_ACCURACY_BIBLE.md
opens with (a celestial body's name got geocoded and matched to a European
city). Per §1's hard rule, this client must be UNREACHABLE for `space`,
`historical-figure`, and `historical-place` domains -- enforced in
source_router.py via GEOCODING_FORBIDDEN_DOMAINS, not just by convention
here. This class itself also refuses to run for those domains as a second,
redundant guard, since the whole point of this bible is "structurally
impossible," not "policy says don't."

NOTE: this session's egress policy was not tested against nominatim.
openstreetmap.org specifically, but api.nasa.gov/commons.wikimedia.org/
www.loc.gov were all denied -- assume the same applies until proven
otherwise; do not assume this client works live without checking.
"""

from __future__ import annotations

import requests

from ..config import GEOCODING_FORBIDDEN_DOMAINS
from ..errors import DomainRoutingViolation
from ..types import SourcedAsset, VisualKeyword
from .base import AssetClient

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "DopamineStudiosFootageSourcing/0.1 (build pipeline; contact via repo)"


class NominatimClient(AssetClient):
    name = "nominatim"

    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        if keyword.domain in GEOCODING_FORBIDDEN_DOMAINS:
            raise DomainRoutingViolation(
                f"Refusing to geocode a '{keyword.domain.value}' keyword "
                f"('{keyword.text}') -- this is exactly the class of bug "
                "04_ASSET_ACCURACY_BIBLE.md exists to prevent."
            )
        resp = requests.get(
            NOMINATIM_SEARCH_URL,
            params={"q": keyword.text, "format": "json", "limit": 5},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            SourcedAsset(
                source=self.name,
                asset_id=str(place.get("place_id", "")),
                title=place.get("display_name", ""),
                description=place.get("type", ""),
                url="",  # Nominatim returns place data, not imagery -- the
                # asset-sourcing step for earthly-place still needs an
                # actual image client downstream; this client only confirms
                # the place resolves to what the script's context implies
                # (§4's "validate the returned country/region" check).
                api_relevance_score=place.get("importance"),
            )
            for place in data
        ]
