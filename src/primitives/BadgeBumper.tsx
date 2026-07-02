import React from "react";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants/canvas";
import { FONT_SPACE_GROTESK } from "../constants/fonts";

// Spec: 02_VISUAL_BIBLE.md §2
// - Solid color rectangle, top-left corner, fixed position for the entire video
// - ~24px from left, 24px from top at 720x1280; scales proportionally at other canvas sizes
// - Bold white text, no icon, 3-4 char tag
// - Never animates, never disappears, never changes position mid-video
// - Always the topmost layer (§8 layering order)
export type BadgeBumperProps = {
  tag: string;
  accentColor: string;
  canvasWidth?: number;
  canvasHeight?: number;
};

export const BadgeBumper: React.FC<BadgeBumperProps> = ({
  tag,
  accentColor,
  canvasWidth = CANVAS_WIDTH,
  canvasHeight = CANVAS_HEIGHT,
}) => {
  const scale = canvasWidth / CANVAS_WIDTH;
  const inset = 24 * scale;
  const paddingX = 14 * scale;
  const paddingY = 8 * scale;
  const fontSize = 22 * scale;

  return (
    <div
      style={{
        position: "absolute",
        left: inset,
        top: inset,
        paddingLeft: paddingX,
        paddingRight: paddingX,
        paddingTop: paddingY,
        paddingBottom: paddingY,
        backgroundColor: accentColor,
        zIndex: 100,
      }}
    >
      <span
        style={{
          fontFamily: FONT_SPACE_GROTESK,
          fontWeight: 700,
          fontSize,
          color: "#ffffff",
          letterSpacing: 1,
          lineHeight: 1,
          whiteSpace: "nowrap",
        }}
      >
        {tag}
      </span>
    </div>
  );
};
