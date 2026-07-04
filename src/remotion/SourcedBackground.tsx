import React, { useRef, useState } from "react";
import { AbsoluteFill, continueRender, delayRender } from "remotion";
import { GradeTestBackground } from "../dev/GradeTestBackground";
import type { BeatJson } from "./shotBrief";

// Phase 2 wiring: replaces the hardcoded GradeTestBackground call every
// channel composition used directly, with a component that uses a REAL
// sourced asset when one was accepted (beat.background_asset_url, set by
// pipeline/footage_sourcing/resolve.py), and falls back to the existing
// placeholder -- now labeled with the REAL reason sourcing didn't produce
// an asset -- when it wasn't.
//
// This does not invent a fallback image. Per 04_ASSET_ACCURACY_BIBLE.md's
// fail-loud/reject-don't-guess rule (already enforced upstream in
// confidence.py/resolve.py), a beat with no confident real match has
// nothing to show but the same non-shipping placeholder this repo has
// used since Phase 1 -- the difference from before is that the label now
// says WHY (a real client error, a real rejection reason, or "cascade
// beat -- no keyword to source"), not just a generic beat_id.
//
// ## Real render-blocking bug history (2026-07-03/04 CI runs), and why
// this is a hand-rolled <img> now, not Remotion's own `Img` component
//
// Attempt 1: Remotion's `Img` left its internal delayRender() uncleared
// for its default 30s on one slow Pixabay response, hard-failing the
// ENTIRE ~1900-frame render. Fixed by setting `Img`'s real, documented
// `delayRenderRetries`/`delayRenderTimeoutInMilliseconds` props (traced
// to node_modules/remotion/dist/esm/index.mjs:9828-9831's real compiled
// source).
//
// Attempt 2: the VERY NEXT CI run hit a DIFFERENT real failure -- a
// genuine, repeated HTTP 429 from Pixabay. This goes through `Img`'s own
// on-error retry path (real exponential backoff, confirmed in
// node_modules/remotion/dist/cjs/Img.js's `exponentialBackoff()`/
// `didGetError()`), not the delayRender-timeout path attempt 1 fixed.
// Bumped `Img`'s real `maxRetries` prop (default 2) to 5. Real result:
// this measurably helped (multiple images in the next run recovered
// after 1-4 retries, confirmed via real `retrying again in Nms` log
// lines up to the full 16000ms/5th-retry backoff) -- but ONE image STILL
// exhausted all 5 retries (~31s of backoff) and failed anyway, and
// `Img.js`'s own `didGetError()` calls `cancelRender()` once retries are
// exhausted with no `onError` prop supplied -- killing the whole render
// again, just less often.
//
// Root problem: `Img`'s built-in exhausted-retries behavior is to cancel
// the ENTIRE render job over ONE beat's CDN flakiness, and passing more
// retries only lowers the odds, never removes the failure mode. A
// transient CDN issue on a single already-accepted asset should degrade
// to this beat's own placeholder, not take down every other beat's frame
// too -- the exact same "reject/degrade this one beat, don't crash
// everything" principle SourcedBackground already applies when sourcing
// itself fails.
//
// Implementation: a plain <img> with its OWN delayRender()/
// continueRender() lifecycle (both real, stable, top-level `remotion`
// exports -- node_modules/remotion/dist/cjs/delay-render.d.ts) instead
// of Img's wrapper, so `continueRender()` is guaranteed to fire (and the
// frame capture guaranteed to unblock) the moment retries are truly
// exhausted -- not left contingent on however Img's own onError/
// cancelRender interaction behaves. Same real exponential-backoff formula
// Img.js itself uses (1s/2s/4s/8s/16s), same MAX_RETRIES=5 budget. On
// final failure: continueRender() first (unblock the render), THEN
// switch to rendering GradeTestBackground labeled with the real failure
// -- degrading this one beat, not cancelling the other ~1900 frames.
const MAX_RETRIES = 5;
const DELAY_RENDER_TIMEOUT_MS = 45000;

function exponentialBackoffMs(attempt: number): number {
  return 1000 * 2 ** (attempt - 1); // 1s, 2s, 4s, 8s, 16s
}

const SourcedImage: React.FC<{ beat: BeatJson; src: string }> = ({ beat, src }) => {
  const [handle] = useState(() =>
    delayRender(`Loading sourced background: ${beat.beat_id}`, { timeoutInMilliseconds: DELAY_RENDER_TIMEOUT_MS })
  );
  const [attempt, setAttempt] = useState(0);
  const [failed, setFailed] = useState(false);
  const settledRef = useRef(false);

  if (failed) {
    return (
      <GradeTestBackground
        label={`${beat.beat_id} -- PLACEHOLDER (image failed to load after ${MAX_RETRIES} retries: ${src})`}
      />
    );
  }

  // Cache-busting query param forces a real fresh request on retry,
  // rather than the browser re-surfacing the same failed response.
  const resolvedSrc = attempt === 0 ? src : `${src}${src.includes("?") ? "&" : "?"}retry=${attempt}`;

  return (
    <AbsoluteFill>
      {/* eslint-disable-next-line @remotion/warn-native-media-tag --
          intentionally NOT Remotion's own <Img>: this component
          re-implements Img's own frame-blocking delayRender()/
          continueRender() lifecycle by hand (see this file's header
          comment) specifically so a CDN failure can degrade to this
          beat's placeholder instead of Img's own built-in behavior of
          cancelling the entire render once its retries are exhausted. */}
      <img
        src={resolvedSrc}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        onLoad={() => {
          if (settledRef.current) return;
          settledRef.current = true;
          continueRender(handle);
        }}
        onError={() => {
          if (settledRef.current) return;
          if (attempt < MAX_RETRIES) {
            setTimeout(() => setAttempt((a) => a + 1), exponentialBackoffMs(attempt + 1));
            return;
          }
          settledRef.current = true;
          continueRender(handle); // unblock the render first --
          setFailed(true); // -- then degrade to the placeholder for this beat only
        }}
      />
    </AbsoluteFill>
  );
};

export const SourcedBackground: React.FC<{ beat: BeatJson }> = ({ beat }) => {
  if (beat.background_asset_url) {
    return <SourcedImage beat={beat} src={beat.background_asset_url} />;
  }

  const reason = beat.background_sourcing_status ?? "no sourcing attempted";
  return <GradeTestBackground label={`${beat.beat_id} -- PLACEHOLDER (${reason})`} />;
};
