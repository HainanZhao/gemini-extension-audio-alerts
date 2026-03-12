#!/usr/bin/env bash

# Installation script for Gemini Audio Alerts Extension
# This script verifies the hooks.json configuration and makes scripts executable
# Note: Hooks are now defined in hooks/hooks.json and loaded automatically by Gemini CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_PATH="$(cd "$SCRIPT_DIR/.." && pwd)"

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
log ""

# Verify hooks.json exists
HOOKS_JSON="$EXTENSION_PATH/hooks/hooks.json"
if [ ! -f "$HOOKS_JSON" ]; then
    echo "❌ Error: hooks/hooks.json not found!"
    echo ""
    echo "This file is required for the extension to work."
    echo "Please ensure the extension was installed correctly."
    exit 1
fi

log "✓ Found hooks/hooks.json"

# Verify hook script exists
HOOK_SCRIPT="$EXTENSION_PATH/hooks/handle_notification.sh"
if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "❌ Error: hooks/handle_notification.sh not found!"
    exit 1
fi

# Make the hook script executable
chmod +x "$HOOK_SCRIPT"
log "✓ Hook script made executable"

# Verify assets directory
ASSETS_DIR="$EXTENSION_PATH/assets"
if [ ! -d "$ASSETS_DIR" ]; then
    echo "⚠️  Warning: assets directory not found"
fi

log ""
log "✅ Installation complete!"
log ""
log "The hooks are defined in hooks/hooks.json and will be loaded automatically"
log "by Gemini CLI when the extension is enabled."
log ""
log "To verify, run: gemini extensions list"
log ""
log "Optional: Set a theme with:"
log "  export AUDIO_ALERTS_THEME=retro"
log ""
log "Add to your ~/.zshrc or ~/.bashrc to make it permanent."
