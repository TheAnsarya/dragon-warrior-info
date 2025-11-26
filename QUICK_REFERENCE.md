# Dragon Warrior ROM Hacking - Quick Reference

## Essential Tools Cheat Sheet

### 🔍 Analysis & Inspection
```bash
# Analyze ROM
python tools/rom_metadata_analyzer.py rom.nes

# Find duplicates
python tools/tileset_manager.py rom.nes --find-duplicates

# Show stats
python tools/character_editor.py rom.nes --show-all
```

### 📝 Text Editing
```bash
# Search text
python tools/dialogue_editor.py rom.nes --search "text"

# Replace text
python tools/dialogue_editor.py rom.nes --replace "old" "new" -o new.nes

# Optimal DTE
python tools/dialogue_editor.py rom.nes --optimize-dte
```

### ⚔️ Enemy Editing
```bash
# List enemies
python tools/enemy_ai_editor.py rom.nes --list

# Edit enemy
python tools/enemy_ai_editor.py rom.nes --enemy "Slime" --hp 20 -o new.nes

# Balance check
python tools/enemy_ai_editor.py rom.nes --analyze-balance
```

### 🎒 Item Editing
```bash
# List items
python tools/item_shop_editor.py rom.nes --list-items

# Edit item
python tools/item_shop_editor.py rom.nes --item "Copper Sword" --attack 15 -o new.nes

# Show shops
python tools/item_shop_editor.py rom.nes --list-shops
```

### ✨ Spell Editing
```bash
# List spells
python tools/spell_editor.py rom.nes --list

# Edit spell
python tools/spell_editor.py rom.nes --spell "Heal" --power 20 -o new.nes

# Analyze magic
python tools/spell_editor.py rom.nes --analyze-progression
```

### 📈 Character Stats
```bash
# Show levels
python tools/character_editor.py rom.nes --show-all

# Edit level
python tools/character_editor.py rom.nes --level 10 --hp 60 -o new.nes

# Rebalance XP
python tools/character_editor.py rom.nes --rebalance-xp --difficulty easier -o new.nes
```

### 🎨 Graphics
```bash
# Export pattern table
python tools/tileset_manager.py rom.nes --export-pattern-table 0 --output tiles.png

# Extract monsters
python tools/sprite_editor_advanced.py rom.nes --extract-monsters output/

# Optimize tileset
python tools/tileset_manager.py rom.nes --optimize
```

### 🗺️ Map Tools
```bash
# Render map
python tools/map_editor.py rom.nes --render-world world.png

# Show encounters
python tools/map_editor.py rom.nes --show-encounters

# List warps
python tools/map_editor.py rom.nes --list-warps
```

### 🎵 Music
```bash
# Extract all
python tools/music_editor_advanced.py rom.nes --extract-all music/

# Export NSF
python tools/music_editor_advanced.py rom.nes --export-nsf music.nsf

# Export MIDI
python tools/music_editor_advanced.py rom.nes --track overworld --export-midi track.mid
```

### 🔧 Patching
```bash
# Create patch
python tools/binary_patch_tool.py original.nes modified.nes --create patch.bps --format bps

# Apply patch
python tools/binary_patch_tool.py rom.nes patch.bps --apply

# Inspect patch
python tools/binary_patch_tool.py patch.bps --inspect
```

### ✅ Validation
```bash
# Validate save
python tools/game_state_validator.py save.sav

# Strict check
python tools/game_state_validator.py save.sav --level strict

# Auto-repair
python tools/game_state_validator.py save.sav --repair -o fixed.sav
```

---

## Common Workflows

### Complete Hack Pipeline
```bash
# 1. Backup
cp original.nes backup.nes

# 2. Make changes
python tools/enemy_ai_editor.py original.nes --enemy "Slime" --hp 20 -o mod.nes
python tools/spell_editor.py mod.nes --spell "Heal" --power 15 -o mod.nes

# 3. Create patch
python tools/binary_patch_tool.py original.nes mod.nes --create myhack.bps --format bps

# 4. Validate
python tools/rom_metadata_analyzer.py mod.nes
```

### Balance Testing
```bash
# Check all systems
python tools/enemy_ai_editor.py rom.nes --analyze-balance
python tools/item_shop_editor.py rom.nes --analyze-balance
python tools/spell_editor.py rom.nes --analyze-balance
python tools/character_editor.py rom.nes --analyze
```

### Graphics Extraction
```bash
# Extract everything
python tools/tileset_manager.py rom.nes --extract-all gfx/tiles/
python tools/sprite_editor_advanced.py rom.nes --extract-monsters gfx/monsters/
python tools/map_editor.py rom.nes --render-world gfx/world.png
```

---

## Quick Stats Reference

### Dragon Warrior Data
- **Enemies:** 39 total
- **Items:** 38 (9 weapons, 7 armor, 6 shields, 15 tools)
- **Spells:** 10 player spells
- **Max Level:** 30
- **World Map:** 120×120 tiles
- **CHR-ROM:** 16KB (1024 tiles, 4 pattern tables)

### Important Offsets
- **CHR-ROM:** 0x10010
- **Enemy Stats:** 0x5E9D
- **Level XP:** 0x6023
- **HP/MP/STR/AGI:** 0x6080-0x61F3
- **Dialogue:** 0x36A0-0x5FFF

### Key Formulas
- **Damage:** Random(0-255) × STR ÷ DEF ÷ 2
- **Hit:** 1 - (Enemy AGI ÷ (2 × Player AGI))
- **Critical:** 1/32 (3.125%)
- **Heal:** Random(10, 17)
- **Healmore:** Random(85, 100)

---

## Tool Output Formats

| Tool | Exports |
|------|---------|
| ROM Metadata | JSON, XML, TXT |
| Tileset Manager | PNG (tiles) |
| Dialogue Editor | TXT (strings) |
| Enemy AI | JSON |
| Item Shop | JSON |
| Spell Editor | JSON |
| Character | JSON |
| Map Editor | PNG, JSON |
| Music | NSF, MIDI |
| Patch Tool | IPS, BPS |

---

## Installation

```bash
# Clone repository
git clone <repo-url>
cd dragon-warrior-info

# Install dependencies
pip install -r requirements.txt

# Test tools
python tools/rom_metadata_analyzer.py test.nes
```

---

## Getting Help

```bash
# All tools support --help
python tools/<tool-name>.py --help

# Examples:
python tools/enemy_ai_editor.py --help
python tools/spell_editor.py --help
```

---

**Quick Reference v1.0**
For full documentation see `TOOLS_DOCUMENTATION.md`
