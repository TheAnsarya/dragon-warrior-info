# Dragon Warrior ROM Hacking Toolkit - Tools Documentation

Complete reference guide for all Dragon Warrior ROM hacking tools in the toolkit.

## Table of Contents

1. [Core Tools](#core-tools)
2. [Graphics & Art Tools](#graphics--art-tools)
3. [Text & Dialogue Tools](#text--dialogue-tools)
4. [Game Balance Tools](#game-balance-tools)
5. [Map & World Tools](#map--world-tools)
6. [Analysis & Debugging Tools](#analysis--debugging-tools)
7. [Advanced Tools](#advanced-tools)
8. [Tool Integration Workflows](#tool-integration-workflows)

---

## Core Tools

### ROM Metadata Analyzer (`rom_metadata_analyzer.py`)
**Purpose:** Comprehensive ROM analysis and validation

**Features:**
- NES header parsing (iNES/NES 2.0)
- Mapper detection and analysis
- Checksum calculation (MD5, SHA1, SHA256, CRC32)
- Bank structure analysis (PRG/CHR)
- ROM validation and verification
- Memory map generation (ASCII art)
- ROM comparison (diff two ROMs)

**Usage:**
```bash
# Analyze ROM
python tools/rom_metadata_analyzer.py rom.nes

# Generate detailed report
python tools/rom_metadata_analyzer.py rom.nes --detailed

# Compare two ROMs
python tools/rom_metadata_analyzer.py rom.nes --compare modified.nes

# Export to JSON
python tools/rom_metadata_analyzer.py rom.nes --export metadata.json
```

**Key Classes:**
- `NESHeader`: Header data structure
- `ROMChecksums`: Multi-algorithm checksum calculation
- `BankStructure`: PRG/CHR bank organization
- `ROMAnalyzer`: Main analysis engine
- `ReportGenerator`: Report formatting and export
- `ROMComparator`: ROM difference detection

---

### Binary Patch Tool (`binary_patch_tool.py`)
**Purpose:** Create and apply binary patches (IPS/BPS formats)

**Features:**
- IPS patch creation/application
- BPS patch creation/application with CRC validation
- RLE compression detection
- Patch inspection and metadata extraction
- Variable-length integer encoding (BPS)
- Truncation support
- Patch verification

**Usage:**
```bash
# Create IPS patch
python tools/binary_patch_tool.py original.nes modified.nes --create patch.ips

# Apply IPS patch
python tools/binary_patch_tool.py rom.nes patch.ips --apply

# Create BPS patch with validation
python tools/binary_patch_tool.py original.nes modified.nes --create patch.bps --format bps

# Inspect patch
python tools/binary_patch_tool.py patch.ips --inspect
```

**Patch Formats:**
- **IPS:** Simple offset-based format, 16MB limit
- **BPS:** Advanced format with CRC32 validation, unlimited size

---

### Disassembly Annotator (`disasm_annotator.py`)
**Purpose:** 6502 assembly label and annotation management

**Features:**
- Symbol database management
- Cross-reference tracking (jump/call/branch/read/write)
- Automatic subroutine detection
- Label conflict detection
- Multi-format export (FCEUX, Mesen, CA65, JSON)
- Code analysis and documentation

**Usage:**
```bash
# Analyze ROM and generate labels
python tools/disasm_annotator.py rom.nes --analyze

# Export to FCEUX format
python tools/disasm_annotator.py rom.nes --export labels.nl --format fceux

# Export to Mesen format
python tools/disasm_annotator.py rom.nes --export labels.mlb --format mesen

# Export to CA65 assembly
python tools/disasm_annotator.py rom.nes --export labels.inc --format ca65
```

**Symbol Types:**
- Code labels (subroutines, functions)
- Data labels (tables, strings)
- Jump targets
- Variable addresses

---

## Graphics & Art Tools

### Tileset Manager (`tileset_manager.py`)
**Purpose:** Comprehensive CHR-ROM tile management

**Features:**
- Pattern table extraction (4 tables, 256 tiles each)
- Duplicate tile detection
- Tile usage analysis
- Tileset optimization
- Pattern table export to PNG
- Tile atlas generation
- Compression ratio analysis

**Usage:**
```bash
# Extract all tiles
python tools/tileset_manager.py rom.nes --extract-all output/

# Find duplicate tiles
python tools/tileset_manager.py rom.nes --find-duplicates

# Export pattern table 0 (Font & UI)
python tools/tileset_manager.py rom.nes --export-pattern-table 0 --output font.png

# Analyze tile usage
python tools/tileset_manager.py rom.nes --analyze-usage

# Optimize tileset
python tools/tileset_manager.py rom.nes --optimize
```

**CHR-ROM Organization:**
- Pattern Table 0: Font & UI (256 tiles)
- Pattern Table 1: Hero sprites (256 tiles)
- Pattern Table 2: Monster sprites (256 tiles)
- Pattern Table 3: Map tiles & NPCs (256 tiles)

**Data Structures:**
- `Tile`: 8x8 CHR tile with pixels and metadata
- `PatternTable`: Collection of 256 tiles
- `TilesetStats`: Usage and compression statistics

---

### Sprite Editor Advanced (`sprite_editor_advanced.py`)
**Purpose:** Advanced sprite and graphics editing

**Features:**
- Monster sprite extraction (fixed bug!)
- Hero sprite editing
- OAM (Object Attribute Memory) editing
- Sprite animation sequences
- Palette management
- PNG export/import
- Sprite metadata editing

**Usage:**
```bash
# Extract all monster sprites
python tools/sprite_editor_advanced.py rom.nes --extract-monsters output/

# Extract specific monster
python tools/sprite_editor_advanced.py rom.nes --monster "Slime" --export slime.png

# Import sprite
python tools/sprite_editor_advanced.py rom.nes --import slime_modified.png --monster "Slime" -o new.nes
```

**Bug Fix (Commit bebe46d):**
- Fixed CHR-ROM offset: 0x20010 → 0x10010
- Fixed CHR-ROM size: 0x2000 → 0x4000
- Fixed monster tile indices (now reads actual tiles 85, 83, 84 instead of 0x00-0x0F)

---

## Text & Dialogue Tools

### Dialogue Editor (`dialogue_editor.py`)
**Purpose:** Text extraction, editing, and DTE compression

**Features:**
- Text extraction from all regions
- DTE (Dual Tile Encoding) compression/decompression
- String search and replace
- Text table editing
- Character frequency analysis
- Optimal DTE pair calculation
- Text overflow detection
- Control code handling

**Usage:**
```bash
# Extract all text
python tools/dialogue_editor.py rom.nes --extract-all text/

# Search for text
python tools/dialogue_editor.py rom.nes --search "Welcome"

# Replace text
python tools/dialogue_editor.py rom.nes --replace "Welcome" "Greetings" -o new.nes

# Analyze DTE compression
python tools/dialogue_editor.py rom.nes --analyze-dte

# Calculate optimal DTE pairs
python tools/dialogue_editor.py rom.nes --optimize-dte

# Show statistics
python tools/dialogue_editor.py rom.nes --stats
```

**Text Regions:**
- Dialogue: 0x36A0-0x5FFF
- Menu text: 0x2800-0x36A0
- Item names: 0x1AF0-0x1C3F
- Spell names: 0x1C40-0x1CFF
- Monster names: 0x1D00-0x1E7F

**DTE Pairs:**
Top compression pairs: "th", "er", "on", "an", "re", "he", "in", "ed", etc.

---

## Game Balance Tools

### Enemy AI & Battle Mechanics Editor (`enemy_ai_editor.py`)
**Purpose:** Enemy stats, AI, and battle system editing

**Features:**
- Enemy stat editing (HP, strength, agility, XP, gold)
- AI behavior pattern configuration
- Spell usage probability
- Attack pattern analysis
- Battle formula modification
- Damage calculation
- Reward balance analysis
- Enemy tier classification

**Usage:**
```bash
# List all enemies
python tools/enemy_ai_editor.py rom.nes --list

# Show enemy details
python tools/enemy_ai_editor.py rom.nes --enemy "Dragon"

# Edit enemy stats
python tools/enemy_ai_editor.py rom.nes --enemy "Slime" --hp 10 --strength 8 -o new.nes

# Analyze AI patterns
python tools/enemy_ai_editor.py rom.nes --analyze-ai

# Analyze reward balance
python tools/enemy_ai_editor.py rom.nes --analyze-balance

# Export database
python tools/enemy_ai_editor.py rom.nes --export enemies.json
```

**Enemy Data (39 Enemies):**
- Stats: HP, Strength, Agility, XP, Gold
- AI: Spell type, spell probability, attack pattern
- Groups: Encounter group composition

**Battle Formulas:**
- Damage = Random(0-255) × Strength ÷ Defense ÷ 2
- Hit Chance = 1 - (Enemy Agility ÷ (2 × Player Agility))
- Critical = 1/32 chance
- Run = (Player Agility - Enemy Agility) ÷ 4

---

### Item & Shop Editor (`item_shop_editor.py`)
**Purpose:** Item stats and shop inventory management

**Features:**
- Item stat editing (attack, defense, price)
- Shop inventory management
- Price balancing analysis
- Equipment effect editing
- Progression curve analysis
- Cost efficiency calculation
- Item comparison

**Usage:**
```bash
# List all items
python tools/item_shop_editor.py rom.nes --list-items

# List all shops
python tools/item_shop_editor.py rom.nes --list-shops

# Edit item stats
python tools/item_shop_editor.py rom.nes --item "Copper Sword" --attack 15 -o new.nes

# Analyze item balance
python tools/item_shop_editor.py rom.nes --analyze-balance

# Analyze progression curves
python tools/item_shop_editor.py rom.nes --analyze-progression

# Export database
python tools/item_shop_editor.py rom.nes --export items.json
```

**Item Categories:**
- Weapons (9): Bamboo Pole → Erdrick's Sword
- Armor (7): Clothes → Erdrick's Armor
- Shields (6): Leather Shield → Silver Shield
- Tools (15): Torch, Herbs, Keys, Wings, etc.

**Shop Locations:**
- Brecconary (3 shops), Garinham (2 shops), Kol, Rimuldar (2 shops), Cantlin (2 shops)

---

### Spell & Magic System Editor (`spell_editor.py`)
**Purpose:** Spell data and magic system editing

**Features:**
- Spell data editing (MP cost, power, effect)
- Spell learning levels
- Magic formula modification
- Damage/healing calculation
- MP cost balancing
- Spell progression curves
- Efficiency analysis

**Usage:**
```bash
# List all spells
python tools/spell_editor.py rom.nes --list

# Show spell details
python tools/spell_editor.py rom.nes --spell "Heal"

# Edit spell stats
python tools/spell_editor.py rom.nes --spell "Hurt" --mp-cost 1 --power 20 -o new.nes

# Analyze balance
python tools/spell_editor.py rom.nes --analyze-balance

# Analyze progression
python tools/spell_editor.py rom.nes --analyze-progression

# Export database
python tools/spell_editor.py rom.nes --export spells.json
```

**Player Spells (10):**
- Heal (Lv 3), Hurt (Lv 4), Sleep (Lv 7), Radiant (Lv 9)
- Stopspell (Lv 10), Outside (Lv 12), Return (Lv 13)
- Repel (Lv 15), Healmore (Lv 17), Hurtmore (Lv 19)

**Magic Formulas:**
- Heal: Random(10, 17)
- Healmore: Random(85, 100)
- Hurt: Random(8, 16)
- Hurtmore: Random(58, 65)

---

### Character Stats & Progression Editor (`character_editor.py`)
**Purpose:** Character development and leveling system

**Features:**
- Experience curve editing
- HP/MP growth curves
- Stat progression (Strength, Agility)
- Level-up formula modification
- XP curve rebalancing
- Difficulty scaling
- Progression analysis

**Usage:**
```bash
# Show all level stats
python tools/character_editor.py rom.nes --show-all

# Show specific level
python tools/character_editor.py rom.nes --level 10

# Edit level stats
python tools/character_editor.py rom.nes --level 5 --hp 40 --mp 12 -o new.nes

# Analyze progression
python tools/character_editor.py rom.nes --analyze

# Rebalance XP curve
python tools/character_editor.py rom.nes --rebalance-xp --difficulty easier -o new.nes

# Export stats
python tools/character_editor.py rom.nes --export stats.json
```

**Stat Growth (Level 1 → 30):**
- HP: 15 → 220 (~4-5 per level)
- MP: 0 → 210 (~3-4 per level after Lv 3)
- Strength: 4 → 130 (~3-4 per level)
- Agility: 4 → 140 (~4-5 per level)

**XP Milestones:**
- Level 2: 7 XP
- Level 10: 2,090 XP
- Level 20: 52,000 XP
- Level 30: 260,000 XP

---

## Map & World Tools

### World Map & Encounter Editor (`map_editor.py`)
**Purpose:** World map and encounter zone management

**Features:**
- World map tile editing (120x120)
- Encounter zone configuration
- Encounter rate editing
- Warp point management
- Treasure chest placement
- Map rendering to PNG
- Zone boundary detection
- Map statistics

**Usage:**
```bash
# Render world map
python tools/map_editor.py rom.nes --render-world output/world.png

# Show encounter zones
python tools/map_editor.py rom.nes --show-encounters

# List all warps
python tools/map_editor.py rom.nes --list-warps

# List treasure chests
python tools/map_editor.py rom.nes --list-chests

# Show map statistics
python tools/map_editor.py rom.nes --stats

# Export map data
python tools/map_editor.py rom.nes --export map_data.json
```

**Encounter Zones (9 zones):**
1. Tantegel Castle (Safe)
2. Tantegel Area (Lv 1-3)
3. Alefgard Plains (Lv 2-5)
4. Forest (Lv 3-7)
5. Hills (Lv 4-9)
6. Swamp (Lv 5-12)
7. Mountain (Lv 7-15)
8. Desert (Lv 10-18)
9. Dragonlord Castle (Lv 15-30)

---

## Analysis & Debugging Tools

### Game State Validator (`game_state_validator.py`)
**Purpose:** Save file validation and impossible state detection

**Features:**
- Save file consistency checking
- Experience vs level validation
- Stat progression validation
- Spell unlock verification
- Inventory validation
- Progression flag checking
- Gold limit validation
- Auto-fix suggestions
- Multiple validation levels (loose/normal/strict/paranoid)

**Usage:**
```bash
# Validate save file
python tools/game_state_validator.py savefile.sav

# Strict validation
python tools/game_state_validator.py savefile.sav --level strict

# Auto-repair
python tools/game_state_validator.py savefile.sav --repair -o fixed.sav

# Check 100% completion
python tools/game_state_validator.py savefile.sav --check-100percent

# Speedrun validation
python tools/game_state_validator.py savefile.sav --speedrun
```

**Validation Categories:**
- Level/XP consistency
- HP/MP vs level curves
- Stat progression
- Spell availability by level
- Equipment validity
- Progression flags (Princess, Rainbow Drop, etc.)
- Gold limits (max 65535)

---

### Music Editor Advanced (`music_editor_advanced.py`)
**Purpose:** NES music extraction and analysis

**Features:**
- Music track extraction
- NSF export (NES Sound Format)
- MIDI export
- Music pattern analysis
- Note distribution statistics
- APU channel analysis
- Envelope editing
- Period table management

**Usage:**
```bash
# Extract all music
python tools/music_editor_advanced.py rom.nes --extract-all output/

# Export to NSF
python tools/music_editor_advanced.py rom.nes --export-nsf music.nsf

# Export to MIDI
python tools/music_editor_advanced.py rom.nes --track overworld --export-midi overworld.mid

# Show track info
python tools/music_editor_advanced.py rom.nes --list

# Analyze track
python tools/music_editor_advanced.py rom.nes --track battle --info
```

**Music Tracks (9):**
- Overworld, Town, Castle, Dungeon
- Battle, Final Battle
- Victory, Death, Ending

**NES APU Channels:**
- PULSE1, PULSE2: Melody and harmony
- TRIANGLE: Bass
- NOISE: Percussion
- DMC: Samples

---

## Advanced Tools

### Integration Workflows

#### Complete ROM Hack Pipeline
```bash
# 1. Analyze original ROM
python tools/rom_metadata_analyzer.py original.nes --detailed

# 2. Extract all assets
python tools/tileset_manager.py original.nes --extract-all assets/tiles/
python tools/dialogue_editor.py original.nes --extract-all assets/text/
python tools/music_editor_advanced.py original.nes --extract-all assets/music/

# 3. Make modifications
python tools/enemy_ai_editor.py original.nes --enemy "Slime" --hp 20 -o modified.nes
python tools/spell_editor.py modified.nes --spell "Heal" --power 15 -o modified.nes

# 4. Create patch
python tools/binary_patch_tool.py original.nes modified.nes --create myhack.bps --format bps

# 5. Validate changes
python tools/rom_metadata_analyzer.py modified.nes --compare original.nes

# 6. Test with state validator
python tools/game_state_validator.py testsave.sav
```

#### Balance Optimization Workflow
```bash
# 1. Analyze current balance
python tools/enemy_ai_editor.py rom.nes --analyze-balance
python tools/item_shop_editor.py rom.nes --analyze-balance
python tools/spell_editor.py rom.nes --analyze-balance
python tools/character_editor.py rom.nes --analyze

# 2. Make adjustments based on recommendations

# 3. Re-analyze to verify
```

#### Graphics Overhaul Workflow
```bash
# 1. Extract all graphics
python tools/tileset_manager.py rom.nes --extract-all gfx/tiles/
python tools/sprite_editor_advanced.py rom.nes --extract-monsters gfx/monsters/

# 2. Optimize tileset
python tools/tileset_manager.py rom.nes --find-duplicates
python tools/tileset_manager.py rom.nes --optimize

# 3. Export pattern tables for editing
python tools/tileset_manager.py rom.nes --export-pattern-table 0 --output pt0.png
python tools/tileset_manager.py rom.nes --export-pattern-table 1 --output pt1.png
python tools/tileset_manager.py rom.nes --export-pattern-table 2 --output pt2.png
python tools/tileset_manager.py rom.nes --export-pattern-table 3 --output pt3.png
```

---

## Tool Integration Matrix

| Tool | Input | Output | Dependencies |
|------|-------|--------|--------------|
| ROM Metadata Analyzer | ROM | Report, JSON, XML | - |
| Binary Patch Tool | ROM(s) | IPS/BPS patch | - |
| Disassembly Annotator | ROM | .nl, .mlb, .inc, JSON | - |
| Tileset Manager | ROM | PNG, stats | PIL, numpy |
| Sprite Editor | ROM | PNG, sprites | PIL, numpy |
| Dialogue Editor | ROM | Text files | - |
| Enemy AI Editor | ROM | Modified ROM, JSON | - |
| Item Shop Editor | ROM | Modified ROM, JSON | - |
| Spell Editor | ROM | Modified ROM, JSON | - |
| Character Editor | ROM | Modified ROM, JSON | - |
| Map Editor | ROM | PNG, JSON | PIL, numpy |
| Game State Validator | Save file | Validation report | - |
| Music Editor | ROM | NSF, MIDI | - |

---

## Dependencies

### Python Requirements
```
pillow>=9.0.0
numpy>=1.20.0
```

### Installation
```bash
pip install -r requirements.txt
```

---

## Best Practices

### 1. Always Backup
```bash
cp original.nes backup.nes
```

### 2. Use Version Control
```bash
git add .
git commit -m "Modified enemy stats"
```

### 3. Create Patches
```bash
# Share your work as patches, not modified ROMs
python tools/binary_patch_tool.py original.nes modified.nes --create mypatch.bps --format bps
```

### 4. Validate Changes
```bash
# Always validate after modifications
python tools/rom_metadata_analyzer.py modified.nes
python tools/game_state_validator.py save.sav
```

### 5. Document Changes
```bash
# Export databases for documentation
python tools/enemy_ai_editor.py modified.nes --export changes/enemies.json
python tools/item_shop_editor.py modified.nes --export changes/items.json
```

---

## Troubleshooting

### Common Issues

**"ROM not found"**
- Check file path is correct
- Use absolute paths if relative paths fail

**"Invalid ROM format"**
- Verify ROM is Dragon Warrior (USA)
- Check ROM has iNES header

**"PIL/numpy required"**
```bash
pip install pillow numpy
```

**"Permission denied"**
- Check file is not read-only
- Run with appropriate permissions

---

## Contributing

See `CONTRIBUTING.md` for guidelines on extending tools.

---

## License

See `LICENSE` for details.

---

**Dragon Warrior ROM Hacking Toolkit - Complete Suite**
Version 1.0 | © 2024
