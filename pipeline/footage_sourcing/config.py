"""Per-channel asset source allow-list, transcribed exactly from
04_ASSET_ACCURACY_BIBLE.md §2's table. Do not add sources here without
updating the bible reference in the comment -- this table IS the fail-loud
boundary between "sourced correctly" and "structurally forbidden."
"""

from __future__ import annotations

from .types import ChannelId, Domain

# Client names correspond to modules in clients/.
CHANNEL_SOURCES: dict[ChannelId, dict[str, list[str] | str]] = {
    ChannelId.CH1: {"primary": "pexels", "secondary": "pixabay", "never": ["ai_diagram_unreviewed"]},
    ChannelId.CH2: {"primary": "pexels", "secondary": "pixabay", "never": ["unverified_named_entity_stock"]},
    ChannelId.CH3: {"primary": "wikimedia", "secondary": "loc", "never": ["nominatim"]},
    ChannelId.CH4: {"primary": "pexels", "secondary": "pixabay", "never": ["nominatim", "unverified_brain_scan"]},
    ChannelId.CH5: {"primary": "wikimedia", "secondary": "loc", "never": ["nominatim"]},
    ChannelId.CH6: {"primary": "nasa", "secondary": None, "never": ["generic_stock"]},
}

# Hard rule from §1: which domains may NEVER be routed to a geocoder,
# regardless of channel. Enforced in source_router.py, not just documented.
GEOCODING_FORBIDDEN_DOMAINS = {
    Domain.SPACE,
    Domain.HISTORICAL_FIGURE,
    Domain.HISTORICAL_PLACE,
}

# §3 point 5 threshold. NOT specified as a number anywhere in the bible --
# the bible says "below-threshold results are rejected" but gives no value.
# This default is this build's own choice, not a confirmed bible number;
# flagged here the same way DuotoneGrade's filter values are flagged as
# unverified. Tune once real accept/reject outcomes are reviewed.
CONFIDENCE_THRESHOLD = 0.5
