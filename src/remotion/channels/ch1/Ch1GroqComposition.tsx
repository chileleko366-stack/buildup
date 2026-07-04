import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch1-groq-generated-001.json";

// Proof-of-concept composition for a REAL Groq-generated CH1 script (see
// pipeline/render_ch1_from_groq.py). Committed JSON here is a placeholder
// (a copy of the static CH1 short, relabeled) so this file's static
// import resolves before CI's generation step runs -- the real content is
// written fresh by `python3 -m pipeline.render_ch1_from_groq` before each
// render, exactly like every other channel's committed JSON is
// regenerated fresh per CI run (see CLAUDE.md's Phase 2 revisited note).
// Uses the same GenericChannelShort engine as CH1-CH5's static-script
// path -- no separate rendering logic for a generated script.
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch1GroqComposition: React.FC = () => (
  <GenericChannelShort channelKey="CH1" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch1GroqShotBrief = brief;
export const ch1GroqDurationInFrames = totalDurationInFrames(brief);
