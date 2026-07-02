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


def synthesize(text: str, voice: str = "en-us") -> SynthResult:
    """Synthesizes `text` and returns real PCM audio plus real per-word
    start timestamps (from espeak-ng's own synthesis event stream, not
    estimated from character count or a fixed clock)."""

    lib = ctypes.CDLL(espeakng_loader.get_library_path())

    lib.espeak_Initialize.restype = ctypes.c_int
    lib.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    data_path = espeakng_loader.get_data_path().encode("utf-8")
    sample_rate = lib.espeak_Initialize(_AUDIO_OUTPUT_RETRIEVAL, 0, data_path, 0)
    if sample_rate <= 0:
        raise RuntimeError(f"espeak_Initialize failed, rc={sample_rate}")

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
