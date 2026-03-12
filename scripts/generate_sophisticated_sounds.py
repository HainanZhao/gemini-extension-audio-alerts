#!/usr/bin/env python3
"""
Generate sophisticated sound effects for different themes.
Uses advanced synthesis techniques: FM synthesis, harmonics, envelopes, and effects.
"""

import os
import wave
import struct
import math

SAMPLE_RATE = 44100

def generate_envelope(duration, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
    """Generate ADSR envelope."""
    n_samples = int(SAMPLE_RATE * duration)
    envelope = []
    
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)
    release_samples = int(SAMPLE_RATE * release)
    sustain_start = attack_samples + decay_samples
    sustain_end = n_samples - release_samples
    
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        if i < attack_samples:
            # Attack phase
            envelope.append(i / attack_samples)
        elif i < sustain_start:
            # Decay phase
            progress = (i - attack_samples) / decay_samples
            envelope.append(1.0 - (1.0 - sustain) * progress)
        elif i < sustain_end:
            # Sustain phase
            envelope.append(sustain)
        else:
            # Release phase
            progress = (i - sustain_end) / release_samples
            envelope.append(sustain * (1.0 - progress))
    
    return envelope

def generate_sine(freq, duration, volume=0.5):
    """Generate sine wave."""
    n_samples = int(SAMPLE_RATE * duration)
    return [volume * math.sin(2 * math.pi * freq * i / SAMPLE_RATE) for i in range(n_samples)]

def generate_square(freq, duration, volume=0.3):
    """Generate square wave (8-bit style)."""
    n_samples = int(SAMPLE_RATE * duration)
    period = SAMPLE_RATE / freq
    return [volume if (i % int(period)) < period / 2 else -volume for i in range(n_samples)]

def generate_triangle(freq, duration, volume=0.4):
    """Generate triangle wave."""
    n_samples = int(SAMPLE_RATE * duration)
    period = SAMPLE_RATE / freq
    samples = []
    for i in range(n_samples):
        t = (i % int(period)) / period
        samples.append(volume * (4 * abs(t - 0.5) - 1) * -1)
    return samples

def generate_sawtooth(freq, duration, volume=0.3):
    """Generate sawtooth wave."""
    n_samples = int(SAMPLE_RATE * duration)
    period = SAMPLE_RATE / freq
    return [volume * (2 * ((i / period) % 1) - 1) for i in range(n_samples)]

def fm_synthesize(carrier_freq, mod_freq, mod_index, duration, volume=0.3):
    """FM synthesis for bell-like tones."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        modulator = mod_index * math.sin(2 * math.pi * mod_freq * t)
        sample = volume * math.sin(2 * math.pi * carrier_freq * t + modulator)
        samples.append(sample)
    return samples

def add_harmonics(base_freq, duration, harmonics_list, volumes):
    """Add harmonics to create richer tones."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * n_samples
    
    for harmonic, vol in zip(harmonics_list, volumes):
        freq = base_freq * harmonic
        for i in range(n_samples):
            samples[i] += vol * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
    
    # Normalize
    max_val = max(abs(s) for s in samples)
    if max_val > 0:
        samples = [s / max_val * 0.8 for s in samples]
    
    return samples

def apply_reverb(samples, decay=0.3, delay_ms=50):
    """Apply simple reverb effect."""
    delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
    output = samples.copy()
    
    # Add delayed, decayed copies
    for i in range(delay_samples, len(samples)):
        output[i] += samples[i - delay_samples] * decay
    
    for i in range(delay_samples * 2, len(samples)):
        output[i] += samples[i - delay_samples * 2] * decay * 0.5
    
    # Normalize
    max_val = max(abs(s) for s in output)
    if max_val > 0.9:
        output = [s * 0.9 / max_val for s in output]
    
    return output

def apply_filter(samples, cutoff_freq):
    """Apply simple low-pass filter."""
    alpha = cutoff_freq / (cutoff_freq + SAMPLE_RATE / (2 * math.pi))
    filtered = [samples[0]]
    for i in range(1, len(samples)):
        filtered.append(alpha * samples[i] + (1 - alpha) * filtered[-1])
    return filtered

def mix_sounds(sound_lists):
    """Mix multiple sound lists together."""
    max_len = max(len(s) for s in sound_lists)
    mixed = [0.0] * max_len
    
    for sound in sound_lists:
        for i, sample in enumerate(sound):
            if i < len(mixed):
                mixed[i] += sample
    
    # Normalize
    max_val = max(abs(s) for s in mixed)
    if max_val > 0:
        mixed = [s / max_val * 0.85 for s in mixed]
    
    return mixed

def save_mp3(samples, filepath):
    """Save samples as WAV file (named .mp3 for compatibility)."""
    n_samples = len(samples)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        for sample in samples:
            value = int(sample * 32767)
            value = max(-32768, min(32767, value))
            wav_file.writeframes(struct.pack('<h', value))

# ============================================================================
# THEME SOUND GENERATORS
# ============================================================================

def generate_espionage_sounds():
    """Espionage theme: mysterious, tech, spy sounds."""
    sounds = {}
    
    # Question: Mysterious high-tech ping with FM synthesis
    fm_tone = fm_synthesize(1200, 300, 200, 0.15, 0.4)
    envelope = generate_envelope(0.15, attack=0.005, decay=0.05, sustain=0.3, release=0.09)
    fm_tone = [s * e for s, e in zip(fm_tone, envelope)]
    sounds['question'] = apply_reverb(fm_tone, decay=0.2, delay_ms=30)
    
    # Error: Dark suspense drone with harmonics
    base = add_harmonics(150, 0.4, [1, 1.5, 2, 3], [0.5, 0.2, 0.15, 0.1])
    envelope = generate_envelope(0.4, attack=0.02, decay=0.1, sustain=0.6, release=0.2)
    base = [s * e for s, e in zip(base, envelope)]
    sounds['error'] = apply_filter(base, 800)
    
    # Done: Success chord progression (minor to major resolution)
    chord1 = add_harmonics(440, 0.2, [1, 2, 3], [0.4, 0.2, 0.1])
    chord2 = add_harmonics(554, 0.3, [1, 2, 3], [0.4, 0.2, 0.1])
    envelope1 = generate_envelope(0.2, attack=0.01, decay=0.05, sustain=0.5, release=0.1)
    envelope2 = generate_envelope(0.3, attack=0.01, decay=0.08, sustain=0.5, release=0.15)
    chord1 = [s * e for s, e in zip(chord1, envelope1)]
    chord2 = [s * e for s, e in zip(chord2, envelope2)]
    # Delay chord2
    chord2 = [0.0] * int(SAMPLE_RATE * 0.15) + chord2
    sounds['done'] = apply_reverb(mix_sounds([chord1 + [0.0] * (len(chord2) - len(chord1)), chord2]), 0.3, 40)
    
    return sounds

def generate_hero_sounds():
    """Hero theme: epic, triumphant, victory sounds."""
    sounds = {}
    
    # Question: Heroic fanfare buildup (major triad arpeggio)
    notes = [523, 659, 784]  # C major
    arpeggio = []
    for i, freq in enumerate(notes):
        note = add_harmonics(freq, 0.15, [1, 2, 3, 4], [0.5, 0.25, 0.15, 0.1])
        env = generate_envelope(0.15, attack=0.01, decay=0.05, sustain=0.6, release=0.08)
        note = [s * e for s, e in zip(note, env)]
        note = [0.0] * int(SAMPLE_RATE * i * 0.08) + note
        arpeggio.extend(note)
    sounds['question'] = apply_reverb(arpeggio, 0.4, 60)
    
    # Error: Dramatic low impact with crash
    impact = generate_sawtooth(80, 0.5, 0.5)
    crash = generate_square(200, 0.3, 0.2)
    env_impact = generate_envelope(0.5, attack=0.01, decay=0.2, sustain=0.3, release=0.25)
    env_crash = generate_envelope(0.3, attack=0.005, decay=0.1, sustain=0.2, release=0.15)
    impact = [s * e for s, e in zip(impact, env_impact)]
    crash = [s * e for s, e in zip(crash, env_crash)]
    sounds['error'] = apply_reverb(mix_sounds([impact, crash]), 0.3, 50)
    
    # Done: Epic victory fanfare (full major chord with harmonics)
    chord = add_harmonics(523, 0.6, [1, 1.25, 1.5, 2, 2.5, 3], [0.4, 0.3, 0.25, 0.2, 0.15, 0.1])
    envelope = generate_envelope(0.6, attack=0.02, decay=0.1, sustain=0.7, release=0.35)
    chord = [s * e for s, e in zip(chord, envelope)]
    sounds['done'] = apply_reverb(chord, 0.5, 80)
    
    return sounds

def generate_portal_sounds():
    """Portal theme: whoosh, teleport, transition sounds."""
    sounds = {}
    
    # Question: Rising whoosh (frequency sweep)
    n_samples = int(SAMPLE_RATE * 0.2)
    whoosh = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq = 400 + t * 4000  # Sweep from 400Hz to 4400Hz
        whoosh.append(0.3 * math.sin(2 * math.pi * freq * t))
    envelope = generate_envelope(0.2, attack=0.01, decay=0.05, sustain=0.4, release=0.1)
    whoosh = [s * e for s, e in zip(whoosh, envelope)]
    sounds['question'] = apply_reverb(whoosh, 0.3, 30)
    
    # Error: Blocking thud
    import random
    thud = generate_triangle(120, 0.25, 0.5)
    noise = [0.1 * (random.random() * 2 - 1) for _ in range(int(SAMPLE_RATE * 0.15))]
    env_thud = generate_envelope(0.25, attack=0.005, decay=0.1, sustain=0.3, release=0.12)
    thud = [s * e for s, e in zip(thud, env_thud)]
    sounds['error'] = thud + [0.0] * (int(SAMPLE_RATE * 0.25) - len(thud))
    
    # Done: Magical teleport arrival (sparkling chime cascade)
    chimes = []
    freqs = [880, 1100, 1320, 1760]
    for i, freq in enumerate(freqs):
        chime = fm_synthesize(freq, freq * 1.5, 100, 0.3, 0.3)
        env = generate_envelope(0.3, attack=0.005, decay=0.08, sustain=0.5, release=0.18)
        chime = [s * e for s, e in zip(chime, env)]
        chime = [0.0] * int(SAMPLE_RATE * i * 0.05) + chime
        chimes.append(chime)
    sounds['done'] = apply_reverb(mix_sounds(chimes), 0.4, 50)
    
    return sounds

def generate_premium_sounds():
    """Premium theme: elegant, luxury, refined sounds."""
    sounds = {}
    
    # Question: Crystal bell (pure FM bell tone)
    bell = fm_synthesize(1047, 1565, 350, 0.4, 0.4)
    envelope = generate_envelope(0.4, attack=0.005, decay=0.1, sustain=0.6, release=0.25)
    bell = [s * e for s, e in zip(bell, envelope)]
    sounds['question'] = apply_reverb(bell, 0.4, 60)
    
    # Error: Subtle warning chime
    warning = add_harmonics(698, 0.25, [1, 2, 3], [0.5, 0.2, 0.1])
    envelope = generate_envelope(0.25, attack=0.01, decay=0.08, sustain=0.5, release=0.12)
    warning = [s * e for s, e in zip(warning, envelope)]
    sounds['error'] = apply_reverb(warning, 0.25, 40)
    
    # Done: Luxury chord progression (rich jazz chord)
    # Major 7th chord: C-E-G-B
    chord_freqs = [523, 659, 784, 988]
    chord = []
    for freq in chord_freqs:
        tone = add_harmonics(freq, 0.7, [1, 2, 3, 4, 5], [0.35, 0.2, 0.15, 0.1, 0.08])
        chord.extend(tone[:int(SAMPLE_RATE * 0.1)])
    
    # Layer multiple octaves
    bass = add_harmonics(261, 0.7, [1, 2, 3], [0.4, 0.2, 0.1])
    treble = add_harmonics(1047, 0.7, [1, 2], [0.3, 0.15])
    
    envelope = generate_envelope(0.7, attack=0.02, decay=0.15, sustain=0.7, release=0.4)
    full_chord = mix_sounds([bass, chord[:len(bass)], treble[:len(bass)]])
    full_chord = [s * e for s, e in zip(full_chord, envelope)]
    sounds['done'] = apply_reverb(full_chord, 0.5, 70)
    
    return sounds

def generate_retro_sounds():
    """Retro theme: 8-bit, arcade, vintage game sounds."""
    sounds = {}
    
    # Question: Classic arcade coin insert sound
    coin1 = generate_square(880, 0.06, 0.4)
    coin2 = generate_square(1760, 0.12, 0.4)
    env1 = generate_envelope(0.06, attack=0.002, decay=0.02, sustain=0.5, release=0.03)
    env2 = generate_envelope(0.12, attack=0.002, decay=0.04, sustain=0.5, release=0.06)
    coin1 = [s * e for s, e in zip(coin1, env1)]
    coin2 = [s * e for s, e in zip(coin2, env2)]
    sounds['question'] = coin1 + coin2
    
    # Error: Game over descending tone
    n_samples = int(SAMPLE_RATE * 0.4)
    descend = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq = 440 - t * 300  # Descend from 440Hz to 140Hz
        descend.append(0.4 * math.sin(2 * math.pi * freq * t))
    envelope = generate_envelope(0.4, attack=0.01, decay=0.1, sustain=0.5, release=0.25)
    descend = [s * e for s, e in zip(descend, envelope)]
    sounds['error'] = descend
    
    # Done: Victory jingle (classic arcade win)
    notes = [523, 659, 784, 1047]
    jingle = []
    for i, freq in enumerate(notes):
        note = generate_square(freq, 0.12, 0.4)
        env = generate_envelope(0.12, attack=0.002, decay=0.04, sustain=0.6, release=0.06)
        note = [s * e for s, e in zip(note, env)]
        jingle.extend(note)
    sounds['done'] = jingle
    
    return sounds

def main():
    """Generate all theme sounds."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, 'assets')
    
    themes = {
        'espionage': generate_espionage_sounds(),
        'hero': generate_hero_sounds(),
        'portal': generate_portal_sounds(),
        'premium': generate_premium_sounds(),
        'retro': generate_retro_sounds(),
    }
    
    for theme_name, sounds in themes.items():
        theme_dir = os.path.join(assets_dir, theme_name)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"  Theme: {theme_name.upper()}")
        print(f"{'='*60}")
        
        for sound_type, samples in sounds.items():
            filepath = os.path.join(theme_dir, f"{sound_type}.mp3")
            save_mp3(samples, filepath)
            duration = len(samples) / SAMPLE_RATE
            print(f"  ✓ {sound_type:10} - {duration:.2f}s ({len(samples):,} samples)")
    
    print(f"\n{'='*60}")
    print("  ✓ All sophisticated sounds generated!")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
