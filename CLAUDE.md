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

## What does not exist yet (do not assume otherwise)

- `shot_brief.py` / `_validate_shot_brief()`
- Channel config JSONs (60-80 field schema per the audit protocol — not
  designed yet)
- A chosen LLM provider for keyword extraction or script/brief generation
- kokoro-onnx TTS invocation
- Any Remotion composition that renders an actual shot/short
- GitHub Actions workflows, cron schedule, secrets
- YouTube upload script / OAuth flow
- The particle burst transition primitive (bible §6) — not built, out of
  Phase 1 scope
- Normal-pace (non-cascade) kinetic caption primitive (bible §4) — not
  built, out of Phase 1 scope
- `06_INFRA_SECRETS_AUTOPOST.md` and `07_REVIEW_GATE_PROTOCOL.md` content —
  still unseen by any session as of Phase 2
