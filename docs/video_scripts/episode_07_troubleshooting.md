# Episode 7: Troubleshooting Common Build Errors

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Troubleshooting Common Errors" |
| **Duration** | 8-10 minutes |
| **Difficulty** | All Levels |
| **Prerequisites** | Episode 1 setup |
| **Related Docs** | `docs/TROUBLESHOOTING.md`, `docs/BUILD_GUIDE.md` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
0:30 - Error Categories
1:15 - Build/Assembly Errors
3:00 - JSON/Data Errors
4:30 - Runtime/Emulator Errors
6:00 - Environment Setup Issues
7:15 - Using the Diagnostic Tools
8:30 - Getting Help
9:15 - Closing
```

---

## Full Script

### [0:00] Introduction (30 seconds)

**[VISUAL: Error message on screen, person looking confused]**

**NARRATION:**
> "Getting errors? Don't worry - they happen to everyone! This episode covers the most common Dragon Warrior ROM hacking errors and how to fix them.
>
> I'll walk you through build errors, JSON mistakes, emulator issues, and setup problems. Let's debug together!"

---

### [0:30] Error Categories (45 seconds)

**[VISUAL: Four-quadrant diagram of error types]**

**NARRATION:**
> "Errors fall into four main categories:
>
> 1. **Build/Assembly** - Ophis can't assemble the code
> 2. **JSON/Data** - Invalid or corrupt data files
> 3. **Runtime** - ROM builds but crashes in emulator
> 4. **Environment** - Missing tools or bad configuration
>
> Let's tackle each one."

---

### [1:15] Build/Assembly Errors (1 minute 45 seconds)

**[VISUAL: Terminal showing assembly errors]**

**NARRATION:**
> "Build errors appear when running `build.ps1`. Common ones:
>
> **'Ophis not found' or 'command not recognized':**"

```
Ophis : The term 'Ophis' is not recognized as the name of a cmdlet
```

> "Fix: Add Ophis to your PATH, or copy `Ophis.exe` to the project folder.
>
> **'Undefined label' error:**"

```
Error: Undefined label 'MonsterTable' in Bank02.asm
```

> "Fix: Check spelling. Labels are case-sensitive. Also verify the source file including that label is in your build.
>
> **'Branch out of range':**"

```
Error: Branch out of range at line 1234
```

> "Fix: Branches (BEQ, BNE, etc.) can only jump 127 bytes. Use a JMP with a nearby label instead.
>
> **'Duplicate symbol' or 'redefined label':**"

```
Warning: Symbol 'DamageCalc' redefined
```

> "Fix: Two things have the same name. Rename one or remove the duplicate."

---

### [3:00] JSON/Data Errors (1 minute 30 seconds)

**[VISUAL: JSON file with red error squiggles]**

**NARRATION:**
> "JSON errors break the asset generators. VS Code usually highlights them:
>
> **Syntax errors (missing comma, bracket):**"

```json
{
  "name": "Slime"     // Missing comma!
  "hp": 3
}
```

> "Fix: Look for the red squiggle. Usually a missing comma, quote, or bracket nearby.
>
> **Invalid values:**"

```json
{"hp": "ten"}  // Should be a number!
```

> "Fix: Check the data type. HP should be a number, not string.
>
> **Missing required fields:**"

```
Generator error: Missing required field 'id' in monster entry
```

> "Fix: Check the schema. Each entry needs specific fields. Copy an existing entry as template."

**[VISUAL: Use VS Code JSON validation features]**

---

### [4:30] Runtime/Emulator Errors (1 minute 30 seconds)

**[VISUAL: Emulator showing glitchy/crashed game]**

**NARRATION:**
> "ROM builds but doesn't work? These are runtime errors:
>
> **Game freezes on title screen:**
> Usually a bad jump address or infinite loop in assembly changes. Undo recent assembly edits.
>
> **Garbled graphics:**
> CHR data corruption. Check your graphics files and conversion. Try re-extracting original graphics.
>
> **Wrong text appears:**
> Dialog table offset issue. Verify your JSON doesn't exceed original text sizes.
>
> **Crashes in specific situations:**
> Edge case bug. Use emulator debugger to find the crash point, then trace back to your changes."

**[VISUAL: Debugger catching a crash]**

> "Pro tip: Save states are your friend. Create saves at different game points to quickly test specific scenarios."

---

### [6:00] Environment Setup Issues (1 minute 15 seconds)

**[VISUAL: System configuration screens]**

**NARRATION:**
> "Environment problems prevent anything from working:
>
> **'Python not found':**"

```
Python : The term 'python' is not recognized
```

> "Fix: Reinstall Python and CHECK 'Add to PATH'. Or close and reopen PowerShell after installing.
>
> **'ROM not found':**"

```
Error: Cannot find dragon_warrior.nes in roms/
```

> "Fix: Place your legally-obtained ROM in the `roms` folder with exact name `dragon_warrior.nes`.
>
> **Permission denied:**"

```
Access to the path 'build/output.nes' is denied
```

> "Fix: Close any programs using the ROM (emulators!). Or run PowerShell as Administrator."

---

### [7:15] Using the Diagnostic Tools (1 minute 15 seconds)

**[VISUAL: Running diagnostic script]**

**NARRATION:**
> "The project includes diagnostic tools:
>
> **Verify your build:**"

```powershell
python tools/verify_build.py
```

> "This compares your built ROM against expected checksums to catch corruption.
>
> **Check asset status:**"

```powershell
python tools/generate_all_assets.py
```

> "Shows status of each generator. Failed generators indicate JSON problems.
>
> **Run the test suite:**"

```powershell
pytest tests/
```

> "Automated tests catch many common issues. If all tests pass, your environment is working."

---

### [8:30] Getting Help (45 seconds)

**[VISUAL: GitHub Issues page, community links]**

**NARRATION:**
> "Still stuck? Here's how to get help:
>
> 1. **Check the docs** - `docs/TROUBLESHOOTING.md` has more solutions
> 2. **Search Issues** - Someone may have had the same problem
> 3. **Create an Issue** - Include:
>    - Full error message
>    - What you were trying to do
>    - Your OS and tool versions
> 4. **ROM hacking communities** - ROMhacking.net forums, Discord servers
>
> Everyone started as a beginner. Don't be afraid to ask!"

---

### [9:15] Closing (30 seconds)

**[VISUAL: Happy ending - successful build]**

**NARRATION:**
> "Errors are frustrating but fixable. Remember:
> - Read error messages carefully - they usually point to the problem
> - Undo recent changes to find what broke
> - Use version control to compare working vs broken states
> - Ask for help when needed
>
> That's the complete tutorial series! You have all the tools to create amazing Dragon Warrior mods.
>
> Good luck, and happy hacking!"

---

## Video Description Template

```
🎮 Dragon Warrior ROM Hacking: Troubleshooting Common Errors

Having build problems? This episode covers all the common errors you'll encounter and how to fix them - assembly errors, JSON mistakes, runtime crashes, and setup issues.

📋 TIMESTAMPS:
0:00 - Introduction
0:30 - Error Categories
1:15 - Build/Assembly Errors
3:00 - JSON/Data Errors
4:30 - Runtime/Emulator Errors
6:00 - Environment Setup Issues
7:15 - Using the Diagnostic Tools
8:30 - Getting Help
9:15 - Closing

❌ COMMON ERRORS & FIXES:

"Ophis not found"
→ Add to PATH or copy Ophis.exe to project

"Undefined label"
→ Check spelling (case-sensitive!)

"Python not found"
→ Reinstall with "Add to PATH" checked

JSON syntax error
→ Look for missing commas or brackets

Game crashes
→ Undo recent assembly changes

⌨️ DIAGNOSTIC COMMANDS:
```powershell
# Verify build integrity
python tools/verify_build.py

# Check all generators
python tools/generate_all_assets.py

# Run test suite
pytest tests/
```

📁 HELP RESOURCES:
• docs/TROUBLESHOOTING.md - Full troubleshooting guide
• GitHub Issues - Search or create an issue
• ROMhacking.net Forums - Community help

📺 COMPLETE SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 3: Graphics Editing: [LINK]
• Ep 4: Dialog Editing: [LINK]
• Ep 5: Game Balance: [LINK]
• Ep 6: Advanced Assembly: [LINK]

#DragonWarrior #NES #ROMHacking #Troubleshooting #Tutorial
```

---

## Production Notes

### Error Examples to Capture
- [ ] Ophis not found error
- [ ] Python not found error
- [ ] JSON syntax error in VS Code
- [ ] Undefined label assembly error
- [ ] Emulator crash/glitch footage

### Before/After Clips
- [ ] Broken build → fixed build
- [ ] Corrupt graphics → fixed graphics
- [ ] Error message → running game

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |

