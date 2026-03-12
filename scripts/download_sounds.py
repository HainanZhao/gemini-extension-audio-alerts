#!/usr/bin/env python3
"""Download sound effects from working free sources."""

import os
import urllib.request
import ssl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Working URLs from various free sources
SOUNDS = {
    'espionage': {
        # Spy/tech themed sounds
        'question': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/sci-fi-click.mp3',
        'error': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/suspense-drone.mp3',
        'done': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/tech-hum.mp3',
    },
    'hero': {
        # Victory/fanfare sounds
        'question': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/fanfare-short.mp3',
        'done': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/victory-chime.mp3',
        'error': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/dramatic-hit.mp3',
    },
    'portal': {
        # Transition/whoosh sounds
        'question': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/magic-whoosh.mp3',
        'done': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/teleport-swoosh.mp3',
        'error': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/magic-sweep.mp3',
    },
    'premium': {
        # Elegant chime sounds
        'question': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/crystal-chime.mp3',
        'done': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/elegant-bell.mp3',
        'error': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/soft-notification.mp3',
    },
    'retro': {
        # 8-bit/arcade sounds
        'question': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/retro-game-notification.mp3',
        'done': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/arcade-win.mp3',
        'error': 'https://raw.githubusercontent.com/Audio-Previews/Free-SFX/main/game-over.mp3',
    },
}

# Alternative: Use Kenney.nl assets (public domain)
KENNEY_SOUNDS = {
    'espionage': {
        'question': 'https://kenney.nl/media/pages/sounds/interface-sounds/click_1.mp3',
        'error': 'https://kenney.nl/media/pages/sounds/interface-sounds/error_1.mp3',
        'done': 'https://kenney.nl/media/pages/sounds/interface-sounds/complete_1.mp3',
    },
}

def download_file(url, filepath):
    """Download a file from URL."""
    print(f"  URL: {url}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept': '*/*',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read()
            
        if len(content) < 1000 or content.startswith(b'<!DOCTYPE') or content.startswith(b'<html') or content.startswith(b'404'):
            print(f"  ❌ Invalid response ({len(content)} bytes)")
            return False
            
        with open(filepath, 'wb') as f:
            f.write(content)
            
        print(f"  ✓ Downloaded: {len(content):,} bytes")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    success = 0
    total = 0
    
    for theme, sounds in SOUNDS.items():
        theme_dir = os.path.join(ASSETS_DIR, theme)
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"Theme: {theme.upper()}")
        print(f"{'='*50}")
        
        for sound_type, url in sounds.items():
            filepath = os.path.join(theme_dir, f"{sound_type}.mp3")
            total += 1
            if download_file(url, filepath):
                success += 1
    
    print(f"\n{'='*50}")
    print(f"Complete: {success}/{total} files")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
