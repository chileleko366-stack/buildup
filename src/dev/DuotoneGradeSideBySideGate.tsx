import React from "react";
import { AbsoluteFill } from "remotion";
import { DuotoneGrade, DuotoneVariant } from "../primitives/DuotoneGrade";
import { GradeTestBackground } from "./GradeTestBackground";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";

// 07_REVIEW_GATE_PROTOCOL.md Gate 1 requirement: "same background image
// with neutral / teal-archival / warm-sepia grading applied, side by side"
// -- a single frame, not DuotoneGradeGate.tsx's sequential-in-time version.
const VARIANTS: DuotoneVariant[] = ["neutral", "teal-archival", "warm-sepia"];
const PANEL_WIDTH = CANVAS_WIDTH / VARIANTS.length;

export const DuotoneGradeSideBySideGate: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {VARIANTS.map((variant, i) => (
        <div
          key={variant}
          style={{
            position: "absolute",
            left: i * PANEL_WIDTH,
            top: 0,
            width: PANEL_WIDTH,
            height: CANVAS_HEIGHT,
            overflow: "hidden",
          }}
        >
          {/* Same full-height center crop of the same background image in
              every panel (not scaled-to-fit, which would letterbox a 9:16
              image into a ~3:16 panel and waste 2/3 of the frame) -- so
              each panel is a true apples-to-apples comparison at full
              vertical resolution, just graded differently. */}
          <div
            style={{
              position: "absolute",
              left: -(CANVAS_WIDTH - PANEL_WIDTH) / 2,
              top: 0,
              width: CANVAS_WIDTH,
              height: CANVAS_HEIGHT,
            }}
          >
            <DuotoneGrade variant={variant}>
              <GradeTestBackground label={variant} />
            </DuotoneGrade>
          </div>
        </div>
      ))}
    </AbsoluteFill>
  );
};

export const duotoneGradeSideBySideGateDurationInFrames = 1;
