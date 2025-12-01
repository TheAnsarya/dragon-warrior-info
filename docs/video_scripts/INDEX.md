# Video Tutorial Scripts Index

This folder contains complete scripts for the Dragon Warrior ROM Hacking video tutorial series.

## Episode List

| Episode | Title | Duration | Difficulty | Script |
|---------|-------|----------|------------|--------|
| 1 | Getting Started | 10-12 min | Beginner | [episode_01_getting_started.md](episode_01_getting_started.md) |
| 2 | Monster Stats | 8-10 min | Beginner | [episode_02_monster_stats.md](episode_02_monster_stats.md) |
| 3 | Graphics Editing | 12-15 min | Intermediate | [episode_03_graphics_editing.md](episode_03_graphics_editing.md) |
| 4 | Dialog Editing | 10-12 min | Beginner-Int | [episode_04_dialog_editing.md](episode_04_dialog_editing.md) |
| 5 | Game Balance | 10-12 min | Beginner-Int | [episode_05_game_balance.md](episode_05_game_balance.md) |
| 6 | Advanced Assembly | 15-18 min | Advanced | [episode_06_advanced_assembly.md](episode_06_advanced_assembly.md) |
| 7 | Troubleshooting | 8-10 min | All Levels | [episode_07_troubleshooting.md](episode_07_troubleshooting.md) |

**Total Series Duration:** ~75-90 minutes

## Episode Summaries

### Episode 1: Getting Started

Your first mod in 10 minutes! Fork the enhanced project from GitHub, install Python and Ophis, add your Dragon Warrior ROM, run the build script, and test in an emulator. By the end, you'll have a working modding environment ready for any changes you want to make.

### Episode 2: Monster Stats

Make the game your own by editing monster data. Open `assets/json/monsters.json`, find the Slime entry, and crank up its HP, attack, or gold drops. Rebuild, fight the modified Slime in-game, and experience the thrill of your first gameplay change. Also covers the Universal Editor GUI for visual editing.

### Episode 3: Graphics Editing

Create custom sprites and tiles using any image editor! Extract graphics to PNG files, edit them in GIMP/Photoshop/Paint, and rebuild. Covers NES palette limitations (4 colors per tile), the asset workflow, and testing tips. No specialized tools like YY-CHR required.

### Episode 4: Dialog Editing

Give Alefgard a new voice! Edit `assets/json/dialogs.json` to change what NPCs say. Learn control codes like `{NAME}`, `{WAIT}`, and `{ITEM}`. Make the King's intro more dramatic, add humor to guards, or create entirely new story elements.

### Episode 5: Game Balance

Take control of Dragon Warrior's infamous grind. Adjust experience curves for faster leveling, tweak gold drops and shop prices, modify spell costs and effects, and boost early equipment. Create "Easy Mode" for friends or "Nightmare Mode" for challenge runs.

### Episode 6: Advanced Assembly

Go beyond JSON into the 6502 assembly code. Learn basic instructions (LDA, STA, CMP, BEQ), navigate the source files, use Mesen's debugger to find code locations, and implement changes like modified damage calculations or a critical hit system.

### Episode 7: Troubleshooting

When things go wrong (and they will!), this episode has your back. Covers build errors (Ophis/Python not found, undefined labels), JSON syntax mistakes, emulator crashes, and environment setup issues. Includes diagnostic commands and where to get help.

## Production Guide

For video production automation and workflows, see: [VIDEO_AUTOMATION.md](VIDEO_AUTOMATION.md)

## Script Format

Each episode script includes:

1. **Video Metadata** - Title, duration, difficulty, prerequisites
2. **Chapter Markers** - YouTube timestamps for navigation
3. **Full Script** - Complete narration with visual cues
4. **Video Description Template** - Ready-to-copy YouTube description
5. **Production Notes** - Footage requirements, B-roll suggestions
6. **Revision History** - Version tracking

## How to Use These Scripts

### For Video Creators

1. Read through the full script
2. Prepare any mentioned assets or examples
3. Record narration following the script
4. Record screen captures as indicated by `[VISUAL:]` tags
5. Use the description template for YouTube upload

### For Documentation

These scripts also serve as detailed written tutorials. Users can follow along even without watching videos.

### For Contributors

1. Follow the existing format for consistency
2. Include timing estimates for each section
3. Add production notes for complex visuals
4. Keep narration conversational but informative

## Related Documentation

- [VIDEO_TUTORIALS.md](../VIDEO_TUTORIALS.md) - Original planning document
- [README.md](../../README.md) - Project overview
- [BUILD_GUIDE.md](../BUILD_GUIDE.md) - Build instructions
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Error solutions

## Status

| Phase | Status |
|-------|--------|
| Scripts Written | ✅ Complete |
| Recording | ⏳ Not Started |
| Editing | ⏳ Not Started |
| Publishing | ⏳ Not Started |

---

*Created: 2025-12-02*
*Last Updated: 2025-12-02*

