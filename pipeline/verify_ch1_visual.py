"""Real per-beat verification harness for CH1's rendered short.

Two things the prior CI run's proof did NOT establish, both flagged in the
follow-up instruction that created this file:

1. Visual-register consistency PER BEAT across the whole short (was: a
   single fixed-interval frame grab that happened to land on 3 different
   beats showing 3 different visual registers -- real photo, paper-craft-
   sculpture photo, cartoon vector illustration -- which is what exposed
   the illustration-mismatch bug this session fixed in
   pipeline/footage_sourcing/content_type_filter.py, clients/pixabay.py,
   and pipeline/channel_scripts.py's keyword text).
2. Ken Burns motion WITHIN a single beat's own on-screen duration -- the
   prior run's fixed-interval frames each landed on a different beat, so
   they proved coverage, not motion.

This script reads the shot-brief JSON that pipeline.render_channel_short
just (re)generated -- NOT a hardcoded pacing-bible assumption -- because
CH1-CH5's beat durations are real per-beat TTS lengths (see CLAUDE.md's
Phase 4 section), summed here to get each beat's true
[start_frame, end_frame) window on the actual rendered timeline.

Run as: python3 -m pipeline.verify_ch1_visual <mp4_path> <json_path> <out_dir>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from pipeline.audio.ffmpeg_bin import ffmpeg_path

# background_asset_url is now a LOCAL file path (pipeline/footage_sourcing/
# attach_background.py downloads each accepted asset once during
# generation, to remove the real render-time CDN rate-limit failure a
# remote-URL <img> src caused -- see that module's own docstring), so the
# source can no longer be inferred from the URL's hostname. The real
# source name is instead embedded directly in background_sourcing_status
# as "accepted (<source>): <reason>" -- parsed back out here for this
# manifest's reporting.
_STATUS_SOURCE_RE = re.compile(r"^accepted \(([^)]+)\):")


def _infer_source(status: str | None) -> str:
    if not status:
        return "unknown"
    m = _STATUS_SOURCE_RE.match(status)
    return m.group(1) if m else "unknown"


def _extract_frame(ffmpeg: str, video_path: str, timestamp_s: float, out_path: Path) -> None:
    result = subprocess.run(
        [ffmpeg, "-y", "-ss", f"{timestamp_s:.3f}", "-i", video_path, "-frames:v", "1", "-q:v", "2", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg frame extraction failed at {timestamp_s}s:\n{result.stderr[-2000:]}")


def main() -> None:
    video_path, json_path, out_dir_str = sys.argv[1], sys.argv[2], sys.argv[3]
    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    brief = json.loads(Path(json_path).read_text())
    fps = brief.get("fps", 24)
    beats = brief["beats"]

    ffmpeg = ffmpeg_path()
    print(f"Resolved ffmpeg binary: {ffmpeg}", file=sys.stderr)

    # Real per-beat frame windows, computed by cumulative sum of each
    # beat's own real duration_frames -- not assumed from a fixed table.
    windows = []
    cursor = 0
    for beat in beats:
        start = cursor
        dur = beat["duration_frames"]
        end = start + dur  # exclusive
        windows.append((beat, start, end))
        cursor = end
    total_frames = cursor
    print(f"Total beats: {len(beats)}, total frames: {total_frames} ({total_frames / fps:.2f}s @ {fps}fps)", file=sys.stderr)

    per_beat_manifest = []
    for i, (beat, start, end) in enumerate(windows):
        mid_frame = start + (end - start) // 2
        mid_s = mid_frame / fps
        bg_url = beat.get("background_asset_url")
        bg_status = beat.get("background_sourcing_status")
        content_type = "real photo" if bg_url else "mograph placeholder"
        source = _infer_source(bg_status) if bg_url else None

        frame_name = f"ch1_beat_{i:02d}_{beat['beat_id']}.png"
        frame_path = out_dir / frame_name
        _extract_frame(ffmpeg, video_path, mid_s, frame_path)

        entry = {
            "index": i,
            "beat_id": beat["beat_id"],
            "beat_type": beat["beat_type"],
            "text": beat["text"],
            "start_frame": start,
            "end_frame": end,
            "duration_frames": end - start,
            "midpoint_timestamp_s": round(mid_s, 3),
            "content_type": content_type,
            "source": source,
            "background_asset_url": bg_url,
            "background_sourcing_status": bg_status,
            "frame_file": frame_name,
        }
        per_beat_manifest.append(entry)
        print(f"[beat {i:02d}] {beat['beat_id']} @ {mid_s:.2f}s -- {content_type}"
              f"{f' ({source})' if source else ''} -- {bg_status}", file=sys.stderr)

    # Pick the motion-proof beat: prefer the LONGEST non-cascade beat with
    # a real accepted photo, to maximize the number of distinct 0.5s
    # samples across its own on-screen duration.
    candidates = [
        (beat, start, end) for beat, start, end in windows
        if not beat.get("cascade") and beat.get("background_asset_url")
    ]
    motion_manifest = None
    if not candidates:
        print("NO BEAT WITH A REAL ACCEPTED PHOTO -- cannot run the motion proof this pass.", file=sys.stderr)
    else:
        beat, start, end = max(candidates, key=lambda c: c[2] - c[1])
        duration_s = (end - start) / fps
        print(f"Motion-proof beat: {beat['beat_id']} ({(end - start)} frames / {duration_s:.2f}s), "
              f"source={_infer_source(beat['background_sourcing_status'])}", file=sys.stderr)

        motion_frames = []
        t = 0.0
        while t < duration_s + 1e-6:
            abs_s = start / fps + t
            frame_name = f"ch1_motion_{beat['beat_id']}_{t:.1f}s.png"
            frame_path = out_dir / frame_name
            _extract_frame(ffmpeg, video_path, abs_s, frame_path)
            motion_frames.append({"local_offset_s": round(t, 2), "absolute_timestamp_s": round(abs_s, 3), "frame_file": frame_name})
            print(f"  motion frame @ local {t:.1f}s (absolute {abs_s:.2f}s) -> {frame_name}", file=sys.stderr)
            t += 0.5

        motion_manifest = {
            "beat_id": beat["beat_id"],
            "beat_type": beat["beat_type"],
            "text": beat["text"],
            "start_frame": start,
            "end_frame": end,
            "duration_s": round(duration_s, 3),
            "ken_burns": beat["ken_burns"],
            "background_asset_url": beat["background_asset_url"],
            "source": _infer_source(beat["background_sourcing_status"]),
            "frames": motion_frames,
        }

    manifest = {
        "video_path": video_path,
        "json_path": json_path,
        "fps": fps,
        "total_frames": total_frames,
        "per_beat": per_beat_manifest,
        "motion_proof": motion_manifest,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote manifest: {manifest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
