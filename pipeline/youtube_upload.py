"""YouTube Data API v3 upload -- real OAuth2 refresh-token flow + real
resumable upload, adapted from Google/YouTube's own official sample repo
(not a tutorial snippet):

  github.com/youtube/api-samples, `python/upload_video.py` (real, first-
  party, maintained by the YouTube org itself). Fetched directly. Reused
  verbatim: the `videos().insert(part=..., body=..., media_body=...)`
  call shape, the `body=dict(snippet=dict(...), status=dict(...))`
  structure, `MediaFileUpload(path, chunksize=-1, resumable=True)`, and
  the retry loop (`MAX_RETRIES=10`, `RETRIABLE_STATUS_CODES=[500,502,503,
  504]`, exponential backoff with `random.random() * (2 ** retry)`).

  NOT reused from that sample: its auth step. The sample uses
  `InstalledAppFlow` (opens a browser for interactive consent) -- not
  usable on a headless CI runner. This module instead builds
  `google.oauth2.credentials.Credentials` directly from a refresh token,
  client ID, and client secret -- the real, documented, non-interactive
  refresh path from Google's own OAuth library
  (github.com/googleapis/google-auth-library-python,
  `google/oauth2/credentials.py`: `Credentials(refresh_token=...,
  token_uri=..., client_id=..., client_secret=...)`). `token_uri` is
  Google's own publicly documented OAuth2 token endpoint,
  `https://oauth2.googleapis.com/token` -- not invented.

## PRIVACY: hardcoded, not configurable

`PRIVACY_STATUS = "private"` below is a module-level literal, read by
nothing else, overridable by nothing else. `upload_video()` does not
accept a privacy parameter at all -- there is no argument, env var,
workflow input, or config value anywhere in this module (or the workflow
step that calls it) that can change what gets written into
`body["status"]["privacyStatus"]`. There is also no function anywhere in
this file, or called by it, that changes a video's status after upload
(no `videos().update()` call, no publish/approve step of any kind).

## Environment quirk fixed while building this

This session's `cryptography` package (`google-auth`'s dependency) was
installed as a broken Debian system package
(`/usr/lib/python3/dist-packages`, version 41.0.7) missing its `_cffi_backend`
extension -- importing `google.oauth2.credentials` crashed with a Rust
`pyo3` panic, not a normal Python exception. Fixed by `pip install
--ignore-installed cryptography cffi`, which shadows the broken system
copy with a working wheel-installed one. Specific to this dev sandbox;
note if rebuilding this environment elsewhere.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from pipeline.footage_sourcing.types import ChannelId

TOKEN_URI = "https://oauth2.googleapis.com/token"  # Google's own documented OAuth2 token endpoint
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

# Hardcoded literal. See module docstring's "PRIVACY" section. Do not add
# a parameter, env var, or config path that can override this.
PRIVACY_STATUS = "private"

MAX_TITLE_CHARS = 100  # YouTube Data API's documented videos.snippet.title limit
CATEGORY_ID = "27"  # "Education" -- youtube/api-samples's own default category

# Mirrors src/constants/channels.ts's `name` field exactly (that file is
# the source of truth for channel display names; duplicated here rather
# than shared because this repo's Python pipeline and TypeScript render
# layer are separate packages with no cross-language import mechanism).
CHANNEL_NAMES: dict[ChannelId, str] = {
    ChannelId.CH1: "Dopamine Loop",
    ChannelId.CH2: "FinanceFiction",
    ChannelId.CH3: "Redacted",
    ChannelId.CH4: "The Grey Matter",
    ChannelId.CH5: "The Quiet Record",
    ChannelId.CH6: "Red Space Facts",
}

MAX_RETRIES = 10  # youtube/api-samples upload_video.py
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]  # youtube/api-samples upload_video.py
RETRIABLE_EXCEPTIONS = (IOError, OSError)  # youtube/api-samples upload_video.py (also covers httplib2/socket errors)


@dataclass(frozen=True)
class OAuthCredentials:
    client_id: str
    client_secret: str
    refresh_token: str


@dataclass(frozen=True)
class VideoMetadata:
    title: str
    description: str
    tags: list[str]


def build_metadata_from_shot_brief(channel: ChannelId, shot_brief_json_path: Path) -> VideoMetadata:
    """Derives title/description/tags from the REAL shot brief JSON this
    channel's render step already produced -- not invented fields. No
    "title" field exists in the shot brief schema (checked
    pipeline/shot_brief.py's Beat/ShotBrief dataclasses before writing
    this), so:
    - title: the "hook" beat's own text (real, already written to grab
      attention -- a natural fit), truncated to MAX_TITLE_CHARS.
    - description: every beat's text concatenated in order (the actual
      full script, real), plus the channel's display name.
    - tags: channel name + genre-agnostic Shorts tags.
    """
    data = json.loads(shot_brief_json_path.read_text())
    beats = data["beats"]

    hook_beat = next((b for b in beats if b["beat_type"] == "hook"), beats[0])
    title = hook_beat["text"].strip()
    if len(title) > MAX_TITLE_CHARS:
        title = title[: MAX_TITLE_CHARS - 1].rstrip() + "…"

    script_lines = [b["text"] for b in beats]
    channel_name = CHANNEL_NAMES[channel]
    description = "\n".join(script_lines) + f"\n\n{channel_name} #Shorts"

    tags = [channel_name, "Shorts", "YouTubeShorts"]

    return VideoMetadata(title=title, description=description, tags=tags)


def _build_youtube_client(creds: OAuthCredentials):
    credentials = Credentials(
        token=None,  # forces an immediate refresh using refresh_token below
        refresh_token=creds.refresh_token,
        token_uri=TOKEN_URI,
        client_id=creds.client_id,
        client_secret=creds.client_secret,
        scopes=[YOUTUBE_UPLOAD_SCOPE],
    )
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials, cache_discovery=False)


def upload_video(
    channel: ChannelId,
    video_path: Path,
    metadata: VideoMetadata,
    creds: OAuthCredentials,
) -> str:
    """Uploads `video_path` to `channel`'s YouTube account. Returns the
    real video ID on success. Raises on failure -- fail loud, no silent
    skip (matches this repo's rule everywhere else).

    Body/retry structure adapted from youtube/api-samples's
    upload_video.py -- see module docstring for the exact citation."""
    youtube = _build_youtube_client(creds)

    body = dict(
        snippet=dict(
            title=metadata.title,
            description=metadata.description,
            tags=metadata.tags,
            categoryId=CATEGORY_ID,
        ),
        status=dict(privacyStatus=PRIVACY_STATUS),  # hardcoded literal -- see module docstring
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" not in response:
                    raise RuntimeError(f"Upload for {channel.value} failed with unexpected response: {response}")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            retry += 1
            if retry > MAX_RETRIES:
                raise RuntimeError(f"Upload for {channel.value} failed after {MAX_RETRIES} retries: {error}")
            sleep_seconds = random.random() * (2**retry)
            time.sleep(sleep_seconds)
            error = None

    return response["id"]


def _creds_from_env(channel: ChannelId) -> OAuthCredentials:
    """Reads this channel's OAuth secrets from env vars named
    YT_{channel}_CLIENT_ID / _CLIENT_SECRET / _REFRESH_TOKEN, per
    06_INFRA_SECRETS_AUTOPOST.md §2's naming convention. GitHub Actions'
    `secrets.*` context does not support dynamic key lookup by matrix
    value (`secrets[matrix.channel]` is not valid Actions syntax), so the
    workflow step exports all 6 channels' secrets as env vars explicitly
    and this function picks the right one at runtime using the CHANNEL
    env var -- a normal Python dict/env lookup, not subject to that
    Actions-context restriction.

    Fails loud (raises, does not silently skip) if any of the 3 required
    values is missing or empty -- this repo has never confirmed these 18
    secrets exist in this repo's GitHub Settings (flagged in CLAUDE.md
    since Phase 1); a missing secret should stop this step with a clear
    diagnostic, not silently no-op the upload.
    """
    prefix = f"YT_{channel.value}"
    client_id = os.environ.get(f"{prefix}_CLIENT_ID", "")
    client_secret = os.environ.get(f"{prefix}_CLIENT_SECRET", "")
    refresh_token = os.environ.get(f"{prefix}_REFRESH_TOKEN", "")
    missing = [
        name for name, val in [("CLIENT_ID", client_id), ("CLIENT_SECRET", client_secret), ("REFRESH_TOKEN", refresh_token)]
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Missing OAuth secret(s) for {channel.value}: {[f'{prefix}_{m}' for m in missing]}. "
            "These must be configured as real GitHub repo secrets before this step can run -- "
            "see CLAUDE.md's flagged conflict with 06_INFRA_SECRETS_AUTOPOST.md §2."
        )
    return OAuthCredentials(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)


def main() -> None:
    """CLI entry point for the workflow step:
    python3 -m pipeline.youtube_upload CH1 out/CH1.mp4 src/remotion/data/ch1-dopamine-loop-notifications-001.json
    """
    if len(sys.argv) != 4:
        print(
            "usage: python3 -m pipeline.youtube_upload <CHANNEL> <video_path> <shot_brief_json_path>",
            file=sys.stderr,
        )
        sys.exit(2)

    channel = ChannelId(sys.argv[1])
    video_path = Path(sys.argv[2])
    shot_brief_json_path = Path(sys.argv[3])

    if not video_path.exists():
        raise FileNotFoundError(
            f"Render output {video_path} does not exist -- refusing to upload a missing/partial file."
        )

    creds = _creds_from_env(channel)
    metadata = build_metadata_from_shot_brief(channel, shot_brief_json_path)
    video_id = upload_video(channel, video_path, metadata, creds)
    print(f"Uploaded {channel.value}: https://youtube.com/watch?v={video_id} (privacyStatus={PRIVACY_STATUS})")


if __name__ == "__main__":
    main()
