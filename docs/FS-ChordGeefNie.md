# 📘 Functionele Specificatie – ChordGeefNie

## Metadata
- Productnaam: ChordGeefNie
- FS-versie: v0.2 (Extended-B)
- Datum: 2026-02-09
- Status: Goedgekeurd voor Tech Specs
- Ontwikkelmodel: AI-first, spec-gedreven
- MVP artefact: chordgeefniet.py (single file)

---

## 0. Doel van dit document
Dit document is de **enige bron van waarheid** voor functionaliteit.
Geen code wordt gegenereerd zonder expliciete goedkeuring van deze FS.

---

## 1. Productdefinitie

ChordGeefNie is een akkoordprogressie-generator die:
- Muzikale progressies genereert
- MIDI-output levert voor DAW’s
- Deterministisch of random kan werken
- Volledig offline en OS-onafhankelijk is

Niet het doel:
- Audio synthese
- Muziektheorie-educatie
- Genre- of hit-voorspelling

---

## 2. Ontwikkelfilosofie (AI-first)

- Eerst specificaties, dan techniek, dan code
- AI is uitvoerend, niet beslissend
- Elke stap is:
  - verklaarbaar
  - reproduceerbaar
  - rollbackbaar

---

## 3. Ontwikkelcyclus

1. Functionele specs → review → freeze
2. Technische specs → review → freeze
3. Code generatie (class-based)
4. Werkende demo

Geen fases overslaan.

---

## 4. Versiebeheer & rollback

- FS-versies zijn immutabel na goedkeuring
- Code en presets verwijzen naar FS-versie
- Rollback = terug naar eerdere FS + code tag

---

## 5. Architectuurprincipes

- Class-based
- Geen globale functies
- Core los van UI
- Herbruikbaar voor CLI, Web, VST3

---

## 6. MVP-constraint

- Alle code in één bestand: `chordgeefniet.py`
- Intern logisch gescheiden via classes

---

## 7. Functionele eisen

### FS-01 – Harmony Engine

#### FS-01.1 Progressie-generatie
- Op basis van key, scale, bars
- Harmonisch consistent
- Diatonisch in MVP

#### FS-01.2 Scales
- Major
- Natural minor (MVP)

#### FS-01.3 Cadence styles
- none
- soft (V→I)
- strong (V→I force)
- **plagal (IV→I / iv→i)**
- **half (…→V)**

Cadence wordt toegepast in de laatste 1–2 maten.

#### FS-01.4 Seventh chords toggle
- `SEVENTH_CHORDS_ENABLED: bool`
- Alleen diatonische sevenths
- Geen non-diatonics

Los van complexiteitsinstelling.

#### FS-01.5 Iteratief regenereren
- Zelfde seed ⇒ zelfde output

---

### FS-02 – Key & Scale handling
- Chromatische keys
- Intern genormaliseerd

---

### FS-03 – MIDI Export

#### FS-03.1 Timing
- PPQ instelbaar
- Default: 480

#### FS-03.2 Playback modes
- simultaneous
- arpeggio (met spread)

#### FS-03.3 Note length
- In beats

#### FS-03.4 Velocity modes
- fixed
- range
- humanize (seed-aware)

#### FS-03.5 Tempo
- Tempo meta-event in MIDI file

#### FS-03.6 Track & Channel
- 1 track
- Channel 1–16 instelbaar

#### FS-03.7 Voicing & inversies
- `VOICING_SPREAD`: close | open
- `INVERSION_MODE`:
  - root
  - random (seed-aware)
  - smooth (minimale sprongen)

Geen non-diatonic notes toegestaan.

---

### FS-04 – Determinisme
- Seed-ondersteuning
- Volledige reproduceerbaarheid

---

### FS-05 – Determinisme tests (verplicht)

#### FS-05.1 Progression test
- Zelfde config + seed
- Identieke akkoorden (symbolen, noten, degrees, bars)

#### FS-05.2 MIDI test
- Zelfde input
- Identieke MIDI events **of**
- Identieke `.mid` file hash

---

### FS-06 – Preset management

- Opslaan/laden als JSON
- Bevat:
  - config snapshot
  - progression
  - versie-informatie
- Waarschuwing bij versieverschil

---

## 8. Configuratie (ChordGeefNieConfig)

### Core
- APP_VERSION
- FS_VERSION
- SEED
- KEY
- SCALE
- BARS
- TEMPO_BPM
- TIME_SIGNATURE (4/4 MVP)

### Harmony
- CHORD_COMPLEXITY
- SEVENTH_CHORDS_ENABLED
- CADENCE_STYLE
- ALLOW_NON_DIATONIC (false in MVP)

### Voicing
- VOICING_SPREAD
- INVERSION_MODE

### MIDI
- MIDI_PPQ
- MIDI_CHANNEL
- NOTE_LENGTH_BEATS
- CHORD_PLAYBACK_MODE
- ARPEGGIO_SPREAD_BEATS

### Velocity
- VELOCITY_MODE
- VELOCITY_FIXED
- VELOCITY_MIN / MAX
- HUMANIZE_AMOUNT

### IO
- OUTPUT_FORMAT
- EXPORT_MIDI
- MIDI_OUTPUT_PATH
- PRESET_DIR

---

## 9. CLI & Web-voorbereiding

- CLI is contract voor frontend
- JSON output verplicht voor web
- Volledig offline
- OS-onafhankelijk

---

## 10. Non-functionele eisen

- Geen internet
- Geen telemetry
- Deterministisch gedrag
- <100 ms generatie
- Dependencies gepind

---

## 11. Testbaarheid

- Unit tests voor determinisme
- Event-dump of hash-based MIDI tests
- Optionele `--selftest`

---

## 12. Succescriterium MVP

```bash
python chordgeefniet.py --key C --scale minor --bars 8 --seed 123 --export-midi
