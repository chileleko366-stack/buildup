import React from "react";
import { useCurrentFrame } from "remotion";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../../../constants/canvas";

// NOT specified in any bible available to this session. Reconstructed only
// from a diff fragment's comment: "AmbientBackground + Starfield (deep
// space ..., drifting parallax stars -- one instance each for the whole
// video ... NOT per-beat, or they'd be nested inside BeatCompositor's
// TransitionSeries.Sequence and visibly [cut/reset each beat]." No
// implementation was shown. This is new design work.
//
// Design: two star layers at different (fixed) sizes/speeds for a basic
// parallax effect, drifting continuously for the whole video's duration
// (not reset per-beat, matching the diff comment's own stated reason for
// keeping this a single global instance). Positions are seeded
// deterministically (a plain LCG, not Math.random()) so every frame render
// is reproducible -- required for Remotion's frame-independent rendering
// model.
export type StarfieldProps = {
  starCount?: number;
  canvasWidth?: number;
  canvasHeight?: number;
};

function seededRandom(seed: number): () => number {
  let state = seed;
  return () => {
    state = (state * 1103515245 + 12345) & 0x7fffffff;
    return state / 0x7fffffff;
  };
}

type Star = { x: number; y: number; size: number; layer: 0 | 1 };

const makeStars = (count: number, canvasWidth: number, canvasHeight: number): Star[] => {
  const rand = seededRandom(42);
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    stars.push({
      x: rand() * canvasWidth,
      y: rand() * canvasHeight,
      size: rand() < 0.85 ? 1 : 2,
      layer: rand() < 0.7 ? 0 : 1,
    });
  }
  return stars;
};

const LAYER_SPEED = [0.15, 0.4]; // px/frame, back layer drifts slower than front layer

export const Starfield: React.FC<StarfieldProps> = ({
  starCount = 180,
  canvasWidth = CANVAS_WIDTH,
  canvasHeight = CANVAS_HEIGHT,
}) => {
  const frame = useCurrentFrame();
  const stars = React.useMemo(() => makeStars(starCount, canvasWidth, canvasHeight), [starCount, canvasWidth, canvasHeight]);

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      {stars.map((star, i) => {
        const drift = frame * LAYER_SPEED[star.layer];
        const y = ((star.y + drift) % canvasHeight + canvasHeight) % canvasHeight;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: star.x,
              top: y,
              width: star.size,
              height: star.size,
              borderRadius: "50%",
              backgroundColor: "#ffffff",
              opacity: star.layer === 0 ? 0.5 : 0.9,
            }}
          />
        );
      })}
    </div>
  );
};
