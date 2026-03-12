#!/usr/bin/env python3
"""
Sound Generator for Gemini Extension Audio Alerts
Uses ffmpeg to synthesize themed sound effects
"""

import argparse
import os
import subprocess
import sys
import tempfile

# Theme configurations with fun sound characteristics
THEME_CONFIGS = {
    "default": {
        "description": "Clean, modern notification sounds",
        "sounds": {
            "ping": {
                "type": "chime",
                "frequencies": [523.25, 659.25, 783.99],  # C5, E5, G5
                "duration": 0.4,
                "description": "Pleasant three-note ascending chime"
            },
            "question": {
                "type": "arpeggio",
                "frequencies": [392.0, 523.25, 659.25, 783.99],  # G4, C5, E5, G5
                "duration": 0.6,
                "description": "Gentle rising arpeggio, curious and inviting"
            },
            "error": {
                "type": "warning",
                "frequencies": [261.63, 220.0],  # C4, A3 (descending)
                "duration": 0.5,
                "description": "Descending two-tone warning"
            },
            "error_ping": {
                "type": "alert",
                "frequencies": [261.63],
                "duration": 0.15,
                "description": "Sharp alert beep"
            },
            "done": {
                "type": "fanfare",
                "frequencies": [523.25, 659.25, 783.99, 1046.50],  # C5, E5, G5, C6
                "duration": 0.6,
                "description": "Triumphant major chord arpeggio"
            }
        }
    },
    "retro": {
        "description": "8-bit video game style sounds",
        "sounds": {
            "ping": {
                "type": "coin",
                "frequencies": [1046.50, 1318.51],  # C6, E6
                "duration": 0.2,
                "waveform": "square",
                "description": "Classic 8-bit coin pickup sound"
            },
            "question": {
                "type": "powerup",
                "frequencies": [523.25, 587.33, 659.25, 698.46],  # C5, D5, E5, F5
                "duration": 0.3,
                "waveform": "square",
                "description": "Retro game power-up sequence"
            },
            "error": {
                "type": "damage",
                "frequencies": [261.63, 246.94, 220.0],  # C4, B3, A3
                "duration": 0.3,
                "waveform": "sawtooth",
                "description": "Classic video game damage sound"
            },
            "error_ping": {
                "type": "alert",
                "frequencies": [261.63],
                "duration": 0.12,
                "waveform": "square",
                "description": "Sharp 8-bit alert beep"
            },
            "done": {
                "type": "victory",
                "frequencies": [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98],
                "duration": 0.4,
                "waveform": "square",
                "description": "Victory fanfare, level complete"
            }
        }
    },
    "portal": {
        "description": "Sci-fi portal and teleportation effects",
        "sounds": {
            "ping": {
                "type": "sweep",
                "frequencies": [523.25],
                "duration": 0.5,
                "sweep": True,
                "description": "Ethereal portal activation hum"
            },
            "question": {
                "type": "alien",
                "frequencies": [392.0, 523.25, 783.99],
                "duration": 0.6,
                "modulation": True,
                "description": "Mysterious alien communication signal"
            },
            "error": {
                "type": "malfunction",
                "frequencies": [130.81, 65.41],  # C3, C2
                "duration": 0.6,
                "sweep_down": True,
                "description": "Portal malfunction alarm"
            },
            "error_ping": {
                "type": "system_alert",
                "frequencies": [1046.50],
                "duration": 0.15,
                "description": "Sharp system alert beep"
            },
            "done": {
                "type": "stabilize",
                "frequencies": [261.63, 329.63, 392.0, 523.25],
                "duration": 0.7,
                "reverb": True,
                "description": "Portal stabilization complete"
            }
        }
    },
    "espionage": {
        "description": "Spy thriller and secret agent sounds",
        "sounds": {
            "ping": {
                "type": "encrypted",
                "frequencies": [261.63],
                "duration": 0.35,
                "vibrato": True,
                "description": "Encrypted message received tone"
            },
            "question": {
                "type": "covert",
                "frequencies": [196.0, 261.63, 293.66],
                "duration": 0.5,
                "echo": True,
                "description": "Covert inquiry signal"
            },
            "error": {
                "type": "compromised",
                "frequencies": [130.81, 98.0],
                "duration": 0.5,
                "distortion": True,
                "description": "Compromised mission alert"
            },
            "error_ping": {
                "type": "urgent",
                "frequencies": [523.25],
                "duration": 0.12,
                "description": "Urgent encrypted alert"
            },
            "done": {
                "type": "mission_accomplished",
                "frequencies": [261.63, 392.0, 523.25],
                "duration": 0.6,
                "reverb": True,
                "description": "Mission accomplished spy sting"
            }
        }
    },
    "hero": {
        "description": "Epic superhero and cinematic sounds",
        "sounds": {
            "ping": {
                "type": "heroic",
                "frequencies": [523.25, 783.99],
                "duration": 0.45,
                "reverb": True,
                "description": "Heroic call to attention"
            },
            "question": {
                "type": "noble",
                "frequencies": [392.0, 523.25, 659.25, 783.99],
                "duration": 0.6,
                "reverb": True,
                "description": "Noble inquiry, quest invitation"
            },
            "error": {
                "type": "peril",
                "frequencies": [261.63, 220.0, 174.61],
                "duration": 0.6,
                "dramatic": True,
                "description": "Hero in peril warning"
            },
            "error_ping": {
                "type": "battle_alert",
                "frequencies": [523.25],
                "duration": 0.2,
                "description": "Urgent battle alert"
            },
            "done": {
                "type": "victory_theme",
                "frequencies": [261.63, 329.63, 392.0, 523.25, 659.25, 783.99, 1046.50],
                "duration": 0.8,
                "epic": True,
                "description": "Victory theme, epic fanfare"
            }
        }
    },
    "premium": {
        "description": "Luxury and high-end product sounds",
        "sounds": {
            "ping": {
                "type": "refined",
                "frequencies": [1046.50],
                "duration": 0.35,
                "soft": True,
                "description": "Refined luxury notification chime"
            },
            "question": {
                "type": "elegant",
                "frequencies": [783.99, 1046.50, 1318.51],
                "duration": 0.5,
                "soft": True,
                "description": "Elegant inquiry arpeggio"
            },
            "error": {
                "type": "polite",
                "frequencies": [261.63, 196.0],
                "duration": 0.5,
                "muted": True,
                "description": "Polite sophisticated error"
            },
            "error_ping": {
                "type": "subtle",
                "frequencies": [523.25],
                "duration": 0.15,
                "description": "Subtle attention getter"
            },
            "done": {
                "type": "crystal",
                "frequencies": [523.25, 659.25, 783.99, 1046.50],
                "duration": 0.6,
                "crystal": True,
                "description": "Luxury crystal completion chime"
            }
        }
    }
}


def generate_tone_file(frequency, duration, output_file, waveform="sine"):
    """Generate a single tone using ffmpeg's sine/square/sawtooth source"""
    # Use ffmpeg's built-in audio sources
    if waveform == "square":
        # Create square wave using anote filter
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={frequency}:duration={duration}",
            "-af", "volume=0.8",
            "-b:a", "192k",
            output_file
        ]
    elif waveform == "sawtooth":
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={frequency}:duration={duration}",
            "-af", "volume=0.8",
            "-b:a", "192k",
            output_file
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={frequency}:duration={duration}",
            "-af", "volume=0.8",
            "-b:a", "192k",
            output_file
        ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr.decode()}")
        return False


def concatenate_audio_files(input_files, output_file):
    """Concatenate multiple audio files using ffmpeg"""
    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for file in input_files:
            f.write(f"file '{file}'\n")
        concat_file = f.name
    
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        os.unlink(concat_file)
        return True
    except subprocess.CalledProcessError as e:
        os.unlink(concat_file)
        return False


def apply_effects(input_file, output_file, effects_config, total_duration):
    """Apply audio effects using ffmpeg"""
    filters = []
    
    # Add fade in/out
    fade_in = min(0.02, total_duration * 0.1)
    fade_out = min(0.05, total_duration * 0.15)
    filters.append(f"afade=t=in:st=0:d={fade_in}")
    filters.append(f"afade=t=out:st={total_duration-fade_out}:d={fade_out}")
    
    # Add reverb/echo
    if effects_config.get("reverb") or effects_config.get("epic"):
        filters.append("aecho=0.8:0.9:1000:0.5")
    
    if effects_config.get("crystal"):
        filters.append("aecho=0.3:0.2:50:0.3")
    
    if effects_config.get("echo"):
        filters.append("aecho=0.8:0.8:200:0.5")
    
    if effects_config.get("vibrato"):
        filters.append("vibrato=f=6:d=0.5")
    
    # Volume adjustment
    if effects_config.get("muted"):
        filters.append("volume=0.5")
    else:
        filters.append("volume=0.7")
    
    filter_str = ",".join(filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-af", filter_str,
        "-b:a", "192k",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error applying effects: {e.stderr.decode()}")
        return False


def generate_sound(theme, sound_type, output_path):
    """Generate a sound effect for the given theme"""
    theme_config = THEME_CONFIGS.get(theme, THEME_CONFIGS["default"])
    sound_config = theme_config["sounds"].get(sound_type, theme_config["sounds"]["ping"])
    
    frequencies = sound_config.get("frequencies", [523.25])
    duration = sound_config.get("duration", 0.3)
    waveform = sound_config.get("waveform", "sine")
    description = sound_config.get("description", "Sound effect")
    
    print(f"  Generating: {theme}/{sound_type}")
    print(f"  {description}")
    
    # Create temp directory for intermediate files
    temp_dir = tempfile.mkdtemp()
    temp_files = []
    
    try:
        # Generate each tone
        note_duration = duration / len(frequencies)
        for i, freq in enumerate(frequencies):
            temp_file = os.path.join(temp_dir, f"tone_{i}.mp3")
            if generate_tone_file(freq, note_duration, temp_file, waveform):
                temp_files.append(temp_file)
        
        if not temp_files:
            print(f"  ✗ Failed to generate tones")
            return False
        
        # Concatenate tones
        combined_file = os.path.join(temp_dir, "combined.mp3")
        if not concatenate_audio_files(temp_files, combined_file):
            print(f"  ✗ Failed to concatenate tones")
            return False
        
        # Apply effects
        success = apply_effects(combined_file, output_path, sound_config, duration)
        
        if success:
            print(f"  ✓ Generated: {output_path}")
        else:
            print(f"  ✗ Failed: {output_path}")
        
        return success
        
    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def generate_all_sounds():
    """Generate all sounds for all themes"""
    themes = list(THEME_CONFIGS.keys())
    sound_types = ["ping", "question", "error", "error_ping", "done"]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    extension_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(extension_root, "assets")
    
    total = len(themes) * len(sound_types)
    count = 0
    success_count = 0
    
    print(f"Generating {total} sounds for {len(themes)} themes...\n")
    
    for theme in themes:
        theme_dir = os.path.join(assets_dir, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"Theme: {theme.upper()}")
        print(f"Description: {THEME_CONFIGS[theme]['description']}")
        print(f"{'='*50}")
        
        for sound_type in sound_types:
            output_path = os.path.join(theme_dir, f"{sound_type}.mp3")
            if generate_sound(theme, sound_type, output_path):
                success_count += 1
            count += 1
            print()
    
    print(f"\n{'='*50}")
    print(f"✓ Generated {success_count}/{count} sounds successfully!")
    print(f"{'='*50}")
    
    return success_count == count


def main():
    parser = argparse.ArgumentParser(
        description="Generate themed sound effects for Gemini Extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --theme retro --type ping --output ./assets/retro/ping.mp3
  %(prog)s --all  # Generate all sounds for all themes
        """
    )
    parser.add_argument("--theme", help="Theme name (default, retro, portal, espionage, hero, premium)")
    parser.add_argument("--type", choices=["ping", "question", "error", "error_ping", "done"],
                       help="Sound type")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--all", action="store_true", help="Generate all sounds for all themes")
    
    args = parser.parse_args()
    
    if args.all:
        success = generate_all_sounds()
        sys.exit(0 if success else 1)
    elif args.theme and args.type and args.output:
        if args.theme not in THEME_CONFIGS:
            print(f"Error: Unknown theme '{args.theme}'")
            print(f"Available themes: {', '.join(THEME_CONFIGS.keys())}")
            sys.exit(1)
        success = generate_sound(args.theme, args.type, args.output)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
