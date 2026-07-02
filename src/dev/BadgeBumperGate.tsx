import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { CHANNELS } from "../constants/channels";
import { FPS } from "../constants/canvas";

// Gate render: BadgeBumper at 3 different tag text lengths, held across a
// duration each, to confirm fixed position / non-animation per spec.
const SEGMENT_FRAMES = FPS * 2; // 2s each

const SEGMENTS: { tag: string; accentColor: string; label: string }[] = [
  { tag: "CH", accentColor: CHANNELS.CH2.accentColor, label: "2-char tag" },
  { tag: CHANNELS.CH1.badgeTag, accentColor: CHANNELS.CH1.accentColor, label: "3-char tag (DPL)" },
  { tag: "REDX", accentColor: CHANNELS.CH3.accentColor, label: "4-char tag" },
  {
    tag: CHANNELS.CH6.badgeTag,
    accentColor: CHANNELS.CH6.accentColor,
    label: "long handle tag (CH6, confirmed exception to 3-4 char rule)",
  },
];

export const BadgeBumperGate: React.FC = () => {
  return (
    <AbsoluteFill>
      {SEGMENTS.map((seg, i) => (
        <Sequence key={seg.tag} from={i * SEGMENT_FRAMES} durationInFrames={SEGMENT_FRAMES}>
          <AbsoluteFill>
            <PlaceholderBackground label={seg.label} />
            <BadgeBumper tag={seg.tag} accentColor={seg.accentColor} />
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const badgeBumperGateDurationInFrames = SEGMENT_FRAMES * SEGMENTS.length;
