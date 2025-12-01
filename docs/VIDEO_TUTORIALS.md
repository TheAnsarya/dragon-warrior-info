# Dragon Warrior ROM Hacking Video Tutorial Series

A planned series of video tutorials for visual learners covering common ROM hacking workflows.

---

## Overview

While comprehensive written documentation exists for all Dragon Warrior ROM hacking tasks, video tutorials can demonstrate workflows more effectively for hands-on learners. This document outlines the planned video series.

---

## Planned Video Topics

### Episode 1: Getting Started
**Title:** "Getting Started: Fork to First Build in 10 Minutes"

**Topics:**
- Forking the repository
- Installing prerequisites (Python, Ophis)
- Running your first build
- Verifying the ROM in an emulator

**Duration:** ~10 minutes

**Related Docs:** `README.md`, `docs/BUILD_GUIDE.md`

---

### Episode 2: Monster Stats
**Title:** "Modifying Monster Stats: Complete Walkthrough"

**Topics:**
- Understanding monster JSON structure
- Opening the Universal Editor
- Changing attack, defense, HP values
- Regenerating and testing

**Duration:** ~8 minutes

**Related Docs:** `docs/MODIFICATION_EXAMPLES.md` (Example 1)

---

### Episode 3: Graphics Editing
**Title:** "Editing Graphics with CHR Tools"

**Topics:**
- Extracting CHR tiles
- Using YY-CHR or similar tools
- NES palette restrictions
- Reinserting modified graphics
- Testing in emulator

**Duration:** ~12 minutes

**Related Docs:** `docs/CHR_WORKFLOW.md`

---

### Episode 4: Dialog Editing
**Title:** "Creating Custom Dialog and Text"

**Topics:**
- Understanding TBL encoding
- Using the Dialog Editor tab
- Control codes (NAME, ITEM, WAIT, etc.)
- Testing dialog in-game

**Duration:** ~10 minutes

**Related Docs:** `docs/ASSET_PIPELINE.md` (Dialog section)

---

### Episode 5: Game Balance
**Title:** "Adjusting Game Balance and Difficulty"

**Topics:**
- Modifying experience curves
- Changing shop prices
- Adjusting spell effects
- Testing balance changes

**Duration:** ~10 minutes

**Related Docs:** `docs/technical/GAME_FORMULAS.md`

---

### Episode 6: Advanced Assembly
**Title:** "Advanced: Assembly Code Modifications"

**Topics:**
- Understanding 6502 assembly basics
- Finding code locations
- Making simple patches
- Using breakpoints in emulators

**Duration:** ~15 minutes

**Related Docs:** `docs/technical/GAME_FORMULAS.md` (Code Locations)

---

### Episode 7: Troubleshooting
**Title:** "Troubleshooting Common Build Errors"

**Topics:**
- Understanding error messages
- Running diagnostics
- Common issues and solutions
- When to ask for help

**Duration:** ~8 minutes

**Related Docs:** `docs/TROUBLESHOOTING.md`

---

## Production Notes

### Recording Setup
- **Screen Recording:** OBS Studio or similar
- **Resolution:** 1920x1080 (1080p)
- **Audio:** Clear narration with noise reduction
- **Editor Zoom:** 150% for readability

### Content Guidelines
- Keep videos focused (5-15 minutes each)
- Show VS Code, PowerShell, emulator testing
- Provide code/commands in video descriptions
- Include chapter markers/timestamps
- Add captions for accessibility

### Platform
- **Primary:** YouTube (unlisted or public)
- **Backup:** Video files in cloud storage
- **Links:** Add to documentation pages

### Script Template
```
1. Introduction (30 seconds)
   - What we'll accomplish
   - Prerequisites

2. Main Content (5-12 minutes)
   - Step-by-step demonstration
   - Explanations as we go
   - Common pitfalls to avoid

3. Testing (1-2 minutes)
   - Verify changes work
   - Show results in emulator

4. Recap (30 seconds)
   - Summary of steps
   - Link to written docs
```

---

## Timeline

| Episode | Priority | Status |
|---------|----------|--------|
| Ep 1: Getting Started | High | Planned |
| Ep 2: Monster Stats | High | Planned |
| Ep 3: Graphics Editing | High | Planned |
| Ep 4: Dialog Editing | Medium | Planned |
| Ep 5: Game Balance | Medium | Planned |
| Ep 6: Advanced Assembly | Low | Planned |
| Ep 7: Troubleshooting | Medium | Planned |

---

## Resources Required

### Software
- [ ] Screen recording software (OBS Studio)
- [ ] Video editing software
- [ ] Audio editing (Audacity)

### Assets
- [ ] Intro/outro graphics
- [ ] Dragon Warrior themed overlays
- [ ] Example project files

### Time Estimate
- **Per Video:** 2-4 hours recording/editing
- **Total Series:** ~20 hours

---

## Contributing

If you'd like to help create video tutorials:

1. Review the planned topics above
2. Create a script following the template
3. Record and edit following production guidelines
4. Submit via pull request with video link

---

## Related Documentation

- [README.md](../README.md) - Project overview
- [MODIFICATION_EXAMPLES.md](MODIFICATION_EXAMPLES.md) - Written tutorials
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error solutions
- [CHR_WORKFLOW.md](CHR_WORKFLOW.md) - Graphics workflow
- [ASSET_PIPELINE.md](ASSET_PIPELINE.md) - Build system

---

*Status: Planning Phase*
*Priority: Low (nice-to-have supplement to written documentation)*
