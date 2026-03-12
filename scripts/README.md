# Sound Generation System

This directory contains scripts for generating themed sound effects for the Gemini Extension Audio Alerts.

## Overview

The sound generator uses **ffmpeg** to synthesize custom audio alerts for each theme. Each theme has a unique character:

- **Default**: Clean, modern notification sounds
- **Retro**: 8-bit video game style sounds
- **Portal**: Sci-fi portal and teleportation effects
- **Espionage**: Spy thriller and secret agent sounds
- **Hero**: Epic superhero and cinematic sounds
- **Premium**: Luxury and high-end product sounds

## Requirements

- **ffmpeg**: Must be installed on your system
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`
- **Python 3**: For running the generation script

## Usage

### Generate All Sounds

To regenerate sounds for all themes:

```bash
cd scripts
./generate_sound.py --all
```

### Generate Specific Theme

To generate sounds for a specific theme:

```bash
./generate_sound.py --theme retro --type ping --output ../assets/retro/ping.mp3
```

### Available Options

```
--theme <name>   Theme name (default, retro, portal, espionage, hero, premium)
--type <type>    Sound type (ping, question, error, error_ping, done)
--output <path>  Output file path
--all            Generate all sounds for all themes
```

## Sound Types

Each theme includes 5 sound types:

1. **ping**: Notification alert (for tool permissions)
2. **question**: Question alert (when Gemini asks for input)
3. **error**: Error notification
4. **error_ping**: Error prefix alert
5. **done**: Completion notification

## Customization

To customize sounds, edit the `THEME_CONFIGS` dictionary in `generate_sound.py`. Each sound can be configured with:

- **frequencies**: List of musical note frequencies (in Hz)
- **duration**: Total sound duration (in seconds)
- **waveform**: Waveform type (sine, square, sawtooth)
- **effects**: Audio effects (reverb, echo, vibrato, etc.)

### Example Configuration

```python
"ping": {
    "frequencies": [523.25, 659.25, 783.99],  # C5, E5, G5
    "duration": 0.4,
    "waveform": "sine",
    "reverb": False,
    "description": "Pleasant three-note ascending chime"
}
```

## Note Frequencies Reference

Standard musical note frequencies (Hz):

```
C4: 261.63    D4: 293.66    E4: 329.63    F4: 349.23    G4: 392.00    A4: 440.00    B4: 493.88
C5: 523.25    D5: 587.33    E5: 659.25    F5: 698.46    G5: 783.99    A5: 880.00    B5: 987.77
C6: 1046.50   D6: 1174.66   E6: 1318.51   F6: 1396.91   G6: 1567.98
```

## Troubleshooting

### ffmpeg not found
Install ffmpeg using your package manager:
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Fedora: `sudo dnf install ffmpeg`

### Permission denied
Make the script executable:
```bash
chmod +x generate_sound.py
```

### Sounds too quiet/loud
Adjust the `volume` parameter in the `apply_effects()` function.

## Future Enhancements

Potential improvements for the sound generation system:

1. **Qwen API Integration**: Use Qwen's audio generation API for more complex sounds
2. **Custom themes**: Allow users to create their own theme configurations
3. **Sound preview**: Add a preview feature to test sounds before generating
4. **Batch export**: Export sounds in multiple formats (MP3, WAV, OGG)
5. **Advanced effects**: Add more audio effects (chorus, flanger, phaser)

## License

This sound generation system is part of the Gemini Extension Audio Alerts project.
