# Dragon Warrior ROM Hacking Guide

**Complete Guide to Modifying Dragon Warrior (NES)**

Version: 1.0  
Last Updated: November 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [ROM Structure](#rom-structure)
3. [Memory Map](#memory-map)
4. [Data Formats](#data-formats)
5. [Build System](#build-system)
6. [Modification Workflow](#modification-workflow)
7. [Asset Extraction](#asset-extraction)
8. [Asset Modification](#asset-modification)
9. [Testing & Verification](#testing--verification)
10. [Advanced Topics](#advanced-topics)

---

## Introduction

This guide covers everything you need to know to modify Dragon Warrior (NES) ROM. The project includes:

- **Complete disassembly** - Fully commented 6502 assembly source code
- **Asset extraction tools** - Extract graphics, text, data, maps
- **Build system** - Reassemble ROM from source with verification
- **Modification tools** - Edit and reinsert game data
- **Documentation** - Memory maps, data structures, algorithms

### Prerequisites

- **Ophis Assembler** - 6502 assembler (included in `/Ophis/`)
- **Python 3.8+** - For extraction/modification tools
- **PowerShell 5.1+** - For build scripts (Windows)
- **Hex Editor** - For manual ROM editing (optional)
- **NES Emulator** - For testing (Mesen, FCEUX, etc.)

### ROM Versions

Dragon Warrior has two versions:

| Version | Differences | File Offset | PRG0 Value | PRG1 Value |
|---------|-------------|-------------|------------|------------|
| PRG0 | Original release | 0x3FAE | 0x37 | 0x32 |
| PRG0 | Original release | 0x3FAF | 0x32 | 0x29 |
| PRG0 | Original release | 0xAF7C | 0xEF | 0xF0 |
| PRG1 | Revised (recommended) | - | - | - |

**Our disassembly builds PRG1 by default.** To build PRG0, modify the bytes in `Bank00.asm` and `Bank02.asm` as documented in the source comments.

---

## What and Where to Edit

This section provides quick reference for finding and modifying specific game content.

### Monster Graphics

**Location:** `extracted_assets/chr_organized/sprites_monsters_*.png`

Monster sprites are extracted as organized PNG files:

- `sprites_monsters_01_slimes.png` - Slimes and basic enemies
- `sprites_monsters_02_dragons.png` - Dragon family
- `sprites_monsters_03_undead.png` - Ghosts, skeletons, wraiths
- `sprites_monsters_04_humanoid.png` - Knights, wizards, golems
- `sprites_monsters_05_special.png` - Metal slime, Dragonlord forms

**Format:** 8×8 tiles in PNG format with proper NES palettes
**Restrictions:**
- Must use 4-color NES palettes (3 colors + transparency)
- Maximum 64 8×8 tiles per sprite sheet
- Each tile is 8×8 pixels
- Reinsertion requires CHR-ROM rebuild

**How to Edit:**
1. Edit PNG files in graphics editor (GIMP, Aseprite, etc.)
2. Maintain NES color restrictions
3. Use `tools/graphics_reinserter.py` to rebuild CHR-ROM *(when implemented)*
4. Rebuild ROM with `build_rom.ps1`

### Monster Stats

**Location:** `extracted_assets/data/monsters.json`

**Also in Assembly:** `source_files/Bank01.asm` at line ~4000+ (offset 0x5E5B)

**Format (JSON):**

```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 3,
    "strength": 5,
    "agility": 15,
    "attack_power": 5,
    "defense": 3,
    "magic_defense": 1,
    "experience_reward": 1,
    "gold_reward": 2,
    "spell": 0
  }
}
```

**Restrictions:**
- All stats 0-255 (1 byte each)
- 39 monsters total (ID 0-38)
- Spell field is bitflag (0 = no spell)

**How to Edit:**
1. Method A: Edit `monsters.json` and use `tools/reinsert_assets.py`
2. Method B: Edit `Bank01.asm` directly at monster data table
3. Rebuild ROM

### Palettes

**Location:** `extracted_assets/palettes/` (when extracted)

**Also in Assembly:** `source_files/Bank01.asm` - Search for "palette" or "PPU"

NES has 8 palettes (4 background, 4 sprite):
- Each palette = 4 colors (1 shared background + 3 unique)
- Colors from NES 64-color master palette

**Common Palette Addresses:**
- Background palettes: Various addresses in Bank01/Bank03
- Sprite palettes: Set dynamically via PPU writes

**How to Edit:**
1. Find palette data in `Bank01.asm` or `Bank03.asm`
2. Edit color values (0x00-0x3F from NES palette)
3. Rebuild ROM
4. Test in emulator to verify colors

### Dialog and Text

**Location (Assembly):** `source_files/Bank02.asm`

**Structure:**
- TextBlock1 through TextBlock19 - All game dialog
- Special control codes: HERO, WAIT, LINE, PAGE, CHOICE, etc.

**Encoding:**
- 0x00-0x5F: Basic ASCII (offset by 0x20)
- 0x60-0x7F: Extended characters
- 0x80-0x8F: Word compression ("the", "thou", "thy", etc.)
- 0xF0-0xFF: Control codes

**Example:**

```assembly
TextBlock1Entry0:
	.text "Welcome to Alefgard,", LINE
	.text HERO, ".", END
```

**Restrictions:**
- Text is compressed using dictionary words
- Must fit within ROM space limits
- Control codes must be used correctly
- Text encoding is custom (not pure ASCII)

**How to Edit:**
1. Edit dialog strings in `Bank02.asm`
2. Use provided text encoding (see `extracted_assets/text/` for encoding table)
3. Stay within line length limits
4. Rebuild ROM

### Maps

**Location:** `extracted_assets/maps/*.json`

**Also in Assembly:** `source_files/Bank00.asm` and map data tables

**Format:**

```json
{
  "id": 1,
  "name": "Tantegel Castle - Throne Room",
  "width": 30,
  "height": 30,
  "tiles": [ /* 2D array of tile IDs */ ],
  "npcs": [ /* NPC positions */ ],
  "chests": [ /* Treasure locations */ ]
}
```

**Map Files:**
- 22 interior maps (towns, castles, caves)
- Overworld map (special format, larger)

**Restrictions:**
- Maximum map size varies by location
- Tile IDs must reference valid CHR tiles
- Collision data stored separately
- NPC count limits per map

**How to Edit:**
1. Edit map JSON files
2. Use map editor tool *(when implemented)*
3. Or edit map data directly in `Bank00.asm`
4. Rebuild ROM

### Attack Calculations and Game Mechanics

**Location:** `source_files/Bank00.asm` and `Bank03.asm`

**Key Routines:**

**Damage Calculation** - `Bank03.asm` around line 3000+

```assembly
; Player attack damage
; Damage = (Attack / 2) - (EnemyDef / 4) + Random(0-3)
CalcPlayerDamage:
	LDA PlayerAttack
	LSR A               ; Divide by 2
	; ... more calculation code
```

**Enemy AI** - `Bank03.asm` enemy behavior routines

**Battle System** - `Bank00.asm` and `Bank03.asm` battle management

**Spell Effects** - `Bank03.asm` spell calculation routines

**Experience/Leveling** - `Bank03.asm` level-up calculations

**How to Edit:**
1. Find specific routine in assembly source
2. Modify calculation formulas
3. Be careful with stack operations and register usage
4. Rebuild and test extensively
5. **Advanced:** Use emulator debugger to trace execution

### Spells

**Location:** `extracted_assets/data/spells.json`

**Also in Assembly:** `source_files/Bank01.asm` at MP cost table (offset 0x7CFD)

**Format:**

```json
{
  "0": {
    "id": 0,
    "name": "HEAL",
    "mp_cost": 4,
    "effect": "Restore HP",
    "formula": "10-17 HP restored"
  }
}
```

**How to Edit:**
1. Edit `spells.json` and use `tools/reinsert_assets.py`
2. Or edit MP costs in `Bank01.asm`
3. Spell effects coded in `Bank03.asm`

### Equipment (Weapons, Armor, Shields)

**Location:** `extracted_assets/data/items_equipment.json`

**Also in Assembly:** `source_files/Bank01.asm` stat tables

**Stats Tables (Bank01):**
- Weapons: Offset 0x7CF5 (7 weapons)
- Armor: Offset 0x7D05 (7 armor pieces)
- Shields: Offset 0x7D0D (3 shields)

**How to Edit:**
1. Edit `items_equipment.json`
2. Or edit stat values directly in `Bank01.asm`
3. Rebuild ROM

### Graphics Restrictions Summary

**NES PPU Limitations:**
- 4 background palettes (4 colors each)
- 4 sprite palettes (4 colors each)
- Maximum 64 sprites on screen (8 per scanline)
- 8×8 pixel tiles only
- 2-bit color depth (4 colors per palette)
- 256×240 resolution

**CHR-ROM:**
- Total 1024 tiles (512 background + 512 sprites)
- Each tile = 16 bytes
- Cannot exceed 16KB total CHR data

---

## ROM Structure

### File Layout

```
Offset       Size    Description
-----------  ------  ------------------------------------
0x00000      16 B    iNES Header
0x00010      16 KB   PRG Bank 00 (0x8000-0xBFFF)
0x04010      16 KB   PRG Bank 01 (0x8000-0xBFFF)
0x08010      16 KB   PRG Bank 02 (0x8000-0xBFFF)
0x0C010      16 KB   PRG Bank 03 (0xC000-0xFFFF)
0x10010      16 KB   CHR-ROM (Pattern Tables)
```

Total ROM size: **81,936 bytes** (80 KB)

### iNES Header

```
Offset  Value   Description
------  -----   -----------
0x00    'N'     Signature byte 1
0x01    'E'     Signature byte 2
0x02    'S'     Signature byte 3
0x03    0x1A    Signature byte 4
0x04    0x04    PRG ROM size (4 × 16KB = 64KB)
0x05    0x04    CHR ROM size (4 × 4KB = 16KB)
0x06    0x12    Mapper 1 (MMC1), Vertical mirroring
0x07    0x00    Mapper upper bits
0x08-0x0F       Padding (zeros)
```

### PRG Banks

- **Bank 00** (0x8000-0xBFFF) - Game engine, battle system
- **Bank 01** (0x8000-0xBFFF) - Data tables, graphics pointers
- **Bank 02** (0x8000-0xBFFF) - Text, dialog, menus
- **Bank 03** (0xC000-0xFFFF) - Main game loop, events (fixed bank)

Bank 03 is always mapped to 0xC000-0xFFFF. Banks 00-02 are swappable and map to 0x8000-0xBFFF.

### CHR-ROM

16KB of graphics data (pattern tables) containing 1024 tiles:

- **Bank 0-1** (0x0000-0x1FFF) - Background tiles
- **Bank 2-3** (0x2000-0x3FFF) - Sprite tiles

Each 8×8 tile uses 16 bytes (2 bitplanes).

---

## Memory Map

### CPU Memory Map

```
0x0000-0x00FF   Zero Page (fast access RAM)
0x0100-0x01FF   Stack
0x0200-0x07FF   RAM (1.5KB)
0x6000-0x7FFF   Battery-backed SRAM (8KB)
0x8000-0xBFFF   Switchable PRG ROM (Bank 00/01/02)
0xC000-0xFFFF   Fixed PRG ROM (Bank 03)
```

### Key RAM Addresses

```assembly
; Player Stats (Zero Page)
CharXPos         = $3A   ; Player X position
CharYPos         = $3B   ; Player Y position
CharDirection    = $3C   ; 0=Down, 1=Left, 2=Up, 3=Right
PlayerHP         = $C5   ; Current HP
PlayerMaxHP      = $C6   ; Maximum HP
PlayerMP         = $C7   ; Current MP
PlayerMaxMP      = $C8   ; Maximum MP
PlayerGold       = $BC-$BE  ; Gold (3 bytes, BCD)
PlayerLevel      = $BA   ; Character level

; Equipment
EqippedItems     = $BF   ; Bitflags for equipped items

; Map & Location
MapNumber        = $45   ; Current map ID
InBattle         = $52   ; 0=overworld, 1=battle

; Enemy Stats
EnBaseHP         = $EC   ; Enemy current HP
EnMaxHP          = $ED   ; Enemy maximum HP
```

---

## Data Formats

### Monster Stats

Location: **Bank01:0x9E4B** (file offset **0x5E5B**)

Format: 16 bytes per monster

```
Offset  Size  Description
------  ----  ---------------------------
0x00    1     Attack power
0x01    1     Defense
0x02    1     Hit points
0x03    1     Spell flags
0x04    1     Agility
0x05    1     Magic defense
0x06    1     Experience reward
0x07    1     Gold reward
0x08-0x0F     Unused (padding)
```

39 monsters total (indices 0x00-0x26).

### Monster Sprites

Location: **Bank01:0x99E4** (file offset **0x59F4**)

Pointer table (2 bytes per monster) to sprite data. Each sprite is a list of 3-byte entries:

```
Byte 0: Tile index
Byte 1: Attributes (VHYYYYYY)
        V = Vertical flip
        H = Horizontal flip
        Y = Y offset
Byte 2: X position and palette (XXXXXXPP)
        X = X position
        P = Palette (0-3)
```

Sprite list ends with 0x00 byte.

### Items

Location: **Bank01** (various tables)

Item names, prices, and effects are stored in separate tables. See `source_files/Bank01.asm` for exact offsets.

### CHR Tiles

Each tile is 16 bytes:

```
Bytes 0-7:   Bitplane 0 (low bit of color)
Bytes 8-15:  Bitplane 1 (high bit of color)
```

For each pixel (8 pixels per row, 8 rows):
```
Pixel Color = (Bitplane0 & 1) | ((Bitplane1 & 1) << 1)
Result: 0, 1, 2, or 3 (palette index)
```

---

## Build System

### Quick Start

```powershell
# Basic build
.\build_rom.ps1

# Enhanced build with report
.\build_enhanced.ps1 -Report

# Clean build
.\build_enhanced.ps1 -Clean -Report
```

### Build Process

1. **Assemble Header** - Create iNES header from `Header.asm`
2. **Assemble Banks** - Compile each bank (`Bank00.asm` through `Bank03.asm`)
3. **Extract CHR** - Copy CHR-ROM from reference ROM
4. **Concatenate** - Combine all components into final ROM
5. **Verify** - Compare against reference ROM byte-by-byte

### Build Output

```
build/
├── dragon_warrior_rebuilt.nes    # Final ROM
├── header.bin                     # iNES header
├── bank00.bin                     # PRG Bank 00
├── bank01.bin                     # PRG Bank 01
├── bank02.bin                     # PRG Bank 02
├── bank03.bin                     # PRG Bank 03
├── chr_rom.bin                    # CHR-ROM
└── reports/
    ├── build_report_*.txt         # Build summary
    └── comparison_*.txt           # Byte differences
```

### Verification

The enhanced build script performs:

- **Size checks** - Verify each component is correct size
- **Byte comparison** - Compare against reference ROM
- **Difference reporting** - Log all mismatches with offsets
- **Version detection** - Auto-detect PRG0 vs PRG1

A **perfect build** has 0 byte differences.

---

## Modification Workflow

### Basic Workflow

1. **Extract Assets** - Use extraction tools to get JSON/PNG data
2. **Modify Data** - Edit JSON files or assembly source
3. **Rebuild ROM** - Run build script
4. **Test** - Load in emulator and verify changes
5. **Iterate** - Refine and rebuild as needed

### Example: Modifying Monster Stats

#### Step 1: Extract Monster Data

```powershell
python tools/extraction/data_extractor.py extract-monsters
```

Output: `extracted_assets/json/monsters.json`

#### Step 2: Edit Monster Stats

Edit `monsters.json`:

```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 3,           // Change to 999
    "strength": 5,      // Change to 100
    "agility": 15,
    "experience": 1,
    "gold": 2
  }
}
```

#### Step 3: Update Assembly Source

Modify `source_files/Bank01.asm` around line 4439:

```assembly
;Enemy $00-Slime.
;             Att  Def   HP  Spel Agi  Mdef Exp  Gld
L9E4B:  .byte $64, $03, $E7, $00, $0F, $01, $01, $02
              ; ^100      ^999 (0xE7 = 231 decimal)
```

**Note:** HP is capped at 255 (0xFF) in single byte.

#### Step 4: Rebuild

```powershell
.\build_enhanced.ps1 -Report
```

#### Step 5: Test

Load `build/dragon_warrior_rebuilt.nes` in emulator and battle a Slime.

---

## Asset Extraction

### Extract All Assets

```powershell
# Extract graphics
python tools/extraction/comprehensive_graphics_extractor.py

# Extract game data
python tools/extraction/data_extractor.py

# Extract CHR tiles
python tools/extract_chr_tiles.py

# Generate visual catalog
python tools/generate_asset_catalog.py
```

### Extracted Assets

```
extracted_assets/
├── chr_tiles/             # All 1024 CHR tiles as PNG
├── graphics/              # Sprite PNGs
├── graphics_comprehensive/
│   └── monsters/          # Monster sprite data + metadata
├── json/
│   ├── monsters.json      # Monster stats
│   ├── items.json         # Item data
│   ├── spells.json        # Spell data
│   ├── palettes.json      # Color palettes
│   └── dialogs.json       # NPC text
└── data/
    └── item_database.json # Complete item info
```

### Visual Catalog

Open `docs/asset_catalog/index.html` for browsable HTML documentation of all extracted assets with images and data tables.

---

## Asset Modification

### Graphics

#### CHR Tile Editing

1. Extract tiles: `python tools/extract_chr_tiles.py`
2. Edit PNGs in `extracted_assets/chr_tiles/`
3. Use tool to reinsert (TBD) or manually edit CHR-ROM

#### Sprite Composition

Monster sprites are composed of multiple CHR tiles. Edit sprite data in `Bank01.asm` around line 4048:

```assembly
SlimeSprts:
L9B0E:  .byte $55, $32, $64     ; Tile, Attr, X/Pal
        .byte $53, $2B, $60
        .byte $54, $33, $60
        ; ... more tiles
        .byte $00               ; End marker
```

### Data Tables

#### Monster Stats

Direct assembly edit in `Bank01.asm`:

```assembly
;Enemy $00-Slime.
;             Att  Def   HP  Spel Agi  Mdef Exp  Gld
L9E4B:  .byte $05, $03, $03, $00, $0F, $01, $01, $02
```

#### Items

Item stats scattered across multiple tables in `Bank01.asm`. Search for item names or use extraction tool to locate.

### Text

Dragon Warrior uses custom text compression. Text strings are in `Bank02.asm` but encoded. See "Advanced Topics" for text encoding details.

---

## Testing & Verification

### Emulator Testing

Recommended emulators:

- **Mesen** - Cycle-accurate, best debugging
- **FCEUX** - Good debugger, cheat support
- **Nestopia** - High compatibility

### Debugging

Use Mesen's debugger to:

- Set breakpoints
- View RAM/ROM
- Trace code execution
- Monitor memory writes

### Automated Verification

```powershell
# Verify extracted data accuracy
python tools/verify_extractions.py

# Compare two ROMs
python tools/rom_compare.py rom1.nes rom2.nes
```

### Test Cases

When modifying, test:

- **Battle system** - Fight modified monsters
- **Item shops** - Buy/sell modified items
- **Equipment** - Equip weapons/armor, check stats
- **Spells** - Cast spells, verify MP cost/effects
- **Maps** - Walk around, check collisions
- **Saving** - Save game, reset, verify save integrity

---

## Advanced Topics

### Text Compression

Dragon Warrior uses dictionary-based compression for dialog text. Common words/phrases are stored once and referenced by index.

**Compression Format:**
- Values 0x00-0x5F: ASCII characters (offset by 0x20)
- Values 0x60-0xFF: Dictionary references

See `Bank02.asm` for dictionary tables.

### Bank Switching

Dragon Warrior uses MMC1 mapper for bank switching:

```assembly
; Switch to Bank 1
LDA #$01
JSR SetPRGBankAndSwitch
```

Bank switch code in `Bank03.asm` around 0xFF91.

### Sprite DMA

Sprites use DMA transfer to OAM:

```assembly
LDA #$02          ; Source page (0x0200)
STA $4014         ; OAMDMA register
```

Sprite data at RAM 0x0200-0x02FF (256 bytes, 64 sprites).

### CHR Bank Switching

CHR banks can be switched for different tilesets:

```assembly
; Switch CHR banks (MMC1)
; Write to $E000-$FFFF control registers
```

See MMC1 mapper documentation for details.

### Battle System

Battle loop in `Bank00.asm`. Key functions:

- `InitBattle` - Start battle sequence
- `BattleLoop` - Main battle state machine
- `CalcDamage` - Damage calculation
- `BattleVictory` - Award EXP/Gold

### Encounter System

Random encounters triggered by step counter. Encounter zones defined in map data.

---

## Quick Reference

### Important Files

| File | Description |
|------|-------------|
| `source_files/Dragon_Warrior_Defines.asm` | All constant definitions |
| `source_files/Bank01.asm` | Data tables (monsters, items, etc.) |
| `source_files/Bank02.asm` | Text and dialog |
| `source_files/Bank03.asm` | Main game loop |
| `build_enhanced.ps1` | Enhanced build script |
| `tools/verify_extractions.py` | Verification tool |

### Useful Constants

```assembly
; Directions
DIR_DOWN  = $00
DIR_LEFT  = $01
DIR_UP    = $02
DIR_RIGHT = $03

; Item equip flags
AR_WEAPON = $01
AR_ARMOR  = $02
AR_SHIELD = $04

; Map IDs
MAP_OVERWORLD   = $00
MAP_TANTEGEL    = $01
MAP_CHARLOCK_1F = $0E
```

See `Dragon_Warrior_Defines.asm` for complete list.

### Build Quick Reference

```powershell
# Standard build
.\build_rom.ps1

# Enhanced with report
.\build_enhanced.ps1 -Report

# Clean build
.\build_enhanced.ps1 -Clean

# Extract assets
python tools/extract_chr_tiles.py

# Verify extraction
python tools/verify_extractions.py

# Generate catalog
python tools/generate_asset_catalog.py
```

---

## Appendix

### Monster IDs

```
0x00 - Slime           0x0D - Metal Scorpion   0x1A - Knight
0x01 - Red Slime       0x0E - Wolf             0x1B - Magiwyvern
0x02 - Drakee          0x0F - Wraith           0x1C - Demon Knight
0x03 - Ghost           0x10 - Metal Slime      0x1D - Werewolf
0x04 - Magician        0x11 - Specter          0x1E - Green Dragon
0x05 - Magidrakee      0x12 - Wolflord         0x1F - Starwyvern
0x06 - Scorpion        0x13 - Druinlord        0x20 - Wizard
0x07 - Druin           0x14 - Drollmagi        0x21 - Axe Knight
0x08 - Poltergeist     0x15 - Wyvern           0x22 - Blue Dragon
0x09 - Droll           0x16 - Rouge Scorpion   0x23 - Stoneman
0x0A - Drakeema        0x17 - Wraith Knight    0x24 - Armored Knight
0x0B - Skeleton        0x18 - Golem            0x25 - Red Dragon
0x0C - Warlock         0x19 - Goldman          0x26 - Dragonlord (form 1)
                                                0x27 - Dragonlord (form 2)
```

### Resources

- **Datacrystal Wiki** - https://datacrystal.tcrf.net/Dragon_Warrior_(NES)
- **6502 Reference** - http://www.6502.org/
- **NES Dev Wiki** - https://www.nesdev.org/
- **MMC1 Mapper** - https://www.nesdev.org/wiki/MMC1

---

## Credits

- **Original Game** - Chunsoft, Enix (1989)
- **Disassembly** - Community effort
- **Tools & Scripts** - This project
- **Documentation** - This guide

---

**Happy ROM Hacking! 🐉**
