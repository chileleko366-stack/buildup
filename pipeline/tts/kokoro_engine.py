"""kokoro-onnx TTS engine -- BLOCKED, not stubbed-and-forgotten.

The `kokoro-onnx` pip package installs fine in this environment (PyPI is
reachable). It is NOT usable here because both of its documented model-file
sources are unreachable, for two different, unrelated, verified reasons:

1. `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{kokoro-v1.0.onnx,voices-v1.0.bin}`
   -- these are the URLs `kokoro_onnx/config.py` itself prints in its own
   error message when the files are missing. This session's GitHub access
   is scoped to `chileleko366-stack/buildup` only; a direct request to that
   URL returns HTTP 403 with the body:
   `{"message":"GitHub access to this repository is not enabled for this
   session. Use add_repo to request access."}` -- a session-scoping denial,
   not a network outage.

2. `https://huggingface.co/hexgrad/Kokoro-82M/...` (the alternate host for
   the same model weights) -- blocked at the network egress/proxy policy
   level (`403` on the CONNECT tunnel, confirmed via the proxy's own status
   endpoint: `{"kind": "connect_rejected", "host": "huggingface.co:443"}`).

Per CLAUDE.md's fail-loud rule, this is surfaced as an explicit error, not
silently swapped for a placeholder duration. `espeak_engine.py` in this
same package is a real, working, network-independent alternative used as
an explicitly-labeled stand-in (NOT the intended Kokoro voice) until real
model files are available in this session by some other means (e.g.
provided directly rather than fetched).
"""

from __future__ import annotations


class KokoroModelFilesUnavailableError(Exception):
    pass


def synthesize(text: str, voice: str = "af_heart"):  # noqa: ARG001
    raise KokoroModelFilesUnavailableError(
        "kokoro-onnx model files are unreachable in this session: "
        "github.com/thewh1teagle/kokoro-onnx is outside this session's "
        "GitHub repo scope (chileleko366-stack/buildup only), and "
        "huggingface.co is denied by this session's egress policy. "
        "See this file's module docstring for the exact verified errors. "
        "Use pipeline.tts.espeak_engine as an explicitly-labeled stand-in, "
        "or provide the model files directly."
    )
