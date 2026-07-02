"""Combines all three of this pass's real fixes on the SAME cascade-1 CH6
beat used by Gate-Cascade1-RealTTS / Gate-Cascade1-FullChain, so the
before/after is directly comparable to those prior renders:

1. Voiceover naturalness: pipeline/tts/voice_profiles.py's CH6 pitch/range
   (espeak's own documented PITCH/RANGE params, never set before this
   pass) + apply_naturalness_processing() (real ffmpeg acompressor chain,
   sourced from nodeblackbox/Kokoro-Voice-Api -- see mix.py docstring).
2. Music: real CH6 track ("Alien Spaceship Atmosphere", CC0-1.0, see
   pipeline/audio/music.py) trimmed to this beat's length, ducked under
   the voice via the SAME duck_music_under_voice() chain already used for
   the placeholder-sine-tone version -- not a separate untested path.
3. Video texture: NOT applied by this script -- FilmGrain.tsx is a React
   component composited at render time by NaturalnessMusicGrainGate.tsx,
   not something this audio-only pipeline script touches.

Run: python3 -m pipeline.render_naturalness_music_grain_demo
"""

from __future__ import annotations

import json
from pathlib import Path

from .audio.mix import apply_loudnorm_two_pass, apply_naturalness_processing, duck_music_under_voice, verify_loudness
from .audio.music import get_channel_music_clip
from .footage_sourcing.types import ChannelId
from .tts.espeak_engine import synthesize, write_wav
from .tts.voice_profiles import VOICE_PROFILES

FPS = 24
PUBLIC_AUDIO = Path("public/audio")
SCRATCH = Path("/tmp/naturalness_music_grain_demo")
CASCADE_TEXT = "A storm that never stops"  # same text as the prior cascade-1 gates


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    profile = VOICE_PROFILES[ChannelId.CH6]

    result = synthesize(CASCADE_TEXT, pitch=profile.pitch, pitch_range=profile.pitch_range)
    raw_voice_path = SCRATCH / "voice_raw.wav"
    write_wav(result, raw_voice_path)

    voice_path = SCRATCH / "voice_naturalness.wav"
    apply_naturalness_processing(raw_voice_path, voice_path)

    word_timings = [
        {"word": wt.word, "startFrame": round(wt.start_ms / 1000 * FPS)} for wt in result.word_timings
    ]
    audio_end_frame = round(result.duration_ms / 1000 * FPS)

    duration_s = max(result.duration_ms / 1000, 0.5) + 0.5
    music_path = SCRATCH / "music_ch6.wav"
    get_channel_music_clip(ChannelId.CH6, duration_s, music_path)

    ducked_path = SCRATCH / "ducked.wav"
    duck_music_under_voice(voice_path, music_path, ducked_path)

    mastered_path = PUBLIC_AUDIO / "ch6_cascade1_naturalness_music_mastered.wav"
    measurement = apply_loudnorm_two_pass(ducked_path, mastered_path)
    verification = verify_loudness(mastered_path)

    out = {
        "text": CASCADE_TEXT,
        "voice_profile": {"pitch": profile.pitch, "pitch_range": profile.pitch_range},
        "wordTimings": word_timings,
        "audioEndFrame": audio_end_frame,
        "audioFile": f"audio/{mastered_path.name}",
        "first_pass_measurement": {
            "input_i": measurement.input_i,
            "input_tp": measurement.input_tp,
            "input_lra": measurement.input_lra,
        },
        "final_verification": verification,
    }

    # Also export a voice-only (no music/ducking) mastered file for the
    # A/B naturalness comparison the user asked for -- same synth + same
    # naturalness compression, just skips the music-bed steps.
    voice_only_mastered = PUBLIC_AUDIO / "ch6_cascade1_naturalness_voiceonly_mastered.wav"
    apply_loudnorm_two_pass(voice_path, voice_only_mastered)
    out["voiceOnlyAudioFile"] = f"audio/{voice_only_mastered.name}"

    data_path = Path("src/remotion/data/ch6-cascade-1-naturalness-music.json")
    data_path.write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
