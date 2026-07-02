import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { WordCascade } from "../primitives/WordCascade";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { AmbientBackground } from "../remotion/channels/ch6/AmbientBackground";
import { Starfield } from "../remotion/channels/ch6/Starfield";
import { CHANNELS } from "../constants/channels";
import realTtsData from "../remotion/data/ch6-cascade-1-real-tts.json";

// Real-TTS proof of concept for the CH6 "cascade-1" beat
// ("A storm that never stops"), replacing the pacing-bible placeholder
// duration/timing with REAL audio + REAL per-word timestamps from
// pipeline/tts/espeak_engine.py. NOT kokoro-onnx (blocked this session --
// see pipeline/tts/kokoro_engine.py) -- espeak-ng is an explicitly-labeled
// stand-in voice, used only to prove the real-timestamp-driven pipeline
// works end to end.
//
// Old (pacing-bible placeholder) duration for this beat: 43 frames (1.79s)
// New (real audio) duration: audioEndFrame(36) + finalHoldFrames(18) = 54
// frames (2.25s) -- LONGER than the placeholder in this case, not shorter;
// reported as measured, not adjusted to match any particular expectation.
const data = realTtsData as {
  wordTimings: { word: string; startFrame: number }[];
  audioEndFrame: number;
  audioFile: string;
};

export const cascade1RealTtsDurationInFrames = data.audioEndFrame + 18;

export const Cascade1RealTTSGate: React.FC = () => {
  const words = data.wordTimings.map((w) => w.word);

  return (
    <AbsoluteFill>
      <AmbientBackground />
      <Starfield />
      <Audio src={staticFile(data.audioFile)} />
      <WordCascade
        words={words}
        startFrame={0}
        wordTimings={data.wordTimings}
        audioEndFrame={data.audioEndFrame}
        anchorYRatio={0.5}
      />
      <BadgeBumper tag={CHANNELS.CH6.badgeTag} accentColor={CHANNELS.CH6.accentColor} />
    </AbsoluteFill>
  );
};
