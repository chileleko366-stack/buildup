import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { DuotoneGrade } from "../primitives/DuotoneGrade";
import { FilmGrain } from "../primitives/FilmGrain";
import { CANVAS_WIDTH, CANVAS_HEIGHT, FPS } from "../constants/canvas";
import type { BeatJson } from "./shotBrief";

// 02_VISUAL_BIBLE.md §7 / pipeline/shot_brief.py's own MAX_SHOT_SECONDS=4.0
// ("No shot ... exceeds ~4s"). Phase 4's real-TTS-driven beats can run much
// longer than that (a beat's duration_frames is now real audio length + a
// tail hold, not the pacing bible's placeholder range) -- capping the
// motion window to complete within 4s (then holding at zoom_end/full pan)
// stops the same total movement from looking proportionally slower on a
// beat several times longer than 4s.
const MAX_KEN_BURNS_FRAMES = 4 * FPS;

// Front-loaded ease-out: most of the push happens in the first half of the
// motion window, decelerating toward zoom_end/full pan, rather than a
// constant-rate drift across the whole window -- matches a "deliberate
// push" reference style rather than a linear pan. Cubic ease-out
// (1 - (1-t)^3) is a standard, well-documented easing curve, not an
// invented one; picked over ease-in-out because the requirement is
// specifically "most movement in the first half," which ease-in-out (which
// is front- AND back-loaded symmetrically) doesn't satisfy on its own.
const easeOutCubic = (t: number): number => 1 - Math.pow(1 - t, 3);

// NOT specified in any bible available to this session beyond fragments.
// Reconstructed from a diff comment naming "ShotBriefLayer (brief-driven
// primitive/positioning/depth for non-celestial beats)" for CH6, with no
// implementation shown. This build interprets that literally as "render
// this beat's background asset with brief-driven Ken Burns and grading" --
// the most defensible reading given the words "brief-driven" and
// "positioning" and what's already spec'd (Ken Burns per
// 05_PACING_MOVEMENT_BIBLE.md §3, grading per 02_VISUAL_BIBLE.md §5). The
// "for non-celestial beats" / "depth" parts of the diff's description
// aren't implemented -- no spec exists for what makes a beat "celestial"
// vs not at the component level, or what "depth" means beyond Ken Burns'
// zoom. This renders every beat uniformly; a future session with a real
// spec should revisit this.
//
// This session has no reachable image-source API (see
// pipeline/footage_sourcing/ CLAUDE.md notes) and no downloaded real asset
// for any beat, so `background` is always the caller-supplied placeholder
// element, never a real photo/image -- explicitly not claiming otherwise.
export type ShotBriefLayerProps = {
  beat: BeatJson;
  background: React.ReactNode;
  canvasWidth?: number;
  canvasHeight?: number;
};

export const ShotBriefLayer: React.FC<ShotBriefLayerProps> = ({
  beat,
  background,
  canvasWidth = CANVAS_WIDTH,
  canvasHeight = CANVAS_HEIGHT,
}) => {
  const frame = useCurrentFrame();
  const { zoom_start, zoom_end, pan_direction, pan_amount_ratio } = beat.ken_burns;

  const motionFrames = Math.min(beat.duration_frames, MAX_KEN_BURNS_FRAMES);
  const linearProgress = interpolate(frame, [0, Math.max(motionFrames - 1, 1)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const progress = easeOutCubic(linearProgress);
  const scale = zoom_start + (zoom_end - zoom_start) * progress;

  const panPx = pan_amount_ratio * canvasWidth * progress;
  let translateX = 0;
  let translateY = 0;
  if (pan_direction === "left") translateX = -panPx;
  else if (pan_direction === "right") translateX = panPx;
  else if (pan_direction === "up") translateY = -panPx;
  else if (pan_direction === "down") translateY = panPx;

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: "center center",
        }}
      >
        <DuotoneGrade variant={beat.grading}>{background}</DuotoneGrade>
      </div>
      {/* Grain sits on top of grading, not instead of it (see
          FilmGrain.tsx header), and stays inside this background-only
          wrapper -- BeatCompositor renders captions/BadgeBumper as later
          siblings, so DOM order alone keeps grain off text/badge without
          needing an explicit exclusion mask. */}
      <FilmGrain canvasWidth={canvasWidth} canvasHeight={canvasHeight} />
    </div>
  );
};
