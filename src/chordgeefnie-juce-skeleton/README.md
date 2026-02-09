# ChordGeefNie JUCE Skeleton (AU / VST3)

This repo is a **starter skeleton** for a JUCE-based MIDI FX plugin.
Goal: port the Harmony Engine to C++ and schedule MIDI events in-process.

## Targets
- AU (Logic Pro)
- VST3 (Ableton/Reaper/etc.)

## Next
- Decide JUCE build system: Projucer or CMake
- Implement parameter layout (1:1 with engine config)
- Implement scheduling in `processBlock()` using host tempo/PPQ.
