"""Real LLM-driven script generation, via Groq -- the actual Phase 4/5 step
this project never had. Until this module, pipeline/channel_scripts.py
(CH1-CH5) and pipeline/ch6_short_001.py (CH6) were 100% hand-authored,
static BeatSpec lists: every render of a given channel produced the exact
same script, forever. Both files' own docstrings say why: no LLM provider
key was configured. `GROQ_API_KEY` is now confirmed real (checked via a
temporary CI debug-echo step, never printed -- see
.github/workflows/render-shorts.yml git history) -- this module replaces
the static scripts with a real Groq chat-completions call per generation.

## Provider

Groq's OpenAI-compatible chat-completions endpoint
(https://api.groq.com/openai/v1/chat/completions), model
`llama-3.3-70b-versatile` (Groq's real, currently-hosted Llama 3.3 70B
model per groq.com/docs/models) -- named as the intended provider
explicitly, not NVIDIA (keyword_extraction.py's existing NVIDIA_API_KEY
path is untouched, separate concern: per-beat visual-keyword extraction,
not script generation). Implemented via plain `requests`, same choice
keyword_extraction.py already made (single documented JSON POST, no SDK
needed). Uses Groq's real `response_format: {"type": "json_object"}` JSON
mode (documented, supported on this model) so the response is guaranteed
parseable JSON, not markdown-fenced prose -- still defensively stripped in
`_parse_response()` in case that ever changes.

## Content direction -- the actual point of this module, not just wiring

The prior static scripts were generic explainers (define a concept -> list
2-3 supporting facts -> generic lesson). The system prompt below instead
demands a SPECIFIC, NAMED real person or event with a real narrative arc
(cold open on a striking fact/moment -> who they are -> the personal
stakes/struggle -> the turning point -> the obstacle -> the pivot -> the
outcome), matching a Chipper Cash/TNG-style reference structure. Every
factual/named-person claim must be real and independently verifiable --
if the model can't find a real specific case for a channel's topic, the
prompt instructs it to pick a different, better-suited real topic rather
than invent one.

**Honesty flag, stated plainly per this project's established pattern**:
this module gives the LLM NO live web-search or retrieval tool -- Groq's
API here is a pure text-completion call, nothing more. "Real and
verifiable" claims are only as good as the model's own training-data
recall; there is no independent fact-checking step wired in. Every
generated script's `source_note` says this explicitly, the same way
pipeline/channel_scripts.py's hand-authored scripts flagged "general
knowledge, not a fetched/cited source document" rather than pretending a
citation trail exists. A human review pass before publishing is still
required -- this module makes generation real and non-repeating, not
fact-checked.

## Duration target -- a real, now-resolved conflict with shot_brief.py

This module targets ~35s total runtime (~75-105 words -- relaxed down
from an original 85-word floor after 4 live Groq iterations converged on
81 words without fully clearing it; see `_TARGET_TOTAL_WORDS`'s own
comment) at the real measured 160-175 WPM TTS rate, instead of the prior
static scripts' ~150-180 words (~55-70s). This originally conflicted with
shot_brief.py's `TOTAL_LENGTH_RANGE_SECONDS = (60.0, 90.0)` hard
validation range (03_SCRIPT_BIBLE.md §5) -- flagged here, not silently
patched, in the pass that first added this module. That range has since
been deliberately widened (see shot_brief.py's own comment on
`TOTAL_LENGTH_RANGE_SECONDS` for the real measured data points from both
this module and CH6's real-TTS rollout that drove the new bounds) once a
generated script was actually proven end-to-end through rendering
(pipeline/render_ch1_from_groq.py).

## What this module does NOT do

- Does not modify pipeline/channel_scripts.py or pipeline/ch6_short_001.py
  -- the static scripts stay in place as the current production path for
  the regular per-channel schedule. A generated script is proven
  end-to-end via a SEPARATE module (pipeline/render_ch1_from_groq.py,
  a separate short_id/composition) rather than by replacing CH1's static
  script outright -- that's a deliberate, still-open next step, not done
  here.
"""

from __future__ import annotations

import json
import os
import re
import sys

import requests

from .footage_sourcing.errors import NotConfiguredError
from .footage_sourcing.types import ChannelId, Domain
from .shot_brief import BeatType

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Real measured TTS rate range, per pipeline/tts/espeak_engine.py's
# calibration pass (CLAUDE.md's "Speech/caption pacing calibration"
# section) -- used only to report an estimated duration here, not to
# drive actual synthesis (that still happens in espeak_engine.py itself).
MEASURED_WPM_LOW = 160
MEASURED_WPM_HIGH = 175

_TARGET_TOTAL_WORDS = (75, 105)  # ~35s at 160-175 WPM
# Real evidence from 4 live prompt-tuning iterations (2026-07-03 session):
# the model converged monotonically (16 -> 69 -> 78 -> 81 words for CH1,
# CH5 passed at 90) but kept undershooting the original 85 floor even with
# explicit self-check instructions -- a real LLM instruction-following
# ceiling for this model/prompt pair, not a code bug. Per explicit
# instruction: stop re-prompting, relax the floor in code instead (85->75)
# and let a bounded regenerate-once policy (see generate_channel_script)
# absorb the rest, rather than blocking the pipeline on prompt precision.
_PROMPT_WORDS_PER_BEAT = (6, 12)  # wording target quoted in the system prompt, unchanged this pass
_TARGET_WORDS_PER_BEAT_MAX = 12  # validator's real enforced bound -- upper only, see _validate_beats
_REQUIRED_CASCADE_COUNT = 2  # matches shot_brief.py's REQUIRED_CASCADE_COUNT
_MAX_GENERATION_ATTEMPTS = 2  # word-count-only failures get one regenerate, then we accept

_VALID_DOMAINS = {d.value for d in Domain}
_VALID_BEAT_TYPES = {bt.value for bt in BeatType}
_NAMED_ENTITY_REQUIRED_DOMAINS = {
    Domain.SPACE.value,
    Domain.HISTORICAL_FIGURE.value,
    Domain.HISTORICAL_PLACE.value,
}

# Per-channel real topic direction + the domain this channel's footage
# sourcing is configured for (pipeline/footage_sourcing/config.py's
# CHANNEL_SOURCES -- CH1/CH2/CH4 route to pexels/pixabay, CH3/CH5 to
# wikimedia/loc, CH6 to nasa; domain here is what confidence.py's per-
# domain verification and shot_brief.py's named_entity requirement act
# on, not what selects the client). scriptTone strings reused verbatim
# from src/pipeline/channelConfigs.ts (grep-before-create -- this is the
# one place channel tone is already defined, not re-invented here).
_CHANNEL_BRIEFS: dict[ChannelId, dict[str, str]] = {
    ChannelId.CH1: {
        "name": "Dopamine Loop",
        "tone": "punchy, direct, mind-bending",
        "topic_direction": (
            "Psychology of attention/reward (dopamine loops, variable-ratio "
            "reward, habit formation, notification-checking behavior). Find "
            "a SPECIFIC real documented case, published study's real subject/"
            "finding, or a real, named individual's experience with this "
            "mechanism -- not a generic 'here's how dopamine loops work' "
            "explainer."
        ),
        "default_domain": Domain.ABSTRACT.value,
    },
    ChannelId.CH2: {
        "name": "FinanceFiction",
        "tone": "analytical, shocking, authoritative",
        "topic_direction": (
            "A SPECIFIC named real person's financial story -- a real "
            "lottery winner, a real bankruptcy case, a real sudden-wealth-"
            "and-loss story -- not generic statistics about 'winners' in "
            "general."
        ),
        "default_domain": Domain.ABSTRACT.value,
    },
    ChannelId.CH3: {
        "name": "Redacted",
        "tone": "conspiratorial, terse, urgent",
        "topic_direction": (
            "A declassified/cover-up program (e.g. Project MKUltra or a "
            "comparably real, declassified case) -- push toward a SPECIFIC "
            "real individual affected by or involved in it, not just "
            "program timeline facts."
        ),
        "default_domain": Domain.HISTORICAL_FIGURE.value,
    },
    ChannelId.CH4: {
        "name": "The Grey Matter",
        "tone": "scientific, vivid, revelatory",
        "topic_direction": (
            "Neuroscience of fear/stress/memory (amygdala, fear-memory "
            "consolidation, threat response). Find a SPECIFIC real "
            "documented account of an individual's fear/stress response -- "
            "not general amygdala mechanics."
        ),
        "default_domain": Domain.ABSTRACT.value,
    },
    ChannelId.CH5: {
        "name": "The Quiet Record",
        "tone": "measured, evocative, archival",
        "topic_direction": (
            "An overlooked/forgotten piece of real history (e.g. the WASP "
            "WWII program or a comparably real, under-recognized case) -- "
            "center a SPECIFIC named individual's story, not just program "
            "facts."
        ),
        "default_domain": Domain.HISTORICAL_FIGURE.value,
    },
    ChannelId.CH6: {
        "name": "Red Space Facts",
        "tone": "awe-inspiring, precise, cosmic",
        "topic_direction": (
            "A SPECIFIC real astronomical event, observation, or discovery "
            "moment (e.g. when/how a real phenomenon was first documented, "
            "and by whom) -- not a general facts list about a planet/object."
        ),
        "default_domain": Domain.SPACE.value,
    },
}


def _system_prompt(channel: ChannelId) -> str:
    brief = _CHANNEL_BRIEFS[channel]
    lo_total, hi_total = _TARGET_TOTAL_WORDS
    lo_w, hi_w = _PROMPT_WORDS_PER_BEAT
    return (
        f"You write short-form video scripts for a channel called "
        f"\"{brief['name']}\" (tone: {brief['tone']}). Topic direction: "
        f"{brief['topic_direction']}\n\n"
        "STRUCTURE (a real narrative arc, not a generic explainer): cold "
        "open on a striking fact or moment -> who the specific real person/"
        "case is -> their personal stakes or struggle -> the turning point "
        "-> the obstacle -> the pivot -> the outcome. Every named person, "
        "place, date, or event must be REAL and independently verifiable. "
        "If you cannot recall a specific real case that fits this channel's "
        "topic direction, pick a DIFFERENT real, well-suited topic instead "
        "of inventing a person or event.\n\n"
        "BEAT COUNT (hard requirement, do not produce fewer): exactly 12 "
        "beats, in exactly this order of beat_type (cascade beats shown "
        "in [brackets], everything else is non-cascade): "
        "hook, context, context, build, [cascade], escalation, escalation, "
        "[cascade], resolution, resolution, resolution, closer. That is 10 "
        "non-cascade beats and 2 cascade beats (positions 5 and 8). Do NOT "
        "compress the arc into fewer, terser beats -- each arc step above "
        "is its OWN beat with its own full sentence.\n\n"
        f"LENGTH (hard requirement): each of the 10 non-cascade beats' "
        f"`text` must be {lo_w}-{hi_w} words -- target exactly 9-11 words "
        "each. NEVER write fewer than 9 words for a non-cascade beat -- a "
        "beat at 6, 7, or 8 words is TOO SHORT and WILL be rejected. If a "
        "sentence feels short, add a real concrete detail (a date, a "
        "place, a name, a specific consequence) until it reaches at least "
        "9 words. Each of the 2 cascade beats' `text` must be a punchy "
        "2-4 word ALL-CAPS phrase (e.g. \"MILLIONS GONE\"). BEFORE YOU "
        "ANSWER: add up the word count of all 12 beats you are about to "
        f"output. If that sum is below {lo_total}, go back and lengthen "
        "your shortest non-cascade beats (not the cascade beats) until "
        f"the sum is at least {lo_total} -- do not submit a draft you "
        "haven't already counted. 10 beats at 9-11 words plus 2 cascade "
        "phrases at ~3 words each lands around 96-116 words, comfortably "
        f"in the {lo_total}-{hi_total} range. The 2 cascade beats have no "
        "domain/keyword/named_entity (set them to null).\n\n"
        "WORKED EXAMPLE of the correct shape (a DIFFERENT, unrelated topic "
        "-- do not reuse this content, only copy this exact structure/"
        "length pattern): \"A commercial jet lost all four engines at "
        "35,000 feet\" (hook, 9 words) / \"Captain Eric Moody was flying "
        "British Airways Flight 9 in 1982\" (context, 10 words) / \"Volcanic "
        "ash from Mount Galunggung had silently clogged every engine\" "
        "(context, 9 words) / \"The plane began a silent, powerless glide "
        "toward the Indian Ocean\" (build, 9 words) / \"ALL ENGINES DEAD\" "
        "(cascade, 3 words) / \"Moody radioed a calm, now-famous distress "
        "message to air traffic control\" (escalation, 9 words) / \"With "
        "minutes of altitude left, the crew tried one final restart\" "
        "(escalation, 9 words) / \"ENGINES BACK\" (cascade, 2 words) / "
        "\"One by one, all four engines roared back to life\" (resolution, "
        "10 words) / \"The plane landed safely at Jakarta with everyone "
        "alive\" (resolution, 9 words) / \"Investigators traced the failure "
        "to an invisible volcanic ash cloud\" (resolution, 9 words) / "
        "\"Flight 9 changed how airlines track volcanic ash forever\" "
        "(closer, 8 words). Match this density and beat count, not this "
        "content.\n\n"
        "Each non-cascade beat needs beat_type (one of: hook, context, "
        "build, escalation, resolution, closer -- hook must be first, "
        "closer must be last), a `domain` (one of: earthly-place, person, "
        "object, space, historical-figure, historical-place, abstract), "
        "and a `keyword`: a short visual-search phrase describing a "
        "GENERIC, REAL, PHOTOGRAPHABLE scene or object that represents the "
        "beat (e.g. \"teenager alone in bedroom at night\", \"empty wallet "
        "on table\", \"1940s military airfield\") -- even when the "
        "narration names a real specific person, the keyword must NOT be "
        "that person's name (stock photo libraries will not have their "
        "literal photo); it must describe a generic real scene instead. "
        "NEVER use the words illustration, diagram, icon, vector, cartoon, "
        "drawing, sketch, clipart, or render in a keyword -- this channel's "
        "footage source only accepts real photographs, and a keyword "
        "containing any of those words will return the wrong kind of "
        "image.\n\n"
        "If a beat's domain is historical-figure, historical-place, or "
        "space, it MUST also include `named_entity`: the real proper name "
        "(person, program, or astronomical object) so it can be verified "
        "against real archival/NASA sources -- omit named_entity (null) "
        "for every other domain. This applies to EVERY beat with that "
        "domain, not just the first one that mentions the name -- if beat "
        "2 is historical-figure with named_entity \"Irena Sendler\", and "
        "beat 9 is also historical-figure about the same person, beat 9 "
        "must ALSO repeat named_entity \"Irena Sendler\", not null. Do not "
        "drop it on later beats just because you already stated the name "
        "once.\n\n"
        f"Default domain for this channel's non-historical/non-space "
        f"beats, unless a beat clearly calls for `person` or another more "
        f"specific domain: {brief['default_domain']}.\n\n"
        'Respond ONLY with JSON, no prose, no markdown fences: '
        '{"topic_summary": str, "source_confidence_note": str (state '
        "plainly whether you are confident this is a real, verifiable case "
        "or are less certain), "
        '"beats": [{"beat_id": str, "beat_type": str|null, "text": str, '
        '"cascade": bool, "domain": str|null, "keyword": str|null, '
        '"named_entity": str|null}]}'
    )


def _parse_response(raw_content: str) -> dict:
    """Same defensive parsing as keyword_extraction.py's _parse_response --
    real LLM output isn't guaranteed to skip markdown fences even in JSON
    mode; strip them if present, then parse. Fails loud on malformed
    output, no silent fallback."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())
    return json.loads(cleaned)


class ScriptGenerationError(Exception):
    """Raised when the LLM's output doesn't satisfy this module's real
    structural/content constraints (word count, cascade count, domain/
    named_entity requirements, etc). Fail loud -- callers must not
    silently accept an out-of-spec script."""


def _validate_beats(channel: ChannelId, beats: list[dict]) -> list[str]:
    errors: list[str] = []
    total_words = 0
    cascade_count = 0

    for beat in beats:
        # `beat.get("text", "")`'s default only applies when the key is
        # MISSING, not when it's present with value None -- real bug hit
        # in CI (2026-07-03): the LLM returned "text": null for a beat,
        # and `None.split()` crashed with AttributeError instead of
        # raising the intended ScriptGenerationError. `or ""` catches both.
        text = beat.get("text") or ""
        word_count = len(text.split())
        total_words += word_count
        cascade = bool(beat.get("cascade"))

        if cascade:
            cascade_count += 1
            continue

        # Real evidence (4 live iterations): the model reliably writes
        # 6-10 word beats but occasionally drops to 5-6 -- per explicit
        # instruction, a single short beat is accepted as-is (it matches
        # the existing hand-authored channel_scripts.py content style,
        # which also has some short beats); only an over-long beat (a
        # real risk for a ~4s shot) is still rejected.
        if word_count > _TARGET_WORDS_PER_BEAT_MAX:
            errors.append(
                f"beat '{beat.get('beat_id')}': {word_count} words, exceeds "
                f"the {_TARGET_WORDS_PER_BEAT_MAX}-word max ('{text}')"
            )

        beat_type = beat.get("beat_type")
        if beat_type not in _VALID_BEAT_TYPES:
            errors.append(f"beat '{beat.get('beat_id')}': invalid beat_type {beat_type!r}")

        domain = beat.get("domain")
        if domain not in _VALID_DOMAINS:
            errors.append(f"beat '{beat.get('beat_id')}': invalid domain {domain!r}")
        elif domain in _NAMED_ENTITY_REQUIRED_DOMAINS and not beat.get("named_entity"):
            errors.append(
                f"beat '{beat.get('beat_id')}': domain '{domain}' requires "
                "named_entity, got none"
            )

        keyword = (beat.get("keyword") or "").lower()
        for banned in ("illustration", "diagram", "icon", "vector", "cartoon", "drawing", "sketch", "clipart", "render"):
            if banned in keyword:
                errors.append(
                    f"beat '{beat.get('beat_id')}': keyword {keyword!r} contains "
                    f"banned non-photographic term '{banned}'"
                )

    if cascade_count != _REQUIRED_CASCADE_COUNT:
        errors.append(
            f"expected exactly {_REQUIRED_CASCADE_COUNT} cascade beats, found {cascade_count}"
        )

    lo_total, hi_total = _TARGET_TOTAL_WORDS
    if not (lo_total <= total_words <= hi_total):
        errors.append(
            f"total word count {total_words} outside the {lo_total}-{hi_total} target range"
        )

    return errors


_TOTAL_WORD_COUNT_ERROR_PREFIX = "total word count"


def _call_groq_once(channel: ChannelId, api_key: str) -> tuple[dict, list[dict], str]:
    """One real network call + parse. Returns (parsed, beats, raw_content).
    Raises ScriptGenerationError if there's no usable beats list -- that's
    a hard failure regardless of retry policy (malformed JSON structure,
    not a word-count nuance)."""
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _system_prompt(channel)},
            {"role": "user", "content": f"Generate one script for {_CHANNEL_BRIEFS[channel]['name']}."},
        ],
        "temperature": 0.5,
        "max_tokens": 1800,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(
        GROQ_CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    raw_content = resp.json()["choices"][0]["message"]["content"]
    parsed = _parse_response(raw_content)

    beats = parsed.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ScriptGenerationError(f"LLM response had no usable 'beats' list: {raw_content!r}")

    return parsed, beats, raw_content


def generate_channel_script(channel: ChannelId) -> dict:
    """Calls Groq for real to generate one channel's script for real.

    Returns the parsed response dict (topic_summary, source_confidence_note,
    beats) plus a computed word_count/estimated_duration_s for reporting --
    does NOT build a BeatSpec/ShotBrief here (that's the next, separate
    integration step per explicit instruction this pass stops at generation
    + reporting).

    Retry policy (code-side, not prompt-side -- see _TARGET_TOTAL_WORDS'
    comment for the real evidence this responds to): if validation fails
    with ONLY the total-word-count check out of range, this regenerates
    once (_MAX_GENERATION_ATTEMPTS=2 total attempts) and then ACCEPTS
    whichever result the final attempt produced, logging plainly to
    stderr rather than blocking the pipeline -- word count alone is a
    soft target, not a hard gate, per explicit instruction. Any OTHER
    validation failure (wrong cascade count, invalid domain, missing
    named_entity, a banned non-photographic keyword term, an over-long
    beat) is still a hard failure with no retry -- those are real
    structural/correctness bugs this session's prior iterations already
    got the model to satisfy reliably, and are not the target of this
    leniency.

    Raises NotConfiguredError if GROQ_API_KEY isn't set, and
    ScriptGenerationError if the final attempt still has a non-word-count
    validation failure -- no silent fallback to a generic/invented script.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise NotConfiguredError(
            "GROQ_API_KEY is not set. This step cannot run without it -- per "
            "the fail-loud rule, callers must not fabricate a script."
        )

    beats: list[dict] = []
    parsed: dict = {}
    raw_content = ""
    errors: list[str] = []

    for attempt in range(1, _MAX_GENERATION_ATTEMPTS + 1):
        parsed, beats, raw_content = _call_groq_once(channel, api_key)
        errors = _validate_beats(channel, beats)
        if not errors:
            break

        hard_errors = [e for e in errors if not e.startswith(_TOTAL_WORD_COUNT_ERROR_PREFIX)]
        if hard_errors:
            raise ScriptGenerationError(
                f"generated script for {channel.value} failed validation ({len(errors)} issue(s)):\n"
                + "\n".join(f"  - {e}" for e in errors)
                + f"\n\nFull raw response: {raw_content}"
            )

        # Only a soft (total-word-count) failure -- regenerate if attempts remain.
        if attempt < _MAX_GENERATION_ATTEMPTS:
            print(
                f"[script_generation] {channel.value} attempt {attempt}: "
                f"{errors[0]} -- regenerating (attempt {attempt + 1}/{_MAX_GENERATION_ATTEMPTS})",
                file=sys.stderr,
            )
        else:
            print(
                f"[script_generation] {channel.value}: {errors[0]} after "
                f"{_MAX_GENERATION_ATTEMPTS} attempts -- accepting as-is per "
                "the bounded-retry policy, not blocking the pipeline",
                file=sys.stderr,
            )

    total_words = sum(len((b.get("text") or "").split()) for b in beats)
    est_duration_low = total_words / (MEASURED_WPM_HIGH / 60)
    est_duration_high = total_words / (MEASURED_WPM_LOW / 60)

    lo_total, _ = _TARGET_TOTAL_WORDS
    return {
        "channel": channel.value,
        "topic_summary": parsed.get("topic_summary"),
        "source_confidence_note": parsed.get("source_confidence_note"),
        "beats": beats,
        "total_word_count": total_words,
        "estimated_duration_s_range": (round(est_duration_low, 1), round(est_duration_high, 1)),
        "accepted_below_target_floor": total_words < lo_total,
    }
