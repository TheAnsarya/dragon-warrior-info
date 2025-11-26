# Dragon Warrior ROM Hacking Verification Checklist

**Version:** 1.0  
**Created:** 2024-11-25  
**Purpose:** Manual verification of extracted data accuracy and ROM modification integrity

---

## Table of Contents

1. [Overview](#overview)
2. [Setup Requirements](#setup-requirements)
3. [Monster Stats Verification](#monster-stats-verification)
4. [Spell Data Verification](#spell-data-verification)
5. [Item & Equipment Verification](#item--equipment-verification)
6. [Map Layout Verification](#map-layout-verification)
7. [Text & Dialog Verification](#text--dialog-verification)
8. [Graphics Verification](#graphics-verification)
9. [ROM Modification Testing](#rom-modification-testing)
10. [Final Validation](#final-validation)

---

## Overview

This checklist provides systematic verification steps for all extracted game data. Use this after:
- Initial ROM extraction
- Data modifications
- ROM reinsertion
- Before releasing ROM hacks

**Verification Methodology:**
- ✅ **PASS**: Data matches original game
- ❌ **FAIL**: Discrepancy found
- ⚠️ **PARTIAL**: Mostly correct with minor issues
- 🔍 **VERIFY**: Needs additional testing

---

## Setup Requirements

### Emulator Setup

- [ ] Install FCEUX or Mesen (recommended for accuracy)
- [ ] Load original Dragon Warrior (U) PRG1 ROM
- [ ] Configure save states (F5 = Save, F7 = Load)
- [ ] Enable cheats/debug mode if needed
- [ ] Prepare comparison screenshots directory: `verification/screenshots/`

### Test ROM Files

- [ ] Original ROM: `roms/dragon_warrior_original.nes` (SHA-256 verified)
- [ ] Modified ROM: `build/dragon_warrior_rebuilt.nes`
- [ ] Backup ROM: `build/backup/dragon_warrior_backup.nes`

### Verification Tools

- [ ] Hex editor (HxD, ImHex, or 010 Editor)
- [ ] JSON validator/viewer
- [ ] Image comparison tool (for sprite sheets)
- [ ] Text diff tool

### Data Files to Verify

- [ ] `extracted_assets/json/monsters.json` (39 monsters)
- [ ] `extracted_assets/json/spells.json` (10 spells)
- [ ] `extracted_assets/json/items.json` (32 items)
- [ ] `extracted_assets/maps/*.json` (22 interior locations)
- [ ] `extracted_assets/text/*.json` (dialog data)
- [ ] `extracted_assets/graphics/*.png` (sprite sheets)

---

## Monster Stats Verification

**Purpose:** Verify all 39 monster stats match in-game battle data  
**Extracted Data:** `extracted_assets/json/monsters.json`  
**ROM Offset:** 0x5E5B (39 × 16 bytes)

### Verification Method

1. Load ROM in emulator
2. Use cheats to encounter specific monster
3. Enter battle and observe stats
4. Compare with extracted JSON data
5. Mark checkboxes below

### Monster Stats Checklist

| ID | Monster Name | HP | Att | Def | Agi | Spel | MDef | XP | Gold | Status |
|----|--------------|----|----|-----|-----|------|------|-----|------|--------|
| 00 | Slime | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 01 | Red Slime | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 02 | Drakee | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 03 | Ghost | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 04 | Magician | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 05 | Magidrakee | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 06 | Scorpion | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 07 | Druin | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 08 | Poltergeist | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 09 | Droll | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 10 | Drakeema | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 11 | Skeleton | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 12 | Warlock | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 13 | Metal Scorpion | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 14 | Wolf | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 15 | Wraith | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 16 | Metal Slime | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 17 | Specter | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 18 | Wolflord | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 19 | Druinlord | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 20 | Drollmagi | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 21 | Wyvern | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 22 | Rouge Scorpion | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 23 | Wraith Knight | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 24 | Golem | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 25 | Goldman | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 26 | Knight | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 27 | Magiwyvern | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 28 | Demon Knight | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 29 | Werewolf | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 30 | Green Dragon | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 31 | Starwyvern | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 32 | Wizard | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 33 | Axe Knight | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 34 | Blue Dragon | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 35 | Stoneman | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 36 | Armored Knight | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 37 | Red Dragon | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |
| 38 | Dragonlord Form 1 | __ | __ | __ | __ | __ | __ | __ | __ | ☐ |

### Verification Notes

**How to Test:**
1. Use GameGenie code `AAAAAA` to force encounter with monster ID XX
2. Enter battle and observe HP/stats displayed
3. Compare with `monsters.json` entry
4. Check XP/Gold reward after defeating monster

**Common Issues:**
- Spell ID may not directly correspond to spell name (check spell table)
- Some monsters have 0x00 (no spell) - verify they don't cast spells in battle
- Metal Slime stats are intentionally difficult (high defense, low HP, flees often)

**Status Key:**
- ✅ All stats verified correct
- ❌ Discrepancy found (document in Notes section)
- ⚠️ Partial verification (some stats confirmed)

---

## Spell Data Verification

**Purpose:** Verify MP costs and spell effects  
**Extracted Data:** `extracted_assets/json/spells.json`  
**ROM Offset:** 0x5F3B (10 × 8 bytes)

### Spell Verification Table

| ID | Spell Name | MP Cost | Effect | In-Game MP | Verified | Status |
|----|------------|---------|--------|------------|----------|--------|
| 00 | HEAL | __ | Restore HP | __ | ☐ | |
| 01 | HURT | __ | Attack Damage | __ | ☐ | |
| 02 | SLEEP | __ | Sleep Enemy | __ | ☐ | |
| 03 | RADIANT | __ | Reveal Surroundings | __ | ☐ | |
| 04 | STOPSPELL | __ | Block Enemy Spells | __ | ☐ | |
| 05 | OUTSIDE | __ | Exit Dungeon | __ | ☐ | |
| 06 | RETURN | __ | Warp to Castle | __ | ☐ | |
| 07 | REPEL | __ | Reduce Encounters | __ | ☐ | |
| 08 | HEALMORE | __ | Greater HP Restore | __ | ☐ | |
| 09 | HURTMORE | __ | Greater Attack | __ | ☐ | |

### Verification Method

1. Load save with hero at appropriate level
2. Open menu and check spell MP costs
3. Cast each spell and verify effect
4. Compare with `spells.json`

**Test Cases:**
- [ ] HEAL restores HP proportional to level
- [ ] HURT damages enemies (verify damage formula if possible)
- [ ] SLEEP causes enemy to skip turns
- [ ] RADIANT reveals hidden items/stairs
- [ ] STOPSPELL prevents enemy magic
- [ ] OUTSIDE exits dungeon to world map
- [ ] RETURN warps to Tantegel throne room
- [ ] REPEL reduces random encounter rate
- [ ] HEALMORE restores more HP than HEAL
- [ ] HURTMORE deals more damage than HURT

---

## Item & Equipment Verification

**Purpose:** Verify item prices, stats, and effects  
**Extracted Data:** `extracted_assets/json/items.json`  
**ROM Offset:** 0x5F83 (32 × 8 bytes)

### Item Categories

#### Tools (15 items)

| ID | Item Name | Buy Price | Sell Price | Effect | Verified | Status |
|----|-----------|-----------|------------|--------|----------|--------|
| 00 | Herb | __ | __ | Restore ~30 HP | ☐ | |
| 01 | Torch | __ | __ | Light radius | ☐ | |
| 02 | Fairy Water | __ | __ | Repel enemies | ☐ | |
| 03 | Wings | __ | __ | Return to castle | ☐ | |
| 04 | Dragon's Scale | __ | __ | Reduce fire damage | ☐ | |
| 05 | Fairy Flute | __ | __ | Put Golem to sleep | ☐ | |
| 06 | Fighter's Ring | __ | __ | +ATK bonus | ☐ | |
| 07 | Erdrick's Token | N/A | N/A | Quest item | ☐ | |
| 08 | Gwaelin's Love | N/A | N/A | Show distance to castle | ☐ | |
| 09 | Cursed Belt | __ | __ | Cursed item | ☐ | |
| 10 | Silver Harp | __ | __ | Random enemy summon | ☐ | |
| 11 | Death Necklace | N/A | N/A | Cursed item | ☐ | |
| 12 | Stones of Sunlight | N/A | N/A | Quest item | ☐ | |
| 13 | Staff of Rain | N/A | N/A | Quest item | ☐ | |
| 14 | Rainbow Drop | N/A | N/A | Creates bridge | ☐ | |

#### Weapons (7 items)

| ID | Weapon Name | Buy Price | Sell Price | Attack Bonus | Verified | Status |
|----|-------------|-----------|------------|--------------|----------|--------|
| 15 | Bamboo Pole | __ | __ | +__ | ☐ | |
| 16 | Club | __ | __ | +__ | ☐ | |
| 17 | Copper Sword | __ | __ | +__ | ☐ | |
| 18 | Hand Axe | __ | __ | +__ | ☐ | |
| 19 | Broad Sword | __ | __ | +__ | ☐ | |
| 20 | Flame Sword | __ | __ | +__ | ☐ | |
| 21 | Erdrick's Sword | N/A | N/A | +__ | ☐ | |

#### Armor (7 items)

| ID | Armor Name | Buy Price | Sell Price | Defense Bonus | Verified | Status |
|----|------------|-----------|------------|---------------|----------|--------|
| 22 | Clothes | __ | __ | +__ | ☐ | |
| 23 | Leather Armor | __ | __ | +__ | ☐ | |
| 24 | Chain Mail | __ | __ | +__ | ☐ | |
| 25 | Half Plate | __ | __ | +__ | ☐ | |
| 26 | Full Plate | __ | __ | +__ | ☐ | |
| 27 | Magic Armor | __ | __ | +__ | ☐ | |
| 28 | Erdrick's Armor | N/A | N/A | +__ | ☐ | |

#### Shields (3 items)

| ID | Shield Name | Buy Price | Sell Price | Defense Bonus | Verified | Status |
|----|-------------|-----------|------------|---------------|----------|--------|
| 29 | Small Shield | __ | __ | +__ | ☐ | |
| 30 | Large Shield | __ | __ | +__ | ☐ | |
| 31 | Silver Shield | __ | __ | +__ | ☐ | |

### Verification Steps

1. Visit shops in Brecconary, Garinham, Kol, Rimuldar, Cantlin
2. Compare shop prices with `items.json`
3. Equip items and verify stat changes
4. Test item effects (Herb healing, Torch light radius, etc.)

**Shop Verification:**
- [ ] Brecconary shop prices match JSON
- [ ] Garinham shop prices match JSON
- [ ] Kol shop prices match JSON
- [ ] Rimuldar shop prices match JSON
- [ ] Cantlin shop prices match JSON

**Equipment Stat Verification:**
- [ ] Weapons increase Attack as specified
- [ ] Armor increases Defense as specified
- [ ] Shields increase Defense as specified
- [ ] Cursed items can be equipped but not removed

---

## Map Layout Verification

**Purpose:** Verify interior map tile layouts  
**Extracted Data:** `extracted_assets/maps/*.json`  
**ROM Data:** MapDatTbl offsets in Bank00.asm

### Interior Locations (22 Total)

| ID | Location Name | Size | Tiles Verified | NPCs Verified | Status |
|----|---------------|------|----------------|---------------|--------|
| 00 | Tantegel Throne Room | __x__ | ☐ | ☐ | |
| 01 | Tantegel Inn | __x__ | ☐ | ☐ | |
| 02 | Tantegel Storage | __x__ | ☐ | ☐ | |
| 03 | Brecconary Town | __x__ | ☐ | ☐ | |
| 04 | Brecconary Inn | __x__ | ☐ | ☐ | |
| 05 | Garinham Town | __x__ | ☐ | ☐ | |
| 06 | Garinham Inn | __x__ | ☐ | ☐ | |
| 07 | Kol Town | __x__ | ☐ | ☐ | |
| 08 | Kol Inn | __x__ | ☐ | ☐ | |
| 09 | Rimuldar Town | __x__ | ☐ | ☐ | |
| 10 | Rimuldar Inn | __x__ | ☐ | ☐ | |
| 11 | Cantlin Town | __x__ | ☐ | ☐ | |
| 12 | Cantlin Inn | __x__ | ☐ | ☐ | |
| 13 | Erdrick's Cave | __x__ | ☐ | ☐ | |
| 14 | Mountain Cave | __x__ | ☐ | ☐ | |
| 15 | Garin's Grave | __x__ | ☐ | ☐ | |
| 16 | Swamp Cave | __x__ | ☐ | ☐ | |
| 17 | Southern Cave | __x__ | ☐ | ☐ | |
| 18 | Charlock Castle Level 1 | __x__ | ☐ | ☐ | |
| 19 | Charlock Castle Level 2 | __x__ | ☐ | ☐ | |
| 20 | Charlock Castle Level 3 | __x__ | ☐ | ☐ | |
| 21 | Charlock Throne Room | __x__ | ☐ | ☐ | |

### Verification Method

1. Load ROM and enter each location
2. Walk through entire map
3. Compare tile placement with extracted PNG/JSON
4. Note any discrepancies

**Map Verification Steps:**
- [ ] Wall tiles match extracted data
- [ ] Floor tiles match extracted data
- [ ] Door placements correct
- [ ] Stair placements correct
- [ ] Treasure chest locations correct
- [ ] NPC positions match

---

## Text & Dialog Verification

**Purpose:** Verify text encoding, dialogs, and compression  
**Extracted Data:** `extracted_assets/text/*.json`

### Text Categories

#### NPC Dialogs

- [ ] King Lorik's throne room speech
- [ ] Princess Gwaelin's dialog
- [ ] Gwaelin's "Dost thou love me?" question
- [ ] Shop keeper greetings
- [ ] Inn keeper "Welcome to the Inn" dialog
- [ ] Guard dialogs (hints and lore)
- [ ] Wise Man dialogs
- [ ] Random townspeople gossip

#### Item Descriptions

- [ ] Herb description in menu
- [ ] Torch description
- [ ] Key item descriptions (Token, Love, etc.)
- [ ] Weapon descriptions in shops
- [ ] Armor descriptions in shops

#### System Messages

- [ ] "A Slime draws near! Command?" battle prompt
- [ ] "Thou art dead" game over message
- [ ] Level up messages
- [ ] Spell learning messages
- [ ] Status ailment messages

#### Special Text

- [ ] Dragonlord's final speech
- [ ] Ending text sequence
- [ ] "Thy experience blessed thee with added power!"
- [ ] "The spell will not work!" messages

### Encoding Verification

**Character Map (0x00-0x7F):**
- [ ] All alphabet characters (A-Z) decode correctly
- [ ] Numbers (0-9) decode correctly
- [ ] Punctuation (.,!?') decodes correctly
- [ ] Special characters decode correctly

**Word Substitutions (0x80-0x8F):**
- [ ] Common words compressed (SWORD, STAFF, etc.)
- [ ] Word substitution table matches ROM
- [ ] Compression saves expected bytes

**Control Codes (0xF0-0xFF):**
- [ ] 0xFC = Player name insertion
- [ ] 0xFD = Wait for button press
- [ ] 0xFE = Line break
- [ ] 0xFF = String terminator

---

## Graphics Verification

**Purpose:** Verify sprite sheets, palettes, and CHR tiles  
**Extracted Data:** `extracted_assets/graphics/*.png`

### Sprite Sheets (18 Total)

| Sheet Name | Tiles | Palette | Verified | Status | Notes |
|------------|-------|---------|----------|--------|-------|
| hero_sprites | 16 | character | ☐ | | Hero walking animations |
| monster_sprites | 64 | monster | ☐ | | 252 tiles, 19 definitions, 39 monsters |
| npc_sprites | 32 | character | ☐ | | Townspeople, guards, king |
| items_equipment | 16 | menu | ☐ | | Weapons, armor, treasures |
| ui_elements | 16 | menu | ☐ | | Cursors, borders, boxes |
| font_text | 112 | dialog | ☐ | | Characters, numbers, symbols |
| overworld_terrain | 64 | overworld | ☐ | | Grass, trees, mountains |
| town_buildings | 64 | town | ☐ | | Buildings, roads, doors |
| dungeon_tiles | 64 | dungeon | ☐ | | Walls, floors, stairs |
| battle_backgrounds | 64 | battle | ☐ | | Battle scene tiles |
| castle_interior | 64 | town | ☐ | | Castle walls, throne |
| water_tiles | 32 | overworld | ☐ | | Ocean, rivers, bridges |
| mountain_tiles | 32 | overworld | ☐ | | Mountain peaks, caves |
| special_tiles | 16 | overworld | ☐ | | Signs, barriers, rainbow bridge |
| menu_borders | 16 | menu | ☐ | | Command window frames |
| extended_font | 48 | dialog | ☐ | | Additional characters |
| decorative_elements | 32 | town | ☐ | | Furniture, decorations |
| unused_tiles | 32 | menu | ☐ | | Blank/unused CHR space |

### Palette Verification

**8 NES Palettes:**
1. [ ] Overworld palette (greens, browns, blues)
2. [ ] Dungeon palette (grays, purples, blacks)
3. [ ] Town palette (browns, reds, tans)
4. [ ] Battle palette (varied for different environments)
5. [ ] Menu palette (whites, blues, blacks)
6. [ ] Character palette (skin tones, hair, clothing)
7. [ ] Monster palette (varied creature colors)
8. [ ] Dialog palette (white text, blue background)

### CHR Tile Verification

- [ ] All 1024 tiles (0x000-0x3FF) extracted correctly
- [ ] Tile 0x00-0x3F: Monster sprites (64 tile slots)
- [ ] Tile 0x40-0x4F: Hero sprites (16 tiles)
- [ ] Tile 0x50-0x6F: NPC sprites (32 tiles)
- [ ] Tile 0x70-0x7F: Items/equipment (16 tiles)
- [ ] Tile 0x80-0x8F: UI elements (16 tiles)
- [ ] Tile 0x90-0xFF: Font/text (112 tiles)
- [ ] Tile 0x100-0x3FF: Background tiles (768 tiles)

**Sprite Sharing Verification:**
- [ ] SlimeSprts (8 tiles) used by: Slime, Red Slime, Metal Slime
- [ ] DrakeeSprts (10 tiles) used by: Drakee, Magidrakee, Drakeema
- [ ] GhstSprts (13 tiles) used by: Ghost, Poltergeist, Specter
- [ ] WolfSprts (30 tiles) used by: Wolf, Wolflord, Werewolf
- [ ] GolemSprts (31 tiles) used by: Golem, Goldman, Stoneman

**Reference:** See `extracted_assets/reports/monster_sprite_allocation.md` for complete sprite sharing details

---

## ROM Modification Testing

**Purpose:** Verify ROM modifications work correctly

### Pre-Modification Checks

- [ ] Original ROM SHA-256 verified
- [ ] Backup ROM created in `build/backup/`
- [ ] Modified data validated before reinsertion
- [ ] Modification report generated

### Modification Testing

#### Monster Stat Modifications

Test Case: Increase Slime HP from 3 to 10
- [ ] Modify `monsters.json` entry for Slime
- [ ] Run reinsertion script
- [ ] Load modified ROM
- [ ] Encounter Slime in battle
- [ ] Verify Slime has 10 HP
- [ ] Defeat Slime and verify XP/Gold unchanged (unless also modified)

#### Spell MP Cost Modifications

Test Case: Change HEAL MP cost from 4 to 2
- [ ] Modify `spells.json` entry for HEAL
- [ ] Run reinsertion script
- [ ] Load modified ROM
- [ ] Check HEAL in spell menu
- [ ] Verify MP cost shows 2
- [ ] Cast HEAL and verify only 2 MP consumed

#### Item Price Modifications

Test Case: Change Copper Sword price from 180G to 100G
- [ ] Modify `items.json` entry for Copper Sword
- [ ] Run reinsertion script
- [ ] Load modified ROM
- [ ] Visit weapon shop
- [ ] Verify Copper Sword costs 100G

### Complex Modification Tests

#### Hard Mode ROM Hack (example_rom_hack.py)

- [ ] Run `python tools/example_rom_hack.py`
- [ ] Verify 62 modifications applied
- [ ] Load `build/dragon_warrior_hard_mode.nes`
- [ ] Test monster difficulty increases
- [ ] Test item price increases
- [ ] Test spell MP cost increases
- [ ] Verify game is beatable but harder

#### Custom Modifications

Your custom modification:
- [ ] Description: _______________________________
- [ ] Files modified: _____________________________
- [ ] Expected result: ____________________________
- [ ] Actual result: ______________________________
- [ ] Status: ☐ Pass ☐ Fail ☐ Partial

---

## Final Validation

### Build System Verification

- [ ] `build.ps1` executes without errors
- [ ] `build_rom.ps1` executes without errors
- [ ] `dragon_warrior_build.py` executes without errors
- [ ] Output ROM generated in `build/`
- [ ] Build reports created in `build/reports/`
- [ ] Verification reports created in `verification_reports/`

### ROM Integrity Checks

- [ ] Output ROM size = 81,936 bytes (same as original)
- [ ] Header bytes 0x00-0x0F unchanged
- [ ] PRG-ROM checksum matches (if no code changes)
- [ ] CHR-ROM checksum matches (if no graphics changes)
- [ ] ROM loads in emulator without errors
- [ ] No graphical corruption visible
- [ ] No crash bugs encountered

### Playthrough Testing

**Quick Playthrough (30 minutes):**
- [ ] Start new game
- [ ] Talk to King Lorik
- [ ] Exit castle
- [ ] Enter Brecconary
- [ ] Buy equipment
- [ ] Fight 10 random battles
- [ ] Level up at least once
- [ ] Enter dungeon
- [ ] Use all spells
- [ ] Return to castle
- [ ] Save game

**Full Playthrough (8-12 hours):**
- [ ] Complete all quests
- [ ] Visit all towns
- [ ] Explore all dungeons
- [ ] Collect all key items
- [ ] Defeat Dragonlord
- [ ] Watch ending sequence
- [ ] No game-breaking bugs encountered

### Documentation Verification

- [ ] README.md up to date
- [ ] All tools documented in `docs/`
- [ ] Changelog updated with modifications
- [ ] Screenshots captured for verification
- [ ] Bug reports filed for any issues

---

## Verification Summary

**Date Completed:** __________________  
**Completed By:** __________________  
**ROM Version:** __________________

### Results

- **Total Tests:** ______
- **Passed:** ______
- **Failed:** ______
- **Partial:** ______

### Critical Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Minor Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Verification Status

☐ **VERIFIED** - All tests passed, ROM ready for release  
☐ **PARTIAL** - Most tests passed, minor issues acceptable  
☐ **FAILED** - Critical issues found, ROM needs fixes  
☐ **IN PROGRESS** - Verification incomplete

### Next Steps

- [ ] Fix critical issues
- [ ] Re-test failed items
- [ ] Update documentation
- [ ] Create release build
- [ ] Publish ROM hack (if applicable)

---

## Notes

Use this section for additional observations, edge cases, or testing methodology refinements.

**Additional Notes:**

_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

---

**End of Verification Checklist**
