#!/usr/bin/env bash

# The Gemini CLI sets these environment variables when executing hooks
EXTENSION_PATH="${GEMINI_EXTENSION_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Read theme from environment variable, default to 'default'
THEME="${AUDIO_ALERTS_THEME:-default}"
# Normalize theme name to lowercase
THEME=$(echo "$THEME" | tr '[:upper:]' '[:lower:]')

# Verify theme directory exists, fallback to default if not
if [ ! -d "$EXTENSION_PATH/assets/$THEME" ]; then
  THEME="default"
fi

ASSETS_DIR="$EXTENSION_PATH/assets/$THEME"

# Cross-platform audio player detection
play_audio() {
  local file=$1
  if [[ "$OSTYPE" == "darwin"* ]]; then
    /usr/bin/afplay "$file" &
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v play >/dev/null 2>&1; then
      play -q "$file" &
    elif command -v mpg123 >/dev/null 2>&1; then
      mpg123 -q "$file" &
    elif command -v paplay >/dev/null 2>&1; then
      paplay "$file" &
    fi
  fi
}

# Read hook data from stdin
CONTEXT=$(cat)

# 1. Handle Notifications
if [[ "$1" == "--notification" ]]; then
  NOTIFICATION_TYPE=$(echo "$CONTEXT" | grep -o '"notification_type":"[^"]*"' | cut -d'"' -f4)
  
  # Case: ToolPermission (specifically ask_user)
  if [[ "$NOTIFICATION_TYPE" == "ToolPermission" ]] && echo "$CONTEXT" | grep -q '"type":"ask_user"'; then
    play_audio "$ASSETS_DIR/ping.mp3"
    play_audio "$ASSETS_DIR/question.mp3"
  
  # Case: Generic Errors
  elif echo "$CONTEXT" | grep -qi "error"; then
    play_audio "$ASSETS_DIR/error_ping.mp3"
    play_audio "$ASSETS_DIR/error.mp3"
  fi

# 2. Handle Agent Completion (AfterAgent Hook)
elif [[ "$1" == "--finished" ]]; then
  play_audio "$ASSETS_DIR/done.mp3"
fi

exit 0
