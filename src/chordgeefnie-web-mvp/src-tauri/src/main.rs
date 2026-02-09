#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct EngineRequest {
  pub key: String,
  pub scale: String,
  pub bars: i32,
  pub seed: Option<i64>,
  pub cadence: String,
  pub sevenths: bool,
  pub voicing: String,
  pub inversion: String,
}

// TODO (next step): implement a Tauri command that spawns the engine binary/script
// and returns stdout JSON. Keep offline. No network.
//
// #[tauri::command]
// fn generate_progression(req: EngineRequest) -> Result<serde_json::Value, String> {
//   // spawn ../engine/chordgeefniet ... --json ...
//   Ok(serde_json::json!({ "ok": true }))
// }

fn main() {
  tauri::Builder::default()
    // .invoke_handler(tauri::generate_handler![generate_progression])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
