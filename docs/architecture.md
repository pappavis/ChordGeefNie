# 🏗️ Architecture – ChordGeefNie

## Overzicht

ChordGeefNie is opgebouwd als een **engine-first systeem**.
De kernlogica is volledig gescheiden van UI, web of plugin-integratie.

<img src="../img/architectuur_technisch.jpg" width="40%" height="40%">

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
└── README.mdß
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

mkdir -p docs
cp /pad/naar/chordgeefnie_repo_docs_architecture.png docs/architecture.png

git add docs/architecture.png README.md
git commit -m "docs: add architecture infographic"
git push

En voeg in je README:

## 🧩 Architecture Overview
![ChordGeefNie Architecture](docs/architecture.png)


⸻

3) LinkedIn post schrijven (GIF + architectuur)

Hier is een recruiter-proof post: kort, technisch, zonder hype.

Post (copy/paste):

Built a deterministic chord-progression → MIDI engine (offline).

ChordGeefNie v0.2.0 generates diatonic progressions with:
- seed-based determinism (same seed ⇒ same progression + same MIDI)
- cadence variants (plagal / half / strong)
- diatonic 7ths toggle
- voicing spread + inversions (root/random/smooth)
- MIDI export (PPQ, tempo, arpeggio/simultaneous, velocity models)

Why I built it:
I wanted a spec-driven prototype (FS → TS → code) that’s testable and portable:
CLI today, React+Tauri desktop next, JUCE AU/VST3 MIDI FX later.

Demo: short GIF (CLI → MIDI export → DAW import)
Architecture: see diagram in repo.

Repo: ChordGeefNie (MIT)

GIF-script (30–45 sec)
	1.	Terminal: run MIDI export
	2.	Drag demo.mid into Logic (of Ableton)
	3.	Play (toon simultaan vs arpeggio)

Aanrader: maak 2 MIDI’s:
	•	demo_simul.mid
	•	demo_arp.mid

⸻

4) JUCE skeleton repo starten

Download: chordgeefnie-juce-skeleton.zip￼

Wat zit erin:
	•	docs/JUCE_PLUGIN_MAPPING.md (parameter mapping + scheduling sketch)
	•	Source/PluginProcessor.* en PluginEditor.* placeholders
	•	README met targets (AU/VST3)

Eerstvolgende stap in dit repo: kiezen Projucer vs CMake, daarna parameter layout in AudioProcessorValueTreeState.

⸻

Laatste chat-opties (wat wil je dat ik hierna concreet oplever?)

Kies één, dan maak ik het meteen “push-ready”:
	1.	Web MVP: Tauri command implementeren (spawn engine + return JSON + error handling)
	2.	LinkedIn post finetunen op jouw toon + hashtags + “call to action”
	3.	JUCE: echte C++ parameter table + processBlock pseudo-code met PPQ/sample offsets
	4.	Alles integreren in één mono-repo (root + /web + /plugin + /engine)


## 🧩 Architecture Overview
![ChordGeefNie Architecture](../img/architectuur_technisch.jpg)
