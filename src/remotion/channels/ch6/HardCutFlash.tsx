import React from "react";
import { useCurrentFrame } from "remotion";

// NOT specified in any bible available to this session. Reconstructed only
// from a diff fragment's file-header comment naming a component
// "HardCutFlash (orange accent flash)" for CH6, with no implementation
// shown. This is new design work, not a confirmed spec -- revisit if a
// real spec ever surfaces.
//
// Design: a brief, hard-edged flash of the channel's accent color,
// triggered at a beat's start and gone within a handful of frames -- no
// fade-in, no easing -- to stay consistent with 05_PACING_MOVEMENT_BIBLE.md
// §6's "no crossfades, ever" / "no spring/bounce easing" rules. It's an
// opacity step function (on for N frames, then off), not a smooth
// transition. Callers (BeatCompositor) decide which beat boundaries get
// this -- this component doesn't know or enforce frequency.
export type HardCutFlashProps = {
  startFrame: number;
  accentColor: string;
  flashFrames?: number; // how many frames it stays visible before hard-cutting to gone
  opacity?: number;
};

export const HardCutFlash: React.FC<HardCutFlashProps> = ({
  startFrame,
  accentColor,
  flashFrames = 2,
  opacity = 0.35,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  if (localFrame < 0 || localFrame >= flashFrames) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: accentColor,
        opacity,
        zIndex: 40,
      }}
    />
  );
};
