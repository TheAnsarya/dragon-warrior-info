# Video Production Pipeline - GitHub Issues

This document contains issue templates for the video production toolchain.
These can be created in the GitHub repository using the GitHub CLI or web interface.

---

## Issue 1: Video Production Pipeline MVP

**Title:** Implement Video Production Pipeline MVP

**Labels:** enhancement, documentation, video-production

**Body:**

### Summary

Implement a minimum viable product (MVP) for the video production pipeline that enables automated creation of Dragon Warrior ROM hacking tutorial videos.

### Goals

- [ ] Automated gameplay capture using Mesen Lua scripts
- [ ] Narration extraction from markdown scripts
- [ ] Basic video assembly workflow
- [ ] Documentation for the complete process

### Acceptance Criteria

1. **Mesen Automation**
   - [ ] Lua scripts for all 7 episodes' key scenes
   - [ ] Screenshot capture working automatically
   - [ ] Save state management for reproducible captures

2. **Narration Tools**
   - [ ] Extract narration from markdown to plain text
   - [ ] Export in teleprompter-friendly format
   - [ ] SSML output for TTS services

3. **Video Assembly**
   - [ ] FFmpeg-based video concatenation
   - [ ] Audio track mixing (narration + background music)
   - [ ] Standard export presets for YouTube

4. **Documentation**
   - [ ] Step-by-step production guide
   - [ ] Tool usage documentation
   - [ ] Troubleshooting guide

### Technical Details

- Python 3.8+ for automation scripts
- Mesen 2.x for NES emulation
- FFmpeg for video processing
- Markdown-based script format

### Related Files

- `tools/video/` - Python tooling
- `docs/video_scripts/` - Episode scripts
- `docs/VIDEO_PRODUCTION_GUIDE.md` - Main documentation

---

## Issue 2: AI Narration Integration

**Title:** Integrate AI Text-to-Speech for Video Narration

**Labels:** enhancement, video-production, ai

**Body:**

### Summary

Implement integration with AI text-to-speech services to automatically generate narration audio from episode scripts.

### Goals

- [ ] Support multiple TTS providers (ElevenLabs, Azure, OpenAI)
- [ ] SSML preprocessing for natural speech
- [ ] Batch processing for all episodes
- [ ] Voice consistency across episodes

### TTS Provider Support

1. **ElevenLabs** (Primary)
   - High-quality voices
   - Custom voice option
   - API wrapper needed

2. **Azure Cognitive Services** (Secondary)
   - Cost-effective for long content
   - Good SSML support
   - Neural voices available

3. **OpenAI TTS** (Fallback)
   - Simple API
   - Quick prototyping

### Implementation Tasks

- [ ] Create `tools/video/tts_generator.py`
- [ ] Implement ElevenLabs integration
- [ ] Implement Azure TTS integration
- [ ] Add SSML preprocessing
- [ ] Create configuration for voice selection
- [ ] Add caching to avoid re-generating unchanged sections
- [ ] Implement audio normalization post-processing

### Configuration Example

```yaml
tts:
  provider: elevenlabs
  voice_id: "custom_voice_123"
  settings:
    stability: 0.5
    similarity_boost: 0.75
  output_format: mp3
  sample_rate: 48000
```

### Dependencies

- `elevenlabs` Python package
- `azure-cognitiveservices-speech` package
- `openai` package
- API keys stored securely (environment variables)

---

## Issue 3: Mesen Automation Scripts

**Title:** Create Comprehensive Mesen Lua Scripts for All Episodes

**Labels:** enhancement, video-production, automation

**Body:**

### Summary

Develop a complete set of Mesen Lua scripts that automate gameplay capture for all 7 tutorial episodes.

### Goals

- [ ] Scene scripts for each episode's key moments
- [ ] Battle detection and auto-capture
- [ ] Tutorial overlay system
- [ ] Input recording and playback

### Episode Scene Requirements

#### Episode 1: Getting Started
- [ ] Title screen display
- [ ] New game creation sequence
- [ ] Throne room to overworld walk

#### Episode 2: Monster Stats
- [ ] Random encounter trigger
- [ ] Battle UI demonstration
- [ ] Level up sequence

#### Episode 3: Graphics Editing
- [ ] Multiple area screenshots
- [ ] Sprite demonstrations
- [ ] Before/after comparisons

#### Episode 4: Dialog Editing
- [ ] King's dialog playback
- [ ] Shop interaction
- [ ] NPC conversations

#### Episode 5: Game Balance
- [ ] Combat demonstrations
- [ ] Shop price displays
- [ ] Stat progression

#### Episode 6: Advanced Assembly
- [ ] Specific code behavior demos
- [ ] Memory visualization

#### Episode 7: Troubleshooting
- [ ] Debug overlay demonstrations
- [ ] Error state captures

### Technical Requirements

- Save state dependencies documented
- Input frame timings tested
- Screenshot naming conventions
- Error handling for failed captures

### Deliverables

- [ ] Lua scripts in `video_assets/mesen_scripts/`
- [ ] Save states in `video_assets/savestates/`
- [ ] Scene index JSON for each episode
- [ ] Master runner script

---

## Issue 4: Automated Thumbnail Generation

**Title:** Implement Automated YouTube Thumbnail Generator

**Labels:** enhancement, video-production, automation

**Body:**

### Summary

Create a tool to automatically generate YouTube thumbnails from episode metadata and game screenshots.

### Goals

- [ ] Consistent branding across all episodes
- [ ] Episode-specific screenshots
- [ ] Text overlays with episode number/title
- [ ] Multiple design variants

### Thumbnail Requirements

- **Dimensions:** 1280x720 (minimum for YouTube)
- **File size:** Under 2MB
- **Format:** PNG or JPEG
- **Elements:**
  - Episode number (prominent)
  - Episode title (readable)
  - Dragon Warrior imagery
  - Series branding/logo

### Design Templates

1. **Standard Template**
   - Game screenshot background
   - Gradient overlay
   - Bold episode number
   - Title text at bottom

2. **Action Template**
   - Battle scene screenshot
   - Dynamic text positioning
   - Emphasis on "ROM Hacking"

3. **Technical Template**
   - Code/hex editor imagery
   - Technical aesthetic
   - Episode focus highlighted

### Implementation

- [ ] Create `tools/video/thumbnail_generator.py`
- [ ] Use Pillow for image manipulation
- [ ] Template configuration in JSON/YAML
- [ ] Font handling (bundle required fonts)
- [ ] Batch generation for all episodes
- [ ] Preview generation before final export

### Example Usage

```bash
python -m tools.video.thumbnail_generator \
    --episode 1 \
    --template standard \
    --screenshot captures/ep01_title.png \
    --output thumbnails/
```

---

## Issue 5: Video Assembly Automation

**Title:** Enhance Video Assembly Pipeline with Advanced Features

**Labels:** enhancement, video-production

**Body:**

### Summary

Extend the video assembly tools with advanced features for professional-quality output.

### Goals

- [ ] Automated chapter markers
- [ ] Audio ducking for narration over music
- [ ] Transition effects
- [ ] End screen/outro integration

### Features to Implement

#### Chapter Markers
- Parse scene plans for chapter timestamps
- Embed chapters in MP4 metadata
- Export chapter list for YouTube

#### Audio Processing
- [ ] Automatic audio normalization
- [ ] Sidechain compression for ducking
- [ ] Noise reduction preprocessing
- [ ] Volume envelope automation

#### Transitions
- [ ] Cross-fade between clips
- [ ] Title card fade-in/out
- [ ] Custom transition timing

#### End Screen
- [ ] Standard 20-second outro
- [ ] Subscribe animation
- [ ] Next episode preview

### Technical Implementation

```python
# Chapter marker generation
chapters = [
    {"time": "0:00", "title": "Introduction"},
    {"time": "2:15", "title": "Setting Up Tools"},
    {"time": "5:30", "title": "First ROM Edit"},
]

# Embed in metadata
ffmpeg_cmd.extend([
    '-metadata', f'chapter{i}={format_chapter(ch)}'
])
```

### Dependencies

- FFmpeg with libfdk-aac
- Pillow for title cards
- NumPy for audio processing (optional)

---

## Issue 6: CI/CD for Video Assets

**Title:** Implement CI/CD Pipeline for Video Asset Validation

**Labels:** enhancement, automation, ci-cd

**Body:**

### Summary

Create a CI/CD pipeline that validates video production assets and generates previews automatically.

### Goals

- [ ] Script validation (markdown lint)
- [ ] Lua script syntax checking
- [ ] Scene plan generation on PR
- [ ] Narration preview generation

### Pipeline Stages

1. **Validate Scripts**
   - Markdown linting
   - Link checking
   - Metadata validation

2. **Generate Assets**
   - Extract narration text
   - Create scene plans
   - Generate descriptions

3. **Preview Generation**
   - TTS preview for narration (first 30 seconds)
   - Timeline visualization

4. **Artifact Storage**
   - Upload generated assets as artifacts
   - Store for manual review

### GitHub Actions Workflow

```yaml
name: Video Asset Validation

on:
  push:
    paths:
      - 'docs/video_scripts/**'
      - 'tools/video/**'
  pull_request:
    paths:
      - 'docs/video_scripts/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Lint scripts
        run: markdownlint docs/video_scripts/
      
      - name: Generate scene plans
        run: python -m tools.video.scene_planner --all
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: video-assets
          path: scene_plans/
```

---

## How to Create These Issues

### Using GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Create issues from this file
gh issue create \
    --title "Implement Video Production Pipeline MVP" \
    --body-file issue_1_body.md \
    --label "enhancement,documentation,video-production"

gh issue create \
    --title "Integrate AI Text-to-Speech for Video Narration" \
    --body-file issue_2_body.md \
    --label "enhancement,video-production,ai"
```

### Using GitHub Web Interface

1. Go to https://github.com/TheAnsarya/dragon-warrior-info/issues
2. Click "New Issue"
3. Copy title and body from above
4. Add appropriate labels
5. Submit

---

*Generated for Dragon Warrior Info Project video production toolchain*
