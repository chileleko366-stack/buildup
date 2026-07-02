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
`06_INFRA_SECRETS_AUTOPOST.md`, `07_REVIEW_GATE_PROTOCOL.md`. Only
`01` and `02`'s actual content were available to the session that did this
build. `03`–`07` were referenced by name only — their content has not been
seen, so nothing about script structure, asset-sourcing rules, pacing/Ken
Burns specifics, secrets/workflow conventions, or the review-gate protocol
should be assumed to exist yet, even though the master prompt references
concrete deliverables (channel configs, `shot_brief.py`, TTS pipeline,
GitHub Actions matrix, YouTube upload) built on top of them.

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
order). Channel accent colors and default tag strings ("CH1".."CH6") live
in `src/constants/channels.ts`, sourced from bible §2. No channel config
JSON exists yet (Phase 2+ work) — niches for CH1/CH2/CH4/CH5 are not named
anywhere available to this session; only CH3 ("Redacted") and CH6 ("Red
Space Facts") are named, in the master prompt's Phase 3 section.

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

## What does not exist yet (do not assume otherwise)

- `shot_brief.py` / `_validate_shot_brief()`
- Channel config JSONs (60-80 field schema per the audit protocol — not
  designed yet)
- Keyword extraction / footage-sourcing module (Phase 2)
- kokoro-onnx TTS invocation
- Any Remotion composition that renders an actual shot/short
- GitHub Actions workflows, cron schedule, secrets
- YouTube upload script / OAuth flow
- The particle burst transition primitive (bible §6) — not built, out of
  Phase 1 scope
- Normal-pace (non-cascade) kinetic caption primitive (bible §4) — not
  built, out of Phase 1 scope
