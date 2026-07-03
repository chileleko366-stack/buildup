import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch4-fear-response-001.json";

// CH4 (The Grey Matter) -- see GenericChannelShort.tsx for what's shared
// vs. channel-specific, and pipeline/channel_scripts.py for this short's
// hand-authored script (not LLM output -- no LLM provider key configured).
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch4Composition: React.FC = () => (
  <GenericChannelShort channelKey="CH4" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch4ShotBrief = brief;
export const ch4DurationInFrames = totalDurationInFrames(brief);
