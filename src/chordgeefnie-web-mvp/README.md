# ChordGeefNie Web MVP (React + Tauri)

This is a **skeleton** repo:
- React UI renders a generator + results.
- Next step is wiring a Tauri command to spawn the local engine and return JSON.

## Dev
```bash
npm install
npm run dev
```

## Tauri (after installing Rust + Tauri CLI)
```bash
npm run tauri dev
```

## Engine contract (target)
Spawn local engine:
```bash
chordgeefniet --json --key C --scale minor --bars 8 --seed 123 --cadence plagal --sevenths --voicing open --inversion smooth
```
