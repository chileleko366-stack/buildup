import React, { useEffect } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { FONT_ANTON, FONT_SPACE_GROTESK } from "../constants/fonts";

// Injects @font-face rules for the self-hosted font files (see fonts.ts
// comment) and blocks rendering until they're loaded, mirroring what
// @remotion/google-fonts' loadFont().waitUntilDone() would otherwise do.
export const Fonts: React.FC = () => {
  useEffect(() => {
    const [handle] = [delayRender("Loading self-hosted fonts")];
    Promise.all([
      document.fonts.load(`400 64px "${FONT_ANTON}"`),
      document.fonts.load(`700 64px "${FONT_SPACE_GROTESK}"`),
    ])
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, []);

  return (
    <style>
      {`
        @font-face {
          font-family: '${FONT_ANTON}';
          src: url('${staticFile("fonts/Anton-Regular.woff2")}') format('woff2');
          font-weight: 400;
          font-style: normal;
          font-display: block;
        }
        @font-face {
          font-family: '${FONT_SPACE_GROTESK}';
          src: url('${staticFile("fonts/SpaceGrotesk-Variable.woff2")}') format('woff2');
          font-weight: 300 700;
          font-style: normal;
          font-display: block;
        }
      `}
    </style>
  );
};
