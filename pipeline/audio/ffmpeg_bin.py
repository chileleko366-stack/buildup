"""Resolves a real, full-featured ffmpeg binary.

Neither ffmpeg build already present in this environment supports the
filters this package needs:
- The Playwright-bundled build (`/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux`)
  is a `--disable-everything` build with only mjpeg/vp8/png -- confirmed
  during Phase 1 gate-render work.
- The Remotion-bundled build (`node_modules/@remotion/compositor-linux-x64-*/ffmpeg`)
  is a `--disable-filters` build with an explicit small allowlist
  (aformat, atrim, amix, loudnorm, volume, sine, ...) -- has `loudnorm` but
  not `sidechaincompress`, `compand`, `highshelf`, `astats`, `alimiter`,
  or `dynaudnorm`. Confirmed via `-hide_banner -filters` during this
  session's audio-pipeline work.

`imageio-ffmpeg` (pip package) bundles a real static build from
johnvansickle.com (`ffmpeg version 7.0.2-static`, `--enable-gpl
--enable-version3`, full filter set) -- confirmed via the same
`-hide_banner -filters` check to have every filter this package uses.
"""

from __future__ import annotations

import functools


@functools.lru_cache(maxsize=1)
def ffmpeg_path() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()
