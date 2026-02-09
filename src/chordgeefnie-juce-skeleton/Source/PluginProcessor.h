#pragma once
// JUCE skeleton placeholder (not yet wired to JUCE modules)

class PluginProcessor {
public:
  PluginProcessor();
  ~PluginProcessor();

  void prepareToPlay(double sampleRate, int samplesPerBlock);
  void processBlock(/*AudioBuffer<float>&*/ void* audio, /*MidiBuffer&*/ void* midi);

  // TODO: parameters + state serialization
};
