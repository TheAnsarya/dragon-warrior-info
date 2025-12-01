# Dragon Warrior Assembly Bank Map

Comprehensive documentation of what each assembly code bank contains and where specific game systems are located.

---

## Overview

Dragon Warrior uses a standard NES ROM layout with 4 banks of assembly code:
- **Bank00.asm** - Core engine, graphics, sound foundations
- **Bank01.asm** - Music engine, windows, game data tables
- **Bank02.asm** - Dialog text, intro sequence
- **Bank03.asm** - Main game loop, battle system, save/load

---

## Bank00.asm - Core Engine

**File:** `source_files/Bank00.asm`  
**Size:** ~7,000+ lines  
**CPU Address Range:** $8000-$9FFF (estimated)

### Contents

#### Graphics System
| Address Range | Label | Description |
|---------------|-------|-------------|
| $8000+ | - | PPU initialization |
| - | ScrollSystem | Background scrolling routines |
| - | TileBlockGraphics | 16x16 metatile definitions |
| - | PatternTables | CHR-RAM loading routines |

#### Core Systems
| Component | Description |
|-----------|-------------|
| NMI Handler | Vertical blank interrupt |
| PPU Updates | Sprite and background rendering |
| Scroll Engine | Map scrolling implementation |
| Palette Control | Color palette management |

#### Map Data
| Data | Description |
|------|-------------|
| Map Metatiles | 16x16 tile block definitions |
| Map Graphics | Tile graphics data |
| Map Collision | Walkable/blocked tile flags |

### Key Routines

```
WaitForNMI          - Wait for vertical blank
UpdatePPU           - Send updates to PPU
LoadPatterns        - Load tile patterns to CHR-RAM
SetScroll           - Set scroll position
DrawMetatile        - Draw 16x16 metatile
```

---

## Bank01.asm - Music and Data

**File:** `source_files/Bank01.asm`  
**Size:** ~9,657 lines  
**CPU Address Range:** $8000-$BFFF

### Contents

#### Music Engine ($8000-$8900)
| Address | Label | Description |
|---------|-------|-------------|
| $8000 | MusicPointers | Sound/music pointer table |
| $801A | SetBaseStats | Get player stats for level |
| $8333 | SQ1LevelUp | Level up sound (square 1) |
| $8640 | SQ2LevelUp | Level up sound (square 2) |
| $843B | AttackSFX | Attack sound effect |

#### Window System ($A100-$A800)
| Address | Label | Description |
|---------|-------|-------------|
| $A194 | ShowWindow | Display game window |
| $A19B | WindowSequence | Window building sequence |
| $A230 | WindowEngine | Main window rendering |
| $A63D | DoBlinkingCursor | Selection cursor animation |

#### Game Data Tables

##### Player Stats ($A0CD-$A180)
| Address | Label | Description |
|---------|-------|-------------|
| $A0CB | BaseStatsTbl | Player base stats per level |
| - | Format | 6 bytes/level: STR, AGI, HP, MP, Spell1, Spell2 |

##### Monster Stats ($9E49-$A0CA)
| Address | Label | Description |
|---------|-------|-------------|
| $9E49 | EnStatTblPtr | Pointer to enemy stats |
| $9E4B | EnStatTbl | Enemy statistics (16 bytes/enemy) |
| - | Format | ATK, DEF, HP, Spells, AGI, MDEF, EXP, Gold |

##### Sprite Tables ($99E4-$9E48)
| Address | Label | Description |
|---------|-------|-------------|
| $99E4 | EnSpritesPtrTbl | Enemy sprite pointers |
| $9A32 | DKnightSprts | Dark Knight sprites |
| $9A3E | SkelSprts | Skeleton sprites |
| $9A87 | DrollSprts | Droll sprites |

##### Item/Treasure Tables ($9E00-$9E48)
| Address | Label | Description |
|---------|-------|-------------|
| $9E00 | TreasureTbl | Chest contents by location |

### Key Constants

```asm
; Level data (6 bytes per level, 30 levels)
; Byte 1: Strength
; Byte 2: Agility  
; Byte 3: Max HP
; Byte 4: Max MP
; Byte 5: Healmore/Hurtmore spell flags
; Byte 6: Other spell flags
```

---

## Bank02.asm - Dialog Text

**File:** `source_files/Bank02.asm`  
**Size:** ~8,000+ lines  
**CPU Address Range:** $8000-$BFFF

### Contents

#### Dialog System
| Component | Description |
|-----------|-------------|
| TextPointerTable | Pointers to dialog entries |
| TextCommandPointerTable | Control code handlers |
| TextChunkDialogue | Actual dialog text data |

#### Text Blocks
| Block | Content |
|-------|---------|
| TextBlock1 | Battle messages, system text |
| TextBlock2-19 | NPC dialogs by region |

#### Control Codes
| Code | Byte | Function |
|------|------|----------|
| {NAME} | $F8 | Insert player name |
| {ENMY} | $F4 | Insert enemy name |
| {ITEM} | $F7 | Insert item name |
| {SPEL} | $F6 | Insert spell name |
| {AMNT} | $F5 | Insert number |
| {WAIT} | $FB | Wait for button press |
| {END} | $FC | End of text |
| \n | $FD | New line |

#### Intro Sequence
| Address | Label | Description |
|---------|-------|-------------|
| $8000+ | IntroRoutine | Opening sequence code |
| - | ScrollingText | Title screen text scroll |
| - | PrincessScene | Intro cutscene |

### Text Encoding

```
$00-$09  Numbers 0-9
$0A-$23  Lowercase a-z
$24-$3D  Uppercase A-Z
$3E-$5F  Punctuation and special
$F0-$FC  Control codes
$FD      Newline
```

---

## Bank03.asm - Game Logic

**File:** `source_files/Bank03.asm`  
**Size:** ~10,922 lines  
**CPU Address Range:** $C000-$FFFF

### Contents

#### Main Game Loop ($C000-$D000)
| Address | Label | Description |
|---------|-------|-------------|
| $C000 | MainLoop | Core game loop |
| $C55B | UpdateRandNum | Random number generator |
| $C6F0 | Dowindow | Display window wrapper |

#### Battle System ($E000-$F000)
| Address | Label | Description |
|---------|-------|-------------|
| $E651 | PlayerCalcHitDmg | Player attack damage |
| $E654 | CalcDamage | Damage calculation result |
| $EBD6 | EnCalcHitDmg | Enemy attack damage |
| $EBEE | EnCastSpell | Enemy spell casting |
| $EE54 | ExitFight | Return to map after battle |
| $EFE5 | PlayerCalcHitDmg | Physical damage formula |
| $EFF4 | EnCalcHitDmg | Enemy physical damage |

#### Spell System ($DB00-$DC00)
| Address | Label | Description |
|---------|-------|-------------|
| $DBB8 | DoHeal | HEAL spell implementation |
| $DBD7 | DoHealmore | HEALMORE spell implementation |
| $DBC2 | PlayerAddHP | Add HP to player |
| $DBCB | PlayerMaxHP | Cap HP at maximum |

#### Level/Stats System ($F050-$F110)
| Address | Label | Description |
|---------|-------|-------------|
| $F050 | LoadStats | Load stats from level |
| $F056 | GetLevelLoop | Determine player level |
| $F0CD | AddItemBonuses | Apply equipment bonuses |
| $F10C | ReduceStat | Apply 10% stat penalty |

#### Experience Table ($F35B-$F396)
| Address | Label | Description |
|---------|-------|-------------|
| $F35B | LevelUpTbl | Experience requirements |
| - | Format | 2 bytes per level (30 levels) |

#### Map System ($F397+)
| Address | Label | Description |
|---------|-------|-------------|
| $F397 | CmbtBGPlcmntTbl | Combat background layout |
| $F3C8 | MapEntryTbl | Map connection table |

#### Save/Load System
| Address | Label | Description |
|---------|-------|-------------|
| - | SaveGame | Write to SRAM |
| - | LoadGame | Read from SRAM |
| - | ValidateSave | Checksum verification |

#### Interrupt Vectors ($FFFA-$FFFF)
| Address | Vector | Handler |
|---------|--------|---------|
| $FFFA | NMI | VBlank interrupt |
| $FFFC | RESET | Power-on/reset |
| $FFFE | IRQ | Hardware interrupt |

---

## Cross-Reference Tables

### Finding Game Systems

| System | Primary Bank | Key Addresses |
|--------|--------------|---------------|
| Music/Sound | Bank01 | $8000-$8900 |
| Windows/UI | Bank01 | $A100-$A800 |
| Monster Stats | Bank01 | $9E4B |
| Player Stats | Bank01 | $A0CD |
| Dialog Text | Bank02 | TextChunkDialogue |
| Battle Logic | Bank03 | $E000-$F000 |
| Damage Calcs | Bank03 | $EFE5, $EFF4 |
| Spells | Bank03 | $DBB8-$DC00 |
| Level System | Bank03 | $F050-$F110 |
| Experience | Bank03 | $F35B |
| Save/Load | Bank03 | SRAM routines |

### RAM Variables (Zero Page)

| Address | Alias | Description |
|---------|-------|-------------|
| $3C | CalcDamage | Calculated damage |
| $3D | AttackStat | Current attack value |
| $3E | DefenseStat | Current defense value |
| $BA | ExpLB | Experience (low byte) |
| $BB | ExpUB | Experience (high byte) |
| $C5 | HitPoints | Current HP |
| $C6 | DisplayedMaxHP | Max HP display |

---

## Modification Guide

### Changing Monster Stats
1. Locate `EnStatTbl` at $9E4B in Bank01.asm
2. Each monster = 16 bytes (8 used + 8 unused)
3. Modify ATK/DEF/HP/etc. values

### Changing Experience Curve
1. Locate `LevelUpTbl` at $F35B in Bank03.asm
2. 2 bytes per level (little-endian)
3. Modify experience requirements

### Changing Spell Effects
1. Locate `DoHeal` at $DBB8 in Bank03.asm
2. Modify base value and random range
3. Example: `ADC #$0A` changes HEAL base to 10

### Changing Equipment Bonuses
1. Locate bonus tables in Bank01 or generated files
2. Modify `WeaponsBonusTbl`, `ArmorBonusTbl`, `ShieldBonusTbl`

---

## Related Documentation

- [GAME_FORMULAS.md](technical/GAME_FORMULAS.md) - Detailed formula documentation
- [ROM_MAP.md](datacrystal/ROM_MAP.md) - Overall ROM structure
- [MODIFICATION_EXAMPLES.md](MODIFICATION_EXAMPLES.md) - Practical modification guides

---

*Last Updated: Session documentation improvements*
