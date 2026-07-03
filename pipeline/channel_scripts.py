"""Phase 4: hand-authored scripts for CH1-CH5, filling the gap flagged in
CLAUDE.md ("only CH6 has been wired end-to-end"). Same rules as
ch6_short_001.py:

- HAND-AUTHORED, NOT LLM OUTPUT (no LLM provider key configured -- see
  keyword_extraction.py). Stands in for what a real script-generation step
  would eventually produce.
- Every factual claim is general, well-established knowledge (attention/
  reward psychology, lottery-winner statistics, MKUltra as a declassified
  historical program, fear/amygdala neuroscience, the WASP program) --
  `source_snippet` on each entry says so honestly rather than claiming a
  fetched/cited source document that doesn't exist.
- Deliberately kept to short (roughly 6-12 word) sentences: real TTS at
  this repo's calibrated 160 WPM rate runs measurably slower than
  05_PACING_MOVEMENT_BIBLE.md §2's fixed placeholder ranges assume for
  longer sentences (see shot_brief.py's `_validate_shot_brief()` real-
  timing exemption, and CLAUDE.md's Phase 4 section for the measured
  numbers) -- short sentences keep most beats close to the pacing bible's
  original intent even though the hard range check no longer applies to
  real-timed beats.
- Keyword choices were checked against pipeline/audio/sfx_triggers.py's
  real, already-verified per-channel keyword sets (not invented fresh) so
  each channel's real SFX categories actually fire on this content, same
  diligence as the sample_beats.py / ch6_short_001.py content did.

Domains follow pipeline/footage_sourcing/config.py's real CHANNEL_SOURCES
routing table: CH1/CH2/CH4 route to pexels/pixabay (general stock) --
ABSTRACT domain; CH3/CH5 route to wikimedia/loc (historical) --
HISTORICAL_FIGURE, which requires a `named_entity` per
04_ASSET_ACCURACY_BIBLE.md §4 (enforced by _validate_shot_brief()).
"""

from __future__ import annotations

from dataclasses import dataclass

from .footage_sourcing.types import ChannelId, Domain
from .shot_brief import BeatType


@dataclass(frozen=True)
class BeatSpec:
    beat_id: str
    beat_type: BeatType
    text: str
    domain: Domain | None  # None for cascade beats (no visual_keywords, matches ch6_short_001.py)
    keyword: str | None
    named_entity: str | None
    cascade: bool = False


CH1_SOURCE_NOTE = (
    "General attention/reward psychology (variable-ratio reward schedules, "
    "notification-driven checking behavior) -- not a fetched/cited source "
    "document; no LLM+source-material step ran."
)

CH1_BEATS: list[BeatSpec] = [
    BeatSpec("hook", BeatType.HOOK, "Why does checking your phone feel so hard to resist?",
             Domain.ABSTRACT, "person checking phone anxiously", None),
    BeatSpec("context-1", BeatType.CONTEXT, "It's not weak willpower. It's a dopamine loop your brain built on purpose.",
             Domain.ABSTRACT, "brain reward pathway illustration", None),
    BeatSpec("context-2", BeatType.CONTEXT, "Every notification is a tiny, unpredictable reward.",
             Domain.ABSTRACT, "phone notification screen", None),
    BeatSpec("context-3", BeatType.CONTEXT, "You never know in advance if it will be worth checking.",
             Domain.ABSTRACT, "person glancing at phone screen", None),
    BeatSpec("build-1", BeatType.BUILD, "Researchers call this a variable reward schedule.",
             Domain.ABSTRACT, "researcher studying behavior", None),
    BeatSpec("build-2", BeatType.BUILD, "The same system that keeps a gambler pulling a slot machine lever.",
             Domain.ABSTRACT, "slot machine lever", None),
    BeatSpec("build-3", BeatType.BUILD, "One study found people check their phones over eighty times a day.",
             Domain.ABSTRACT, "person using smartphone repeatedly", None),
    BeatSpec("cascade-1", BeatType.ESCALATION, "PURE HABIT", None, None, None, cascade=True),
    BeatSpec("escalation-1", BeatType.ESCALATION, "But the craving doesn't come from wanting the phone.",
             Domain.ABSTRACT, "hand reaching for phone", None),
    BeatSpec("escalation-2", BeatType.ESCALATION, "It comes from the urge to end the uncertainty.",
             Domain.ABSTRACT, "person anxiously waiting", None),
    BeatSpec("cascade-2", BeatType.RESOLUTION, "NEVER SATISFIED", None, None, None, cascade=True),
    BeatSpec("resolution-1", BeatType.RESOLUTION, "Suddenly the loop resets the moment you unlock your screen.",
             Domain.ABSTRACT, "phone lock screen unlocking", None),
    BeatSpec("resolution-2", BeatType.RESOLUTION, "Your brain doesn't crave the content. It craves the checking itself.",
             Domain.ABSTRACT, "brain scan illustration", None),
    BeatSpec("resolution-3", BeatType.RESOLUTION, "That's why the habit is so hard to break.",
             Domain.ABSTRACT, "person trying to put phone down", None),
    BeatSpec("resolution-4", BeatType.RESOLUTION, "Understanding the loop doesn't switch it off by itself.",
             Domain.ABSTRACT, "person reflecting thoughtfully", None),
    BeatSpec("closer-1", BeatType.CLOSER, "A single notification isn't the problem. The loop underneath it is.",
             Domain.ABSTRACT, "phone with notification badge", None),
    BeatSpec("closer-2", BeatType.CLOSER, "So the next time you feel that urge, you'll know it's the loop, not you.",
             Domain.ABSTRACT, "person setting phone aside", None),
]

CH2_SOURCE_NOTE = (
    "General personal-finance knowledge (commonly cited lottery-winner "
    "bankruptcy statistics, sudden-wealth psychology) -- not a fetched/"
    "cited source document; no LLM+source-material step ran."
)

CH2_BEATS: list[BeatSpec] = [
    BeatSpec("hook", BeatType.HOOK, "How do lottery winners lose millions so fast?",
             Domain.ABSTRACT, "lottery ticket and cash", None),
    BeatSpec("context-1", BeatType.CONTEXT, "About seventy percent of winners go broke within a few years.",
             Domain.ABSTRACT, "empty wallet", None),
    BeatSpec("context-2", BeatType.CONTEXT, "A sudden fortune doesn't fix money habits. It just makes them bigger.",
             Domain.ABSTRACT, "stack of cash", None),
    BeatSpec("context-3", BeatType.CONTEXT, "The prize money usually arrives faster than any plan for it.",
             Domain.ABSTRACT, "oversized novelty check", None),
    BeatSpec("build-1", BeatType.BUILD, "Most winners have never managed anything close to that kind of money.",
             Domain.ABSTRACT, "person reviewing bank statement", None),
    BeatSpec("build-2", BeatType.BUILD, "The average winner spends far more than they ever planned to.",
             Domain.ABSTRACT, "luxury car purchase", None),
    BeatSpec("build-3", BeatType.BUILD, "Friends and family start asking for loans almost immediately.",
             Domain.ABSTRACT, "family gathering tension", None),
    BeatSpec("cascade-1", BeatType.ESCALATION, "MILLIONS GONE", None, None, None, cascade=True),
    BeatSpec("escalation-1", BeatType.ESCALATION, "But the real cost isn't the spending. It's the isolation.",
             Domain.ABSTRACT, "person alone in large house", None),
    BeatSpec("escalation-2", BeatType.ESCALATION, "Then the lawsuits over a share of the winnings start.",
             Domain.ABSTRACT, "courtroom gavel", None),
    BeatSpec("cascade-2", BeatType.RESOLUTION, "SEVENTY PERCENT BROKE", None, None, None, cascade=True),
    BeatSpec("resolution-1", BeatType.RESOLUTION, "Advisors say the biggest mistake is telling anyone at all.",
             Domain.ABSTRACT, "financial advisor meeting", None),
    BeatSpec("resolution-2", BeatType.RESOLUTION, "The winners who keep their fortune almost always change nothing about their life.",
             Domain.ABSTRACT, "modest home exterior", None),
    BeatSpec("resolution-3", BeatType.RESOLUTION, "They treat the windfall as a number on paper, not spending money.",
             Domain.ABSTRACT, "bank statement closeup", None),
    BeatSpec("resolution-4", BeatType.RESOLUTION, "The habits that built the fortune matter more than the fortune itself.",
             Domain.ABSTRACT, "person budgeting at desk", None),
    BeatSpec("closer-1", BeatType.CLOSER, "The lesson has nothing to do with luck.",
             Domain.ABSTRACT, "four leaf clover", None),
    BeatSpec("closer-2", BeatType.CLOSER, "Money doesn't fix what it doesn't touch.",
             Domain.ABSTRACT, "cash on table", None),
]

CH3_SOURCE_NOTE = (
    "General, widely-documented facts about Project MKUltra (a real, "
    "declassified CIA program) -- not a fetched/cited source document; no "
    "LLM+source-material step ran."
)

CH3_BEATS: list[BeatSpec] = [
    BeatSpec("hook", BeatType.HOOK, "What was really inside Project MKUltra?",
             Domain.HISTORICAL_FIGURE, "CIA headquarters exterior", "MKUltra"),
    BeatSpec("context-1", BeatType.CONTEXT, "In the 1950s, the CIA ran a classified mind-control program.",
             Domain.HISTORICAL_FIGURE, "1950s government building", "MKUltra"),
    BeatSpec("context-2", BeatType.CONTEXT, "Most of the records were destroyed before Congress ever found out.",
             Domain.HISTORICAL_FIGURE, "shredded documents", "MKUltra"),
    BeatSpec("build-1", BeatType.BUILD, "What survived was declassified decades later, and it was disturbing.",
             Domain.HISTORICAL_FIGURE, "declassified document stamp", "MKUltra"),
    BeatSpec("build-2", BeatType.BUILD, "Researchers tested drugs and sensory deprivation on people who never consented.",
             Domain.HISTORICAL_FIGURE, "1950s laboratory", "MKUltra"),
    BeatSpec("build-3", BeatType.BUILD, "The program stayed secret for over twenty years.",
             Domain.HISTORICAL_FIGURE, "locked filing cabinet", "MKUltra"),
    BeatSpec("cascade-1", BeatType.ESCALATION, "NEVER FULLY EXPOSED", None, None, None, cascade=True),
    BeatSpec("escalation-1", BeatType.ESCALATION, "Then, in 1977, a leaked cache of documents finally surfaced.",
             Domain.HISTORICAL_FIGURE, "1970s congressional hearing", "MKUltra"),
    BeatSpec("escalation-2", BeatType.ESCALATION, "The cover-up wasn't just secrecy. It was systematic destruction of evidence.",
             Domain.HISTORICAL_FIGURE, "burning documents", "MKUltra"),
    BeatSpec("cascade-2", BeatType.RESOLUTION, "STILL PARTLY REDACTED", None, None, None, cascade=True),
    BeatSpec("resolution-1", BeatType.RESOLUTION, "Even the declassified files have entire pages blacked out.",
             Domain.HISTORICAL_FIGURE, "redacted document page", "MKUltra"),
    BeatSpec("resolution-2", BeatType.RESOLUTION, "No one was ever prosecuted for what happened.",
             Domain.HISTORICAL_FIGURE, "empty courtroom", "MKUltra"),
    BeatSpec("resolution-3", BeatType.RESOLUTION, "The full scope of the program may still be hidden.",
             Domain.HISTORICAL_FIGURE, "sealed archive boxes", "MKUltra"),
    BeatSpec("closer-1", BeatType.CLOSER, "Some documents remain buried in agency archives to this day.",
             Domain.HISTORICAL_FIGURE, "government archive shelves", "MKUltra"),
    BeatSpec("closer-2", BeatType.CLOSER, "What isn't classified is that it happened. What's missing is why.",
             Domain.HISTORICAL_FIGURE, "CIA seal", "MKUltra"),
]

CH4_SOURCE_NOTE = (
    "General neuroscience knowledge (amygdala threat response, fear-memory "
    "consolidation) -- not a fetched/cited source document; no LLM+"
    "source-material step ran."
)

CH4_BEATS: list[BeatSpec] = [
    BeatSpec("hook", BeatType.HOOK, "What happens in your brain the instant you feel afraid?",
             Domain.ABSTRACT, "brain illustration glowing", None),
    BeatSpec("context-1", BeatType.CONTEXT, "A signal reaches your amygdala before you're even consciously aware of it.",
             Domain.ABSTRACT, "amygdala brain diagram", None),
    BeatSpec("context-2", BeatType.CONTEXT, "Your mind reacts to danger faster than you can think about it.",
             Domain.ABSTRACT, "startled facial expression", None),
    BeatSpec("context-3", BeatType.CONTEXT, "This entire pathway evolved to keep you alive, not to feel comfortable.",
             Domain.ABSTRACT, "brain evolution illustration", None),
    BeatSpec("build-1", BeatType.BUILD, "Neurons fire a threat response in a fraction of a second.",
             Domain.ABSTRACT, "neuron network illustration", None),
    BeatSpec("build-2", BeatType.BUILD, "This happens before the rational part of your cortex gets involved.",
             Domain.ABSTRACT, "prefrontal cortex diagram", None),
    BeatSpec("build-3", BeatType.BUILD, "The signal travels along a synapse thousands of times a second.",
             Domain.ABSTRACT, "synapse closeup illustration", None),
    BeatSpec("cascade-1", BeatType.ESCALATION, "FASTER THAN THOUGHT", None, None, None, cascade=True),
    BeatSpec("escalation-1", BeatType.ESCALATION, "But your brain doesn't just react. It also remembers.",
             Domain.ABSTRACT, "brain memory illustration", None),
    BeatSpec("escalation-2", BeatType.ESCALATION, "Every frightening moment gets tagged for stronger memory storage.",
             Domain.ABSTRACT, "person recalling memory", None),
    BeatSpec("cascade-2", BeatType.RESOLUTION, "WIRED TO REMEMBER", None, None, None, cascade=True),
    BeatSpec("resolution-1", BeatType.RESOLUTION, "That's why you rarely forget the moment something scared you.",
             Domain.ABSTRACT, "person startled memory flash", None),
    BeatSpec("resolution-2", BeatType.RESOLUTION, "Your neural pathways get reinforced every time that fear repeats.",
             Domain.ABSTRACT, "neural pathway illustration", None),
    BeatSpec("resolution-3", BeatType.RESOLUTION, "Even decades later, your mind can recall it instantly.",
             Domain.ABSTRACT, "elderly person remembering", None),
    BeatSpec("resolution-4", BeatType.RESOLUTION, "That's also why certain fears can feel impossible to unlearn.",
             Domain.ABSTRACT, "person facing fear symbolically", None),
    BeatSpec("closer-1", BeatType.CLOSER, "Fear isn't a flaw in your brain. It's a feature that kept you alive.",
             Domain.ABSTRACT, "brain protective illustration", None),
    BeatSpec("closer-2", BeatType.CLOSER, "Your mind was built to never quite forget it.",
             Domain.ABSTRACT, "person deep in thought", None),
]

CH5_SOURCE_NOTE = (
    "General, widely-documented facts about the WASP program (Women "
    "Airforce Service Pilots, WWII) -- not a fetched/cited source "
    "document; no LLM+source-material step ran."
)

CH5_BEATS: list[BeatSpec] = [
    BeatSpec("hook", BeatType.HOOK, "In 1943, over a thousand women became military pilots in secret.",
             Domain.HISTORICAL_FIGURE, "1940s female pilot portrait", "WASP"),
    BeatSpec("context-1", BeatType.CONTEXT, "They were called the WASP -- the Women Airforce Service Pilots.",
             Domain.HISTORICAL_FIGURE, "WASP pilots group photo", "WASP"),
    BeatSpec("context-2", BeatType.CONTEXT, "They ferried aircraft across the country during the Second World War.",
             Domain.HISTORICAL_FIGURE, "WWII era aircraft on runway", "WASP"),
    BeatSpec("context-3", BeatType.CONTEXT, "Every one of them had to pay her own way to training.",
             Domain.HISTORICAL_FIGURE, "1940s flight training school", "WASP"),
    BeatSpec("build-1", BeatType.BUILD, "None of them were allowed to fly in combat.",
             Domain.HISTORICAL_FIGURE, "female pilot in cockpit", "WASP"),
    BeatSpec("build-2", BeatType.BUILD, "Thirty-eight of them died in service to their country.",
             Domain.HISTORICAL_FIGURE, "WWII memorial plaque", "WASP"),
    BeatSpec("build-3", BeatType.BUILD, "But they weren't granted military status, so their deaths went largely unrecognized.",
             Domain.HISTORICAL_FIGURE, "folded flag ceremony", "WASP"),
    BeatSpec("cascade-1", BeatType.ESCALATION, "NO MILITARY HONORS", None, None, None, cascade=True),
    BeatSpec("escalation-1", BeatType.ESCALATION, "Their records were sealed and classified for over thirty years.",
             Domain.HISTORICAL_FIGURE, "sealed archive box 1940s", "WASP"),
    BeatSpec("escalation-2", BeatType.ESCALATION, "Most Americans had simply forgotten they ever existed.",
             Domain.HISTORICAL_FIGURE, "faded newspaper clipping", "WASP"),
    BeatSpec("cascade-2", BeatType.RESOLUTION, "ALMOST VANISHED ENTIRELY", None, None, None, cascade=True),
    BeatSpec("resolution-1", BeatType.RESOLUTION, "In 1977, they were finally recognized as veterans.",
             Domain.HISTORICAL_FIGURE, "1970s veterans ceremony", "WASP"),
    BeatSpec("resolution-2", BeatType.RESOLUTION, "By then, their story was nearly lost to history.",
             Domain.HISTORICAL_FIGURE, "old photograph archive", "WASP"),
    BeatSpec("resolution-3", BeatType.RESOLUTION, "Only a handful of survivors lived to see that recognition.",
             Domain.HISTORICAL_FIGURE, "elderly veteran portrait", "WASP"),
    BeatSpec("closer-1", BeatType.CLOSER, "Their war never came with medals or headlines.",
             Domain.HISTORICAL_FIGURE, "quiet military cemetery", "WASP"),
    BeatSpec("closer-2", BeatType.CLOSER, "But it happened, and it very nearly went unrecorded.",
             Domain.HISTORICAL_FIGURE, "archival photo collection", "WASP"),
]

CHANNEL_SCRIPTS: dict[ChannelId, tuple[list[BeatSpec], str]] = {
    ChannelId.CH1: (CH1_BEATS, CH1_SOURCE_NOTE),
    ChannelId.CH2: (CH2_BEATS, CH2_SOURCE_NOTE),
    ChannelId.CH3: (CH3_BEATS, CH3_SOURCE_NOTE),
    ChannelId.CH4: (CH4_BEATS, CH4_SOURCE_NOTE),
    ChannelId.CH5: (CH5_BEATS, CH5_SOURCE_NOTE),
}

SHORT_IDS: dict[ChannelId, str] = {
    ChannelId.CH1: "ch1-dopamine-loop-notifications-001",
    ChannelId.CH2: "ch2-lottery-winners-broke-001",
    ChannelId.CH3: "ch3-mkultra-001",
    ChannelId.CH4: "ch4-fear-response-001",
    ChannelId.CH5: "ch5-wasp-pilots-001",
}
