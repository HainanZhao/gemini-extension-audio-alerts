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
### Manual Configuration

You can edit the `.env` file directly.
1.  **Locate the extension directory**: `~/.gemini/extensions/audio-alerts`
2.  **Edit the environment file**:
    ```bash
    # Open the .env file in your editor
    open ~/.gemini/extensions/audio-alerts/.env
    ```
3.  **Set the variables**:
    ```dotenv
    # Set your preferred theme (default, retro, portal, hero, premium)
    AUDIO_ALERTS_THEME=retro

    # Enable debug logging (optional, 1=enabled, 0=disabled)
    AUDIO_ALERTS_DEBUG=0

    # Disable Text-to-Speech (TTS) completely (true or false)
    AUDIO_ALERTS_DISABLE_TTS=false
    ```

Changes to the `.env` file are loaded automatically by Gemini CLI.

## Sound Themes

| Theme | Style |
|-------|-------|
| default | Agent thriller |
| retro | 8-bit video game |
| portal | Sci-fi |
| hero | Cinematic |
| premium | Elegant |

To change the theme, use the `gemini settings` command or edit the `~/.gemini/extensions/audio-alerts/.env` file.

## How It Works

Hooks are defined in `hooks/hooks.json`:
- **Notification** (`ToolPermission`) → Question sound (standalone terminal)
- **AfterAgent** → Completion sound (skips TTS if < 30s)

## Requirements

- **macOS**: Built-in `afplay`
- **Linux**: `sox`, `mpg123`, or `paplay`

## License

ISC License
