#!/usr/bin/env python3
# ============================================================
# ChordGeefNie
# File: chordgeefniet.py
# App Version: 0.2.0
# Date: 2026-02-09
#
# Implements:
#   - FS-ChordGeefNie-v0.2 (Extended-B)
#   - TS-ChordGeefNie-v0.2 (Harmony + MIDI + Determinism Tests)
#
# MVP constraints:
#   - single-file
#   - class-based
#   - no global helper functions (entry-point only)
#
# Traceability:
#   - Classes/methods include FS/TS references in docstrings.
# ============================================================

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class AppMeta:
    """
    Implements:
    - FS 0.2: Version visibility, rollback friendliness
    """
    APP_VERSION = "0.2.0"
    FS_VERSION = "FS-ChordGeefNie-v0.2 (Extended-B)"
    TS_VERSION = "TS-ChordGeefNie-v0.2"

    @classmethod
    def banner(cls) -> str:
        return f"ChordGeefNie v{cls.APP_VERSION} | {cls.FS_VERSION} | {cls.TS_VERSION}"


@dataclass
class ChordGeefNieConfig:
    """
    Implements:
    - FS Config keys
    - FS-03: MIDI specifics
    - FS-01: cadence/sevenths controls
    - FS-03.7: voicing/inversions flags
    - FS-05: determinism via SEED
    """
    # Meta
    APP_VERSION: str = AppMeta.APP_VERSION
    FS_VERSION: str = AppMeta.FS_VERSION
    TS_VERSION: str = AppMeta.TS_VERSION

    # Core
    SEED: Optional[int] = None
    KEY: str = "C"
    SCALE: str = "minor"          # "major" | "minor"
    BARS: int = 8
    TIME_SIGNATURE: str = "4/4"   # MVP supports only 4/4
    TEMPO_BPM: int = 120

    # Harmony
    CHORD_COMPLEXITY: str = "triads"   # "triads" | "sevenths" | "mixed"
    SEVENTH_CHORDS_ENABLED: bool = False
    ALLOW_NON_DIATONIC: bool = False   # MVP: must be false
    CADENCE_STYLE: str = "soft"        # "none" | "soft" | "strong" | "plagal" | "half"

    # Voicing / inversions
    VOICING_SPREAD: str = "close"      # "close" | "open"
    INVERSION_MODE: str = "root"       # "root" | "random" | "smooth"

    # MIDI
    MIDI_PPQ: int = 480
    MIDI_CHANNEL: int = 1
    MIDI_TRACKS: int = 1              # MVP: fixed to 1
    NOTE_LENGTH_BEATS: float = 4.0
    CHORD_PLAYBACK_MODE: str = "simultaneous"   # "simultaneous" | "arpeggio"
    ARPEGGIO_SPREAD_BEATS: float = 0.25

    # Velocity
    VELOCITY_MODE: str = "fixed"       # "fixed" | "range" | "humanize"
    VELOCITY_FIXED: int = 90
    VELOCITY_MIN: int = 70
    VELOCITY_MAX: int = 100
    HUMANIZE_AMOUNT: float = 0.15

    # IO
    OUTPUT_FORMAT: str = "text"        # "text" | "json"
    EXPORT_MIDI: bool = False
    MIDI_OUTPUT_PATH: str = "./output.mid"
    PRESET_DIR: str = "./presets"

    # Tests / diagnostics
    DUMP_MIDI_EVENTS_JSON: Optional[str] = None  # path for event dump (optional)
    SELFTEST: bool = False

    def validate(self) -> None:
        """
        Implements:
        - TS v0.2 validation constraints
        """
        if self.SCALE not in ("major", "minor"):
            raise ValueError("SCALE must be 'major' or 'minor'.")
        if self.BARS < 1:
            raise ValueError("BARS must be >= 1.")
        if self.TIME_SIGNATURE != "4/4":
            raise ValueError("MVP supports only TIME_SIGNATURE=4/4.")
        if not (1 <= self.MIDI_CHANNEL <= 16):
            raise ValueError("MIDI_CHANNEL must be 1..16.")
        if self.MIDI_PPQ <= 0:
            raise ValueError("MIDI_PPQ must be > 0.")
        if self.MIDI_TRACKS != 1:
            raise ValueError("MVP supports only MIDI_TRACKS=1.")
        if self.CADENCE_STYLE not in ("none", "soft", "strong", "plagal", "half"):
            raise ValueError("CADENCE_STYLE must be none|soft|strong|plagal|half.")
        if self.CHORD_COMPLEXITY not in ("triads", "sevenths", "mixed"):
            raise ValueError("CHORD_COMPLEXITY must be triads|sevenths|mixed.")
        if self.CHORD_PLAYBACK_MODE not in ("simultaneous", "arpeggio"):
            raise ValueError("CHORD_PLAYBACK_MODE must be simultaneous|arpeggio.")
        if self.VELOCITY_MODE not in ("fixed", "range", "humanize"):
            raise ValueError("VELOCITY_MODE must be fixed|range|humanize.")
        if not (1 <= self.VELOCITY_FIXED <= 127):
            raise ValueError("VELOCITY_FIXED must be 1..127.")
        if not (1 <= self.VELOCITY_MIN <= 127 and 1 <= self.VELOCITY_MAX <= 127):
            raise ValueError("VELOCITY_MIN/MAX must be 1..127.")
        if self.VELOCITY_MIN > self.VELOCITY_MAX:
            raise ValueError("VELOCITY_MIN must be <= VELOCITY_MAX.")
        if not (0.0 <= self.HUMANIZE_AMOUNT <= 1.0):
            raise ValueError("HUMANIZE_AMOUNT must be 0..1.")
        if self.VOICING_SPREAD not in ("close", "open"):
            raise ValueError("VOICING_SPREAD must be close|open.")
        if self.INVERSION_MODE not in ("root", "random", "smooth"):
            raise ValueError("INVERSION_MODE must be root|random|smooth.")
        # MVP: no non-diatonics
        if self.ALLOW_NON_DIATONIC:
            raise ValueError("MVP does not allow non-diatonics (ALLOW_NON_DIATONIC must be false).")


class NoteUtils:
    """
    Encapsulated note utilities (no global functions).
    """
    _NOTE_TO_PC = {
        "C": 0, "C#": 1, "Db": 1,
        "D": 2, "D#": 3, "Eb": 3,
        "E": 4,
        "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8,
        "A": 9, "A#": 10, "Bb": 10,
        "B": 11,
    }
    _PC_TO_NAME_SHARP = {
        0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
        6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"
    }

    @classmethod
    def normalize_key(cls, key: str) -> str:
        k = key.strip()
        if k not in cls._NOTE_TO_PC:
            raise ValueError(f"Unsupported KEY '{key}'. Use e.g. C, C#, Eb, F#.")
        pc = cls._NOTE_TO_PC[k]
        return cls._PC_TO_NAME_SHARP[pc]

    @classmethod
    def note_to_pc(cls, note: str) -> int:
        if note not in cls._NOTE_TO_PC:
            raise ValueError(f"Unknown note '{note}'.")
        return cls._NOTE_TO_PC[note]

    @classmethod
    def pc_to_name(cls, pc: int) -> str:
        return cls._PC_TO_NAME_SHARP[pc % 12]

    @classmethod
    def pc_to_midi(cls, pc: int, octave: int) -> int:
        # MIDI: C4 = 60 => (4+1)*12 + 0
        return (octave + 1) * 12 + (pc % 12)

    @classmethod
    def sha256_file(cls, path: str) -> str:
        import hashlib
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()


@dataclass
class Chord:
    """
    Implements:
    - FS-01: chord representation
    - TS 1.2: Chord structure
    """
    root: str
    quality: str
    notes: List[str]
    degree: int
    bar_index: int

    def __str__(self) -> str:
        q = self.quality
        if q == "maj":
            return f"{self.root}"
        if q == "min":
            return f"{self.root}m"
        if q == "dim":
            return f"{self.root}dim"
        if q == "7":
            return f"{self.root}7"
        if q == "maj7":
            return f"{self.root}maj7"
        if q == "min7":
            return f"{self.root}m7"
        if q == "m7b5":
            return f"{self.root}m7b5"
        return f"{self.root}{q}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "quality": self.quality,
            "notes": self.notes,
            "degree": self.degree,
            "bar_index": self.bar_index,
            "symbol": str(self),
        }


@dataclass
class Progression:
    """
    Implements:
    - FS-01 output container
    - TS 1.3: Progression structure
    """
    key: str
    scale: str
    bars: int
    chords: List[Chord]
    seed: int

    def summary(self) -> str:
        return " | ".join(str(c) for c in self.chords)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "scale": self.scale,
            "bars": self.bars,
            "seed": self.seed,
            "chords": [c.to_dict() for c in self.chords],
        }


class HarmonyEngine:
    """
    Implements:
    - FS-01: generation
    - FS-01.3: cadence variants (none/soft/strong/plagal/half)
    - FS-01.4: seventh toggle (diatonic only)
    - FS-04/FS-05: determinism via seed
    - TS v0.2: harmony algorithm
    """

    def __init__(self, config: ChordGeefNieConfig) -> None:
        self.config = config
        self._last_seed: Optional[int] = None

    def generate(self) -> Progression:
        self.config.validate()

        key = NoteUtils.normalize_key(self.config.KEY)
        scale = self.config.SCALE

        seed = self._resolve_seed(self.config.SEED)
        rng = random.Random(seed)

        diatonic = self._build_diatonic_table(key, scale)

        bars = self.config.BARS
        cadence = self.config.CADENCE_STYLE

        chords: List[Chord] = []
        current_group = "tonic"

        # Helper: choose complexity with gating by SEVENTH_CHORDS_ENABLED
        def pick_complexity() -> str:
            if not self.config.SEVENTH_CHORDS_ENABLED:
                return "triads"
            if self.config.CHORD_COMPLEXITY == "mixed":
                return "sevenths" if rng.random() < 0.35 else "triads"
            return self.config.CHORD_COMPLEXITY

        for bar in range(bars):
            degree, current_group = self._choose_degree_for_bar(
                rng=rng,
                bar=bar,
                bars=bars,
                cadence=cadence,
                current_group=current_group,
                scale=scale,
            )
            comp = pick_complexity()
            chord = self._degree_to_chord(diatonic, degree, bar, comp, scale)
            chords.append(chord)

        self._last_seed = seed
        return Progression(key=key, scale=scale, bars=bars, chords=chords, seed=seed)

    def regenerate(self, use_same_seed: bool = True) -> Progression:
        if use_same_seed and self._last_seed is not None:
            self.config.SEED = self._last_seed
        else:
            self.config.SEED = None
        return self.generate()

    def _resolve_seed(self, seed: Optional[int]) -> int:
        if seed is not None:
            return int(seed)
        return random.SystemRandom().randint(0, 2**31 - 1)

    def _build_diatonic_table(self, key: str, scale: str) -> Dict[int, Tuple[str, str, List[str]]]:
        key_pc = NoteUtils.note_to_pc(key)

        if scale == "major":
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]
            qualities = {1: "maj", 2: "min", 3: "min", 4: "maj", 5: "maj", 6: "min", 7: "dim"}
        else:
            # natural minor MVP
            scale_intervals = [0, 2, 3, 5, 7, 8, 10]
            qualities = {1: "min", 2: "dim", 3: "maj", 4: "min", 5: "min", 6: "maj", 7: "maj"}

        degree_to_pc = {deg: (key_pc + interval) % 12 for deg, interval in enumerate(scale_intervals, start=1)}

        table: Dict[int, Tuple[str, str, List[str]]] = {}
        for deg in range(1, 8):
            root_pc = degree_to_pc[deg]
            root_name = NoteUtils.pc_to_name(root_pc)
            q = qualities[deg]
            triad_pcs = self._build_triad_pcs(root_pc, q)
            triad_names = [NoteUtils.pc_to_name(pc) for pc in triad_pcs]
            table[deg] = (root_name, q, triad_names)
        return table

    def _build_triad_pcs(self, root_pc: int, quality: str) -> List[int]:
        if quality == "maj":
            return [root_pc, (root_pc + 4) % 12, (root_pc + 7) % 12]
        if quality == "min":
            return [root_pc, (root_pc + 3) % 12, (root_pc + 7) % 12]
        if quality == "dim":
            return [root_pc, (root_pc + 3) % 12, (root_pc + 6) % 12]
        return [root_pc, (root_pc + 4) % 12, (root_pc + 7) % 12]

    def _choose_degree_for_bar(
        self,
        rng: random.Random,
        bar: int,
        bars: int,
        cadence: str,
        current_group: str,
        scale: str,
    ) -> Tuple[int, str]:
        # Cadence enforcement in final bars
        if bars >= 2:
            if cadence == "strong":
                if bar == bars - 2:
                    return 5, "dominant"
                if bar == bars - 1:
                    return 1, "tonic"
            if cadence == "plagal":
                if bar == bars - 2:
                    return 4, "subdominant"
                if bar == bars - 1:
                    return 1, "tonic"
            if cadence == "half":
                if bar == bars - 1:
                    return 5, "dominant"
            if cadence == "soft":
                if bar == bars - 1:
                    # bias to tonic at end
                    return rng.choices([1, 6, 3], weights=[0.6, 0.25, 0.15])[0], "tonic"

        # Normal probabilistic transition
        groups = {
            "tonic": [1, 3, 6],
            "subdominant": [2, 4],
            "dominant": [5, 7],
        }
        if current_group == "tonic":
            next_group = rng.choices(["subdominant", "dominant", "tonic"], weights=[0.50, 0.30, 0.20])[0]
        elif current_group == "subdominant":
            next_group = rng.choices(["dominant", "tonic", "subdominant"], weights=[0.55, 0.30, 0.15])[0]
        else:
            next_group = rng.choices(["tonic", "subdominant", "dominant"], weights=[0.65, 0.25, 0.10])[0]

        degree = rng.choice(groups[next_group])
        if degree == 7 and rng.random() < 0.5:
            degree = 5
            next_group = "dominant"
        return degree, next_group

    def _degree_to_chord(
        self,
        diatonic: Dict[int, Tuple[str, str, List[str]]],
        degree: int,
        bar_index: int,
        complexity: str,
        scale: str,
    ) -> Chord:
        root, base_quality, triad_notes = diatonic[degree]

        quality = base_quality
        notes = list(triad_notes)

        if complexity == "sevenths":
            root_pc = NoteUtils.note_to_pc(root)
            # Diatonic-ish heuristics (no non-diatonics)
            if base_quality == "maj":
                if degree == 5:
                    quality = "7"
                    seventh_pc = (root_pc + 10) % 12
                else:
                    quality = "maj7"
                    seventh_pc = (root_pc + 11) % 12
            elif base_quality == "min":
                quality = "min7"
                seventh_pc = (root_pc + 10) % 12
            else:
                quality = "m7b5"
                seventh_pc = (root_pc + 10) % 12
            notes.append(NoteUtils.pc_to_name(seventh_pc))

        return Chord(root=root, quality=quality, notes=notes, degree=degree, bar_index=bar_index)


class PresetManager:
    """
    Implements:
    - FS-06: presets save/load/list
    """
    def __init__(self, config: ChordGeefNieConfig) -> None:
        self.config = config
        self.preset_dir = Path(config.PRESET_DIR)

    def _ensure_dir(self) -> None:
        self.preset_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, progression: Progression) -> Path:
        self._ensure_dir()
        safe = self._slug(name)
        path = self.preset_dir / f"{safe}.json"
        payload = {
            "preset_version": "0.2.0",
            "saved_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "app_version": AppMeta.APP_VERSION,
            "fs_version": AppMeta.FS_VERSION,
            "ts_version": AppMeta.TS_VERSION,
            "config": asdict(self.config),
            "progression": progression.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def load(self, name: str) -> Dict[str, Any]:
        self._ensure_dir()
        safe = self._slug(name)
        path = self.preset_dir / f"{safe}.json"
        if not path.exists():
            raise FileNotFoundError(f"Preset not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_presets(self) -> List[str]:
        self._ensure_dir()
        return sorted(p.stem for p in self.preset_dir.glob("*.json"))

    def _slug(self, s: str) -> str:
        keep = []
        for ch in s.strip().lower():
            if ch.isalnum() or ch in ("-", "_"):
                keep.append(ch)
            elif ch.isspace():
                keep.append("-")
        out = "".join(keep).strip("-")
        return out or "preset"


class MidiExporter:
    """
    Implements:
    - FS-03: MIDI export specifics (PPQ, tempo, playback mode, velocity, channel)
    - FS-03.7: voicing spread + inversions (root/random/smooth)
    - FS-05.2: MIDI event determinism (event dump)
    """

    def __init__(self, config: ChordGeefNieConfig) -> None:
        self.config = config

    def export(self, progression: Progression, output_path: str) -> None:
        midi, events = self._build_midi_and_events(progression)
        midi.save(output_path)

        if self.config.DUMP_MIDI_EVENTS_JSON:
            Path(self.config.DUMP_MIDI_EVENTS_JSON).write_text(json.dumps(events, indent=2), encoding="utf-8")

    def dump_events(self, progression: Progression) -> List[Dict[str, Any]]:
        _, events = self._build_midi_and_events(progression)
        return events

    def _build_midi_and_events(self, progression: Progression):
        self.config.validate()

        try:
            import mido  # type: ignore
            from mido import Message, MidiFile, MidiTrack, MetaMessage  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Missing dependency 'mido'. Install with: pip install mido\n"
                f"Original error: {e}"
            )

        ppq = self.config.MIDI_PPQ
        midi = MidiFile(ticks_per_beat=ppq)
        track = MidiTrack()
        midi.tracks.append(track)

        tempo = mido.bpm2tempo(self.config.TEMPO_BPM)
        track.append(MetaMessage("set_tempo", tempo=tempo, time=0))
        track.append(MetaMessage("time_signature", numerator=4, denominator=4,
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

        beats_per_bar = 4
        chord_len_ticks = int(round(self.config.NOTE_LENGTH_BEATS * ppq))
        channel = self.config.MIDI_CHANNEL - 1

        rng = random.Random(progression.seed)

        # Deterministic voicing state for smooth inversions
        prev_voicing: Optional[List[int]] = None

        abs_events: List[Tuple[int, Any]] = []
        event_dump: List[Dict[str, Any]] = []

        for chord in progression.chords:
            chord_start = chord.bar_index * beats_per_bar * ppq

            chord_pcs = [NoteUtils.note_to_pc(n) for n in chord.notes]
            midi_notes, prev_voicing = self._apply_voicing_and_inversions(
                chord_pcs=chord_pcs,
                rng=rng,
                prev_voicing=prev_voicing,
            )

            # Playback scheduling
            if self.config.CHORD_PLAYBACK_MODE == "simultaneous":
                starts = [chord_start for _ in midi_notes]
            else:
                spread = int(round(self.config.ARPEGGIO_SPREAD_BEATS * ppq))
                starts = [chord_start + i * spread for i in range(len(midi_notes))]

            # Velocity per note
            velocities = [self._velocity_for_note(rng) for _ in midi_notes]

            for note, start_tick, vel in zip(midi_notes, starts, velocities):
                on = Message("note_on", note=int(note), velocity=int(vel), channel=int(channel), time=0)
                off = Message("note_off", note=int(note), velocity=0, channel=int(channel), time=0)

                abs_events.append((start_tick, on))
                abs_events.append((start_tick + chord_len_ticks, off))

                event_dump.append({"abs_tick": int(start_tick), "type": "note_on", "note": int(note), "velocity": int(vel), "channel": int(channel)})
                event_dump.append({"abs_tick": int(start_tick + chord_len_ticks), "type": "note_off", "note": int(note), "velocity": 0, "channel": int(channel)})

        # stable ordering: note_off before note_on at same tick
        def sort_key(item: Tuple[int, Any]) -> Tuple[int, int]:
            tick, msg = item
            t = getattr(msg, "type", "")
            prio = 0 if t == "note_off" else 1
            return (tick, prio)

        abs_events.sort(key=sort_key)
        event_dump.sort(key=lambda d: (d["abs_tick"], 0 if d["type"] == "note_off" else 1, d["note"]))

        # Convert to delta times
        last_tick = 0
        for tick, msg in abs_events:
            delta = tick - last_tick
            msg.time = max(0, int(delta))
            track.append(msg)
            last_tick = tick

        return midi, event_dump

    def _velocity_for_note(self, rng: random.Random) -> int:
        mode = self.config.VELOCITY_MODE
        if mode == "fixed":
            return self._clamp_vel(self.config.VELOCITY_FIXED)
        if mode == "range":
            return self._clamp_vel(rng.randint(self.config.VELOCITY_MIN, self.config.VELOCITY_MAX))
        # humanize
        base = rng.randint(self.config.VELOCITY_MIN, self.config.VELOCITY_MAX)
        jitter = int(round((rng.random() - 0.5) * 2 * 15 * self.config.HUMANIZE_AMOUNT))
        return self._clamp_vel(base + jitter)

    def _clamp_vel(self, v: int) -> int:
        return max(1, min(127, int(v)))

    def _apply_voicing_and_inversions(
        self,
        chord_pcs: List[int],
        rng: random.Random,
        prev_voicing: Optional[List[int]],
    ) -> Tuple[List[int], List[int]]:
        """
        Implements:
        - FS-03.7 VOICING_SPREAD + INVERSION_MODE
        - TS v0.2: smooth inversion selection (min distance)
        """
        # Build base close voicing in octave 3-4
        root_pc = chord_pcs[0]
        base_root = NoteUtils.pc_to_midi(root_pc, octave=3)

        # Build ascending close voicing from pcs
        base = []
        last = base_root - 1
        for pc in chord_pcs:
            n = NoteUtils.pc_to_midi(pc, octave=3)
            while n <= last:
                n += 12
            # ensure root is around base_root
            while n < base_root:
                n += 12
            base.append(n)
            last = n

        # Generate inversions (rotations)
        candidates: List[List[int]] = []
        for inv in range(len(base)):
            vo = base[inv:] + [x + 12 for x in base[:inv]]
            # Normalize ascending
            fixed = []
            last2 = vo[0] - 1
            for n in vo:
                while n <= last2:
                    n += 12
                fixed.append(n)
                last2 = n
            candidates.append(fixed)

        # Apply VOICING_SPREAD (open): lift upper notes
        def apply_spread(notes: List[int]) -> List[int]:
            if self.config.VOICING_SPREAD == "close":
                return list(notes)
            # open: raise 2nd and 3rd chord tone by octave (simple, musical enough for MVP)
            out = list(notes)
            for i in range(1, len(out)):
                if i % 2 == 1:
                    out[i] += 12
            # re-sort to keep ascending
            out_sorted = sorted(out)
            return out_sorted

        candidates = [apply_spread(c) for c in candidates]

        mode = self.config.INVERSION_MODE
        if mode == "root":
            chosen = candidates[0]
        elif mode == "random":
            chosen = candidates[rng.randrange(len(candidates))]
        else:  # smooth
            if prev_voicing is None:
                chosen = candidates[0]
            else:
                chosen = self._choose_smooth_candidate(prev_voicing, candidates)

        return chosen, chosen

    def _choose_smooth_candidate(self, prev: List[int], candidates: List[List[int]]) -> List[int]:
        # Compare by sum of absolute distances between sorted note lists (pad to min length)
        prev_s = sorted(prev)
        best = candidates[0]
        best_score = 10**18
        for cand in candidates:
            cand_s = sorted(cand)
            m = min(len(prev_s), len(cand_s))
            score = 0
            for i in range(m):
                score += abs(prev_s[i] - cand_s[i])
            # penalty for extra notes (sevenths)
            score += 50 * abs(len(prev_s) - len(cand_s))
            if score < best_score:
                best_score = score
                best = cand
        return best


class DeterminismTester:
    """
    Implements:
    - FS-05.1 progression determinism
    - FS-05.2 MIDI determinism (event list + optional file hash)
    """

    def __init__(self, base_config: ChordGeefNieConfig) -> None:
        self.base_config = base_config

    def run(self) -> Tuple[bool, List[str]]:
        messages: List[str] = []

        # Deterministic progression test
        cfg = self._clone_config()
        cfg.SEED = 123
        cfg.KEY = "C"
        cfg.SCALE = "minor"
        cfg.BARS = 8
        cfg.CADENCE_STYLE = "plagal"
        cfg.SEVENTH_CHORDS_ENABLED = True
        cfg.CHORD_COMPLEXITY = "mixed"
        cfg.VOICING_SPREAD = "open"
        cfg.INVERSION_MODE = "smooth"

        engine1 = HarmonyEngine(cfg)
        p1 = engine1.generate()
        engine2 = HarmonyEngine(cfg)
        p2 = engine2.generate()

        if json.dumps(p1.to_dict(), sort_keys=True) != json.dumps(p2.to_dict(), sort_keys=True):
            messages.append("FAIL: Progression determinism (same seed) mismatch.")
            return False, messages
        messages.append("PASS: Progression determinism (same seed)")

        # MIDI event determinism test (requires mido)
        try:
            exporter = MidiExporter(cfg)
            e1 = exporter.dump_events(p1)
            e2 = exporter.dump_events(p2)
            if json.dumps(e1, sort_keys=True) != json.dumps(e2, sort_keys=True):
                messages.append("FAIL: MIDI event determinism mismatch.")
                return False, messages
            messages.append("PASS: MIDI event determinism (same seed)")

            # Optional: file hash determinism
            import tempfile
            tdir = tempfile.mkdtemp(prefix="chordgeefnie_")
            f1 = str(Path(tdir) / "t1.mid")
            f2 = str(Path(tdir) / "t2.mid")
            exporter.export(p1, f1)
            exporter.export(p2, f2)
            h1 = NoteUtils.sha256_file(f1)
            h2 = NoteUtils.sha256_file(f2)
            if h1 != h2:
                messages.append("FAIL: MIDI file hash determinism mismatch.")
                return False, messages
            messages.append("PASS: MIDI file hash determinism (SHA-256)")
        except Exception as e:
            messages.append(f"FAIL: MIDI determinism tests require 'mido' (pip install mido). Error: {e}")
            return False, messages

        return True, messages

    def _clone_config(self) -> ChordGeefNieConfig:
        return ChordGeefNieConfig(**asdict(self.base_config))


class ChordGeefNieApp:
    """
    Thin wrapper: CLI + orchestration.
    Implements:
    - FS CLI
    - MVP demo criterion
    """

    def __init__(self) -> None:
        self.args = self._parse_args()

    def run(self) -> int:
        try:
            if self.args.version:
                print(AppMeta.banner())
                return 0

            cfg = self._config_from_args()
            cfg.validate()

            if cfg.SELFTEST:
                ok, msgs = DeterminismTester(cfg).run()
                for m in msgs:
                    (print(m) if m.startswith("PASS") else print(m, file=sys.stderr))
                return 0 if ok else 2

            preset_mgr = PresetManager(cfg)

            if self.args.preset_list:
                for p in preset_mgr.list_presets():
                    print(p)
                return 0

            if self.args.preset_load:
                data = preset_mgr.load(self.args.preset_load)
                self._emit_loaded_preset(data)
                if self.args.export_midi:
                    prog = self._progression_from_preset(data)
                    cfg2 = self._config_from_preset(data)
                    # allow current overrides
                    cfg2.MIDI_OUTPUT_PATH = cfg.MIDI_OUTPUT_PATH
                    cfg2.EXPORT_MIDI = True
                    cfg2.DUMP_MIDI_EVENTS_JSON = cfg.DUMP_MIDI_EVENTS_JSON
                    MidiExporter(cfg2).export(prog, cfg2.MIDI_OUTPUT_PATH)
                    print(f"MIDI saved: {cfg2.MIDI_OUTPUT_PATH}")
                return 0

            engine = HarmonyEngine(cfg)
            prog = engine.generate()

            self._emit_progression(cfg, prog)

            if self.args.preset_save:
                path = preset_mgr.save(self.args.preset_save, prog)
                print(f"Preset saved: {path}")

            if self.args.export_midi:
                MidiExporter(cfg).export(prog, cfg.MIDI_OUTPUT_PATH)
                print(f"MIDI saved: {cfg.MIDI_OUTPUT_PATH}")

            return 0
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    def _parse_args(self) -> argparse.Namespace:
        p = argparse.ArgumentParser(prog="chordgeefniet.py", add_help=True)

        p.add_argument("--version", action="store_true", help="Show version banner and exit.")
        p.add_argument("--selftest", action="store_true", help="Run determinism unit tests (requires mido).")

        p.add_argument("--key", default="C", help="Key (e.g. C, C#, Eb, F#).")
        p.add_argument("--scale", default="minor", choices=["major", "minor"], help="Scale.")
        p.add_argument("--bars", type=int, default=8, help="Number of bars.")
        p.add_argument("--seed", type=int, default=None, help="Seed (deterministic output).")
        p.add_argument("--tempo", type=int, default=120, help="Tempo in BPM.")

        p.add_argument("--complexity", default="triads", choices=["triads", "sevenths", "mixed"], help="Chord complexity.")
        p.add_argument("--sevenths", action="store_true", help="Enable diatonic seventh chords (toggle).")
        p.add_argument("--cadence", default="soft", choices=["none", "soft", "strong", "plagal", "half"], help="Cadence style.")

        p.add_argument("--voicing", default="close", choices=["close", "open"], help="Voicing spread.")
        p.add_argument("--inversion", default="root", choices=["root", "random", "smooth"], help="Inversion mode.")

        p.add_argument("--json", action="store_true", help="Output as JSON.")
        p.add_argument("--export-midi", action="store_true", help="Export MIDI file.")
        p.add_argument("--midi-out", default="./output.mid", help="MIDI output path.")
        p.add_argument("--ppq", type=int, default=480, help="MIDI ticks per beat (PPQ).")
        p.add_argument("--channel", type=int, default=1, help="MIDI channel (1-16).")
        p.add_argument("--note-length", type=float, default=4.0, help="Note length in beats.")
        p.add_argument("--playback", default="simultaneous", choices=["simultaneous", "arpeggio"], help="Playback mode.")
        p.add_argument("--arp-spread", type=float, default=0.25, help="Arpeggio spread in beats.")

        p.add_argument("--velocity", default="fixed", choices=["fixed", "range", "humanize"], help="Velocity mode.")
        p.add_argument("--vel-fixed", type=int, default=90, help="Fixed velocity (1-127).")
        p.add_argument("--vel-min", type=int, default=70, help="Min velocity.")
        p.add_argument("--vel-max", type=int, default=100, help="Max velocity.")
        p.add_argument("--humanize", type=float, default=0.15, help="Humanize amount (0..1).")

        p.add_argument("--preset-dir", default="./presets", help="Preset directory.")
        p.add_argument("--preset-save", default=None, help="Save preset under this name.")
        p.add_argument("--preset-load", default=None, help="Load preset by name.")
        p.add_argument("--preset-list", action="store_true", help="List presets.")

        p.add_argument("--dump-midi-events", default=None, help="Dump MIDI event list to JSON (diagnostic).")

        return p.parse_args()

    def _config_from_args(self) -> ChordGeefNieConfig:
        cfg = ChordGeefNieConfig(
            SEED=self.args.seed,
            KEY=self.args.key,
            SCALE=self.args.scale,
            BARS=self.args.bars,
            TEMPO_BPM=self.args.tempo,

            CHORD_COMPLEXITY=self.args.complexity,
            SEVENTH_CHORDS_ENABLED=bool(self.args.sevenths),
            CADENCE_STYLE=self.args.cadence,

            VOICING_SPREAD=self.args.voicing,
            INVERSION_MODE=self.args.inversion,

            MIDI_PPQ=self.args.ppq,
            MIDI_CHANNEL=self.args.channel,
            NOTE_LENGTH_BEATS=float(self.args.note_length),
            CHORD_PLAYBACK_MODE=self.args.playback,
            ARPEGGIO_SPREAD_BEATS=float(self.args.arp_spread),

            VELOCITY_MODE=self.args.velocity,
            VELOCITY_FIXED=self.args.vel_fixed,
            VELOCITY_MIN=self.args.vel_min,
            VELOCITY_MAX=self.args.vel_max,
            HUMANIZE_AMOUNT=float(self.args.humanize),

            OUTPUT_FORMAT="json" if self.args.json else "text",
            EXPORT_MIDI=bool(self.args.export_midi),
            MIDI_OUTPUT_PATH=self.args.midi_out,
            PRESET_DIR=self.args.preset_dir,

            DUMP_MIDI_EVENTS_JSON=self.args.dump_midi_events,
            SELFTEST=bool(self.args.selftest),
        )
        return cfg

    def _emit_progression(self, cfg: ChordGeefNieConfig, prog: Progression) -> None:
        if cfg.OUTPUT_FORMAT == "json":
            payload = {
                "meta": {
                    "banner": AppMeta.banner(),
                    "app_version": AppMeta.APP_VERSION,
                    "fs_version": AppMeta.FS_VERSION,
                    "ts_version": AppMeta.TS_VERSION,
                },
                "config": asdict(cfg),
                "progression": prog.to_dict(),
            }
            print(json.dumps(payload, indent=2))
            return

        print(AppMeta.banner())
        print(f"Key: {prog.key} | Scale: {prog.scale} | Bars: {prog.bars} | Seed: {prog.seed}")
        print(f"Cadence: {cfg.CADENCE_STYLE} | Sevenths: {cfg.SEVENTH_CHORDS_ENABLED} | Voicing: {cfg.VOICING_SPREAD} | Inversion: {cfg.INVERSION_MODE}")
        print(prog.summary())

    def _emit_loaded_preset(self, data: Dict[str, Any]) -> None:
        app_v = data.get("app_version")
        fs_v = data.get("fs_version")
        if app_v != AppMeta.APP_VERSION:
            print(f"WARNING: preset app_version={app_v} differs from current app_version={AppMeta.APP_VERSION}", file=sys.stderr)
        if fs_v != AppMeta.FS_VERSION:
            print(f"WARNING: preset fs_version={fs_v} differs from current fs_version={AppMeta.FS_VERSION}", file=sys.stderr)

        prog_data = data.get("progression", {})
        chords = prog_data.get("chords", [])
        symbols = [c.get("symbol", "?") for c in chords]
        print(AppMeta.banner())
        print(f"Loaded preset: key={prog_data.get('key')} scale={prog_data.get('scale')} bars={prog_data.get('bars')} seed={prog_data.get('seed')}")
        print(" | ".join(symbols))

    def _progression_from_preset(self, data: Dict[str, Any]) -> Progression:
        p = data["progression"]
        chords: List[Chord] = []
        for c in p["chords"]:
            chords.append(Chord(
                root=c["root"],
                quality=c["quality"],
                notes=list(c["notes"]),
                degree=int(c["degree"]),
                bar_index=int(c["bar_index"]),
            ))
        return Progression(
            key=p["key"],
            scale=p["scale"],
            bars=int(p["bars"]),
            chords=chords,
            seed=int(p.get("seed", 0)),
        )

    def _config_from_preset(self, data: Dict[str, Any]) -> ChordGeefNieConfig:
        cfg = data.get("config", {})
        allowed = set(ChordGeefNieConfig().__dict__.keys())
        filtered = {k: v for k, v in cfg.items() if k in allowed}
        return ChordGeefNieConfig(**filtered)


if __name__ == "__main__":
    app = ChordGeefNieApp()
    raise SystemExit(app.run())
