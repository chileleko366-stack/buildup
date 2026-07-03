import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { ShotBriefLayer } from "./ShotBriefLayer";
import { WordCascade } from "../primitives/WordCascade";
import { KineticCaption } from "../primitives/KineticCaption";
import type { ShotBriefJson, BeatJson } from "./shotBrief";

// NOT specified in any bible available to this session. A diff fragment
// referenced "BeatCompositor.tsx" and "TransitionSeries.Sequence" and a
// "useActiveBeatBgColor" hook, with no implementation shown -- this build
// does NOT use @remotion/transitions' TransitionSeries (no dependency was
// added for it) because every cut in this format is a hard cut with zero
// transition (05_PACING_MOVEMENT_BIBLE.md §6: "No crossfades, ever,
// anywhere in this format") -- a plain back-to-back <Sequence> already IS
// a hard cut, so pulling in a transitions library to render "no
// transition" would be an unjustified dependency. `useActiveBeatBgColor`
// is also not implemented -- nothing in this session's CH6 render needs a
// per-beat background *color* (CH6's background is the fixed deep-space
// AmbientBackground, not a per-beat color per channelConfigs.ts); if a
// future channel needs it, add it then.
//
// What this generic, channel-agnostic engine actually does: sequences
// beats back-to-back (hard cuts), and per beat renders ShotBriefLayer
// (background + Ken Burns + grading) plus either WordCascade (cascade
// beats) or KineticCaption (all other beats), respecting
// composition.primary_anchor. BadgeBumper is NOT rendered here -- per
// 02_VISUAL_BIBLE.md §2, it's static for the whole video, so the caller
// renders it once, outside/on top of BeatCompositor.
export type BeatCompositorProps = {
  brief: ShotBriefJson;
  renderBackground: (beat: BeatJson) => React.ReactNode;
  renderBeatOverlay?: (beat: BeatJson) => React.ReactNode;
};

export const BeatCompositor: React.FC<BeatCompositorProps> = ({
  brief,
  renderBackground,
  renderBeatOverlay,
}) => {
  let cursor = 0;
  const sequences = brief.beats.map((beat) => {
    const from = cursor;
    cursor += beat.duration_frames;
    return { beat, from };
  });

  return (
    <AbsoluteFill>
      {sequences.map(({ beat, from }) => (
        <Sequence key={beat.beat_id} from={from} durationInFrames={beat.duration_frames}>
          <AbsoluteFill>
            <ShotBriefLayer beat={beat} background={renderBackground(beat)} />
            {beat.cascade ? (
              <WordCascade
                words={beat.word_timings ? beat.word_timings.map((w) => w.word) : beat.text.split(/\s+/)}
                startFrame={0}
                anchorYRatio={brief.composition.primary_anchor}
                wordTimings={
                  beat.word_timings?.map((w) => ({ word: w.word, startFrame: w.start_frame })) ?? undefined
                }
                audioEndFrame={beat.audio_end_frame ?? undefined}
              />
            ) : (
              <KineticCaption
                text={beat.text}
                startFrame={0}
                anchorYRatio={brief.composition.primary_anchor}
                wordTimings={
                  beat.word_timings?.map((w) => ({ word: w.word, startFrame: w.start_frame })) ?? undefined
                }
              />
            )}
            {renderBeatOverlay?.(beat)}
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
