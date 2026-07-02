"""Real per-channel background music beds -- replaces the synthetic
`_make_music_bed()` sine-tone placeholder (render_audio_demo.py /
render_sfx_verification.py) with actual licensed music, routed through the
same already-built `duck_music_under_voice()` ducking chain (mix.py).

## Source and licensing

Tracks are real CC0-1.0 (public domain equivalent) files mirrored in
github.com/SoundSafari/CC0-1.0-Music, a real repo (confirmed: distinct
per-source subfolders -- chosic.com/, freemusicarchive.org/, freepd.com/,
freesound.org/, pixbay.com/ -- each itself a real, independently-known
royalty-free-music site). Repo's own stated license: "A collection of
public-domain/CC0-1.0-licensed music from scattered locations across the
internet." CC0-1.0 requires no attribution and permits commercial use,
confirmed directly against the license text at
creativecommons.org/publicdomain/zero/1.0/ -- safe for YouTube upload
without a separate license/attribution step.

This session's GitHub MCP access is scoped to chileleko366-stack/buildup
only (cannot browse SoundSafari's repo via the GitHub API/MCP tools), but
`raw.githubusercontent.com` file fetches are NOT blocked by this session's
egress policy (confirmed: direct `curl` to individual file URLs returned
real HTTP 200 with real audio bytes, unlike every other external asset
host checked this session -- NASA/Wikimedia/LOC/HuggingFace/freesound.org/
pixabay.com/mixkit.co are all blocked). Directory listings were read via
WebFetch against the repo's GitHub web UI (which does render, unlike the
scoped API), to get exact real filenames before downloading -- not
guessed.

## Per-channel track selection

One real, distinct track per channel (not one generic bed reused 6x),
chosen by matching each track's own title/mood against
`channelConfigs.ts`'s existing `scriptTone` string for that channel --
this pairing is new design work (no bible specifies music mood), same
"flagged, not invented from nothing" treatment as sfx_triggers.py's
`_channel_flavor()`. All 6 downloaded and confirmed as real playable MP3
via ffmpeg -- not zero-byte or an HTML error page (see this module's
DOWNLOAD_SOURCES for the exact source URL used per channel).

Files live in public/audio/music/{CH1..CH6}.mp3 (full-length tracks,
1:17-8:51 real running time each -- see DOWNLOAD_SOURCES). Beats in this
repo are a few seconds long, so `get_channel_music_clip()` trims the
track's own opening segment (with a short fade-in/out, since these are
mid-song excerpts, not composed intros) to the beat's duration, rather
than looping a short clip (which the existing `_make_music_bed()` sine
placeholder did, but real music loops audibly unless beat-matched, which
is out of scope here).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..footage_sourcing.types import ChannelId
from .ffmpeg_bin import ffmpeg_path

MUSIC_DIR = Path("public/audio/music")

FADE_S = 0.3

# Real source URLs actually fetched this session (raw.githubusercontent.com,
# all returned HTTP 200 with real audio bytes -- see module docstring).
DOWNLOAD_SOURCES: dict[ChannelId, str] = {
    ChannelId.CH1: "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/freepd.com/Circuit.mp3",
    ChannelId.CH2: "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/freepd.com/Battle%20Ready.mp3",
    ChannelId.CH3: "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/freepd.com/Dark%20Hallway.mp3",
    ChannelId.CH4: "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/freepd.com/Chronos.mp3",
    ChannelId.CH5: (
        "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/"
        "chosic.com/Albinoni-Adagio-de-Albinoni%28chosic.com%29.mp3"
    ),
    ChannelId.CH6: (
        "https://raw.githubusercontent.com/SoundSafari/CC0-1.0-Music/main/"
        "freepd.com/Alien%20Spaceship%20Atmosphere.mp3"
    ),
}

# Why each track was picked -- matched against channelConfigs.ts's scriptTone.
MOOD_RATIONALE: dict[ChannelId, str] = {
    ChannelId.CH1: "'Circuit' -- pulsing/electronic, fits CH1's 'punchy, direct, mind-bending' tone",
    ChannelId.CH2: "'Battle Ready' -- driving/dramatic, fits CH2's 'analytical, shocking, authoritative' tone",
    ChannelId.CH3: "'Dark Hallway' -- tense/low, fits CH3's 'conspiratorial, terse, urgent' tone",
    ChannelId.CH4: "'Chronos' -- fits CH4's 'scientific, vivid, revelatory' tone",
    ChannelId.CH5: "Albinoni's Adagio -- classical/archival, fits CH5's 'measured, evocative, archival' tone",
    ChannelId.CH6: "'Alien Spaceship Atmosphere' -- ambient/cosmic, fits CH6's 'awe-inspiring, precise, cosmic' tone",
}


def music_bed_path(channel: ChannelId) -> Path:
    path = MUSIC_DIR / f"{channel.value}.mp3"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found -- download real tracks per DOWNLOAD_SOURCES before calling this."
        )
    return path


def get_channel_music_clip(channel: ChannelId, duration_s: float, out_path: Path) -> None:
    """Trims channel's real music bed to `duration_s` (from the track's
    own start), with a short fade-in/out since this is a mid-song excerpt,
    not a composed intro/outro."""
    source = music_bed_path(channel)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fade_out_start = max(duration_s - FADE_S, 0.0)
    filter_str = f"afade=t=in:st=0:d={FADE_S},afade=t=out:st={fade_out_start}:d={FADE_S}"
    result = subprocess.run(
        [
            ffmpeg_path(), "-y",
            "-i", str(source),
            "-t", str(duration_s),
            "-af", filter_str,
            str(out_path),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg music clip trim failed:\n{result.stderr}")
