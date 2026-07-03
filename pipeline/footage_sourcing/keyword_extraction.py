"""Beat -> visual keywords, via a real LLM call.

Per 04_ASSET_ACCURACY_BIBLE.md §3 points 1-2: an LLM extracts 2-4 concrete
visual keywords per script beat, each tagged with a `domain` (the field
that drives all downstream routing).

## Provider: NVIDIA NIM (`NVIDIA_API_KEY`)

Added this pass -- the user confirmed `NVIDIA_API_KEY` is the intended
provider (it's one of the 4 secrets this pass was asked to check for).
NVIDIA's hosted NIM endpoint (`integrate.api.nvidia.com/v1`) is a real,
documented, OpenAI-compatible chat-completions API (build.nvidia.com) --
implemented here via plain `requests` POST rather than adding the
`openai` package as a dependency, since the request/response shape is a
single well-documented JSON POST, not something that needs a client SDK.

GROQ_API_KEY/GEMINI_API_KEY/ANTHROPIC_API_KEY are kept as previously-
recognized provider env vars (Phase 2's original stub checked for these,
before NVIDIA was named) but have no call implementation here -- only
NVIDIA_API_KEY has a real, callable path. If one of the other three is
set but NVIDIA_API_KEY isn't, this still raises NotImplementedError
naming which key was found, same as before.

## Reality check on this session's egress

`integrate.api.nvidia.com` and `api.nvidia.com` are both confirmed
egress-blocked from this session (403 at the CONNECT tunnel, via the
proxy's own status log -- `"kind": "connect_rejected", "detail": "gateway
answered 403 to CONNECT"`), the same as every other real data-source host
this repo has tried. So even with a real key configured, this call cannot
succeed FROM THIS SESSION. The code below is real and untested live here,
same situation as the NASA/Wikimedia/LOC clients -- it should work as-is
wherever egress to NVIDIA's API is actually permitted (e.g. a GitHub
Actions runner).
"""

from __future__ import annotations

import json
import os
import re

import requests

from .errors import NotConfiguredError
from .types import ChannelId, Domain, VisualKeyword

_KNOWN_PROVIDER_ENV_VARS = ("NVIDIA_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY")

NVIDIA_CHAT_COMPLETIONS_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Real, currently-hosted NVIDIA NIM model per build.nvidia.com's own model
# catalog -- a general instruction-following chat model, not a vision model
# (this call only reasons over beat TEXT, it doesn't need to see images).
NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

_VALID_DOMAINS = {d.value for d in Domain}

_SYSTEM_PROMPT = (
    "You extract visual keywords from short-form video narration for footage "
    "sourcing. For the given beat of narration, return 2-4 concrete visual "
    "keywords (subject, setting, or object -- not abstract concepts unless "
    "unavoidable). For each keyword, assign exactly one domain from this set: "
    "earthly-place, person, object, space, historical-figure, historical-place, "
    "abstract. If the keyword names a specific real person, place, or space "
    "object, also return named_entity (the real proper name) so it can be "
    "verified against source results -- otherwise omit it. "
    'Respond ONLY with JSON: {"keywords": [{"text": str, "domain": str, '
    '"named_entity": str|null}]}. No prose, no markdown fences.'
)


def _build_request_body(beat_text: str) -> dict:
    return {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": beat_text},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }


def _parse_response(raw_content: str) -> list[dict]:
    """Real LLM output isn't guaranteed to be bare JSON even when asked --
    strip markdown code fences if present, then parse. Raises (not
    silently returns []) on malformed output -- fail loud, per this
    module's own established rule."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())
    data = json.loads(cleaned)
    keywords = data.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        raise ValueError(f"LLM response had no usable 'keywords' list: {raw_content!r}")
    return keywords


def extract_keywords(beat_text: str, channel: ChannelId, beat_id: str) -> list[VisualKeyword]:
    """Extract 2-4 visual keywords from a script beat via a real NVIDIA NIM
    chat-completions call.

    Raises NotConfiguredError if NVIDIA_API_KEY isn't set (even if one of
    the other 3 known provider vars is, since only NVIDIA has a real call
    implemented -- see module docstring). Raises on any HTTP/parse failure
    too -- no silent fallback to generic keywords, per the fail-loud rule
    this whole module follows."""
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        configured = [v for v in _KNOWN_PROVIDER_ENV_VARS if os.environ.get(v)]
        if configured:
            raise NotImplementedError(
                f"A provider key was found ({configured[0]}) but only NVIDIA_API_KEY has a "
                "real call implemented in this module -- see keyword_extraction.py's docstring."
            )
        raise NotConfiguredError(
            "NVIDIA_API_KEY is not set. This step cannot run without it -- per the "
            "fail-loud rule, callers must flag the beat for manual review rather "
            "than fabricate keywords."
        )

    resp = requests.post(
        NVIDIA_CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=_build_request_body(beat_text),
        timeout=30,
    )
    resp.raise_for_status()
    raw_content = resp.json()["choices"][0]["message"]["content"]
    raw_keywords = _parse_response(raw_content)

    results: list[VisualKeyword] = []
    for kw in raw_keywords:
        domain_str = kw.get("domain", "")
        if domain_str not in _VALID_DOMAINS:
            raise ValueError(f"LLM returned an unrecognized domain {domain_str!r} for keyword {kw!r}")
        results.append(
            VisualKeyword(
                text=kw["text"],
                domain=Domain(domain_str),
                channel=channel,
                beat_id=beat_id,
                named_entity=kw.get("named_entity") or None,
            )
        )
    if not (2 <= len(results) <= 4):
        raise ValueError(f"LLM returned {len(results)} keywords for beat {beat_id!r}, expected 2-4")
    return results
