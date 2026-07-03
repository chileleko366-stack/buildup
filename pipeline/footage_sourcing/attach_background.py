"""Bridges footage_sourcing.resolve to pipeline/shot_brief.py's Beat --
attempts a REAL resolve_keyword() call for a beat's primary visual
keyword and returns the (background_asset_url, background_sourcing_status)
pair to attach to that Beat. Shared by pipeline/ch6_short_001.py and
pipeline/render_channel_short.py so both channel-generation paths use the
identical real resolution attempt, not two different implementations.
"""

from __future__ import annotations

from .cache import AssetCache
from .resolve import resolve_keyword
from .types import VisualKeyword

_shared_cache = AssetCache()


def resolve_beat_background(visual_keywords: list[VisualKeyword]) -> tuple[str | None, str]:
    """Real attempt, using this beat's first visual keyword (the primary
    subject, per how these are authored -- one keyword is enough for a
    single background asset per beat). Cascade beats have no
    visual_keywords at all (see shot_brief.py's Beat docstring), so those
    short-circuit here without attempting a network call."""
    if not visual_keywords:
        return None, "cascade beat -- no keyword to source"

    keyword = visual_keywords[0]
    result = resolve_keyword(keyword, cache=_shared_cache)
    if result.match is not None:
        return result.match.asset.url, f"accepted: {result.match.reason}"
    return None, result.flag_reason or "no confident match"
