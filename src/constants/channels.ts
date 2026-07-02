// Per-channel names, badge tags, and accent colors, per 02_VISUAL_BIBLE.md
// §2 (revised): badge tags are the channel's own on-screen abbreviation,
// never a generic "CH1".."CH6" slot label. `CH1`.."CH6" here are just this
// codebase's internal channel IDs (matches YT_CH{n} secret naming per the
// bible's own note that the two are unrelated) -- never render `id` on
// screen, only `badgeTag`.
// No channel config JSON exists in this (greenfield) repo, so this table is
// the bible's own "working assumption, not the final source of truth" --
// re-confirm against a real channel config JSON once one exists.
export type ChannelId = "CH1" | "CH2" | "CH3" | "CH4" | "CH5" | "CH6";

export const CHANNELS: Record<
  ChannelId,
  { name: string; accentColor: string; badgeTag: string }
> = {
  CH1: { name: "Dopamine Loop", accentColor: "#d400ff", badgeTag: "DPL" },
  CH2: { name: "FinanceFiction", accentColor: "#00ff88", badgeTag: "FNF" },
  CH3: { name: "Redacted", accentColor: "#cc0000", badgeTag: "RED" },
  CH4: { name: "The Grey Matter", accentColor: "#0097a7", badgeTag: "TGM" },
  CH5: { name: "The Quiet Record", accentColor: "#c8a96e", badgeTag: "TQR" },
  // "RSF" vs the channel's existing "@RedFACTS.I" on-screen handle was
  // explicitly flagged as unconfirmed by the bible; user confirmed
  // @RedFACTS.I is correct (2026-07-02).
  CH6: { name: "Red Space Facts", accentColor: "#ff4500", badgeTag: "@RedFACTS.I" },
};
