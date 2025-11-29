# Sprite Sharing and Palette Swapping Guide

**Advanced Graphics Optimization for Dragon Warrior**

*Version 1.0 - November 2024*

---

## Table of Contents

1. [Introduction](#introduction)
2. [Sprite System Overview](#sprite-system-overview)
3. [Palette Swapping Basics](#palette-swapping-basics)
4. [Sprite Families](#sprite-families)
5. [Creating Palette Variants](#creating-palette-variants)
6. [Advanced Techniques](#advanced-techniques)
7. [Optimization Strategies](#optimization-strategies)
8. [Case Studies](#case-studies)

---

## Introduction

Dragon Warrior's sprite system is highly efficient, using **palette swapping** to create monster variety without consuming additional CHR-ROM space.

### Current Implementation

```
39 monsters using 19 sprite definitions
= 51% sprite sharing efficiency
= 184 tiles saved (2,944 bytes CHR-ROM)
```

### Potential

With advanced palette swapping:
- **60-80% sharing efficiency**
- **10-15 additional monsters** using 0 bytes CHR
- **3,500-4,500 bytes saved**

---

## Sprite System Overview

### CHR-ROM Structure

```
Dragon Warrior CHR-ROM: 8KB (8,192 bytes)
├── Tiles: 512 possible (8×8 pixels each)
├── Used: 252 tiles (49%)
└── Unused: 260 tiles (51%)

Tile format: 2 planes × 8 bytes = 16 bytes per tile
```

### Sprite Storage

Each monster sprite:
- **Size**: 2×2 tiles (16×16 pixels)
- **Data**: 4 tiles × 16 bytes = 64 bytes
- **Pattern**: Stored in CHR-ROM at specific offsets

### Palette System

```
NES Palette Limitations:
├── 64 total colors available
├── 4 background palettes (4 colors each)
└── 8 sprite palettes (4 colors each)

Each palette:
├── Color 0: Transparent (shared across all palettes)
├── Color 1: Primary shade
├── Color 2: Secondary shade
└── Color 3: Highlight
```

---

## Palette Swapping Basics

### How It Works

1. **Single sprite pattern** stored in CHR-ROM
2. **Multiple palette indices** (0-7) applied at runtime
3. **Different appearance** without duplicate graphics

### Example: Slime Variants

```python
# Base sprite (CHR-ROM offset 0x1000)
slime_sprite = {
    'chr_offset': 0x1000,
    'pattern': [
        # 16×16 pattern data (4 tiles)
        # ...stored once in CHR-ROM...
    ]
}

# Palette variants
green_slime = {
    'sprite': slime_sprite,
    'palette_index': 0,  # Green palette
    'name': "Slime"
}

red_slime = {
    'sprite': slime_sprite,
    'palette_index': 1,  # Red palette
    'name': "Red Slime"
}

metal_slime = {
    'sprite': slime_sprite,
    'palette_index': 7,  # Metal palette
    'name': "Metal Slime"
}

# Result: 3 monsters, 1 sprite pattern
# Savings: 128 bytes CHR-ROM (2 sprite copies)
```

### Palette Definitions

```python
# Dragon Warrior sprite palettes (8 palettes × 4 colors)
SPRITE_PALETTES = {
    0: [0x0F, 0x16, 0x27, 0x37],  # Green (Slime, Dragon)
    1: [0x0F, 0x16, 0x17, 0x37],  # Red (Red Slime, Red Dragon)
    2: [0x0F, 0x02, 0x12, 0x37],  # Blue (Magician, Wyvern)
    3: [0x0F, 0x18, 0x28, 0x37],  # Orange (Scorpion, Goldman)
    4: [0x0F, 0x17, 0x27, 0x37],  # Brown (Wolf, Golem)
    5: [0x0F, 0x30, 0x10, 0x37],  # White (Ghost, Specter)
    6: [0x0F, 0x11, 0x21, 0x37],  # Purple (Poltergeist, Wizard)
    7: [0x0F, 0x10, 0x00, 0x37],  # Metal (Metal Slime, Metal Scorpion)
}

# NES color codes (subset):
NES_COLORS = {
    0x0F: "Black",
    0x00: "Gray",
    0x10: "Light Gray",
    0x16: "Dark Green",
    0x17: "Dark Red",
    0x18: "Dark Orange",
    0x27: "Light Green",
    0x28: "Light Orange",
    0x30: "White",
    0x37: "Light Yellow",
    # ... (64 colors total)
}
```

---

## Sprite Families

### Identifying Families

Monsters with similar **body structure** can share sprites:

#### Family 1: Slimes (Blob-like)
```
Base sprite: Slime
Variants:
├── Slime (Green, palette 0)
├── Red Slime (Red, palette 1)
└── Metal Slime (Metal, palette 7)

Potential additions:
├── Blue Slime (Blue, palette 2)
├── Purple Slime (Purple, palette 6)
└── Orange Slime (Orange, palette 3)
```

#### Family 2: Dragons (Quadruped)
```
Base sprite: Dragon
Variants:
├── Green Dragon (Green, palette 0)
├── Blue Dragon (Blue, palette 2)
└── Red Dragon (Red, palette 1)

Potential additions:
├── Purple Dragon (Purple, palette 6)
└── Metal Dragon (Metal, palette 7)
```

#### Family 3: Knights (Humanoid, Armored)
```
Base sprite: Knight
Variants:
├── Knight (Brown/Gray, palette 4)
├── Demon Knight (Red, palette 1)
├── Wraith Knight (White, palette 5)
├── Axe Knight (Orange, palette 3)
└── Armored Knight (Metal, palette 7)

Potential additions:
├── Ice Knight (Blue, palette 2)
└── Dark Knight (Purple, palette 6)
```

#### Family 4: Magicians (Humanoid, Robed)
```
Base sprite: Magician
Variants:
├── Magician (Blue, palette 2)
├── Warlock (Purple, palette 6)
└── Wizard (White, palette 5)

Potential additions:
├── Fire Mage (Red, palette 1)
└── Earth Mage (Brown, palette 4)
```

#### Family 5: Beasts (Quadruped, Organic)
```
Base sprite: Wolf
Variants:
├── Wolf (Brown, palette 4)
├── Wolflord (Red, palette 1)
└── Werewolf (Purple, palette 6)

Potential additions:
├── Ice Wolf (Blue, palette 2)
└── Metal Wolf (Metal, palette 7)
```

---

## Creating Palette Variants

### Step-by-Step Process

#### 1. Choose Base Monster

```python
# Example: Create "Shadow Knight" from Knight
base_monster = {
    'id': 26,
    'name': "Knight",
    'sprite_family': "knight",
    'palette_index': 4,  # Brown/gray
    'hp': 70,
    'attack': 80,
    # ... other stats
}
```

#### 2. Select New Palette

```python
# Choose palette that fits theme
# Shadow Knight = Dark/Purple
new_palette_index = 6  # Purple palette
```

#### 3. Adjust Stats

```python
# Make variant stronger (or weaker)
shadow_knight = {
    'id': 39,  # New monster ID
    'name': "Shadow Knight",
    'sprite_family': "knight",  # SAME as base
    'palette_index': 6,  # DIFFERENT palette
    
    # Adjusted stats (typically 10-30% different)
    'hp': 90,        # +20 HP (28% increase)
    'attack': 100,   # +20 attack (25% increase)
    'defense': 85,   # +15 defense
    'xp': 250,       # Higher rewards
    'gold': 180,
}
```

#### 4. Implement in Code

```python
# Using tools/create_palette_variant.py
from tools.create_palette_variant import create_variant

new_monster = create_variant(
    base_monster_id=26,  # Knight
    new_name="Shadow Knight",
    new_palette=6,  # Purple
    stat_multiplier=1.25,  # 25% stronger
    xp_multiplier=1.5,
    gold_multiplier=1.4
)

# Save to JSON
import json
with open('extracted_assets/monsters/shadow_knight.json', 'w') as f:
    json.dump(new_monster, f, indent=2)
```

### Palette Compatibility Chart

| Base Sprite | Compatible Palettes | Visual Result |
|-------------|---------------------|---------------|
| Slime | 0, 1, 2, 3, 6, 7 | Green, Red, Blue, Orange, Purple, Metal |
| Dragon | 0, 1, 2, 6, 7 | Green, Red, Blue, Purple, Metal |
| Knight | 1, 2, 4, 5, 6, 7 | Red, Blue, Brown, White, Purple, Metal |
| Magician | 1, 2, 5, 6 | Red, Blue, White, Purple |
| Wolf | 1, 2, 4, 6, 7 | Red, Blue, Brown, Purple, Metal |
| Scorpion | 1, 2, 3, 7 | Red, Blue, Orange, Metal |

---

## Advanced Techniques

### Mixing Palettes and Stats

Create **themed enemy sets**:

```python
# Ice-themed enemies (all use palette 2 - Blue)
ice_enemies = [
    {
        'base': 'slime',
        'name': 'Ice Slime',
        'palette': 2,
        'special': 'Resist HURT (ice theme)'
    },
    {
        'base': 'dragon',
        'name': 'Ice Dragon',
        'palette': 2,
        'special': 'High defense, slow'
    },
    {
        'base': 'knight',
        'name': 'Ice Knight',
        'palette': 2,
        'special': 'Freezing attack'
    }
]

# Fire-themed enemies (palette 1 - Red)
fire_enemies = [
    {
        'base': 'slime',
        'name': 'Lava Slime',
        'palette': 1,
        'special': 'Damage on touch'
    },
    {
        'base': 'dragon',
        'name': 'Fire Dragon',
        'palette': 1,
        'special': 'Breath fire spell'
    }
]
```

### Dynamic Palette Switching

For **boss variants**:

```python
# Dragonlord phases
dragonlord_phase1 = {
    'sprite_family': 'dragonlord',
    'palette_index': 6,  # Purple (human form)
    'hp': 100,
}

dragonlord_phase2 = {
    'sprite_family': 'dragon',  # Different sprite!
    'palette_index': 1,  # Red (dragon form)
    'hp': 130,
}
```

---

## Optimization Strategies

### Maximizing Sprite Reuse

**Strategy 1**: Palette Rotation

```python
# Use all 8 palettes for maximum variety
sprite_families = ['slime', 'dragon', 'knight']
palettes = range(8)

generated_monsters = []
for sprite in sprite_families:
    for palette in palettes:
        if is_compatible(sprite, palette):
            generated_monsters.append({
                'sprite': sprite,
                'palette': palette,
                'name': generate_name(sprite, palette)
            })

# Result: 3 sprites × 6 palettes = 18 monsters
# CHR space used: 3 sprites × 64 bytes = 192 bytes
# CHR space saved: 15 sprites × 64 bytes = 960 bytes
```

**Strategy 2**: Stat Scaling

```python
def generate_scaled_variant(base, scale_factor):
    """Create variant with scaled stats"""
    return {
        'name': f"{scale_factor}× {base['name']}",
        'sprite_family': base['sprite_family'],
        'palette_index': (base['palette_index'] + 1) % 8,
        
        'hp': int(base['hp'] * scale_factor),
        'attack': int(base['attack'] * scale_factor),
        'defense': int(base['defense'] * scale_factor),
        'xp': int(base['xp'] * scale_factor),
        'gold': int(base['gold'] * scale_factor),
    }

# Create monster progression
slime_variants = [
    base_slime,  # Level 1
    generate_scaled_variant(base_slime, 1.5),  # Level 2
    generate_scaled_variant(base_slime, 2.0),  # Level 3
    generate_scaled_variant(base_slime, 3.0),  # Level 4 (boss)
]
```

---

## Case Studies

### Case Study 1: Doubling Monster Count

**Goal**: Add 20 new monsters using 0 bytes CHR

**Implementation**:

```python
# Existing: 19 sprite families, 39 monsters
# Plan: Create 20 palette variants

new_monsters = [
    # Family 1: Slime (add 3)
    {'base': 'slime', 'name': 'Blue Slime', 'palette': 2},
    {'base': 'slime', 'name': 'Purple Slime', 'palette': 6},
    {'base': 'slime', 'name': 'Orange Slime', 'palette': 3},
    
    # Family 2: Dragon (add 3)
    {'base': 'dragon', 'name': 'Purple Dragon', 'palette': 6},
    {'base': 'dragon', 'name': 'White Dragon', 'palette': 5},
    {'base': 'dragon', 'name': 'Metal Dragon', 'palette': 7},
    
    # Family 3: Knight (add 4)
    {'base': 'knight', 'name': 'Ice Knight', 'palette': 2},
    {'base': 'knight', 'name': 'Dark Knight', 'palette': 6},
    {'base': 'knight', 'name': 'Gold Knight', 'palette': 3},
    {'base': 'knight', 'name': 'Crystal Knight', 'palette': 5},
    
    # Family 4: Wolf (add 3)
    {'base': 'wolf', 'name': 'Ice Wolf', 'palette': 2},
    {'base': 'wolf', 'name': 'Shadow Wolf', 'palette': 6},
    {'base': 'wolf', 'name': 'Metal Wolf', 'palette': 7},
    
    # ... continue for 20 total
]

# Result:
# Old: 39 monsters, 19 sprites
# New: 59 monsters, 19 sprites
# Sharing efficiency: 68%
# CHR savings: 1,280 bytes (20 sprites not created)
```

### Case Study 2: Themed Areas

**Goal**: Create ice/fire/shadow themed dungeons

**Ice Dungeon** (Palette 2 - Blue):
```python
ice_dungeon_monsters = [
    {'name': 'Ice Slime', 'sprite': 'slime', 'palette': 2, 'hp': 30},
    {'name': 'Frost Drake', 'sprite': 'drakee', 'palette': 2, 'hp': 25},
    {'name': 'Ice Scorpion', 'sprite': 'scorpion', 'palette': 2, 'hp': 35},
    {'name': 'Frozen Knight', 'sprite': 'knight', 'palette': 2, 'hp': 80},
    {'name': 'Ice Dragon', 'sprite': 'dragon', 'palette': 2, 'hp': 150},  # Boss
]
# Visual coherence: All blue palette
# CHR cost: 0 bytes (all reuse existing sprites)
```

**Fire Dungeon** (Palette 1 - Red):
```python
fire_dungeon_monsters = [
    {'name': 'Lava Slime', 'sprite': 'slime', 'palette': 1, 'hp': 35},
    {'name': 'Flame Drake', 'sprite': 'drakee', 'palette': 1, 'hp': 28},
    {'name': 'Fire Scorpion', 'sprite': 'scorpion', 'palette': 1, 'hp': 40},
    {'name': 'Flame Knight', 'sprite': 'knight', 'palette': 1, 'hp': 90},
    {'name': 'Fire Dragon', 'sprite': 'dragon', 'palette': 1, 'hp': 165},  # Boss (already exists!)
]
```

**Shadow Dungeon** (Palette 6 - Purple):
```python
shadow_dungeon_monsters = [
    {'name': 'Shadow Slime', 'sprite': 'slime', 'palette': 6, 'hp': 40},
    {'name': 'Dark Drake', 'sprite': 'drakee', 'palette': 6, 'hp': 32},
    {'name': 'Void Scorpion', 'sprite': 'scorpion', 'palette': 6, 'hp': 45},
    {'name': 'Dark Knight', 'sprite': 'knight', 'palette': 6, 'hp': 100},
    {'name': 'Shadow Dragon', 'sprite': 'dragon', 'palette': 6, 'hp': 180},  # Boss
]
```

**Result**: 15 new thematic monsters, 0 bytes CHR used

---

## Tools and Automation

### Palette Variant Generator

```python
# tools/generate_palette_variants.py
import json
from pathlib import Path

def generate_variants(base_monster_path, output_dir, palettes):
    """
    Generate palette variants
    
    Args:
        base_monster_path: Path to base monster JSON
        output_dir: Output directory
        palettes: List of (palette_index, name_suffix) tuples
    """
    with open(base_monster_path) as f:
        base = json.load(f)
    
    variants = []
    for palette_idx, suffix in palettes:
        variant = base.copy()
        variant['name'] = f"{suffix} {base['name']}"
        variant['palette_index'] = palette_idx
        variant['id'] = get_next_monster_id()
        
        # Save individual file
        variant_path = output_dir / f"{variant['name'].lower().replace(' ', '_')}.json"
        with open(variant_path, 'w') as f:
            json.dump(variant, f, indent=2)
        
        variants.append(variant)
    
    return variants

# Usage
generate_variants(
    'extracted_assets/monsters/slime.json',
    Path('extracted_assets/monsters/variants/'),
    palettes=[
        (2, 'Blue'),
        (6, 'Purple'),
        (3, 'Orange'),
    ]
)
```

---

## Best Practices

### Do's

✅ **Use thematic palettes** for coherent areas  
✅ **Scale stats proportionally** (10-30% per tier)  
✅ **Test color combinations** in emulator  
✅ **Document sprite families** for future reference  
✅ **Reserve palette 7** for special/metal enemies  

### Don'ts

❌ **Don't create palette variants randomly** (feels inconsistent)  
❌ **Don't use incompatible palettes** (check chart above)  
❌ **Don't exceed 8 palettes** (NES hardware limit)  
❌ **Don't ignore visual coherence** (blue fire looks wrong)  
❌ **Don't forget to update encounter tables**  

---

## Conclusion

Sprite sharing via palette swapping is the **most efficient** way to expand Dragon Warrior's monster roster:

- **Zero CHR-ROM cost**
- **Minimal code changes**
- **Infinite creative potential**

With 8 palettes and 19 sprite families, you can theoretically create **152 unique monsters** (8 × 19) using only the existing graphics.

---

*Last Updated: November 2024*  
*Dragon Warrior ROM Hacking Toolkit v1.0*
