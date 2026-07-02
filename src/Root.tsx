import "./index.css";
import { Composition } from "remotion";
import { CANVAS_WIDTH, CANVAS_HEIGHT, FPS } from "./constants/canvas";
import { Fonts } from "./dev/Fonts";
import { BadgeBumperGate, badgeBumperGateDurationInFrames } from "./dev/BadgeBumperGate";
import {
  BadgeBumperAllChannelsGate,
  badgeBumperAllChannelsGateDurationInFrames,
} from "./dev/BadgeBumperAllChannelsGate";
import { WordCascadeGate, wordCascadeGateDurationInFrames } from "./dev/WordCascadeGate";
import { DuotoneGradeGate, duotoneGradeGateDurationInFrames } from "./dev/DuotoneGradeGate";
import {
  DuotoneGradeSideBySideGate,
  duotoneGradeSideBySideGateDurationInFrames,
} from "./dev/DuotoneGradeSideBySideGate";
import { KineticCaptionGate, kineticCaptionGateDurationInFrames } from "./dev/KineticCaptionGate";
import { Ch6Composition, ch6ShotBrief } from "./remotion/channels/ch6/Ch6Composition";
import { totalDurationInFrames } from "./remotion/shotBrief";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Fonts />
      {/* Phase 1 gate renders -- one primitive per composition, isolated
          against a placeholder background, per master prompt §2 Phase 1. */}
      <Composition
        id="Gate-BadgeBumper"
        component={BadgeBumperGate}
        durationInFrames={badgeBumperGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      <Composition
        id="Gate-WordCascade"
        component={WordCascadeGate}
        durationInFrames={wordCascadeGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      <Composition
        id="Gate-DuotoneGrade"
        component={DuotoneGradeGate}
        durationInFrames={duotoneGradeGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* 07_REVIEW_GATE_PROTOCOL.md Gate 1 exact-spec renders (single-frame
          side-by-side comparisons, distinct from the sequential gates above). */}
      <Composition
        id="Gate-BadgeBumper-AllChannels"
        component={BadgeBumperAllChannelsGate}
        durationInFrames={badgeBumperAllChannelsGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      <Composition
        id="Gate-DuotoneGrade-SideBySide"
        component={DuotoneGradeSideBySideGate}
        durationInFrames={duotoneGradeSideBySideGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* Phase 3 addition: KineticCaption fills the 02_VISUAL_BIBLE.md §4
          gap (normal-pace captions, out of Phase 1 scope until now). */}
      <Composition
        id="Gate-KineticCaption"
        component={KineticCaptionGate}
        durationInFrames={kineticCaptionGateDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* Phase 3 gate: CH6 end-to-end short. See Ch6Composition.tsx's
          header comment for exactly what's real vs. placeholder (no real
          NASA imagery, no TTS audio, in this render). */}
      <Composition
        id="CH6-jupiter-red-spot-001"
        component={Ch6Composition}
        durationInFrames={totalDurationInFrames(ch6ShotBrief)}
        fps={ch6ShotBrief.fps}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
    </>
  );
};
