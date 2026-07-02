import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { DuotoneGrade } from "../primitives/DuotoneGrade";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import type { BeatJson } from "./shotBrief";

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

  const progress = interpolate(frame, [0, Math.max(beat.duration_frames - 1, 1)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
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
    </div>
  );
};
