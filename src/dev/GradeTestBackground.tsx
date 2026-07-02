import React from "react";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_SPACE_GROTESK } from "../constants/fonts";

// Background used only for the DuotoneGrade gate render. The generic
// PlaceholderBackground is a near-black gradient, which barely shows a
// grading filter's effect (hue-rotate/sepia/contrast do little to near-black
// pixels). This one has actual midtone color content -- sky, foliage-green,
// warm ground, and a neutral gray strip -- so the 3 grade variants are
// visibly distinguishable in a still frame.
export const GradeTestBackground: React.FC<{ label: string }> = ({ label }) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: CANVAS_WIDTH,
        height: CANVAS_HEIGHT,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, #6ea8d8 0%, #a9c9dc 28%, #7c9e5c 46%, #4d6b34 64%, #8a6b45 82%, #3d2c1a 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "40%",
          height: 80,
          background:
            "linear-gradient(90deg, #202020 0%, #808080 25%, #d8d8d8 50%, #808080 75%, #202020 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 0,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT_SPACE_GROTESK,
          fontSize: 20,
          color: "rgba(255,255,255,0.7)",
          textShadow: "0 1px 4px rgba(0,0,0,0.6)",
        }}
      >
        {label}
      </div>
    </div>
  );
};
