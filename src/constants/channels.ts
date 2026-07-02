// Per-channel accent colors, confirmed from 02_VISUAL_BIBLE.md §2.
// No channel config JSON exists in this (greenfield) repo, so badge tags
// default to "CH1".."CH6" per the bible's fallback rule. Niches for CH3
// (Redacted) and CH6 (Red Space Facts) are named in the master prompt
// Phase 3 section; CH1/CH2/CH4/CH5 niches are not specified anywhere
// provided to this session and are left unset rather than invented.
export type ChannelId = "CH1" | "CH2" | "CH3" | "CH4" | "CH5" | "CH6";

export const CHANNELS: Record<ChannelId, { accentColor: string; badgeTag: string }> = {
  CH1: { accentColor: "#d400ff", badgeTag: "CH1" },
  CH2: { accentColor: "#00ff88", badgeTag: "CH2" },
  CH3: { accentColor: "#cc0000", badgeTag: "CH3" },
  CH4: { accentColor: "#0097a7", badgeTag: "CH4" },
  CH5: { accentColor: "#c8a96e", badgeTag: "CH5" },
  CH6: { accentColor: "#ff4500", badgeTag: "CH6" },
};
