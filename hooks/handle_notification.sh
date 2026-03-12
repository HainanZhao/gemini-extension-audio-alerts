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
    THEME_MESSAGES[done]="Level complete"
    ;;
  *)
    THEME_MESSAGES[question]="Permission required"
    THEME_MESSAGES[error]="Error occurred"
    THEME_MESSAGES[done]="Task completed"
    ;;
esac

# Cross-platform audio player detection (blocking/synchronous)
play_audio() {
  local file=$1
  if [[ "$OSTYPE" == "darwin"* ]]; then
    /usr/bin/afplay "$file"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v play >/dev/null 2>&1; then
      play -q "$file"
    elif command -v mpg123 >/dev/null 2>&1; then
      mpg123 -q "$file"
    elif command -v paplay >/dev/null 2>&1; then
      paplay "$file"
    fi
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    powershell -Command "(New-Object System.Media.SoundPlayer '$file').PlaySync()"
  fi
}

# Cross-platform TTS (blocking/synchronous)
speak() {
  local text="$1"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    say "$text"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v espeak >/dev/null 2>&1; then
      espeak "$text"
    elif command -v gtts-cli >/dev/null 2>&1; then
      gtts-cli "$text" --output /tmp/gtts.mp3 && play -q /tmp/gtts.mp3
    fi
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('$text')"
  fi
}

# Play audio then TTS in sequence, running asynchronously
play_alert() {
  local audio_file=$1
  local text=$2
  play_audio "$audio_file"
  speak "$text"
}

# Get timestamp file path (unique per terminal session)
get_timestamp_file() {
  local terminal_id="${TERM_SESSION_ID:-$$}"
  echo "/tmp/audio_alerts_${terminal_id}.timestamp"
}

# Read hook data from stdin
CONTEXT=$(cat)

# 1. Handle BeforeAgent - Record start timestamp
if [[ "$1" == "--before" ]]; then
  TIMESTAMP_FILE=$(get_timestamp_file)
  date +%s > "$TIMESTAMP_FILE"
  exit 0
fi

# 2. Handle Notifications
if [[ "$1" == "--notification" ]]; then
  NOTIFICATION_TYPE=$(echo "$CONTEXT" | grep -o '"notification_type":"[^"]*"' | cut -d'"' -f4)

  # Case: ToolPermission (specifically ask_user)
  if [[ "$NOTIFICATION_TYPE" == "ToolPermission" ]] && echo "$CONTEXT" | grep -q '"type":"ask_user"'; then
    play_alert "$ASSETS_DIR/question.wav" "${THEME_MESSAGES[question]}" &

  # Case: Generic Errors
  elif echo "$CONTEXT" | grep -qi "error"; then
    play_alert "$ASSETS_DIR/error.wav" "${THEME_MESSAGES[error]}" &
  fi

# 3. Handle Agent Completion (AfterAgent Hook)
elif [[ "$1" == "--finished" ]]; then
  TIMESTAMP_FILE=$(get_timestamp_file)
  SKIP_SOUND=false

  if [ -f "$TIMESTAMP_FILE" ]; then
    START_TIME=$(cat "$TIMESTAMP_FILE")
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))

    # Skip sound if less than 30 seconds elapsed
    if [ "$ELAPSED" -lt 30 ]; then
      SKIP_SOUND=true
    fi

    # Clean up timestamp file
    rm -f "$TIMESTAMP_FILE"
  fi

  if [ "$SKIP_SOUND" = false ]; then
    play_alert "$ASSETS_DIR/done.wav" "${THEME_MESSAGES[done]}" &
  fi
fi

exit 0
