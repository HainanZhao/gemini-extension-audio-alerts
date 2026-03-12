#!/usr/bin/env python3
"""Generate simple sound effects for different themes using waveforms."""

import os
import wave
import struct
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

SAMPLE_RATE = 44100
DURATION = 0.3  # seconds

def generate_envelope(n_samples, attack=0.01, decay=0.1, sustain=0.7, release=0.3):
    """Generate ADSR envelope."""
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)
    release_samples = int(SAMPLE_RATE * release)
    sustain_end = n_samples - release_samples
    
    envelope = []
    for i in range(n_samples):
        if i < attack_samples:
            envelope.append(i / attack_samples)
        elif i < attack_samples + decay_samples:
            progress = (i - attack_samples) / decay_samples
            envelope.append(1.0 - (1.0 - sustain) * progress)
        elif i < sustain_end:
            envelope.append(sustain)
        else:
            progress = (i - sustain_end) / release_samples
            envelope.append(sustain * (1.0 - progress))
    return envelope

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE, volume=0.5):
    """Generate a sine wave with proper envelope."""
    n_samples = int(sample_rate * duration)
    samples = []
    envelope = generate_envelope(n_samples, attack=0.005, decay=0.05, sustain=0.6, release=0.2)
    
    for i in range(n_samples):
        t = i / sample_rate
        value = volume * math.sin(2 * math.pi * frequency * t)
        value *= envelope[i]
        samples.append(value)
    return samples

def generate_chime(frequencies, duration, sample_rate=SAMPLE_RATE):
    """Generate a rich chime with multiple harmonics."""
    n_samples = int(sample_rate * duration)
    samples = [0.0] * n_samples
    
    # Envelope with quick attack and long release
    envelope = generate_envelope(n_samples, attack=0.005, decay=0.1, sustain=0.5, release=0.4)
    
    for freq in frequencies:
        for i in range(n_samples):
            t = i / sample_rate
            # Add slight detuning for richer sound
            value = 0.25 * math.sin(2 * math.pi * freq * t)
            value += 0.1 * math.sin(2 * math.pi * freq * 2 * t)  # Octave
            value *= envelope[i]
            samples[i] += value
    
    # Normalize
    max_val = max(abs(s) for s in samples)
    if max_val > 0:
        samples = [s / max_val * 0.8 for s in samples]
    
    return samples

def generate_retro_sound(base_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a retro 8-bit style sound with better envelope."""
    n_samples = int(sample_rate * duration)
    samples = []
    period = sample_rate / base_freq
    
    envelope = generate_envelope(n_samples, attack=0.002, decay=0.05, sustain=0.8, release=0.1)
    
    for i in range(n_samples):
        # Square wave
        value = 0.4 if (i % int(period)) < period / 2 else -0.4
        value *= envelope[i]
        samples.append(value)
    
    return samples

def save_wav(samples, filepath, sample_rate=SAMPLE_RATE):
    """Save samples as WAV file."""
    n_samples = len(samples)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            # Convert to 16-bit integer
            value = int(sample * 32767)
            value = max(-32768, min(32767, value))
            wav_file.writeframes(struct.pack('<h', value))
    
    print(f"  ✓ Generated: {filepath} ({n_samples} samples)")

def generate_theme_sounds():
    """Generate sounds for all themes."""
    
    themes = {
        'default': {
            'question': {'type': 'chime', 'freqs': [880, 1100], 'duration': 0.25},  # Pleasant two-tone
            'error': {'type': 'tone', 'freq': 330, 'duration': 0.35},  # Soft low alert
            'done': {'type': 'chime', 'freqs': [523, 659, 784], 'duration': 0.5},  # Success chime (C major)
        },
        'espionage': {
            'question': {'type': 'tone', 'freq': 800, 'duration': 0.15},  # High-tech click
            'error': {'type': 'tone', 'freq': 200, 'duration': 0.4},  # Low warning
            'done': {'type': 'chime', 'freqs': [440, 660, 880], 'duration': 0.5},  # Success chord
        },
        'hero': {
            'question': {'type': 'chime', 'freqs': [523, 659, 784], 'duration': 0.4},  # Major triad
            'error': {'type': 'tone', 'freq': 150, 'duration': 0.5},  # Dramatic low
            'done': {'type': 'chime', 'freqs': [523, 659, 784, 1047], 'duration': 0.6},  # Victory fanfare
        },
        'portal': {
            'question': {'type': 'tone', 'freq': 1200, 'duration': 0.2},  # High whoosh start
            'error': {'type': 'tone', 'freq': 300, 'duration': 0.4},  # Block sound
            'done': {'type': 'chime', 'freqs': [880, 1100, 1320], 'duration': 0.5},  # Magical transition
        },
        'premium': {
            'question': {'type': 'chime', 'freqs': [1047, 1319], 'duration': 0.4},  # Elegant bell
            'error': {'type': 'tone', 'freq': 400, 'duration': 0.3},  # Soft warning
            'done': {'type': 'chime', 'freqs': [523, 659, 784, 988, 1175], 'duration': 0.7},  # Rich chord
        },
        'retro': {
            'question': {'type': 'retro', 'freq': 880, 'duration': 0.15},  # 8-bit blip
            'error': {'type': 'retro', 'freq': 220, 'duration': 0.4},  # 8-bit error
            'done': {'type': 'retro', 'freq': 1760, 'duration': 0.3},  # 8-bit win
        },
    }
    
    for theme, sounds in themes.items():
        theme_dir = os.path.join(ASSETS_DIR, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"Theme: {theme.upper()}")
        print(f"{'='*50}")
        
        for sound_type, config in sounds.items():
            filepath = os.path.join(theme_dir, f"{sound_type}.mp3")
            
            if config['type'] == 'tone':
                samples = generate_tone(config['freq'], config['duration'])
            elif config['type'] == 'chime':
                samples = generate_chime(config['freqs'], config['duration'])
            elif config['type'] == 'retro':
                samples = generate_retro_sound(config['freq'], config['duration'])
            else:
                samples = generate_tone(440, 0.2)
            
            # Save as WAV first, then we can convert if needed
            wav_path = filepath.replace('.mp3', '.wav')
            save_wav(samples, wav_path)
            
            # Also save as MP3-compatible WAV (most players accept .wav with .mp3 extension)
            # For true MP3, we'd need pydub or similar library

if __name__ == '__main__':
    generate_theme_sounds()
    print("\n✓ Sound generation complete!")
    print("Note: Files saved as .wav format (compatible with most audio players)")
