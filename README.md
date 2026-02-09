# 🎹 ChordGeefNie

**ChordGeefNie** is een **deterministische akkoordprogressie-engine** die MIDI genereert voor DAW’s.  
Het project is opgezet als een **spec-gedreven Proof of Concept (MVP)** met een helder groeipad naar:

- een lokale desktop app (React + Tauri/Electron)
- en een MIDI-FX plugin (AU / VST3 via JUCE)

Alles werkt **offline**, **OS-onafhankelijk** en **reproduceerbaar**.

> Geen magie, geen hype. Gewoon: akkoordprogressies → MIDI → muziek.

---

## ✨ Wat doet ChordGeefNie?

- Genereert akkoordprogressies (major / minor)
- Volledig **deterministisch** via seed
- Exporteert **MIDI** met:
  - instelbare PPQ (ticks per beat)
  - tempo meta-event
  - simultaan of arpeggio playback
  - velocity modes (fixed / range / humanize)
  - instelbare MIDI channel
- Ondersteunt:
  - cadence varianten (soft / strong / plagal / half)
  - diatonische seventh chords (toggle)
  - voicing spread (close / open)
  - inversies (root / random / smooth)
- Presets opslaan & laden (JSON)
- CLI + library-bruikbaar
- Volledig **offline**

---

## ❌ Wat doet het expliciet niet?

- Geen audio synthese
- Geen genre-voorspelling
- Geen “AI schrijft een hit”
- Geen cloud / telemetry
- Geen non-diatonische harmonie (MVP)

---

## 📦 Projectstatus

- **Versie:** v0.2.0
- **Status:** Werkende MVP / Proof of Concept
- **Architectuur:** single-file (`chordgeefniet.py`)
- **Ontwikkelmodel:** AI-first, spec-gedreven

---

## 📁 Repository structuur
chordgeefnie/
├── chordgeefniet.py          # Engine + CLI (MVP)
├── README.md
├── CHANGELOG.md
├── LICENSE
└── docs/
├── FS-ChordGeefNie-v0.2-Extended-B.md
└── TS-ChordGeefNie-v0.2.md

    ---

## 🚀 Quick start

### Vereisten
- Python 3.10+
- Voor MIDI export:  
  ```bash
  pip install mido


  Basisgebruik
```bash
  python chordgeefniet.py --key C --scale minor --bars 8
```

Deterministisch (reproduceerbaar)
```bash
 python chordgeefniet.py --key C --scale minor --bars 8 --seed 123
```

JSON output (voor web / integratie)
```bash
python chordgeefniet.py --key C --scale minor --bars 8 --seed 123 --json

```

MIDI export
```bash
python chordgeefniet.py --key C --scale minor --bars 8 --seed 123 \
--export-midi --midi-out output.mid
```


🧪 Determinisme & tests

ChordGeefNie is testbaar deterministisch.
```bash
pip install mido
python chordgeefniet.py --selftest
```

Tests controleren:
	•	identieke progressies bij gelijke seed
	•	identieke MIDI events
	•	identieke .mid file hash (SHA-256)

💾 Presets
# Opslaan
python chordgeefniet.py --preset-save demo-seed-123

# Laden
python chordgeefniet.py --preset-load demo-seed-123

# Lijst
python chordgeefniet.py --preset-list

Presets bevatten:
	•	config snapshot
	•	gegenereerde progression
	•	versie-informatie (rollback-vriendelijk)

⸻

🧠 Ontwikkelfilosofie

Dit project volgt een strikt spec-gedreven aanpak:
	1.	Functionele specificaties (FS)
	2.	Technische specificaties (TS)
	3.	Codegeneratie
	4.	Werkende demo

Geen code zonder goedgekeurde specs.
Geen “AI doet maar wat”.


🗺️ Roadmap (high level)
	•	CLI MVP (v0.1.0)
	•	Determinisme, cadence varianten, voicing (v0.2.0)
	•	Web MVP (React + Tauri/Electron)
	•	Standalone binary (zonder Python dependency)
	•	JUCE port (AU / VST3 MIDI FX)
	•	UI-gedreven preset management

⸻

📜 Licentie

MIT License — vrij te gebruiken, ook commercieel.

⸻

⚠️ Disclaimer

ChordGeefNie is bedoeld als hulpmiddel, geen vervanging van muzikale keuzes.
Gebruik het als startpunt, niet als eindpunt.
