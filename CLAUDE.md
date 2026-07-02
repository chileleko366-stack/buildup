# Dopamine Studios — CLAUDE.md

This file is binding, per project convention (see the audit protocol below).
Read it before writing code in this repo.

## Repo status

This repo (`chileleko366-stack/buildup`) was **empty** when this build
started (2026-07-02): no commits, no branches, no files. Everything under
`src/`, `public/`, and the config files was created from scratch on
branch `claude/dopamine-blueprint-rebuild-k63rsu` starting from Phase 1 of
the "Dopamine Studios — Blueprint-Driven Rebuild" master prompt. There was
no prior codebase to audit against — do not assume any file, convention, or
primitive exists beyond what's listed below without checking.

The master prompt that drove this build referenced a full spec set:
`01_REPO_AUDIT_PROTOCOL.md`, `02_VISUAL_BIBLE.md`, `03_SCRIPT_BIBLE.md`,
`04_ASSET_ACCURACY_BIBLE.md`, `05_PACING_MOVEMENT_BIBLE.md`,
`06_INFRA_SECRETS_AUTOPOST.md`, `07_REVIEW_GATE_PROTOCOL.md`. All 7 have now
been provided and read (as of the session that added Phase 2's Gate 1/2
backfill + read `06`/`07`).

**Known conflict, flagged not silently resolved (per the audit protocol's
own rule that "the repo wins"):** `06_INFRA_SECRETS_AUTOPOST.md` §2 states
`GROQ_API_KEY`, `GEMINI_API_KEY`, and 18 `YT_CH{n}_CLIENT_ID`/`_CLIENT_SECRET`/
`_REFRESH_TOKEN` secrets "already exist — confirm during repo audit, don't
recreate." That assumes the prior repo. This repo was empty at the start of
this build (see above) — those secrets almost certainly do not exist here.
No session so far has had GitHub repo-secrets visibility to confirm either
way (secret values are never readable via the API, and secret *names*
weren't checked). Do not assume any of those 21 secrets are configured;
confirm with the user or check the repo's Settings → Secrets before Phase 5
work depends on them.

## Ground rules (carried over from the master prompt, still binding)

1. No imagination — confirm before referencing, same as the audit protocol
   demands of the (nonexistent) prior repo.
2. Fail loud — no silent fallback, no soft-skip, no "close enough" asset
   substitution.
3. No "done" without a rendered artifact.
4. Grep-before-create — check `src/primitives/` before adding a primitive
   that might duplicate one.

## Stack

- Remotion 4.0.484 (`remotion`, `@remotion/cli`), React 19.2.3, TypeScript,
  no Tailwind (removed from the `create-video` blank template — primitives
  use inline styles per the visual bible's exact values).
- Canvas: 720×1280, 24fps (`src/constants/canvas.ts`), confirmed against
  `02_VISUAL_BIBLE.md` §1.
- Dev entry: `npm run dev` (`remotion studio`). Render: `npx remotion render
  src/index.ts <composition-id> <output>`. Still frame: `npx remotion still
  src/index.ts <composition-id> <output> --frame=<n>`.

## Environment quirk: fonts are self-hosted, not fetched via @remotion/google-fonts

This session's headless Chromium does not trust the outbound TLS proxy's CA,
so `@remotion/google-fonts`' runtime CDN fetch to `fonts.gstatic.com` fails
render with `ERR_CERT_AUTHORITY_INVALID`. Worked around by downloading the
two font files once via `curl --cacert /root/.ccr/ca-bundle.crt` (which does
trust the proxy) into `public/fonts/`, and loading them via a plain
`@font-face` + `staticFile()` component (`src/dev/Fonts.tsx`) instead of
`loadFont()`. `@remotion/google-fonts` is not a dependency.
If you rebuild this in an environment without that proxy quirk, switching
back to `@remotion/google-fonts`' `loadFont()` is fine and arguably cleaner
— this workaround exists only because of this session's network setup.

Also: `remotion.config.ts` points `Config.setBrowserExecutable()` at
`/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`
because Remotion's own headless-shell download (from `remotion.media`) is
blocked by the environment's egress allowlist. That path is specific to
this container image — update or remove it if rendering elsewhere.

## Fonts

- Anton (`FONT_ANTON`, weight 400) — bold condensed display face, used for
  WordCascade and (per bible §4) the normal caption system.
- Space Grotesk (`FONT_SPACE_GROTESK`, variable weight 300–700) — used for
  BadgeBumper tag text. **Not explicitly specified** in `02_VISUAL_BIBLE.md`
  §2 (which only says "bold white text, no icon") — Space Grotesk was
  chosen as the more UI/label-appropriate of the two confirmed fonts, but
  this is an assumption, not a confirmed fact. Revisit if the (unseen)
  blueprint video frames show otherwise.
- Files: `public/fonts/Anton-Regular.woff2`, `public/fonts/SpaceGrotesk-Variable.woff2`.

## Primitive library (as of Phase 1 — 3 primitives, not 49)

The master prompt's audit protocol describes a "~49-primitive library" —
that assumes the prior repo. This repo has exactly three, all in
`src/primitives/`:

| File | Component | Spec |
|---|---|---|
| `src/primitives/BadgeBumper.tsx` | `BadgeBumper` | `02_VISUAL_BIBLE.md` §2 |
| `src/primitives/WordCascade.tsx` | `WordCascade` | `02_VISUAL_BIBLE.md` §3 |
| `src/primitives/DuotoneGrade.tsx` | `DuotoneGrade` | `02_VISUAL_BIBLE.md` §5 |

Grep this directory before adding a new one.

### BadgeBumper
Fixed top-left badge, 24px inset at 720×1280 (scales proportionally via
`canvasWidth`/`canvasHeight` props), solid accent-color fill, bold white
tag text, static for the whole video, z-index 100 (topmost, per §8 layering
order). Channel names, accent colors, and badge tags live in
`src/constants/channels.ts`, sourced from bible §2 (revised): `CH1`.."CH6"
are this codebase's internal IDs only (never rendered on screen) —
`name`/`badgeTag` are the real per-channel identity: Dopamine Loop (`DPL`),
FinanceFiction (`FNF`), Redacted (`RED`), The Grey Matter (`TGM`), The Quiet
Record (`TQR`), Red Space Facts (`@RedFACTS.I` — confirmed by the user as
the channel's real handle over the bible's own `RSF` fallback, 2026-07-02;
this is a deliberate exception to the general "3-4 char" badge rule). No
channel config JSON exists yet (Phase 2+ work) — this table is still the
bible's own "working assumption, not the final source of truth."

### WordCascade
Rapid word-flash timing mode: 4-6 frame hold per word (default 5), hard cut
between words (one word visible at a time, no accumulation, no fade), then
a 12-24 frame hold (default 18) on the full phrase. `wordCascadeDuration()`
exported for callers to compute total duration. `anchorYRatio` prop stands
in for the not-yet-existing `brief.composition.primaryAnchor` field the
bible says WordCascade must respect — wire that field through this prop
once `shot_brief.py` exists.

### DuotoneGrade
Three variants (`neutral`, `teal-archival`, `warm-sepia`) as a CSS `filter`
wrapper, applied only to the background layer (never text/badge, per §8).
**The filter values are UNVERIFIED.** The bible itself calls them "a
starting point, not a locked number" pending visual comparison against
extracted blueprint frames — this session had no access to the blueprint
video. Gate render (`src/dev/DuotoneGradeGate.tsx`) against a
colorful test background (`src/dev/GradeTestBackground.tsx`, not
`PlaceholderBackground` — that one's too dark/desaturated to show grading
differences) shows `teal-archival`'s `hue-rotate(140deg)` swinging a blue
sky to pink/magenta, which reads as a much more dramatic shift than "teal
archival" suggests. Don't treat this variant as final; re-derive against
real footage before shipping any channel that uses it (CH3, CH4 per the
bible).

## Dev / gate-render harness

`src/dev/` holds non-shipping helper components used only to produce the
Phase 1 gate renders (isolation renders of each primitive at 3 text
lengths/durations, shown to the user before Phase 2, per the master
prompt's gate discipline): `PlaceholderBackground.tsx`,
`GradeTestBackground.tsx`, `Fonts.tsx`, and one `*Gate.tsx` composition per
primitive, registered in `src/Root.tsx` as `Gate-BadgeBumper`,
`Gate-WordCascade`, `Gate-DuotoneGrade`. These are scaffolding, not shot
compositions — expect them to be replaced once Phase 3 wires a real channel
end-to-end.

**`07_REVIEW_GATE_PROTOCOL.md`'s Gate 1 spec (seen after the above were
built) is stricter than what those three covered**: it wants BadgeBumper
shown for all 6 channel colors *side by side in one frame* (the original
gate only varied tag length across 3 colors), and the DuotoneGrade
comparison *side by side in one frame*, not sequential-in-time. Backfilled
as two more compositions: `Gate-BadgeBumper-AllChannels`
(`BadgeBumperAllChannelsGate.tsx`) and `Gate-DuotoneGrade-SideBySide`
(`DuotoneGradeSideBySideGate.tsx`, which center-crops the same full-height
slice of the background into each panel rather than scaling-to-fit-width,
since scaling a 9:16 image into a ~3:16 panel would letterbox and waste 2/3
of the frame).

## Phase 2 — footage-sourcing module (`pipeline/footage_sourcing/`)

Python, not TypeScript — matches the master prompt's own references to
`shot_brief.py` and kokoro-onnx (Python), on the assumption the backend
pipeline (script → brief → TTS → asset sourcing) is Python and only the
render step is Remotion/JS. `requirements.txt` at repo root (`requests`
only, so far).

**Environment constraint, confirmed not assumed:** this session has no
Pexels/Pixabay API keys, no LLM provider key (Groq/Gemini/Anthropic/etc.),
and its egress policy denies `api.nasa.gov`, `commons.wikimedia.org`, and
`www.loc.gov` (403 from the proxy — an org policy denial, checked via direct
curl, not assumed). Nominatim wasn't separately tested but should be assumed
blocked too until proven otherwise. So no live network call from this
module has ever succeeded in this session — everything below marked "real"
means real, uncorrupted, would-work code, not "tested against a live API."

| File | What it does | Live-tested this session? |
|---|---|---|
| `types.py` | `Domain`, `ChannelId`, `VisualKeyword`, `SourcedAsset`, `ScoredMatch`, `SourcingResult` dataclasses | n/a (pure types) |
| `config.py` | `CHANNEL_SOURCES` (transcribed from `04_ASSET_ACCURACY_BIBLE.md` §2's table), `GEOCODING_FORBIDDEN_DOMAINS`, `CONFIDENCE_THRESHOLD` | n/a |
| `keyword_extraction.py` | LLM call, beat text → 2-4 `VisualKeyword`s | **Stub.** Raises `NotConfiguredError` — no LLM key present. Provider not chosen yet. |
| `clients/pexels.py`, `clients/pixabay.py` | Real HTTP call code | **Stub-gated.** Raises `NotConfiguredError` without `PEXELS_API_KEY`/`PIXABAY_API_KEY`. |
| `clients/nasa.py`, `clients/wikimedia.py`, `clients/loc.py` | Real HTTP call code, no key needed | Written for real, **never successfully called** — egress denied in this session. |
| `clients/nominatim.py` | Real HTTP call code for `earthly-place` only | Same as above, plus a hard `DomainRoutingViolation` raise if ever called with a `space`/`historical-*` keyword — this is the structural fix for the Nominatim/celestial-body bug the bible opens with. |
| `source_router.py` | `route(keyword) -> [clients]` per `CHANNEL_SOURCES`, with `_guard_against_forbidden_domain()` as a second, redundant enforcement of the same hard rule | Routing logic itself tested (unit-style, in `gate_test.py`) |
| `confidence.py` | Scoring (source relevance score, else keyword-overlap) + domain-specific hard verification (§4: NASA catalog-ID check, historical named-entity-in-title check, earthly-place region-hint check) + reject-below-threshold | Tested against fixture data |
| `cache.py` | JSON-file cache keyed by `(channel, keyword, domain)`; never caches rejected matches; `verified: false` on first accepted historical match per §4's "flag for manual review, don't auto-reuse" rule | Tested against fixture data |
| `sample_beats.py` | 30 hand-authored test beats, 5/channel, following `03_SCRIPT_BIBLE.md` §3's per-channel arc | Hand-authored, **not LLM output** — stands in for `shot_brief.py`, which doesn't exist yet |
| `fixture_results.py` | Hand-authored stand-ins for what `client.search()` would return, since no client can reach its API this session | Explicitly labeled as fixtures, not real search results, including 4 deliberately-failing cases to prove the reject path actually rejects |
| `gate_test.py` | Runs `sample_beats.py` through the real router/scorer/cache using `fixture_results.py`; run via `python3 -m pipeline.footage_sourcing.gate_test` | This is the Phase 2 gate deliverable |

**What Phase 2's gate actually proves, and what it doesn't:** domain-based
routing, the geocoding hard-guard, confidence scoring/rejection, and caching
all run correctly against fixture data. It does NOT prove any real API
integration works — that requires (a) Pexels/Pixabay keys, (b) an LLM
provider key for `keyword_extraction.py`, and (c) an environment whose
egress policy allows NASA/Wikimedia/LOC/Nominatim. Don't report Phase 2 as
fully done until those are in place and re-tested live.

## Phase 3 — CH6 end-to-end short (`ch6-jupiter-red-spot-001`)

Built from a diff the user provided against files that didn't otherwise
exist in this repo (`src/pipeline/channelConfigs.ts`,
`src/remotion/channels/ch{2,4,6}/*`) — confirmed by checking this repo's
only branch, which had none of them. The user confirmed (2026-07-02): no
fuller version of these files exists anywhere to hand over; design the
missing architecture from the 5 available bibles + the diff's fragments,
flagging anything beyond that as new/unconfirmed design work rather than
inventing it silently.

| File | Status |
|---|---|
| `src/pipeline/channelConfigs.ts` | **Real**, built directly from the diff's before/after color values (all 6 channels) — not invented |
| `pipeline/shot_brief.py` (`ShotBrief`, `Beat`, `_validate_shot_brief`) | New design, traced beat-by-beat to bible rules in the file's own docstring (cascade count, duration ranges, `composition.primary_anchor`) |
| `src/primitives/KineticCaption.tsx` | Fills the `02_VISUAL_BIBLE.md` §4 gap (normal-pace captions) left open since Phase 1. Per-word hold range is bible-confirmed (12-24 frames); progressive-accumulation behavior and hard-appear (no fade) are this build's own design choices, documented in the file |
| `src/remotion/channels/ch6/{HardCutFlash,AmbientBackground,Starfield}.tsx` | **Not in any bible.** Reconstructed only from a diff comment naming them, with no implementation shown — each file's header says so explicitly |
| `src/remotion/{ShotBriefLayer,BeatCompositor}.tsx` | Generic engine, channel-agnostic. Ken Burns/grading logic is bible-traceable; the "brief-driven primitive/positioning/depth" and "celestial vs non-celestial" framing from the diff aren't implemented (no spec for what those mean) — every beat is treated uniformly |
| `pipeline/ch6_short_001.py` | Hand-authored script (26 beats, 61.9s), **not LLM output** — same reason as Phase 2's `sample_beats.py`. Facts are general astronomical knowledge, not fetched/cited source documents; `source_snippet` says so on every beat rather than pretending a citation trail exists |
| `src/remotion/data/ch6-jupiter-red-spot-001.json` | Exported shot brief, validated by `_validate_shot_brief()` |
| `src/remotion/channels/ch6/Ch6Composition.tsx`, composition id `CH6-jupiter-red-spot-001` | The rendered short |

**What this render does NOT contain, stated plainly:** no real NASA imagery
(egress to `images-api.nasa.gov` is blocked this session, confirmed in
Phase 2; every beat's background is `GradeTestBackground`, the same
non-shipping placeholder from the Phase 1 gates) and no audio track
(kokoro-onnx was never wired up — no self-hosted model files exist, no TTS
call was made). Beat durations come from `05_PACING_MOVEMENT_BIBLE.md` §2's
table, not real speech timing. Don't present this MP4 as a finished,
publishable short — it proves the render *engine* (hard cuts, Ken Burns,
grading, badge, WordCascade/KineticCaption, brief validation, real asset
*routing* decisions) works end-to-end, not that real footage or narration
exist yet.

## TTS investigation (`pipeline/tts/`) — kokoro-onnx blocked, espeak-ng works

`kokoro-onnx` (the pip package) installs fine — PyPI is reachable. It is
NOT usable in this session because both of its documented model-file
sources are unreachable, for two different, verified reasons (see
`pipeline/tts/kokoro_engine.py`'s module docstring for the exact errors):

1. `github.com/thewh1teagle/kokoro-onnx/releases/...` — outside this
   session's GitHub repo scope (`chileleko366-stack/buildup` only); returns
   HTTP 403 "GitHub access to this repository is not enabled for this
   session."
2. `huggingface.co/hexgrad/Kokoro-82M/...` (the alternate host for the same
   weights) — blocked at the network egress/proxy policy level (confirmed
   403 CONNECT rejection via the proxy's own status endpoint).

`pipeline/tts/espeak_engine.py` is a **real, working, network-independent**
alternative: it drives the `libespeak-ng.so` + data files that ship inside
`espeakng-loader` (a transitive dependency of `kokoro-onnx`, already on
disk, no download needed) directly via ctypes — retrieval-mode synthesis
with a word-boundary event callback, giving real PCM audio *and* real
per-word start timestamps from espeak-ng's own synthesis engine (not
estimated). **This is explicitly a stand-in voice, not Kokoro** — robotic
synthesized speech, used only to prove real-timestamp-driven timing works
end to end while kokoro-onnx itself stays blocked.

Proven end-to-end on one beat (CH6's `cascade-1`, "A storm that never
stops"): real WAV audio (`public/audio/ch6-cascade-1-espeak.wav`) + real
per-word frame timings (`src/remotion/data/ch6-cascade-1-real-tts.json`),
fed into `WordCascade.tsx`'s new `wordTimings`/`audioEndFrame` props (added
alongside the existing fixed-clock fallback, per
`05_PACING_MOVEMENT_BIBLE.md` §5's own "TTS-aligned timing is preferred...
fixed hold is the fallback" framing — not a replacement, an addition).
Rendered as `Gate-Cascade1-RealTTS` — real audio muxed into the mp4
(verified via `mp4a`/`soun` box markers), real duration (54 frames/2.25s,
vs. the placeholder's 43 frames/1.79s for the same beat — longer, not
shorter, measured not assumed). The full CH6 `ch6-jupiter-red-spot-001`
short is UNCHANGED — still all pacing-bible placeholder durations; only
this one beat has been proven with real timing.

## Sound engineering (`pipeline/audio/`) — sourced from real repos, cited per value

Every numeric value in `pipeline/audio/mix.py` and `sfx_triggers.py` is
either (a) fetched directly from a real repo's actual source file (not a
tutorial/gist), with the repo name and exact quoted line in the code
comment, or (b) explicitly marked `NOT_SOURCED` where no real reference
could be verified. Full research trail (what was checked, what was
rejected and why) is in the session history; summary:

| Value | Sourced from | Note |
|---|---|---|
| Ducking: music `volume=-22dB`, `sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400`, `alimiter=limit=0.95` | `github.com/Upload-Post/avatar-mix`, `scripts/composite.py`, `mix_audio()` — fetched directly, real production Python, not docs | Real |
| Loudnorm target `I=-16:TP=-1.5:LRA=11` | `github.com/brolnickij/yt-dbl` (222 commits, real releases), `src/yt_dbl/utils/audio_processing.py` | Real; cross-checked against `github.com/SimpelMe/ffmpeg-leveler` (47 commits) which independently converges on `-16.0` LUFS integrated (different TP/LRA) |
| "-14 LUFS for YouTube" | — | **NOT_SOURCED.** Commonly repeated online; no real repo found using it in working code. Used -16 LUFS instead (see above) |
| Two-pass mechanism (measure `print_format=json` → apply `measured_I/TP/LRA/thresh` + `linear=true`) | FFmpeg's own documented `loudnorm` semantics; named by `Piklesh/auto-loudnorm`, `indiscipline/ffmpeg-loudnorm-helper`, `lbcard/2pass_loudnorm` (real, confirmed to exist and be dedicated to this) | Mechanism confirmed; those 3 repos' exact source wasn't independently re-verified line-by-line |
| Music-bed EQ "pocket cut" for vocal presence | — | **NOT_SOURCED.** Closest real match (`yt-dbl`'s `highshelf=gain=-3:frequency=4500:width_type=q:width=0.7` + `compand`) is a voice-side de-esser, not a music-side pocket cut. Not implemented. |
| SFX one-shot normalization target | — | **NOT_SOURCED.** No real repo found with a verified specific value for normalizing one-shot SFX assets. |

**ffmpeg binary:** neither bundled ffmpeg in this repo supports the filters
above — Playwright's build is `--disable-everything` (mjpeg/vp8/png only),
Remotion's (`@remotion/compositor-linux-x64-*`) is `--disable-filters`
with a small explicit allowlist (has `loudnorm`, not `sidechaincompress`/
`compand`/`highshelf`/`astats`/`alimiter`/`dynaudnorm`). `imageio-ffmpeg`
(pip) bundles a real static build (johnvansickle.com, full filter set,
GPL+version3) — confirmed via `-hide_banner -filters` to have everything
needed. `pipeline/audio/ffmpeg_bin.py` resolves it.

**SFX keyword triggers** (`sfx_triggers.py`): money/twist/hook-opener
keyword lists and the cascade "final-word-only" rule are transcribed from
the user's own product spec, not sourced from a bible (they're
requirements, not audio-engineering facts). `MIN_GAP_MS=175` is the
midpoint of the user's stated 150-200ms range, not one exact mandated
number. Per-channel "flavor" selection reuses `channelConfigs.ts`'s
existing `scriptTone` strings (the only per-channel genre/mood data that
exists) via a simple keyword match — new design work, not confirmed by
anything.

**No real SFX asset library exists anywhere in this repo** (confirmed by
`find` before writing any of this) — no cash-register cue, no riser, no
tension hit, no notification pop. `generate_placeholder_tone()` synthesizes
sine beeps via ffmpeg's own `sine` source purely to prove the trigger
detection/timing/priority/mixing mechanism end-to-end. These are NOT real
SFX and must not be shipped as such — sourcing real, licensed SFX is
unresolved work.

**Proven end-to-end**, both with real numbers from actually running the
chain (not descriptions):
- `Gate-Cascade1-FullChain`: cascade-1's real TTS audio, ducked under a
  synthetic placeholder music bed (two detuned sine tones, NOT real music),
  two-pass loudnorm mastered. Re-measured output: -19.82 LUFS / -1.5 dBTP
  (target was -16/-1.5/11) — off-target on integrated loudness because the
  clip is only ~1.5s, which loudnorm's linear-gain mode has real, measured
  difficulty correcting fully within the true-peak ceiling on such a short/
  low-headroom test signal. Not glossed over; this is the actual number.
- `Gate-Ch2-MoneySfxDemo`: a CH2 beat ("...turned $8,000 into a company
  worth billions.") with 3 real MONEY-category triggers detected at real
  word timestamps (`$`@frame62, `worth`@frame104, `billions`@frame111 —
  found "billions" only after adding plural forms to the keyword list,
  which the user's literal spec didn't include; noted, not silently
  patched in without mention), placeholder tones mixed in via
  `overlay_sfx()`, same ducking+loudnorm chain. Re-measured output: -16.74
  LUFS / -1.5 dBTP — close to target, consistent with the ~1.5s-clip
  theory above (this beat is ~5.2s).
- Both rendered as actual mp4s with real audio muxed in (verified via
  `mp4a`/`soun` box markers, not assumed from a successful exit code).
- Espeak's own word-segmentation on digit-heavy text produced visible
  artifacts (e.g. "$8,000" tokenized into `$`, `8,`, `,0` as separate
  caption words) — real, observed behavior, visible in the
  `Gate-Ch2-MoneySfxDemo` render; not cleaned up, flagged instead.

## Keyword SFX extended to all 6 channels (`pipeline/audio/sfx_triggers.py`)

Verified/expanded the user's proposed per-channel keyword lists against
real content in this repo (`pipeline/footage_sourcing/sample_beats.py`'s
5-beat/channel fixtures and `pipeline/ch6_short_001.py`'s 26-beat CH6
script) before finalizing, per the user's own instruction — with one
correction stated plainly rather than silently accepted: that "real
content" is hand-authored test fixtures, not LLM-generated output (no
LLM has ever run in this repo; `keyword_extraction.py` is still
stub-gated). Findings, most significant first:

- **CH4's proposed keywords (neurons/synapse/cortex/signal/neural) appear
  ZERO times in CH4's actual real content**, which says "brain" and
  "mind" instead. Without adding those two words, CH4's own existing
  sample beats would never fire its SFX category at all. Added them —
  this doesn't collapse CH1/CH4 into the same sound, since classification
  is scoped per-channel: a CH1 beat saying "brain" fires CH1's (softer,
  lower) cue, a CH4 beat saying "brain" fires CH4's (sharper, higher)
  cue. Confirmed distinct by generating both and comparing.
- CH3: "leaked" confirmed real; real text says "expose" not "exposed" —
  added "expose" alongside it.
- CH1/CH5/CH6: partial confirmation (CH1 "brain", CH5 year mentions +
  "died", CH6 "miles" + "telescope" all confirmed real); remaining
  proposed words are plausible for the channel's stated niche but not
  proven by the small sample available — kept, flagged as unconfirmed
  rather than either dropped or silently treated as verified.
- Checked 3 more potential real SFX sources this pass (freesound.org,
  pixabay.com, mixkit.co) — all blocked by this session's egress policy,
  same as before. No real SFX library exists; still placeholder tones.
- The "same dynaudnorm settings" the request referred to don't exist —
  no one-shot SFX normalization was ever sourced or applied in the prior
  pass (flagged NOT_SOURCED then, still NOT_SOURCED now). Not silently
  invented to match the request's assumption.
- Found and fixed two real bugs during testing, not before: (1) phrase
  triggers ("cover-up", "black hole", "lost to history") only worked for
  cascade beats' full-text check, never for a normal beat's per-word scan
  — added a sliding-window phrase pass for non-cascade beats. (2)
  "discovery" (noun) didn't match where "discovered" (verb) did.

Priority is now tiered (`SfxCategory` IntEnum): cascade payoff > this
channel's primary topic category > secondary category > twist > hook-
opener. Placeholder tones now use 3 distinct generation shapes (`tone`,
`sweep` via `aevalsrc` chirp, `burst` via `anoisesrc`+`bandpass`) so all
14 categories are audibly distinguishable, not just different pitches of
one beep — e.g. the cascade payoff is now a genuine rising sweep, not a
flat tone mislabeled as a "riser" (the prior pass's comment said "riser"
but the code just played a fixed 400Hz tone; fixed).

Verified via `pipeline/render_sfx_verification.py`: one real beat per
channel (real sample-fixture text containing that channel's actual
keyword), full pipeline (real espeak TTS → real trigger detection →
placeholder SFX overlay → real ducking → real two-pass loudnorm),
explicit PASS/FAIL check that (a) the expected category fired and (b) no
channel accidentally fell back to CH2's MONEY category. **All 6: PASS.**
Real loudness numbers per channel are in the session's report; CH3 landed
at -19.48 LUFS (off-target vs. the -16 goal) for the same short-clip
reason already documented above — not glossed over.

## GitHub Actions (`.github/workflows/render-shorts.yml`)

Confirmed `.github/workflows/` didn't exist before this file was added (no
prior workflow to extend). One workflow, two `schedule:` cron triggers
(09:00 / 21:00 UTC — arbitrary illustrative times, not sourced from
anything, adjust freely) sharing the same job and 6-channel matrix, per
`06_INFRA_SECRETS_AUTOPOST.md` §3's "stagger channels across two daily cron
triggers" framing.

**Real gaps, flagged in the workflow file's own header comment too, not
just here:**
1. Only CH6 has a real composition (`CH6-jupiter-red-spot-001`) to render.
   CH1-CH5 don't exist (Phase 4 hasn't run) — the workflow's composition-
   resolution step fails loud for those 5, on purpose, rather than
   pretending they render.
2. **No automated script → shot-brief → TTS → asset-sourcing pipeline is
   wired to run headlessly.** Every one of those steps in this repo so far
   was a one-off script run manually in a session (`pipeline/ch6_short_001.py`,
   `pipeline/render_audio_demo.py`, etc.). Running this workflow today
   would just re-render the same static CH6 short repeatedly, not generate
   new content — the "2 shorts/day" cadence has no content-generation
   engine behind it yet, independent of the channel-coverage gap above.
3. **No YouTube upload step exists, deliberately.** Searched this repo
   before writing the workflow — there is no YouTube upload script, no
   OAuth flow, anywhere. Per `06_INFRA_SECRETS_AUTOPOST.md` §4's
   `DRY_RUN=true` default and `07_REVIEW_GATE_PROTOCOL.md` Gate 5 (a real
   dry-run render+artifact-save run must happen and be reviewed BEFORE any
   upload step is added), this workflow stops at
   `actions/upload-artifact`. Building an upload script now — even gated
   to `privacyStatus: private` (YouTube's Data API has no separate "draft"
   state; `private` is the closest safe non-public value) — would both
   skip Phase 4 and skip Gate 5's own dry-run-first requirement, and would
   need the `YT_CH{n}_CLIENT_ID`/`_CLIENT_SECRET`/`_REFRESH_TOKEN` secrets
   this repo has never confirmed exist (see the flagged conflict with
   `06_INFRA_SECRETS_AUTOPOST.md` §2 earlier in this file). Not built here;
   flagged instead.

**Also fixed while writing this:** `remotion.config.ts` had a hardcoded
`Config.setBrowserExecutable()` path specific to this session's dev
container (`/opt/pw-browsers/...`) that would not exist on a real GitHub
Actions runner and would break the render step immediately in CI. Now
gated behind `existsSync()` so it's a no-op anywhere that exact path
doesn't exist, letting Remotion fall back to its normal (unblocked, on a
real runner) headless-shell download.

## What does not exist yet (do not assume otherwise)

- Channel config JSONs (60-80 field schema per the audit protocol — not
  designed yet; `channelConfigs.ts` above is a narrower Remotion-styling
  config, not that schema)
- A chosen LLM provider for keyword extraction or script/brief generation
- kokoro-onnx TTS invocation, or Kokoro audio in any rendered short (see
  TTS investigation above — kokoro-onnx itself is blocked; espeak-ng is a
  proven stand-in for exactly one beat, not wired into the full short)
- Real sourced imagery in any rendered short (NASA/Pexels/Pixabay/Wikimedia/LOC)
- CH1/CH2/CH3/CH4/CH5 compositions (only CH6 has been wired end-to-end)
- GitHub Actions workflows, cron schedule, secrets
- YouTube upload script / OAuth flow
- The particle burst transition primitive (bible §6) — not built, out of
  Phase 1 scope, and not used in the CH6 short (HardCutFlash is a
  different, unspecified effect -- see table above)
