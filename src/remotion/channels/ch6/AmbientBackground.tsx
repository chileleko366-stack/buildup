import React from "react";
import { CHANNEL_CONFIGS } from "../../../pipeline/channelConfigs";

// NOT specified in any bible available to this session -- see Starfield.tsx
// for the diff fragment this and Starfield were reconstructed from. Design:
// the deep-space base fill CH6's compositions sit on, using
// channelConfigs.ts's CH6.colors.bgPrimary rather than a hardcoded value so
// it stays in sync with that file if the palette changes.
export const AmbientBackground: React.FC = () => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: CHANNEL_CONFIGS.CH6.colors.bgPrimary,
      }}
    />
  );
};
