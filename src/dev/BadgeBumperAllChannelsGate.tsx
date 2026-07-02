import React from "react";
import { AbsoluteFill } from "remotion";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { CHANNELS, ChannelId } from "../constants/channels";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_SPACE_GROTESK } from "../constants/fonts";

// 07_REVIEW_GATE_PROTOCOL.md Gate 1 requirement (distinct from
// BadgeBumperGate.tsx's tag-length test): "Rendered PNG of BadgeBumper for
// all 6 channel colors, side by side" -- a single frame, not a sequence.
const CHANNEL_IDS = Object.keys(CHANNELS) as ChannelId[];
const ROW_HEIGHT = CANVAS_HEIGHT / CHANNEL_IDS.length;

export const BadgeBumperAllChannelsGate: React.FC = () => {
  return (
    <AbsoluteFill>
      <PlaceholderBackground label="BadgeBumper -- all 6 channel colors" />
      {CHANNEL_IDS.map((id, i) => (
        <div
          key={id}
          style={{
            position: "absolute",
            top: i * ROW_HEIGHT,
            left: 0,
            width: CANVAS_WIDTH,
            height: ROW_HEIGHT,
          }}
        >
          <BadgeBumper tag={CHANNELS[id].badgeTag} accentColor={CHANNELS[id].accentColor} />
          <span
            style={{
              position: "absolute",
              left: 24,
              top: 70,
              fontFamily: FONT_SPACE_GROTESK,
              fontSize: 16,
              color: "rgba(255,255,255,0.5)",
            }}
          >
            {CHANNELS[id].accentColor}
          </span>
        </div>
      ))}
    </AbsoluteFill>
  );
};

export const badgeBumperAllChannelsGateDurationInFrames = 1;
