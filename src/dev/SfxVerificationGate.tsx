import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { KineticCaption } from "../primitives/KineticCaption";
import { BadgeBumper } from "../primitives/BadgeBumper";
import { PlaceholderBackground } from "./PlaceholderBackground";
import { CHANNELS, ChannelId } from "../constants/channels";
import { FONT_SPACE_GROTESK } from "../constants/fonts";
import sfxVerificationData from "../remotion/data/sfx-verification.json";

// 6-channel SFX verification gate: one Composition per channel below,
// all sharing this component via defaultProps (channelKey), rather than
// 6 near-duplicate files. Beats are real content from
// pipeline/footage_sourcing/sample_beats.py / pipeline/ch6_short_001.py
// (see pipeline/audio/sfx_triggers.py's module docstring for what's
// confirmed-real vs. proposed per channel). Placeholder tones only -- see
// same docstring for why.
type VerificationEntry = {
  text: string;
  wordTimings: { word: string; startFrame: number }[];
  audioEndFrame: number;
  audioFile: string;
  triggers: { category: string; word: string; frame: number }[];
  expectedCategory: string;
  pass: boolean;
};

const DATA = sfxVerificationData as Record<string, VerificationEntry>;

export type SfxVerificationGateProps = { channelKey: ChannelId };

export const sfxVerificationDurationInFrames = (channelKey: ChannelId) => DATA[channelKey].audioEndFrame + 24;

const TriggerMarker: React.FC<{ entry: VerificationEntry; accentColor: string }> = ({ entry, accentColor }) => {
  const frame = useCurrentFrame();
  const active = entry.triggers.find((t) => frame >= t.frame && frame < t.frame + 12);
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
        fontSize: 20,
        fontWeight: 700,
        color: accentColor,
        textShadow: "0 2px 8px rgba(0,0,0,0.8)",
      }}
    >
      ♪ SFX: {active.category} on "{active.word}" (placeholder, not real SFX)
    </div>
  );
};

export const SfxVerificationGate: React.FC<SfxVerificationGateProps> = ({ channelKey }) => {
  const entry = DATA[channelKey];
  const channel = CHANNELS[channelKey];

  return (
    <AbsoluteFill>
      <PlaceholderBackground
        label={`${channelKey} SFX verification -- expects ${entry.expectedCategory} -- ${entry.pass ? "PASS" : "FAIL"}`}
      />
      <Audio src={staticFile(entry.audioFile)} />
      <KineticCaption text={entry.text} startFrame={0} wordTimings={entry.wordTimings} />
      <TriggerMarker entry={entry} accentColor={channel.accentColor} />
      <BadgeBumper tag={channel.badgeTag} accentColor={channel.accentColor} />
    </AbsoluteFill>
  );
};
