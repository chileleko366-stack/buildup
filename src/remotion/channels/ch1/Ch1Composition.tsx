import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch1-dopamine-loop-notifications-001.json";

// CH1 (Dopamine Loop) -- see GenericChannelShort.tsx for what's shared vs.
// channel-specific, and pipeline/channel_scripts.py for this short's
// hand-authored script (not LLM output -- no LLM provider key configured).
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch1Composition: React.FC = () => (
  <GenericChannelShort channelKey="CH1" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch1ShotBrief = brief;
export const ch1DurationInFrames = totalDurationInFrames(brief);
