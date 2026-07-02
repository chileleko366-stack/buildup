import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { KineticCaption } from "../primitives/KineticCaption";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { CHANNELS } from "../constants/channels";
import { FONT_SPACE_GROTESK } from "../constants/fonts";
import moneyDemoData from "../remotion/data/ch2-money-sfx-demo.json";

// Proof of concept: keyword-triggered SFX firing on real per-word
// timestamps ("$", "worth", "billions" all match MONEY per
// pipeline/audio/sfx_triggers.py), mixed into the real TTS audio via
// pipeline/render_audio_demo.py (ducked under a placeholder music bed,
// two-pass loudnorm mastered). The SFX sounds themselves are synthesized
// placeholder tones, NOT real SFX -- see sfx_triggers.py's module
// docstring for why (no SFX asset library exists in this repo).
// A small on-screen marker shows which category fired and when, purely
// so this is reviewable without needing to precisely ear-match audio to
// captions.
const data = moneyDemoData as {
  text: string;
  wordTimings: { word: string; startFrame: number }[];
  audioEndFrame: number;
  audioFile: string;
  triggers: { category: string; word: string; frame: number; flavor: string }[];
};

export const ch2MoneySfxDemoDurationInFrames = data.audioEndFrame + 24;

const SfxMarkers: React.FC = () => {
  const frame = useCurrentFrame();
  const active = data.triggers.find((t) => frame >= t.frame && frame < t.frame + 12);
  if (!active) return null;
  return (
    <div
      style={{
        position: "absolute",
        top: "70%",
        left: 0,
        width: "100%",
        textAlign: "center",
        fontFamily: FONT_SPACE_GROTESK,
        fontSize: 22,
        fontWeight: 700,
        color: CHANNELS.CH2.accentColor,
        textShadow: "0 2px 8px rgba(0,0,0,0.8)",
      }}
    >
      ♪ SFX: {active.category} (placeholder tone, not real SFX)
    </div>
  );
};

export const Ch2MoneySfxDemoGate: React.FC = () => {
  return (
    <AbsoluteFill>
      <PlaceholderBackground label="CH2 -- keyword-SFX proof of concept" />
      <Audio src={staticFile(data.audioFile)} />
      <KineticCaption text={data.text} startFrame={0} wordTimings={data.wordTimings} />
      <SfxMarkers />
      <BadgeBumper tag={CHANNELS.CH2.badgeTag} accentColor={CHANNELS.CH2.accentColor} />
    </AbsoluteFill>
  );
};
