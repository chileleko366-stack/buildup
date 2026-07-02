import React from "react";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_SPACE_GROTESK } from "../constants/fonts";

// Not a spec'd primitive -- just a stand-in background for gate renders so
// primitives can be evaluated against something other than a flat void.
export const PlaceholderBackground: React.FC<{ label: string }> = ({ label }) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: CANVAS_WIDTH,
        height: CANVAS_HEIGHT,
        background: "linear-gradient(160deg, #3a3a3a 0%, #1a1a1a 60%, #050505 100%)",
        backgroundImage:
          "repeating-linear-gradient(45deg, rgba(255,255,255,0.04) 0px, rgba(255,255,255,0.04) 2px, transparent 2px, transparent 24px), linear-gradient(160deg, #3a3a3a 0%, #1a1a1a 60%, #050505 100%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 0,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT_SPACE_GROTESK,
          fontSize: 20,
          color: "rgba(255,255,255,0.35)",
        }}
      >
        {label}
      </div>
    </div>
  );
};
