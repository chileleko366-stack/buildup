// TypeScript mirror of pipeline/shot_brief.py's dataclasses, matching the
// JSON shape produced by `python3 -m pipeline.ch6_short_001` (asdict() +
// json.dumps(), enums serialized to their .value). Kept as plain types
// (not re-deriving from the Python side automatically) -- if the Python
// schema changes, update both sides and re-export the JSON.
export type Domain =
  | "earthly-place"
  | "person"
  | "object"
  | "space"
  | "historical-figure"
  | "historical-place"
  | "abstract";

export type VisualKeywordJson = {
  text: string;
  domain: Domain;
  channel: string;
  beat_id: string;
  named_entity: string | null;
  expected_region_hint: string | null;
};

export type BeatType = "hook" | "context" | "build" | "escalation" | "resolution" | "closer";
export type GradingVariant = "neutral" | "teal-archival" | "warm-sepia";

export type KenBurnsJson = {
  zoom_start: number;
  zoom_end: number;
  pan_direction: "left" | "right" | "up" | "down" | "none";
  pan_amount_ratio: number;
};

export type BeatJson = {
  beat_id: string;
  beat_type: BeatType;
  text: string;
  duration_frames: number;
  cascade: boolean;
  grading: GradingVariant;
  ken_burns: KenBurnsJson;
  visual_keywords: VisualKeywordJson[];
  source_snippet: string | null;
};

export type ShotBriefJson = {
  channel: string;
  short_id: string;
  beats: BeatJson[];
  composition: { primary_anchor: number };
  fps: number;
};

export const totalDurationInFrames = (brief: ShotBriefJson): number =>
  brief.beats.reduce((sum, b) => sum + b.duration_frames, 0);
