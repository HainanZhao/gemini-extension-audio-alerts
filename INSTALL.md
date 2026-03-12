# ✅ Installation Complete!

Thank you for installing the **Gemini Audio Alerts Extension**!

## How It Works

The hooks are defined in `hooks/hooks.json` and are **automatically loaded** by Gemini CLI when the extension is enabled. **No manual configuration required!**

## Verify Installation

```bash
# List extensions and verify it's enabled
gemini extensions list

# Test with a simple question
gemini "What is 2+2?"
```

You should hear audio alerts when Gemini asks questions or completes tasks.

## Troubleshooting

### Sounds not playing

1. **Check extension is enabled**:
   ```bash
   gemini extensions list
   ```

2. **Verify hooks.json exists**:
   ```bash
   ls ~/.gemini/extensions/audio-alerts/hooks/hooks.json
   ```

3. **Make sure script is executable**:
   ```bash
   chmod +x ~/.gemini/extensions/audio-alerts/hooks/handle_notification.sh
   ```

4. **Check volume** - Ensure your system volume is up

### Theme Not Changing

To change the theme permanently, use the `gemini settings` command or edit the extension's configuration file.

**Option 1: Use Gemini Settings (Recommended)**

```bash
gemini settings
```
Navigate to the "Audio Alerts" extension and select your desired theme from the dropdown menu.

**Option 2: Edit the Configuration File**

1.  Open the extension's environment file in your editor:
    ```bash
    open ~/.gemini/extensions/audio-alerts/.env
    ```

2.  Change the `AUDIO_ALERTS_THEME` value:
    ```dotenv
    AUDIO_ALERTS_THEME=retro
    ```

## Manual Configuration (Advanced)

If hooks aren't loading automatically, you can manually add them to `~/.gemini/settings.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "name": "notify-audio",
            "type": "command",
            "command": "${extensionPath}/hooks/handle_notification.sh --notification"
          }
        ]
      }
    ],
    "AfterAgent": [
      {
        "matcher": "*",
        "hooks": [
          {
            "name": "notify-done",
            "type": "command",
            "command": "${extensionPath}/hooks/handle_notification.sh --finished"
          }
        ]
      }
    ]
  }
}
```

---

See [README.md](README.md) for full documentation.
