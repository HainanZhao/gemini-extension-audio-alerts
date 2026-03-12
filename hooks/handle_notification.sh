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

# Define messages for each theme (compatible with bash 3.2 - avoid associative arrays)
case "$THEME" in
  espionage)
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
    DONE_MSG="Level complete"
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

# Debug logging
DEBUG_LOG="/tmp/audio_alerts_debug.log"
log_debug() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$DEBUG_LOG"
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

# 2. Handle Notifications
if [[ "$1" == "--notification" ]]; then
  local notification_type=""
  local is_ask_user=false

  # Use jq for reliable parsing
  if command -v jq >/dev/null 2>&1; then
    notification_type=$(echo "$CONTEXT" | jq -r '.notification_type // empty')
    if [[ "$notification_type" == "ToolPermission" ]]; then
      tool_code=$(echo "$CONTEXT" | jq -r '.tool_code // empty')
      if [[ "$tool_code" == *'ask_user'* ]]; then
        is_ask_user=true
      fi
    fi
  else
    # Fallback to grep
    notification_type=$(echo "$CONTEXT" | grep -o '"notification_type":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [[ "$notification_type" == "ToolPermission" ]]; then
      # This is less reliable as 'ask_user' could appear elsewhere
      if echo "$CONTEXT" | grep -q 'ask_user'; then
        is_ask_user=true
      fi
    fi
  fi

  log_debug "Notification: type=$notification_type, is_ask_user=$is_ask_user, theme=$THEME"

  # Case: ToolPermission (specifically ask_user)
  if [[ "$is_ask_user" == true ]]; then
    log_debug "Playing question alert"
    play_alert "$ASSETS_DIR/question.wav" "$QUESTION_MSG" &
  # Case: ToolExecutionError
  elif [[ "$notification_type" == "ToolExecutionError" ]]; then
    log_debug "Playing error alert"
    play_alert "$ASSETS_DIR/error.wav" "$ERROR_MSG" &
  fi

# 3. Handle Agent Completion (AfterAgent Hook)
elif [[ "$1" == "--finished" ]]; then
  TIMESTAMP_FILE=$(get_timestamp_file)
  SKIP_SOUND=false

  if [ -f "$TIMESTAMP_FILE" ]; then
    START_TIME=$(cat "$TIMESTAMP_FILE")
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    log_debug "AfterAgent: elapsed=${ELAPSED}s, theme=$THEME, done_msg=$DONE_MSG"

    # Skip sound if less than 15 seconds elapsed (reduced from 30s)
    if [ "$ELAPSED" -lt 15 ]; then
      SKIP_SOUND=true
      log_debug "Skipping sound (elapsed < 15s)"
    fi

    # Clean up timestamp file
    rm -f "$TIMESTAMP_FILE"
  else
    log_debug "AfterAgent: No timestamp file found at $TIMESTAMP_FILE"
    # If no timestamp file, we don't know the duration. 
    # Default to skip if it's likely a trivial session or if we want to be conservative.
    SKIP_SOUND=true
  fi

  if [ "$SKIP_SOUND" = false ]; then
    log_debug "Playing done alert"
    play_alert "$ASSETS_DIR/done.wav" "$DONE_MSG" &
  fi
fi

exit 0
