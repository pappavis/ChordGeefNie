# JUCE Plugin Mapping – ChordGeefNie

## Plugin Type
- MIDI FX (no audio)
- Outputs MIDI note_on/note_off

## Parameters (suggested)
- Key (0–11)
- Scale (major/minor)
- Bars (2/4/8/16)
- Seed (int + Random toggle)
- CadenceStyle (none/soft/strong/plagal/half)
- SeventhEnabled (bool)
- VoicingSpread (close/open)
- InversionMode (root/random/smooth)
- NoteLengthBeats (float)
- PlaybackMode (simultaneous/arpeggio)
- ArpSpread (float)
- VelocityMode (fixed/range/humanize)
- VelocityFixed/Min/Max/HumanizeAmount
- MidiChannel (1–16)

## Scheduling sketch
- On Generate: build progression and cache
- In processBlock:
  - read host PPQ position + BPM
  - detect bar boundary
  - push MIDI events into MidiBuffer at appropriate sample offsets
