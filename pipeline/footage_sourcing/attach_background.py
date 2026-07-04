"""Bridges footage_sourcing.resolve to pipeline/shot_brief.py's Beat --
attempts a REAL resolve_keyword() call for a beat's primary visual
keyword, downloads the accepted asset to a real local file (see below),
and returns the (background_asset_url, background_sourcing_status) pair
to attach to that Beat. Shared by pipeline/ch6_short_001.py and
pipeline/render_channel_short.py so both channel-generation paths use the
identical real resolution attempt, not two different implementations.

## Real render-time bug this download step fixes (2026-07-04 CI runs)

Real evidence, confirmed from actual CI logs across two separate runs:
the SAME Pixabay image URL failed with a real, repeated HTTP 429 partway
through rendering (e.g. at frame ~495/1912, and again at frame ~999 in a
different run), eventually exhausting real retries and crashing the
whole render (src/remotion/SourcedBackground.tsx's own header comment
documents 3 rounds of retry/degradation fixes attempted for this before
the real root cause was found).

Root cause, confirmed by reading this exact file (as it existed before
this pass): `background_asset_url` was the RAW REMOTE URL returned by
resolve_keyword(), passed straight through to an <img>/<Img> tag in the
Remotion composition -- meaning every one of a beat's ~40-150 frames,
rendered with real concurrency across multiple parallel Chromium tabs
(confirmed via "Tab 0"/"Tab 1" appearing in real CI logs), independently
re-requested the SAME remote image from the SAME CDN concurrently. That
burst-request pattern is exactly what triggers a CDN's rate limiter.
Retry/backoff on the RENDER side (SourcedBackground.tsx) could only ever
tolerate this, never remove it, since the underlying repeated-request
pattern was unchanged no matter how much retry budget was added there.

Real fix: download each accepted asset EXACTLY ONCE here, during the
Python resolution step (which already runs once per beat, before
Remotion ever starts rendering), to a real local file under
public/sourced_assets/. Remotion's render step then reads that local
file via staticFile() -- zero network requests, so it cannot be rate-
limited no matter how many frames or parallel tabs reference it.
`background_asset_url` is now a LOCAL path relative to `public/` (e.g.
"sourced_assets/CH1/hook.jpg"), never a remote URL --
SourcedBackground.tsx wraps it in staticFile() accordingly. If the
download itself fails (a real, separate network error from the
resolution/scoring call that already succeeded), that is treated the
same as sourcing never producing a confident match -- flagged with the
real error, not silently substituted with the (rate-limitable) remote
URL.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests

from .cache import AssetCache
from .resolve import resolve_keyword
from .types import VisualKeyword

_shared_cache = AssetCache()

PUBLIC_ASSETS_DIR = Path("public/sourced_assets")
# Real, browser-renderable formats this pipeline's sources actually return
# (jpg/png from Pexels/Pixabay/NASA/Wikimedia/LOC) -- an unrecognized
# extension falls back to .jpg rather than guessing wrong and producing an
# undecodable local file.
_ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
_DEFAULT_EXTENSION = ".jpg"


def _local_asset_path(channel: str, beat_id: str, url: str) -> Path:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        ext = _DEFAULT_EXTENSION
    return PUBLIC_ASSETS_DIR / channel / f"{beat_id}{ext}"


def _download_asset(url: str, dest: Path) -> None:
    """Real, single, one-shot download -- no retries here deliberately:
    this runs once per beat during generation, well before Remotion's
    real per-frame render concurrency exists, so there is no burst-
    request pattern to protect against on THIS side. A transient failure
    here is a real, single network call failing once; surfaced to the
    caller as a real error, not retried into a different failure mode."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=30, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)


def resolve_beat_background(visual_keywords: list[VisualKeyword]) -> tuple[str | None, str]:
    """Real attempt, using this beat's first visual keyword (the primary
    subject, per how these are authored -- one keyword is enough for a
    single background asset per beat). Cascade beats have no
    visual_keywords at all (see shot_brief.py's Beat docstring), so those
    short-circuit here without attempting a network call.

    On an accepted match, downloads the real asset to a real local file
    (see module docstring for why) and returns that local relative path
    -- never the remote URL directly, which is what caused real render-
    time rate-limit failures in CI."""
    if not visual_keywords:
        return None, "cascade beat -- no keyword to source"

    keyword = visual_keywords[0]
    result = resolve_keyword(keyword, cache=_shared_cache)
    if result.match is None:
        return None, result.flag_reason or "no confident match"

    asset = result.match.asset
    local_path = _local_asset_path(keyword.channel.value, keyword.beat_id, asset.url)
    try:
        _download_asset(asset.url, local_path)
    except Exception as e:
        return None, f"accepted match but real download failed: {type(e).__name__}: {e} (url={asset.url})"

    relative_path = local_path.relative_to("public").as_posix()
    # Source name embedded here (not just "accepted: <reason>") because
    # background_asset_url is now a local path, not a remote URL --
    # callers that used to infer the source from the URL's hostname (e.g.
    # pipeline/verify_ch1_visual.py) can no longer do that once it's a
    # local file, so the source name has to be carried explicitly instead.
    return relative_path, f"accepted ({asset.source}): {result.match.reason}"
