import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { BeatCompositor } from "../BeatCompositor";
import { BadgeBumper } from "../../primitives/BadgeBumper";
import { SourcedBackground } from "../SourcedBackground";
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
// Background is SourcedBackground per beat (Phase 2 wiring, this pass) --
// uses each beat's REAL sourced asset (Pexels/Pixabay for CH1/CH2/CH4,
// Wikimedia/LOC for CH3/CH5, per 04_ASSET_ACCURACY_BIBLE.md §2's
// allow-list) when one was accepted by pipeline/footage_sourcing/
// resolve.py, falling back to the same GradeTestBackground placeholder
// (now labeled with the real reason) when it wasn't. CH1-CH5's currently-
// committed shot brief JSON predates this field and has none set (see
// CLAUDE.md's Phase 2 section for exactly which channels have been
// regenerated with a real resolution attempt vs. which haven't yet) --
// SourcedBackground's fallback path makes that safe either way (no
// undefined-field crash, just the placeholder with a generic status).
// CH6's own bespoke AmbientBackground/Starfield (reconstructed from a
// diff fragment specific to CH6's space visual identity) still is NOT
// reused here -- no equivalent bespoke background exists, or is spec'd,
// for any other channel.
export type GenericChannelShortProps = {
  channelKey: ChannelId;
  brief: ShotBriefJson;
  audioFile: string;
};

const renderBackground = (beat: BeatJson) => <SourcedBackground beat={beat} />;

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
