import React from "react";
import { useCurrentFrame } from "remotion";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_ANTON } from "../constants/fonts";

// Spec: 02_VISUAL_BIBLE.md §3
// - Rapid word-flash, used only at hook/tension/stat-reveal moments (3x in the
//   86s blueprint) -- this component is the timing MODE, callers decide when
//   to use it, this primitive doesn't enforce frequency.
// - Per-word hold: 4-6 frames at 24fps
// - Hard cut, zero fade/overlap between words; one word visible at a time
// - Words do not accumulate
// - After the final word, hold the complete phrase for 12-24 frames
// - Font/weight/color: same as normal caption system (bold condensed sans,
//   white) -- using Anton, the confirmed bold condensed display face
// - Position: centered, vertical anchor should come from
//   brief.composition.primaryAnchor once shot_brief.py exists (it doesn't
//   yet in this greenfield repo) -- exposed here as `anchorYRatio` prop so
//   callers can wire that field in later without changing this component.
//
// Timing source: 05_PACING_MOVEMENT_BIBLE.md §5 -- "WordCascade word timing
// should be driven by the actual TTS word-level timestamps ... if not
// available, the fixed 4-6 frame hold ... is the fallback." `wordTimings`
// (per-word start frame, derived from real TTS output) is that real path;
// omitting it keeps the original fixed-clock fallback behavior unchanged.
export type WordTiming = {
  word: string;
  startFrame: number; // relative to this component's `startFrame` prop
};

export type WordCascadeProps = {
  words: string[];
  startFrame: number;
  framesPerWord?: number; // 4-6 per spec -- ignored if wordTimings is provided
  finalHoldFrames?: number; // 12-24 per spec
  canvasWidth?: number;
  canvasHeight?: number;
  anchorYRatio?: number; // 0 = top, 1 = bottom; defaults to vertical center
  color?: string;
  /** Real per-word start frames (e.g. from TTS word-boundary timestamps).
   * When provided, overrides the fixed framesPerWord clock. Must be the
   * same length as `words`, in the same order, non-decreasing. */
  wordTimings?: WordTiming[];
  /** Required alongside wordTimings: the frame (relative to startFrame) at
   * which the last word's audio finishes -- i.e. when to switch from
   * "show the last word alone" to "hold the complete phrase." Without
   * this there's no way to know how long the last word's own audio lasts
   * (word start timestamps alone only bound word N's duration by word
   * N+1's start, which doesn't exist for the final word). */
  audioEndFrame?: number;
};

export const wordCascadeDuration = (
  wordCount: number,
  framesPerWord = 5,
  finalHoldFrames = 18,
) => wordCount * framesPerWord + finalHoldFrames;

export const wordCascadeDurationFromTimings = (
  audioEndFrame: number,
  finalHoldFrames = 18,
) => audioEndFrame + finalHoldFrames;

export const WordCascade: React.FC<WordCascadeProps> = ({
  words,
  startFrame,
  framesPerWord = 5,
  finalHoldFrames = 18,
  canvasWidth = CANVAS_WIDTH,
  canvasHeight = CANVAS_HEIGHT,
  anchorYRatio = 0.5,
  color = "#ffffff",
  wordTimings,
  audioEndFrame,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  const usingRealTimings = wordTimings !== undefined && audioEndFrame !== undefined;

  const cascadeFrames = usingRealTimings ? audioEndFrame! : words.length * framesPerWord;
  const totalFrames = cascadeFrames + finalHoldFrames;

  if (localFrame < 0 || localFrame >= totalFrames || words.length === 0) {
    return null;
  }

  const scale = canvasWidth / CANVAS_WIDTH;
  const isFinalHold = localFrame >= cascadeFrames;

  let wordIndex: number;
  if (usingRealTimings) {
    // Find the last word whose real start frame has passed.
    wordIndex = 0;
    for (let i = 0; i < wordTimings!.length; i++) {
      if (wordTimings![i].startFrame <= localFrame) {
        wordIndex = i;
      } else {
        break;
      }
    }
  } else {
    wordIndex = isFinalHold
      ? words.length - 1
      : Math.min(Math.floor(localFrame / framesPerWord), words.length - 1);
  }

  const displayText = isFinalHold ? words.join(" ") : words[wordIndex];

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
        padding: `0 ${32 * scale}px`,
        zIndex: 50,
      }}
    >
      <span
        style={{
          fontFamily: FONT_ANTON,
          fontWeight: 400,
          fontSize: 64 * scale,
          color,
          textAlign: "center",
          textTransform: "uppercase",
          lineHeight: 1.05,
          textShadow: "0 2px 12px rgba(0,0,0,0.5)",
        }}
      >
        {displayText}
      </span>
    </div>
  );
};
