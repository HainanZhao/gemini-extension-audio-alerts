#!/usr/bin/env bash

# The Gemini CLI sets these environment variables when executing hooks
EXTENSION_PATH="${GEMINI_EXTENSION_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Read theme from environment variable, default to 'retro'
THEME="${AUDIO_ALERTS_THEME:-retro}"
# Normalize theme name to lowercase
THEME=$(echo "$THEME" | tr '[:upper:]' '[:lower:]')

# Verify theme directory exists, fallback to retro if not
if [ ! -d "$EXTENSION_PATH/assets/$THEME" ]; then
  THEME="retro"
fi

ASSETS_DIR="$EXTENSION_PATH/assets/$THEME"

# Define messages for each theme
declare -A THEME_MESSAGES
case "$THEME" in
  espionage)
    THEME_MESSAGES[question]="Agent requesting permission"
    THEME_MESSAGES[error]="Critical failure detected"
    THEME_MESSAGES[done]="Mission accomplished"
    ;;
  hero)
    THEME_MESSAGES[question]="Your approval is required"
    THEME_MESSAGES[error]="An error has occurred"
    THEME_MESSAGES[done]="Task complete. Well done, hero"
    ;;
  portal)
    THEME_MESSAGES[question]="Permission requested"
    THEME_MESSAGES[error]="Portal malfunction"
    THEME_MESSAGES[done]="Portal activated"
    ;;
  premium)
    THEME_MESSAGES[question]="Permission required"
    THEME_MESSAGES[error]="An error occurred"
    THEME_MESSAGES[done]="Process completed"
    ;;
  retro)
    THEME_MESSAGES[question]="Permission needed"
    THEME_MESSAGES[error]="Error detected"
    THEME_MESSAGES[done]="Game over. You win"
    ;;
  *)
    THEME_MESSAGES[question]="Permission required"
    THEME_MESSAGES[error]="Error occurred"
    THEME_MESSAGES[done]="Task completed"
    ;;
esac

# Cross-platform audio player detection (non-blocking)
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

# Cross-platform TTS (non-blocking)
speak() {
  local text="$1"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    say "$text" &
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v espeak >/dev/null 2>&1; then
      espeak "$text" &
    elif command -v gtts-cli >/dev/null 2>&1; then
      gtts-cli "$text" --output /tmp/gtts.mp3 && play -q /tmp/gtts.mp3 &
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
    play_audio "$ASSETS_DIR/question.wav"
    sleep 0.3
    speak "${THEME_MESSAGES[question]}"
  
  # Case: Generic Errors
  elif echo "$CONTEXT" | grep -qi "error"; then
    play_audio "$ASSETS_DIR/error.wav"
    sleep 0.3
    speak "${THEME_MESSAGES[error]}"
  fi

# 2. Handle Agent Completion (AfterAgent Hook)
elif [[ "$1" == "--finished" ]]; then
  play_audio "$ASSETS_DIR/done.wav"
  sleep 0.3
  speak "${THEME_MESSAGES[done]}"
fi

exit 0
