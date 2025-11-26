# Dragon Warrior Asset Extraction - Session Summary

## Work Completed

This session accomplished comprehensive asset extraction and ROM analysis for Dragon Warrior (NES).

### 1. ROM Build System (✅ Complete)

**Created build_rom.ps1** - Full ROM assembly pipeline:
- Assembles Header + 4 PRG banks + CHR-ROM
- Output: 81,936 bytes (exact ROM size)
- **Critical Discovery**: Disassembly is from **PRG0**, not PRG1
  - 3 byte differences (0x3FAE, 0x3FAF, 0xAF7C)
  - Build produces perfect PRG0 ROM
  - Documented in BUILD_VERIFICATION.md

**Fixed Bank01.asm**:
- Replaced unsupported `.ifdef` conditionals with actual monster data
- Restored 40 monster entries (640 bytes) from backup

### 2. Monster Sprites (✅ Complete - 39/39 Monsters)

**Created rom_monster_sprite_extractor.py**:
- Extracts all 39 monster sprites directly from ROM
- Parses EnSpritesPtrTbl at 0x59F4 (CPU 0x99E4)
- Handles MMC1 bank switching (Bank00/Bank01)
- **Bug Fix**: Specter pointer workaround (0x9BAA invalid, uses Ghost data at 0x1BAA)
- **Output**: 840 sprite tiles total, average 21.5 tiles per monster

**Extracted Assets**:
- 39 monsters: Slime → Dragonlord (True Form)
- Each with palette.png, sprite.png, metadata.json
- Visual catalog with all monster compositions

### 3. CHR-ROM Tiles (✅ Complete - 512 Tiles)

**Created chr_tile_extractor.py**:
- Extracts all 512 tiles from CHR-ROM (16KB at 0x10010)
- Pattern Table 0 (0x000-0x0FF): 256 background/terrain tiles
- Pattern Table 1 (0x100-0x1FF): 256 font/UI tiles
- **Output**: Individual PNGs + tile sheets for each pattern table

**Extracted Assets**:
- 512 individual 8x8 tile images
- 2 comprehensive tile sheets
- metadata.json for each category

### 4. Item/Spell/Shop Database (✅ Complete)

**Created item_data_extractor.py**:
- Complete item database with 35 items
  - 7 weapons (Bamboo Pole → Erdrick's Sword)
  - 7 armor (Clothes → Erdrick's Armor)
  - 3 shields (Small → Silver)
  - 6 consumables (Herb, Torch, Dragon Scale, Wings, Magic Key, Fairy Water)
  - 9 key items (quest-critical items)
  - 2 cursed items (Belt, Necklace)
  - 1 accessory (Fighter's Ring)

- 10 spells with complete data:
  - Names, MP costs, learn levels, effects
  - HEAL, HURT, SLEEP, RADIANT, STOPSPELL, OUTSIDE, RETURN, REPEL, HEALMORE, HURTMORE

- 11 shops across 5 towns:
  - Brecconary: 2 shops (weapons/armor + items)
  - Garinham: 2 shops
  - Kol: 2 shops
  - Cantlin: 4 shops (3 weapon/armor specialty shops)
  - Rimuldar: 1 shop

**Output**: item_database.json with full stats, bonuses, costs, and shop inventories

## Technical Achievements

### ROM Structure Analysis
- **MMC1 Mapper**: Bank00 (fixed 0x8000-0xBFFF), Bank01-03 (switchable 0xC000-0xFFFF)
- **CHR-ROM**: 16KB at file offset 0x10010
- **Sprite Format**: 3-byte entries [tile, attributes, x_pos], 0x00 terminator
- **Pointer Encoding**: <0x8000 = Bank01 offset, >=0x8000 = Bank00 CPU address

### Build System
- **Ophis Assembler**: Separate bank assembly (doesn't support .include for multi-bank)
- **Build Process**: Header → Bank00-03 → CHR concatenation
- **Verification**: Byte-perfect PRG0 reproduction

### Data Extraction
- **Monster Data**: 39 entries × 16 bytes = 624 bytes (EnStatTbl at CPU 0x9E4B)
- **Sprite Data**: 78 byte pointer table → 840 individual sprite tiles
- **Item Costs**: 35 entries × 2 bytes = 70 bytes (WndCostTbl at CPU 0xBE10)
- **Weapon Bonuses**: 7 bytes (0x99CF-0x99D5)
- **Armor Bonuses**: 7 bytes (0x99D7-0x99DD)
- **Shield Bonuses**: 3 bytes (0x99DF-0x99E1)

## Files Created

### Extraction Tools (tools/extraction/)
1. **rom_monster_sprite_extractor.py** (416 lines)
   - Direct ROM sprite parser
   - Multi-tile composition renderer
   - Bank address translator

2. **chr_tile_extractor.py** (290 lines)
   - CHR-ROM tile decoder
   - Tile sheet generator
   - NES palette renderer

3. **item_data_extractor.py** (224 lines)
   - Item/spell database generator
   - Shop inventory compiler

### Build System
1. **build_rom.ps1** (168 lines)
   - Multi-bank ROM assembler
   - CHR-ROM extractor
   - Verification system

### Documentation
1. **BUILD_VERIFICATION.md**
   - ROM version analysis (PRG0 vs PRG1)
   - Build process documentation
   - Byte difference breakdown

### Extracted Assets
- `extracted_assets/graphics_comprehensive/monsters/` - 39 monster sprites (120 files)
- `extracted_assets/chr_tiles/background/` - 256 tiles + sheet
- `extracted_assets/chr_tiles/font_and_ui/` - 256 tiles + sheet
- `extracted_assets/data/item_database.json` - Complete game database

## Commits Made

1. **Extract all 39 monsters with ROM-based sprite extractor** (commit 9eb5574)
   - rom_monster_sprite_extractor.py
   - 39 monsters × 3 files = 120 asset files
   - Visual catalogs regenerated

2. **Fix ROM build system and verify disassembly matches PRG0** (commit 59a2822)
   - build_rom.ps1 created
   - Bank01.asm fixed (monster data restored)
   - BUILD_VERIFICATION.md added
   - PRG0 vs PRG1 analysis documented

3. **Extract CHR tiles, items, spells, and shop data** (commit b422c80)
   - chr_tile_extractor.py: 512 CHR tiles
   - item_data_extractor.py: Complete game database
   - 520 files committed

## Statistics

### Assets Extracted
- **Monster Sprites**: 39 monsters, 840 sprite tiles
- **CHR Tiles**: 512 tiles (256 background + 256 font/UI)
- **Items**: 35 items across 7 categories
- **Spells**: 10 spells with full metadata
- **Shops**: 11 shops in 5 towns

### Code Written
- **Python Scripts**: 3 tools, ~930 lines of code
- **PowerShell**: 1 build script, 168 lines
- **Documentation**: 2 comprehensive markdown files

### Bugs Fixed
- Specter sprite pointer bug (0x9BAA → 0x1BAA workaround)
- Bank01.asm conditional includes (Ophis compatibility)
- PowerShell variable interpolation with colons
- MMC1 bank address translation logic

## Remaining Work (Not Completed)

### Dialog/Text Extraction
- Text encoding system (custom compression)
- Dialog strings for all NPCs
- System messages
- Location names

### Map Data
- Overworld map (120×120 tiles)
- Town/dungeon maps
- NPC placement
- Warp points
- Encounter zones

### Visual Catalog
- HTML catalog for all assets
- Interactive asset browser
- ROM address cross-reference

## Key Insights

1. **Disassembly Source**: Confirmed to be PRG0, not PRG1
2. **ROM Bugs**: Specter sprite pointer bug exists in both PRG0 and PRG1
3. **Build System**: Ophis requires separate bank assembly, not .include-based
4. **MMC1 Banking**: Bank00 fixed, Bank01-03 switchable via mapper
5. **Sprite Storage**: Efficient format (3 bytes per sprite + shared tiles)

## Project Status

**Overall Progress**: ~70% of core asset extraction complete

✅ **Completed**:
- Monster sprites (39/39)
- CHR tiles (512/512)
- Item database (35 items)
- Spell database (10 spells)
- Shop database (11 shops)
- ROM build system
- ROM version verification

⚠️ **In Progress**:
- Dialog/text extraction

❌ **Not Started**:
- Map data extraction
- Hero/NPC sprite identification
- Visual catalog generation

## Recommendations

1. **Use PRG0 as canonical ROM** - Disassembly perfectly matches PRG0
2. **Document Specter bug** - Known issue affects both ROM versions
3. **Continue extraction** - Dialog and map data are next priorities
4. **Create visual catalog** - HTML viewer for all extracted assets
5. **Build reinsertion tools** - Enable ROM hacking/translation

## Session Metrics

- **Time**: ~1 session (used significant token budget)
- **Commits**: 3 major commits, all pushed to origin/master
- **Files Modified/Created**: 525 files total
- **Lines of Code**: ~1,100 lines across all tools
- **Assets Generated**: 670+ files (sprites, tiles, databases, docs)

---

**Project Repository**: dragon-warrior-info  
**Primary ROM**: Dragon Warrior (U) (PRG0) [!].nes  
**Build Output**: dragon_warrior_rebuilt.nes (81,936 bytes - perfect PRG0 match)
