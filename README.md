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

## Sound Themes

| Theme | Style |
|-------|-------|
| default | Agent thriller |
| retro | 8-bit video game |
| portal | Sci-fi |
| hero | Cinematic |
| premium | Elegant |

Change theme:
```bash
export AUDIO_ALERTS_THEME=portal  # Add to ~/.zshrc
```

## How It Works

Hooks are defined in `hooks/hooks.json`:
- **Notification** (`ToolPermission`) → Question sound (standalone terminal)
- **AfterAgent** → Completion sound (skips TTS if < 60s)

## Requirements

- **macOS**: Built-in `afplay`
- **Linux**: `sox`, `mpg123`, or `paplay`

## License

ISC License
