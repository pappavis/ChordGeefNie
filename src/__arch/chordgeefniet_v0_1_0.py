#!/usr/bin/env python3
# ============================================================
# ChordGeefNie
# File: chordgeefniet.py
# App Version: 0.1.0
# Implements:
#   - FS-ChordGeefNie-v0.2 (Extended-A)
#   - TS-ChordGeefNie-v0.1 (Harmony Engine + MIDI Export)
#
# Notes:
# - MVP constraint: single-file, class-based, no global functions.
# - Traceability: classes/methods reference FS/TS sections.
# ============================================================

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class AppMeta:
    """
    Implements:
    - FS 0.1 / 0.2: Version visibility + traceability
    """
    APP_VERSION = "0.1.0"
    FS_VERSION = "FS-ChordGeefNie-v0.2 (Extended-A)"
    TS_VERSION = "TS-ChordGeefNie-v0.1 (Harmony + MIDI)"

    @classmethod
    def banner(cls) -> str:
        return f"ChordGeefNie v{cls.APP_VERSION} | {cls.FS_VERSION} | {cls.TS_VERSION}"


@dataclass
class ChordGeefNieConfig:
    """
    Implements:
    - FS-03: MIDI export specifics (config-driven)
    - FS-05: Determinism (SEED)
    - FS Config keys section
    """
    # Core
    APP_VERSION: str = AppMeta.APP_VERSION
    FS_VERSION: str = AppMeta.FS_VERSION
    TS_VERSION: str = AppMeta.TS_VERSION

    SEED: Optional[int] = None
    KEY: str = "C"
    SCALE: str = "minor"  # "major" | "minor"
    BARS: int = 8
    TIME_SIGNATURE: str = "4/4"
    TEMPO_BPM: int = 120

    # Harmony
    CHORD_COMPLEXITY: str = "triads"  # "triads" | "sevenths" | "mixed"
    ALLOW_NON_DIATONIC: bool = False
    CADENCE_STYLE: str = "soft"  # "none" | "soft" | "strong"

    # MIDI
    MIDI_PPQ: int = 480
    MIDI_CHANNEL: int = 1
    MIDI_TRACKS: int = 1
    NOTE_LENGTH_BEATS: float = 4.0
    CHORD_PLAYBACK_MODE: str = "simultaneous"  # "simultaneous" | "arpeggio"
    ARPEGGIO_SPREAD_BEATS: float = 0.25

    # Velocity
    VELOCITY_MODE: str = "fixed"  # "fixed" | "range" | "humanize"
    VELOCITY_FIXED: int = 90
    VELOCITY_MIN: int = 70
    VELOCITY_MAX: int = 100
    HUMANIZE_AMOUNT: float = 0.15

    # IO
    OUTPUT_FORMAT: str = "text"  # "text" | "json"
    EXPORT_MIDI: bool = False
    MIDI_OUTPUT_PATH: str = "./output.mid"
    PRESET_DIR: str = "./presets"

    def validate(self) -> None:
        """
        Implements:
        - TS 3.0 Validation
        """
        if self.SCALE not in ("major", "minor"):
            raise ValueError("SCALE must be 'major' or 'minor'.")
        if self.BARS < 1:
            raise ValueError("BARS must be >= 1.")
        if not (1 <= self.MIDI_CHANNEL <= 16):
            raise ValueError("MIDI_CHANNEL must be 1..16.")
        if self.MIDI_PPQ <= 0:
            raise ValueError("MIDI_PPQ must be > 0.")
        if self.CADENCE_STYLE not in ("none", "soft", "strong"):
            raise ValueError("CADENCE_STYLE must be none|soft|strong.")
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
        # MVP: time signature prepared but only 4/4 supported
        if self.TIME_SIGNATURE != "4/4":
            raise ValueError("MVP supports only TIME_SIGNATURE=4/4 (prepared for later).")


class NoteUtils:
    """
    Utilities are encapsulated to avoid global functions.
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
            raise ValueError(f"Unsupported KEY '{key}'. Use e.g. C, C#, D, Eb, F#, G, Ab, Bb...")
        # Prefer canonical sharp for internal logic
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
        """
        Convert pitch class and octave to MIDI note number.
        MIDI: C4 = 60 => octave 4, pc 0
        """
        return (octave + 1) * 12 + (pc % 12)


@dataclass
class Chord:
    """
    Implements:
    - TS 1.2.1 Chord
    - FS-01: chord representation
    """
    root: str
    quality: str
    notes: List[str]
    degree: int
    bar_index: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "quality": self.quality,
            "notes": self.notes,
            "degree": self.degree,
            "bar_index": self.bar_index,
            "symbol": str(self),
        }

    def __str__(self) -> str:
        # Simple symbol formatting
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
        return f"{self.root}{q}"


@dataclass
class Progression:
    """
    Implements:
    - TS 1.2.2 Progression
    - FS-01 output container
    """
    key: str
    scale: str
    bars: int
    chords: List[Chord]
    seed: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "scale": self.scale,
            "bars": self.bars,
            "seed": self.seed,
            "chords": [c.to_dict() for c in self.chords],
        }

    def summary(self) -> str:
        return " | ".join(str(c) for c in self.chords)


class HarmonyEngine:
    """
    Implements:
    - FS-01: Chord progression generation
    - FS-02: Key & scale handling
    - FS-04: Iterative regeneration
    - FS-05: Determinism via seed
    - TS 1.x: Harmony engine design
    """

    def __init__(self, config: ChordGeefNieConfig) -> None:
        self.config = config
        self._last_seed: Optional[int] = None
        self._last_progression: Optional[Progression] = None

    def generate(self) -> Progression:
        self.config.validate()

        key = NoteUtils.normalize_key(self.config.KEY)
        scale = self.config.SCALE

        seed = self.config.SEED
        if seed is None:
            # Derive a seed so we can record it (even for "random" runs).
            seed = random.SystemRandom().randint(0, 2**31 - 1)

        rng = random.Random(seed)

        chords: List[Chord] = []
        beats_per_bar = 4  # MVP fixed by TIME_SIGNATURE 4/4

        diatonic = self._build_diatonic_table(key, scale)

        # Decide complexity per chord (triad/seventh) if mixed
        def pick_complexity() -> str:
            if self.config.CHORD_COMPLEXITY == "mixed":
                return "sevenths" if rng.random() < 0.35 else "triads"
            return self.config.CHORD_COMPLEXITY

        # Cadence plan
        bars = self.config.BARS
        cadence = self.config.CADENCE_STYLE

        # Start on tonic
        current_group = "tonic"
        degree = 1

        for bar in range(bars):
            # Cadence enforcement (soft/strong)
            if cadence != "none" and bars >= 2:
                if bar == bars - 1:
                    degree = 1  # tonic
                    current_group = "tonic"
                elif bar == bars - 2 and cadence == "strong":
                    degree = 5  # dominant
                    current_group = "dominant"
                else:
                    degree, current_group = self._choose_next_degree(rng, current_group, scale)
            else:
                degree, current_group = self._choose_next_degree(rng, current_group, scale)

            comp = pick_complexity()
            chord = self._degree_to_chord(
                diatonic=diatonic,
                degree=degree,
                bar_index=bar,
                complexity=comp,
                rng=rng,
            )
            chords.append(chord)

        prog = Progression(key=key, scale=scale, bars=bars, chords=chords, seed=seed)
        self._last_seed = seed
        self._last_progression = prog
        return prog

    def regenerate(self, use_same_seed: bool = True) -> Progression:
        """
        Implements:
        - FS-04: Iterative regeneration
        """
        if use_same_seed and self._last_seed is not None:
            self.config.SEED = self._last_seed
        else:
            self.config.SEED = None
        return self.generate()

    def _build_diatonic_table(self, key: str, scale: str) -> Dict[int, Tuple[str, str, List[str]]]:
        """
        Returns mapping degree -> (root_name, quality, chord_notes_names)
        """
        key_pc = NoteUtils.note_to_pc(key)

        if scale == "major":
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]
            qualities = {1: "maj", 2: "min", 3: "min", 4: "maj", 5: "maj", 6: "min", 7: "dim"}
        else:
            # natural minor MVP
            scale_intervals = [0, 2, 3, 5, 7, 8, 10]
            qualities = {1: "min", 2: "dim", 3: "maj", 4: "min", 5: "min", 6: "maj", 7: "maj"}

        degree_to_pc = {deg: (key_pc + interval) % 12 for deg, interval in enumerate(scale_intervals, start=1)}

        diatonic: Dict[int, Tuple[str, str, List[str]]] = {}
        for deg in range(1, 8):
            root_pc = degree_to_pc[deg]
            root_name = NoteUtils.pc_to_name(root_pc)
            q = qualities[deg]
            triad = self._build_triad_pcs(root_pc, q)
            triad_names = [NoteUtils.pc_to_name(pc) for pc in triad]
            diatonic[deg] = (root_name, q, triad_names)

        return diatonic

    def _build_triad_pcs(self, root_pc: int, quality: str) -> List[int]:
        if quality == "maj":
            return [root_pc, (root_pc + 4) % 12, (root_pc + 7) % 12]
        if quality == "min":
            return [root_pc, (root_pc + 3) % 12, (root_pc + 7) % 12]
        if quality == "dim":
            return [root_pc, (root_pc + 3) % 12, (root_pc + 6) % 12]
        # fallback
        return [root_pc, (root_pc + 4) % 12, (root_pc + 7) % 12]

    def _choose_next_degree(self, rng: random.Random, current_group: str, scale: str) -> Tuple[int, str]:
        """
        Implements:
        - TS 1.3.2: functional-group transitions (weighted)
        """
        groups = {
            "tonic": [1, 3, 6],
            "subdominant": [2, 4],
            "dominant": [5, 7],
        }
        # Minor: degree 3 and 6 are major but still functionally tonic-ish in this MVP
        # Transition weights
        if current_group == "tonic":
            next_group = rng.choices(["subdominant", "dominant", "tonic"], weights=[0.50, 0.30, 0.20])[0]
        elif current_group == "subdominant":
            next_group = rng.choices(["dominant", "tonic", "subdominant"], weights=[0.55, 0.30, 0.15])[0]
        else:  # dominant
            next_group = rng.choices(["tonic", "subdominant", "dominant"], weights=[0.65, 0.25, 0.10])[0]

        # Choose a degree within group
        degs = groups[next_group]
        degree = rng.choice(degs)

        # MVP nicety: avoid too many repeats of VII in minor/major (can sound harsh)
        if degree == 7 and rng.random() < 0.5:
            degree = 5

        return degree, next_group

    def _degree_to_chord(
        self,
        diatonic: Dict[int, Tuple[str, str, List[str]]],
        degree: int,
        bar_index: int,
        complexity: str,
        rng: random.Random,
    ) -> Chord:
        root, base_quality, triad_notes = diatonic[degree]

        # Complexity mapping
        quality = base_quality
        notes = list(triad_notes)

        if complexity == "sevenths":
            # add diatonic seventh based on scale degree: take next 6th interval from scale table
            # MVP approach: add note a third above the fifth: (root + 10 for dom7, +11 for maj7, +10 for min7)
            root_pc = NoteUtils.note_to_pc(root)
            if base_quality == "maj":
                # Heuristic: V7 for dominant, maj7 for tonic-ish
                if degree == 5:
                    quality = "7"
                    seventh_pc = (root_pc + 10) % 12
                else:
                    quality = "maj7"
                    seventh_pc = (root_pc + 11) % 12
            elif base_quality == "min":
                quality = "min7"
                seventh_pc = (root_pc + 10) % 12
            else:  # dim
                # half-diminished-ish: dim + minor7
                quality = "m7b5"
                seventh_pc = (root_pc + 10) % 12
            notes.append(NoteUtils.pc_to_name(seventh_pc))

        return Chord(root=root, quality=quality, notes=notes, degree=degree, bar_index=bar_index)


class PresetManager:
    """
    Implements:
    - FS-06: Preset management (save/load/list)
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
            "preset_version": "0.1.0",
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
        data = json.loads(path.read_text(encoding="utf-8"))
        return data

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
    - FS-03: MIDI export (PPQ, tempo, playback modes, velocity, channel)
    - TS 2.x: MIDI exporter design
    """

    def __init__(self, config: ChordGeefNieConfig) -> None:
        self.config = config

    def export(self, progression: Progression, output_path: str) -> None:
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

        # Meta: tempo + time signature
        tempo = mido.bpm2tempo(self.config.TEMPO_BPM)
        track.append(MetaMessage("set_tempo", tempo=tempo, time=0))
        track.append(MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

        beats_per_bar = 4
        chord_len_ticks = int(round(self.config.NOTE_LENGTH_BEATS * ppq))
        channel = self.config.MIDI_CHANNEL - 1

        rng = random.Random(progression.seed or 0)

        events: List[Tuple[int, Any]] = []  # (abs_tick, mido_message)
        for chord in progression.chords:
            chord_start = chord.bar_index * beats_per_bar * ppq

            # Map note names to MIDI numbers in a fixed register (MVP)
            # Use octave 3 for root-ish, then stack notes upward
            # Strategy: root at octave 3, others at >= root midi
            root_pc = NoteUtils.note_to_pc(chord.notes[0])
            base_midi = NoteUtils.pc_to_midi(root_pc, octave=3)

            midi_notes: List[int] = []
            for i, note_name in enumerate(chord.notes):
                pc = NoteUtils.note_to_pc(note_name)
                n = NoteUtils.pc_to_midi(pc, octave=3)
                # ensure non-decreasing pitch to avoid weird inversions in MVP
                while n < base_midi:
                    n += 12
                # small lift for upper chord tones
                if i > 0 and n == base_midi:
                    n += 12
                midi_notes.append(n)

            # Playback mode scheduling
            mode = self.config.CHORD_PLAYBACK_MODE
            if mode == "simultaneous":
                starts = [chord_start for _ in midi_notes]
            else:
                spread = int(round(self.config.ARPEGGIO_SPREAD_BEATS * ppq))
                starts = [chord_start + i * spread for i in range(len(midi_notes))]

            # Velocity per note
            velocities = [self._velocity_for_note(rng) for _ in midi_notes]

            for note, start_tick, vel in zip(midi_notes, starts, velocities):
                events.append((start_tick, Message("note_on", note=note, velocity=vel, channel=channel, time=0)))
                events.append((start_tick + chord_len_ticks, Message("note_off", note=note, velocity=0, channel=channel, time=0)))

        # Sort by tick; note_off before note_on if same tick? (avoid stuck notes)
        def sort_key(item: Tuple[int, Any]) -> Tuple[int, int]:
            tick, msg = item
            # note_off should come first at same tick
            priority = 0
            try:
                if getattr(msg, "type", "") == "note_on":
                    priority = 1
                if getattr(msg, "type", "") == "note_off":
                    priority = 0
            except Exception:
                priority = 0
            return (tick, priority)

        events.sort(key=sort_key)

        # Convert to delta times
        last_tick = 0
        for tick, msg in events:
            delta = tick - last_tick
            msg.time = max(0, int(delta))
            track.append(msg)
            last_tick = tick

        midi.save(output_path)

    def _velocity_for_note(self, rng: random.Random) -> int:
        mode = self.config.VELOCITY_MODE
        if mode == "fixed":
            return self._clamp_vel(self.config.VELOCITY_FIXED)
        if mode == "range":
            v = rng.randint(self.config.VELOCITY_MIN, self.config.VELOCITY_MAX)
            return self._clamp_vel(v)
        # humanize
        base = rng.randint(self.config.VELOCITY_MIN, self.config.VELOCITY_MAX)
        # micro variation controlled by HUMANIZE_AMOUNT
        jitter = int(round((rng.random() - 0.5) * 2 * 15 * self.config.HUMANIZE_AMOUNT))
        return self._clamp_vel(base + jitter)

    def _clamp_vel(self, v: int) -> int:
        return max(1, min(127, int(v)))


class ChordGeefNieApp:
    """
    Thin wrapper around core classes.
    Implements:
    - FS CLI + demo criterion
    - Non-functional: offline + OS independent execution
    """

    def __init__(self) -> None:
        self.args = self._parse_args()

    def run(self) -> int:
        try:
            if self.args.version:
                print(AppMeta.banner())
                return 0

            config = self._config_from_args()
            config.validate()

            preset_mgr = PresetManager(config)

            # Preset list
            if self.args.preset_list:
                presets = preset_mgr.list_presets()
                for p in presets:
                    print(p)
                return 0

            # Load preset path (optional flow)
            if self.args.preset_load:
                data = preset_mgr.load(self.args.preset_load)
                self._emit_loaded_preset(data)
                # If export requested, export using stored progression
                if self.args.export_midi:
                    prog = self._progression_from_preset(data)
                    config_from_preset = self._config_from_preset(data)
                    # keep current output path overrides
                    config_from_preset.MIDI_OUTPUT_PATH = config.MIDI_OUTPUT_PATH
                    config_from_preset.EXPORT_MIDI = True
                    exporter = MidiExporter(config_from_preset)
                    exporter.export(prog, config_from_preset.MIDI_OUTPUT_PATH)
                    print(f"MIDI saved: {config_from_preset.MIDI_OUTPUT_PATH}")
                return 0

            # Generate progression
            engine = HarmonyEngine(config)
            prog = engine.generate()

            # Emit output
            self._emit_progression(config, prog)

            # Save preset (optional)
            if self.args.preset_save:
                path = preset_mgr.save(self.args.preset_save, prog)
                print(f"Preset saved: {path}")

            # Export MIDI (optional)
            if self.args.export_midi:
                exporter = MidiExporter(config)
                exporter.export(prog, config.MIDI_OUTPUT_PATH)
                print(f"MIDI saved: {config.MIDI_OUTPUT_PATH}")

            return 0
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    def _parse_args(self) -> argparse.Namespace:
        p = argparse.ArgumentParser(prog="chordgeefniet.py", add_help=True)
        p.add_argument("--version", action="store_true", help="Show version banner and exit.")
        p.add_argument("--key", default="C", help="Key (e.g. C, C#, Eb, F#).")
        p.add_argument("--scale", default="minor", choices=["major", "minor"], help="Scale.")
        p.add_argument("--bars", type=int, default=8, help="Number of bars.")
        p.add_argument("--seed", type=int, default=None, help="Seed (deterministic output).")
        p.add_argument("--tempo", type=int, default=120, help="Tempo in BPM.")
        p.add_argument("--complexity", default="triads", choices=["triads", "sevenths", "mixed"], help="Chord complexity.")
        p.add_argument("--cadence", default="soft", choices=["none", "soft", "strong"], help="Cadence style.")
        p.add_argument("--allow-non-diatonic", action="store_true", help="Allow non-diatonic chords (MVP: ignored).")

        p.add_argument("--json", action="store_true", help="Output as JSON.")
        p.add_argument("--export-midi", action="store_true", help="Export MIDI file.")
        p.add_argument("--midi-out", default="./output.mid", help="MIDI output path.")
        p.add_argument("--ppq", type=int, default=480, help="MIDI ticks per beat (PPQ).")
        p.add_argument("--channel", type=int, default=1, help="MIDI channel (1-16).")
        p.add_argument("--note-length", type=float, default=4.0, help="Note length in beats.")
        p.add_argument("--playback", default="simultaneous", choices=["simultaneous", "arpeggio"], help="Chord playback mode.")
        p.add_argument("--arp-spread", type=float, default=0.25, help="Arpeggio spread in beats (arpeggio mode).")

        p.add_argument("--velocity", default="fixed", choices=["fixed", "range", "humanize"], help="Velocity mode.")
        p.add_argument("--vel-fixed", type=int, default=90, help="Fixed velocity (1-127).")
        p.add_argument("--vel-min", type=int, default=70, help="Min velocity.")
        p.add_argument("--vel-max", type=int, default=100, help="Max velocity.")
        p.add_argument("--humanize", type=float, default=0.15, help="Humanize amount (0..1).")

        p.add_argument("--preset-dir", default="./presets", help="Preset directory.")
        p.add_argument("--preset-save", default=None, help="Save preset under this name.")
        p.add_argument("--preset-load", default=None, help="Load preset by name.")
        p.add_argument("--preset-list", action="store_true", help="List presets.")

        return p.parse_args()

    def _config_from_args(self) -> ChordGeefNieConfig:
        cfg = ChordGeefNieConfig(
            SEED=self.args.seed,
            KEY=self.args.key,
            SCALE=self.args.scale,
            BARS=self.args.bars,
            TEMPO_BPM=self.args.tempo,
            CHORD_COMPLEXITY=self.args.complexity,
            ALLOW_NON_DIATONIC=bool(self.args.allow_non_diatonic),
            CADENCE_STYLE=self.args.cadence,

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
        )
        return cfg

    def _emit_progression(self, config: ChordGeefNieConfig, prog: Progression) -> None:
        if config.OUTPUT_FORMAT == "json":
            payload = {
                "meta": {
                    "banner": AppMeta.banner(),
                    "app_version": AppMeta.APP_VERSION,
                    "fs_version": AppMeta.FS_VERSION,
                    "ts_version": AppMeta.TS_VERSION,
                },
                "config": asdict(config),
                "progression": prog.to_dict(),
            }
            print(json.dumps(payload, indent=2))
            return

        print(AppMeta.banner())
        print(f"Key: {prog.key} | Scale: {prog.scale} | Bars: {prog.bars} | Seed: {prog.seed}")
        print(prog.summary())

    def _emit_loaded_preset(self, data: Dict[str, Any]) -> None:
        # Minimal: show what was loaded + warnings
        app_v = data.get("app_version")
        fs_v = data.get("fs_version")
        if app_v != AppMeta.APP_VERSION:
            print(f"WARNING: preset app_version={app_v} differs from current app_version={AppMeta.APP_VERSION}", file=sys.stderr)
        if fs_v != AppMeta.FS_VERSION:
            print(f"WARNING: preset fs_version={fs_v} differs from current fs_version={AppMeta.FS_VERSION}", file=sys.stderr)

        # print progression summary
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
            seed=p.get("seed"),
        )

    def _config_from_preset(self, data: Dict[str, Any]) -> ChordGeefNieConfig:
        cfg = data.get("config", {})
        # Load only keys that exist in dataclass
        allowed = set(ChordGeefNieConfig().__dict__.keys())
        filtered = {k: v for k, v in cfg.items() if k in allowed}
        merged = ChordGeefNieConfig(**filtered)
        return merged


if __name__ == "__main__":
    app = ChordGeefNieApp()
    raise SystemExit(app.run())
