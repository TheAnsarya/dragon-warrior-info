# Dragon Warrior Asset Pipeline

Complete documentation of the asset extraction → editing → generation → build pipeline.

## Overview

The Dragon Warrior ROM hacking toolkit uses a JSON-based asset pipeline that allows editing game data through human-readable files which are then compiled back into assembly code and built into the ROM.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ASSET PIPELINE FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ROM FILE                                                           │
│      ↓                                                               │
│   EXTRACTORS (extract_*.py)                                          │
│      ↓                                                               │
│   JSON FILES (assets/json/*.json)                                    │
│      ↓                                                               │
│   EDITORS (universal_editor.py)                                      │
│      ↓                                                               │
│   GENERATORS (generate_*.py)                                         │
│      ↓                                                               │
│   ASM FILES (source_files/generated/*.asm)                           │
│      ↓                                                               │
│   BUILD SCRIPT (build_with_assets.ps1)                               │
│      ↓                                                               │
│   REBUILT ROM (build/dragon_warrior_rebuilt.nes)                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Asset Types

### Core Game Data

| Asset | JSON File | Generator | ASM Output | Records |
|-------|-----------|-----------|------------|---------|
| 👾 Monsters | `monsters.json` | `generate_monster_tables.py` | `MonsterTables.asm` | 40 |
| 📦 Items | `items.json` | `generate_item_cost_table.py` | `ItemTable.asm` | 29 |
| ✨ Spells | `spells.json` | `generate_spell_cost_table.py` | `SpellTable.asm` | 10 |
| 🏪 Shops | `shops.json` | `generate_shop_items_table.py` | `ShopTables.asm` | 12 |
| 💬 Dialogs | `dialogs.json` | `generate_dialog_tables.py` | `DialogTables.asm` | 298 |
| 🧙 NPCs | `npcs.json` | `generate_npc_tables.py` | `NpcTables.asm` | 24 |
| ⚔️ Equipment | `equipment_bonuses.json` | `generate_equipment_bonus_tables.py` | `EquipmentBonuses.asm` | 32 |
| 🗺️ Maps | `maps.json` | `asset_reinserter.py` | `map_data.asm` | 25 |
| 🎨 Graphics | `graphics_data.json` | `generate_chr_from_pngs.py` | `chr_rom.bin` | 512 tiles |
| 🎨 Palettes | `palettes.json` | `asset_reinserter.py` | `palette_data.asm` | 20 |

### Formula/Mechanics Assets (NEW)

| Asset | JSON File | Generator | ASM Output | Description |
|-------|-----------|-----------|------------|-------------|
| ⚔️ Damage | `damage_formulas.json` | `generate_damage_tables.py` | `damage_tables.asm` | Physical/spell damage parameters |
| ✨ Spell FX | `spell_effects.json` | `generate_spell_effects.py` | `spell_effects.asm` | Spell behavior, ranges, resistances |
| 📈 Experience | `experience_table.json` | `generate_experience_table.py` | `experience_table.asm` | Level 1-30 progression curve |

### Audio Assets (NEW)

| Asset | JSON File | Generator | ASM Output | Records |
|-------|-----------|-----------|------------|---------|
| 🎵 Music | `music.json` | `generate_music_tables.py` | `music_tables.asm` | 27 tracks, 22 SFX |

## Pipeline Steps

### Step 1: Extraction

Extract raw data from the ROM into JSON format:

```powershell
# Extract all data
python tools/extract_all_data.py

# Or extract specific assets:
python tools/extract_monsters_verified.py
python tools/extract_dialogs_from_asm.py
python tools/extract_items_from_rom.py
python tools/extract_spells.py
python tools/extract_shops_from_rom.py
python tools/extract_npcs_from_rom.py
```

### Step 2: Edit JSON

Edit JSON files directly or use the Universal Editor:

```powershell
# Launch Universal Editor
python tools/universal_editor.py

# Or edit JSON files directly in assets/json/
```

### Step 3: Generate Assembly

Generate ASM code from edited JSON using the unified generator:

```powershell
# Run all 11 generators at once (RECOMMENDED)
python tools/generate_all_assets.py

# Run specific generators only
python tools/generate_all_assets.py --only monsters
python tools/generate_all_assets.py --only damage
python tools/generate_all_assets.py --only music

# Force regeneration even if up-to-date
python tools/generate_all_assets.py --force

# Or generate specific assets individually:
python tools/generate_monster_tables.py
python tools/generate_dialog_tables.py
python tools/generate_item_cost_table.py
python tools/generate_spell_cost_table.py
python tools/generate_shop_items_table.py
python tools/generate_npc_tables.py
python tools/generate_equipment_bonus_tables.py
python tools/generate_damage_tables.py
python tools/generate_spell_effects.py
python tools/generate_experience_table.py
python tools/generate_music_tables.py
```

**Unified Generator Output Example:**
```
======================================================================
DRAGON WARRIOR - ASSET GENERATOR
======================================================================
[MONSTERS] ✅ Generated successfully
[ITEMS] ✅ Generated successfully
[DAMAGE] ✅ Generated successfully
[MUSIC] ✅ Generated successfully
----------------------------------------------------------------------
Total: 11/11 generators succeeded
```

### Step 4: Edit Graphics (Optional)

Edit PNG tiles in `assets/graphics/`:

```powershell
# Extract CHR tiles to PNG (if not already done)
python tools/extract_chr_tiles.py

# Edit PNGs in assets/graphics/ using any image editor
# Tiles must be 8x8 pixels with at most 4 colors

# Generate CHR-ROM from edited PNGs
python tools/generate_chr_from_pngs.py
```

### Step 5: Build ROM

Build the ROM with generated assets:

```powershell
# Build with data assets (recommended)
.\build_with_assets.ps1

# Build with data AND graphics assets
.\build_with_assets.ps1 -UseGraphics

# Basic build (no asset integration)
.\build_rom.ps1
```

## Directory Structure

```
dragon-warrior-info/
├── assets/
│   └── json/               # Editable JSON asset files
│       ├── monsters_verified.json
│       ├── items_corrected.json
│       ├── spells.json
│       ├── shops.json
│       ├── dialogs_extracted.json
│       ├── npcs_extracted.json
│       ├── equipment_bonuses.json
│       ├── maps.json
│       ├── graphics_data.json
│       └── palettes.json
│
├── source_files/
│   └── generated/          # Generated ASM files
│       ├── monster_data.asm
│       ├── item_data.asm
│       ├── spell_data.asm
│       ├── shop_data.asm
│       ├── dialog_data.asm
│       ├── npc_tables.asm
│       ├── equipment_bonus_tables.asm
│       ├── map_data.asm
│       ├── graphics_data.asm
│       ├── palette_data.asm
│       └── dragon_warrior_assets.asm  # Master include
│
├── tools/
│   ├── universal_editor.py     # Main editor GUI
│   ├── asset_reinserter.py     # Master generator
│   ├── extract_*.py            # Extraction scripts
│   └── generate_*.py           # Individual generators
│
├── build/
│   └── dragon_warrior_rebuilt.nes  # Output ROM
│
└── roms/
    └── Dragon Warrior (U) (PRG1) [!].nes  # Reference ROM
```

## JSON Formats

### Monster Format (`monsters_verified.json`)

```json
{
  "0": {
    "name": "Slime",
    "hp": 3,
    "strength": 5,
    "defense": 3,
    "agility": 15,
    "magic_defense": 1,
    "spell_power": 0,
    "experience": 1,
    "gold": 2
  }
}
```

### Dialog Format (`dialogs_extracted.json`)

```json
{
  "0": {
    "id": 0,
    "address": "0x8000",
    "bytes_hex": "$0A $0B $0C $FC",
    "text": "Hello!",
    "notes": "Townsperson greeting"
  }
}
```

### Item Format (`items_corrected.json`)

```json
{
  "0": {
    "name": "Bamboo Pole",
    "buy_price": 10,
    "sell_price": 5,
    "attack_bonus": 2,
    "defense_bonus": 0,
    "item_type": 0,
    "equippable": true,
    "useable": false
  }
}
```

### Spell Format (`spells.json`)

```json
{
  "0": {
    "name": "HEAL",
    "mp_cost": 4,
    "min_effect": 10,
    "max_effect": 17,
    "type": "healing"
  }
}
```

### Shop Format (`shops.json`)

```json
{
  "0": {
    "name": "Tantegel Weapon Shop",
    "type": "weapon",
    "items": [0, 1, 2, 3]
  }
}
```

## TBL Encoding Reference

Dragon Warrior uses a custom text encoding (TBL format):

| Byte Range | Characters |
|------------|------------|
| $00-$09 | 0-9 (digits) |
| $0A-$23 | a-z (lowercase) |
| $24-$3D | A-Z (uppercase) |
| $3E-$5E | Punctuation and symbols |
| $5F | Space |
| $F0 | PLRL (plural) |
| $F4 | ENMY (enemy name) |
| $F5 | AMNT (amount) |
| $F6 | SPEL (spell name) |
| $F7 | ITEM (item name) |
| $F8 | NAME (hero name) |
| $FB | WAIT (pause) |
| $FC | END (end of string) |
| $FD | Newline |

## Editors

### Universal Editor (Recommended)

The Universal Editor combines all editing tools into a single tabbed interface:

```powershell
python tools/universal_editor.py
```

Features:
- 🚀 Dashboard with asset status
- 👾 Monster stats editor
- 📦 Item property editor
- ✨ Spell configuration
- 🏪 Shop inventory management
- 💬 Dialog text editor
- 🧙 NPC data editor
- ⚔️ Equipment bonus tables
- 🗺️ Map viewer
- 🎨 Graphics metadata
- 📊 Statistics overview

### Individual Editors

Specialized editors are also available:

- `monster_editor.py` - Detailed monster editing
- `dialog_editor.py` - Dialog text with TBL encoding
- `dialogue_editor.py` - Alternative dialog editor
- `item_editor.py` - Item properties
- `spell_editor.py` - Spell configuration
- `shop_editor.py` - Shop inventories
- `npc_editor.py` - NPC data
- `tile_editor.py` - Graphics tiles
- `palette_editor.py` - Color palettes

## Build Scripts

### build_with_assets.ps1 (Recommended)

Full asset-first build pipeline:
1. Generates ASM from JSON assets
2. Assembles iNES header
3. Assembles all PRG banks
4. Extracts CHR-ROM
5. Concatenates final ROM
6. Validates against reference

### build_rom.ps1

Basic build without asset integration.

## Troubleshooting

### JSON Parse Errors
- Ensure JSON is valid (no trailing commas)
- Use UTF-8 encoding
- Check for proper escaping of special characters

### Generator Failures
- Verify JSON file exists and is readable
- Check Python dependencies: `pip install -r requirements.txt`
- Run with verbose mode for debugging

### Build Failures
- Ensure Ophis assembler is installed
- Check that reference ROM exists
- Verify generated ASM files are valid

## Contributing

To add a new asset type:

1. Create extractor: `tools/extract_<asset>_from_rom.py`
2. Create JSON schema in `assets/json/`
3. Create generator: `tools/generate_<asset>_tables.py`
4. Add to `AssetManager.ASSET_TYPES` in `universal_editor.py`
5. Update `build_with_assets.ps1` to include new ASM

## References

- [Dragon Warrior Data Crystal](https://datacrystal.romhacking.net/wiki/Dragon_Warrior)
- [NES Assembly Guide](https://www.nesdev.org/wiki/)
- [Ophis Assembler](https://michaelcmartin.github.io/Ophis/)
