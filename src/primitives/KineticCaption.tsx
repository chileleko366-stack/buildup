import React from "react";
import { useCurrentFrame } from "remotion";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_ANTON } from "../constants/fonts";

// Spec: 02_VISUAL_BIBLE.md §4 ("normal-pace captions, unchanged mode") --
// this is the majority-mode caption system the bible says already exists
// ("existing kinetic reveal system") in the prior repo. That repo doesn't
// exist here (see CLAUDE.md "Repo status"), so this is a fresh design, not
// a confirmed prior implementation. Confirmed from the bible: per-word/
// phrase hold of 0.5-1s (12-24 frames @24fps). NOT confirmed, and decided
// here: words accumulate into the full sentence rather than swapping
// (WordCascade already covers the swap-and-discard timing mode; this one
// needs to read as the "majority, easy to follow" mode by contrast) --
// and each new word HARD-APPEARS with no fade/scale-in, per
// 05_PACING_MOVEMENT_BIBLE.md §6's general rule against animated text
// entrances ("No spring/bounce easing on text entrances") applied beyond
// just WordCascade.
export type KineticCaptionProps = {
  text: string;
  startFrame: number;
  framesPerWord?: number; // 12-24 per spec (0.5-1s @24fps)
  canvasWidth?: number;
  canvasHeight?: number;
  anchorYRatio?: number; // 0 = top, 1 = bottom; defaults to vertical center
  color?: string;
};

export const kineticCaptionDuration = (text: string, framesPerWord = 18) =>
  text.trim().split(/\s+/).filter(Boolean).length * framesPerWord;

export const KineticCaption: React.FC<KineticCaptionProps> = ({
  text,
  startFrame,
  framesPerWord = 18,
  canvasWidth = CANVAS_WIDTH,
  canvasHeight = CANVAS_HEIGHT,
  anchorYRatio = 0.5,
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;
  const words = text.trim().split(/\s+/).filter(Boolean);
  const totalFrames = words.length * framesPerWord;

  if (localFrame < 0 || localFrame >= totalFrames || words.length === 0) {
    return null;
  }

  const scale = canvasWidth / CANVAS_WIDTH;
  const revealedCount = Math.min(Math.floor(localFrame / framesPerWord) + 1, words.length);
  const displayText = words.slice(0, revealedCount).join(" ");

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: canvasWidth,
        top: canvasHeight * anchorYRatio,
        transform: "translateY(-50%)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: `0 ${48 * scale}px`,
        zIndex: 50,
      }}
    >
      <span
        style={{
          fontFamily: FONT_ANTON,
          fontWeight: 400,
          fontSize: 40 * scale,
          color,
          textAlign: "center",
          lineHeight: 1.2,
          textShadow: "0 2px 10px rgba(0,0,0,0.5)",
        }}
      >
        {displayText}
      </span>
    </div>
  );
};
