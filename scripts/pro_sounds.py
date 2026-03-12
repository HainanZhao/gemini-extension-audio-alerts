#!/usr/bin/env python3
"""
Professional Sound Effects Generator
Advanced synthesis: Multi-oscillator, formants, chorus, convolution reverb, granular textures
"""

import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100

# ============================================================================
# WAVEFORM GENERATORS
# ============================================================================

def sine(freq, phase=0):
    """Sine wave generator."""
    return math.sin(2 * math.pi * freq * phase / SAMPLE_RATE)

def square(freq, phase=0, pulse_width=0.5):
    """Square/pulse wave generator."""
    return 1.0 if (phase * freq / SAMPLE_RATE % 1) < pulse_width else -1.0

def triangle(freq, phase=0):
    """Triangle wave generator."""
    t = (phase * freq / SAMPLE_RATE) % 1
    return 4 * abs(t - 0.5) - 1

def sawtooth(freq, phase=0):
    """Sawtooth wave generator."""
    t = (phase * freq / SAMPLE_RATE) % 1
    return 2 * t - 1

def noise():
    """White noise generator."""
    return random.uniform(-1, 1)

# ============================================================================
# ENVELOPE GENERATORS
# ============================================================================

def adsr_envelope(duration, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
    """ADSR envelope with exponential curves."""
    n_samples = int(SAMPLE_RATE * duration)
    envelope = []
    
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)
    release_samples = int(SAMPLE_RATE * release)
    sustain_start = attack_samples + decay_samples
    sustain_end = n_samples - release_samples
    
    for i in range(n_samples):
        if i < attack_samples:
            # Exponential attack
            envelope.append(1 - math.exp(-5 * i / attack_samples))
        elif i < sustain_start:
            # Exponential decay to sustain
            progress = (i - attack_samples) / decay_samples
            envelope.append(1 - (1 - sustain) * (1 - math.exp(-5 * progress)))
        elif i < sustain_end:
            envelope.append(sustain)
        else:
            # Exponential release
            progress = (i - sustain_end) / release_samples
            envelope.append(sustain * math.exp(-5 * progress))
    
    return envelope

def multi_stage_envelope(stages, duration):
    """
    Multi-stage envelope with custom curve shapes.
    stages: list of (time, level, curve) tuples
    curve: 'linear', 'exp', 'log', 'sin'
    """
    n_samples = int(SAMPLE_RATE * duration)
    envelope = []
    
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        
        # Find current stage
        for j in range(len(stages) - 1):
            t0, l0, c0 = stages[j]
            t1, l1, c1 = stages[j + 1]
            
            if t0 <= t < t1:
                progress = (t - t0) / (t1 - t0) if t1 > t0 else 0
                
                if c0 == 'exp':
                    level = l0 + (l1 - l0) * (math.exp(5 * progress) - 1) / (math.e - 1)
                elif c0 == 'log':
                    level = l0 + (l1 - l0) * math.log(1 + 9 * progress) / math.log(10)
                elif c0 == 'sin':
                    level = l0 + (l1 - l0) * math.sin(progress * math.pi / 2)
                else:  # linear
                    level = l0 + (l1 - l0) * progress
                
                envelope.append(level)
                break
        else:
            envelope.append(stages[-1][1])
    
    return envelope

# ============================================================================
# FILTERS
# ============================================================================

def lowpass_filter(samples, cutoff, resonance=0.7):
    """State-variable lowpass filter with resonance."""
    if cutoff <= 0:
        cutoff = 1
    if cutoff >= SAMPLE_RATE / 2:
        cutoff = SAMPLE_RATE / 2
    
    f = 2 * cutoff / SAMPLE_RATE
    q = 1 - resonance / 255
    
    output = []
    hp = 0
    bp = 0
    lp = 0
    
    for sample in samples:
        hp = sample - lp - q * bp
        bp += f * hp
        lp += f * bp
        output.append(lp)
    
    return output

def highpass_filter(samples, cutoff):
    """Simple highpass filter."""
    if cutoff <= 0:
        return samples
    
    alpha = cutoff / (cutoff + SAMPLE_RATE / (2 * math.pi))
    filtered = [samples[0]]
    for i in range(1, len(samples)):
        filtered.append(alpha * (filtered[-1] + samples[i] - samples[i-1]))
    return filtered

def bandpass_filter(samples, low_cutoff, high_cutoff):
    """Bandpass filter (lowpass + highpass)."""
    return lowpass_filter(highpass_filter(samples, low_cutoff), high_cutoff)

def formant_filter(samples, formant_freqs, bandwidth=100):
    """Apply formant filtering for vocal-like qualities."""
    output = samples.copy()
    for formant in formant_freqs:
        # Resonant peak at formant frequency
        for i in range(1, len(output)):
            output[i] += 0.3 * output[i-1] * math.cos(2 * math.pi * formant / SAMPLE_RATE)
    return output

# ============================================================================
# EFFECTS
# ============================================================================

def apply_reverb(samples, room_size=0.5, decay=0.6, wet=0.3):
    """Schroeder reverb with multiple comb filters and allpass filters."""
    # Comb filters (simulate room modes)
    comb_delays = [int(SAMPLE_RATE * d) for d in [0.03, 0.037, 0.041, 0.047]]
    comb_gains = [decay, decay*0.9, decay*0.85, decay*0.8]
    
    output = samples.copy()
    
    for delay, gain in zip(comb_delays, comb_gains):
        delayed = [0] * delay + samples[:-delay]
        output = [o + d * gain for o, d in zip(output, delayed)]
    
    # Allpass filters (diffusion)
    allpass_delays = [int(SAMPLE_RATE * d) for d in [0.005, 0.01]]
    
    for delay in allpass_delays:
        new_output = output.copy()
        for i in range(delay, len(output)):
            new_output[i] = -output[i] + 0.5 * output[i-delay] + 0.5 * new_output[i-delay]
        output = new_output
    
    # Mix wet/dry
    return [s * (1 - wet) + o * wet for s, o in zip(samples, output)]

def apply_chorus(samples, depth=0.003, rate=2, wet=0.4):
    """Chorus effect with LFO-modulated delay."""
    output = []
    delay_buffer = []
    
    for i, sample in enumerate(samples):
        delay_buffer.append(sample)
        
        # LFO modulation
        lfo = math.sin(2 * math.pi * rate * i / SAMPLE_RATE)
        delay = int(SAMPLE_RATE * depth * (1 + lfo))
        
        if len(delay_buffer) > delay:
            delayed_sample = delay_buffer[-delay - 1]
            output.append(sample * (1 - wet) + delayed_sample * wet)
        else:
            output.append(sample)
    
    return output

def apply_delay(samples, delay_ms, feedback=0.4, wet=0.3):
    """Echo/delay effect."""
    delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
    buffer = [0] * delay_samples
    output = []
    
    for sample in samples:
        delayed = buffer.pop(0)
        buffer.append(sample + delayed * feedback)
        output.append(sample * (1 - wet) + delayed * wet)
    
    return output

def apply_distortion(samples, amount=2):
    """Soft clipping distortion."""
    return [math.tanh(s * amount) / math.tanh(amount) for s in samples]

def apply_tremolo(samples, rate=5, depth=0.5):
    """Tremolo effect (amplitude modulation)."""
    output = []
    for i, sample in enumerate(samples):
        lfo = 1 - depth + depth * math.sin(2 * math.pi * rate * i / SAMPLE_RATE)
        output.append(sample * lfo)
    return output

def apply_vibrato(samples, rate=5, depth=0.005):
    """Vibrato effect (frequency modulation via delay)."""
    output = []
    buffer = []
    
    for i, sample in enumerate(samples):
        buffer.append(sample)
        
        lfo = math.sin(2 * math.pi * rate * i / SAMPLE_RATE)
        delay = int(SAMPLE_RATE * depth * (1 + lfo))
        
        if len(buffer) > delay:
            output.append(buffer[-delay - 1])
        else:
            output.append(sample)
    
    return output

def normalize(samples, target=0.9):
    """Normalize audio to target level."""
    max_val = max(abs(s) for s in samples) if samples else 1
    if max_val > 0:
        return [s * target / max_val for s in samples]
    return samples

def mix_sounds(sound_lists, volumes=None):
    """Mix multiple sounds with optional volume levels."""
    if volumes is None:
        volumes = [1.0] * len(sound_lists)
    
    max_len = max(len(s) for s in sound_lists)
    mixed = [0.0] * max_len
    
    for sound, vol in zip(sound_lists, volumes):
        for i, sample in enumerate(sound):
            if i < len(mixed):
                mixed[i] += sample * vol
    
    return normalize(mixed)

# ============================================================================
# SYNTHESIS ENGINES
# ============================================================================

class MultiOscillator:
    """Multi-oscillator synth with detuning and waveform mixing."""
    
    def __init__(self, base_freq, detune=10, waveforms=['sine', 'sine', 'sine']):
        self.base_freq = base_freq
        self.detune = detune
        self.waveforms = waveforms
    
    def generate(self, duration, envelope=None):
        n_samples = int(SAMPLE_RATE * duration)
        output = [0.0] * n_samples
        
        freq_offset = self.detune / 100 * self.base_freq
        
        for osc_idx, waveform in enumerate(self.waveforms):
            freq = self.base_freq + (osc_idx - len(self.waveforms)/2) * freq_offset / max(1, len(self.waveforms)-1)
            
            for i in range(n_samples):
                if waveform == 'sine':
                    sample = sine(freq, i)
                elif waveform == 'square':
                    sample = square(freq, i)
                elif waveform == 'triangle':
                    sample = triangle(freq, i)
                elif waveform == 'sawtooth':
                    sample = sawtooth(freq, i)
                elif waveform == 'noise':
                    sample = noise()
                else:
                    sample = sine(freq, i)
                
                output[i] += sample / len(self.waveforms)
        
        if envelope:
            output = [s * e for s, e in zip(output, envelope[:n_samples])]
        
        return normalize(output)


class FMOperator:
    """FM synthesis operator with envelope."""
    
    def __init__(self, carrier_freq, mod_freq, mod_index, envelope=None):
        self.carrier_freq = carrier_freq
        self.mod_freq = mod_freq
        self.mod_index = mod_index
        self.envelope = envelope
    
    def generate(self, duration):
        n_samples = int(SAMPLE_RATE * duration)
        output = []
        
        for i in range(n_samples):
            modulator = self.mod_index * math.sin(2 * math.pi * self.mod_freq * i / SAMPLE_RATE)
            sample = math.sin(2 * math.pi * self.carrier_freq * i / SAMPLE_RATE + modulator)
            output.append(sample)
        
        if self.envelope:
            output = [s * e for s, e in zip(output, self.envelope[:n_samples])]
        
        return normalize(output)


class AdditiveSynth:
    """Additive synthesis with harmonic control."""
    
    def __init__(self, base_freq, harmonics, amplitudes):
        self.base_freq = base_freq
        self.harmonics = harmonics
        self.amplitudes = amplitudes
    
    def generate(self, duration, envelope=None):
        n_samples = int(SAMPLE_RATE * duration)
        output = [0.0] * n_samples
        
        for harmonic, amplitude in zip(self.harmonics, self.amplitudes):
            freq = self.base_freq * harmonic
            for i in range(n_samples):
                output[i] += amplitude * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        
        if envelope:
            output = [s * e for s, e in zip(output, envelope[:n_samples])]
        
        return normalize(output)


class GranularSynth:
    """Granular synthesis for textures."""
    
    def __init__(self, grain_duration=0.05, overlap=0.5):
        self.grain_duration = grain_duration
        self.overlap = overlap
    
    def generate(self, duration, base_freq, spread=0.1):
        n_samples = int(SAMPLE_RATE * duration)
        output = [0.0] * n_samples
        
        grain_samples = int(SAMPLE_RATE * self.grain_duration)
        step = int(grain_samples * (1 - self.overlap))
        
        pos = 0
        while pos < n_samples:
            # Random frequency variation
            freq = base_freq * (1 + random.uniform(-spread, spread))
            
            # Generate grain with gaussian envelope
            grain = []
            for i in range(grain_samples):
                t = i / grain_samples
                envelope = math.exp(-((t - 0.5) ** 2) / (2 * 0.2 ** 2))
                grain.append(envelope * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
            
            # Add grain to output
            for i, g in enumerate(grain):
                if pos + i < n_samples:
                    output[pos + i] += g / 10  # Scale down for overlap
            
            pos += step
        
        return normalize(output)

# ============================================================================
# SOUND DESIGN PRESETS
# ============================================================================

def generate_espionage_question():
    """Espionage question: Extended mysterious tech sequence with evolving harmonics."""
    # Multi-layered approach - LONGEST sound
    duration = 1.5
    
    # Layer 1: FM bell with inharmonic partials (extended decay)
    env1 = multi_stage_envelope([
        (0, 0, 'linear'), (0.01, 1, 'exp'), (0.8, 0.5, 'linear'), (1.5, 0, 'exp')
    ], duration)
    fm1 = FMOperator(1400, 830, 180, env1)
    layer1 = fm1.generate(duration)
    
    # Layer 2: High harmonic content with evolution
    env2 = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (1.0, 0.4, 'linear'), (1.5, 0, 'exp')
    ], duration)
    harm2 = AdditiveSynth(2100, [1, 1.41, 2.01, 3.02], [0.3, 0.15, 0.1, 0.05])
    layer2 = harm2.generate(duration, env2)
    
    # Layer 3: Subtle noise burst for attack
    noise_env = adsr_envelope(0.08, 0.001, 0.03, 0, 0.04)
    noise_layer = [noise() * e for e in noise_env] + [0] * (int(SAMPLE_RATE * duration) - int(SAMPLE_RATE * 0.08))
    
    # Layer 4: Pulsing undertone
    pulse_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.1, 0.3, 'exp'), (1.2, 0.3, 'linear'), (1.5, 0, 'exp')
    ], duration)
    pulse = AdditiveSynth(280, [1, 2], [0.2, 0.1])
    layer4 = pulse.generate(duration, pulse_env)
    
    # Mix layers
    mixed = mix_sounds([layer1, layer2, noise_layer, layer4], [1.0, 0.5, 0.12, 0.3])
    
    # Apply effects
    mixed = lowpass_filter(mixed, 5000)
    mixed = apply_reverb(mixed, 0.6, 0.55, 0.4)
    mixed = apply_delay(mixed, 120, 0.35, 0.3)
    mixed = apply_chorus(mixed, 0.003, 1.5, 0.25)
    
    return normalize(mixed)

def generate_espionage_error():
    """Espionage error: Dark suspense with rising tension."""
    duration = 0.6
    
    # Layer 1: Deep drone with harmonics
    env1 = adsr_envelope(duration, 0.05, 0.15, 0.7, 0.4)
    drone = AdditiveSynth(120, [1, 1.5, 2.01, 3.02], [0.5, 0.25, 0.15, 0.1])
    layer1 = drone.generate(duration, env1)
    
    # Layer 2: Metallic tension
    env2 = adsr_envelope(duration, 0.1, 0.2, 0.4, 0.3)
    fm2 = FMOperator(340, 178, 90, env2)
    layer2 = fm2.generate(duration)
    
    # Layer 3: Low rumble
    rumble_env = adsr_envelope(duration, 0.02, 0.1, 0.5, 0.45)
    rumble = AdditiveSynth(60, [1, 2, 4], [0.6, 0.3, 0.15])
    layer3 = rumble.generate(duration, rumble_env)
    
    mixed = mix_sounds([layer1, layer2, layer3], [1.0, 0.4, 0.5])
    mixed = lowpass_filter(mixed, 1200)
    mixed = apply_reverb(mixed, 0.6, 0.65, 0.4)
    
    return normalize(mixed)

def generate_espionage_done():
    """Espionage done: Quick resolution from minor to major (mission accomplished)."""
    duration = 0.5
    
    # Phase 1: Minor chord (tension)
    minor_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (0.15, 0.6, 'linear'), (0.25, 0, 'exp')
    ], 0.25)
    
    minor_chord = AdditiveSynth(440, [1, 1.2, 1.5], [0.4, 0.25, 0.2])
    phase1 = minor_chord.generate(0.25, minor_env)
    
    # Phase 2: Major chord (resolution)
    major_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (0.2, 0.5, 'linear'), (0.3, 0, 'exp')
    ], 0.3)
    
    major_chord = AdditiveSynth(554, [1, 1.25, 1.5], [0.35, 0.2, 0.15])
    phase2 = major_chord.generate(0.3, major_env)
    
    # Add delay to phase 2
    phase2 = [0] * int(SAMPLE_RATE * 0.15) + phase2
    
    # Combine
    max_len = max(len(phase1), len(phase2))
    phase1 = phase1 + [0] * (max_len - len(phase1))
    phase2 = phase2 + [0] * (max_len - len(phase2))
    
    mixed = mix_sounds([phase1, phase2], [1.0, 1.0])
    mixed = apply_reverb(mixed, 0.4, 0.5, 0.3)
    
    return normalize(mixed)

def generate_hero_question():
    """Hero question: Epic fanfare buildup with brass section."""
    # Reasonable length - still longest in theme
    duration = 1.3
    
    # Arpeggiated brass fanfare
    notes = [523.25, 659.25, 783.99, 1046.50]  # C major arpeggio
    arpeggio = []
    
    for i, freq in enumerate(notes):
        note_duration = 0.18
        start_delay = i * 0.12
        
        # Brass-like additive synthesis with rich harmonics
        env = multi_stage_envelope([
            (0, 0, 'linear'), (0.02, 1, 'exp'), (0.1, 0.7, 'linear'), (0.18, 0, 'exp')
        ], note_duration)
        
        brass = AdditiveSynth(freq, [1, 2, 3, 4, 5], [0.4, 0.3, 0.25, 0.18, 0.12])
        note = brass.generate(note_duration, env)
        
        # Add to arpeggio with delay
        if start_delay > 0:
            arpeggio.extend([0] * int(SAMPLE_RATE * start_delay))
        arpeggio.extend(note)
    
    # Pad to duration
    arpeggio = arpeggio + [0] * (int(SAMPLE_RATE * duration) - len(arpeggio))
    
    # Add orchestral hit layer
    hit_env = adsr_envelope(0.4, 0.01, 0.12, 0.5, 0.25)
    hit = AdditiveSynth(261.63, [1, 2, 3, 4], [0.4, 0.25, 0.15, 0.1])
    hit_layer = hit.generate(0.4, hit_env)
    hit_layer = hit_layer + [0] * (int(SAMPLE_RATE * duration) - len(hit_layer))
    
    mixed = mix_sounds([arpeggio, hit_layer], [1.0, 0.4])
    mixed = apply_reverb(mixed, 0.7, 0.65, 0.45)
    mixed = apply_chorus(mixed, 0.004, 1.2, 0.25)
    
    return normalize(mixed)

def generate_hero_done():
    """Hero done: Quick triumphant victory stab."""
    duration = 0.5
    
    # Full major chord stab
    chord_freqs = [523.25, 659.25, 783.99, 1046.50]
    
    layers = []
    for freq in chord_freqs:
        env = multi_stage_envelope([
            (0, 0, 'linear'), (0.03, 1, 'exp'), (0.25, 0.6, 'linear'), (0.4, 0, 'exp')
        ], duration)
        
        brass = AdditiveSynth(freq, [1, 2, 3, 4, 5], [0.4, 0.3, 0.2, 0.15, 0.1])
        layers.append(brass.generate(duration, env))
    
    # Add timpani hit
    timpani_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (0.2, 0.5, 'linear'), (0.35, 0, 'exp')
    ], 0.35)
    timpani = AdditiveSynth(130.81, [1, 2], [0.5, 0.3])
    timpani_layer = timpani.generate(0.35, timpani_env)
    timpani_layer = timpani_layer + [0] * (int(SAMPLE_RATE * duration) - len(timpani_layer))
    
    all_layers = layers + [timpani_layer]
    volumes = [1.0] * len(chord_freqs) + [0.5]
    
    mixed = mix_sounds(all_layers, volumes)
    mixed = apply_reverb(mixed, 0.6, 0.6, 0.4)
    
    return normalize(mixed)

def generate_hero_error():
    """Hero error: Dramatic impact with descending brass."""
    duration = 0.7
    
    # Impact layer
    impact_env = adsr_envelope(0.5, 0.005, 0.15, 0.4, 0.3)
    impact = AdditiveSynth(80, [1, 2, 3, 4, 5], [0.6, 0.4, 0.3, 0.2, 0.1])
    impact_layer = impact.generate(0.5, impact_env)
    impact_layer = impact_layer + [0] * (int(SAMPLE_RATE * duration) - len(impact_layer))
    
    # Descending brass line
    desc_notes = [392, 349, 311, 261]  # G-F-Eb-C
    desc_layer = []
    for i, freq in enumerate(desc_notes):
        note_dur = 0.15
        env = adsr_envelope(note_dur, 0.02, 0.05, 0.5, 0.08)
        brass = AdditiveSynth(freq, [1, 2, 3, 4], [0.5, 0.3, 0.2, 0.1])
        note = brass.generate(note_dur, env)
        desc_layer.extend(note)
    
    desc_layer = desc_layer + [0] * (int(SAMPLE_RATE * duration) - len(desc_layer))
    
    # Noise burst for impact
    noise_env = adsr_envelope(0.1, 0.001, 0.03, 0, 0.06)
    noise_layer = [noise() * e for e in noise_env] + [0] * (int(SAMPLE_RATE * duration) - int(SAMPLE_RATE * 0.1))
    
    mixed = mix_sounds([impact_layer, desc_layer[:len(impact_layer)], noise_layer], [1.0, 0.5, 0.2])
    mixed = lowpass_filter(mixed, 2000)
    mixed = apply_reverb(mixed, 0.9, 0.7, 0.5)
    
    return normalize(mixed)

def generate_portal_question():
    """Portal question: Extended rising energy whoosh with particle effects."""
    # LONGEST sound - extended portal sequence
    duration = 1.6
    
    # Frequency sweep (whoosh) - extended
    n_samples = int(SAMPLE_RATE * duration)
    whoosh = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Exponential frequency sweep with modulation
        freq = 250 * math.exp(3.5 * t) + 50 * math.sin(2 * math.pi * 3 * t)
        whoosh.append(0.25 * math.sin(2 * math.pi * freq * t))
    
    whoosh_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.2, 0.7, 'exp'), (1.0, 0.6, 'linear'), (1.4, 0.5, 'linear'), (1.6, 0, 'exp')
    ], duration)
    whoosh = [w * e for w, e in zip(whoosh, whoosh_env)]
    
    # Particle/granular layer - extended
    particles = GranularSynth(0.04, 0.5)
    particle_layer = particles.generate(duration, 1000, 0.4)
    particle_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.3, 0.5, 'exp'), (1.2, 0.4, 'linear'), (1.6, 0, 'exp')
    ], duration)
    particle_layer = [p * e for p, e in zip(particle_layer, particle_env)]
    
    # High sparkle with vibrato
    sparkle_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.05, 0.3, 'exp'), (1.0, 0.25, 'linear'), (1.6, 0, 'exp')
    ], duration)
    sparkle = AdditiveSynth(2400, [1, 1.5, 2], [0.15, 0.08, 0.04])
    sparkle_layer = sparkle.generate(duration, sparkle_env)
    sparkle_layer = apply_vibrato(sparkle_layer, 4, 0.003)
    
    # Subtle bass undertone
    bass_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.15, 0.4, 'exp'), (1.3, 0.35, 'linear'), (1.6, 0, 'exp')
    ], duration)
    bass = AdditiveSynth(120, [1, 2, 4], [0.3, 0.15, 0.08])
    bass_layer = bass.generate(duration, bass_env)
    
    mixed = mix_sounds([whoosh, particle_layer, sparkle_layer, bass_layer], [1.0, 0.35, 0.25, 0.3])
    mixed = highpass_filter(mixed, 150)
    mixed = apply_reverb(mixed, 0.8, 0.7, 0.5)
    mixed = apply_chorus(mixed, 0.005, 2.5, 0.4)
    
    return normalize(mixed)

def generate_portal_done():
    """Portal done: Quick magical arrival with chimes."""
    duration = 0.5
    
    # Cascade of FM chimes (quick)
    chime_freqs = [880, 1100, 1320, 1760]
    chime_layers = []
    
    for i, freq in enumerate(chime_freqs):
        delay = i * 0.04
        chime_dur = 0.25
        
        env = multi_stage_envelope([
            (0, 0, 'linear'), (0.01, 1, 'exp'), (0.15, 0.4, 'linear'), (0.25, 0, 'exp')
        ], chime_dur)
        
        fm = FMOperator(freq, freq * 1.414, 120, env)
        layer = fm.generate(chime_dur)
        
        # Add delay
        layer = [0] * int(SAMPLE_RATE * delay) + layer
        chime_layers.append(layer)
    
    max_len = max(len(l) for l in chime_layers)
    chime_layers = [l + [0] * (max_len - len(l)) for l in chime_layers]
    
    mixed = mix_sounds(chime_layers, [1.0] * len(chime_freqs))
    mixed = apply_reverb(mixed, 0.6, 0.6, 0.45)
    
    return normalize(mixed)

def generate_portal_error():
    """Portal error: Blocked transition with thud."""
    duration = 0.4
    
    # Thud
    thud_env = adsr_envelope(0.25, 0.005, 0.08, 0.3, 0.15)
    thud = AdditiveSynth(100, [1, 2, 3], [0.5, 0.3, 0.15])
    thud_layer = thud.generate(0.25, thud_env)
    thud_layer = thud_layer + [0] * (int(SAMPLE_RATE * duration) - len(thud_layer))
    
    # Whoosh attempt (cut short)
    n_samples = int(SAMPLE_RATE * 0.15)
    attempt = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq = 400 + t * 2000
        attempt.append(0.3 * math.sin(2 * math.pi * freq * t))
    
    attempt_env = adsr_envelope(0.15, 0.01, 0.05, 0, 0.08)
    attempt = [a * e for a, e in zip(attempt, attempt_env)]
    attempt = attempt + [0] * (int(SAMPLE_RATE * duration) - len(attempt))
    
    # Noise burst
    noise_env = adsr_envelope(0.1, 0.001, 0.03, 0, 0.06)
    noise_layer = [noise() * e for e in noise_env] + [0] * (int(SAMPLE_RATE * duration) - int(SAMPLE_RATE * 0.1))
    
    mixed = mix_sounds([thud_layer, attempt, noise_layer], [1.0, 0.4, 0.25])
    mixed = lowpass_filter(mixed, 1500)
    mixed = apply_reverb(mixed, 0.4, 0.5, 0.35)
    
    return normalize(mixed)

def generate_premium_question():
    """Premium question: Extended elegant crystal bell with rich overtones."""
    # LONGEST sound - extended bell sequence
    duration = 1.4
    
    # Main bell with FM - extended decay
    env = multi_stage_envelope([
        (0, 0, 'linear'), (0.008, 1, 'exp'), (0.6, 0.5, 'linear'), (1.0, 0.3, 'linear'), (1.4, 0, 'exp')
    ], duration)
    
    bell = FMOperator(1046.50, 1568, 450, env)
    bell_layer = bell.generate(duration)
    
    # Second bell harmony (fifth above)
    env2 = multi_stage_envelope([
        (0, 0, 'linear'), (0.01, 1, 'exp'), (0.7, 0.45, 'linear'), (1.4, 0, 'exp')
    ], duration)
    bell2 = FMOperator(1568, 2352, 380, env2)
    bell2_layer = bell2.generate(duration)
    
    # Add harmonic richness
    harm_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (0.8, 0.4, 'linear'), (1.4, 0, 'exp')
    ], duration)
    harmonics = AdditiveSynth(1046.50, [1, 2, 3.01, 4.02, 5.03, 6.05], [0.25, 0.18, 0.12, 0.08, 0.05, 0.03])
    harm_layer = harmonics.generate(duration, harm_env)
    
    # Subtle high sparkle
    sparkle_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.01, 0.25, 'exp'), (0.9, 0.2, 'linear'), (1.4, 0, 'exp')
    ], duration)
    sparkle = AdditiveSynth(4186, [1, 2], [0.12, 0.06])
    sparkle_layer = sparkle.generate(duration, sparkle_env)
    
    # Subtle bass foundation
    bass_env = multi_stage_envelope([
        (0, 0, 'linear'), (0.05, 0.35, 'exp'), (1.0, 0.3, 'linear'), (1.4, 0, 'exp')
    ], duration)
    bass = AdditiveSynth(523.25, [1, 2], [0.3, 0.15])
    bass_layer = bass.generate(duration, bass_env)
    
    mixed = mix_sounds([bell_layer, bell2_layer, harm_layer, sparkle_layer, bass_layer], [1.0, 0.5, 0.4, 0.2, 0.35])
    mixed = highpass_filter(mixed, 400)
    mixed = apply_reverb(mixed, 1.5, 0.8, 0.55)
    mixed = apply_chorus(mixed, 0.004, 1.2, 0.35)
    
    return normalize(mixed)

def generate_premium_done():
    """Premium done: Quick luxurious major 7th chord."""
    duration = 0.6
    
    # Major 7th chord: C-E-G-B (rich jazz voicing)
    chord_freqs = [523.25, 659.25, 783.99, 987.77]
    
    layers = []
    for freq in chord_freqs:
        env = multi_stage_envelope([
            (0, 0, 'sin'), (0.05, 1, 'exp'), (0.35, 0.6, 'linear'), (0.5, 0, 'exp')
        ], duration)
        
        tone = AdditiveSynth(freq, [1, 2, 3, 4, 5], [0.35, 0.25, 0.18, 0.12, 0.08])
        layers.append(tone.generate(duration, env))
    
    # Add bass foundation
    bass_env = multi_stage_envelope([
        (0, 0, 'sin'), (0.06, 1, 'exp'), (0.35, 0.6, 'linear'), (0.5, 0, 'exp')
    ], 0.5)
    bass = AdditiveSynth(261.63, [1, 2], [0.5, 0.3])
    bass_layer = bass.generate(0.5, bass_env)
    bass_layer = bass_layer + [0] * (int(SAMPLE_RATE * duration) - len(bass_layer))
    
    all_layers = layers + [bass_layer]
    volumes = [1.0] * len(chord_freqs) + [0.6]
    
    mixed = mix_sounds(all_layers, volumes)
    mixed = apply_reverb(mixed, 0.9, 0.7, 0.45)
    
    return normalize(mixed)

def generate_premium_error():
    """Premium error: Subtle warning with elegant dissonance."""
    duration = 0.4
    
    # Gentle dissonant interval (minor 2nd)
    env1 = adsr_envelope(0.3, 0.01, 0.08, 0.4, 0.2)
    tone1 = AdditiveSynth(698.46, [1, 2, 3], [0.4, 0.2, 0.1])
    layer1 = tone1.generate(0.3, env1)
    layer1 = layer1 + [0] * (int(SAMPLE_RATE * duration) - len(layer1))
    
    env2 = adsr_envelope(0.3, 0.01, 0.08, 0.4, 0.2)
    tone2 = AdditiveSynth(739.99, [1, 2, 3], [0.3, 0.15, 0.08])
    layer2 = tone2.generate(0.3, env2)
    layer2 = layer2 + [0] * (int(SAMPLE_RATE * duration) - len(layer2))
    
    # Soft attack
    attack_env = adsr_envelope(0.08, 0.002, 0.02, 0, 0.05)
    attack = [noise() * e for e in attack_env] + [0] * (int(SAMPLE_RATE * duration) - int(SAMPLE_RATE * 0.08))
    
    mixed = mix_sounds([layer1, layer2, attack], [1.0, 0.6, 0.15])
    mixed = lowpass_filter(mixed, 2500)
    mixed = apply_reverb(mixed, 0.8, 0.6, 0.4)
    
    return normalize(mixed)

def generate_retro_question():
    """Retro question: Extended classic arcade coin insert with dual-tone sequence."""
    # LONGEST sound - extended coin sequence
    duration = 1.2
    
    # Multiple coin insert sounds in sequence
    coin_sequence = []
    
    # First coin (lower then higher)
    for coin_num in range(3):
        # Lower tone
        env1 = adsr_envelope(0.08, 0.002, 0.02, 0.5, 0.05)
        tone1 = []
        for i in range(int(SAMPLE_RATE * 0.08)):
            tone1.append(0.45 * square(880, i))
        tone1 = [t * e for t, e in zip(tone1, env1)]
        
        # Higher tone
        env2 = adsr_envelope(0.1, 0.002, 0.03, 0.5, 0.06)
        tone2 = []
        for i in range(int(SAMPLE_RATE * 0.1)):
            tone2.append(0.45 * square(1760, i))
        tone2 = [t * e for t, e in zip(tone2, env2)]
        
        # Combine coin sound
        coin_sound = tone1 + tone2
        
        # Add slight pitch variation for each coin
        if coin_num > 0:
            coin_sound = [s * (1 + 0.02 * coin_num) for s in coin_sound]
        
        # Add gap between coins
        coin_sequence.extend(coin_sound)
        if coin_num < 2:
            coin_sequence.extend([0] * int(SAMPLE_RATE * 0.15))
    
    # Pad to duration
    coin_sequence = coin_sequence + [0] * (int(SAMPLE_RATE * duration) - len(coin_sequence))
    
    # Add subtle filter sweep
    coin_sequence = lowpass_filter(coin_sequence, 4500)
    
    # Add reverb for depth
    coin_sequence = apply_reverb(coin_sequence, 0.3, 0.4, 0.25)
    
    return normalize(coin_sequence)

def generate_retro_done():
    """Retro done: Classic arcade victory jingle."""
    # Classic ascending melody
    notes = [523, 659, 784, 1047, 1319]  # C-E-G-C-E
    durations = [0.1, 0.1, 0.1, 0.15, 0.2]
    
    jingle = []
    for freq, dur in zip(notes, durations):
        note = []
        for i in range(int(SAMPLE_RATE * dur)):
            note.append(0.4 * square(freq, i))
        
        # Apply envelope
        env = adsr_envelope(dur, 0.005, 0.03, 0.7, 0.05)
        note = [n * e for n, e in zip(note, env)]
        jingle.extend(note)
    
    # Add harmony layer (thirds below)
    harmony_notes = [392, 523, 659, 784, 1047]
    harmony = []
    for freq, dur in zip(harmony_notes, durations):
        note = []
        for i in range(int(SAMPLE_RATE * dur)):
            note.append(0.25 * square(freq, i))
        env = adsr_envelope(dur, 0.005, 0.03, 0.7, 0.05)
        note = [n * e for n, e in zip(note, env)]
        harmony.extend(note)
    
    # Pad to match lengths
    max_len = max(len(jingle), len(harmony))
    jingle = jingle + [0] * (max_len - len(jingle))
    harmony = harmony + [0] * (max_len - len(harmony))
    
    mixed = mix_sounds([jingle, harmony], [1.0, 0.5])
    mixed = apply_reverb(mixed, 0.3, 0.4, 0.25)
    
    return normalize(mixed)

def generate_retro_error():
    """Retro error: Classic game over descending tone."""
    duration = 0.5
    
    # Descending frequency sweep
    n_samples = int(SAMPLE_RATE * duration)
    descend = []
    
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Linear descent from 440Hz to 110Hz
        freq = 440 - t * 660
        descend.append(0.4 * square(freq, i))
    
    # Apply envelope
    env = multi_stage_envelope([
        (0, 0, 'linear'), (0.02, 1, 'exp'), (0.3, 0.6, 'linear'), (0.5, 0, 'exp')
    ], duration)
    descend = [d * e for d, e in zip(descend, env)]
    
    # Add subtle noise
    noise_env = adsr_envelope(0.1, 0.002, 0.03, 0, 0.06)
    noise_layer = [noise() * 0.15 * e for e in noise_env] + [0] * (n_samples - int(SAMPLE_RATE * 0.1))
    
    mixed = mix_sounds([descend, noise_layer], [1.0, 0.2])
    mixed = lowpass_filter(mixed, 3000)
    mixed = apply_reverb(mixed, 0.25, 0.35, 0.2)
    
    return normalize(mixed)

# ============================================================================
# MAIN
# ============================================================================

def save_audio(samples, filepath):
    """Save samples as WAV file."""
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        for sample in samples:
            value = int(sample * 32767)
            value = max(-32768, min(32767, value))
            wav_file.writeframes(struct.pack('<h', value))

def main():
    """Generate all sophisticated sounds."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, 'assets')
    
    sounds = {
        'espionage': {
            'question': generate_espionage_question,
            'error': generate_espionage_error,
            'done': generate_espionage_done,
        },
        'hero': {
            'question': generate_hero_question,
            'error': generate_hero_error,
            'done': generate_hero_done,
        },
        'portal': {
            'question': generate_portal_question,
            'error': generate_portal_error,
            'done': generate_portal_done,
        },
        'premium': {
            'question': generate_premium_question,
            'error': generate_premium_error,
            'done': generate_premium_done,
        },
        'retro': {
            'question': generate_retro_question,
            'error': generate_retro_error,
            'done': generate_retro_done,
        },
    }
    
    print("\n" + "=" * 70)
    print("   🎵 PROFESSIONAL SOUND EFFECTS GENERATOR 🎵")
    print("=" * 70)
    
    for theme, theme_sounds in sounds.items():
        theme_dir = os.path.join(assets_dir, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n  📁 {theme.upper()}")
        print("  " + "-" * 66)
        
        for sound_type, generator in theme_sounds.items():
            filepath = os.path.join(theme_dir, f"{sound_type}.wav")
            
            print(f"    Generating {sound_type}...", end=" ", flush=True)
            samples = generator()
            save_audio(samples, filepath)
            
            duration = len(samples) / SAMPLE_RATE
            print(f"✓ {duration:.2f}s ({len(samples):,} samples)")
    
    print("\n" + "=" * 70)
    print("   ✅ All professional sounds generated successfully!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
