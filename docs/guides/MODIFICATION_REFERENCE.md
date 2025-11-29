# Dragon Warrior Modification Reference

**Complete quick-lookup guide: "I want to change X" → "Edit file Y at location Z"**

---

## Table of Contents

1. [Monster Modifications](#monster-modifications)
2. [Player Character](#player-character)
3. [Items & Equipment](#items--equipment)
4. [Spells & Magic](#spells--magic)
5. [Shops & Economy](#shops--economy)
6. [Battle System](#battle-system)
7. [Maps & World](#maps--world)
8. [Graphics & Visuals](#graphics--visuals)
9. [Text & Dialog](#text--dialog)
10. [Music & Sound](#music--sound)
11. [Game Mechanics](#game-mechanics)
12. [Technical Limits](#technical-limits)

---

## Monster Modifications

### Monster Stats (HP, Attack, Defense, etc.)

**📁 File:** `extracted_assets/data/monsters.json`  
**🔧 Tool:** `tools/reinsert_assets.py`  
**📖 Alt:** `source_files/Bank01.asm` at offset `0x5E5B` (search for `EnStatTbl`)

**Fields:**

```json
{
  "id": 0,
  "name": "Slime",
  "hp": 3,              // Hit points (0-255)
  "strength": 5,        // Base attack (0-255)
  "agility": 15,        // Speed/evasion (0-255)
  "attack_power": 5,    // Actual attack stat (0-255)
  "defense": 3,         // Physical defense (0-255)
  "magic_defense": 1,   // Magic resistance (0-255)
  "experience_reward": 1,  // EXP given (0-255)
  "gold_reward": 2,     // Gold given (0-255)
  "spell": 0            // Spell bitflags (see below)
}
```

**Spell Flags (bitwise):**

- `0x00` = No spell
- `0x01` = HURT
- `0x02` = SLEEP
- `0x04` = STOPSPELL
- `0x08` = HEALMORE (used by Dragonlord)
- `0x10` = HURTMORE

**Limits:**

- 39 monsters total (ID 0-38)
- All stats: 0-255
- Changing count requires assembly modification

**Example - Buff Slime:**

```json
{
  "0": {
    "hp": 100,
    "attack_power": 50,
    "experience_reward": 500
  }
}
```

### Monster Graphics

**📁 File:** `extracted_assets/chr_organized/sprites_monsters_*.png`  
**🔧 Tool:** Graphics editor (GIMP, Aseprite, etc.) + *future CHR reinserter*  
**📖 Format:** 8×8 pixel tiles, 4-color NES palette

**Files:**

- `sprites_monsters_01_slimes.png` - Slimes (red, blue)
- `sprites_monsters_02_dragons.png` - Dragons (various colors)
- `sprites_monsters_03_undead.png` - Ghosts, skeletons, wraiths
- `sprites_monsters_04_humanoid.png` - Knights, wizards, golems
- `sprites_monsters_05_special.png` - Metal slime, Dragonlord

**Restrictions:**

- 8×8 pixel tiles only
- 4 colors per sprite (3 + transparency)
- Must use NES color palette
- Each monster uses 4-16 tiles

**Process:**

1. Edit PNG in graphics editor
2. Maintain 8×8 tile grid
3. Use only palette colors
4. *Future:* Run CHR reinsertion tool
5. Rebuild ROM

### Monster Names

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** Look for monster name tables  
**📖 Format:** Text encoding (see Text section)

**Current Status:** Names are hardcoded in text blocks. Changing requires finding text references.

### Monster Sprites (Which tiles used)

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** `Monster sprite table` or offset `0x59F4`  
**📖 Format:** Pointer table + sprite data

**Sprite Data Format:**

```assembly
; Each sprite entry: 3 bytes
.byte tile_id, attributes, x_pos_and_palette
```

**Attributes byte:**

- Bit 7: Vertical flip
- Bit 6: Horizontal flip
- Bits 5-0: Y offset

---

## Player Character

### Starting Stats

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `NewGameInit` or initial character setup  
**📖 Values:** Level, HP, MP, STR, AGI, etc.

**Example:**

```assembly
; Starting stats
LDA #$01    ; Level 1
STA PlayerLevel
LDA #$0F    ; 15 HP
STA PlayerHP
STA PlayerMaxHP
LDA #$00    ; 0 MP
STA PlayerMP
```

### Level-Up Stats

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `LevelUpStatGain` or level-up tables  
**📖 Format:** Tables showing HP/MP/STR/AGI gained per level

**Example - Find stat gain tables:**

```assembly
; HP gained per level
HPGainTable:
    .byte $04, $06, $05, $07, $06, $08...
```

### Experience Required per Level

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `ExpTable` or `RequiredExpForLevel`  
**📖 Format:** 16-bit values, experience needed for each level

**Formula (if hardcoded):**

Typically: `EXP = BASE * (Level ^ 2)` or similar polynomial

### Maximum Level

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** Level cap check or `MaxLevel`  
**📖 Default:** Level 30

**Change:** Requires modifying level check and extending stat tables

### Starting Position

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `NewGame` initialization  
**📖 Values:** Map ID, X position, Y position

```assembly
LDA #$01    ; Map 1 (Tantegel throne room)
STA MapNumber
LDA #$0F    ; X position
STA CharXPos
LDA #$0F    ; Y position
STA CharYPos
```

---

## Items & Equipment

### Item Stats (Attack, Defense)

**📁 File:** `extracted_assets/data/items_equipment.json`  
**🔧 Tool:** `tools/reinsert_assets.py`  
**📖 Alt:** `source_files/Bank01.asm` - multiple tables

**Weapon Attack Table:**

```assembly
; Bank01.asm - search WpnAtkTbl
WpnAtkTbl:
    .byte $02  ; Bamboo Pole
    .byte $04  ; Club
    .byte $0A  ; Copper Sword
    .byte $0F  ; Hand Axe
    .byte $14  ; Broad Sword
    .byte $23  ; Flame Sword
    .byte $28  ; Erdrick's Sword
```

**Armor Defense Table:**

```assembly
; Bank01.asm - search ArmrDefTbl
ArmrDefTbl:
    .byte $02  ; Clothes
    .byte $04  ; Leather Armor
    .byte $0A  ; Chain Mail
    .byte $10  ; Half Plate
    .byte $18  ; Full Plate
    .byte $1C  ; Magic Armor
    .byte $1C  ; Erdrick's Armor
```

**Shield Defense Table:**

```assembly
ShldDefTbl:
    .byte $04  ; Small Shield
    .byte $0A  ; Large Shield
    .byte $19  ; Silver Shield
```

### Item Prices (Shops)

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** Shop inventory tables or `ShopData`  
**📖 Format:** 16-bit prices per item

**Shop Tables (example):**

```assembly
; Brecconary Shop
Shop1Data:
    .byte ITEM_CLUB, $60, $00          ; Club: 96 gold
    .byte ITEM_BAMBOO_POLE, $0A, $00   ; Bamboo: 10 gold
    .byte ITEM_CLOTHES, $14, $00       ; Clothes: 20 gold
    .byte $FF  ; End marker
```

### Tool Effects

**📁 File:** `source_files/Bank01.asm` and `Bank03.asm`  
**🔍 Search:** `ToolEffects` or specific item names  
**📖 Location:** Different items have code in different places

**Examples:**

- **Torch:** Lights radius (Bank03)
- **Herb:** Heals ~20-30 HP (Bank03)
- **Dragon's Scale:** Reduces encounter rate (Bank03)
- **Fairy Water:** Prevents encounters (Bank03)
- **Wings:** Return to throne room (Bank03)

**Herb Healing Amount:**

```assembly
; Bank03.asm - search Herb or UseItem
LDA #$14    ; Heal 20 HP
CLC
ADC PlayerHP
; ... clamp to max HP
```

### Item Names

**📁 File:** `source_files/Bank02.asm`  
**🔍 Search:** Item name table  
**📖 Format:** Compressed text strings

---

## Spells & Magic

### Spell MP Costs

**📁 File:** `extracted_assets/data/spells.json`  
**🔧 Tool:** `tools/reinsert_assets.py`  
**📖 Alt:** `source_files/Bank01.asm` at offset `0x7CFD`

```assembly
; MP costs for each spell
SpellMPCosts:
    .byte $04  ; HEAL
    .byte $02  ; HURT
    .byte $02  ; SLEEP
    .byte $02  ; RADIANT
    .byte $02  ; STOPSPELL
    .byte $04  ; OUTSIDE
    .byte $06  ; RETURN
    .byte $08  ; REPEL
    .byte $0A  ; HEALMORE
    .byte $05  ; HURTMORE
```

### Spell Effects

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** Spell name or `SpellEffect`  
**📖 Format:** Assembly code for each spell

**Example - HEAL spell:**

```assembly
; HEAL spell effect
SpellHEAL:
    ; Random healing: 10-17 HP
    JSR Random
    AND #$07    ; 0-7
    CLC
    ADC #$0A    ; +10 = 10-17
    ; Add to current HP...
```

**Example - HURT spell:**

```assembly
; HURT damage formula
SpellHURT:
    ; Damage = (Player Level / 2) + Random(0-3)
    LDA PlayerLevel
    LSR A       ; Divide by 2
    ; ... add random
```

### Spell Learning Levels

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `SpellLearn` or level-up spell grants  
**📖 Format:** Table of levels when spells are learned

```assembly
; Spells learned at each level
LevelSpellTable:
    .byte SPELL_HEAL      ; Level 3
    .byte SPELL_HURT      ; Level 4
    .byte SPELL_SLEEP     ; Level 7
    ; etc.
```

### Spell Names

**📁 File:** `source_files/Bank02.asm`  
**🔍 Search:** Spell name table  
**📖 Format:** Text strings (8 characters max)

---

## Shops & Economy

### Shop Inventories

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** `ShopData` or specific town names  
**📖 Format:** Tables with item IDs and prices

**Structure:**

```assembly
BrecconaryWeaponShop:
    .byte ITEM_ID, PRICE_LO, PRICE_HI
    .byte ITEM_ID, PRICE_LO, PRICE_HI
    .byte $FF  ; End marker
```

### Shop Prices

Same as shop inventories - prices are embedded in shop tables.

### Inn Costs

**📁 File:** `source_files/Bank01.asm` or `Bank03.asm`  
**🔍 Search:** `InnCost` or inn dialog  
**📖 Format:** Constant values

**Example:**

```assembly
; Inn prices by town
BrecconaryInnCost:
    .word $0006  ; 6 gold

RimuldarInnCost:
    .word $0014  ; 20 gold
```

### Selling Price Modifier

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `SellItem` or sell price calculation  
**📖 Default:** Items sell for 1/2 purchase price

```assembly
; Selling price = Buy price / 2
LDA ItemPrice
LSR A       ; Divide by 2
STA SellPrice
```

---

## Battle System

### Damage Formula (Player Attack)

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `CalcPlayerDamage` or `PlayerAttack`  
**📖 Formula:** `Damage = (ATK / 2) - (EnemyDef / 4) + Random(0-3)`

```assembly
CalcPlayerDamage:
    LDA PlayerAttack
    LSR A           ; ATK / 2
    STA TempDamage
    
    LDA EnemyDefense
    LSR A
    LSR A           ; DEF / 4
    
    ; Subtract from damage
    ; Add random 0-3
    ; Clamp to 0 minimum
```

### Damage Formula (Enemy Attack)

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `CalcEnemyDamage` or `EnemyAttack`  
**📖 Formula:** Similar to player damage

### Critical Hit Chance

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `CriticalHit` or damage calculation  
**📖 Default:** Random chance, typically ~1/32

### Hit/Miss Calculation

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `HitCheck` or accuracy  
**📖 Formula:** Based on agility difference

### Enemy AI

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `EnemyAI` or `EnemyTurn`  
**📖 Logic:** Decision tree for attack vs. spell

**Typical AI:**

```assembly
EnemyAI:
    ; Roll random
    ; If enemy has spell AND random < threshold
    ;   Cast spell
    ; Else
    ;   Physical attack
```

### Run Success Rate

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `RunAway` or flee calculation  
**📖 Formula:** Based on agility, level difference

### Experience Calculation

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `GiveExperience` or battle rewards  
**📖 Logic:** Direct value from monster stats

### Gold Reward

Same as experience - uses monster's gold_reward stat.

---

## Maps & World

### Map Layouts

**📁 File:** `extracted_assets/maps/*.json`  
**🔧 Tool:** *Future map editor*  
**📖 Alt:** `source_files/Bank00.asm` - map data tables

**Structure:**

```json
{
  "id": 1,
  "name": "Tantegel Castle",
  "width": 30,
  "height": 30,
  "tiles": [ /* 2D array */ ],
  "warps": [ /* Warp points */ ],
  "npcs": [ /* NPC positions */ ],
  "chests": [ /* Treasure locations */ ]
}
```

### Tile Properties (Walkable, etc.)

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `TileProperties` or collision table  
**📖 Format:** Bitflags for each tile type

**Example:**

```assembly
; Tile flags
; Bit 0: Walkable
; Bit 1: Swamp (damage)
; Bit 2: Barrier (castle)
TileFlags:
    .byte %00000001  ; Grass - walkable
    .byte %00000000  ; Water - not walkable
    .byte %00000011  ; Swamp - walkable + damage
```

### NPC Positions

**📁 File:** `extracted_assets/maps/*.json` or `source_files/Bank00.asm`  
**🔍 Search:** NPC tables or specific map data  
**📖 Format:** X, Y, facing direction, dialog ID

### Warp Points (Doors, Stairs)

**📁 File:** `source_files/Bank00.asm`  
**🔍 Search:** `WarpTable` or door tables  
**📖 Format:** Source map, X, Y → Dest map, X, Y

```assembly
; Warp from Tantegel exterior to interior
.byte $00, $0F, $0F  ; Source: Map 0, pos (15,15)
.byte $01, $0F, $1D  ; Dest: Map 1, pos (15,29)
```

### Encounter Rates

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `EncounterRate` or random encounter  
**📖 Logic:** Step counter + random check

**Typical:**

```assembly
; Every N steps, check for encounter
INC StepCounter
LDA StepCounter
CMP #$08    ; Every 8 steps?
BCC NoCheck
; Random encounter check
```

### Encounter Tables (Which monsters appear where)

**📁 File:** `source_files/Bank01.asm` or `Bank03.asm`  
**🔍 Search:** `EncounterTable` or zone monsters  
**📖 Format:** Tables indexed by map or region

**Example:**

```assembly
; Zone 1 encounters (near Tantegel)
Zone1Monsters:
    .byte MONSTER_SLIME
    .byte MONSTER_RED_SLIME
    .byte MONSTER_DRAKEE
    .byte $FF  ; End
```

---

## Graphics & Visuals

### CHR-ROM (All Tiles)

**📁 File:** ROM offset `0x10010` (after 64KB PRG-ROM)  
**🔧 Tool:** Tile editor or hex editor  
**📖 Format:** 1024 tiles, 16 bytes each (NES 2bpp)

**Extract:**

```powershell
python tools/extract_chr_tiles.py
```

**Files:** `extracted_assets/chr_organized/*.png`

### Sprite Tiles

**📁 Files:**

- `sprites_hero_*.png` - Hero sprites (4 directions, walking)
- `sprites_monsters_*.png` - All monster sprites
- `sprites_npcs_*.png` - Town NPCs, guards, merchants

### Background Tiles

**📁 Files:**

- `terrain_overworld.png` - Grass, water, mountains, trees
- `terrain_dungeons.png` - Cave floors, walls
- `town_tiles.png` - Buildings, roads, doors

### Palettes

**📁 File:** `source_files/Bank01.asm` and `Bank03.asm`  
**🔍 Search:** `PaletteData` or `PPU_Palette`  
**📖 Format:** 4 palettes × 4 colors each

**Example:**

```assembly
; Background palette 0
.byte $0F, $00, $10, $30  ; Black, white, light gray, white

; Sprite palette 0  
.byte $0F, $16, $27, $37  ; Black, red, orange, yellow
```

**NES Color Palette:** 64 colors total (0x00-0x3F)

### Title Screen

**📁 File:** `source_files/Bank02.asm` or `Bank03.asm`  
**🔍 Search:** `TitleScreen` or intro  
**📖 Content:** Tile layout, palette, logo graphics

### Fonts

**📁 File:** CHR-ROM tiles 0x00-0x5F  
**🔧 Tool:** Tile editor  
**📖 Format:** Standard NES font tiles

---

## Text & Dialog

### Dialog Text

**📁 File:** `source_files/Bank02.asm`  
**🔍 Search:** `TextBlock1` through `TextBlock19`  
**📖 Format:** Custom encoded text with control codes

**Example:**

```assembly
TextBlock1Entry0:
    .text "Welcome to my castle,", LINE
    .text HERO, ".", WAIT
    .text "I am Lorik, King of Tantegel.", END
```

### Text Encoding

**📁 File:** `extracted_assets/text/text_encoding.json`  
**📖 Format:**

- `0x00-0x5F`: ASCII characters (offset by 0x20)
- `0x60-0x7F`: Extended characters
- `0x80-0x8F`: Word compression ("the", "thou", "thy")
- `0xF0-0xFF`: Control codes (HERO, WAIT, LINE, PAGE, etc.)

**Control Codes:**

- `HERO` (0xF0): Insert player name
- `WAIT` (0xF1): Wait for button press
- `LINE` (0xF2): New line
- `PAGE` (0xF3): New page (clear text box)
- `END` (0xFF): End of text

### Compressed Words

**📁 File:** `source_files/Bank02.asm`  
**🔍 Search:** `CompressedWordTable`  
**📖 Words:** "the", "thou", "thy", "art", "of", "to", etc.

**Usage:** Saves ROM space by encoding common words as single bytes

### Item/Spell/Monster Names

**📁 File:** `source_files/Bank02.asm`  
**🔍 Search:** Name tables  
**📖 Format:** Text strings, often fixed-width

---

## Music & Sound

### Music Tracks

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** `MusicData` or track names  
**📖 Format:** Note data, tempo, instrument selection

**Tracks:**

- Overworld theme
- Town theme  
- Dungeon theme
- Battle theme
- Castle theme
- Death theme
- Victory theme
- Ending theme

### Sound Effects

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** `SFX` or sound effect routines  
**📖 Format:** APU register writes

**Effects:**

- Menu cursor
- Text scrolling
- Door opening
- Stairs
- Treasure chest
- Spell casting
- Hit/damage
- Level up

### Music Engine

**📁 File:** `source_files/Bank01.asm`  
**🔍 Search:** `MusicEngine` or `SoundEngine`  
**📖 System:** Custom music driver using NES APU

---

## Game Mechanics

### Level-Up Stat Gains

See [Player Character](#player-character) section.

### Stat Calculation (Equipped items)

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `RecalcStats` or equipment check  
**📖 Logic:** Base stats + weapon + armor + shield

```assembly
RecalcPlayerAttack:
    LDA BaseStrength
    CLC
    ADC WeaponAttack
    ; Add any bonuses
    STA PlayerAttack
```

### Death Penalty

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `PlayerDeath` or game over  
**📖 Default:** Lose half gold, return to throne room

```assembly
PlayerDeath:
    ; Gold / 2
    LDA PlayerGold
    LSR A
    STA PlayerGold
    ; Restore HP
    ; Return to castle
```

### Save Game Format

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `SaveGame` or SRAM writes  
**📖 Location:** Battery-backed SRAM (0x6000-0x7FFF)

**Data saved:**

- Player stats (level, HP, MP, STR, AGI, etc.)
- Inventory
- Gold
- Position (map, X, Y)
- Game flags (Erdrick's token, princess rescued, etc.)

### Game Flags (Quest progress)

**📁 File:** `source_files/Bank03.asm`  
**🔍 Search:** `GameFlags` or quest tracking  
**📖 Format:** Bitflags for events

**Example flags:**

- Bit 0: Has Erdrick's Token
- Bit 1: Princess rescued
- Bit 2: Rainbow Drop obtained
- Bit 3: Defeated Dragonlord

---

## Technical Limits

### ROM Size Limits

- **Total ROM:** 81,936 bytes (80 KB)
- **PRG-ROM:** 65,536 bytes (64 KB, 4 banks × 16 KB)
- **CHR-ROM:** 16,384 bytes (16 KB, 1024 tiles)

### Data Structure Limits

| Data Type | Maximum | Notes |
|-----------|---------|-------|
| Monsters | 39 | Hard limit (ID 0-38) |
| Spells | 10 | Hard limit |
| Items | ~32 | Varies by type |
| Maps | ~24 interior | Pointer table size |
| NPCs per map | ~16 | Memory constraint |
| Text blocks | 19 | Bank02 structure |
| Save slots | 3 | SRAM allocation |

### Memory Limits

- **Zero Page RAM:** 256 bytes (0x00-0xFF) - Critical fast access
- **Main RAM:** 2048 bytes (0x200-0x7FF)
- **SRAM:** 8192 bytes (0x6000-0x7FFF) - Battery-backed save

### Graphics Limits

- **Sprite limit:** 64 sprites total (8×8 each)
- **Scanline limit:** 8 sprites per scanline
- **Tiles:** 1024 total (512 BG + 512 sprite)
- **Palettes:** 8 total (4 BG + 4 sprite, 4 colors each)
- **Colors:** 64 in NES palette, 25 displayable at once

### Text Limits

- **Dialog box:** ~2 lines × 32 characters
- **Compressed words:** 16 words (0x80-0x8F)
- **Control codes:** 16 codes (0xF0-0xFF)
- **Text blocks:** 19 blocks in Bank02

---

## Modification Examples

### Example 1: Super Slime

Make Slime a late-game monster:

**File:** `extracted_assets/data/monsters.json`

```json
{
  "0": {
    "name": "Slime",
    "hp": 150,
    "attack_power": 80,
    "defense": 60,
    "magic_defense": 50,
    "agility": 90,
    "experience_reward": 255,
    "gold_reward": 255
  }
}
```

**Build:**

```powershell
python tools/reinsert_assets.py
# Test: output/dragon_warrior_modified.nes
```

### Example 2: Cheap Healing

Reduce HEAL spell cost to 1 MP:

**File:** `source_files/Bank01.asm`

```assembly
SpellMPCosts:
    .byte $01  ; HEAL (was $04)
    .byte $02  ; HURT
    ; ... rest unchanged
```

**Build:**

```powershell
.\build_rom.ps1
```

### Example 3: Overpowered Club

Make Club the best weapon:

**File:** `source_files/Bank01.asm`

```assembly
WpnAtkTbl:
    .byte $02  ; Bamboo Pole
    .byte $50  ; Club (was $04, now 80 ATK!)
    .byte $0A  ; Copper Sword
    ; ... rest unchanged
```

### Example 4: Free Inn

Make all inns free:

**File:** `source_files/Bank03.asm`

Find inn cost checks and force to 0:

```assembly
; Inn cost check
LDA #$00    ; Always free
STA InnCost
```

---

## Where to Learn More

- [ROM Hacking Guide](ROM_HACKING_GUIDE.md) - Complete in-depth guide
- [Tools Documentation](TOOLS_DOCUMENTATION.md) - All tools reference
- [ROM Map](../datacrystal/ROM_MAP.md) - Memory layout
- [Documentation Index](../INDEX.md) - All documentation

---

**Happy ROM hacking! 🐉**

*Use this as a quick reference while modding Dragon Warrior.*
