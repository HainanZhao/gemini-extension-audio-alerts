#!/usr/bin/env bash

# The Gemini CLI sets these environment variables when executing hooks
# When installed in ~/.gemini/hooks, the extension path is ~/.gemini
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$SCRIPT_DIR" == "$HOME/.gemini/hooks" ]]; then
  EXTENSION_PATH="$HOME/.gemini"
else
  EXTENSION_PATH="${GEMINI_EXTENSION_PATH:-$(cd "$SCRIPT_DIR/.." && pwd)}"
fi

# Read theme from environment variable, default to 'default'
THEME="${AUDIO_ALERTS_THEME:-default}"
# Normalize theme name to lowercase
THEME=$(echo "$THEME" | tr '[:upper:]' '[:lower:]')

# Verify theme directory exists, fallback to default if not
if [ ! -d "$EXTENSION_PATH/assets/$THEME" ]; then
  THEME="default"
fi

ASSETS_DIR="$EXTENSION_PATH/assets/$THEME"

# Check if audio alerts are enabled
ENABLED="${AUDIO_ALERTS_ENABLED:-true}"
if [[ "$ENABLED" != "true" && "$ENABLED" != "1" && "$ENABLED" != "yes" ]]; then
  exit 0
fi

# Define messages for each theme (compatible with bash 3.2 - avoid associative arrays)
case "$THEME" in
  default)
    QUESTION_MSG="Agent requesting permission"
    ERROR_MSG="Critical failure detected"
    DONE_MSG="Mission accomplished"
    ;;
  hero)
    QUESTION_MSG="Your approval is required"
    ERROR_MSG="An error has occurred"
    DONE_MSG="Task complete. Well done, hero"
    ;;
  portal)
    QUESTION_MSG="Permission requested"
    ERROR_MSG="Portal malfunction"
    DONE_MSG="Portal activated"
    ;;
  premium)
    QUESTION_MSG="Permission required"
    ERROR_MSG="An error occurred"
    DONE_MSG="Process completed"
    ;;
  retro)
    QUESTION_MSG="Permission needed"
    ERROR_MSG="Error detected"
    DONE_MSG="Task complete"
    ;;
  *)
    QUESTION_MSG="Permission required"
    ERROR_MSG="Error occurred"
    DONE_MSG="Task completed"
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

# Get timestamp file path (unique per session)
get_timestamp_file() {
  # Use GEMINI_SESSION_ID for stability across hook executions
  # Fallback to TERM_SESSION_ID or a temporary ID if not present
  local session_id="${GEMINI_SESSION_ID:-${TERM_SESSION_ID:-default_session}}"
  echo "/tmp/audio_alerts_${session_id}.timestamp"
}

# Debug logging (only when AUDIO_ALERTS_DEBUG=1)
DEBUG_LOG="/tmp/audio_alerts_debug.log"
log_debug() {
  [[ "${AUDIO_ALERTS_DEBUG:-0}" == "1" ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$DEBUG_LOG"
}

# Read hook data from stdin
CONTEXT=$(cat)

# 1. Handle BeforeAgent - Record start timestamp
if [[ "$1" == "--before" ]]; then
  TIMESTAMP_FILE=$(get_timestamp_file)
  date +%s > "$TIMESTAMP_FILE"
  log_debug "BeforeAgent: timestamp recorded at $TIMESTAMP_FILE"
  exit 0
fi

# 1b. Handle BeforeTool - For tool-specific tracking (works in VS Code)
if [[ "$1" == "--before-tool" ]]; then
  # Check if this is an ask_user permission request
  if echo "$CONTEXT" | grep -q '"name":"ask_user"' || echo "$CONTEXT" | grep -q '"name": "ask_user"'; then
    log_debug "BeforeTool: ask_user detected, playing question alert"
    play_alert "$ASSETS_DIR/question.wav" "$QUESTION_MSG" &
  fi
  exit 0
fi

# 2. Handle Notifications (works in standalone terminal, not VS Code)
if [[ "$1" == "--notification" ]]; then
  log_debug "Notification: ToolPermission received, playing question alert"
  play_alert "$ASSETS_DIR/question.wav" "$QUESTION_MSG" &

# 3. Handle Agent Completion (AfterAgent Hook)
elif [[ "$1" == "--finished" ]]; then
  TIMESTAMP_FILE=$(get_timestamp_file)
  SKIP_SOUND=false
  SKIP_TTS=false

  if [ -f "$TIMESTAMP_FILE" ]; then
    START_TIME=$(cat "$TIMESTAMP_FILE")
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    log_debug "AfterAgent: elapsed=${ELAPSED}s, theme=$THEME, done_msg=$DONE_MSG"

    # If less than 60 seconds, play sound only (no TTS)
    if [ "$ELAPSED" -lt 60 ]; then
      SKIP_TTS=true
      log_debug "Short session (< 60s): will play sound only, skip TTS"
    fi

    # Clean up timestamp file
    rm -f "$TIMESTAMP_FILE"
  else
    log_debug "AfterAgent: No timestamp file found at $TIMESTAMP_FILE"
    SKIP_SOUND=true
  fi

  if [ "$SKIP_SOUND" = false ]; then
    if [ "$SKIP_TTS" = true ]; then
      log_debug "Playing done alert (sound only, no TTS)"
      play_audio "$ASSETS_DIR/done.wav" &
    else
      log_debug "Playing done alert"
      play_alert "$ASSETS_DIR/done.wav" "$DONE_MSG" &
    fi
  fi
fi

exit 0
