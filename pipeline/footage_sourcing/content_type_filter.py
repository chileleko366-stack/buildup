"""Post-fetch content-type heuristic: reject non-photographic candidates.

Real root cause (2026-07-03 CI run, real frames inspected): a single 12s
CH1 short showed a real photograph, then a photo of a physical paper-craft
sculpture ("It's not weak willpower" -- a caliper clamping a paper-cut-out
brain), then a flat cartoon vector illustration ("Every notification" -- a
hand-drawn wifi/speech-bubble sketch over a phone) -- three completely
different visual registers back to back. Two contributing bugs, both real:

1. Neither pexels.py nor pixabay.py was ever asked to exclude illustration/
   vector content. Pixabay's search endpoint has a real, documented
   `image_type` param (all/photo/illustration/vector -- pixabay.com/api/
   docs/); it was never passed, so Pixabay's own illustration/vector
   results (and CH1/CH4's photographic misses that fell through to it as
   the secondary source) were accepted on equal footing with real photos.
   Fixed directly in clients/pixabay.py: `image_type=photo`.
2. channel_scripts.py had several beats whose own keyword text literally
   asked for "... illustration" / "... diagram" (e.g. "brain reward
   pathway illustration") -- of course a search engine handed that query
   returns illustrations. Fixed at the source in channel_scripts.py
   (CH1/CH4) by rewording those to photographable real-world subjects
   (anatomical models, MRI scans, microscopy, people) instead of asking
   for a diagram/illustration.

Pexels has no image_type-equivalent parameter at all (Pexels' entire
catalog is licensed photography, not illustration/vector, by the
platform's own stated scope -- there's nothing to pass), so a mismatched
Pexels result (like the paper-craft-sculpture photo -- a REAL photograph,
just of a craft prop rather than the real subject) is a query-relevance
problem, not a missing API filter. NASA/Wikimedia/LOC likewise expose no
documented photo-vs-illustration/vector filter parameter in their real
search APIs (checked each one's actual docs; none has one) -- Wikimedia
Commons and LOC in particular can just as easily surface a painting,
engraving, or map as a photograph for a historical query.

This module is the second, source-agnostic layer of defense that covers
all five of the above cases uniformly: reject any candidate whose own
title/description metadata contains a term that reliably indicates
non-photographic content (illustration, vector, clipart, diagram, craft/
prop terms, etc.), regardless of which client returned it or whether that
client has its own filter param. It cannot verify a positive ("this IS a
real photo") -- only reject an obvious negative signal already present in
the source's own metadata text. An asset with no matching term is not
judged on this axis at all; keyword-overlap/confidence scoring and the
domain-specific checks in confidence.py still apply exactly as before.
"""

from __future__ import annotations

import re

from .types import SourcedAsset

# Terms observed (or reliably expected, per each source's own tagging
# conventions) in Pexels/Pixabay/Wikimedia/LOC title or description
# metadata that indicate the asset is NOT a straight photograph of its
# real subject -- an illustration, a vector/clip-art graphic, a diagram,
# or a craft/prop/model stand-in (paper sculpture, origami, etc.) used as
# a photographic subject instead of the real thing. Whole-word (or whole-
# phrase, for the multi-word entries) matched only, to avoid rejecting a
# real photograph that merely contains one of these words as an unrelated
# substring.
_NON_PHOTOGRAPHIC_TERMS = (
    "illustration", "illustrated", "vector", "clipart", "clip-art",
    "clip art", "cartoon", "drawing", "drawn", "sketch", "sketched",
    "icon", "icons", "diagram", "infographic", "graphic", "graphics",
    "painting", "painted", "engraving", "line art", "lineart",
    "silhouette", "3d render", "render", "rendered", "cgi", "animation",
    "animated", "paper craft", "papercraft", "paper cut", "papercut",
    "paper sculpture", "origami", "cut-out", "cutout",
)

_TERM_PATTERNS = [
    (term, re.compile(r"\b" + re.escape(term).replace(r"\ ", r"[\s-]+") + r"\b"))
    for term in _NON_PHOTOGRAPHIC_TERMS
]


def reject_reason(asset: SourcedAsset) -> str | None:
    """Returns a rejection reason string if this asset's own metadata
    signals non-photographic content, else None (passes this check --
    does not mean accepted, just not rejected on this axis)."""
    haystack = f"{asset.title} {asset.description}".lower()
    for term, pattern in _TERM_PATTERNS:
        if pattern.search(haystack):
            return (
                f"metadata contains non-photographic term '{term}' in "
                f"title/description -- rejecting rather than accepting an "
                "illustration/craft-photo substitute for a real photograph"
            )
    return None
