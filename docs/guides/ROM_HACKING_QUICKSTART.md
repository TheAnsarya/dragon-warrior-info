# Dragon Warrior ROM Hacking - Quick Start Guide

**Get started modifying Dragon Warrior in under 10 minutes!**

---

## Prerequisites

✅ **Windows with PowerShell** (for build scripts)
✅ **Python 3.8+** installed
✅ **Git** for version control
✅ **Text editor** (VS Code recommended)
✅ **NES emulator** (Mesen or FCEUX)
✅ **Dragon Warrior (U) PRG1 ROM** (original, unmodified)

---

## Step 1: Fork and Clone (2 minutes)

### Fork the Project

1. Go to https://github.com/TheAnsarya/dragon-warrior-info
2. Click "Fork" button (top right)
3. This creates YOUR copy of the project

### Clone Your Fork

```powershell
# Clone your fork (replace YOUR-USERNAME)
git clone https://github.com/YOUR-USERNAME/dragon-warrior-info.git
cd dragon-warrior-info

# Create a branch for your mod
git checkout -b my-awesome-mod
```

---

## Step 2: Setup Environment (3 minutes)

### Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Add Your ROM

```powershell
# Copy your original Dragon Warrior ROM to roms/ folder
# File should be named: Dragon Warrior (U) (PRG1) [!].nes
# Size: 81,936 bytes (80 KB)
```

### Verify Build System

```powershell
# Test build (should create identical ROM)
.\build_rom.ps1

# Check output
ls build\dragon_warrior_rebuilt.nes
# Should be 81,936 bytes
```

✅ If successful, you're ready to start modding!

---

## Step 3: Your First Mod (5 minutes)

### Example: Make Slimes Overpowered

Let's make the humble Slime into a fearsome foe!

#### Option A: Edit JSON (Easiest)

**1. Extract current data:**

```powershell
python tools/extract_all_data.py
```

**2. Edit `extracted_assets/data/monsters.json`:**

Find Slime (ID 0):

```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 3,              ← Change to 100
    "strength": 5,        ← Change to 50
    "agility": 15,        ← Change to 99
    "attack_power": 5,    ← Change to 50
    "defense": 3,         ← Change to 40
    "magic_defense": 1,   ← Change to 30
    "experience_reward": 1,  ← Change to 500
    "gold_reward": 2      ← Change to 200
  }
}
```

**3. Reinsert modified data:**

```powershell
python tools/reinsert_assets.py
# Creates: output/dragon_warrior_modified.nes
```

**4. Test your mod:**

```powershell
# Load in emulator
Start-Process "output\dragon_warrior_modified.nes"

# Try fighting a Slime - watch out! 💀
```

#### Option B: Edit Assembly (Advanced)

**1. Open `source_files/Bank01.asm`**

**2. Find the monster data table (around line 4000):**

```assembly
;Enemy $00-Slime.
;             Att  Def   HP  Spel Agi  Mdef Exp  Gld
L9E4B:  .byte $05, $03, $03, $00, $0F, $01, $01, $02
```

**3. Change the values:**

```assembly
;Enemy $00-Slime - OVERPOWERED VERSION!
;             Att  Def   HP  Spel Agi  Mdef Exp  Gld
L9E4B:  .byte $32, $28, $64, $00, $63, $1E, $F4, $C8
```

(Hex: $32=50, $28=40, $64=100, $63=99, $1E=30, $F4=244, $C8=200)

**4. Rebuild ROM:**

```powershell
.\build_rom.ps1

# Output: build\dragon_warrior_rebuilt.nes
```

**5. Test:**

```powershell
Start-Process "build\dragon_warrior_rebuilt.nes"
```

---

## Common Modifications

### Change Weapon Stats

**File:** `source_files/Bank01.asm`

**Search for:** `WpnAtkTbl` or `ToolEffectsTbl`

**Example - Make Club stronger:**

```assembly
WpnAtkTbl:
    .byte $02  ; Bamboo Pole (unchanged)
    .byte $0A  ; Club (was $04, now $0A = 10 attack)
    .byte $0F  ; Copper Sword
    ; ... etc
```

**Rebuild and test!**

### Change Spell MP Costs

**File:** `extracted_assets/data/spells.json`

```json
{
  "0": {
    "name": "HEAL",
    "mp_cost": 4   ← Change to 1 for cheap healing
  }
}
```

### Modify Dialog

**File:** `source_files/Bank02.asm`

**Search for:** `TextBlock1` through `TextBlock19`

**Example - Change king's greeting:**

```assembly
; Original:
TextBlock1Entry0:
    .text "Welcome to Alefgard,", LINE
    .text HERO, ".", END

; Modified:
TextBlock1Entry0:
    .text "Greetings, mighty warrior!", LINE
    .text "The kingdom needs you.", END
```

**Note:** Text uses special encoding - see `extracted_assets/text/` for character map

### Change Graphics

**Files:** `extracted_assets/chr_organized/sprites_monsters_*.png`

**Tools:** GIMP, Aseprite, or any graphics editor

**Process:**

1. Open PNG in graphics editor
2. Edit tiles (remember: 8×8 pixels, 4-color palette)
3. Save PNG
4. *Future:* Use `tools/graphics_reinserter.py` to rebuild CHR-ROM
5. Rebuild ROM

**Current limitation:** Graphics reinsertion tool not yet implemented - edit CHR manually or edit tiles in hex editor

### Modify Maps

**Files:** `extracted_assets/maps/*.json`

**Example - `maps/tantegel_throne_room.json`:**

```json
{
  "id": 1,
  "name": "Tantegel Castle - Throne Room",
  "width": 30,
  "height": 30,
  "tiles": [ [array of tile IDs] ],
  "npcs": [ /* NPC positions */ ]
}
```

**Current limitation:** Map reinsertion tool not yet implemented

---

## Build Your ROM Hack

### Test Thoroughly

```powershell
# Build your final ROM
.\build_rom.ps1

# Play through the game
# Check all your modifications work
# Look for bugs or crashes
```

### Create IPS Patch

```powershell
# Use Lunar IPS or similar tool to create patch
# Compare: original ROM → your modified ROM
# Share .ips file (do NOT share ROM!)
```

### Share Your Mod

**Create a README for your mod:**

```markdown
# My Dragon Warrior Mod

## Changes
- Slimes are now endgame bosses (100 HP, 50 ATK)
- Club does 10 damage instead of 4
- HEAL costs only 1 MP

## Installation
1. Get original Dragon Warrior (U) PRG1 ROM
2. Apply this IPS patch
3. Enjoy!
```

**Share on:**
- ROMhacking.net
- GitHub (your fork with changes)
- Dragon Warrior community forums

---

## What Can You Modify?

### ✅ Easy (JSON Files)

- Monster stats (HP, attack, defense, rewards)
- Spell MP costs
- Item stats (weapon attack, armor defense)

### ⚙️ Moderate (Assembly Editing)

- Dialog text
- Game formulas (damage calculation)
- Battle mechanics
- Level-up stats
- Shop prices
- Enemy AI

### 🔧 Advanced (Binary/CHR Editing)

- Graphics (sprites, tiles, fonts)
- Map layouts
- Music and sound
- Title screen

---

## Quick Reference

### "I want to change..."

| What | Where to Edit | Tool/Method |
|------|---------------|-------------|
| Monster HP/stats | `extracted_assets/data/monsters.json` | Edit JSON + reinsert |
| Weapon attack | `source_files/Bank01.asm` search `WpnAtkTbl` | Edit ASM + rebuild |
| Spell MP cost | `extracted_assets/data/spells.json` | Edit JSON + reinsert |
| Dialog | `source_files/Bank02.asm` search `TextBlock` | Edit ASM + rebuild |
| Monster graphics | `extracted_assets/chr_organized/sprites_monsters_*.png` | Edit PNG + *future tool* |
| Damage formula | `source_files/Bank03.asm` search `CalcPlayerDamage` | Edit ASM + rebuild |
| Maps | `extracted_assets/maps/*.json` | Edit JSON + *future tool* |
| Level-up stats | `source_files/Bank03.asm` search `LevelUp` | Edit ASM + rebuild |

---

## Troubleshooting

### Build Fails

```powershell
# Check Ophis assembler is present
Test-Path "Ophis\ophis.exe"

# Check ROM is correct
Get-FileHash "roms\Dragon Warrior (U) (PRG1) [!].nes"
# Should be specific hash - see ROM_REQUIREMENTS.md
```

### ROM Crashes in Emulator

- Did you exceed any table sizes? (39 monsters max, etc.)
- Did you use invalid values? (stats must be 0-255)
- Did you break address alignment in assembly?

**Debug:**

1. Revert to working version (git checkout)
2. Re-apply changes one at a time
3. Test after each change
4. Find which change causes crash

### Changes Don't Appear

**Using JSON method:**

- Did you run `reinsert_assets.py`?
- Check `output/dragon_warrior_modified.nes` (not `build/`)

**Using ASM method:**

- Did you rebuild with `.\build_rom.ps1`?
- Check `build/dragon_warrior_rebuilt.nes`

---

## Next Steps

### Learn More

- [📖 Complete ROM Hacking Guide](ROM_HACKING_GUIDE.md) - In-depth coverage
- [🔧 Tools Documentation](TOOLS_DOCUMENTATION.md) - All tools reference
- [🗺️ ROM Map](../datacrystal/ROM_MAP.md) - Memory layout
- [📚 Documentation Index](../INDEX.md) - All documentation

### Advanced Topics

- **Text Compression** - How Dragon Warrior stores dialog
- **Bank Switching** - Understanding MMC1 mapper
- **Battle Formulas** - Damage, hit chance, critical hits
- **Graphics Format** - NES CHR-ROM structure
- **Music Engine** - Audio data and sound effects

### Get Help

- **GitHub Issues** - Report bugs or ask questions
- **Documentation** - Comprehensive guides in `docs/`
- **ROM Hacking Forums** - ROMhacking.net community

---

## Example Mod Ideas

🎮 **Difficulty Mods**

- Hard Mode: Boost all enemy stats
- Easy Mode: Reduce enemy HP, increase gold rewards
- Randomizer: Random monster stats

⚔️ **Balance Mods**

- Magic Rebalance: Adjust spell costs and effects
- Weapon Rebalance: Make early weapons more viable
- Economy Mod: Change shop prices

🎨 **Graphics Mods**

- Palette Swap: Change color schemes
- Sprite Replacements: New monster designs
- UI Improvements: Enhanced fonts

📖 **Story Mods**

- Dialog Changes: Rewrite story
- Character Names: Change hero/NPC names
- Alternate Endings: Modify game ending

---

**Ready to create your Dragon Warrior mod? Start with Step 1! 🐉**

*For questions or help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or create a GitHub issue.*
