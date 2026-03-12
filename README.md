# Gemini Extension: Audio Alerts

Custom audio alerts for Gemini CLI to solve the **"Silent Hang"** issue in IDE terminals like VS Code.

## Problem
System notifications are often suppressed in IDE terminals, causing sessions to "hang" when Gemini waits for user input without any audible alert.

## Solution
Direct audio alerts triggered via Gemini's hook system when:
- Gemini requests tools permission
- A task completes
- An error occurs

## Installation

```bash
# Install extension
gemini extensions install https://github.com/HainanZhao/gemini-extension-audio-alerts
```

## Important: Enable Notifications

**This extension requires notifications to be enabled in Gemini settings.**

Enable notifications using:
```
/settings
```

Without notifications enabled, the audio alerts will not trigger for some events.

## Configuration (Optional)

For a permanent theme setting, create a configuration file:

```bash
# Create the config file
touch ~/.gemini/audio_alerts.conf

# Add your preferred theme
echo "AUDIO_ALERTS_THEME=retro" > ~/.gemini/audio_alerts.conf
```

The extension will read this file automatically. An environment variable (`AUDIO_ALERTS_THEME`) can still be used to override the config file for a single session.

## Sound Themes

| Theme | Style |
|-------|-------|
| default | Agent thriller |
| retro | 8-bit video game |
| portal | Sci-fi |
| hero | Cinematic |
| premium | Elegant |

To change the theme, edit `~/.gemini/audio_alerts.conf` or set an environment variable (see above).

## How It Works

Hooks are defined in `hooks/hooks.json`:
- **Notification** (`ToolPermission`) → Question sound (standalone terminal)
- **AfterAgent** → Completion sound (skips TTS if < 60s)

## Requirements

- **macOS**: Built-in `afplay`
- **Linux**: `sox`, `mpg123`, or `paplay`

## License

ISC License
