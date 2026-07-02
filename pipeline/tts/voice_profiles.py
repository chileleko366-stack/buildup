"""Per-channel espeak pitch/pitch-range profiles.

NOT bible-sourced -- none of the 8 bible docs mention TTS prosody. Built
the same way sfx_triggers.py's `_channel_flavor()` was: a simple,
flagged-as-unconfirmed mapping off channelConfigs.ts's existing
`scriptTone` strings (the only per-channel tone/genre data that already
exists), using espeak-ng's own documented 0-100 PITCH/RANGE scale (see
espeak_engine.py module docstring's "Pitch / pitch-range" section for the
sourced enum values and default). Every value below stays inside the
documented 0-100 range; deltas from the 50/50 default are modest (+/-10
max), not extreme.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..footage_sourcing.types import ChannelId


@dataclass(frozen=True)
class VoiceProfile:
    pitch: int
    pitch_range: int


VOICE_PROFILES: dict[ChannelId, VoiceProfile] = {
    # "punchy, direct, mind-bending" -- brighter, more animated
    ChannelId.CH1: VoiceProfile(pitch=54, pitch_range=60),
    # "analytical, shocking, authoritative" -- lower, controlled
    ChannelId.CH2: VoiceProfile(pitch=46, pitch_range=48),
    # "conspiratorial, terse, urgent" -- lower and tighter (less variation)
    ChannelId.CH3: VoiceProfile(pitch=44, pitch_range=45),
    # "scientific, vivid, revelatory" -- near-neutral, slightly wider
    ChannelId.CH4: VoiceProfile(pitch=50, pitch_range=56),
    # "measured, evocative, archival" -- lower, narrow range (narrator calm)
    ChannelId.CH5: VoiceProfile(pitch=45, pitch_range=42),
    # "awe-inspiring, precise, cosmic" -- neutral pitch, wide range (awe)
    ChannelId.CH6: VoiceProfile(pitch=50, pitch_range=62),
}
