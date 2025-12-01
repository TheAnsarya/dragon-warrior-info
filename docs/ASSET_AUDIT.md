# Dragon Warrior Asset Audit

## Purpose
This document provides a complete inventory of all extractable assets in Dragon Warrior (NES),
their current extraction status, JSON representation, generators, and editor integration.

**Last Updated:** Auto-generated
**Repository:** dragon-warrior-info

---

## Asset Inventory Summary

| Category | Assets | Extracted | Has JSON | Has Generator | Has Editor | Pipeline Status |
|----------|--------|-----------|----------|---------------|------------|-----------------|
| **Game Data** | 8 | 8/8 ✅ | 8/8 ✅ | 7/8 ⚠️ | 7/8 ⚠️ | 87% |
| **Text** | 3 | 3/3 ✅ | 3/3 ✅ | 2/3 ⚠️ | 2/3 ⚠️ | 67% |
| **Graphics** | 4 | 4/4 ✅ | 2/4 ⚠️ | 1/4 ❌ | 2/4 ⚠️ | 50% |
| **Maps** | 2 | 2/2 ✅ | 2/2 ✅ | 1/2 ⚠️ | 1/2 ⚠️ | 50% |
| **Audio** | 2 | 1/2 ⚠️ | 1/2 ⚠️ | 0/2 ❌ | 1/2 ⚠️ | 25% |
| **Formulas** | 3 | 3/3 ✅ | 3/3 ✅ | 3/3 ✅ | 3/3 ✅ | 100% |
| **TOTAL** | **22** | **21/22** | **19/22** | **14/22** | **16/22** | **68%** |

---

## Detailed Asset Inventory

### 1. Game Data Assets

#### Monsters (✅ Complete)
- **ROM Location:** Bank01 $8A90-$8DEB, Bank03 various
- **JSON File:** `assets/json/monsters.json`, `monsters_verified.json`
- **Generator:** `tools/generate_monster_tables.py`
- **ASM Output:** `source_files/generated/MonsterTables.asm`
- **Editor Tab:** MonsterEditorTab in Universal Editor
- **Records:** 40 monsters
- **Fields:** HP, MP, attack, defense, agility, XP, gold, patterns, resistance
- **Status:** ✅ Fully integrated

#### Items (✅ Complete)
- **ROM Location:** Bank01 $AE9D-$AFxx, various
- **JSON File:** `assets/json/items.json`, `items_corrected.json`
- **Generator:** `tools/generate_item_cost_table.py`
- **ASM Output:** `source_files/generated/ItemTable.asm`
- **Editor Tab:** ItemEditorTab in Universal Editor
- **Records:** 31 items (weapons, armor, shields, consumables)
- **Fields:** Name, buy price, sell price, attack/defense bonus, type
- **Status:** ✅ Fully integrated

#### Spells (✅ Complete)
- **ROM Location:** Bank03 $E700-$EC90, $DBB8-$DBE1
- **JSON File:** `assets/json/spells.json`
- **Generator:** `tools/generate_spell_cost_table.py`
- **ASM Output:** `source_files/generated/SpellTable.asm`
- **Editor Tab:** SpellEditorTab in Universal Editor
- **Records:** 10 spells
- **Fields:** Name, MP cost, learn level, effect type
- **Status:** ✅ Fully integrated

#### Equipment Bonuses (✅ Complete)
- **ROM Location:** Bank01 $AEB3-$AED3
- **JSON File:** `assets/json/equipment_bonuses.json`
- **Generator:** `tools/generate_equipment_bonus_tables.py`
- **ASM Output:** `source_files/generated/EquipmentBonuses.asm`
- **Editor Tab:** JsonEditorTab (Equipment) in Universal Editor
- **Records:** 32 equipment pieces
- **Fields:** Slot, attack bonus, defense bonus, special properties
- **Status:** ✅ Fully integrated

#### Shops (✅ Complete)
- **ROM Location:** Bank02 various shop tables
- **JSON File:** `assets/json/shops.json`
- **Generator:** `tools/generate_shop_items_table.py`
- **ASM Output:** `source_files/generated/ShopTables.asm`
- **Editor Tab:** ShopEditorTab in Universal Editor
- **Records:** ~10 shop locations
- **Fields:** Location, item list, prices
- **Status:** ✅ Fully integrated

#### NPCs (✅ Complete)
- **ROM Location:** Bank02 NPC tables
- **JSON File:** `assets/json/npcs.json`, `npcs_extracted.json`
- **Generator:** `tools/generate_npc_tables.py`
- **ASM Output:** `source_files/generated/NpcTables.asm`
- **Editor Tab:** NpcEditorTab in Universal Editor
- **Records:** ~100+ NPCs across all maps
- **Fields:** Position, sprite, dialog pointer, behavior
- **Status:** ✅ Fully integrated

#### Encounter Zones (✅ Complete)
- **ROM Location:** Bank01 encounter tables
- **JSON File:** `assets/data/encounter_zones.json`
- **Generator:** (embedded in encounter editor)
- **Editor Tab:** EncounterEditorTab in Universal Editor
- **Records:** 8 zones
- **Fields:** Zone ID, monster list, encounter rate
- **Status:** ✅ Fully integrated

#### Complete Game Data (⚠️ Reference Only)
- **JSON File:** `assets/json/complete_game_data.json`
- **Purpose:** Combined reference file, not used in pipeline
- **Status:** ⚠️ Reference only, no generator

---

### 2. Text Assets

#### Dialogs (✅ Complete)
- **ROM Location:** Bank00 text pointers, Bank01/02/03 text data
- **JSON File:** `assets/json/dialogs.json`, `dialogs_extracted.json`
- **Generator:** `tools/generate_dialog_tables.py`
- **ASM Output:** `source_files/generated/DialogTables.asm`
- **Editor Tab:** DialogEditorTab in Universal Editor
- **Records:** 200+ dialog entries
- **Fields:** ID, speaker, text, conditions
- **Status:** ✅ Fully integrated

#### Text Encoding Table (✅ Complete)
- **Source:** Dragon Warrior text encoding
- **JSON File:** `assets/text/text_table.json` (implicit in tools)
- **Generator:** N/A (encoding built into tools)
- **Editor Tab:** TextTableEditorTab in Universal Editor
- **Records:** 256 character mappings
- **Status:** ✅ Integrated via TBL format

#### Script/Event Text (⚠️ Partial)
- **ROM Location:** Various script locations
- **JSON File:** (extracted as part of dialogs)
- **Generator:** (included in dialog generator)
- **Editor Tab:** ScriptEditorTab in Universal Editor
- **Status:** ⚠️ Partially integrated - needs dedicated JSON

---

### 3. Graphics Assets

#### CHR Tiles (✅ Complete)
- **ROM Location:** Bank04 (CHR-ROM) $0000-$1FFF
- **Format:** 8KB CHR data (512 tiles × 16 bytes)
- **JSON File:** `assets/json/graphics.json`, `graphics_data.json`
- **Asset Files:** `assets/graphics/*.png`, `*.chr`
- **Generator:** `tools/generate_chr_from_pngs.py`
- **Editor Tab:** GraphicsEditorTab in Universal Editor
- **Records:** 512 8×8 tiles
- **Status:** ✅ Fully integrated

#### Monster Sprites (✅ Extracted)
- **ROM Location:** CHR-ROM monster sprite area
- **Asset Files:** `assets/graphics/monsters/*.png`
- **Generator:** (included in CHR generator)
- **Editor Tab:** (part of GraphicsEditorTab)
- **Records:** 40 monster sprites (various sizes)
- **Status:** ✅ Extracted, generator integrated

#### Palettes (✅ Complete)
- **ROM Location:** Bank00 palette tables
- **JSON File:** `assets/json/palettes.json`
- **Asset Files:** `assets/palettes/*.pal`
- **Generator:** (manual or via palette editor export)
- **Editor Tab:** PaletteEditorTab in Universal Editor
- **Records:** ~20 palettes (BG + sprite)
- **Status:** ✅ Fully integrated

#### Title Screen / UI Graphics (⚠️ Partial)
- **ROM Location:** CHR-ROM title area
- **JSON File:** (part of graphics.json)
- **Generator:** (part of CHR generator)
- **Editor Tab:** (part of GraphicsEditorTab)
- **Status:** ⚠️ Extracted but no dedicated editor

---

### 4. Map Assets

#### World Map (✅ Complete)
- **ROM Location:** Bank02 world map data (compressed)
- **JSON File:** `assets/json/maps.json`
- **Asset Files:** `assets/maps/world_map.png`
- **Generator:** (included in map tools)
- **Editor Tab:** MapEditorTab in Universal Editor
- **Records:** 120×120 world map tiles
- **Status:** ✅ Fully integrated

#### Town/Dungeon Maps (⚠️ Partial)
- **ROM Location:** Bank02 various map pointers
- **JSON File:** `assets/json/maps.json` (combined)
- **Generator:** (included in map extraction)
- **Editor Tab:** MapEditorTab in Universal Editor
- **Records:** ~25 indoor maps
- **Status:** ⚠️ Extracted, editor needs improvement

---

### 5. Audio Assets

#### Music/NSF Data (⚠️ Partial)
- **ROM Location:** Bank03 music engine, various
- **JSON File:** `assets/music/*.json` (if exists)
- **Generator:** ❌ Not implemented
- **Editor Tab:** MusicEditorTab in Universal Editor
- **Records:** ~15 music tracks
- **Status:** ⚠️ Editor exists, no JSON extraction/generation

#### Sound Effects (❌ Not Extracted)
- **ROM Location:** Bank03 SFX data
- **JSON File:** ❌ Not extracted
- **Generator:** ❌ Not implemented
- **Editor Tab:** (part of MusicEditorTab)
- **Records:** ~20 sound effects
- **Status:** ❌ Needs extraction and pipeline

---

### 6. Formula/Calculation Assets (NEW)

#### Damage Formulas (✅ Complete)
- **ROM Location:** Bank03 $EFE5-$F04F
- **JSON File:** `assets/json/damage_formulas.json`
- **Generator:** `tools/generate_damage_tables.py`
- **ASM Output:** `build/reinsertion/damage_tables.asm`
- **Editor Tab:** DamageEditorTab in Universal Editor
- **Records:** Physical damage, spell damage, healing, environmental
- **Status:** ✅ NEW - Fully integrated

#### Spell Effects (✅ Complete)
- **ROM Location:** Bank03 $E700-$EC90, $DBB8-$DBE1
- **JSON File:** `assets/json/spell_effects.json`
- **Generator:** `tools/generate_spell_effects.py`
- **ASM Output:** `build/reinsertion/spell_effects.asm`
- **Editor Tab:** SpellEffectsEditorTab in Universal Editor
- **Records:** 10 player spells, 4 enemy spell variants
- **Status:** ✅ NEW - Fully integrated

#### Experience Table (✅ Complete)
- **ROM Location:** Bank03 $F35B (exp), Bank01 $A0CD (stats)
- **JSON File:** `assets/json/experience_table.json`
- **Generator:** `tools/generate_experience_table.py`
- **ASM Output:** `build/reinsertion/experience_table.asm`
- **Editor Tab:** ExperienceEditorTab in Universal Editor
- **Records:** 30 levels with exp, stats, spell unlocks
- **Status:** ✅ NEW - Fully integrated

---

## Pipeline Status Summary

### Fully Integrated (Pipeline Complete) ✅
1. Monsters - JSON → Generator → ASM → ROM → Editor
2. Items - JSON → Generator → ASM → ROM → Editor
3. Spells - JSON → Generator → ASM → ROM → Editor
4. Equipment - JSON → Generator → ASM → ROM → Editor
5. Shops - JSON → Generator → ASM → ROM → Editor
6. NPCs - JSON → Generator → ASM → ROM → Editor
7. Dialogs - JSON → Generator → ASM → ROM → Editor
8. CHR Graphics - PNG/JSON → Generator → CHR → ROM → Editor
9. Palettes - PAL/JSON → Manual → ROM → Editor
10. World Map - JSON → Tools → ROM → Editor
11. Damage Formulas - JSON → Generator → ASM → Editor (NEW)
12. Spell Effects - JSON → Generator → ASM → Editor (NEW)
13. Experience Table - JSON → Generator → ASM → Editor (NEW)

### Partially Integrated (Needs Work) ⚠️
1. Town/Dungeon Maps - Extracted, editor limited
2. Music - Editor exists, no JSON/generator
3. Script Events - Combined with dialogs, needs separation
4. Title Graphics - Part of CHR, no dedicated handling

### Not Extracted (TODO) ❌
1. Sound Effects - Need extraction and pipeline
2. AI Behavior Patterns - Embedded in code, complex extraction

---

## Action Items

### High Priority
1. ✅ DONE: Extract damage formulas to JSON
2. ✅ DONE: Create spell effects abstraction
3. ✅ DONE: Extract experience/level progression
4. ⬜ Create music JSON extraction tool
5. ⬜ Create sound effects extraction tool

### Medium Priority
6. ⬜ Improve indoor map editor functionality
7. ⬜ Separate script events from dialogs
8. ⬜ Add AI behavior pattern extraction
9. ⬜ Create title screen dedicated editor

### Low Priority
10. ⬜ Add batch export/import for all assets
11. ⬜ Create asset dependency graph
12. ⬜ Add automated testing for pipeline
13. ⬜ Create asset comparison tools

---

## Universal Editor Tab Summary

| Tab # | Name | Asset Type | Status |
|-------|------|------------|--------|
| 0 | 🚀 Dashboard | Overview | ✅ |
| 1 | 👾 Monsters | monsters.json | ✅ |
| 2 | 📦 Items | items.json | ✅ |
| 3 | ✨ Spells | spells.json | ✅ |
| 4 | 🏪 Shops | shops.json | ✅ |
| 5 | 💬 Dialogs | dialogs.json | ✅ |
| 6 | 🧙 NPCs | npcs.json | ✅ |
| 7 | ⚔️ Equipment | equipment_bonuses.json | ✅ |
| 8 | 🗺️ Maps | maps.json | ✅ |
| 9 | 🎨 Graphics | graphics.json | ✅ |
| 10 | 🖌️ Palettes | palettes.json | ✅ |
| 11 | 🔢 Hex Viewer | ROM direct | ✅ |
| 12 | 📝 Script Editor | ASM files | ✅ |
| 13 | 🔍 Compare ROMs | ROM diff | ✅ |
| 14 | 🎮 Cheat Codes | Game Genie | ✅ |
| 15 | 🎵 Music | music data | ⚠️ |
| 16 | 📋 Text Table | TBL encoding | ✅ |
| 17 | ⚔️ Encounters | encounter_zones.json | ✅ |
| 18 | 📄 ROM Info | iNES header | ✅ |
| 19 | 📊 Statistics | Analytics | ✅ |
| 20 | ⚔️ Damage | damage_formulas.json | ✅ NEW |
| 21 | ✨ Spell FX | spell_effects.json | ✅ NEW |
| 22 | 📈 Experience | experience_table.json | ✅ NEW |

**Total: 23 tabs, 21 functional, 2 partial**

---

## Generator Scripts Summary

| Script | Input | Output | Status |
|--------|-------|--------|--------|
| generate_monster_tables.py | monsters.json | MonsterTables.asm | ✅ |
| generate_item_cost_table.py | items.json | ItemTable.asm | ✅ |
| generate_spell_cost_table.py | spells.json | SpellTable.asm | ✅ |
| generate_equipment_bonus_tables.py | equipment_bonuses.json | EquipmentBonuses.asm | ✅ |
| generate_shop_items_table.py | shops.json | ShopTables.asm | ✅ |
| generate_npc_tables.py | npcs.json | NpcTables.asm | ✅ |
| generate_dialog_tables.py | dialogs.json | DialogTables.asm | ✅ |
| generate_chr_from_pngs.py | *.png | *.chr | ✅ |
| generate_damage_tables.py | damage_formulas.json | damage_tables.asm | ✅ NEW |
| generate_spell_effects.py | spell_effects.json | spell_effects.asm | ✅ NEW |
| generate_experience_table.py | experience_table.json | experience_table.asm | ✅ NEW |

---

*Document auto-maintained by asset audit tools*
