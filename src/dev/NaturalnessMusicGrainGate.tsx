import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { WordCascade } from "../primitives/WordCascade";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { DuotoneGrade } from "../primitives/DuotoneGrade";
import { FilmGrain } from "../primitives/FilmGrain";
import { GradeTestBackground } from "./GradeTestBackground";
import { CHANNELS } from "../constants/channels";
import naturalnessData from "../remotion/data/ch6-cascade-1-naturalness-music.json";

// Same cascade-1 CH6 beat as Gate-Cascade1-RealTTS / Gate-Cascade1-FullChain,
// now with all 3 of this pass's real fixes applied together:
//   1. Voiceover naturalness -- espeak PITCH/RANGE (voice_profiles.py) +
//      ffmpeg acompressor de-robotify pass (mix.py, sourced from
//      nodeblackbox/Kokoro-Voice-Api).
//   2. Music -- real CC0-1.0 CH6 track ("Alien Spaceship Atmosphere",
//      pipeline/audio/music.py), ducked under voice via the SAME
//      duck_music_under_voice() chain the placeholder-tone version used.
//   3. Texture -- FilmGrain.tsx (real @remotion/noise + sourced grain
//      technique, see that file's header) layered on top of DuotoneGrade,
//      per 02_VISUAL_BIBLE.md §8's grading-then-texture layering order.
// Background is GradeTestBackground (colorful placeholder), same choice
// CLAUDE.md documents for DuotoneGradeGate -- PlaceholderBackground is too
// dark/desaturated to show grading+grain differences. Grading variant is
// "neutral", matching what ch6-jupiter-red-spot-001.json actually uses for
// every beat (checked, not assumed).
const data = naturalnessData as {
  wordTimings: { word: string; startFrame: number }[];
  audioEndFrame: number;
  audioFile: string;
  voice_profile: { pitch: number; pitch_range: number };
};

export const naturalnessMusicGrainDurationInFrames = data.audioEndFrame + 18;

export const NaturalnessMusicGrainGate: React.FC = () => {
  const words = data.wordTimings.map((w) => w.word);

  return (
    <AbsoluteFill>
      <DuotoneGrade variant="neutral">
        <GradeTestBackground label="CH6 naturalness+music+grain gate" />
      </DuotoneGrade>
      <FilmGrain />
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
