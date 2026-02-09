import type { EngineRequest, EngineResponse } from "../types/ChordGeefNie";

/**
 * Web MVP skeleton:
 * - In dev you can fake the engine response here.
 * - In Tauri you will call a Rust command that spawns the local engine binary/script.
 */
export async function generateProgression(req: EngineRequest): Promise<EngineResponse> {
  // TODO: replace with Tauri invoke (command: generate_progression)
  // const res = await invoke<EngineResponse>("generate_progression", { req });

  // Temporary mocked response (keeps UI working):
  const seed = req.seed ?? 123;
  return {
    meta: {
      banner: "ChordGeefNie (web skeleton)",
      app_version: "0.0.1",
      fs_version: "FS-ChordGeefNie-v0.2 (Extended-B)",
      ts_version: "TS-ChordGeefNie-v0.2"
    },
    config: req,
    progression: {
      key: req.key,
      scale: req.scale,
      bars: req.bars,
      seed,
      chords: [
        { symbol: "Am", notes: ["A", "C", "E"], degree: 1, bar_index: 0, root: "A", quality: "min" },
        { symbol: "Dm", notes: ["D", "F", "A"], degree: 4, bar_index: 1, root: "D", quality: "min" },
        { symbol: "E7", notes: ["E", "G#", "B", "D"], degree: 5, bar_index: 2, root: "E", quality: "7" },
        { symbol: "Am", notes: ["A", "C", "E"], degree: 1, bar_index: 3, root: "A", quality: "min" }
      ]
    }
  };
}
