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
import { Cascade1RealTTSGate, cascade1RealTtsDurationInFrames } from "./dev/Cascade1RealTTSGate";
import { Cascade1FullChainGate, cascade1FullChainDurationInFrames } from "./dev/Cascade1FullChainGate";
import { Ch2MoneySfxDemoGate, ch2MoneySfxDemoDurationInFrames } from "./dev/Ch2MoneySfxDemoGate";
import { SfxVerificationGate, sfxVerificationDurationInFrames } from "./dev/SfxVerificationGate";
import type { ChannelId } from "./constants/channels";

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
      {/* Real-TTS proof of concept: cascade-1 beat with real espeak-ng
          audio + real per-word timestamps, replacing the pacing-bible
          placeholder duration/timing. See Cascade1RealTTSGate.tsx and
          pipeline/tts/ for what's real vs. blocked (kokoro-onnx itself). */}
      <Composition
        id="Gate-Cascade1-RealTTS"
        component={Cascade1RealTTSGate}
        durationInFrames={cascade1RealTtsDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* Full audio chain: same cascade-1 beat, now ducked under a
          placeholder music bed + two-pass loudnorm mastered. See
          pipeline/audio/mix.py for sourced filter values. */}
      <Composition
        id="Gate-Cascade1-FullChain"
        component={Cascade1FullChainGate}
        durationInFrames={cascade1FullChainDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* Keyword-triggered SFX proof of concept (real timestamps, real
          detection/priority logic, placeholder tones -- see
          pipeline/audio/sfx_triggers.py). */}
      <Composition
        id="Gate-Ch2-MoneySfxDemo"
        component={Ch2MoneySfxDemoGate}
        durationInFrames={ch2MoneySfxDemoDurationInFrames}
        fps={FPS}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
      />
      {/* 6-channel SFX verification: one real beat per channel (real text
          from sample_beats.py / ch6_short_001.py), one Composition per
          channel sharing SfxVerificationGate.tsx via defaultProps. See
          pipeline/render_sfx_verification.py for the pass/fail report. */}
      {(["CH1", "CH2", "CH3", "CH4", "CH5", "CH6"] as ChannelId[]).map((channelKey) => (
        <Composition
          key={channelKey}
          id={`Gate-SfxVerify-${channelKey}`}
          component={SfxVerificationGate}
          durationInFrames={sfxVerificationDurationInFrames(channelKey)}
          fps={FPS}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          defaultProps={{ channelKey }}
        />
      ))}
    </>
  );
};
