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
   ls ~/.gemini/extensions/gemini-audio-alerts/hooks/hooks.json
   ```

3. **Make sure script is executable**:
   ```bash
   chmod +x ~/.gemini/extensions/gemini-audio-alerts/hooks/handle_notification.sh
   ```

4. **Check volume** - Ensure your system volume is up

### Theme not changing

Set the environment variable:
```bash
export AUDIO_ALERTS_THEME=retro  # Options: default, retro, portal, default, hero, premium
```

Add to your `~/.zshrc` or `~/.bashrc` to make it permanent.

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
