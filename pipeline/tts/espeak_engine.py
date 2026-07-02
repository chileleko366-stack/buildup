"""Real, working, network-independent TTS via the bundled espeak-ng shared
library (ships inside the `espeakng-loader` wheel, a transitive dependency
of `kokoro-onnx` -- no separate download needed, confirmed present on disk
in this session).

THIS IS NOT KOKORO. It's a synthesized-sounding robotic voice, explicitly
used here as a proof that real TTS audio + real per-word timestamps CAN
flow through this pipeline today, while kokoro-onnx itself is blocked (see
kokoro_engine.py). Do not ship this as a channel's actual voice without an
explicit decision to do so -- it's a stand-in, not the intended output.

Uses espeak-ng's C API directly via ctypes (retrieval-mode synthesis +
word-boundary event callback), not a CLI wrapper -- there is no system
`espeak-ng` binary in this environment, only the bundled .so + data files.
Event type constants are from espeak-ng's speak_lib.h `espeak_EVENT_TYPE`
enum (verified against the library's actual runtime behavior in this
session -- earlier attempts with guessed values segfaulted from reading an
unterminated event array; `espeakEVENT_LIST_TERMINATED = 0` is the correct
value, not 6).

## Speech rate (`rate` param, default 160)

This code never called `espeak_SetParameter(espeakRATE, ...)` before, so
every prior render in this session ran at whatever espeak-ng's own
built-in default is -- confirmed by querying `espeak_GetParameter(1, 1)`
(1=espeakRATE) right after init with no rate call made: it returned 175,
matching the "nominally in words-per-minute" `espeakRATE_NORMAL` constant
documented in espeak-ng's actual `speak_lib.h`
(github.com/espeak-ng/espeak-ng, `src/include/espeak-ng/speak_lib.h` --
`#define espeakRATE_NORMAL 175`, min 80, max 450). There is no separate
"voiceRate config" anywhere else stacking a multiplier on top of this --
grepped the repo before writing this, found none.

175 is itself inside the 160-180 WPM target range the user specified
(BBC subtitle guideline, ~15-17 CPS), but it's a NOMINAL target, not a
guaranteed delivered rate -- real measured WPM on 4 real test sentences at
rate=175 ranged from 158.1 to 207.9 WPM (avg 187.2), i.e. actually
delivered speech runs faster than the nominal parameter on sentences
without much internal punctuation-driven pausing. Measured (not guessed)
by resynthesizing those same 4 sentences at several candidate rate values:

    rate=175 (unset default): per-beat WPM [207.9, 190.0, 158.1, 192.9], avg 187.2
    rate=160:                 per-beat WPM [190.6, 175.0, 144.9, 177.2], avg 171.9
    rate=150:                 per-beat WPM [180.3, 164.3, 136.0, 165.3], avg 161.5
    rate=145:                 per-beat WPM [176.6, 159.0, 132.6, 160.0], avg 157.0

rate=160 was chosen because it centers the average (171.9) in the middle
of the 160-180 target while keeping the two least-paused sentences inside
or near the band (175.0, 177.2). No single rate value lands EVERY real
sentence inside 160-180 -- the punctuation-heavy outlier ("In 1943, over a
thousand women...") measures 144.9 WPM even at rate=160, because its
internal comma-pausing is structural (from the text itself), not
proportionally scaled by the rate parameter the same way continuous
word-speaking speed is. Stated plainly rather than overclaiming "always in
range."

## Pitch / pitch-range (`pitch`, `pitch_range` params, both new)

Before this pass, `espeak_SetParameter` was never called for PITCH (3) or
RANGE (4) either -- confirmed the same way as RATE was: queried
`espeak_GetParameter` for both right after init with no call made, got
PITCH=50, RANGE=50. These match espeak-ng's own documented defaults in
`speak_lib.h` (fetched from github.com/espeak-ng/espeak-ng,
`src/include/espeak-ng/speak_lib.h`): the `espeak_PARAMETER` enum comment
next to `espeakPITCH` reads "base pitch, range 0-100. 50=normal"; next to
`espeakRANGE`: "pitch range, range 0-100. 0-monotone, 50=normal". So every
prior render in this session (including the rate=160 pass) used flat
default pitch and default pitch-range on every channel -- no per-channel
voice differentiation existed anywhere before this.

espeak-ng's own project documentation (fetched search result, not
guessed) states plainly that espeak's formant-synthesis approach is "not
as natural or smooth as larger [sample-based] synthesizers" -- raising
RANGE cannot make espeak sound like a human recording; it only widens how
much the synthesizer's pitch contour moves, which is the one real,
documented lever this library exposes for "less flat/monotone." Per-
channel RANGE/PITCH values below are this build's own new design work
(not sourced from any bible -- none of the 8 bible docs mention TTS
prosody), loosely differentiated from channelConfigs.ts's existing
`scriptTone` strings, same "no confirmed taxonomy, flag it" caveat as
`sfx_triggers.py`'s `_channel_flavor()`. Kept inside the documented 0-100
range in all cases; none pushed to extremes.
"""

from __future__ import annotations

import ctypes
import wave
from dataclasses import dataclass
from pathlib import Path

import espeakng_loader

_AUDIO_OUTPUT_RETRIEVAL = 1
_ESPEAK_EVENT_LIST_TERMINATED = 0
_ESPEAK_EVENT_WORD = 1
_ESPEAK_CHARS_UTF8 = 1
_ESPEAK_RATE = 1  # espeak_PARAMETER enum, confirmed via espeak-ng's real speak_lib.h
_ESPEAK_PITCH = 3
_ESPEAK_RANGE = 4

# Empirically calibrated, not guessed -- see module docstring's "Speech
# rate" section for the real measured WPM data across candidate values.
DEFAULT_RATE_WPM = 160

# espeak-ng's own documented defaults (speak_lib.h: "50=normal" for both).
DEFAULT_PITCH = 50
DEFAULT_PITCH_RANGE = 50


class _EspeakEventId(ctypes.Union):
    _fields_ = [
        ("number", ctypes.c_int),
        ("name", ctypes.c_char_p),
        ("string", ctypes.c_char * 8),
    ]


class _EspeakEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("unique_identifier", ctypes.c_uint),
        ("text_position", ctypes.c_int),
        ("length", ctypes.c_int),
        ("audio_position", ctypes.c_int),  # ms into this synthesis call's audio
        ("sample", ctypes.c_int),
        ("user_data", ctypes.c_void_p),
        ("id", _EspeakEventId),
    ]


@dataclass(frozen=True)
class WordTiming:
    word: str
    start_ms: int


@dataclass(frozen=True)
class SynthResult:
    sample_rate: int
    pcm_bytes: bytes  # mono, 16-bit signed PCM
    word_timings: list[WordTiming]
    duration_ms: int


def synthesize(
    text: str,
    voice: str = "en-us",
    rate_wpm: int = DEFAULT_RATE_WPM,
    pitch: int = DEFAULT_PITCH,
    pitch_range: int = DEFAULT_PITCH_RANGE,
) -> SynthResult:
    """Synthesizes `text` and returns real PCM audio plus real per-word
    start timestamps (from espeak-ng's own synthesis event stream, not
    estimated from character count or a fixed clock).

    `rate_wpm` is the nominal espeak rate parameter (not a guaranteed
    delivered WPM -- see module docstring). Default is empirically
    calibrated against real measured output, not espeak's own unset
    default of 175.

    `pitch`/`pitch_range` are espeak-ng's own documented 0-100 parameters
    (50=normal for both; see module docstring's "Pitch / pitch-range"
    section). Defaults match espeak's own unset behavior -- pass
    per-channel values from VOICE_PROFILES (voice_profiles.py) for any
    channel-differentiated render."""

    lib = ctypes.CDLL(espeakng_loader.get_library_path())

    lib.espeak_Initialize.restype = ctypes.c_int
    lib.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    data_path = espeakng_loader.get_data_path().encode("utf-8")
    sample_rate = lib.espeak_Initialize(_AUDIO_OUTPUT_RETRIEVAL, 0, data_path, 0)
    if sample_rate <= 0:
        raise RuntimeError(f"espeak_Initialize failed, rc={sample_rate}")

    lib.espeak_SetParameter.restype = ctypes.c_int
    lib.espeak_SetParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    rc = lib.espeak_SetParameter(_ESPEAK_RATE, rate_wpm, 0)
    if rc != 0:
        raise RuntimeError(f"espeak_SetParameter(RATE, {rate_wpm}) failed, rc={rc}")
    rc = lib.espeak_SetParameter(_ESPEAK_PITCH, pitch, 0)
    if rc != 0:
        raise RuntimeError(f"espeak_SetParameter(PITCH, {pitch}) failed, rc={rc}")
    rc = lib.espeak_SetParameter(_ESPEAK_RANGE, pitch_range, 0)
    if rc != 0:
        raise RuntimeError(f"espeak_SetParameter(RANGE, {pitch_range}) failed, rc={rc}")

    pcm = bytearray()
    word_timings: list[WordTiming] = []

    synth_callback_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.POINTER(_EspeakEvent)
    )

    def _callback(wav, numsamples, events):
        if numsamples > 0 and wav:
            pcm.extend(ctypes.string_at(wav, numsamples * 2))
        if events:
            i = 0
            while True:
                ev = events[i]
                if ev.type == _ESPEAK_EVENT_LIST_TERMINATED:
                    break
                if ev.type == _ESPEAK_EVENT_WORD:
                    word_text = text[ev.text_position - 1 : ev.text_position - 1 + ev.length]
                    word_timings.append(WordTiming(word=word_text, start_ms=ev.audio_position))
                i += 1
        return 0

    cb = synth_callback_t(_callback)
    lib.espeak_SetSynthCallback.restype = None
    lib.espeak_SetSynthCallback.argtypes = [synth_callback_t]
    lib.espeak_SetSynthCallback(cb)

    lib.espeak_SetVoiceByName.restype = ctypes.c_int
    lib.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
    rc = lib.espeak_SetVoiceByName(voice.encode("utf-8"))
    if rc != 0:
        raise RuntimeError(f"espeak_SetVoiceByName({voice!r}) failed, rc={rc}")

    lib.espeak_Synth.restype = ctypes.c_int
    lib.espeak_Synth.argtypes = [
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.c_void_p,
    ]
    text_bytes = text.encode("utf-8")
    uid = ctypes.c_uint(0)
    rc = lib.espeak_Synth(text_bytes, len(text_bytes) + 1, 0, 0, 0, _ESPEAK_CHARS_UTF8, ctypes.byref(uid), None)
    if rc != 0:
        raise RuntimeError(f"espeak_Synth failed, rc={rc}")

    lib.espeak_Synchronize()
    lib.espeak_Terminate()

    duration_ms = round(len(pcm) / 2 / sample_rate * 1000)
    return SynthResult(
        sample_rate=sample_rate,
        pcm_bytes=bytes(pcm),
        word_timings=word_timings,
        duration_ms=duration_ms,
    )


def write_wav(result: SynthResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(result.sample_rate)
        w.writeframes(result.pcm_bytes)
