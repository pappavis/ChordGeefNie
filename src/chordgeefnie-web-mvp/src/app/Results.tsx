import React from "react";
import type { EngineResponse } from "../types/ChordGeefNie";

export default function Results({ data }: { data: EngineResponse }) {
  const symbols = data.progression.chords.map((c) => c.symbol);
  return (
    <div style={{ marginTop: 16, padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}>
        <div>
          <strong>{data.meta.banner}</strong><br />
          Key: {data.progression.key} | Scale: {data.progression.scale} | Bars: {data.progression.bars} | Seed: {data.progression.seed}
        </div>
        <button
          onClick={() => navigator.clipboard.writeText(symbols.join(" | "))}
          style={{ padding: "8px 12px", borderRadius: 10 }}
        >
          Copy chords
        </button>
      </div>

      <h3 style={{ marginBottom: 6 }}>Progression</h3>
      <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
        {symbols.join(" | ")}
      </div>

      <h3 style={{ marginBottom: 6, marginTop: 16 }}>Chord notes</h3>
      <ul>
        {data.progression.chords.map((c, i) => (
          <li key={i}>
            <strong>{c.symbol}</strong>: {c.notes.join(", ")}
          </li>
        ))}
      </ul>

      <p style={{ opacity: 0.75 }}>
        Next: wire up Tauri command to spawn the local engine and return this JSON.
      </p>
    </div>
  );
}
