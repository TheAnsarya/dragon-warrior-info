# Dragon Warrior Unified Editor - Design Specification

**Version:** 1.0  
**Created:** 2024-11-25  
**Purpose:** Complete specification for single-editor ROM hacking tool with tabbed interface

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [User Interface Design](#user-interface-design)
5. [Monster Editor Tab](#monster-editor-tab)
6. [Spell Editor Tab](#spell-editor-tab)
7. [Item Editor Tab](#item-editor-tab)
8. [Map Editor Tab](#map-editor-tab)
9. [Text Editor Tab](#text-editor-tab)
10. [Graphics Editor Tab](#graphics-editor-tab)
11. [Data Flow & File I/O](#data-flow--file-io)
12. [Validation & Error Handling](#validation--error-handling)
13. [Build Integration](#build-integration)
14. [Implementation Plan](#implementation-plan)

---

## Overview

### Purpose

The **Dragon Warrior Unified Editor** is a comprehensive GUI tool for editing all aspects of Dragon Warrior (NES) ROM data through a single, integrated interface. It replaces multiple separate tools with one cohesive application.

### Design Philosophy

**Unified Experience:**
- Single window application
- Tab-based navigation
- Consistent UI/UX across all editors
- Shared undo/redo system
- Integrated validation
- Real-time preview where possible

**Data-Driven:**
- Edit JSON/PNG assets (not raw ROM)
- Auto-save changes to JSON files
- Build system handles ROM reinsertion
- Validation before commit

**User-Friendly:**
- Intuitive table-based editing
- Dropdown selectors for constrained values
- Visual previews (sprites, maps, palettes)
- Keyboard shortcuts
- Search/filter capabilities
- Import/export CSV for batch editing

### Target Users

- ROM hackers creating Dragon Warrior modifications
- Translators editing text/dialogs
- Balance modders adjusting stats
- Map designers creating custom dungeons
- Graphics artists creating sprite variants

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Dragon Warrior Editor                      │
│                    (Main Application)                        │
├─────────────────────────────────────────────────────────────┤
│  MenuBar │ ToolBar │ StatusBar │ UndoRedoStack              │
├─────────────┬───────────────────────────────────────────────┤
│             │                                                │
│   Tab       │            Tab Content Area                    │
│  Widget     │                                                │
│             │   ┌──────────────────────────────────────┐    │
│  ☑ Monster  │   │      Monster Editor Tab              │    │
│  ☐ Spell    │   │   (Table + Sprite Preview Panel)     │    │
│  ☐ Item     │   │                                      │    │
│  ☐ Map      │   └──────────────────────────────────────┘    │
│  ☐ Text     │                                                │
│  ☐ Graphics │   When "Spell" tab clicked:                   │
│             │   ┌──────────────────────────────────────┐    │
│             │   │       Spell Editor Tab               │    │
│             │   │   (Table + Effect Description)       │    │
│             │   │                                      │    │
│             │   └──────────────────────────────────────┘    │
└─────────────┴───────────────────────────────────────────────┘
```

### Class Structure

```python
DragonWarriorEditor (QMainWindow)
│
├── MenuBar
│   ├── File Menu (Open ROM, Save, Export, Exit)
│   ├── Edit Menu (Undo, Redo, Preferences)
│   ├── Tools Menu (Validate Data, Export All, Import CSV)
│   └── Help Menu (Documentation, About)
│
├── ToolBar
│   ├── Quick Save Button
│   ├── Undo/Redo Buttons
│   ├── Validate Button
│   └── Export Button
│
├── TabWidget
│   ├── MonsterEditorTab (QWidget)
│   │   ├── MonsterTableWidget (QTableWidget)
│   │   ├── SpritePreviewPanel (QFrame)
│   │   └── SearchFilterBar (QLineEdit)
│   │
│   ├── SpellEditorTab (QWidget)
│   │   ├── SpellTableWidget (QTableWidget)
│   │   └── EffectDescriptionPanel (QTextEdit)
│   │
│   ├── ItemEditorTab (QWidget)
│   │   ├── ItemTableWidget (QTableWidget)
│   │   └── ItemIconPreviewPanel (QFrame)
│   │
│   ├── MapEditorTab (QWidget)
│   │   ├── LocationSelector (QComboBox)
│   │   ├── TileGrid (Custom QWidget)
│   │   ├── TilePalette (QListWidget)
│   │   └── MapTools (ToolBox)
│   │
│   ├── TextEditorTab (QWidget)
│   │   ├── DialogTree (QTreeWidget)
│   │   ├── TextEditor (QTextEdit)
│   │   ├── CharacterMap (QTableWidget)
│   │   └── EncodingPreview (QLabel)
│   │
│   └── GraphicsEditorTab (QWidget)
│       ├── SpriteSheetSelector (QComboBox)
│       ├── SpriteGrid (Custom QWidget)
│       ├── PaletteSelector (QComboBox)
│       ├── TileEditor (Custom QWidget)
│       └── ColorPicker (QColorDialog)
│
├── StatusBar
│   ├── StatusLabel (file info)
│   ├── ModificationIndicator (unsaved changes)
│   └── ValidationStatus (errors/warnings)
│
└── DataManager
    ├── load_rom_data()
    ├── save_json_data()
    ├── validate_all_data()
    └── export_to_csv()
```

---

## Technology Stack

### Primary Framework: PyQt5

**Why PyQt5:**
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Rich widget library (tables, trees, custom widgets)
- ✅ Professional UI styling
- ✅ Qt Designer for rapid prototyping
- ✅ Excellent documentation
- ✅ Strong community support

**Alternative Considered:**
- Tkinter: Too basic, limited widgets
- wxPython: Less modern, smaller community
- Kivy: Overkill for desktop app
- Web-based (Electron): Unnecessary complexity

### Dependencies

```
requirements.txt:
PyQt5>=5.15.9
Pillow>=10.0.0
numpy>=1.24.0
```

### File Handling

**JSON:** Standard library `json` module  
**PNG:** Pillow (PIL fork)  
**ROM:** Binary file I/O with `struct` module

### Data Validation

**JSON Schema:** `jsonschema` library for data validation  
**Range Checking:** Custom validators for game constraints

---

## User Interface Design

### Main Window Layout

```
┌────────────────────────────────────────────────────────────┐
│ Dragon Warrior Editor - monsters.json                  [_][□][X] │
├────────────────────────────────────────────────────────────┤
│ File  Edit  Tools  Help                                    │ ← MenuBar
├────────────────────────────────────────────────────────────┤
│ 💾 Save | ⎌ Undo | ⎌ Redo | ✓ Validate | 📤 Export       │ ← ToolBar
├────┬───────────────────────────────────────────────────────┤
│ 👾 │ Monster Editor                                       │ │
│ Monster │                                                      │ │
│ ────────┤  ┌─────────────────────────────────────────┐   │ │
│ 🪄 │  │ ID│Name         │HP │Att│Def│Agi│...│XP │Gold│   │ │
│ Spell    │  ├───┼─────────────┼───┼───┼───┼───┼───┼───┤   │ │
│ ────────┤  │ 0│Slime        │ 3│ 5│ 2│ 3│  0│ 1│ 2│   │ │
│ 🗡️ │  │ 1│Red Slime    │ 4│ 7│ 2│ 5│  0│ 2│ 3│   │ │
│ Item     │  │ 2│Drakee       │ 6│ 9│ 6│ 6│  0│ 3│ 5│   │ │
│ ────────┤  │...│...          │...│...│...│...│...│...│...│   │ │
│ 🗺️ │  └─────────────────────────────────────────┘   │ │
│ Map      │                                                      │ │
│ ────────┤  Sprite Preview: [Slime sprite image]             │ │
│ 💬 │                                                      │ │
│ Text     │  Search: [____________] 🔍                          │ │
│ ────────┤                                                      │ │
│ 🎨 │                                                      │ │
│ Graphics │                                                      │ │
├────┴───────────────────────────────────────────────────────┤
│ Status: monsters.json loaded | Modified: Yes | Errors: 0  │ ← StatusBar
└────────────────────────────────────────────────────────────┘
```

### Window Properties

**Size:**
- Default: 1280×720 (HD resolution)
- Minimum: 1024×600
- Resizable: Yes
- Maximizable: Yes

**Theme:**
- Light theme (default)
- Dark theme option (future)
- System theme integration

**Icons:**
- Tab icons (monster, spell, item, etc.)
- Toolbar icons (save, undo, validate)
- Status icons (success, warning, error)

### Color Scheme

**Primary Colors:**
- Blue (#2196F3): Primary actions
- Green (#4CAF50): Success/valid
- Orange (#FF9800): Warnings
- Red (#F44336): Errors
- Gray (#757575): Disabled

**Background:**
- White (#FFFFFF): Main content
- Light gray (#F5F5F5): Panels
- Dark gray (#EEEEEE): Inactive tabs

---

## Monster Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Monster Editor                                [Search: ____🔍]│
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────┐ ┌──────────────────┐│
│ │ Monster Table (Sortable)           │ │ Sprite Preview   ││
│ │                                    │ │                  ││
│ │ ID│Name    │HP│Att│Def│Agi│Spel│...│ │  [Slime sprite]  ││
│ ├──┼────────┼──┼───┼───┼───┼────┤...│ │                  ││
│ │0 │Slime   │3 │5  │2  │3  │0   │...│ │  8x8 tiles       ││
│ │1 │Red Slime│4│7  │2  │5  │0   │...│ │  scaled 4x       ││
│ │2 │Drakee  │6 │9  │6  │6  │0   │...│ │                  ││
│ │...│...     │..│...│...│...│... │...│ │  Palette:        ││
│ │38│DragonL │100│120│120│75│6   │...│ │  [monster]       ││
│ └────────────────────────────────────┘ │                  ││
│ Rows: 39 | Selected: Slime (ID 0)      │ Sprite Source:   ││
│                                         │ SlimeSprts       ││
│ [Edit Selected] [Bulk Edit] [Export CSV]│ (shared by 3)    ││
└──────────────────────────────────────────┴──────────────────┘
```

### Table Columns

| Column | Type | Range | Validator | Description |
|--------|------|-------|-----------|-------------|
| ID | Integer | 0-38 | Read-only | Monster index |
| Name | String | 1-15 chars | AlphaNumeric | Monster name (display only) |
| HP | Integer | 1-255 | Range | Hit Points |
| Attack | Integer | 0-255 | Range | Attack power |
| Defense | Integer | 0-255 | Range | Defense power |
| Agility | Integer | 0-255 | Range | Speed/agility |
| Spell | Integer | 0-9 | Range | Spell ID (0=none) |
| M.Defense | Integer | 0-255 | Range | Magic defense |
| XP | Integer | 0-65535 | Range | Experience reward |
| Gold | Integer | 0-65535 | Range | Gold reward |

### Features

#### Inline Editing
- Click cell to edit
- Tab to next cell
- Enter to save and move down
- ESC to cancel edit
- Validators prevent invalid input

#### Sorting
- Click column header to sort ascending
- Click again for descending
- Shift+Click for multi-column sort

#### Search/Filter
- Search box: filter by name
- Filter by stat range: "HP > 50"
- Regular expression support

#### Sprite Preview
- Displays monster sprite from sprite sheet
- Shows sprite name (e.g., "SlimeSprts")
- Lists monsters sharing same sprite
- Auto-updates when selecting different monster

#### Bulk Edit
- Select multiple rows (Ctrl+Click, Shift+Click)
- Apply percentage increase: "+10% HP to all"
- Apply flat bonus: "+5 Attack to selected"
- Apply multiplier: "×2 XP for all"

#### Import/Export
- Export to CSV: `monsters_export.csv`
- Import from CSV with validation
- Template CSV generation

### Data Validation

**Rules:**
- HP must be > 0 (no zero-HP monsters)
- All stats 0-255 (8-bit constraints)
- XP/Gold 0-65535 (16-bit constraints)
- Spell ID must exist in spell table (0-9)
- Name cannot be empty

**Visual Feedback:**
- 🟢 Green: Valid value
- 🟡 Yellow: Warning (unusual value)
- 🔴 Red: Invalid (blocks save)

---

## Spell Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Spell Editor                                                  │
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────┐ ┌───────────┐│
│ │ ID│Name    │MP│Effect    │Power│Range│Anim││ Spell Icon││
│ ├──┼────────┼──┼──────────┼─────┼─────┼────┤│           ││
│ │0 │HEAL    │4 │Heal      │~30  │Self │0   ││  [icon]   ││
│ │1 │HURT    │2 │Damage    │~10  │Enemy│1   ││           ││
│ │2 │SLEEP   │2 │Status    │0    │Enemy│2   ││ Category: ││
│ │3 │RADIANT │3 │Field     │0    │Radius│3  ││ Recovery  ││
│ │...│...     │..│...       │...  │...  │... ││           ││
│ └────────────────────────────────────────────┘ └───────────┘│
│                                                               │
│ Effect Description:                                           │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ HEAL: Restores HP to the hero. Amount varies by level.  ││
│ │                                                          ││
│ │ Formula: BaseHeal + (Level × HealModifier)              ││
│ │ BaseHeal: ~10 HP                                        ││
│ │ HealModifier: ~2 HP/level                               ││
│ │                                                          ││
│ │ MP Cost: 4 MP per cast                                  ││
│ │ Availability: Learned at Level 3                        ││
│ └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Table Columns

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| ID | Integer | 0-9 | Spell index |
| Name | String | 4-8 chars | Spell name |
| MP Cost | Integer | 0-255 | Mana point cost |
| Effect Type | Dropdown | Enum | Damage/Heal/Buff/Debuff/Field |
| Power | Integer | 0-255 | Effect magnitude |
| Range | Dropdown | Enum | Self/Enemy/All/Radius |
| Animation | Integer | 0-15 | Animation ID |

### Features

#### Effect Type Dropdown
- Damage (HURT, HURTMORE)
- Heal (HEAL, HEALMORE)
- Status (SLEEP, STOPSPELL)
- Field (RADIANT, REPEL)
- Utility (OUTSIDE, RETURN)

#### Description Panel
- Rich text editor
- Formula notation support
- Markdown formatting
- Auto-saves with spell data

#### Spell Icon Preview
- Shows spell icon from sprite sheet
- Category badge (Recovery, Attack, etc.)
- MP cost prominently displayed

---

## Item Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Item Editor                          [Filter: All ▾] [Search]│
├──────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────┐ ┌────────┐│
│ │ID│Name       │Type  │Buy│Sell│+Att│+Def│Slot ││  Icon  ││
│ ├─┼───────────┼──────┼───┼────┼────┼────┼─────┤│        ││
│ │0│Herb       │Item  │24 │12  │  0 │  0 │None ││ [herb] ││
│ │1│Torch      │Item  │8  │4   │  0 │  0 │None ││        ││
│ │15│BambooPole│Weapon│10 │5   │ +2 │  0 │Wpn  ││ Type:  ││
│ │22│Clothes   │Armor │20 │10  │  0 │ +2 │Body ││ Item   ││
│ │29│SmallShld│Shield│90 │45  │  0 │ +4 │Shld ││        ││
│ │...│...       │...   │...│... │... │... │...  ││ Flags: ││
│ └───────────────────────────────────────────────┘ │ None   ││
│ Selected: Herb (ID 0)                              └────────┘│
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Flags: ☐ Equippable ☐ Cursed ☐ Key Item ☐ Quest     ││
│ │ Description: Restores ~30 HP when used               ││
│ │ Shop Locations: Brecconary, Garinham, Rimuldar       ││
│ └──────────────────────────────────────────────────────────┘│
│ [Edit Selected] [Price Calculator] [Export Items]            │
└──────────────────────────────────────────────────────────────┘
```

### Table Columns

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| ID | Integer | 0-31 | Item index |
| Name | String | 1-15 chars | Item name |
| Type | Dropdown | Enum | Weapon/Armor/Shield/Item/Key |
| Buy Price | Integer | 0-65535 | Purchase price in Gold |
| Sell Price | Integer | 0-65535 | Sell price (usually Buy/2) |
| +Attack | Integer | -128 to 127 | Attack bonus (weapons) |
| +Defense | Integer | -128 to 127 | Defense bonus (armor/shields) |
| Equip Slot | Dropdown | Enum | Weapon/Body/Shield/None |

### Features

#### Type Filter
- All Items
- Tools (15 items)
- Weapons (7 items)
- Armor (7 items)
- Shields (3 items)

#### Flags System
- **Equippable:** Can be equipped
- **Cursed:** Cannot be removed once equipped
- **Key Item:** Cannot be sold/dropped
- **Quest Item:** Required for story progress

#### Price Calculator
- Auto-calc sell price (Buy / 2)
- Bulk price adjustment (+10% all weapons)
- Balance analyzer (compare prices)

#### Item Icon Preview
- Shows item sprite from sprite sheet
- Type badge (Weapon, Armor, etc.)
- Equip slot indicator

---

## Map Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Map Editor            [Location: Tantegel Throne Room ▾]      │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌────────────────────────────────┐ ┌───────┐│
│ │ Tile Palette│ │ Map Grid (32×32)               │ │Minimap││
│ │             │ │                                │ │       ││
│ │ [Wall]      │ │ ████████████████████████████   │ │ [map] ││
│ │ [Floor]     │ │ █                          █   │ │       ││
│ │ [Door]      │ │ █    👑                    █   │ │ Zoom: ││
│ │ [Stairs]    │ │ █                          █   │ │ 200%  ││
│ │ [Chest]     │ │ █                          █   │ │       ││
│ │ [NPC]       │ │ █         📦               █   │ │ Grid: ││
│ │ ...         │ │ █                          █   │ │  ON   ││
│ │             │ │ ████████████████████████████   │ │       ││
│ └─────────────┘ └────────────────────────────────┘ └───────┘│
│ Tools: ✏️Pencil 🪣Fill ❌Eraser 🔍Zoom [Layer:BG▾]           │
│ Tile: Wall (0x42) | Pos: (15, 8) | Modified: Yes             │
└──────────────────────────────────────────────────────────────┘
```

### Location Selector

**22 Interior Locations:**
1. Tantegel Throne Room
2. Tantegel Inn
3. Tantegel Storage
4. Brecconary Town
5-22. (All other locations)

### Tile Grid

**Display:**
- Scrollable canvas
- Zoom: 50%, 100%, 200%, 400%
- Grid lines toggle
- Tile IDs overlay (optional)

**Interaction:**
- Click to place tile
- Drag to paint
- Right-click to sample tile
- Scroll wheel to zoom

### Tile Palette

**Categories:**
- Walls
- Floors
- Doors
- Stairs
- Furniture
- NPCs
- Items
- Decorations

**CHR Tile Reference:**
- Loads tiles from CHR-ROM
- Renders with appropriate palette
- Shows tile ID and name

### Map Tools

**Pencil:** Draw individual tiles  
**Fill:** Flood fill area  
**Eraser:** Clear tiles  
**Eyedropper:** Sample tile from map  
**Selection:** Select and move regions  
**Zoom:** Zoom in/out

### Layers

**Background:** Floor, walls, base tiles  
**Objects:** Furniture, chests, decorations  
**NPCs:** Character sprites  
**Collision:** Walkable/blocked tiles (metadata)

### Features

#### Auto-Tile System
- Detect wall patterns
- Auto-connect adjacent walls
- Corner tile selection
- Border tile optimization

#### NPC Placement
- Drag NPCs from palette to map
- Set NPC dialog ID
- Set movement pattern
- Set facing direction

#### Export/Import
- Export map to PNG image
- Export map to JSON (tile IDs)
- Import map from JSON
- Import tileset from PNG

---

## Text Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Text Editor                                                   │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌──────────────────────────────────────┐│
│ │ Dialog Tree     │ │ Text Content                         ││
│ │                 │ │                                      ││
│ │ ▼ NPCs          │ │ King Lorik (Throne Room)             ││
│ │   ► King Lorik  │ │ ┌──────────────────────────────────┐││
│ │   ► Princess    │ │ │ Welcome to Tantegel Castle.      │││
│ │   ► Guards      │ │ │ I am King Lorik.                 │││
│ │ ▼ Shops         │ │ │                                  │││
│ │   ► Brecconary  │ │ │ Brave {HERO}, thou hast come to  │││
│ │   ► Garinham    │ │ │ save our land from the evil      │││
│ │ ▼ System        │ │ │ Dragonlord!                      │││
│ │   ► Battle      │ │ └──────────────────────────────────┘││
│ │   ► Level Up    │ │                                      ││
│ │   ► Game Over   │ │ Encoding Preview:                    ││
│ └─────────────────┘ │ 57 65 6C 63 6F 6D 65 20 74 6F 20... ││
│                     │                                      ││
│                     │ Length: 85 chars | Max: 128          ││
├─────────────────────┴──────────────────────────────────────┤
│ Character Map                                               │
│ ┌───┬───┬───┬───┬───┬───┬───┬───┐ Word Subs:             │
│ │ A │ B │ C │ D │ E │ F │ G │ H │ 0x80: SWORD             │
│ │ I │ J │ K │ L │ M │ N │ O │ P │ 0x81: STAFF             │
│ │ Q │ R │ S │ T │ U │ V │ W │ X │ 0x82: SHIELD            │
│ │ Y │ Z │ . │ , │ ! │ ? │ ' │ - │ ...                     │
│ └───┴───┴───┴───┴───┴───┴───┴───┘                         │
│ Control Codes: 0xFC={HERO} 0xFD={WAIT} 0xFE={NEWLINE}       │
└──────────────────────────────────────────────────────────────┘
```

### Dialog Tree Structure

```
📁 NPCs
  └─ 👑 King Lorik
      ├─ Initial Greeting
      ├─ Quest Assignment
      ├─ Status Report
      └─ Victory Celebration
  └─ 👸 Princess Gwaelin
      ├─ Rescue Dialog
      ├─ Love Question
      └─ Carried Dialog
📁 Shops
  └─ 🏪 Brecconary
      ├─ Weapon Shop
      ├─ Armor Shop
      └─ Inn
📁 System Messages
  └─ ⚔️ Battle
      ├─ Encounter
      ├─ Victory
      ├─ Defeat
      └─ Escape
```

### Features

#### Text Encoding
- Real-time encoding preview
- Character map insertion
- Word substitution support
- Control code insertion

#### Length Validation
- Warning when approaching limit
- Error when exceeding space
- Character counter

#### Search/Replace
- Find text across all dialogs
- Replace text globally
- Regular expression support

#### Import/Export
- Export to CSV for translation
- Import from CSV with validation
- Template generation

---

## Graphics Editor Tab

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Graphics Editor    [Sheet: monster_sprites ▾] [Palette: monster▾]│
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌────────────────────────────────────┐  │
│ │ Sprite Sheets   │ │ Sprite Grid (16 columns)           │  │
│ │                 │ │                                    │  │
│ │ ☑ monster_sprites│ │ [🟢][🔴][🐉][👻][🧙][...64 tiles...]│  │
│ │ ☐ hero_sprites  │ │                                    │  │
│ │ ☐ npc_sprites   │ │ Selected: Tile 0x00 (Slime)        │  │
│ │ ☐ items         │ │                                    │  │
│ │ ...             │ └────────────────────────────────────┘  │
│ └─────────────────┘                                         │
│ ┌──────────────────────────────────────┐ ┌────────────────┐│
│ │ Tile Editor (8×8 pixels, 4 colors)   │ │ Palette Editor ││
│ │                                      │ │                ││
│ │ ████████████████ [Zoom: 8x]          │ │ Color 0: ▓▓▓▓  ││
│ │ ████▒▒▒▒▒▒▒▒████                     │ │ Color 1: ▒▒▒▒  ││
│ │ ██▒▒░░░░░░░░▒▒██                     │ │ Color 2: ░░░░  ││
│ │ ██▒░░██░░██░░▒██                     │ │ Color 3: ████  ││
│ │ ██▒░░░░░░░░░░▒██                     │ │                ││
│ │ ██▒░░░██░░░░░▒██                     │ │ [NES Palette]  ││
│ │ ████▒▒▒▒▒▒▒▒████                     │ │ (Click to edit)││
│ │ ████████████████                     │ └────────────────┘│
│ └──────────────────────────────────────┘                   │
│ Tools: ✏️Pencil 🪣Fill ❌Eraser 🔍Eyedropper [Grid: ON]     │
│ [Export Tile] [Import Tile] [Copy] [Paste]                  │
└──────────────────────────────────────────────────────────────┘
```

### Features

#### Sprite Sheet Selector
- 18 organized sprite sheets
- Preview grid for each sheet
- Tile count indicator

#### CHR Tile Viewer
- All 1024 tiles displayed
- Tile ID overlay
- Palette selector
- Zoom controls

#### Tile Editor
- 8×8 pixel editor
- 4-color NES palette
- Pencil, fill, eraser tools
- Grid toggle
- Zoom: 4x, 8x, 16x

#### Palette Editor
- NES color picker (64 colors)
- Modify 4 colors per palette
- Preview palette on sprites
- Save/load palette files

#### Export/Import
- Export tile to PNG
- Import PNG to tile (8×8, 4-color)
- Export sprite sheet to PNG
- Import sprite sheet from PNG

---

## Data Flow & File I/O

### Data Pipeline

```
ROM File (dragon_warrior.nes)
    ↓
Extract Data (tools/extract_all_data.py)
    ↓
JSON/PNG Assets (extracted_assets/)
    ├─ json/monsters.json
    ├─ json/spells.json
    ├─ json/items.json
    ├─ maps/*.json
    ├─ text/*.json
    └─ graphics/*.png
    ↓
Dragon Warrior Editor (Edit Data)
    ↓
Save to JSON/PNG (Auto-save)
    ↓
Build System (build.ps1 / dragon_warrior_build.py)
    ↓
Reinsert Data (tools/reinsert_assets.py)
    ↓
Modified ROM (build/dragon_warrior_modified.nes)
```

### File Paths

**Data Files:**
```
extracted_assets/
├── json/
│   ├── monsters.json       ← Monster Editor
│   ├── spells.json         ← Spell Editor
│   ├── items.json          ← Item Editor
│   ├── palettes.json       ← Graphics Editor
│   └── metadata.json       ← Editor config
├── maps/
│   ├── tantegel_throne.json    ← Map Editor
│   ├── brecconary_town.json
│   └── ... (22 locations)
├── text/
│   ├── npc_dialogs.json    ← Text Editor
│   ├── system_messages.json
│   └── shop_dialogs.json
└── graphics/
    ├── monster_sprites.png ← Graphics Editor
    ├── hero_sprites.png
    └── ... (18 sprite sheets)
```

### Load/Save Operations

**On Application Start:**
```python
def load_rom_data(self):
    """Load all JSON/PNG data into editor"""
    self.monsters = self.load_json("extracted_assets/json/monsters.json")
    self.spells = self.load_json("extracted_assets/json/spells.json")
    self.items = self.load_json("extracted_assets/json/items.json")
    # ... load all other data
    self.populate_tables()  # Populate UI tables
```

**On Edit:**
```python
def on_cell_changed(self, row, col):
    """Handle table cell edit"""
    new_value = self.table.item(row, col).text()
    if self.validate_value(new_value, row, col):
        self.data[row][col] = new_value
        self.mark_modified()  # Show unsaved indicator
        self.auto_save()      # Save to JSON
```

**On Save:**
```python
def save_all_data(self):
    """Save all modified data to JSON files"""
    self.save_json(self.monsters, "monsters.json")
    self.save_json(self.spells, "spells.json")
    # ... save all modified data
    self.clear_modified_flag()
```

### Auto-Save System

**Behavior:**
- Auto-save every 30 seconds (configurable)
- Save on tab change
- Save on application exit
- Backup before save

**Settings:**
```json
{
  "auto_save_enabled": true,
  "auto_save_interval": 30,
  "backup_on_save": true,
  "max_backups": 10
}
```

---

## Validation & Error Handling

### Validation Levels

**1. Input Validation (Immediate)**
- Type checking (int, string, etc.)
- Range checking (0-255, etc.)
- Length checking (string limits)
- Format checking (alphanumeric, etc.)

**2. Cross-Reference Validation (On Save)**
- Spell IDs exist in spell table
- Item IDs exist in item table
- Map tile IDs exist in tileset
- Character codes valid in encoding table

**3. Logical Validation (On Export)**
- No zero-HP monsters
- No negative prices
- No duplicate IDs
- No circular references

### Error Display

**Visual Indicators:**
- 🟢 **Green Border:** Valid value
- 🟡 **Yellow Border:** Warning (unusual but allowed)
- 🔴 **Red Border:** Error (invalid, blocks save)

**Status Bar Messages:**
- "✓ All data valid" (green)
- "⚠ 3 warnings found" (yellow)
- "❌ 5 errors found - cannot save" (red)

**Error Dialog:**
```
┌─────────────────────────────────────┐
│ ❌ Validation Errors                │
├─────────────────────────────────────┤
│ Monster Tab:                        │
│  • Row 5: HP must be > 0            │
│  • Row 12: Spell ID 15 does not     │
│            exist (max 9)            │
│                                     │
│ Item Tab:                           │
│  • Row 22: Price cannot be negative │
│                                     │
│ [View Details] [Fix Automatically]  │
└─────────────────────────────────────┘
```

### Validation Rules

**Monster Data:**
```python
{
    "hp": {"min": 1, "max": 255},
    "attack": {"min": 0, "max": 255},
    "defense": {"min": 0, "max": 255},
    "agility": {"min": 0, "max": 255},
    "spell": {"min": 0, "max": 9},  # Must exist in spell table
    "m_defense": {"min": 0, "max": 255},
    "xp": {"min": 0, "max": 65535},
    "gold": {"min": 0, "max": 65535}
}
```

**Spell Data:**
```python
{
    "mp_cost": {"min": 0, "max": 255},
    "power": {"min": 0, "max": 255},
    "effect_type": {"enum": ["damage", "heal", "status", "field", "utility"]},
    "range": {"enum": ["self", "enemy", "all", "radius"]}
}
```

**Item Data:**
```python
{
    "buy_price": {"min": 0, "max": 65535},
    "sell_price": {"min": 0, "max": 65535},
    "attack_bonus": {"min": -128, "max": 127},
    "defense_bonus": {"min": -128, "max": 127},
    "type": {"enum": ["weapon", "armor", "shield", "item", "key_item"]},
    "equip_slot": {"enum": ["weapon", "body", "shield", "none"]}
}
```

---

## Build Integration

### Build Pipeline Trigger

**From Editor:**
```python
def build_modified_rom(self):
    """Trigger build process from editor"""
    # 1. Validate all data
    if not self.validate_all_data():
        self.show_error("Fix validation errors before building")
        return
    
    # 2. Save all data
    self.save_all_data()
    
    # 3. Run build script
    result = subprocess.run(
        ["powershell", "-File", "build.ps1"],
        capture_output=True,
        text=True
    )
    
    # 4. Show build results
    if result.returncode == 0:
        self.show_success("ROM built successfully!")
        self.open_rom_in_emulator()
    else:
        self.show_error(f"Build failed:\n{result.stderr}")
```

**Build Menu:**
- **Build ROM** (Ctrl+B): Run full build pipeline
- **Quick Build** (Ctrl+Shift+B): Skip validation
- **Clean Build** (Ctrl+Alt+B): Delete build/ and rebuild
- **Test ROM** (F5): Build and launch emulator

### Emulator Integration

**Settings:**
```json
{
  "emulator_path": "C:/Program Files/FCEUX/fceux.exe",
  "rom_output_path": "build/dragon_warrior_modified.nes",
  "auto_launch_on_build": true
}
```

**Launch Emulator:**
```python
def launch_emulator(self):
    """Launch emulator with modified ROM"""
    emulator = self.settings["emulator_path"]
    rom = self.settings["rom_output_path"]
    subprocess.Popen([emulator, rom])
```

---

## Implementation Plan

### Phase 1: Core Framework (Week 1)

**Tasks:**
- [x] Create PyQt5 project structure
- [x] Design main window layout
- [x] Implement MenuBar, ToolBar, StatusBar
- [x] Create TabWidget framework
- [x] Implement data loading system
- [x] Implement data saving system
- [x] Add undo/redo stack
- [x] Add validation framework

**Deliverables:**
- `dragon_warrior_editor.py` - Main application
- `data_manager.py` - Data I/O handling
- `validators.py` - Validation rules

### Phase 2: Monster & Spell Editors (Week 2)

**Tasks:**
- [x] Implement MonsterEditorTab
- [x] Create monster table widget
- [x] Add sprite preview panel
- [x] Implement sorting/filtering
- [x] Implement SpellEditorTab
- [x] Create spell table widget
- [x] Add effect description panel

**Deliverables:**
- `monster_editor.py`
- `spell_editor.py`

### Phase 3: Item & Map Editors (Week 3)

**Tasks:**
- [x] Implement ItemEditorTab
- [x] Create item table widget
- [x] Add item icon preview
- [x] Implement price calculator
- [x] Implement MapEditorTab
- [x] Create tile grid widget
- [x] Create tile palette widget
- [x] Implement map tools (pencil, fill, etc.)

**Deliverables:**
- `item_editor.py`
- `map_editor.py`
- `tile_grid.py` (custom widget)

### Phase 4: Text & Graphics Editors (Week 4)

**Tasks:**
- [x] Implement TextEditorTab
- [x] Create dialog tree widget
- [x] Create text encoding system
- [x] Add character map
- [x] Implement GraphicsEditorTab
- [x] Create sprite grid widget
- [x] Create tile editor widget
- [x] Create palette editor widget

**Deliverables:**
- `text_editor.py`
- `graphics_editor.py`
- `tile_editor.py` (custom widget)
- `palette_editor.py` (custom widget)

### Phase 5: Polish & Testing (Week 5)

**Tasks:**
- [x] Implement keyboard shortcuts
- [x] Add tooltips and help text
- [x] Implement CSV import/export
- [x] Add error dialogs and confirmations
- [x] Comprehensive testing
- [x] Bug fixes
- [x] Performance optimization
- [x] Documentation

**Deliverables:**
- Fully functional editor
- User manual
- Test report

---

## Appendix: Mock-Up Screenshots

(To be created with Qt Designer or mockup tool)

### Main Window
- Full application window
- All tabs visible
- Sample data loaded

### Monster Editor
- Table with 39 monsters
- Sprite preview panel
- Search/filter in action

### Spell Editor
- Spell table
- Effect description panel
- Spell icon preview

### Item Editor
- Item table with all 32 items
- Type filter active
- Item icon preview

### Map Editor
- Tantegel Throne Room loaded
- Tile palette visible
- Map tools active

### Text Editor
- Dialog tree expanded
- Text content editor
- Character map visible

### Graphics Editor
- Monster sprite sheet loaded
- Tile editor active
- Palette editor visible

---

**End of Unified Editor Design Specification**
