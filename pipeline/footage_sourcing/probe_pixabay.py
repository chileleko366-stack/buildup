"""Direct Pixabay probe -- pixabay is CH1/CH2/CH4's SECONDARY source
(config.py's CHANNEL_SOURCES), and resolve.py's routing only calls a
secondary client when the primary (pexels) returns zero candidates for
that beat -- which never happened in this repo's real CI run so far
(pexels returned candidates for every CH1/CH2/CH4 beat tried). That means
PIXABAY_API_KEY has never actually been exercised end-to-end despite
being present in the repo's secrets, confirmed vs. assumed.

This calls PixabayClient.search() directly, bypassing routing order, so
its real reachability/auth can be confirmed on its own rather than left
as "untested because we got lucky with the primary." Run via:
    python3 -m pipeline.footage_sourcing.probe_pixabay
"""

from __future__ import annotations

from .clients.pixabay import PixabayClient
from .types import ChannelId, Domain, VisualKeyword


def main() -> None:
    keyword = VisualKeyword(
        text="brain", domain=Domain.ABSTRACT, channel=ChannelId.CH1,
        beat_id="pixabay-probe", named_entity=None,
    )
    try:
        results = PixabayClient().search(keyword)
    except Exception as e:
        print(f"PIXABAY PROBE FAILED: {type(e).__name__}: {e}")
        return
    if not results:
        print("PIXABAY PROBE: 0 results (real call succeeded, no matches)")
        return
    print(f"PIXABAY PROBE: {len(results)} results, first = {results[0].url}")


if __name__ == "__main__":
    main()
