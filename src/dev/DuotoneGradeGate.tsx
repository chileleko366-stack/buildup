import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { DuotoneGrade, DuotoneVariant } from "../primitives/DuotoneGrade";
import { GradeTestBackground } from "./GradeTestBackground";
import { FPS } from "../constants/canvas";

// Gate render: all 3 DuotoneGrade variants against the same placeholder
// background so they can be visually compared side by side (in sequence).
// NOTE: per DuotoneGrade.tsx comment, these filter values are unverified
// against the actual blueprint frames (not available in this session).
const SEGMENT_FRAMES = FPS * 2;

const VARIANTS: DuotoneVariant[] = ["neutral", "teal-archival", "warm-sepia"];

export const DuotoneGradeGate: React.FC = () => {
  return (
    <AbsoluteFill>
      {VARIANTS.map((variant, i) => (
        <Sequence key={variant} from={i * SEGMENT_FRAMES} durationInFrames={SEGMENT_FRAMES}>
          <AbsoluteFill>
            <DuotoneGrade variant={variant}>
              <GradeTestBackground label={`variant: ${variant}`} />
            </DuotoneGrade>
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const duotoneGradeGateDurationInFrames = SEGMENT_FRAMES * VARIANTS.length;
