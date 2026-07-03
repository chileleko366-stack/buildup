import React from "react";
import { AbsoluteFill } from "remotion";
import { BeatCompositor } from "../../BeatCompositor";
import { AmbientBackground } from "./AmbientBackground";
import { Starfield } from "./Starfield";
import { HardCutFlash } from "./HardCutFlash";
import { BadgeBumper } from "../../../primitives/BadgeBumper";
import { SourcedBackground } from "../../SourcedBackground";
import { CHANNELS } from "../../../constants/channels";
import { CHANNEL_CONFIGS } from "../../../pipeline/channelConfigs";
import type { ShotBriefJson, BeatJson } from "../../shotBrief";
import shotBriefData from "../../data/ch6-jupiter-red-spot-001.json";

// Ch6Composition -- Red Space Facts channel (ch6).
// Space Grotesk body / Anton accent / #000000 bg / #ff1744 accent1
// (colors sourced from src/pipeline/channelConfigs.ts).
//
// Layer stack, per the diff fragment this was reconstructed from (see
// AmbientBackground.tsx / Starfield.tsx / HardCutFlash.tsx / ShotBriefLayer.tsx
// for what's confirmed vs. new design work in each):
//   - ShotBriefLayer      (brief-driven background/Ken Burns/grading, per beat)
//   - Beat audio          NOT IMPLEMENTED -- no kokoro-onnx TTS in this
//                         session (no self-hosted model files exist yet,
//                         see CLAUDE.md); this render is silent.
//   - HardCutFlash        (orange accent flash) -- applied only at cascade
//                         beat starts, a scope decision made in this file,
//                         not specified anywhere
//   - BadgeBumper         static for the whole video, rendered once here,
//                         not per-beat, per 02_VISUAL_BIBLE.md §2
// Global: AmbientBackground + Starfield (deep space #000000, drifting
//   parallax stars -- one instance each for the whole video, NOT per-beat,
//   or they'd reset/jump at every hard cut).
//
// Phase 2 wiring (this pass): renderBackground now uses SourcedBackground,
// which uses each beat's REAL resolved NASA asset (background_asset_url,
// written by pipeline/ch6_short_001.py via footage_sourcing/resolve.py)
// when one was accepted, and falls back to the same GradeTestBackground
// placeholder -- now labeled with the REAL reason -- when it wasn't. As
// of this render, this session's egress still denies images-api.nasa.gov
// (confirmed fresh, not assumed -- see CLAUDE.md's Phase 2 section), so
// every beat's background_asset_url is still null and every beat falls
// back to the labeled placeholder. The WIRING is real; the imagery still
// isn't, because no real NASA call has ever succeeded in this session.
const brief = shotBriefData as unknown as ShotBriefJson;

const renderBackground = (beat: BeatJson) => <SourcedBackground beat={beat} />;

const renderBeatOverlay = (beat: BeatJson) =>
  beat.cascade ? (
    <HardCutFlash startFrame={0} accentColor={CHANNEL_CONFIGS.CH6.colors.accent1} />
  ) : null;

export const Ch6Composition: React.FC = () => {
  return (
    <AbsoluteFill>
      <AmbientBackground />
      <Starfield />
      <BeatCompositor
        brief={brief}
        renderBackground={renderBackground}
        renderBeatOverlay={renderBeatOverlay}
      />
      <BadgeBumper tag={CHANNELS.CH6.badgeTag} accentColor={CHANNELS.CH6.accentColor} />
    </AbsoluteFill>
  );
};

export { brief as ch6ShotBrief };
