# Dragon Warrior Asset Extraction & Editing Pipeline

Complete asset extraction, editing, and reinsertion system for Dragon Warrior (NES).

## Overview

This system provides a complete workflow for:
1. **Extracting** game assets from the ROM into JSON and PNG files
2. **Editing** assets using interactive visual editors
3. **Generating** assembly code for reinsertion
4. **Building** modified ROM with edited assets

## Quick Start

### 1. Extract Assets
```bash
python dragon_warrior_build.py
# Select option 1: Extract assets from ROM
```

### 2. Edit Assets
```bash
python dragon_warrior_build.py  
# Select option 2: Launch asset editors
```

### 3. Build Modified ROM
```bash
python dragon_warrior_build.py
# Select option 7: Full build pipeline
```

## Asset Editors

### 🐲 Monster Editor (`tools/editors/monster_editor.py`)
- Edit monster HP, strength, agility, experience, gold drops
- Visual monster stats tables with color coding
- Search and filter monsters
- Export monster data to text files

### ⚔️ Item Editor (`tools/editors/item_editor.py`)  
- Edit item attack/defense bonuses, prices, properties
- Manage equippable and useable flags
- Item type categorization
- Pricing balance analysis

### 🗺️ Map Editor (`tools/editors/map_editor.py`)
- Visual ASCII map editing with terrain symbols
- Tile-by-tile editing with coordinate system
- Map metadata (music, palette, dimensions)
- Export maps to text and image formats

### 🪄 Spell Editor (`tools/editors/spell_editor.py`)
- Edit MP cost, power, learn level
- Spell type categorization (healing, attack, status, utility)
- Magic system balance tools
- Spell list export

### 💬 Dialog Editor (`tools/editors/dialog_editor.py`)
- Multi-line text editing with NPC assignment
- Search dialogs by location or content
- Export dialog trees to text files
- Location-based filtering

### 🏪 Shop Editor (`tools/editors/shop_editor.py`)
- Edit shop inventories and item lists
- Manage inn prices and services
- Cross-reference with item database
- Economic balance analysis

### 🎨 Graphics Editor (`tools/editors/graphics_editor.py`)
- Visual tile editor with pixel-level editing
- NES palette color editing with live preview
- PNG import/export for external editing
- Tile animation preview

## Directory Structure

```
dragon-warrior-info/
├── dragon_warrior_build.py          # Master build system
├── tools/
│   ├── asset_pipeline.py             # Asset extraction orchestrator
│   ├── asset_reinserter.py           # Assembly code generator
│   ├── asset_validator.py            # Asset validation framework
│   ├── extraction/
│   │   ├── data_structures.py        # Game data definitions
│   │   ├── data_extractor.py         # JSON data extraction
│   │   └── graphics_extractor.py     # PNG graphics extraction
│   └── editors/
│       ├── monster_editor.py         # Monster stats editor
│       ├── item_editor.py            # Item properties editor
│       ├── map_editor.py             # Map terrain editor
│       ├── spell_editor.py           # Spell system editor
│       ├── dialog_editor.py          # Dialog text editor
│       ├── shop_editor.py            # Shop inventory editor
│       └── graphics_editor.py        # Visual graphics editor
├── extracted_assets/
│   ├── json/                         # Extracted game data
│   │   ├── monsters.json
│   │   ├── items.json
│   │   ├── spells.json
│   │   ├── shops.json
│   │   ├── dialogs.json
│   │   ├── maps.json
│   │   ├── graphics.json
│   │   └── palettes.json
│   ├── graphics/                     # PNG tile graphics
│   ├── palettes/                     # PNG palette swatches
│   └── maps/                         # PNG map images
├── build/
│   └── generated/                    # Generated assembly files
└── output/
    └── dragon_warrior_modified.nes   # Final ROM
```

## Data Format Examples

### Monster Data (JSON)
```json
{
  "1": {
    "name": "Slime",
    "hp": 3,
    "strength": 5,
    "agility": 3,
    "max_damage": 2,
    "dodge_rate": 0,
    "sleep_resistance": 15,
    "hurt_resistance": 0,
    "experience": 1,
    "gold": 2,
    "monster_type": 0,
    "sprite_id": 1
  }
}
```

### Item Data (JSON)
```json
{
  "1": {
    "name": "Bamboo Pole",
    "attack_bonus": 2,
    "defense_bonus": 0,
    "buy_price": 10,
    "sell_price": 5,
    "equippable": true,
    "useable": false,
    "item_type": 1,
    "sprite_id": 10
  }
}
```

### Graphics Data (JSON)
```json
{
  "1": {
    "name": "Hero Sprite",
    "tile_data": [0, 0, 24, 60, 126, 90, 60, 24, 0, 0, 0, 24, 126, 90, 60, 24],
    "palette_id": 0,
    "animation_frames": 4
  }
}
```

## Build Pipeline

### 1. Asset Extraction
- **Graphics Extractor**: Decodes CHR-ROM tiles to PNG images with proper NES palette conversion
- **Data Extractor**: Parses ROM data structures into JSON format
- **Merging**: Combines data with graphics references for complete asset packages

### 2. Asset Editing
- **Interactive Editors**: Rich CLI and GUI tools for editing specific asset types
- **Cross-referencing**: Editors validate references between assets (items in shops, etc.)
- **Export Tools**: Multiple output formats for analysis and backup

### 3. Assembly Generation  
- **Code Generator**: Converts edited JSON back to 6502 assembly
- **Data Structures**: Recreates original ROM data layout with modifications
- **Include System**: Modular assembly files for selective replacement

### 4. ROM Building
- **Assembler Integration**: Uses Ophis assembler for final ROM generation
- **Asset Replacement**: Selective replacement of original data with edited versions
- **Validation**: Checksum and size validation for proper ROM format

## Advanced Usage

### Asset Validation
```bash
# Validate all extracted assets
python tools/asset_validator.py extracted_assets

# Validate only JSON files
python tools/asset_validator.py extracted_assets --json-only

# Validate cross-references between files
python tools/asset_validator.py extracted_assets --cross-refs
```

### Command Line Tools
```bash
# Extract specific asset type
python tools/asset_pipeline.py extract extracted_assets --type monsters

# Launch specific editor
python tools/editors/monster_editor.py extracted_assets/json/monsters.json

# Generate assembly for specific asset type
python tools/asset_reinserter.py extracted_assets --output-dir build/generated

# Build ROM with custom settings
python dragon_warrior_build.py --source-dir custom_source --output-dir custom_output
```

### Error Handling & Validation
The asset pipeline includes comprehensive validation:
- **ROM Validation**: Checks file format, size, and readability
- **JSON Validation**: Validates structure and content of extracted data
- **Cross-Reference Checking**: Ensures item IDs in shops exist in item database
- **Data Integrity**: Validates game balance and logical constraints
- **Graphics Validation**: Checks PNG file integrity and dimensions

### Custom Data Structures
The system uses Python dataclasses for type safety and easy serialization:
```python
@dataclass
class MonsterStats:
    name: str
    hp: int
    strength: int
    # ... other fields
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonsterStats':
        return cls(**data)
```

### Graphics Format
Graphics are stored as:
- **PNG files**: For visual editing in external tools
- **Raw tile data**: For assembly generation
- **Palette information**: NES color indices with RGB mappings

## Requirements

- Python 3.8+
- PIL (Pillow) for image processing
- Rich for CLI interfaces
- Click for command line parsing
- Tkinter for GUI editors (usually included with Python)
- Ophis assembler for ROM building

## Installation

```bash
# Clone repository
git clone <repo-url>
cd dragon-warrior-info

# Install Python dependencies
pip install -r requirements.txt

# Ensure Ophis assembler is available in Ophis/ directory
```

## Contributing

The modular design allows easy extension:
- Add new asset types by extending `data_structures.py`
- Create new editors following the existing patterns
- Add new export formats in individual editors
- Extend the build system for additional ROM modifications

## Architecture Notes

### Data Flow
1. **ROM → JSON/PNG** via extraction tools
2. **JSON/PNG → Edited JSON/PNG** via interactive editors  
3. **Edited JSON/PNG → Assembly** via code generators
4. **Assembly → Modified ROM** via build system

### Editor Design
- **Rich CLI**: Consistent table-based interfaces with color coding
- **Validation**: Input validation and cross-reference checking
- **Persistence**: Automatic save/load with change tracking
- **Export**: Multiple output formats (text, CSV, etc.)

### Build Integration
- **Incremental**: Only rebuild what changed
- **Modular**: Selective asset replacement
- **Validation**: Comprehensive error checking and reporting
- **Extensible**: Plugin architecture for new asset types

This system provides a complete solution for Dragon Warrior ROM modification with a focus on usability, data integrity, and extensibility.
