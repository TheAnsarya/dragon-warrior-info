# Dragon Warrior (NES) - Label Reference Guide

This document provides comprehensive documentation for the named labels in the Dragon Warrior disassembly.

## Label Naming Convention

Labels follow the format: `FunctionName_Description` or `DataStructure_Field`

### Function Labels
- Main function entry points use CamelCase
- Internal labels use the parent function name as a prefix
- Branch targets use `_Branchto`, `_BranchTruthy`, `_BranchFalsy`, etc.
- Loop constructs use `_Loop`, `_Continue`, `_Break`, `_Done`
- Return points use `_Exit`, `_Return`, `_Done`

### Data Labels
- Tables use `TableName_EntryXX` format
- Pointers use `_Ptr` or `_Word` suffix
- Byte data uses `_Byte` suffix
- Arrays indexed by value use `_ByValue`

## Bank Structure

### Bank 00 (CPU $8000-$BFFF) - Main Code Bank
Contains core game systems:
- Dialog system and text rendering
- Window management
- Menu system (items, spells, status)
- Combat calculations
- NPC interaction
- Equipment handling
- Gold management
- Experience/level calculations

### Bank 01 (CPU $8000-$BFFF) - Switchable Bank
Contains:
- Sound engine
- Music playback
- SFX routines
- Additional dialog data
- Map transitions
- Overworld processing

### Bank 02 (CPU $8000-$BFFF) - Switchable Bank
Contains:
- Intro/title sequence
- Enemy encounter tables
- World map data
- Starburst animation
- Palette data

### Bank 03 (CPU $C000-$FFFF) - Fixed Bank
Contains:
- Reset vector and initialization
- NMI handler
- Main game loop
- Bank switching routines
- Common utilities

## Key Systems

### Dialog System (Bank 00)
- `DoDialogHiBlock` - Main dialog processing
- `GetDialogChar` - Character retrieval
- `PrintChar` - Character display
- `DialogWaitBtn` - Button wait
- `ClearDialog` - Dialog cleanup

### Window System (Bank 00)
- `DoWindow` - Window creation/management
- `WindowErase` - Window removal
- `WindowYesNo` - Yes/No prompts
- `WindowLoadCmd` - Command window

### Combat System (Bank 00)
- `CalcAttackDamage` - Attack damage calculation
- `CalcDefense` - Defense calculation
- `GetEnemy` - Enemy data retrieval
- `DoBattleRound` - Combat round processing

### Sound System (Bank 01)
- `UpdateSound` - Main sound processing
- `PlaySFX` - Sound effect playback
- `PlayMusic` - Music playback
- `SFX_*` - Individual sound effects

### Intro System (Bank 02)
- `DoIntroRou` - Intro routine
- `IntroLoop` - Main intro loop
- `Starburst*` - Starburst animation

## Memory Map Labels

See `Dragon_Warrior_Defines.asm` for complete memory map including:
- Zero page variables ($00-$FF)
- RAM variables ($0200-$07FF)
- I/O registers ($2000-$401F)
- ROM address aliases

## Statistics

- **Total named labels**: ~3,000+
- **Bank 00**: ~1,200 labels
- **Bank 01**: ~1,000 labels
- **Bank 02**: ~500 labels
- **Bank 03**: ~300 labels

## Version History

- 2025-01: Initial label naming from disassembly
- 2025-01-07: Renamed 535 `_L_XXXX` generic labels to descriptive names
- 2025-01-07: Removed 5,143 unreferenced fine-grained labels
