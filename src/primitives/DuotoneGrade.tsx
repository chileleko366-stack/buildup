import React from "react";

// Spec: 02_VISUAL_BIBLE.md §5
// - 3 variants: neutral, teal-archival, warm-sepia
// - Applied to the background footage layer ONLY (§8 layering order), never
//   to text/badge
// - The filter values below are the bible's own "starting point, not a
//   locked number" -- the bible explicitly says to render and visually
//   compare against blueprint reference frames before treating them as
//   final. This session has no access to the blueprint video or its
//   extracted frames, so these values remain UNVERIFIED. Flagging per
//   ground rule #3 (fail loud, no silent "close enough").
export type DuotoneVariant = "neutral" | "teal-archival" | "warm-sepia";

const FILTERS: Record<DuotoneVariant, string> = {
  neutral: "contrast(1.05)",
  "teal-archival":
    "sepia(0.3) hue-rotate(140deg) saturate(1.4) contrast(1.15) brightness(0.85)",
  "warm-sepia": "sepia(0.45) saturate(1.2) contrast(1.05) brightness(1.05)",
};

export type DuotoneGradeProps = {
  variant: DuotoneVariant;
  children: React.ReactNode;
};

export const DuotoneGrade: React.FC<DuotoneGradeProps> = ({ variant, children }) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        filter: FILTERS[variant],
      }}
    >
      {children}
    </div>
  );
};
