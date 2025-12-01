# Dragon Warrior Modification Examples

Step-by-step tutorials for common ROM modifications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Example 1: Change Monster Stats](#example-1-change-monster-stats)
3. [Example 2: Modify Item Prices](#example-2-modify-item-prices)
4. [Example 3: Edit NPC Dialog](#example-3-edit-npc-dialog)
5. [Example 4: Customize Starting Stats](#example-4-customize-starting-stats)
6. [Example 5: Create a Harder Difficulty](#example-5-create-a-harder-difficulty)
7. [Example 6: Change Shop Inventories](#example-6-change-shop-inventories)
8. [Example 7: Modify Spell Effects](#example-7-modify-spell-effects)
9. [Example 8: Edit Map Encounters](#example-8-edit-map-encounters)

---

## Getting Started

### Prerequisites

1. **Dragon Warrior ROM** (PRG1 version recommended)
2. **Universal Editor** installed
3. **Basic understanding** of hex values

### Running the Editor

```bash
cd dragon-warrior-info
python tools/universal_editor.py
```

### Backup First!

Always backup your ROM before making changes:

```bash
# Windows
copy roms\Dragon_Warrior.nes roms\Dragon_Warrior_backup.nes

# Linux/Mac
cp roms/Dragon_Warrior.nes roms/Dragon_Warrior_backup.nes
```

---

## Example 1: Change Monster Stats

**Goal:** Make Slimes slightly stronger for more challenge.

### Step 1: Open Monster Editor

1. Launch Universal Editor
2. Click the **👾 Monsters** tab
3. Select "Slime" from the list

### Step 2: View Current Stats

```
Slime
━━━━━━━━━━━━━━━━━━━━━━━━━
ID:           0
HP:           3
Strength:     5
Agility:      15
Max Damage:   5
Experience:   1
Gold:         2
```

### Step 3: Modify Stats

Change the values in the editor:

| Stat | Original | Modified | Effect |
|------|----------|----------|--------|
| HP | 3 | 5 | Takes more hits |
| Strength | 5 | 7 | Hits harder |
| Experience | 1 | 2 | More XP reward |

### Step 4: Save Changes

1. Click **Save** button
2. Confirm the save dialog

### Step 5: Test in Emulator

1. Load your modified ROM
2. Start a new game
3. Find a Slime and battle it
4. Verify the changes worked!

### JSON Representation

The change modifies `assets/json/monsters_verified.json`:

```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 5,          // Changed from 3
    "strength": 7,    // Changed from 5
    "agility": 15,
    "max_damage": 5,
    "experience": 2,  // Changed from 1
    "gold": 2
  }
}
```

---

## Example 2: Modify Item Prices

**Goal:** Make the Erdrick's Armor affordable earlier.

### Step 1: Open Item Editor

1. Click the **📦 Items** tab
2. Find "Erdrick's Armor" in the list

### Step 2: Current Prices

```
Erdrick's Armor
━━━━━━━━━━━━━━━━━━━━━━━━━
Buy Price:   Cannot buy
Sell Price:  9000
Defense:     +28
```

### Step 3: Enable Purchase

Change buy price from 65535 (cannot buy) to a value:

| Property | Original | Modified |
|----------|----------|----------|
| Buy Price | 65535 | 25000 |

### Step 4: Find a Shop to Sell It

Open the **🏪 Shops** tab and add Erdrick's Armor to Cantlin's armor shop.

### Result

Now players can save up and buy the legendary armor!

---

## Example 3: Edit NPC Dialog

**Goal:** Change the King's opening speech.

### Step 1: Open Dialog Editor

1. Click the **💬 Dialogs** tab
2. Search for "King Lorik" or browse castle dialogs

### Step 2: Find the Dialog

```
Dialog ID: 12
Speaker: King Lorik
Text: "Descendant of Erdrick, listen now to my words..."
```

### Step 3: Edit the Text

Change to your custom message:

```
Dialog ID: 12
Speaker: King Lorik
Text: "Welcome, hero! The realm needs you..."
```

### Important Notes

- Keep text roughly the same length
- Use valid characters only (see Text Table)
- Test in game to ensure it displays correctly

### Text Character Limits

| Location | Max Characters |
|----------|----------------|
| Name entry | 8 |
| Dialog line | ~32 per line |
| Item names | 12 |
| Spell names | 8 |

---

## Example 4: Customize Starting Stats

**Goal:** Give the hero better starting equipment or stats.

### Method 1: Starting Gold

Modify the starting gold value:

1. Open **Hex Viewer** tab
2. Navigate to offset `$C04B` (starting gold low byte)
3. Change the value

```
Original: $78 $00  (120 gold)
Modified: $E8 $03  (1000 gold)
```

### Method 2: Starting Level

The hero starts at level 1. To change starting experience:

1. Find experience table
2. Modify starting XP value

### Method 3: Starting Equipment

Modify the initial equipment flags:

```
Offset $C052: Starting weapon
Offset $C053: Starting armor
Offset $C054: Starting shield
```

Values correspond to item IDs in the item table.

---

## Example 5: Create a Harder Difficulty

**Goal:** Make the game more challenging for experienced players.

### Step 1: Increase Monster Stats

Bulk modify all monsters:

```python
# Script to increase all monster HP by 50%
import json

with open('assets/json/monsters_verified.json') as f:
    monsters = json.load(f)

for id, monster in monsters.items():
    monster['hp'] = int(monster['hp'] * 1.5)
    monster['strength'] = int(monster['strength'] * 1.2)

with open('assets/json/monsters_verified.json', 'w') as f:
    json.dump(monsters, f, indent=2)
```

### Step 2: Reduce Gold Drops

```python
for id, monster in monsters.items():
    monster['gold'] = int(monster['gold'] * 0.7)
```

### Step 3: Increase Item Prices

```python
import json

with open('assets/json/items_corrected.json') as f:
    items = json.load(f)

for id, item in items.items():
    if item['buy_price'] < 65535:
        item['buy_price'] = int(item['buy_price'] * 1.5)

with open('assets/json/items_corrected.json', 'w') as f:
    json.dump(items, f, indent=2)
```

### Step 4: Rebuild and Test

```bash
python dragon_warrior_build.py
# Test in emulator
```

---

## Example 6: Change Shop Inventories

**Goal:** Add new items to the Brecconary weapon shop.

### Step 1: Open Shop Editor

1. Click **🏪 Shops** tab
2. Select "Brecconary - Weapons"

### Step 2: Current Inventory

```
Brecconary Weapon Shop
━━━━━━━━━━━━━━━━━━━━━━━━━
1. Bamboo Pole    (10g)
2. Club           (60g)
3. Copper Sword   (180g)
```

### Step 3: Add Items

Add Hand Axe to the inventory:

```
Brecconary Weapon Shop
━━━━━━━━━━━━━━━━━━━━━━━━━
1. Bamboo Pole    (10g)
2. Club           (60g)
3. Copper Sword   (180g)
4. Hand Axe       (560g)  ← Added
```

### Step 4: Save and Test

1. Save the shop changes
2. Load game and visit Brecconary
3. Check the weapon shop menu

---

## Example 7: Modify Spell Effects

**Goal:** Make HEAL restore more HP.

### Step 1: Open Spell Editor

1. Click **✨ Spells** tab
2. Select "HEAL"

### Step 2: Current Values

```
HEAL
━━━━━━━━━━━━━━━━━━━━━━━━━
MP Cost:      4
Min Effect:   10
Max Effect:   17
```

### Step 3: Modify Effect

Change the healing range:

| Property | Original | Modified |
|----------|----------|----------|
| Min Effect | 10 | 20 |
| Max Effect | 17 | 30 |

### Step 4: Consider Balance

If HEAL is too strong:
- Increase MP cost to compensate
- Or buff enemy damage

---

## Example 8: Edit Map Encounters

**Goal:** Change which monsters appear in an area.

### Step 1: Open Encounter Editor

1. Click **⚔️ Encounters** tab
2. Select a map zone

### Step 2: View Current Encounters

```
Zone: Tantegel Castle Grounds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Slime:       40% chance
Red Slime:   30% chance
Drakee:      20% chance
Ghost:       10% chance
```

### Step 3: Modify Encounter Table

Change the encounter rates:

```
Zone: Tantegel Castle Grounds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Slime:       25% chance  ← Reduced
Red Slime:   25% chance  ← Reduced
Drakee:      30% chance  ← Increased
Ghost:       20% chance  ← Increased
```

### Step 4: Add New Monster

Add a new monster to the zone:

```
Zone: Tantegel Castle Grounds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Slime:       20%
Red Slime:   20%
Drakee:      25%
Ghost:       20%
Magician:    15%  ← New!
```

---

## Tips for Modding

### Do's ✅

1. **Backup everything** before modifying
2. **Test frequently** after each change
3. **Document your changes** for others
4. **Start small** and build up
5. **Use save states** for quick testing

### Don'ts ❌

1. **Don't modify everything at once**
2. **Don't ignore balance** - test gameplay
3. **Don't forget text length limits**
4. **Don't skip testing** edge cases

### Common Issues

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Game crashes | Invalid data | Restore backup, smaller changes |
| Text garbled | Wrong encoding | Check text table |
| Stats wrong | Byte overflow | Keep values in valid range |
| Item missing | Invalid ID | Check item table |

---

## Sharing Your Mod

### Create a Patch

Instead of distributing the ROM, create a patch:

```bash
# Generate IPS patch
python tools/patch_generator.py original.nes modified.nes output.ips
```

### Document Changes

Create a README for your mod:

```markdown
# My Dragon Warrior Mod

## Changes
- Monster HP increased 50%
- Gold drops reduced 30%
- New shop items in Brecconary

## Installation
1. Apply patch to clean Dragon Warrior (PRG1) ROM
2. Enjoy!
```

### Community Sharing

- [Romhacking.net](https://www.romhacking.net/) - Submit patches
- [Data Crystal](https://datacrystal.romhacking.net/wiki/Dragon_Warrior) - Share documentation

---

## Next Steps

After mastering these basics:

1. **Graphics Editing** - See [CHR Workflow Guide](CHR_WORKFLOW.md)
2. **Music Editing** - See [Music & Sound Guide](MUSIC_SOUND_EDITING.md)
3. **Assembly Hacking** - Dive into `source_files/`
4. **Create total conversions** - New story, maps, characters!

Happy modding! 🐉⚔️
