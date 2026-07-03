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
export const SourcedBackground: React.FC<{ beat: BeatJson }> = ({ beat }) => {
  if (beat.background_asset_url) {
    return (
      <AbsoluteFill>
        <Img
          src={beat.background_asset_url}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    );
  }

  const reason = beat.background_sourcing_status ?? "no sourcing attempted";
  return <GradeTestBackground label={`${beat.beat_id} -- PLACEHOLDER (${reason})`} />;
};
