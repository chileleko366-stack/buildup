import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { KineticCaption, kineticCaptionDuration } from "../primitives/KineticCaption";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { FPS } from "../constants/canvas";

// Gate render: KineticCaption at 3 different sentence lengths, to confirm
// the 0.5-1s per-word accumulation reads clearly and wraps sensibly.
const PAD_FRAMES = FPS / 2;

const CASES: { text: string; label: string }[] = [
  { text: "Jupiter spins faster than any other planet.", label: "short sentence" },
  {
    text: "Beneath the clouds, pressure crushes hydrogen into a strange metallic liquid.",
    label: "medium sentence",
  },
  {
    text: "Scientists have tracked the Great Red Spot shrinking for over a century of continuous observation.",
    label: "long sentence",
  },
];

const buildSegments = () => {
  let cursor = 0;
  return CASES.map((c) => {
    const dur = kineticCaptionDuration(c.text) + PAD_FRAMES * 2;
    const seg = { ...c, from: cursor, durationInFrames: dur, captionStart: PAD_FRAMES };
    cursor += dur;
    return seg;
  });
};

const SEGMENTS = buildSegments();

export const KineticCaptionGate: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {SEGMENTS.map((seg) => (
        <Sequence key={seg.label} from={seg.from} durationInFrames={seg.durationInFrames}>
          <AbsoluteFill>
            <PlaceholderBackground label={seg.label} />
            <KineticCaption text={seg.text} startFrame={seg.captionStart} />
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const kineticCaptionGateDurationInFrames = SEGMENTS.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);
