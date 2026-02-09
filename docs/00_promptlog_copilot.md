Perfect. Ik ga dit exact volgens jouw ontwikkelcyclus doen.

Wat je hieronder krijgt is:
	•	Technische Specificatie v0.1
	•	Beperkt tot:
	1.	Harmony Engine
	2.	MIDI Export
	•	Volledig traceable naar FS-ID’s
	•	Geschikt om hierna 1-op-1 code te genereren
	•	Nog géén code (dat is bewust, dit is de laatste ontwerp-gate)

⸻

🛠️ Technische Specificatie

ChordGeefNie – Tech Specs v0.1

Gebaseerd op: FS-ChordGeefNie-v0.2 (Extended-A)
Datum: 2026-02-09
Status: Concept – review vereist
Scope: Harmony Engine + MIDI Export

⸻

0. Algemene technische uitgangspunten

0.1 Taal & runtime
	•	Python 3.10+
	•	Geen internet
	•	Alleen standaardlib + lichte MIDI-lib (bijv. mido of pretty_midi, definitieve keuze later)

0.2 Architectuurregels
	•	Class-based
	•	Geen globale functies
	•	Geen side-effects bij import
	•	Alle random processen seed-aware
	•	MVP: alles in chordgeefniet.py

⸻

1. Harmony Engine – Tech Specs

1.1 Doel

Implementeert:
	•	FS-01 Akkoordprogressie genereren
	•	FS-02 Key & scale
	•	FS-04 Iteratief regenereren
	•	FS-05 Determinisme

De Harmony Engine genereert géén MIDI, alleen muzikale structuur.

⸻

1.2 Kernclasses

1.2.1 Chord

Verantwoordelijkheid: representatie van één akkoord.

Attributes
	•	root: str (bv. "C")
	•	quality: str ("maj", "min", "dim", "7", "maj7")
	•	notes: list[str] (bv. ["C", "E", "G"])
	•	degree: int (1–7, diatonisch)
	•	bar_index: int

Methods
	•	to_dict() -> dict
	•	__str__() -> str (bv. "Cm7")

⸻

1.2.2 Progression

Verantwoordelijkheid: container voor een akkoordprogressie.

Attributes
	•	key: str
	•	scale: str
	•	bars: int
	•	chords: list[Chord]
	•	seed: int | None

Methods
	•	to_dict() -> dict
	•	summary() -> str

⸻

1.2.3 HarmonyEngine

Verantwoordelijkheid: genereert Progression-objecten.

Implementeert
	•	FS-01
	•	FS-02
	•	FS-04
	•	FS-05

Constructor

HarmonyEngine(config: ChordGeefNieConfig)

Public methods

generate() -> Progression
regenerate(use_same_seed: bool = True) -> Progression


⸻

1.3 Interne logica

1.3.1 Diatonische mapping

Per scale wordt een vaste mapping gebruikt:

Major

Degree	Quality
I	maj
ii	min
iii	min
IV	maj
V	maj
vi	min
vii°	dim

Minor (natural, MVP)

Degree	Quality
i	min
ii°	dim
III	maj
iv	min
v	min
VI	maj
VII	maj


⸻

1.3.2 Progressie-algoritme (MVP)
	1.	Start op tonic (I of i)
	2.	Voor elke volgende maat:
	•	Selecteer kandidaat-akkoorden o.b.v. functionele groep:
	•	Tonic
	•	Subdominant
	•	Dominant
	•	Kansgestuurd (weighted random)
	3.	Laatste maat:
	•	Bij CADENCE_STYLE != none
	•	Forceer dominant → tonic

Belangrijk
	•	Geen non-diatonic akkoorden in MVP
	•	Geen modulaties
	•	Kansmatrix is deterministisch bij vaste seed

⸻

1.3.3 Determinisme
	•	Python random.Random(seed)
	•	Één RNG per generatie
	•	RNG wordt doorgegeven aan subroutines (velocity, arpeggio)

⸻

2. MIDI Export – Tech Specs

2.1 Doel

Implementeert:
	•	FS-03 MIDI export (volledig)
	•	Ondersteunt DAW-consistente output

⸻

2.2 Kernclass

2.2.1 MidiExporter

Constructor

MidiExporter(config: ChordGeefNieConfig)

Public method

export(progression: Progression, output_path: str) -> None


⸻

2.3 MIDI-structuur

2.3.1 Timing
	•	PPQ = config.MIDI_PPQ
	•	Tempo meta-event:
	•	config.TEMPO_BPM
	•	Time signature:
	•	MVP hardcoded 4/4 (config voorbereid)

⸻

2.3.2 Track & channel
	•	1 track
	•	Channel = config.MIDI_CHANNEL - 1 (0-based MIDI)

⸻

2.4 Note generatie

2.4.1 Note length

note_length_ticks =
  NOTE_LENGTH_BEATS × PPQ


⸻

2.4.2 Playback mode

Simultaneous
	•	Alle notes:
	•	note_on op zelfde tick
	•	note_off na note_length_ticks

Arpeggio
	•	Starttijd per note:

start_tick = chord_start + (index × ARPEGGIO_SPREAD_BEATS × PPQ)


⸻

2.4.3 Velocity

Fixed
	•	Alle notes: VELOCITY_FIXED

Range
	•	Per note: random [VELOCITY_MIN, VELOCITY_MAX]

Humanize
	•	Zoals range
	•	Extra micro-variatie per chord
	•	Deterministisch via seed

⸻

2.5 MIDI-noot mapping
	•	Noten als MIDI-nummers (C4 = 60)
	•	Octaafkeuze:
	•	MVP: vast (bijv. C3–C4 range)
	•	Later uitbreidbaar

⸻

3. Fouten & validatie

3.1 Harmony Engine
	•	Ongeldige key → ValueError
	•	Bars < 1 → ValueError

3.2 MIDI Export
	•	Velocity buiten 1–127 → clamp
	•	Channel buiten 1–16 → error
	•	Geen progression → error

⸻

4. Traceability-matrix

FS-ID	Class	Methode
FS-01	HarmonyEngine	generate
FS-02	HarmonyEngine	generate
FS-03	MidiExporter	export
FS-04	HarmonyEngine	regenerate
FS-05	HarmonyEngine	generate


⸻

5. Review checklist (voor jou)

Check bij review:
	•	Harmony-regels logisch genoeg voor MVP?
	•	Kansgestuurd vs deterministisch OK?
	•	MIDI playback-modes voldoende?
	•	Velocity-model niet te complex / niet te simpel?

⸻

6. Volgende stap (na jouw GO)

Volgens jouw cyclus:
	1.	✔️ FS goedgekeurd
	2.	✔️ Tech Specs Harmony + MIDI
	3.	👉 Code generatie v0.1 (chordgeefniet.py)

# instructie
Tech Specs v0.1 goedgekeurd – genereer code.

---

Perfect. Ik ga dit exact volgens jouw ontwikkelcyclus doen.

Wat je hieronder krijgt is:
	•	Technische Specificatie v0.1
	•	Beperkt tot:
	1.	Harmony Engine
	2.	MIDI Export
	•	Volledig traceable naar FS-ID’s
	•	Geschikt om hierna 1-op-1 code te genereren
	•	Nog géén code (dat is bewust, dit is de laatste ontwerp-gate)

⸻

🛠️ Technische Specificatie

ChordGeefNie – Tech Specs v0.1

Gebaseerd op: FS-ChordGeefNie-v0.2 (Extended-A)
Datum: 2026-02-09
Status: Concept – review vereist
Scope: Harmony Engine + MIDI Export

⸻

0. Algemene technische uitgangspunten

0.1 Taal & runtime
	•	Python 3.10+
	•	Geen internet
	•	Alleen standaardlib + lichte MIDI-lib (bijv. mido of pretty_midi, definitieve keuze later)

0.2 Architectuurregels
	•	Class-based
	•	Geen globale functies
	•	Geen side-effects bij import
	•	Alle random processen seed-aware
	•	MVP: alles in chordgeefniet.py

⸻

1. Harmony Engine – Tech Specs

1.1 Doel

Implementeert:
	•	FS-01 Akkoordprogressie genereren
	•	FS-02 Key & scale
	•	FS-04 Iteratief regenereren
	•	FS-05 Determinisme

De Harmony Engine genereert géén MIDI, alleen muzikale structuur.

⸻

1.2 Kernclasses

1.2.1 Chord

Verantwoordelijkheid: representatie van één akkoord.

Attributes
	•	root: str (bv. "C")
	•	quality: str ("maj", "min", "dim", "7", "maj7")
	•	notes: list[str] (bv. ["C", "E", "G"])
	•	degree: int (1–7, diatonisch)
	•	bar_index: int

Methods
	•	to_dict() -> dict
	•	__str__() -> str (bv. "Cm7")

⸻

1.2.2 Progression

Verantwoordelijkheid: container voor een akkoordprogressie.

Attributes
	•	key: str
	•	scale: str
	•	bars: int
	•	chords: list[Chord]
	•	seed: int | None

Methods
	•	to_dict() -> dict
	•	summary() -> str

⸻

1.2.3 HarmonyEngine

Verantwoordelijkheid: genereert Progression-objecten.

Implementeert
	•	FS-01
	•	FS-02
	•	FS-04
	•	FS-05

Constructor

HarmonyEngine(config: ChordGeefNieConfig)

Public methods

generate() -> Progression
regenerate(use_same_seed: bool = True) -> Progression


⸻

1.3 Interne logica

1.3.1 Diatonische mapping

Per scale wordt een vaste mapping gebruikt:

Major

Degree	Quality
I	maj
ii	min
iii	min
IV	maj
V	maj
vi	min
vii°	dim

Minor (natural, MVP)

Degree	Quality
i	min
ii°	dim
III	maj
iv	min
v	min
VI	maj
VII	maj


⸻

1.3.2 Progressie-algoritme (MVP)
	1.	Start op tonic (I of i)
	2.	Voor elke volgende maat:
	•	Selecteer kandidaat-akkoorden o.b.v. functionele groep:
	•	Tonic
	•	Subdominant
	•	Dominant
	•	Kansgestuurd (weighted random)
	3.	Laatste maat:
	•	Bij CADENCE_STYLE != none
	•	Forceer dominant → tonic

Belangrijk
	•	Geen non-diatonic akkoorden in MVP
	•	Geen modulaties
	•	Kansmatrix is deterministisch bij vaste seed

⸻

1.3.3 Determinisme
	•	Python random.Random(seed)
	•	Één RNG per generatie
	•	RNG wordt doorgegeven aan subroutines (velocity, arpeggio)

⸻

2. MIDI Export – Tech Specs

2.1 Doel

Implementeert:
	•	FS-03 MIDI export (volledig)
	•	Ondersteunt DAW-consistente output

⸻

2.2 Kernclass

2.2.1 MidiExporter

Constructor

MidiExporter(config: ChordGeefNieConfig)

Public method

export(progression: Progression, output_path: str) -> None


⸻

2.3 MIDI-structuur

2.3.1 Timing
	•	PPQ = config.MIDI_PPQ
	•	Tempo meta-event:
	•	config.TEMPO_BPM
	•	Time signature:
	•	MVP hardcoded 4/4 (config voorbereid)

⸻

2.3.2 Track & channel
	•	1 track
	•	Channel = config.MIDI_CHANNEL - 1 (0-based MIDI)

⸻

2.4 Note generatie

2.4.1 Note length

note_length_ticks =
  NOTE_LENGTH_BEATS × PPQ


⸻

2.4.2 Playback mode

Simultaneous
	•	Alle notes:
	•	note_on op zelfde tick
	•	note_off na note_length_ticks

Arpeggio
	•	Starttijd per note:

start_tick = chord_start + (index × ARPEGGIO_SPREAD_BEATS × PPQ)


⸻

2.4.3 Velocity

Fixed
	•	Alle notes: VELOCITY_FIXED

Range
	•	Per note: random [VELOCITY_MIN, VELOCITY_MAX]

Humanize
	•	Zoals range
	•	Extra micro-variatie per chord
	•	Deterministisch via seed

⸻

2.5 MIDI-noot mapping
	•	Noten als MIDI-nummers (C4 = 60)
	•	Octaafkeuze:
	•	MVP: vast (bijv. C3–C4 range)
	•	Later uitbreidbaar

⸻

3. Fouten & validatie

3.1 Harmony Engine
	•	Ongeldige key → ValueError
	•	Bars < 1 → ValueError

3.2 MIDI Export
	•	Velocity buiten 1–127 → clamp
	•	Channel buiten 1–16 → error
	•	Geen progression → error

⸻

4. Traceability-matrix

FS-ID	Class	Methode
FS-01	HarmonyEngine	generate
FS-02	HarmonyEngine	generate
FS-03	MidiExporter	export
FS-04	HarmonyEngine	regenerate
FS-05	HarmonyEngine	generate


⸻

5. Review checklist (voor jou)

Check bij review:
	•	Harmony-regels logisch genoeg voor MVP?
	•	Kansgestuurd vs deterministisch OK?
	•	MIDI playback-modes voldoende?
	•	Velocity-model niet te complex / niet te simpel?

⸻

6. Volgende stap (na jouw GO)

Volgens jouw cyclus:
	1.	✔️ FS goedgekeurd
	2.	✔️ Tech Specs Harmony + MIDI
	3.	👉 Code generatie v0.1 (chordgeefniet.py)

# instructie
Tech Specs v0.1 goedgekeurd – genereer code.


---
toevoegen aan de functionele specs:1. Unit tests voor determinisme (zelfde seed ⇒ identieke progression & MIDI events).
2. Optionele cadence varianten (plagal, half), en seventh chords toggle (zonder non‑diatonics).
3. Config‑flag voor voicing spread en inversies.
