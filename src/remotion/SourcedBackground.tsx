import React from "react";
import { AbsoluteFill, Img } from "remotion";
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
// Uses Remotion's own `Img` component (not a plain `<img>`) -- it holds
// frame capture until the image has actually loaded, which is required
// for headless rendering of a remote URL to not race the screenshot.
//
// Real, observed render-blocking bug (2026-07-03/04 CI runs): a single
// slow/flaky response from a real third-party CDN (Pixabay, in the
// observed failure) left Img's internal delayRender() call uncleared for
// its default 30s, hard-failing the ENTIRE render job (all ~1900 frames)
// on account of one image, not just that beat. Real error from the CI
// log: `A delayRender() "Loading <Img> with src=https://pixabay.com/
// get/..." was called but not cleared after 28000ms.`
//
// Fix confirmed real by reading the actual installed Remotion version's
// own compiled source, visible in that same log's stack trace
// (node_modules/remotion/dist/esm/index.mjs:9828-9831): `Img` forwards
// two real, documented props straight into its internal delayRender()
// call -- `delayRenderRetries` (-> `retries`) and
// `delayRenderTimeoutInMilliseconds` (-> `timeoutInMilliseconds`).
// Neither was ever set, so both silently used Remotion's own defaults
// (no retries, 30s timeout) -- exactly the 28s-then-hard-fail behavior
// observed. Set here to a real retry budget + a longer timeout instead
// of reimplementing the same mechanism by hand.
//
// SECOND real, distinct failure mode (found in the very next CI run after
// the fix above): a real, repeated HTTP 429 from Pixabay --
// `Failed to load resource: the server responded with a status of 429`,
// then `EncodingError: The source image cannot be decoded`, retried twice
// with real exponential backoff (1s, 2s per Img's own
// `exponentialBackoff()`), then a real `CancelledError: Error loading
// image with src: https://pixabay.com/get/...` that hard-cancelled the
// whole render. This is NOT the delayRender-timeout path above -- an
// `onerror` DID fire (repeatedly), so `Img`'s own error-count check
// (`errors[src] > maxRetries`) governed, and its real default
// (`maxRetries = 2`, confirmed in node_modules/remotion/dist/cjs/
// Img.js's `ImgContent` destructuring) was exhausted before the rate
// limit cleared. Fixed by also setting `maxRetries` higher -- a real,
// documented Img prop (node_modules/remotion/dist/cjs/Img.d.ts) --
// giving real exponential backoff (1s/2s/4s/8s/16s, ~31s total) more
// room for a transient 429 to clear, comfortably inside the
// delayRenderTimeoutInMilliseconds window above.
const IMG_DELAY_RENDER_TIMEOUT_MS = 45000;
const IMG_DELAY_RENDER_RETRIES = 3;
const IMG_MAX_RETRIES = 5;

export const SourcedBackground: React.FC<{ beat: BeatJson }> = ({ beat }) => {
  if (beat.background_asset_url) {
    return (
      <AbsoluteFill>
        <Img
          src={beat.background_asset_url}
          delayRenderRetries={IMG_DELAY_RENDER_RETRIES}
          delayRenderTimeoutInMilliseconds={IMG_DELAY_RENDER_TIMEOUT_MS}
          maxRetries={IMG_MAX_RETRIES}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    );
  }

  const reason = beat.background_sourcing_status ?? "no sourcing attempted";
  return <GradeTestBackground label={`${beat.beat_id} -- PLACEHOLDER (${reason})`} />;
};
