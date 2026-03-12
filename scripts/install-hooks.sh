#!/usr/bin/env bash

# Installation script for Gemini Audio Alerts Extension
# Installs hooks to ~/.gemini/hooks for use with Gemini CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_PATH="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="$HOME/.gemini/hooks"

# Parse arguments
QUIET=false
for arg in "$@"; do
    case $arg in
        --quiet) QUIET=true ;;
    esac
done

log() {
    if [ "$QUIET" = false ]; then
        echo "$@"
    fi
}

log "🔧 Gemini Audio Alerts Extension Installer"
log "=========================================="
log ""
log "Extension path: $EXTENSION_PATH"
log "Installing to: $TARGET_DIR"
log ""

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy hooks.json
cat > "$TARGET_DIR/hooks.json" << 'EOF'
{
  "hooks": {
    "Notification": [
      {
        "matcher": "ToolPermission",
        "hooks": [
          {
            "name": "notify-permission",
            "type": "command",
            "command": "$HOME/.gemini/hooks/handle_notification.sh --notification"
          }
        ]
      },
      {
        "matcher": "ToolExecutionError",
        "hooks": [
          {
            "name": "notify-error",
            "type": "command",
            "command": "$HOME/.gemini/hooks/handle_notification.sh --notification --error"
          }
        ]
      }
    ],
    "BeforeTool": [
      {
        "matcher": "ask_user",
        "hooks": [
          {
            "name": "ask-user-alert",
            "type": "command",
            "command": "$HOME/.gemini/hooks/handle_notification.sh --before-tool"
          }
        ]
      }
    ],
    "BeforeAgent": [
      {
        "matcher": "*",
        "hooks": [
          {
            "name": "record-start",
            "type": "command",
            "command": "$HOME/.gemini/hooks/handle_notification.sh --before"
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
            "command": "$HOME/.gemini/hooks/handle_notification.sh --finished"
          }
        ]
      }
    ]
  }
}
EOF
log "✓ Installed hooks.json"

# Copy hook script
cp "$EXTENSION_PATH/hooks/handle_notification.sh" "$TARGET_DIR/"
chmod +x "$TARGET_DIR/handle_notification.sh"
log "✓ Installed handle_notification.sh"

# Copy assets
rm -rf "$HOME/.gemini/assets"
cp -r "$EXTENSION_PATH/assets" "$HOME/.gemini/"
log "✓ Installed assets"

log ""
log "✅ Installation complete!"
log ""
log "Audio alerts are now installed in ~/.gemini/hooks/"
log ""
log "Optional: Set a theme with:"
log "  export AUDIO_ALERTS_THEME=retro"
log ""
log "Add to your ~/.zshrc or ~/.bashrc to make it permanent."
