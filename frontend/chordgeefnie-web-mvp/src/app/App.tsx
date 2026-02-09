import React, { useState } from "react";
import { generateProgression } from "../api/chordEngine";
import type { EngineResponse, EngineRequest } from "../types/ChordGeefNie";
import Generator from "./Generator";
import Results from "./Results";

export default function App() {
  const [result, setResult] = useState<EngineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onGenerate(req: EngineRequest) {
    setBusy(true);
    setError(null);
    try {
      const res = await generateProgression(req);
      setResult(res);
    } catch (e: any) {
      setError(String(e?.message ?? e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 16, maxWidth: 980, margin: "0 auto" }}>
      <h1>ChordGeefNie</h1>
      <p style={{ marginTop: 0 }}>
        Offline akkoordprogressies → JSON → MIDI. (Web MVP skeleton)
      </p>

      <Generator onGenerate={onGenerate} busy={busy} />

      {error && (
        <div style={{ background: "#fee", padding: 12, borderRadius: 8, marginTop: 12 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && <Results data={result} />}
    </div>
  );
}
