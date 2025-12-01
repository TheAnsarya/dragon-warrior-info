# Video Production Automation Guide

## Overview

This guide covers how to automate and streamline the video tutorial production process for the Dragon Warrior ROM Hacking series.

---

## Recommended Tool Stack

### Screen Recording
| Tool | Purpose | Link |
|------|---------|------|
| **OBS Studio** | Primary recording | https://obsproject.com |
| **ShareX** | Quick captures | https://getsharex.com |
| **FFmpeg** | Command-line processing | https://ffmpeg.org |

### Video Editing
| Tool | Purpose | Link |
|------|---------|------|
| **DaVinci Resolve** | Full editing (free!) | https://blackmagicdesign.com |
| **Shotcut** | Lightweight editing | https://shotcut.org |
| **FFmpeg** | Batch processing | https://ffmpeg.org |

### Audio
| Tool | Purpose | Link |
|------|---------|------|
| **Audacity** | Audio recording/editing | https://audacityteam.org |
| **NVIDIA Broadcast** | Noise removal (RTX) | https://nvidia.com/broadcast |

### AI/Automation
| Tool | Purpose | Link |
|------|---------|------|
| **Whisper** | Auto-transcription | https://github.com/openai/whisper |
| **ElevenLabs** | AI narration (optional) | https://elevenlabs.io |
| **Auto-Editor** | Silence removal | https://github.com/WyattBlue/auto-editor |

---

## Automated Workflows

### 1. Script-to-Recording Pipeline

#### Step 1: Convert Script to Teleprompter Format
```python
#!/usr/bin/env python3
"""Convert markdown script to teleprompter-friendly format."""

import re
import sys
from pathlib import Path

def extract_narration(markdown_file):
    """Extract narration blocks from script markdown."""
    content = Path(markdown_file).read_text(encoding='utf-8')
    
    # Find all blockquoted narration
    narration_blocks = re.findall(r'>\s*"([^"]+)"', content, re.MULTILINE)
    
    output = []
    for i, block in enumerate(narration_blocks, 1):
        # Clean up whitespace
        text = ' '.join(block.split())
        output.append(f"[{i}] {text}\n")
    
    return '\n'.join(output)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_narration.py script.md")
        sys.exit(1)
    
    print(extract_narration(sys.argv[1]))
```

#### Step 2: Record with Section Markers
```powershell
# OBS can be controlled via WebSocket
# Start recording with hotkey, speak section, add marker, continue
# Markers help split recording later

# Example OBS WebSocket command (requires obs-websocket plugin):
# Set hotkey for "Add Chapter Marker" to F9
# Press F9 between each script section while recording
```

### 2. Auto-Edit Pipeline

#### Remove Silences Automatically
```powershell
# Install auto-editor
pip install auto-editor

# Remove silences from recording
auto-editor recording.mp4 --margin 0.3s --edit audio:threshold=4%

# Output: recording_ALTERED.mp4
```

#### Batch Process Multiple Takes
```powershell
# Process all recordings in a folder
Get-ChildItem .\raw_footage\*.mp4 | ForEach-Object {
    auto-editor $_.FullName --margin 0.3s --edit audio:threshold=4%
}
```

### 3. Transcription & Captions

#### Auto-Generate Captions with Whisper
```powershell
# Install whisper
pip install openai-whisper

# Transcribe video
whisper video.mp4 --model medium --output_format srt

# Output: video.srt (subtitle file)
```

#### Batch Transcribe
```python
#!/usr/bin/env python3
"""Batch transcribe videos for captions."""

import subprocess
from pathlib import Path

def transcribe_videos(video_folder: str, output_folder: str):
    """Transcribe all videos in a folder."""
    video_folder = Path(video_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    
    for video in video_folder.glob("*.mp4"):
        output = output_folder / f"{video.stem}.srt"
        if not output.exists():
            print(f"Transcribing: {video.name}")
            subprocess.run([
                "whisper", str(video),
                "--model", "medium",
                "--output_format", "srt",
                "--output_dir", str(output_folder)
            ])
    
    print("Done!")

if __name__ == '__main__':
    transcribe_videos("videos", "captions")
```

### 4. Thumbnail Generation

#### Automated Thumbnail Template
```python
#!/usr/bin/env python3
"""Generate video thumbnails from template."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_thumbnail(
    episode_num: int,
    title: str,
    output_path: str,
    template_path: str = "thumbnail_template.png"
):
    """Create a video thumbnail with episode number and title."""
    # Load template
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Fonts (adjust paths as needed)
    title_font = ImageFont.truetype("arial.ttf", 48)
    episode_font = ImageFont.truetype("arial.ttf", 72)
    
    # Add episode number
    draw.text((50, 50), f"EP {episode_num}", font=episode_font, fill="yellow")
    
    # Add title (may need word wrapping for long titles)
    draw.text((50, 150), title, font=title_font, fill="white")
    
    # Save
    img.save(output_path)
    print(f"Created: {output_path}")

# Generate thumbnails for all episodes
episodes = [
    (1, "Getting Started"),
    (2, "Monster Stats"),
    (3, "Graphics Editing"),
    (4, "Dialog Editing"),
    (5, "Game Balance"),
    (6, "Advanced Assembly"),
    (7, "Troubleshooting"),
]

for num, title in episodes:
    create_thumbnail(num, title, f"thumbnails/ep{num:02d}_thumb.png")
```

### 5. YouTube Upload Automation

#### Using YouTube API
```python
#!/usr/bin/env python3
"""
Upload videos to YouTube with metadata from script files.
Requires google-api-python-client and oauth2client.
"""

import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from pathlib import Path
import json

def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    credentials_file: str = "youtube_credentials.json"
):
    """Upload a video to YouTube."""
    creds = Credentials.from_authorized_user_file(credentials_file)
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '20'  # Gaming
        },
        'status': {
            'privacyStatus': 'unlisted',  # Start unlisted, make public later
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = request.execute()
    print(f"Uploaded: https://youtube.com/watch?v={response['id']}")
    return response['id']

# Example usage
if __name__ == '__main__':
    upload_video(
        "final/episode_01.mp4",
        "Dragon Warrior ROM Hacking: Getting Started",
        open("descriptions/ep01_description.txt").read(),
        ["Dragon Warrior", "NES", "ROM Hacking", "Tutorial"]
    )
```

---

## Complete Production Pipeline

### Phase 1: Pre-Production
```powershell
# 1. Create script from template
cp docs/video_scripts/template.md docs/video_scripts/episode_XX.md

# 2. Write script in markdown
code docs/video_scripts/episode_XX.md

# 3. Extract narration for teleprompter
python tools/video/extract_narration.py docs/video_scripts/episode_XX.md > teleprompter/ep_XX.txt

# 4. Generate thumbnail
python tools/video/create_thumbnail.py --episode XX --title "Title Here"
```

### Phase 2: Recording
```powershell
# 1. Open OBS with preset scene collection
Start-Process obs-studio --args "--collection DragonWarrior"

# 2. Record each section, adding markers
# Press F9 between sections

# 3. Export to raw_footage/episode_XX/
```

### Phase 3: Post-Production
```powershell
# 1. Remove silences
auto-editor raw_footage/episode_XX/main.mp4 --margin 0.3s

# 2. Generate captions
whisper raw_footage/episode_XX/main_ALTERED.mp4 --model medium --output_format srt

# 3. Edit in DaVinci Resolve
# - Import footage
# - Add intro/outro
# - Add captions from .srt
# - Color grade
# - Export to final/episode_XX.mp4

# 4. Generate description from script
python tools/video/generate_description.py docs/video_scripts/episode_XX.md > descriptions/ep_XX.txt
```

### Phase 4: Publishing
```powershell
# 1. Upload to YouTube (unlisted)
python tools/video/youtube_upload.py --video final/episode_XX.mp4 --description descriptions/ep_XX.txt

# 2. Add end cards and cards in YouTube Studio

# 3. Schedule or publish

# 4. Update documentation links
# - Add YouTube link to VIDEO_TUTORIALS.md
# - Add link to related docs
```

---

## Batch Processing Scripts

### Process Entire Series
```powershell
#!/usr/bin/env pwsh
# build_all_videos.ps1 - Process all raw footage

param(
    [string]$RawFolder = "raw_footage",
    [string]$OutputFolder = "processed",
    [switch]$SkipTranscription
)

# Create output folder
New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null

# Process each episode folder
Get-ChildItem $RawFolder -Directory | ForEach-Object {
    $episode = $_.Name
    Write-Host "Processing: $episode" -ForegroundColor Cyan
    
    $mainFile = Join-Path $_.FullName "main.mp4"
    
    if (Test-Path $mainFile) {
        # 1. Remove silences
        Write-Host "  Removing silences..." -ForegroundColor Yellow
        auto-editor $mainFile --margin 0.3s --output "$OutputFolder/$episode.mp4"
        
        # 2. Generate captions
        if (-not $SkipTranscription) {
            Write-Host "  Generating captions..." -ForegroundColor Yellow
            whisper "$OutputFolder/$episode.mp4" --model medium --output_format srt --output_dir $OutputFolder
        }
    }
    else {
        Write-Warning "No main.mp4 found in $episode"
    }
}

Write-Host "Done!" -ForegroundColor Green
```

### Generate All Descriptions
```python
#!/usr/bin/env python3
"""Generate YouTube descriptions from all scripts."""

import re
from pathlib import Path

def extract_description_template(script_path: Path) -> str:
    """Extract the video description template from a script file."""
    content = script_path.read_text(encoding='utf-8')
    
    # Find the Video Description Template section
    match = re.search(
        r'## Video Description Template\s*```\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    
    if match:
        return match.group(1).strip()
    return ""

def main():
    scripts_folder = Path("docs/video_scripts")
    output_folder = Path("video_descriptions")
    output_folder.mkdir(exist_ok=True)
    
    for script in scripts_folder.glob("episode_*.md"):
        print(f"Processing: {script.name}")
        description = extract_description_template(script)
        
        if description:
            output_file = output_folder / f"{script.stem}_description.txt"
            output_file.write_text(description, encoding='utf-8')
            print(f"  Created: {output_file.name}")
        else:
            print(f"  Warning: No description template found")

if __name__ == '__main__':
    main()
```

---

## Asset Templates

### OBS Scene Collection (JSON export)
The OBS scene collection should include:
- **Main Recording** scene with screen capture
- **Emulator** scene with game capture
- **Code** scene with VS Code capture
- **Intro** scene with branded graphics
- **Outro** scene with end card

Save scene collection and import on each machine.

### DaVinci Resolve Project Template
Create a template project with:
- Standard timeline settings (1080p, 30fps)
- Color grading presets
- Intro/outro media imported
- Audio tracks configured (narration, music, SFX)

### Thumbnail Template (Photoshop/GIMP)
Create a 1280x720 template with:
- Dragon Warrior background
- Episode number placeholder
- Title placeholder
- Consistent branding

---

## Quality Checklist

### Before Recording
- [ ] Script reviewed and finalized
- [ ] Project clean and ready to demonstrate
- [ ] OBS scenes configured
- [ ] Audio levels tested
- [ ] Screen resolution and scaling correct

### After Recording
- [ ] All sections recorded
- [ ] Audio clear (no clipping, background noise minimal)
- [ ] No personal info visible in footage
- [ ] Markers placed for editing

### Before Publishing
- [ ] Captions reviewed for accuracy
- [ ] Description includes all links
- [ ] Timestamps accurate
- [ ] Thumbnail created and uploaded
- [ ] Cards and end screens added
- [ ] Privacy set correctly

---

## Time Estimates

| Phase | Per Episode |
|-------|-------------|
| Script Writing | 1-2 hours |
| Recording | 30-60 min |
| Auto-Edit (silence removal) | 5 min |
| Transcription | 10 min |
| Manual Editing | 1-2 hours |
| Description/Metadata | 15 min |
| Upload & Publish | 30 min |
| **Total** | **4-6 hours** |

With automation, the manual work can be reduced to primarily:
- Script writing
- Recording
- Review and polish
- Publishing

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial automation guide |

