import "./index.css";
import { Composition } from "remotion";
import { CANVAS_WIDTH, CANVAS_HEIGHT, FPS } from "./constants/canvas";
import { Fonts } from "./dev/Fonts";
import { BadgeBumperGate, badgeBumperGateDurationInFrames } from "./dev/BadgeBumperGate";
import { WordCascadeGate, wordCascadeGateDurationInFrames } from "./dev/WordCascadeGate";
import { DuotoneGradeGate, duotoneGradeGateDurationInFrames } from "./dev/DuotoneGradeGate";

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
    </>
  );
};
