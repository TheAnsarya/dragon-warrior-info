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

## Mesen Emulator Automation

Mesen is the recommended emulator for Dragon Warrior video tutorials because it supports:

- High-quality video and screenshot capture
- Lua scripting for automation
- Built-in recording tools
- Debugging and memory viewing

### Installation

Download Mesen from: <https://mesen.ca>

### Screenshot Automation

Mesen can capture screenshots via:

1. **Menu:** Tools → Take Screenshot (F12 by default)
2. **Command Line:** `Mesen.exe rom.nes --screenshot output.png`
3. **Lua Script:** Automated screenshot sequences

### Video Recording

#### Built-in Recording

```text
1. File → Movies → Record Movie
2. Play through the sequence
3. File → Movies → Stop Recording
4. Result: .mmo movie file (can export to AVI)
```

#### Export to AVI

```text
1. File → Movies → Play Movie
2. File → Video Recording → Start Recording
3. Let movie play
4. File → Video Recording → Stop Recording
5. Result: High-quality AVI file
```

### Lua Scripting for Automated Captures

Mesen supports Lua scripting for advanced automation.

#### Screenshot Sequence Script

```lua
-- screenshot_sequence.lua
-- Takes screenshots at specific game states

local screenshots_taken = 0
local screenshot_folder = "C:/screenshots/"

-- Define when to capture
local capture_triggers = {
    {address = 0x0045, value = 0x01, name = "title_screen"},
    {address = 0x0045, value = 0x03, name = "overworld"},
    {address = 0x0045, value = 0x05, name = "battle"},
    {address = 0x0045, value = 0x07, name = "menu"},
}

function onMemoryRead(address, value)
    for _, trigger in ipairs(capture_triggers) do
        if address == trigger.address and value == trigger.value then
            local filename = screenshot_folder .. trigger.name .. "_" .. os.time() .. ".png"
            emu.takeScreenshot(filename)
            screenshots_taken = screenshots_taken + 1
            emu.log("Screenshot: " .. trigger.name)
        end
    end
end

emu.addMemoryCallback(onMemoryRead, emu.callbackType.read, 0x0045)

emu.log("Screenshot automation loaded - watching for game state changes")
```

#### Save State Automation

```lua
-- save_state_demo.lua
-- Create save states for video demonstration points

local demo_points = {
    {name = "start_game", frames = 600},      -- After 10 seconds
    {name = "first_battle", frames = 3600},   -- After 1 minute  
    {name = "level_up", frames = 7200},       -- After 2 minutes
}

local frame_count = 0

function onFrame()
    frame_count = frame_count + 1
    
    for _, point in ipairs(demo_points) do
        if frame_count == point.frames then
            local filename = "demo_" .. point.name .. ".mss"
            emu.saveSavestate(filename)
            emu.log("Saved: " .. point.name)
        end
    end
end

emu.addEventCallback(onFrame, emu.eventType.endFrame)
```

### Batch Processing with Mesen

#### PowerShell Script for Multiple Screenshots

```powershell
# batch_screenshots.ps1
# Take screenshots from multiple save states

$mesenPath = "C:\Tools\Mesen\Mesen.exe"
$romPath = "roms\dragon_warrior.nes"
$outputFolder = "video_assets\screenshots"

# Ensure output folder exists
New-Item -ItemType Directory -Force -Path $outputFolder | Out-Null

# List of save states and their screenshot names
$saveStates = @(
    @{state = "savestates\title.mss"; name = "title_screen"},
    @{state = "savestates\overworld.mss"; name = "overworld_view"},
    @{state = "savestates\castle.mss"; name = "castle_interior"},
    @{state = "savestates\battle.mss"; name = "battle_scene"},
    @{state = "savestates\menu.mss"; name = "menu_open"},
    @{state = "savestates\shop.mss"; name = "weapon_shop"},
    @{state = "savestates\dragon_lord.mss"; name = "final_boss"}
)

foreach ($item in $saveStates) {
    $outputPath = Join-Path $outputFolder "$($item.name).png"
    
    Write-Host "Capturing: $($item.name)"
    
    # Load save state and take screenshot
    & $mesenPath $romPath `
        --load-state $item.state `
        --screenshot $outputPath `
        --no-audio `
        --headless
    
    Start-Sleep -Milliseconds 500
}

Write-Host "Done! Screenshots saved to: $outputFolder"
```

#### Automated Demo Video Recording

```powershell
# record_demo.ps1
# Record a demo video from a movie file

$mesenPath = "C:\Tools\Mesen\Mesen.exe"
$romPath = "roms\dragon_warrior.nes"
$movieFile = "movies\demo_playthrough.mmo"
$outputVideo = "video_assets\demo_capture.avi"

Write-Host "Recording demo video..."

& $mesenPath $romPath `
    --movie $movieFile `
    --record-avi $outputVideo `
    --no-audio `
    --video-scale 3

Write-Host "Video saved to: $outputVideo"
```

### Creating Demo Save States

To create save states for automated capture:

1. **Play through the game** and save at key moments
2. **Name saves descriptively:** `title.mss`, `first_town.mss`, `slime_battle.mss`
3. **Store in project:** `video_assets/savestates/`

Key moments for Dragon Warrior tutorials:

| Save State | Scene | Use Case |
|------------|-------|----------|
| `title.mss` | Title screen | Episode intros |
| `new_game.mss` | Name entry | Character creation |
| `throne_room.mss` | King's dialogue | NPC/dialog editing |
| `overworld.mss` | Field exploration | Map tutorials |
| `slime_battle.mss` | Combat with Slime | Monster stat demos |
| `level_up.mss` | Level up screen | Experience table demos |
| `weapon_shop.mss` | Brecconary shop | Shop editing |
| `spell_menu.mss` | Spell selection | Spell editing |
| `dragonlord.mss` | Final boss | Advanced examples |

### Mesen Video Settings for Recording

For best video quality in tutorials:

```text
Options → Video:
- Video Scale: 3x or 4x
- Aspect Ratio: Auto (8:7 NTSC)
- Filter: None (crisp pixels) or NTSC (authentic look)
- Use Integer Scale: Enabled

Options → AVI Recording:
- Codec: Uncompressed or Lagarith Lossless
- Scale: Match display
```

### Integrating with OBS

For complex recording setups, use Mesen as a game capture source in OBS:

1. Open OBS with NES Recording scene
2. Add Game Capture source → Select Mesen window
3. Start Mesen and load game
4. Record in OBS with overlays, facecam, etc.

This gives you OBS's flexibility with Mesen's accuracy.

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
| 2025-12-02 | 1.1 | Add Mesen emulator automation section |

