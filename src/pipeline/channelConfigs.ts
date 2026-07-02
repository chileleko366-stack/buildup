// Per-channel Remotion composition styling (fonts, palette, script tone,
// beat-type taxonomy) for the per-channel render architecture referenced by
// a diff the user provided against files that don't otherwise exist in this
// repo (src/pipeline/channelConfigs.ts, src/remotion/channels/ch{2,4,6}/*).
// This file is reconstructed FROM that diff's confirmed data (it shows both
// the before and after value of every color field for all 6 channels,
// which is real, quoted data, not invention) -- built directly to the
// diff's final ("+") state rather than an intermediate pre-diff state.
//
// NOT confirmed by anything available to this session, and deliberately
// left out rather than invented: any fields on ChannelConfig beyond what
// the diff's hunks actually showed (the diff's context window starts at
// `bodyFont:`, so fields possibly above that in the real object literal --
// e.g. an id/name/description -- are unknown). Callers needing channel
// name/badge/accent-for-the-badge should use `CHANNELS` in
// `src/constants/channels.ts` (Visual Bible §2's badge-specific accent
// color, which is fixed and separate from this file's broader `accent1`/
// `accent2` composition palette -- they're allowed to differ, and several
// channels' accent1 here do differ from their badge color).
import type { ChannelId } from "../constants/channels";

export type BeatType = string;

export type ChannelConfig = {
  bodyFont: string;
  accentFont: string;
  colors: {
    bgPrimary: string;
    accent1: string;
    accent2: string;
    text: string;
    textMuted: string;
  };
  scriptTone: string;
  beatTypes: BeatType[];
};

export const CHANNEL_CONFIGS: Record<ChannelId, ChannelConfig> = {
  CH1: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#000000",
      accent1: "#d400ff",
      accent2: "#00f0ff",
      text: "#ffffff",
      textMuted: "rgba(255,255,255,0.6)",
    },
    scriptTone: "punchy, direct, mind-bending",
    beatTypes: ["person", "stat", "none"],
  },
  CH2: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#ffffff",
      accent1: "#00c853",
      accent2: "#d50000",
      text: "#0a0e1a",
      textMuted: "rgba(10,14,26,0.6)",
    },
    scriptTone: "analytical, shocking, authoritative",
    beatTypes: ["brand", "stat", "person"],
  },
  CH3: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#000000",
      accent1: "#cc0000",
      accent2: "#1a1305",
      text: "#e8e0cc",
      textMuted: "rgba(232,224,204,0.6)",
    },
    scriptTone: "conspiratorial, terse, urgent",
    beatTypes: ["person", "place", "none"],
  },
  CH4: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#ffffff",
      accent1: "#0097a7",
      accent2: "#5e35b1",
      text: "#0d1117",
      textMuted: "rgba(13,17,23,0.6)",
    },
    scriptTone: "scientific, vivid, revelatory",
    beatTypes: ["anatomy", "person", "stat"],
  },
  CH5: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#ffffff",
      accent1: "#6b4c1e",
      accent2: "#3d2b0d",
      text: "#1a1510",
      textMuted: "rgba(26,21,16,0.6)",
    },
    scriptTone: "measured, evocative, archival",
    beatTypes: ["person", "place", "none"],
  },
  CH6: {
    bodyFont: "'Space Grotesk', sans-serif",
    accentFont: "'Anton', sans-serif",
    colors: {
      bgPrimary: "#000000",
      accent1: "#ff1744",
      accent2: "#00e5ff",
      text: "#ffffff",
      textMuted: "rgba(255,255,255,0.6)",
    },
    scriptTone: "awe-inspiring, precise, cosmic",
    beatTypes: ["celestial", "stat", "distance"],
  },
};
