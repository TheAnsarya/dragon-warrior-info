# Asset Integration Status & Tracking

This document tracks the status of JSON asset integration into the ROM build pipeline.

## ✅ Fully Integrated

These assets are edited via JSON and automatically included in the ROM build.

### Monster Data
- **JSON File**: `assets/json/monsters_verified.json`
- **Generator**: `tools/asset_reinserter.py` → `source_files/generated/monster_data.asm`
- **Bank Integration**: Bank01.asm via `.include "generated/monster_data.asm"`
- **Editor**: `tools/editors/monster_editor.py`
- **Status**: ✅ Complete

### Item Costs (Prices)
- **JSON File**: `assets/json/items_corrected.json`
- **Generator**: `tools/generate_item_cost_table.py` → `source_files/generated/item_cost_table.asm`
- **Bank Integration**: Bank00.asm via `.include "generated/item_cost_table.asm"`
- **Editor**: `tools/editors/item_editor.py`
- **Status**: ✅ Complete

### Spell Costs (MP)
- **JSON File**: `assets/json/spells.json`
- **Generator**: `tools/generate_spell_cost_table.py` → `source_files/generated/spell_cost_table.asm`
- **Bank Integration**: Bank00.asm via `.include "generated/spell_cost_table.asm"`
- **Editor**: `tools/editors/spell_editor.py`
- **Status**: ✅ Complete (Added 2025-11-29)

### Shop Inventories
- **JSON File**: `assets/json/shops.json`
- **Generator**: `tools/generate_shop_items_table.py` → `source_files/generated/shop_items_table.asm`
- **Bank Integration**: Bank00.asm via `.include "generated/shop_items_table.asm"`
- **Editor**: `tools/editors/shop_editor.py`, `tools/shop_editor.py`
- **Extractor**: `tools/extract_shops_from_rom.py` (extracts correct shop data from ROM)
- **Status**: ✅ Complete (Added 2025-11-29)

---

## ⚠️ Generated But Not Linked

These assets have JSON data and generate ASM, but are not yet linked to Bank files.

### Dialog Text
- **JSON File**: `assets/json/dialogs.json`
- **Generator**: `tools/asset_reinserter.py` → `source_files/generated/dialog_data.asm`
- **Bank Location**: Multiple banks with pointer tables
- **Editor**: `tools/editors/dialog_editor.py`
- **Blocker**: Complex pointer table system, text compression
- **Effort**: High - Requires pointer recalculation
- **Status**: 🔴 Needs significant work

**Technical Details:**
- Dragon Warrior uses word substitution compression (0x80-0x8F)
- Dialog has pointer tables pointing to text strings
- Changing text length requires updating all following pointers
- Need careful space management

---

## ❌ Not Yet Implemented

### PNG → CHR Graphics
- **Source**: `assets/graphics/*.png` (144 files)
- **Target**: `build/chr_rom.bin` or `source_files/chr_rom.bin`
- **Editor**: Various image editors + `tools/visual_graphics_editor.py`
- **GitHub Issue**: #4 "Build CHR Reinsertion Tool"
- **Effort**: High
- **Status**: 🔴 Not started

**Technical Details:**
- NES uses 2bpp planar format for CHR tiles
- Each tile is 8x8 pixels, 16 bytes
- Must respect 4-color palette constraints
- Need palette assignment per tile group

### Graphics Metadata
- **JSON File**: `assets/json/graphics.json`, `assets/json/graphics_data.json`
- **Generator**: Generates but not used
- **Status**: 🔴 Depends on PNG→CHR

### Palette Data
- **JSON File**: `assets/json/palettes.json`
- **Source PNGs**: `assets/palettes/*.png` (8 files)
- **Generator**: `tools/asset_reinserter.py` → `source_files/generated/palette_data.asm`
- **Bank Location**: Multiple locations in Bank00/Bank01
- **Effort**: Medium
- **Status**: 🔴 Needs investigation

### Map Data
- **JSON File**: `assets/json/maps.json` (1.5MB!)
- **Generator**: `tools/asset_reinserter.py` → `source_files/generated/map_data.asm`
- **Editor**: `tools/map_editor.py`, `tools/world_map_editor.py`
- **Effort**: Very High - RLE compression, space constraints
- **Status**: 🔴 Needs significant work

### NPC Data
- **JSON File**: `assets/json/npcs.json`
- **No Generator**: Not yet implemented
- **Editor**: None yet
- **Effort**: Medium
- **Status**: 🔴 Not started

### Music/Audio
- **Source**: `assets/music/` (empty)
- **Editor**: `tools/music_editor.py`
- **Effort**: High - Complex audio format
- **Status**: 🔴 Not extracted

---

## Related GitHub Issues

| Issue | Title | Status |
|-------|-------|--------|
| #1 | Document Assembly Code Bank Contents | Open |
| #2 | Create CHR-ROM Graphics Editing Workflow Guide | Open |
| #4 | Build CHR Reinsertion Tool | Open |
| #5 | Create Interactive Map Editor Tool | Open |
| #7 | Create Music/Sound Effect Editing Guide | Open |

---

## Priority Order for Implementation

1. **Shop Data** - Relatively simple format, high modding value
2. **Palette Data** - Needed before PNG→CHR can be useful
3. **PNG→CHR** (Issue #4) - Enables graphics modding
4. **NPC Data** - Useful for game modifications
5. **Map Data** - Complex but valuable for level editing
6. **Dialog Text** - Complex pointer system, lower priority
7. **Music** - Least common modification

---

## Build Commands

```powershell
# Build with all integrated assets (recommended)
.\build_with_assets.ps1

# Build without asset generation (raw ASM only)
.\build_with_assets.ps1 -UseAssets:$false

# Clean build
.\build_with_assets.ps1 -Clean
```

---

*Last updated: 2025-11-29*
