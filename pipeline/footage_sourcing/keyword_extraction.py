"""Beat -> visual keywords, via an LLM call -- STUB.

Per 04_ASSET_ACCURACY_BIBLE.md §3 points 1-2: an LLM extracts 2-4 concrete
visual keywords per script beat, each tagged with a `domain` (the field
that drives all downstream routing).

No LLM API key (Groq/Gemini/Anthropic/etc.) is available in the environment
this module was built in -- confirmed by checking `env` during this build,
not assumed. 03_SCRIPT_BIBLE.md §4 references an "existing" Groq/Gemini
shot_brief generator, but that assumes the prior repo, which does not exist
here (see CLAUDE.md "Repo status"). This build makes no choice of provider;
that decision needs a real key and is left to whoever wires one in.

Real interface, gated behind NotConfiguredError, same pattern as the keyed
asset clients -- no mock keyword output pretending to be LLM extraction.
"""

from __future__ import annotations

import os

from .errors import NotConfiguredError
from .types import ChannelId, VisualKeyword

# Any of these being set is enough to know *a* provider is configured; the
# actual call implementation still needs to be written once a provider is
# chosen (see NotConfiguredError message below).
_KNOWN_PROVIDER_ENV_VARS = ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY")


def extract_keywords(
    beat_text: str, channel: ChannelId, beat_id: str
) -> list[VisualKeyword]:
    """Extract 2-4 visual keywords from a script beat.

    Raises NotConfiguredError unless a provider key is present -- this is
    intentional. Do not add a "just return generic keywords" fallback here;
    that is precisely the "close enough" substitution the asset-accuracy
    bible's fail-loud rule forbids.
    """
    configured = [v for v in _KNOWN_PROVIDER_ENV_VARS if os.environ.get(v)]
    if not configured:
        raise NotConfiguredError(
            "No LLM provider is configured for keyword extraction (checked "
            f"{', '.join(_KNOWN_PROVIDER_ENV_VARS)}). This step cannot run "
            "without one -- per the fail-loud rule, callers must flag the "
            "beat for manual review rather than fabricate keywords."
        )
    raise NotImplementedError(
        f"A provider key was found ({configured[0]}) but the actual LLM "
        "call is not implemented yet -- this stub only proves the "
        "configuration check works. Implement the call for the chosen "
        "provider before using this in a real pipeline run."
    )
