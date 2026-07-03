import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { BeatCompositor } from "../BeatCompositor";
import { BadgeBumper } from "../../primitives/BadgeBumper";
import { GradeTestBackground } from "../../dev/GradeTestBackground";
import { CHANNELS, ChannelId } from "../../constants/channels";
import type { ShotBriefJson, BeatJson } from "../shotBrief";

// Phase 4: shared composition engine for CH1-CH5, replicating CH6's real,
// already-verified pattern (BadgeBumper mounted once at root, BeatCompositor
// driving per-beat background/Ken-Burns/DuotoneGrade/FilmGrain + captions,
// nothing reinvented per channel) -- channel-specific only in the config
// values passed as props (badge/accent color from CHANNELS, the brief JSON,
// the mastered audio file). See Ch6Composition.tsx for the pattern this
// mirrors; CH6 itself is untouched by this file.
//
// One real difference from CH6, stated plainly rather than silently
// matched: CH6's own composition has no audio track at all (still 100%
// silent, per CLAUDE.md). CH1-CH5 DO have a real mastered audio track
// (TTS + naturalness + music + SFX + ducking + loudnorm, see
// pipeline/render_channel_short.py) muxed in here via a single root-level
// <Audio> tag, with per-beat duration_frames/word_timings/audio_end_frame
// all derived from that same real audio (see shot_brief.py's Beat fields)
// -- not the pacing-bible placeholder timing CH6 still uses. FilmGrain is
// wired in identically to CH6 (it's inside ShotBriefLayer, shared by both).
//
// Background is GradeTestBackground per beat, the same standard non-
// shipping placeholder used everywhere else in this repo outside of CH6
// (which has its own bespoke AmbientBackground/Starfield, reconstructed
// from a diff fragment specific to CH6's space visual identity -- no
// equivalent bespoke background exists, or is spec'd, for any other
// channel, so it is NOT reused here).
export type GenericChannelShortProps = {
  channelKey: ChannelId;
  brief: ShotBriefJson;
  audioFile: string;
};

const renderBackground = (beat: BeatJson) => <GradeTestBackground label={beat.beat_id} />;

export const GenericChannelShort: React.FC<GenericChannelShortProps> = ({ channelKey, brief, audioFile }) => {
  const channel = CHANNELS[channelKey];
  return (
    <AbsoluteFill>
      <Audio src={staticFile(audioFile)} />
      <BeatCompositor brief={brief} renderBackground={renderBackground} />
      <BadgeBumper tag={channel.badgeTag} accentColor={channel.accentColor} />
    </AbsoluteFill>
  );
};
