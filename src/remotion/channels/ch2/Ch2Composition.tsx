import React from "react";
import { GenericChannelShort } from "../GenericChannelShort";
import { totalDurationInFrames } from "../../shotBrief";
import type { ShotBriefJson } from "../../shotBrief";
import shotBriefData from "../../data/ch2-lottery-winners-broke-001.json";

// CH2 (FinanceFiction) -- see GenericChannelShort.tsx for what's shared vs.
// channel-specific, and pipeline/channel_scripts.py for this short's
// hand-authored script (not LLM output -- no LLM provider key configured).
const brief = shotBriefData as unknown as ShotBriefJson;

export const Ch2Composition: React.FC = () => (
  <GenericChannelShort channelKey="CH2" brief={brief} audioFile={`audio/${brief.short_id}.wav`} />
);

export const ch2ShotBrief = brief;
export const ch2DurationInFrames = totalDurationInFrames(brief);
