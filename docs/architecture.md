# 🏗️ Architecture – ChordGeefNie

## Overzicht

ChordGeefNie is opgebouwd als een **engine-first systeem**.
De kernlogica is volledig gescheiden van UI, web of plugin-integratie.

<img src="../img/architectuur_technisch.jpg" width="40%" height="40%">

```text
[ CLI / Web / Plugin ]
|
v
[ JSON / Config Contract ]
|
v
[ Harmony Engine ]
|
v
[ MIDI Exporter ]
|
v
[ .mid file / MIDI events ]
```

---

## Kerncomponenten

### HarmonyEngine
Verantwoordelijk voor:
- akkoordprogressie-generatie
- cadence logica
- seventh toggles
- voicing & inversies
- determinisme via seed

➡️ **Geen MIDI-kennis**, puur muzikale structuur.

---

### MidiExporter
Verantwoordelijk voor:
- timing (PPQ, tempo, beats)
- playback mode (simultaan / arpeggio)
- velocity models
- MIDI event scheduling
- determinisme-tests (event dump / hash)

---

### Config & Contract
- Eén configuratiemodel
- JSON-serialiseerbaar
- Identiek gebruikt door:
  - CLI
  - Web frontend
  - Plugin parameters

---

## Determinisme
- Één RNG per generatie
- Seed wordt doorgegeven aan:
  - harmony
  - voicing
  - velocity
- Tests valideren:
  - progression equality
  - MIDI event equality
  - MIDI file hash

---

## Ontwerpkeuzes
- Single-file MVP (bewust)
- Geen globale helpers
- Engine is portable:
  - Python (CLI / web)
  - C++ (JUCE plugin)

---

## Niet-doelen
- Geen audio synthese
- Geen realtime DSP
- Geen non-diatonische harmonie (MVP)

```text
chordgeefnie-web/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   ├── Generator.tsx
│   │   ├── Results.tsx
│   │   └── Presets.tsx
│   ├── api/
│   │   └── chordEngine.ts   # spawn local engine
│   ├── types/
│   │   └── ChordGeefNie.ts  # JSON contract
│   └── main.tsx
├── src-tauri/               # of electron/
│   ├── tauri.conf.json
│   └── main.rs / main.js
├── engine/
│   └── chordgeefniet        # python script of binary
├── package.json
└── README.md
```

# Web–engine contract
```bash
chordgeefniet --json --key C --scale minor --bars 8 --seed 123
```

# 4️⃣ JUCE plugin skeleton (AU / VST3)

## Plugin type
	•	MIDI-FX plugin
	•	Geen audio output
	•	Alleen MIDI events

```text
Source/
├── PluginProcessor.h/.cpp
├── PluginEditor.h/.cpp
├── HarmonyEngine.h/.cpp   # C++ port
├── MidiScheduler.h/.cpp
└── Parameters.h
```

## Parameters (1:1 met engine)
```text
Key
Scale
Bars
Seed
CadenceStyle
SeventhEnabled
VoicingSpread
InversionMode
NoteLengthBeats
PlaybackMode
ArpSpread
VelocityMode
VelocityFixed / Min / Max
MidiChannel
```

## processBlock() gedrag (concept)
```cpp
if (generateTriggered)
    progression = harmonyEngine.generate(config);

for each bar boundary:
    schedule MIDI events into MidiBuffer
```

## Engine-strategie
	•	Python engine = referentie-implementatie
	•	Plugin = C++ port
	•	Geen Python embedding (macOS sandbox & signing issues)

⸻

# 5️⃣ (nieuw) GitHub Architecture Infographic
```bash
## 🧩 Architecture Overview

![ChordGeefNie Architecture](docs/architecture.png)
```

---




Klaar. Ik heb 2 downloadbare skeleton-repos voor je gegenereerd (Web MVP + JUCE) én ik heb je architectuur-infographic als apart bestand klaargezet zodat je ‘m direct in docs/architecture.png kunt committen.

1) Web MVP skeleton (React + Tauri)

Download: chordgeefnie-web-mvp.zip￼

Wat zit erin:
	•	React UI: generator + results (werkt nu met mock)
	•	Tauri skeleton: klaar om straks engine-spawn command toe te voegen
	•	JSON contract types (src/types/ChordGeefNie.ts)
	•	API stub (src/api/chordEngine.ts) → later vervangen door Tauri invoke

Eerstvolgende stap in dit repo: Tauri command toevoegen die ../engine/chordgeefniet spawnt en stdout JSON teruggeeft.

⸻

2) Architecture infographic committen

Je infographic is hier als commit-klaar bestand:
Download: chordgeefnie_repo_docs_architecture.png￼

Plaats in je repo:
	•	docs/architecture.png

Git commands:
```bash
mkdir -p docs
cp /pad/naar/chordgeefnie_repo_docs_architecture.png docs/architecture.png

git add docs/architecture.png README.md
git commit -m "docs: add architecture infographic"
git push
```

## 🧩 Architecture Overview
![ChordGeefNie Architecture](../img/architectuur_technisch.jpg)
