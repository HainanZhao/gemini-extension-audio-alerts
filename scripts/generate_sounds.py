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

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE, volume=0.5):
    """Generate a simple sine wave tone."""
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        value = volume * math.sin(2 * math.pi * frequency * t)
        # Apply fade out
        fade = 1.0 - (i / n_samples)
        value *= fade
        samples.append(value)
    return samples

def generate_chime(frequencies, duration, sample_rate=SAMPLE_RATE):
    """Generate a chime with multiple frequencies."""
    n_samples = int(sample_rate * duration)
    samples = [0.0] * n_samples
    
    for freq in frequencies:
        for i in range(n_samples):
            t = i / sample_rate
            value = 0.3 * math.sin(2 * math.pi * freq * t)
            # Apply exponential decay
            decay = math.exp(-3 * t / duration)
            samples[i] += value * decay
    
    # Normalize
    max_val = max(abs(s) for s in samples)
    if max_val > 0:
        samples = [s / max_val * 0.8 for s in samples]
    
    return samples

def generate_retro_sound(base_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a retro 8-bit style sound with square wave."""
    n_samples = int(sample_rate * duration)
    samples = []
    period = sample_rate / base_freq
    
    for i in range(n_samples):
        t = i / sample_rate
        # Square wave
        value = 0.5 if (i % int(period)) < period / 2 else -0.5
        # Apply envelope
        envelope = 1.0 - (i / n_samples)
        samples.append(value * envelope)
    
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
            
            # Save as WAV first, then we can convert if needed
            wav_path = filepath.replace('.mp3', '.wav')
            save_wav(samples, wav_path)
            
            # Also save as MP3-compatible WAV (most players accept .wav with .mp3 extension)
            # For true MP3, we'd need pydub or similar library

if __name__ == '__main__':
    generate_theme_sounds()
    print("\n✓ Sound generation complete!")
    print("Note: Files saved as .wav format (compatible with most audio players)")
