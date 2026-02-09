export type EngineRequest = {
  key: string;
  scale: "major" | "minor";
  bars: number;
  seed: number | null;
  cadence: "none" | "soft" | "strong" | "plagal" | "half";
  sevenths: boolean;
  voicing: "close" | "open";
  inversion: "root" | "random" | "smooth";
};

export type EngineChord = {
  symbol: string;
  notes: string[];
  degree: number;
  bar_index: number;
  root: string;
  quality: string;
};

export type EngineResponse = {
  meta: { banner: string; app_version: string; fs_version: string; ts_version: string };
  config: any;
  progression: {
    key: string;
    scale: string;
    bars: number;
    seed: number;
    chords: EngineChord[];
  };
};
