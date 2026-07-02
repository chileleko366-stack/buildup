"""Domain + channel -> client routing.

Per 04_ASSET_ACCURACY_BIBLE.md §2 point 3: "`domain` determines which
source router handles the query -- this is the mechanism that prevents a
space keyword from ever reaching a places API." That guarantee lives here:
route() looks up CHANNEL_SOURCES for the channel's primary/secondary client
names, then hard-checks GEOCODING_FORBIDDEN_DOMAINS before ever
instantiating a geocoding client, regardless of what CHANNEL_SOURCES says.
"""

from __future__ import annotations

from .clients import (
    AssetClient,
    LocClient,
    NasaClient,
    NominatimClient,
    PexelsClient,
    PixabayClient,
    WikimediaClient,
)
from .config import CHANNEL_SOURCES, GEOCODING_FORBIDDEN_DOMAINS
from .errors import DomainRoutingViolation
from .types import ChannelId, VisualKeyword

_CLIENT_REGISTRY: dict[str, type[AssetClient]] = {
    "pexels": PexelsClient,
    "pixabay": PixabayClient,
    "wikimedia": WikimediaClient,
    "loc": LocClient,
    "nasa": NasaClient,
    "nominatim": NominatimClient,
}


def route(keyword: VisualKeyword) -> list[AssetClient]:
    """Return the ordered list of clients to try for this keyword (primary
    first, then secondary if the primary yields nothing confident)."""

    if keyword.domain.value == "earthly-place" and keyword.channel not in (
        ChannelId.CH1,
        ChannelId.CH2,
        ChannelId.CH4,
    ):
        # §4: earthly-place is "rare, only if a channel script names a real
        # modern location" -- not part of any channel's normal allow-list.
        # Route explicitly to Nominatim + a verification step, never through
        # a channel's configured primary/secondary (which don't know how to
        # geocode).
        _guard_against_forbidden_domain(keyword)
        return [NominatimClient()]

    sources = CHANNEL_SOURCES.get(keyword.channel)
    if sources is None:
        raise ValueError(f"No source configuration for channel {keyword.channel}")

    _guard_against_forbidden_domain(keyword)

    clients: list[AssetClient] = []
    for key in ("primary", "secondary"):
        name = sources.get(key)
        if not name:
            continue
        client_cls = _CLIENT_REGISTRY.get(name)  # type: ignore[arg-type]
        if client_cls is None:
            raise ValueError(f"Unknown client '{name}' referenced in CHANNEL_SOURCES")
        clients.append(client_cls())
    return clients


def _guard_against_forbidden_domain(keyword: VisualKeyword) -> None:
    """Hard rule from §1, enforced structurally, not just documented.

    This function exists purely so route() can never silently hand a
    forbidden-domain keyword to a geocoder-shaped client, even if a future
    edit to CHANNEL_SOURCES accidentally adds "nominatim" somewhere.
    """
    if keyword.domain in GEOCODING_FORBIDDEN_DOMAINS:
        sources = CHANNEL_SOURCES.get(keyword.channel, {})
        for key in ("primary", "secondary"):
            if sources.get(key) == "nominatim":
                raise DomainRoutingViolation(
                    f"Channel {keyword.channel} configures nominatim as a "
                    f"source, but keyword domain '{keyword.domain.value}' is "
                    "in GEOCODING_FORBIDDEN_DOMAINS -- refusing to route."
                )
