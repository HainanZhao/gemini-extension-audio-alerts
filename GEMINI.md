# Gemini Audio Alerts Extension

This extension provides context-aware audio alerts for the Gemini CLI. It is specifically designed to solve the "silent hang" problem when running inside IDE terminals like VS Code.

## Features
- **Ask User Alert**: Plays "Gemini has a question" when the agent requires user input.
- **Error Alert**: Plays an error tone and voice prompt when a tool execution fails.
- **Done Alert**: Plays "Gemini has finished the task" when the agent's work cycle is complete.

## Implementation Details
- The extension uses a `Notification` hook for tool permissions and errors.
- It uses an `AfterAgent` hook for task completion.
- All logic is handled by a portable Bash script (`hooks/handle_notification.sh`) and bundled MP3 assets.
