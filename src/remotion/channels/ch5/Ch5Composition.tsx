import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch5-wasp-pilots-001.json";

// CH5 (The Quiet Record) -- see GenericChannelShort.tsx for what's shared
// vs. channel-specific, and pipeline/channel_scripts.py for this short's
// hand-authored script (not LLM output -- no LLM provider key configured).
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch5Composition: React.FC = () => (
  <GenericChannelShort channelKey="CH5" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch5ShotBrief = brief;
export const ch5DurationInFrames = totalDurationInFrames(brief);
