#!/usr/bin/env bash

# Sound Generation Script using Qwen API
# This script generates themed audio alerts for the Gemini Extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS_DIR="$EXTENSION_ROOT/assets"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Qwen API key is set
check_qwen_api() {
    if [ -z "$QWEN_API_KEY" ]; then
        log_error "QWEN_API_KEY environment variable is not set"
        echo ""
        echo "Please set your Qwen API key:"
        echo "  export QWEN_API_KEY='your-api-key-here'"
        echo ""
        echo "You can get an API key from: https://dashscope.console.aliyun.com/"
        exit 1
    fi
    log_info "Qwen API key found"
}

# Generate sound using Qwen TTS API
# This uses Qwen's audio generation capabilities
generate_sound() {
    local theme=$1
    local sound_type=$2
    local description=$3
    local output_file=$4
    
    log_info "Generating $theme/$sound_type..."
    
    # Use Qwen API for text-to-speech with SSML for sound effects
    # The description contains SSML markup for sound characteristics
    local response
    response=$(curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/services/audio/text-to-speech/generation" \
        -H "Authorization: Bearer $QWEN_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"sambert-zh-v1\",
            \"input\": {
                \"text\": \"$description\"
            },
            \"parameters\": {
                \"format\": \"mp3\",
                \"sample_rate\": 44100,
                \"volume\": 50,
                \"rate\": 1.0,
                \"pitch\": 50
            }
        }")
    
    # Extract audio URL from response and download
    local audio_url
    audio_url=$(echo "$response" | grep -o '"output_url":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$audio_url" ]; then
        curl -s "$audio_url" -o "$output_file"
        log_success "Generated: $output_file"
    else
        log_error "Failed to generate sound: $sound_type"
        echo "Response: $response"
        return 1
    fi
}

# Alternative: Generate sounds using Python with pydub and system sounds
generate_sound_python() {
    local theme=$1
    local sound_type=$2
    local output_file=$3
    
    log_info "Generating $theme/$sound_type using Python..."
    
    python3 "$SCRIPT_DIR/generate_sound.py" \
        --theme "$theme" \
        --type "$sound_type" \
        --output "$output_file"
}

# Main generation function
generate_theme_sounds() {
    local theme=$1
    
    log_info "Generating sounds for theme: $theme"
    
    local theme_dir="$ASSETS_DIR/$theme"
    mkdir -p "$theme_dir"
    
    # Generate each sound type (only what's needed by the hook)
    generate_sound_python "$theme" "question" "$theme_dir/question.mp3"
    generate_sound_python "$theme" "error" "$theme_dir/error.mp3"
    generate_sound_python "$theme" "done" "$theme_dir/done.mp3"
    
    log_success "Completed theme: $theme"
}

# Generate all themes
generate_all() {
    log_info "Generating sounds for all themes..."
    
    local themes=("default" "retro" "portal" "espionage" "hero" "premium")
    
    for theme in "${themes[@]}"; do
        generate_theme_sounds "$theme"
        echo ""
    done
    
    log_success "All themes generated successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --theme <name>    Generate sounds for a specific theme"
    echo "                    (default, retro, portal, espionage, hero, premium)"
    echo "  --all             Generate sounds for all themes"
    echo "  --help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  QWEN_API_KEY      Your Qwen API key (required)"
    echo ""
    echo "Examples:"
    echo "  $0 --theme retro"
    echo "  $0 --all"
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

check_qwen_api

while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            THEME_NAME="$2"
            generate_theme_sounds "$THEME_NAME"
            shift 2
            ;;
        --all)
            generate_all
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done
