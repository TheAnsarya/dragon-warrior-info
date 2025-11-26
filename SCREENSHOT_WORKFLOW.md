# Dragon Warrior Screenshot Verification Workflow

**Version:** 1.0  
**Created:** 2024-11-25  
**Purpose:** Systematic screenshot capture and comparison for ROM hacking verification

---

## Table of Contents

1. [Overview](#overview)
2. [Equipment & Setup](#equipment--setup)
3. [Screenshot Directory Structure](#screenshot-directory-structure)
4. [Monster Verification Screenshots](#monster-verification-screenshots)
5. [Spell Verification Screenshots](#spell-verification-screenshots)
6. [Item & Shop Verification Screenshots](#item--shop-verification-screenshots)
7. [Map Verification Screenshots](#map-verification-screenshots)
8. [Text & Dialog Verification Screenshots](#text--dialog-verification-screenshots)
9. [Graphics Comparison Screenshots](#graphics-comparison-screenshots)
10. [Screenshot Comparison Tools](#screenshot-comparison-tools)
11. [Verification Workflow](#verification-workflow)

---

## Overview

This document provides detailed instructions for capturing game screenshots to verify:
- Data extraction accuracy (original ROM vs extracted JSON/PNG)
- ROM modification integrity (original ROM vs modified ROM)
- Build system correctness (extracted data → reinsertion → playable ROM)

**Verification Principle:**
```
Original ROM Screenshot → Extract Data → Modify Data → Reinsert Data → Modified ROM Screenshot → Compare
```

Screenshots serve as **ground truth** for validating automated extraction and reinsertion processes.

---

## Equipment & Setup

### Required Tools

#### Emulator (Choose One)

**FCEUX (Recommended for Screenshots)**
- Download: https://fceux.com/
- Windows: fceux.exe
- Features: Built-in screenshot, save states, Lua scripting
- Screenshot hotkey: F12 (default)
- Save state: F5 (save), F7 (load)

**Mesen (Recommended for Accuracy)**
- Download: https://www.mesen.ca/
- Features: High accuracy, debugging tools, HD packs
- Screenshot hotkey: F11
- Save state: F5 (save), F7 (load)

**Nestopia**
- Alternative option
- Screenshot: F12
- Save state: F5/F7

#### Image Comparison Tools

**ImageMagick (Command Line)**
```powershell
# Install via Chocolatey
choco install imagemagick

# Compare two screenshots
magick compare original.png modified.png diff.png
```

**DiffImg (GUI)**
- Download: https://diffimg.com/
- Drag and drop two images
- Highlights pixel differences

**Beyond Compare**
- Download: https://www.scootersoftware.com/
- Professional file/image comparison
- Side-by-side view with highlighting

#### Screenshot Organization

**Directory Structure:** `verification/screenshots/`

```
verification/
├── screenshots/
│   ├── original/           # Original ROM screenshots
│   │   ├── monsters/
│   │   ├── spells/
│   │   ├── items/
│   │   ├── maps/
│   │   ├── text/
│   │   └── graphics/
│   ├── modified/           # Modified ROM screenshots
│   │   ├── monsters/
│   │   ├── spells/
│   │   ├── items/
│   │   ├── maps/
│   │   ├── text/
│   │   └── graphics/
│   ├── comparison/         # Diff images
│   │   └── (auto-generated)
│   └── notes/              # Annotation images
│       └── (marked-up screenshots)
```

### Emulator Configuration

#### FCEUX Setup

1. **Load ROM:**
   - File → Open ROM
   - Select `roms/dragon_warrior_original.nes`

2. **Configure Screenshot Settings:**
   - Config → Screenshot Options
   - Format: PNG
   - Directory: `verification/screenshots/original/`
   - Naming: `dw_YYYYMMDD_HHMMSS.png`

3. **Save State Setup:**
   - Create save state folder: `verification/save_states/`
   - F5 to save, F7 to load
   - Name states descriptively: `tantegel_throne.fc0`

4. **Cheat Codes (Optional):**
   - Tools → Cheats
   - Add GameGenie codes for testing
   - Example: Force encounters, max gold, level up

#### Mesen Setup

1. **Load ROM:**
   - File → Open
   - Select Dragon Warrior ROM

2. **Screenshot Configuration:**
   - Tools → Preferences → Screenshots
   - Format: PNG
   - Output: `verification/screenshots/original/`

3. **Debugging Tools:**
   - Tools → Debugger (for memory inspection)
   - Tools → Memory Viewer (verify data offsets)
   - Tools → Event Viewer (track game events)

### Game Preparation

**Required Save States:**

Create save states at key game checkpoints:

1. **`01_new_game.sav`** - Fresh game start
2. **`02_level_3_brecconary.sav`** - Level 3, in Brecconary, 200G
3. **`03_level_10_equipment.sav`** - Level 10, good equipment
4. **`04_all_spells.sav`** - Hero has all spells learned
5. **`05_endgame.sav`** - Level 20, Erdrick equipment, ready for Dragonlord
6. **`06_pre_dragonlord.sav`** - In Charlock throne room

**Cheat Codes for Testing:**

```
# Max Gold (GameGenie)
AAAAAA + AAAAAA = 65535 Gold

# No Random Encounters (GameGenie)
GZEUATVG

# Max HP (GameGenie)
NYXTVISE

# Walk Through Walls (GameGenie)
ASAAASPA
```

---

## Screenshot Directory Structure

### Naming Convention

**Format:** `{category}_{subject}_{detail}_{state}.png`

**Examples:**
- `monster_00_slime_battle.png` - Slime in battle
- `monster_00_slime_stats.png` - Slime stats display
- `spell_00_heal_menu.png` - HEAL spell in menu
- `spell_00_heal_casting.png` - HEAL being cast
- `item_15_coppersword_shop.png` - Copper Sword in shop
- `map_00_tantegel_throne_overview.png` - Tantegel throne room
- `text_01_king_lorik_dialog1.png` - King's first dialog
- `text_01_king_lorik_dialog2.png` - King's second dialog

### Directory Organization

```
verification/screenshots/
├── original/
│   ├── monsters/
│   │   ├── battle/                 # In-battle screenshots
│   │   │   ├── monster_00_slime_battle.png
│   │   │   ├── monster_01_redslime_battle.png
│   │   │   └── ... (39 total)
│   │   └── stats/                  # Stat display screenshots
│   │       ├── monster_00_slime_hp.png
│   │       └── ... (39 total)
│   ├── spells/
│   │   ├── menu/                   # Spell menu screenshots
│   │   │   ├── spell_00_heal_menu.png
│   │   │   └── ... (10 total)
│   │   └── effects/                # Spell effect screenshots
│   │       ├── spell_00_heal_effect.png
│   │       └── ... (10 total)
│   ├── items/
│   │   ├── shops/                  # Item shop screenshots
│   │   │   ├── shop_brecconary_weapons.png
│   │   │   ├── shop_brecconary_armor.png
│   │   │   └── ... (5 shops)
│   │   └── inventory/              # Item descriptions
│   │       ├── item_00_herb_desc.png
│   │       └── ... (32 total)
│   ├── maps/
│   │   ├── overviews/              # Full map views
│   │   │   ├── map_00_tantegel_throne.png
│   │   │   └── ... (22 locations)
│   │   └── details/                # Close-up sections
│   │       ├── map_00_tantegel_throne_king.png
│   │       └── ... (detailed areas)
│   ├── text/
│   │   ├── dialogs/                # NPC dialogs
│   │   │   ├── npc_king_lorik_1.png
│   │   │   └── ... (all NPCs)
│   │   └── messages/               # System messages
│   │       ├── battle_encounter.png
│   │       ├── levelup.png
│   │       └── ... (common messages)
│   └── graphics/
│       ├── sprites/                # Sprite comparisons
│       │   ├── hero_walk_north.png
│       │   └── ... (animations)
│       └── tilesets/               # Tileset samples
│           ├── overworld_terrain.png
│           └── ... (tile types)
├── modified/
│   └── (same structure as original/)
└── comparison/
    └── (auto-generated diff images)
```

---

## Monster Verification Screenshots

**Purpose:** Verify all 39 monster stats match extracted JSON data

### Required Screenshots per Monster

1. **Battle Encounter Screen**
   - Shows monster name and sprite
   - File: `monster_{ID}_{name}_battle.png`

2. **Monster HP Display**
   - Shows current/max HP during battle
   - File: `monster_{ID}_{name}_hp.png`

3. **Victory Screen**
   - Shows XP and Gold rewards
   - File: `monster_{ID}_{name}_victory.png`

### Screenshot Capture Method

#### Using Save States + Cheats

**Step 1: Setup**
```
1. Load save state: `02_level_3_brecconary.sav`
2. Apply cheat code to force specific monster encounter
3. Exit town to overworld
4. Wait for encounter
```

**Step 2: Capture Battle Screen**
```
1. Monster appears: "A {Name} draws near! Command?"
2. Press F12 to capture screenshot
3. Verify monster sprite visible
4. Save as: monster_{ID}_{name}_battle.png
```

**Step 3: Capture HP Display**
```
1. Select "FIGHT" command
2. Hero attacks, damage dealt
3. Monster HP bar visible
4. Press F12 to capture
5. Save as: monster_{ID}_{name}_hp.png
```

**Step 4: Capture Victory Screen**
```
1. Defeat monster
2. "Thou hast done well in defeating the {Name}!"
3. XP/Gold rewards displayed
4. Press F12 to capture
5. Save as: monster_{ID}_{name}_victory.png
```

### Monster Screenshot Checklist

| ID | Monster Name | Battle | HP | Victory | Notes |
|----|--------------|--------|-----|---------|-------|
| 00 | Slime | ☐ | ☐ | ☐ | |
| 01 | Red Slime | ☐ | ☐ | ☐ | |
| 02 | Drakee | ☐ | ☐ | ☐ | |
| 03 | Ghost | ☐ | ☐ | ☐ | |
| 04 | Magician | ☐ | ☐ | ☐ | |
| 05 | Magidrakee | ☐ | ☐ | ☐ | |
| 06 | Scorpion | ☐ | ☐ | ☐ | |
| 07 | Druin | ☐ | ☐ | ☐ | |
| 08 | Poltergeist | ☐ | ☐ | ☐ | |
| 09 | Droll | ☐ | ☐ | ☐ | |
| 10 | Drakeema | ☐ | ☐ | ☐ | |
| 11 | Skeleton | ☐ | ☐ | ☐ | |
| 12 | Warlock | ☐ | ☐ | ☐ | |
| 13 | Metal Scorpion | ☐ | ☐ | ☐ | |
| 14 | Wolf | ☐ | ☐ | ☐ | |
| 15 | Wraith | ☐ | ☐ | ☐ | |
| 16 | Metal Slime | ☐ | ☐ | ☐ | Often flees, may need multiple attempts |
| 17 | Specter | ☐ | ☐ | ☐ | |
| 18 | Wolflord | ☐ | ☐ | ☐ | |
| 19 | Druinlord | ☐ | ☐ | ☐ | |
| 20 | Drollmagi | ☐ | ☐ | ☐ | |
| 21 | Wyvern | ☐ | ☐ | ☐ | |
| 22 | Rouge Scorpion | ☐ | ☐ | ☐ | |
| 23 | Wraith Knight | ☐ | ☐ | ☐ | |
| 24 | Golem | ☐ | ☐ | ☐ | |
| 25 | Goldman | ☐ | ☐ | ☐ | |
| 26 | Knight | ☐ | ☐ | ☐ | |
| 27 | Magiwyvern | ☐ | ☐ | ☐ | |
| 28 | Demon Knight | ☐ | ☐ | ☐ | |
| 29 | Werewolf | ☐ | ☐ | ☐ | |
| 30 | Green Dragon | ☐ | ☐ | ☐ | |
| 31 | Starwyvern | ☐ | ☐ | ☐ | |
| 32 | Wizard | ☐ | ☐ | ☐ | |
| 33 | Axe Knight | ☐ | ☐ | ☐ | |
| 34 | Blue Dragon | ☐ | ☐ | ☐ | |
| 35 | Stoneman | ☐ | ☐ | ☐ | |
| 36 | Armored Knight | ☐ | ☐ | ☐ | |
| 37 | Red Dragon | ☐ | ☐ | ☐ | |
| 38 | Dragonlord Form 1 | ☐ | ☐ | ☐ | Boss fight |

### Sprite Sharing Verification

**Purpose:** Verify sprite sharing documented in `monster_sprite_allocation.md`

**Screenshot Groups:**

1. **SlimeSprts (Shared by 3)**
   - Slime (ID 00)
   - Red Slime (ID 01)
   - Metal Slime (ID 16)
   - **Verification:** Place screenshots side-by-side, compare sprite shapes

2. **DrakeeSprts (Shared by 3)**
   - Drakee (ID 02)
   - Magidrakee (ID 05)
   - Drakeema (ID 10)

3. **GhstSprts (Shared by 3)**
   - Ghost (ID 03)
   - Poltergeist (ID 08)
   - Specter (ID 17)

4. **WolfSprts (Shared by 3)**
   - Wolf (ID 14)
   - Wolflord (ID 18)
   - Werewolf (ID 29)

5. **GolemSprts (Shared by 3)**
   - Golem (ID 24)
   - Goldman (ID 25)
   - Stoneman (ID 35)

**Verification Steps:**
- [ ] Capture all sprite-sharing groups
- [ ] Compare sprites visually (should be identical except palette)
- [ ] Note any unexpected differences
- [ ] Cross-reference with `extracted_assets/reports/monster_sprite_allocation.md`

---

## Spell Verification Screenshots

**Purpose:** Verify MP costs and spell effects for all 10 spells

### Required Screenshots per Spell

1. **Spell Menu Display**
   - Shows spell name and MP cost
   - File: `spell_{ID}_{name}_menu.png`

2. **Spell Casting**
   - Shows spell being cast
   - File: `spell_{ID}_{name}_casting.png`

3. **Spell Effect**
   - Shows spell effect result
   - File: `spell_{ID}_{name}_effect.png`

### Spell Screenshot Checklist

| ID | Spell | Menu | Casting | Effect | MP Cost | Notes |
|----|-------|------|---------|--------|---------|-------|
| 00 | HEAL | ☐ | ☐ | ☐ | __ | HP restoration amount |
| 01 | HURT | ☐ | ☐ | ☐ | __ | Damage dealt to enemy |
| 02 | SLEEP | ☐ | ☐ | ☐ | __ | Enemy falls asleep |
| 03 | RADIANT | ☐ | ☐ | ☐ | __ | Light radius increases |
| 04 | STOPSPELL | ☐ | ☐ | ☐ | __ | Enemy spell blocked |
| 05 | OUTSIDE | ☐ | ☐ | ☐ | __ | Exit dungeon |
| 06 | RETURN | ☐ | ☐ | ☐ | __ | Warp to Tantegel |
| 07 | REPEL | ☐ | ☐ | ☐ | __ | Reduced encounters |
| 08 | HEALMORE | ☐ | ☐ | ☐ | __ | Greater HP restoration |
| 09 | HURTMORE | ☐ | ☐ | ☐ | __ | Greater damage |

### Capture Method

**Step 1: Spell Menu**
```
1. Load save state: `04_all_spells.sav`
2. Press START to open menu
3. Select "SPELL"
4. Cursor on spell (e.g., HEAL)
5. MP cost visible next to spell name
6. Press F12 to capture
7. Save as: spell_{ID}_{name}_menu.png
```

**Step 2: Spell Casting**
```
1. In menu or battle, select spell
2. "Thy MP decreaseth by {cost}!" message appears
3. Press F12 to capture
4. Save as: spell_{ID}_{name}_casting.png
```

**Step 3: Spell Effect**
```
1. Spell animation plays
2. Effect visible (HP restored, enemy damaged, etc.)
3. Press F12 to capture
4. Save as: spell_{ID}_{name}_effect.png
```

---

## Item & Shop Verification Screenshots

**Purpose:** Verify item prices and stats in shops and inventory

### Required Screenshots

#### Shop Screenshots (5 Towns)

1. **Brecconary Shops**
   - Weapon shop: `shop_brecconary_weapons.png`
   - Armor shop: `shop_brecconary_armor.png`
   - Item shop: `shop_brecconary_items.png`

2. **Garinham Shops**
   - Weapon shop: `shop_garinham_weapons.png`
   - Item shop: `shop_garinham_items.png`

3. **Kol Shops**
   - Weapon shop: `shop_kol_weapons.png`
   - Armor shop: `shop_kol_armor.png`

4. **Rimuldar Shops**
   - Weapon shop: `shop_rimuldar_weapons.png`
   - Armor shop: `shop_rimuldar_armor.png`
   - Item shop: `shop_rimuldar_items.png`

5. **Cantlin Shops**
   - Weapon shop: `shop_cantlin_weapons.png`
   - Armor shop: `shop_cantlin_armor.png`

#### Item Description Screenshots

For each of 32 items, capture:
- Inventory view: `item_{ID}_{name}_inventory.png`
- Description (if available): `item_{ID}_{name}_desc.png`
- Equipped status: `item_{ID}_{name}_equipped.png` (for equipment)

### Shop Screenshot Checklist

| Shop Location | Type | Items Visible | Prices Verified | Screenshot | Status |
|---------------|------|---------------|-----------------|------------|--------|
| Brecconary | Weapons | Bamboo Pole, Club, Copper Sword | ☐ | ☐ | |
| Brecconary | Armor | Clothes, Leather Armor, Small Shield | ☐ | ☐ | |
| Brecconary | Items | Herb, Torch, Fairy Water | ☐ | ☐ | |
| Garinham | Weapons | Hand Axe | ☐ | ☐ | |
| Garinham | Items | Herb, Key, Torch | ☐ | ☐ | |
| Kol | Weapons | Broad Sword | ☐ | ☐ | |
| Kol | Armor | Chain Mail, Large Shield | ☐ | ☐ | |
| Rimuldar | Weapons | Flame Sword | ☐ | ☐ | |
| Rimuldar | Armor | Half Plate, Full Plate, Magic Armor | ☐ | ☐ | |
| Rimuldar | Items | Dragon's Scale, Wings | ☐ | ☐ | |
| Cantlin | Weapons | (Special items) | ☐ | ☐ | |
| Cantlin | Armor | Silver Shield | ☐ | ☐ | |

### Capture Method

**Shop Prices:**
```
1. Enter town (e.g., Brecconary)
2. Enter shop (e.g., weapon shop)
3. Talk to shopkeeper
4. "We deal in weapons. Dost thou wish to buy?" → YES
5. Item list with prices displayed
6. Press F12 to capture
7. Save as: shop_{town}_{type}.png
```

**Item Descriptions:**
```
1. Open menu → ITEM
2. Cursor on item (e.g., Herb)
3. Press A to view description
4. Description displayed: "An herb to cure 30 HP or less"
5. Press F12 to capture
6. Save as: item_{ID}_{name}_desc.png
```

---

## Map Verification Screenshots

**Purpose:** Verify interior map layouts match extracted map data

### Required Screenshots per Location

1. **Full Map Overview**
   - Hero visible to show scale
   - File: `map_{ID}_{name}_overview.png`

2. **Detailed Sections**
   - Close-ups of specific areas
   - File: `map_{ID}_{name}_{section}.png`
   - Example: `map_00_tantegel_throne_king.png` (king's throne area)

3. **Entry/Exit Points**
   - Doors, stairs, warps
   - File: `map_{ID}_{name}_entry.png`

### Map Screenshot Checklist (22 Locations)

| ID | Location Name | Overview | Details | Entry/Exit | Notes |
|----|---------------|----------|---------|------------|-------|
| 00 | Tantegel Throne Room | ☐ | ☐ | ☐ | King, Princess, stairs |
| 01 | Tantegel Inn | ☐ | ☐ | ☐ | Innkeeper, beds |
| 02 | Tantegel Storage | ☐ | ☐ | ☐ | Chests, items |
| 03 | Brecconary Town | ☐ | ☐ | ☐ | Shops, houses, inn |
| 04 | Brecconary Inn | ☐ | ☐ | ☐ | |
| 05 | Garinham Town | ☐ | ☐ | ☐ | |
| 06 | Garinham Inn | ☐ | ☐ | ☐ | |
| 07 | Kol Town | ☐ | ☐ | ☐ | |
| 08 | Kol Inn | ☐ | ☐ | ☐ | |
| 09 | Rimuldar Town | ☐ | ☐ | ☐ | |
| 10 | Rimuldar Inn | ☐ | ☐ | ☐ | |
| 11 | Cantlin Town | ☐ | ☐ | ☐ | |
| 12 | Cantlin Inn | ☐ | ☐ | ☐ | |
| 13 | Erdrick's Cave | ☐ | ☐ | ☐ | Dark cave, tablets |
| 14 | Mountain Cave | ☐ | ☐ | ☐ | Requires Key |
| 15 | Garin's Grave | ☐ | ☐ | ☐ | Cursed Belt location |
| 16 | Swamp Cave | ☐ | ☐ | ☐ | Erdrick's Armor |
| 17 | Southern Cave | ☐ | ☐ | ☐ | Stones of Sunlight |
| 18 | Charlock Level 1 | ☐ | ☐ | ☐ | |
| 19 | Charlock Level 2 | ☐ | ☐ | ☐ | |
| 20 | Charlock Level 3 | ☐ | ☐ | ☐ | |
| 21 | Charlock Throne Room | ☐ | ☐ | ☐ | Dragonlord battle |

### Capture Method

**Overview Screenshot:**
```
1. Enter location
2. Position hero near center or entrance
3. Ensure maximum map area visible
4. Press F12 to capture
5. Save as: map_{ID}_{name}_overview.png
6. If map too large, capture multiple sections
```

**Detail Screenshot:**
```
1. Walk to specific area (e.g., king's throne)
2. Center area on screen
3. Press F12 to capture
4. Save as: map_{ID}_{name}_{detail}.png
5. Example: map_00_tantegel_throne_stairs.png
```

**Tile-by-Tile Verification:**
- [ ] Compare screenshot with `extracted_assets/maps/{location}.json`
- [ ] Verify tile IDs match visual tiles
- [ ] Check wall placements
- [ ] Check floor patterns
- [ ] Check door/stair locations
- [ ] Check NPC positions

---

## Text & Dialog Verification Screenshots

**Purpose:** Verify text encoding, dialogs, and word compression

### Required Screenshot Categories

#### NPC Dialogs

Capture key NPC conversations:

1. **King Lorik**
   - `text_king_lorik_greeting.png` - Initial greeting
   - `text_king_lorik_quest.png` - Quest description
   - `text_king_lorik_status.png` - Status report dialog

2. **Princess Gwaelin**
   - `text_gwaelin_rescue.png` - "I am Gwaelin, Princess of Tantegel"
   - `text_gwaelin_love.png` - "Dost thou love me?"
   - `text_gwaelin_yes.png` - Response to "YES"
   - `text_gwaelin_no.png` - Response to "NO"

3. **Shopkeepers**
   - `text_shop_greeting.png` - Shop welcome message
   - `text_shop_transaction.png` - Buy/sell confirmation

4. **Inn Keepers**
   - `text_inn_greeting.png` - "Welcome to the Inn"
   - `text_inn_cost.png` - "It costs {price}G per night"

5. **Important NPCs**
   - Wise men
   - Guards with hints
   - Townspeople with lore

#### System Messages

1. **Battle Messages**
   - `text_battle_encounter.png` - "A {Monster} draws near! Command?"
   - `text_battle_victory.png` - Victory message
   - `text_battle_defeat.png` - "Thou art dead"
   - `text_battle_run.png` - Escape messages

2. **Level Up Messages**
   - `text_levelup.png` - "Thy experience blessed thee..."
   - `text_spell_learned.png` - Spell learning message

3. **Item Messages**
   - `text_item_get.png` - "The {Hero} found a {Item}!"
   - `text_item_use.png` - Item usage messages
   - `text_item_cursed.png` - "But thou cannot remove it!"

4. **Special Events**
   - `text_dragonlord_offer.png` - Dragonlord's proposition
   - `text_ending_1.png` - Ending sequence (multiple screenshots)
   - `text_rainbow_bridge.png` - Rainbow bridge creation

### Text Encoding Verification

**Character Set Screenshot:**
```
1. Capture all unique characters in dialogs
2. Create reference sheet: text_charset.png
3. Compare with extracted character map (0x00-0x7F)
4. Verify all characters decode correctly
```

**Word Substitution Screenshot:**
```
1. Find dialogs using word substitutions (0x80-0x8F)
2. Example: "SWORD" compressed to single byte
3. Capture dialog: text_wordsub_sword.png
4. Verify compression working (compare ROM hex vs display)
```

**Control Code Screenshot:**
```
1. Find dialogs with control codes
2. 0xFC = Player name insertion
3. 0xFD = Wait for button press
4. 0xFE = Line break
5. Capture examples of each
```

### Text Screenshot Checklist

| Category | Subject | Screenshot | Verified | Notes |
|----------|---------|------------|----------|-------|
| King | Greeting | ☐ | ☐ | |
| King | Quest | ☐ | ☐ | |
| Gwaelin | Rescue | ☐ | ☐ | |
| Gwaelin | Love Question | ☐ | ☐ | |
| Shop | Greeting | ☐ | ☐ | |
| Inn | Greeting | ☐ | ☐ | |
| Battle | Encounter | ☐ | ☐ | |
| Battle | Victory | ☐ | ☐ | |
| Level Up | Message | ☐ | ☐ | |
| Spell Learn | Message | ☐ | ☐ | |
| Dragonlord | Final Speech | ☐ | ☐ | |
| Ending | Sequence | ☐ | ☐ | Multiple screenshots |

---

## Graphics Comparison Screenshots

**Purpose:** Verify sprite sheets and CHR tiles match extracted graphics

### Sprite Comparison Method

#### Hero Sprites

**Required Screenshots:**
1. Hero walking north: `sprite_hero_north.png`
2. Hero walking south: `sprite_hero_south.png`
3. Hero walking west: `sprite_hero_west.png`
4. Hero walking east: `sprite_hero_east.png`

**Capture:**
```
1. Load save state on overworld
2. Walk in each direction
3. Capture mid-stride for animation frame
4. Compare with extracted sprite sheet: hero_sprites.png
```

#### Monster Sprites

**Reference:** `extracted_assets/reports/monster_sprite_allocation.md`

**Sprite Sharing Verification:**
- [ ] SlimeSprts: Capture Slime, Red Slime, Metal Slime side-by-side
- [ ] DrakeeSprts: Capture Drakee, Magidrakee, Drakeema side-by-side
- [ ] GhstSprts: Capture Ghost, Poltergeist, Specter side-by-side
- [ ] Compare sprite shapes (should be identical except palette)

#### NPC Sprites

**Screenshot Each NPC Type:**
- King
- Princess
- Shopkeeper
- Innkeeper
- Guard
- Wise Man
- Merchant
- Townsperson (various)

#### Tileset Screenshots

**Overworld:**
- Grass tiles
- Tree tiles
- Mountain tiles
- Water tiles
- Bridge tiles
- Town tiles

**Dungeon:**
- Wall tiles
- Floor tiles
- Stair tiles
- Torch tiles

**Town:**
- Building tiles
- Road tiles
- Door tiles
- Roof tiles

### Palette Verification

**Capture Each Palette Context:**
1. `palette_overworld.png` - Overworld colors
2. `palette_dungeon.png` - Dungeon colors
3. `palette_town.png` - Town colors
4. `palette_battle.png` - Battle background colors
5. `palette_menu.png` - Menu/UI colors
6. `palette_character.png` - Hero/NPC colors
7. `palette_monster.png` - Monster colors
8. `palette_dialog.png` - Dialog box colors

**Verification Steps:**
- [ ] Capture screenshot in each palette context
- [ ] Use color picker tool to sample RGB values
- [ ] Compare with extracted palette data
- [ ] Verify NES palette indices (0x00-0x3F)

---

## Screenshot Comparison Tools

### ImageMagick Batch Comparison

**Script:** `verification/compare_screenshots.ps1`

```powershell
# Compare original vs modified screenshots
$original = "verification/screenshots/original"
$modified = "verification/screenshots/modified"
$output = "verification/screenshots/comparison"

Get-ChildItem -Path $original -Recurse -Filter "*.png" | ForEach-Object {
    $relPath = $_.FullName.Substring($original.Length)
    $modPath = Join-Path $modified $relPath
    $outPath = Join-Path $output $relPath
    
    if (Test-Path $modPath) {
        $outDir = Split-Path $outPath -Parent
        if (-not (Test-Path $outDir)) {
            New-Item -ItemType Directory -Path $outDir -Force
        }
        
        # Generate diff image
        magick compare $_.FullName $modPath -highlight-color red $outPath
        
        # Calculate similarity metric
        $metric = magick compare -metric RMSE $_.FullName $modPath null: 2>&1
        Write-Host "$relPath : $metric"
    }
}
```

**Usage:**
```powershell
cd c:\Users\me\source\repos\dragon-warrior-info
.\verification\compare_screenshots.ps1
```

### Manual Comparison Checklist

For each screenshot pair:
- [ ] Open original in left window
- [ ] Open modified in right window
- [ ] Visually compare for differences
- [ ] Note any pixel-level changes
- [ ] Mark as ✅ MATCH or ❌ DIFF

**Acceptable Differences:**
- Palette changes (if intentional)
- Stat modifications (if part of ROM hack)
- Text changes (if part of translation/modification)

**Unacceptable Differences:**
- Graphical corruption
- Missing sprites
- Incorrect tile placement
- Text encoding errors

---

## Verification Workflow

### Phase 1: Original ROM Baseline

**Step 1: Capture Original Screenshots**
```
1. Load original ROM: dragon_warrior_original.nes
2. Create save states at key checkpoints
3. Systematically capture all required screenshots
4. Organize in verification/screenshots/original/
5. Create verification checklist
```

**Estimated Time:** 4-6 hours for complete capture

### Phase 2: Data Extraction Verification

**Step 2: Compare Extracted Data**
```
1. Run extraction tools:
   - tools/organize_chr_tiles.py
   - tools/extract_all_data.py
   - tools/extract_maps_npcs.py
   - tools/extract_text_dialogs.py

2. Compare extracted JSON/PNG with screenshots
3. Verify:
   - Monster stats match battle screenshots
   - Spell MP costs match menu screenshots
   - Item prices match shop screenshots
   - Map tiles match location screenshots
   - Text matches dialog screenshots
   - Graphics match sprite screenshots
```

**Validation:**
- [ ] All 39 monsters verified
- [ ] All 10 spells verified
- [ ] All 32 items verified
- [ ] All 22 maps verified
- [ ] All text categories verified
- [ ] All sprite sheets verified

### Phase 3: ROM Modification Testing

**Step 3: Modify Data**
```
1. Make intended modifications:
   - Edit monsters.json
   - Edit spells.json
   - Edit items.json
   - Edit maps/*.json
   - Edit text/*.json

2. Run reinsertion:
   - tools/reinsert_assets.py
   - or build system (build.ps1)

3. Generate modified ROM:
   - build/dragon_warrior_modified.nes
```

**Step 4: Capture Modified ROM Screenshots**
```
1. Load modified ROM in emulator
2. Use SAME save states as Phase 1
3. Capture screenshots in verification/screenshots/modified/
4. Use identical naming convention
5. Ensure same camera positions/angles
```

**Step 5: Compare Original vs Modified**
```
1. Run compare_screenshots.ps1
2. Review diff images in verification/screenshots/comparison/
3. Verify changes match intended modifications
4. Check for unintended side effects
5. Document all differences
```

### Phase 4: Final Validation

**Step 6: Playthrough Test**
```
1. Play modified ROM from start
2. Encounter all 39 monsters
3. Use all 10 spells
4. Buy/use all 32 items
5. Visit all 22 locations
6. Read all NPC dialogs
7. Complete game
```

**Step 7: Create Verification Report**
```
1. Compile screenshot comparison results
2. Document all verified changes
3. List any discrepancies found
4. Create final approval checklist
5. Sign off on verification
```

---

## Verification Report Template

**Report:** `verification/SCREENSHOT_VERIFICATION_REPORT.md`

```markdown
# Dragon Warrior Screenshot Verification Report

**Date:** _________________
**ROM Version:** _________________
**Verified By:** _________________

## Summary

- **Total Screenshots:** _____
- **Verified Matches:** _____
- **Verified Differences:** _____
- **Errors Found:** _____

## Monster Verification

| Monster | Original | Modified | Status | Notes |
|---------|----------|----------|--------|-------|
| Slime   | ✅       | ✅       | ✅     |       |
| ...     | ...      | ...      | ...    | ...   |

## Spell Verification

| Spell | Original | Modified | Status | Notes |
|-------|----------|----------|--------|-------|
| HEAL  | ✅       | ✅       | ✅     |       |
| ...   | ...      | ...      | ...    | ...   |

## Item Verification

| Item | Original | Modified | Status | Notes |
|------|----------|----------|--------|-------|
| Herb | ✅       | ✅       | ✅     |       |
| ...  | ...      | ...      | ...    | ...   |

## Map Verification

| Location | Original | Modified | Status | Notes |
|----------|----------|----------|--------|-------|
| Tantegel | ✅       | ✅       | ✅     |       |
| ...      | ...      | ...      | ...    | ...   |

## Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

## Final Approval

☐ **APPROVED** - All screenshots verified, ROM ready for release
☐ **CONDITIONALLY APPROVED** - Minor issues acceptable
☐ **REJECTED** - Critical issues found, ROM needs fixes

**Signature:** _________________
**Date:** _________________
```

---

**End of Screenshot Verification Workflow**
