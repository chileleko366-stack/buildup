import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { WordCascade, wordCascadeDuration } from "../primitives/WordCascade";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { FPS } from "../constants/canvas";

// Gate render: WordCascade at 3 different word-list lengths (short/medium/long)
// to confirm 4-6 frame per-word hold, hard cuts, and the final-phrase hold.
const PAD_FRAMES = FPS; // 1s padding before/after each cascade so the hard cuts read clearly

const CASES: { words: string[]; label: string }[] = [
  { words: ["NEVER", "TOLD", "YOU"], label: "3 words" },
  { words: ["THE", "TRUTH", "THEY", "BURIED", "FOREVER"], label: "5 words" },
  { words: ["NASA", "FOUND", "SOMETHING", "NO", "ONE", "CAN", "EXPLAIN", "YET"], label: "8 words" },
];

const buildSegments = () => {
  let cursor = 0;
  return CASES.map((c) => {
    const dur = wordCascadeDuration(c.words.length) + PAD_FRAMES * 2;
    const seg = { ...c, from: cursor, durationInFrames: dur, cascadeStart: cursor + PAD_FRAMES };
    cursor += dur;
    return seg;
  });
};

const SEGMENTS = buildSegments();

export const WordCascadeGate: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {SEGMENTS.map((seg) => (
        <Sequence key={seg.label} from={seg.from} durationInFrames={seg.durationInFrames}>
          <AbsoluteFill>
            <PlaceholderBackground label={seg.label} />
            <WordCascade words={seg.words} startFrame={PAD_FRAMES} />
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const wordCascadeGateDurationInFrames = SEGMENTS.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);
