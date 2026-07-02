import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { WordCascade } from "../primitives/WordCascade";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { AmbientBackground } from "../remotion/channels/ch6/AmbientBackground";
import { Starfield } from "../remotion/channels/ch6/Starfield";
import { CHANNELS } from "../constants/channels";
import fullChainData from "../remotion/data/ch6-cascade-1-full-chain.json";

// Same cascade-1 beat as Gate-Cascade1-RealTTS, but with the audio now run
// through the full chain: sidechain-ducked under a synthetic placeholder
// music bed (NOT real music -- two detuned sine tones, see
// pipeline/render_audio_demo.py) and mastered with two-pass loudnorm.
// Sourced filter values: see pipeline/audio/mix.py's module docstring.
const data = fullChainData as {
  wordTimings: { word: string; startFrame: number }[];
  audioEndFrame: number;
  audioFile: string;
  loudness: {
    loudnorm_remeasure: { input_i_lufs: number; input_tp_dbtp: number; input_lra_lu: number };
    astats: { peak_level_db: string; rms_level_db: string };
  };
};

export const cascade1FullChainDurationInFrames = data.audioEndFrame + 18;

export const Cascade1FullChainGate: React.FC = () => {
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
