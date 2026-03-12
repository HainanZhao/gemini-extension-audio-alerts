# Gemini Extension: Audio Alerts (macOS/Linux)

Custom audio alerts for Gemini CLI, specifically designed to solve the **"Silent Hang"** issue when running inside IDE terminals like VS Code.

## The Problem
Built-in system notifications are often suppressed, delayed, or hidden when running the Gemini CLI in an integrated editor terminal. This leads to sessions that "hang" because the user is unaware the agent is waiting for an `ask_user` prompt.

## The Solution
This extension uses the `Notification` hook system to trigger direct audio alerts the moment an interactive question is prompted. Features **6 unique themed sound packs** with procedurally generated audio effects.

## Features
- **Surgical Precision**: Only alerts on `ask_user` tool permissions.
- **Immediate Response**: Triggers simultaneously with the prompt appearance.
- **6 Themed Sound Packs**: Choose from retro (default), portal, default, hero, or premium themes.
- **Custom Sound Generation**: Generate your own custom sounds using the included Python script.
- **Cross-Platform**: Works on macOS (afplay) and Linux (play, mpg123, or paplay).

## Sound Themes

| Theme | Description | Style |
|-------|-------------|-------|
| **Retro**  | 8-bit video game style sounds | Nostalgic |
| **Portal** | Sci-fi portal and teleportation effects | Futuristic |
| **default** | Spy thriller and secret agent sounds | Mysterious |
| **Hero** | Epic superhero and cinematic sounds | Dramatic |
| **Premium** | Luxury and high-end product sounds | Elegant |

## Installation

### Quick Install

```bash
gemini extensions install https://github.com/HainanZhao/gemini-extension-audio-alerts
```

Then run the installation script to verify setup:

```bash
cd ~/.gemini/extensions/gemini-audio-alerts
./scripts/install-hooks.sh
```

**That's it!** The hooks are defined in `hooks/hooks.json` and are **automatically loaded** by Gemini CLI when the extension is enabled. No manual `settings.json` configuration required!

### How It Works

1. **Extension Install**: `gemini extensions install` copies the extension to `~/.gemini/extensions/`
2. **Automatic Hook Loading**: Gemini CLI reads `hooks/hooks.json` from the extension directory
3. **Hooks Activated**: The hooks are automatically active when the extension is enabled

### Manual Install (Alternative)

1. Clone or copy this folder to `~/.gemini/extensions/gemini-audio-alerts`
2. Run `./scripts/install-hooks.sh` to make scripts executable
3. Restart Gemini CLI

### Verify Installation

```bash
# List extensions and verify it's enabled
gemini extensions list

# Test with a simple question
gemini "What is 2+2?"
```

You should hear audio alerts when Gemini asks questions or completes tasks.

## Configuration

### Change Theme

Set the `AUDIO_ALERTS_THEME` environment variable:

```bash
export AUDIO_ALERTS_THEME=portal  # Options: retro (default), portal, default, hero, premium
```

Add to your shell config (`~/.zshrc` or `~/.bashrc`) to make it permanent.

### Custom Sounds

Generate custom sounds using the included script:

```bash
cd scripts
./generate_sound.py --all  # Generate all themes
./generate_sound.py --theme retro --type ping --output ../assets/retro/ping.mp3
```

See [scripts/README.md](scripts/README.md) for detailed documentation.

## Requirements
- **macOS**: Built-in `afplay` (included)
- **Linux**: Requires `sox` (`play` command), `mpg123`, or `pulseaudio-utils` (`paplay`)
- **Gemini CLI** with hook support
- **Python 3** (optional, for custom sound generation)
- **ffmpeg** (optional, for custom sound generation)

## Sound Generation (Optional)

If you want to customize or regenerate the sound effects:

1. Install ffmpeg:
   ```bash
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt install ffmpeg
   ```

2. Run the sound generator:
   ```bash
   cd scripts
   ./generate_sound.py --all
   ```

This uses procedural audio synthesis to generate unique sound effects for each theme. No API key required!

## Troubleshooting

### Sounds not playing
- **macOS**: Ensure volume is up and `afplay` is available
- **Linux**: Install required audio tools: `sudo apt install sox mpg123`

### Theme not changing
- Verify the environment variable is set: `echo $AUDIO_ALERTS_THEME`
- Restart your terminal or run `source ~/.zshrc`

### Custom sounds not working
- Ensure MP3 files are valid and not corrupted
- Check file permissions: `chmod 644 assets/*/ *.mp3`

## License

ISC License - See LICENSE file for details.
