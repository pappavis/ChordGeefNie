import React, { useState } from "react";
import type { EngineRequest } from "../types/ChordGeefNie";

export default function Generator({
  onGenerate,
  busy
}: {
  onGenerate: (req: EngineRequest) => void;
  busy: boolean;
}) {
  const [key, setKey] = useState("C");
  const [scale, setScale] = useState<"major" | "minor">("minor");
  const [bars, setBars] = useState(8);
  const [seed, setSeed] = useState<number | "">("");
  const [cadence, setCadence] = useState<"none" | "soft" | "strong" | "plagal" | "half">("plagal");
  const [sevenths, setSevenths] = useState(true);
  const [voicing, setVoicing] = useState<"close" | "open">("open");
  const [inversion, setInversion] = useState<"root" | "random" | "smooth">("smooth");

  return (
    <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(6, minmax(0, 1fr))" }}>
      <label>
        Key<br />
        <input value={key} onChange={(e) => setKey(e.target.value)} style={{ width: "100%" }} />
      </label>

      <label>
        Scale<br />
        <select value={scale} onChange={(e) => setScale(e.target.value as any)} style={{ width: "100%" }}>
          <option value="major">major</option>
          <option value="minor">minor</option>
        </select>
      </label>

      <label>
        Bars<br />
        <input type="number" value={bars} min={1} max={64} onChange={(e) => setBars(Number(e.target.value))} style={{ width: "100%" }} />
      </label>

      <label>
        Seed (optional)<br />
        <input
          type="number"
          value={seed}
          onChange={(e) => setSeed(e.target.value === "" ? "" : Number(e.target.value))}
          style={{ width: "100%" }}
        />
      </label>

      <label>
        Cadence<br />
        <select value={cadence} onChange={(e) => setCadence(e.target.value as any)} style={{ width: "100%" }}>
          <option value="none">none</option>
          <option value="soft">soft</option>
          <option value="strong">strong</option>
          <option value="plagal">plagal</option>
          <option value="half">half</option>
        </select>
      </label>

      <label style={{ display: "flex", alignItems: "end", gap: 8 }}>
        <input type="checkbox" checked={sevenths} onChange={(e) => setSevenths(e.target.checked)} />
        Sevenths
      </label>

      <label>
        Voicing<br />
        <select value={voicing} onChange={(e) => setVoicing(e.target.value as any)} style={{ width: "100%" }}>
          <option value="close">close</option>
          <option value="open">open</option>
        </select>
      </label>

      <label>
        Inversion<br />
        <select value={inversion} onChange={(e) => setInversion(e.target.value as any)} style={{ width: "100%" }}>
          <option value="root">root</option>
          <option value="random">random</option>
          <option value="smooth">smooth</option>
        </select>
      </label>

      <div style={{ gridColumn: "1 / -1" }}>
        <button
          disabled={busy}
          onClick={() =>
            onGenerate({
              key,
              scale,
              bars,
              seed: seed === "" ? null : seed,
              cadence,
              sevenths,
              voicing,
              inversion
            })
          }
          style={{ padding: "10px 14px", borderRadius: 10 }}
        >
          {busy ? "Generating..." : "Generate"}
        </button>
      </div>
    </div>
  );
}
