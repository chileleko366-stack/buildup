import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch3-mkultra-001.json";

// CH3 (Redacted) -- see GenericChannelShort.tsx for what's shared vs.
// channel-specific, and pipeline/channel_scripts.py for this short's
// hand-authored script (not LLM output -- no LLM provider key configured).
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch3Composition: React.FC = () => (
  <GenericChannelShort channelKey="CH3" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch3ShotBrief = brief;
export const ch3DurationInFrames = totalDurationInFrames(brief);
