"""30 sample script beats (5 per channel) for the Phase 2 gate test.

These are hand-authored TEST FIXTURES, not LLM output -- keyword_extraction.py
is stubbed (no LLM key in this environment), so these beats stand in for what
`_validate_shot_brief()`-produced briefs would eventually contain. Each beat's
`visual_keywords` field is likewise hand-authored (by this build, not an LLM)
to exercise source_router / confidence / cache end-to-end; it must not be
mistaken for real keyword-extraction output.

Beat selection per channel follows 03_SCRIPT_BIBLE.md §3's arc (5 of the
8 named beat types per channel -- hook, build, escalation, resolution,
closer; cascade beats are text-timing moments layered over existing B-roll
rather than beats that need their own sourced asset, so they're not
represented here as separate sourcing requests).
"""

from __future__ import annotations

from dataclasses import dataclass

from .types import ChannelId, Domain, VisualKeyword


@dataclass(frozen=True)
class SampleBeat:
    beat_id: str
    channel: ChannelId
    beat_type: str
    text: str
    visual_keywords: list[VisualKeyword]


def _kw(
    text: str,
    domain: Domain,
    channel: ChannelId,
    beat_id: str,
    named_entity: str | None = None,
    expected_region_hint: str | None = None,
) -> VisualKeyword:
    return VisualKeyword(
        text=text,
        domain=domain,
        channel=channel,
        beat_id=beat_id,
        named_entity=named_entity,
        expected_region_hint=expected_region_hint,
    )


SAMPLE_BEATS: list[SampleBeat] = [
    # --- CH1 Dopamine Loop (psychology) ---
    SampleBeat(
        "CH1-hook", ChannelId.CH1, "hook",
        "You check your phone 96 times a day and you don't even notice.",
        [_kw("person checking phone", Domain.PERSON, ChannelId.CH1, "CH1-hook")],
    ),
    SampleBeat(
        "CH1-build", ChannelId.CH1, "build",
        "Every notification is a tiny gamble your brain didn't agree to.",
        [_kw("smartphone notification screen", Domain.OBJECT, ChannelId.CH1, "CH1-build")],
    ),
    SampleBeat(
        "CH1-escalation", ChannelId.CH1, "escalation",
        "But the app isn't guessing what you want. It already knows.",
        [_kw("person scrolling social media at night", Domain.PERSON, ChannelId.CH1, "CH1-escalation")],
    ),
    SampleBeat(
        "CH1-resolution", ChannelId.CH1, "resolution",
        "Once you see the loop, you can't unsee it.",
        [_kw("person looking at phone with neutral expression", Domain.PERSON, ChannelId.CH1, "CH1-resolution")],
    ),
    SampleBeat(
        "CH1-closer", ChannelId.CH1, "closer",
        "The loop was never about the content. It was about the maybe.",
        [_kw("hand hovering over phone screen", Domain.OBJECT, ChannelId.CH1, "CH1-closer")],
    ),
    # --- CH2 FinanceFiction ---
    SampleBeat(
        "CH2-hook", ChannelId.CH2, "hook",
        "In 2010, a college dropout turned $8,000 into a company worth billions.",
        [_kw("startup founder working late", Domain.PERSON, ChannelId.CH2, "CH2-hook")],
    ),
    SampleBeat(
        "CH2-build", ChannelId.CH2, "build",
        "He mortgaged his apartment to make payroll that first year.",
        [_kw("small apartment office", Domain.OBJECT, ChannelId.CH2, "CH2-build")],
    ),
    SampleBeat(
        "CH2-escalation", ChannelId.CH2, "escalation",
        "Then their biggest client pulled out with no warning.",
        [_kw("empty office desk", Domain.OBJECT, ChannelId.CH2, "CH2-escalation")],
    ),
    SampleBeat(
        "CH2-resolution", ChannelId.CH2, "resolution",
        "Eighteen months later, the company IPO'd at $4.2 billion.",
        [_kw("stock exchange trading floor", Domain.OBJECT, ChannelId.CH2, "CH2-resolution")],
    ),
    SampleBeat(
        "CH2-closer", ChannelId.CH2, "closer",
        "He still keeps the eviction notice framed on his desk.",
        [_kw("framed paper on office desk", Domain.OBJECT, ChannelId.CH2, "CH2-closer")],
    ),
    # --- CH3 Redacted (declassified history) ---
    SampleBeat(
        "CH3-hook", ChannelId.CH3, "hook",
        "For 40 years, the CIA denied this program ever existed.",
        [_kw("classified document stamped secret", Domain.HISTORICAL_PLACE, ChannelId.CH3, "CH3-hook",
             named_entity="Central Intelligence Agency")],
    ),
    SampleBeat(
        "CH3-build", ChannelId.CH3, "build",
        "It started in 1954, in a nondescript building outside Washington.",
        [_kw("Cold War era government building", Domain.HISTORICAL_PLACE, ChannelId.CH3, "CH3-build",
             named_entity="Washington")],
    ),
    SampleBeat(
        "CH3-escalation", ChannelId.CH3, "escalation",
        "Then a single leaked memo threatened to expose everything.",
        [_kw("leaked government memo document", Domain.HISTORICAL_FIGURE, ChannelId.CH3, "CH3-escalation",
             named_entity="Project MKUltra")],
    ),
    SampleBeat(
        "CH3-resolution", ChannelId.CH3, "resolution",
        "In 1977, a Senate hearing finally confirmed what reporters suspected.",
        [_kw("Senate hearing room 1977", Domain.HISTORICAL_PLACE, ChannelId.CH3, "CH3-resolution",
             named_entity="United States Senate")],
    ),
    SampleBeat(
        "CH3-closer", ChannelId.CH3, "closer",
        "Most of the records were destroyed before anyone could read them.",
        [_kw("burned paper documents", Domain.OBJECT, ChannelId.CH3, "CH3-closer")],
    ),
    # --- CH4 The Grey Matter (neuroscience) ---
    SampleBeat(
        "CH4-hook", ChannelId.CH4, "hook",
        "The second before you feel afraid, your brain has already decided.",
        [_kw("MRI brain scan image", Domain.OBJECT, ChannelId.CH4, "CH4-hook")],
    ),
    SampleBeat(
        "CH4-build", ChannelId.CH4, "build",
        "You'd assume the fear starts in your mind. It doesn't.",
        [_kw("person startled reaction", Domain.PERSON, ChannelId.CH4, "CH4-build")],
    ),
    SampleBeat(
        "CH4-escalation", ChannelId.CH4, "escalation",
        "It starts in a walnut-sized structure that hijacks your whole body first.",
        [_kw("neuroscience lab equipment", Domain.OBJECT, ChannelId.CH4, "CH4-escalation")],
    ),
    SampleBeat(
        "CH4-resolution", ChannelId.CH4, "resolution",
        "By the time you consciously register fear, 200 milliseconds are already gone.",
        [_kw("clinical lab researcher at desk", Domain.PERSON, ChannelId.CH4, "CH4-resolution")],
    ),
    SampleBeat(
        "CH4-closer", ChannelId.CH4, "closer",
        "Your mind isn't lying to you. It's just always a little late.",
        [_kw("person calm expression close up", Domain.PERSON, ChannelId.CH4, "CH4-closer")],
    ),
    # --- CH5 The Quiet Record (history) ---
    SampleBeat(
        "CH5-hook", ChannelId.CH5, "hook",
        "She flew combat missions the U.S. Army swore no woman ever had.",
        [_kw("WWII female pilot portrait", Domain.HISTORICAL_FIGURE, ChannelId.CH5, "CH5-hook",
             named_entity="Women Airforce Service Pilots")],
    ),
    SampleBeat(
        "CH5-build", ChannelId.CH5, "build",
        "In 1943, over a thousand women trained in secret at a Texas airbase.",
        [_kw("1943 Texas military airbase", Domain.HISTORICAL_PLACE, ChannelId.CH5, "CH5-build",
             named_entity="Avenger Field", expected_region_hint="Texas")],
    ),
    SampleBeat(
        "CH5-escalation", ChannelId.CH5, "escalation",
        "Thirty-eight of them died in service the military refused to acknowledge.",
        [_kw("WWII aircraft wreckage historical photo", Domain.HISTORICAL_PLACE, ChannelId.CH5, "CH5-escalation")],
    ),
    SampleBeat(
        "CH5-resolution", ChannelId.CH5, "resolution",
        "It took until 1977 for Congress to grant them military status.",
        [_kw("US Congress 1977 session", Domain.HISTORICAL_PLACE, ChannelId.CH5, "CH5-resolution",
             named_entity="United States Congress")],
    ),
    SampleBeat(
        "CH5-closer", ChannelId.CH5, "closer",
        "Fewer than 20 of them are still alive to tell it themselves.",
        [_kw("elderly veteran portrait historical", Domain.HISTORICAL_FIGURE, ChannelId.CH5, "CH5-closer",
             named_entity="Women Airforce Service Pilots")],
    ),
    # --- CH6 Red Space Facts ---
    SampleBeat(
        "CH6-hook", ChannelId.CH6, "hook",
        "This dot in the night sky is actually eating its own moons.",
        [_kw("Jupiter planet", Domain.SPACE, ChannelId.CH6, "CH6-hook", named_entity="Jupiter")],
    ),
    SampleBeat(
        "CH6-build", ChannelId.CH6, "build",
        "From Earth it looks like a steady point of light.",
        [_kw("night sky planet viewing", Domain.SPACE, ChannelId.CH6, "CH6-build", named_entity="Jupiter")],
    ),
    SampleBeat(
        "CH6-escalation", ChannelId.CH6, "escalation",
        "Up close, its storms are wider than three Earths side by side.",
        [_kw("Great Red Spot Jupiter storm", Domain.SPACE, ChannelId.CH6, "CH6-escalation",
             named_entity="Great Red Spot")],
    ),
    SampleBeat(
        "CH6-resolution", ChannelId.CH6, "resolution",
        "That storm has been raging continuously for over 350 years.",
        [_kw("Jupiter Great Red Spot closeup", Domain.SPACE, ChannelId.CH6, "CH6-resolution",
             named_entity="Great Red Spot")],
    ),
    SampleBeat(
        "CH6-closer", ChannelId.CH6, "closer",
        "It could swallow every planet in the inner solar system at once.",
        [_kw("Jupiter scale comparison Earth", Domain.SPACE, ChannelId.CH6, "CH6-closer", named_entity="Jupiter")],
    ),
]
