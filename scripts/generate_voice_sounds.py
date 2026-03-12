#!/usr/bin/env python3
"""
Simple Voice Sound Generator for Gemini Extension
Uses macOS 'say' command to create clear voice announcements
"""

import argparse
import os
import subprocess
import tempfile
import shutil

# Theme configurations with voice messages
THEME_CONFIGS = {
    "default": {
        "description": "Original sounds with voice announcements",
        "voice": "Samantha",
        "sounds": {
            "ping": {
                "voice_message": "Tool permission required",
                "description": "Voice: 'Tool permission required'"
            },
            "question": {
                "voice_message": "Gemini has a question",
                "use_original": True,
                "description": "Using original question.mp3"
            },
            "error": {
                "voice_message": "Error occurred",
                "description": "Voice: 'Error occurred'"
            },
            "error_ping": {
                "voice_message": "Warning",
                "description": "Voice: 'Warning'"
            },
            "done": {
                "voice_message": "Task completed",
                "description": "Voice: 'Task completed'"
            }
        }
    },
    "retro": {
        "description": "8-bit game style with retro voice",
        "voice": "Fred",
        "sounds": {
            "ping": {
                "voice_message": "Player one, input required",
                "description": "Retro: 'Player one, input required'"
            },
            "question": {
                "voice_message": "Choose your answer",
                "description": "Retro: 'Choose your answer'"
            },
            "error": {
                "voice_message": "Game over, try again",
                "description": "Retro: 'Game over, try again'"
            },
            "error_ping": {
                "voice_message": "Damage taken",
                "description": "Retro: 'Damage taken'"
            },
            "done": {
                "voice_message": "Level complete",
                "description": "Retro: 'Level complete'"
            }
        }
    },
    "portal": {
        "description": "Sci-fi AI voice",
        "voice": "Fred",
        "sounds": {
            "ping": {
                "voice_message": "Authorization required",
                "description": "Sci-fi: 'Authorization required'"
            },
            "question": {
                "voice_message": "Decision point detected",
                "description": "Sci-fi: 'Decision point detected'"
            },
            "error": {
                "voice_message": "Portal malfunction",
                "description": "Sci-fi: 'Portal malfunction'"
            },
            "error_ping": {
                "voice_message": "Containment breach",
                "description": "Sci-fi: 'Containment breach'"
            },
            "done": {
                "voice_message": "Transit complete",
                "description": "Sci-fi: 'Transit complete'"
            }
        }
    },
    "espionage": {
        "description": "Spy thriller voice",
        "voice": "Fred",
        "sounds": {
            "ping": {
                "voice_message": "Secure channel incoming",
                "description": "Spy: 'Secure channel incoming'"
            },
            "question": {
                "voice_message": "Intel required",
                "description": "Spy: 'Intel required'"
            },
            "error": {
                "voice_message": "Mission compromised",
                "description": "Spy: 'Mission compromised'"
            },
            "error_ping": {
                "voice_message": "Security alert",
                "description": "Spy: 'Security alert'"
            },
            "done": {
                "voice_message": "Mission accomplished",
                "description": "Spy: 'Mission accomplished'"
            }
        }
    },
    "hero": {
        "description": "Epic cinematic narrator",
        "voice": "Fred",
        "sounds": {
            "ping": {
                "voice_message": "Hero, your power is needed",
                "description": "Epic: 'Hero, your power is needed'"
            },
            "question": {
                "voice_message": "A critical choice awaits",
                "description": "Epic: 'A critical choice awaits'"
            },
            "error": {
                "voice_message": "The hero has been wounded",
                "description": "Epic: 'The hero has been wounded'"
            },
            "error_ping": {
                "voice_message": "Danger approaches",
                "description": "Epic: 'Danger approaches'"
            },
            "done": {
                "voice_message": "Victory is ours",
                "description": "Epic: 'Victory is ours'"
            }
        }
    },
    "premium": {
        "description": "Elegant butler voice",
        "voice": "Fred",
        "sounds": {
            "ping": {
                "voice_message": "Your decision is required",
                "description": "Butler: 'Your decision is required'"
            },
            "question": {
                "voice_message": "For your consideration",
                "description": "Butler: 'For your consideration'"
            },
            "error": {
                "voice_message": "An error has occurred",
                "description": "Butler: 'An error has occurred'"
            },
            "error_ping": {
                "voice_message": "Your attention, please",
                "description": "Butler: 'Your attention, please'"
            },
            "done": {
                "voice_message": "Everything is complete",
                "description": "Butler: 'Everything is complete'"
            }
        }
    }
}


def generate_voice_message(text, output_file, voice="Samantha", rate=100):
    """Generate voice message using macOS 'say' command and save as MP3"""
    temp_dir = tempfile.mkdtemp()
    try:
        aiff_file = os.path.join(temp_dir, "voice.aiff")
        
        # Generate voice with say command
        cmd = [
            "say",
            "-v", voice,
            "-r", str(rate),
            "-o", aiff_file,
            text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  say command error: {result.stderr}")
            return False
        
        # Check if AIFF file was created
        if not os.path.exists(aiff_file):
            print(f"  AIFF file not created")
            return False
        
        # Convert AIFF to MP3 using ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", aiff_file,
            "-b:a", "128k",
            "-ar", "44100",
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ffmpeg error: {result.stderr}")
            return False
        
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def generate_sound_with_voice(theme, sound_type, output_path):
    """Generate a voice announcement"""
    theme_config = THEME_CONFIGS.get(theme, THEME_CONFIGS["default"])
    sound_config = theme_config["sounds"].get(sound_type, theme_config["sounds"]["ping"])
    
    voice_message = sound_config.get("voice_message", "")
    description = sound_config.get("description", "")
    use_original = sound_config.get("use_original", False)
    
    print(f"  Generating: {theme}/{sound_type}")
    print(f"  {description}")
    
    # Check if using original file
    if use_original:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        original_file = os.path.join(script_dir, "assets", "default", "question.mp3")
        if os.path.exists(original_file):
            print(f"  ✓ Using original: {original_file}")
            return True
        else:
            print(f"  ⚠ Original not found, generating with voice")
    
    # Generate voice message
    voice = theme_config.get("voice", "Samantha")
    success = generate_voice_message(voice_message, output_path, voice)
    
    if success:
        print(f"  ✓ Generated: {output_path}")
    else:
        print(f"  ✗ Failed: {output_path}")
    
    return success


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
    
    print(f"Generating {total} voice announcements for {len(themes)} themes...\n")
    
    for theme in themes:
        theme_dir = os.path.join(assets_dir, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Theme: {theme.upper()}")
        print(f"Description: {THEME_CONFIGS[theme]['description']}")
        print(f"Voice: {THEME_CONFIGS[theme].get('voice', 'Samantha')}")
        print(f"{'='*60}")
        
        for sound_type in sound_types:
            output_path = os.path.join(theme_dir, f"{sound_type}.mp3")
            if generate_sound_with_voice(theme, sound_type, output_path):
                success_count += 1
            count += 1
            print()
    
    print(f"\n{'='*60}")
    print(f"✓ Generated {success_count}/{count} voice announcements!")
    print(f"{'='*60}")
    
    return success_count == count


def main():
    parser = argparse.ArgumentParser(
        description="Generate voice announcements for Gemini Extension"
    )
    parser.add_argument("--theme", help="Theme name")
    parser.add_argument("--type", choices=["ping", "question", "error", "error_ping", "done"],
                       help="Sound type")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--all", action="store_true", help="Generate all sounds")
    
    args = parser.parse_args()
    
    if args.all:
        success = generate_all_sounds()
        import sys
        sys.exit(0 if success else 1)
    elif args.theme and args.type and args.output:
        if args.theme not in THEME_CONFIGS:
            print(f"Error: Unknown theme '{args.theme}'")
            import sys
            sys.exit(1)
        success = generate_sound_with_voice(args.theme, args.type, args.output)
        import sys
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
