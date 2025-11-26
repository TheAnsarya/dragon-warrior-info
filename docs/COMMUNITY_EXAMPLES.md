# Community Examples and Showcases

**Dragon Warrior ROM Hacks by the Community**

*Last Updated: November 2024*

---

## Table of Contents

1. [Featured Projects](#featured-projects)
2. [Monster Modifications](#monster-modifications)
3. [Map Expansions](#map-expansions)
4. [Quality of Life Improvements](#quality-of-life-improvements)
5. [Challenge Modes](#challenge-modes)
6. [Graphics Enhancements](#graphics-enhancements)
7. [Tutorials and Guides](#tutorials-and-guides)
8. [Contributing Your Work](#contributing-your-work)

---

## Featured Projects

### Example 1: Dragon Warrior Remix

**Author**: Community Member  
**Description**: Complete rebalance with 15 new monsters

**Features**:
- 10 new palette-swapped monsters (0 bytes CHR)
- 5 custom sprite monsters (320 bytes CHR)
- Rebalanced XP curve (faster early game)
- New item: Crystal Shield (+35 defense)

**Download**: See releases  
**Source**: `examples/dragon_warrior_remix/`

**Implementation Highlights**:

```python
# New monsters using palette swapping
new_monsters = [
    {
        'name': 'Shadow Slime',
        'base_sprite': 'slime',
        'palette': 6,  # Purple
        'hp': 45,
        'attack': 12,
        'xp': 18,
    },
    {
        'name': 'Ice Dragon',
        'base_sprite': 'dragon',
        'palette': 2,  # Blue
        'hp': 180,
        'attack': 95,
        'xp': 450,
    },
    # ... 8 more
]

# New XP curve (40% faster levels 1-10)
xp_table_modified = [
    1, 2, 4, 8, 15, 30, 60, 120, 200, 350,  # Faster
    550, 800, 1100, 1500, 2000, 2600, 3200, # Original pace
]
```

---

### Example 2: Dragon Warrior Hard Mode

**Author**: Speedrun Community  
**Description**: Brutal difficulty increase

**Changes**:
- All monster stats ×1.5
- Shop prices ×2
- XP gain ×0.7
- Death penalty: Lose 75% gold (vs 50%)
- Starting gold: 50 (vs 120)

**Download**: See releases  
**Source**: `examples/hard_mode/`

**Implementation**:

```python
# Stat scaling
for monster in monsters:
    monster.hp = int(monster.hp * 1.5)
    monster.attack = int(monster.attack * 1.5)
    monster.defense = int(monster.defense * 1.5)
    monster.xp = int(monster.xp * 0.7)  # Slower progression
    monster.gold = int(monster.gold * 0.8)  # Less gold

# Item price adjustment
for item in items:
    item.price = int(item.price * 2)
    item.sell_price = item.price // 2
```

**Result**: Average completion time: 8 hours (vs 5 hours vanilla)

---

### Example 3: Dragon Warrior Extended

**Author**: ROM Hacking Community  
**Description**: New areas and content expansion

**Features**:
- 3 new dungeons (using map compression)
- 12 new monsters (10 palette swaps, 2 custom sprites)
- Extended overworld (edge areas unlocked)
- New questline: Find 7 hidden crystals

**Download**: See releases  
**Source**: `examples/extended/`

**Technical Details**:

```python
# Map compression saved space
original_map_size = 14400  # 120×120 tiles
compressed_size = 9200     # RLE compression
space_saved = 5200         # Used for new dungeons

# New dungeons
new_dungeons = [
    {
        'name': 'Ice Cavern',
        'size': '30×30',
        'monsters': ['Ice Slime', 'Frost Drake', 'Ice Dragon'],
        'boss': 'Frost King'
    },
    {
        'name': 'Shadow Tower',
        'size': '30×30',
        'monsters': ['Shadow Slime', 'Dark Knight', 'Void Dragon'],
        'boss': 'Shadow Lord'
    },
    {
        'name': 'Crystal Palace',
        'size': '40×40',
        'monsters': ['Crystal Golem', 'Crystal Knight'],
        'boss': 'Crystal Queen'
    }
]
```

---

## Monster Modifications

### Balanced Progression (by ROMHacker123)

**Goal**: Smoother difficulty curve

```python
# Original: Steep difficulty spike at Dragonlord
# Modified: Gradual increase

monster_rebalance = {
    'Green Dragon': {
        'hp': 120,      # Was: 130
        'attack': 85,   # Was: 90
    },
    'Blue Dragon': {
        'hp': 125,      # Was: 140
        'attack': 90,   # Was: 95
    },
    'Red Dragon': {
        'hp': 135,      # Was: 150
        'attack': 95,   # Was: 100
    },
    'Dragonlord': {
        'hp': 110,      # Was: 100 (phase 1)
        'attack': 85,   # Was: 90
    }
}
```

**Result**: 20% fewer Game Overs in final dungeon

---

### Themed Enemy Sets (by PaletteMaster)

**Concept**: Dungeon-specific color themes

```python
# Charlock Castle: Red/Orange (fire theme)
charlock_monsters = [
    {'name': 'Lava Slime', 'palette': 1},      # Red
    {'name': 'Fire Scorpion', 'palette': 3},   # Orange
    {'name': 'Flame Knight', 'palette': 1},    # Red
    {'name': 'Red Dragon', 'palette': 1},      # Red (already exists)
]

# Erdrick's Cave: Blue/Purple (mystical theme)
erdrick_cave_monsters = [
    {'name': 'Mystic Slime', 'palette': 6},    # Purple
    {'name': 'Ether Drake', 'palette': 2},     # Blue
    {'name': 'Arcane Golem', 'palette': 6},    # Purple
]
```

---

## Map Expansions

### Expanded Tantegel (by MapMaker)

**Changes**:
- Tantegel Castle: 30×30 → 40×40
- Added: Weapon shop, Inn (second floor)
- New NPCs with additional dialog

**Map Data**:

```python
# New town layout
tantegel_expanded = {
    'width': 40,
    'height': 40,
    'new_buildings': [
        {'name': 'Weapon Shop', 'x': 10, 'y': 15},
        {'name': 'Inn', 'x': 25, 'y': 18},
        {'name': 'Training Hall', 'x': 30, 'y': 20},
    ],
    'npcs': [
        {'name': 'Weapon Merchant', 'x': 11, 'y': 16, 'dialog': 'weapons_shop'},
        {'name': 'Innkeeper', 'x': 26, 'y': 19, 'dialog': 'inn_welcome'},
        # ... 5 more NPCs
    ]
}
```

---

### Secret Island (by SecretFinder)

**Feature**: Hidden island in southeast corner

```python
# Overworld modification
overworld_modified = {
    'secret_island': {
        'location': (110, 110),
        'size': (8, 8),
        'tiles': 'grass_with_trees',
        'entrance': {
            'type': 'cave',
            'destination': 'secret_dungeon',
            'requires': 'magic_key'
        }
    }
}

# Secret dungeon
secret_dungeon = {
    'size': (20, 20),
    'monsters': ['Metal Slime', 'Metal Scorpion', 'Metal Dragon'],
    'treasure': 'Erdrick\'s Armor (duplicate)',
    'boss': None  # Optional challenge area
}
```

---

## Quality of Life Improvements

### Fast Text Speed (by SpeedRunner)

```assembly
; Original text speed: 4 frames/character
; Modified: 2 frames/character

; ROM offset: 0x1D8A0
.org $D8A0
    LDA #$02    ; Was: #$04
    STA $F8
```

---

### Death Penalty Reduction (by CasualPlayer)

```python
# Original: Lose 50% gold on death
# Modified: Lose 25% gold

# ROM offset: 0x1C340
death_penalty_multiplier = 0.25  # Was: 0.50

# Implementation
def on_player_death():
    current_gold = player.gold
    lost_gold = int(current_gold * 0.25)
    player.gold = current_gold - lost_gold
    return_to_castle()
```

---

### Auto-Save Feature (by ModernGamer)

```python
# Save game automatically after each level up
def level_up():
    player.level += 1
    update_stats()
    
    # Auto-save
    save_game_state()
    display_message("Progress saved!")
```

---

## Challenge Modes

### Randomizer Mode (by RandomizerDev)

**Features**:
- Monster stats randomized (±30%)
- Item locations shuffled
- Shop inventory randomized
- Spell progression scrambled

```python
import random

def randomize_monster_stats(monster):
    """Randomize monster stats by ±30%"""
    variance = 0.30
    
    monster.hp = int(monster.hp * random.uniform(1 - variance, 1 + variance))
    monster.attack = int(monster.attack * random.uniform(1 - variance, 1 + variance))
    monster.defense = int(monster.defense * random.uniform(1 - variance, 1 + variance))
    monster.xp = int(monster.xp * random.uniform(0.8, 1.2))
    
    return monster

# Apply to all monsters
for monster in monsters:
    randomize_monster_stats(monster)
```

---

### Speedrun Optimized (by SpeedrunCommunity)

**Modifications**:
- Removed: Random encounters in first 10 levels
- Increased: Walk speed (×1.2)
- Added: Early Magic Key (in Garinham)
- Reduced: Dialog text length

**Average Time**: 2:45 (vs 5:00 normal)

---

## Graphics Enhancements

### Enhanced Sprites (by ArtistName)

**Custom Sprites** (using unused CHR space):

```python
# New custom sprites (5 total, 320 bytes)
custom_sprites = [
    {
        'name': 'Frost Giant',
        'chr_offset': 0x1F000,  # Unused region
        'size': 64,  # bytes
        'palette': 2,  # Blue
    },
    {
        'name': 'Fire Demon',
        'chr_offset': 0x1F040,
        'size': 64,
        'palette': 1,  # Red
    },
    # ... 3 more
]
```

---

### Animated Sprites (by AnimationFan)

**Implementation**: Frame cycling for boss battles

```python
# Dragonlord animation (2 frames)
dragonlord_frames = [
    'dragonlord_frame_1',  # Base pose
    'dragonlord_frame_2',  # Attack pose
]

# Cycle every 30 frames
def update_boss_sprite():
    global frame_counter
    frame_counter += 1
    
    if frame_counter % 30 == 0:
        current_frame = (frame_counter // 30) % 2
        update_sprite_pattern(dragonlord_frames[current_frame])
```

---

## Tutorials and Guides

### Community Tutorial: Creating Your First Palette Swap

**By**: NewbieHelper

**Steps**:

1. **Extract monster data**:
   ```bash
   python tools/extract_binary.py --rom dragon_warrior.nes
   ```

2. **Edit JSON**:
   ```json
   {
     "id": 39,
     "name": "Shadow Slime",
     "sprite_family": "slime",
     "palette_index": 6,
     "hp": 50,
     "attack": 15
   }
   ```

3. **Package and insert**:
   ```bash
   python tools/package_binary.py --input extracted_assets
   python tools/insert_binary.py --output my_rom_hack.nes
   ```

4. **Test in emulator**

---

### Community Tutorial: Map Editing Basics

**By**: MapEditPro

1. **Extract map**:
   ```bash
   python tools/map_editor.py --rom dragon_warrior.nes --map overworld --export overworld.json
   ```

2. **Edit in tool**:
   ```bash
   python tools/map_editor.py --interactive --import overworld.json
   ```

3. **Commands**:
   ```
   > set 60 60 0x06  # Place town tile
   > rect 50 50 70 70 0x00 fill  # Ocean area
   > obj npc 65 65  # Add NPC
   > save overworld_modified.json
   ```

---

## Contributing Your Work

### Submission Guidelines

1. **Create example directory**:
   ```
   examples/your_project_name/
   ├── README.md (description, features, credits)
   ├── patches/ (IPS or BPS patches)
   ├── source/ (JSON data files)
   └── screenshots/ (PNG images)
   ```

2. **Document your changes**:
   ```markdown
   # Project Name
   
   ## Description
   Brief description of your ROM hack
   
   ## Features
   - Feature 1
   - Feature 2
   
   ## Installation
   Step-by-step instructions
   
   ## Credits
   Your name and any tools used
   ```

3. **Submit pull request**:
	 - Fork repository
	 - Add your example
	 - Create pull request with description

### Community Standards

- ✅ **Document all changes**
- ✅ **Include before/after screenshots**
- ✅ **Credit original authors**
- ✅ **Test thoroughly in emulator**
- ✅ **Provide clean patches (no copyrighted ROMs)**

---

## Recognition Wall

### Top Contributors

🥇 **PaletteMaster** - 15 themed monster sets  
🥈 **MapEditPro** - 8 custom dungeons  
🥉 **SpeedRunner** - Speedrun optimization suite  

### Featured This Month

**ArtistName** - Enhanced sprite pack (5 custom monsters)  
**RandomizerDev** - Full randomizer implementation  
**NewbieHelper** - Beginner-friendly tutorials  

---

## Resources

### External Links

- **ROM Hacking Forum**: [link]
- **Discord Community**: [link]
- **Sprite Requests**: [link]
- **Bug Reports**: GitHub Issues

### Tools Used by Community

- **Dragon Warrior Toolkit**: This toolkit!
- **YY-CHR**: Graphics editing
- **Mesen**: NES emulator with debugging
- **Hex Workshop**: Binary editing

---

*Want your project featured? Submit a pull request!*

*Last Updated: November 2024*  
*Dragon Warrior ROM Hacking Community*
