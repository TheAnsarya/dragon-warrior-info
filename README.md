# Dragon Warrior Info Project

**Comprehensive Dragon Warrior (NES) disassembly, documentation, and modding environment**

Building on the excellent foundation of existing disassembly work, this project creates a complete ecosystem for Dragon Warrior research, modding, and preservation. Based on proven patterns from the [FFMQ project](https://github.com/TheAnsarya/ffmq-info).

## 🎯 Project Goals

- **Complete Documentation** - Every byte mapped, every system understood
- **Modern Toolchain** - Python-based tools for extraction, analysis, and modification
- **Visual Editors** - GUI tools for easy content modification  
- **Build Pipeline** - Automated ROM assembly and testing
- **DataCrystal Wiki** - Comprehensive hacking reference documentation
- **Asset Management** - Extract, edit, and reinsert all game content

## 🚀 Quick Start

### Prerequisites
- Python 3.x with virtual environment support
- Git for version control
- PowerShell (Windows) for build scripts

### Setup
```bash
# Clone the repository
git clone https://github.com/TheAnsarya/dragon-warrior-info.git
cd dragon-warrior-info

# Set up Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows Command Prompt:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Place Dragon Warrior (U) (PRG1) [!].nes in roms/ directory
# See ROM_REQUIREMENTS.md for detailed ROM setup instructions

# Run the build system
python dragon_warrior_build.py
```

### Basic ROM Analysis

```bash
# Display ROM information
python tools/analysis/rom_analyzer.py info dragon_warrior.nes

# Hex dump
python tools/analysis/rom_analyzer.py hexdump dragon_warrior.nes --start 0x8000 --length 256

# Find text strings
python tools/analysis/rom_analyzer.py strings dragon_warrior.nes --min-length 4

# Generate comprehensive report
python tools/analysis/rom_analyzer.py report dragon_warrior.nes
```

### Asset Extraction & Modification Pipeline

```bash
# STEP 1: Extract all assets from ROM
python tools/organize_chr_tiles.py      # Extract & organize CHR sprite sheets
python tools/extract_all_data.py        # Extract monsters, spells, items (verified)
python tools/extract_maps_npcs.py       # Extract interior maps & NPCs
python tools/extract_text_dialogs.py    # Extract text encoding system

# STEP 2: Edit extracted JSON files
# Edit files in extracted_assets/data/:
#   - monsters.json (39 monsters with attack, defense, HP, etc.)
#   - spells.json (10 spells with MP costs)
#   - items_equipment.json (32 items: tools, weapons, armor, shields)

# STEP 3: Reinsert changes into ROM
python tools/reinsert_assets.py
# Or use programmatically:
from tools.reinsert_assets import DragonWarriorROMModifier
modifier = DragonWarriorROMModifier(
    "roms/Dragon Warrior (U) (PRG1) [!].nes",
    "output/dragon_warrior_modified.nes"
)
modifier.create_backup()
modifier.modify_monster_stats("extracted_assets/data/monsters.json")
modifier.modify_spell_data("extracted_assets/data/spells.json")
modifier.modify_equipment_stats("extracted_assets/data/items_equipment.json")
modifier.save_modified_rom()
modifier.generate_modification_report(Path("output/reports"))

# STEP 4: Test modified ROM in emulator
# Load output/dragon_warrior_modified.nes in FCEUX, Mesen, or Nestopia
```

### Extracted Assets Overview

**Graphics (CHR Tiles)**
- 18 organized sprite sheets (replaces 1024 individual tiles)
- Grouped by purpose: heroes, monsters, NPCs, items, UI, fonts, terrain, towns, dungeons, battle backgrounds
- Proper NES palettes applied per category
- Location: `extracted_assets/chr_organized/`

**Game Data (JSON Format)**
- 39 monsters: attack, defense, HP, spell, agility, magic defense, experience, gold
- 10 spells: MP costs, effects, formulas, targets, battle/field usage
- 32 items/equipment: tools (15), weapons (7), armor (7), shields (3) with prices and stats
- All data verified byte-perfect against ROM
- Location: `extracted_assets/data/`

**Interior Maps**
- 22 interior locations: towns, castles, caves
- Map dimensions, tile data, ASCII visualizations
- NPC positions and treasure chest locations
- Location: `extracted_assets/maps/`

**Text System**
- Complete character encoding table (0x00-0x7F)
- Word substitution compression (0x80-0x8F: "the", "thou", "thy", etc.)
- Control codes (0xF0-0xFF: HERO, WAIT, LINE, PAGE, CHOICE, etc.)
- Text decoder for dialog strings
- Location: `extracted_assets/text/`

### Building ROM

```powershell
# Basic build
.\build.ps1

# Clean build with testing
.\build.ps1 -Clean -Test -Verbose

# Build with debug symbols
.\build.ps1 -Symbols -Output "dragon_warrior_modified.nes"
```

## 📊 Current Status

### ✅ Completed - Asset Extraction & Modification Toolkit

**Graphics Extraction**
- ✅ 18 organized sprite sheets from 1024 CHR tiles
- ✅ Proper NES palette application per category
- ✅ Scale factors for visual editing (2x-4x)
- ✅ Metadata JSON with tile ranges and descriptions
- Tool: `tools/organize_chr_tiles.py`

**Game Data Extraction**
- ✅ 39 monsters with 8 stats each (verified byte-perfect)
- ✅ 10 spells with MP costs, effects, formulas
- ✅ 32 items/equipment with stats and prices
- ✅ ROM verification system (all data PASSED)
- Tool: `tools/extract_all_data.py`

**Map Extraction**
- ✅ 22 interior locations (towns, castles, caves)
- ✅ Map dimensions and tile data
- ✅ ASCII visualizations
- ✅ NPC positions (partial)
- ✅ Treasure chest locations
- Tool: `tools/extract_maps_npcs.py`

**Text System**
- ✅ Complete character encoding table (0x00-0x7F)
- ✅ Word compression system (0x80-0x8F)
- ✅ Control codes documented (0xF0-0xFF)
- ✅ Text decoder implementation
- ✅ Item/spell/monster name lists
- Tool: `tools/extract_text_dialogs.py`

**ROM Modification**
- ✅ Asset reinsertion framework
- ✅ Monster stat modification
- ✅ Spell MP cost modification
- ✅ Equipment stat modification
- ✅ Validation system (range checks)
- ✅ Automatic ROM backup
- ✅ Modification logging and reports
- Tool: `tools/reinsert_assets.py`

**Documentation**
- ✅ Visual asset catalog (HTML)
- ✅ ROM offset reference tables
- ✅ Tool usage documentation
- ✅ Quick start guides
- Location: `docs/asset_catalog/toolkit.html`

### 🔄 In Active Development

- **Dialog Extraction** - Full dialog pointer table analysis
- **NPC Data Enhancement** - Complete NPC format documentation
- **Overworld Map** - Extraction of world map data
- **Battle System** - Combat mechanics and formulas

### ⏳ Planned Features

- **Visual Editors** - GUI tools for sprite and map editing
- **Advanced Text Editing** - Dialog editor with compression support
- **CHR Reinsertion** - Modified sprite sheet reinsertion
- **Map Reinsertion** - Edited map tile reinsertion

## 📁 Project Structure

```text
dragon-warrior-info/
├── docs/                    # Comprehensive documentation
│   ├── guides/             # User and developer guides
│   ├── technical/          # Technical specifications
│   └── datacrystal/        # DataCrystal wiki format docs
├── tools/                   # Python analysis and modding tools
│   ├── analysis/           # ROM analysis and hex dump utilities
│   ├── extraction/         # Asset extraction tools
│   ├── github/             # GitHub automation scripts
│   └── build/              # Build system utilities
├── source_files/           # Assembly source code (existing disassembly)
├── tests/                  # Comprehensive test suite
├── ~docs/                  # Session and chat logs
├── build.ps1               # Main build script
├── requirements.txt        # Python dependencies
└── venv/                   # Virtual environment
```

## 🛠️ Tools Overview

### Extraction Tools

**organize_chr_tiles.py**
- Extracts 1024 CHR tiles from ROM offset 0x10010
- Organizes into 18 purposeful sprite sheets
- Categories: heroes, monsters, NPCs, items, UI, fonts, terrain, towns, dungeons, battle, extended
- Applies correct NES palettes per category
- Output: `extracted_assets/chr_organized/`

**extract_all_data.py**
- Comprehensive data extraction with verification
- Monsters: 39 from offset 0x5E5B (Bank01:0x1E4B)
	- Format: 8 bytes stats (Att Def HP Spel Agi Mdef Exp Gld) + 8 unused
- Spells: 10 from offset 0x7CFD with MP costs
- Items: 32 total (tools, weapons, armor, shields) from offsets 0x7CF5+
- Byte-perfect ROM verification
- Output: `extracted_assets/data/`

**extract_maps_npcs.py**
- Interior map extraction from MapDatTbl at ROM 0x801A
- 22 interior locations with dimensions and tile data
- Map format: 5 bytes per map (pointer, width, height, boundary)
- NPC position data and treasure chest locations
- ASCII map visualizations
- Output: `extracted_assets/maps/`

**extract_text_dialogs.py**
- Complete text encoding documentation
- Character map (0x00-0x7F): A-Z, a-z, 0-9, punctuation
- Word substitution (0x80-0x8F): "the", "thou", "thy", "art", etc.
- Control codes (0xF0-0xFF): HERO, WAIT, LINE, PAGE, CHOICE, etc.
- Text decoder for compressed dialog strings
- Output: `extracted_assets/text/`

### Modification Tools

**reinsert_assets.py**
- ROM modification framework for edited JSON data
- Features:
	- Modify monster stats (attack, defense, HP, agility, magic defense, exp, gold)
	- Modify spell MP costs
	- Modify equipment stats (weapon attack, armor/shield defense)
	- Automatic ROM backup before modifications
	- Validation (0-255 range checks for all stats)
	- Modification logging with before/after comparisons
	- Detailed JSON reports
- Output: `output/dragon_warrior_modified.nes`

### ROM Offset Reference

| Data Type | ROM Offset | Bank:Offset | Format | Count |
|-----------|-----------|-------------|--------|-------|
| Monster Stats | $5E5B | Bank01:$1E4B | 16 bytes (8 stats + 8 unused) | 39 |
| Spell MP Costs | $7CFD | Bank01:$3CED | 1 byte per spell | 10 |
| Weapons | $7CF5 | Bank01:$3CE5 | 1 byte attack | 7 |
| Armor | $7D05 | Bank01:$3CF5 | 1 byte defense | 7 |
| Shields | $7D0D | Bank01:$3CFD | 1 byte defense | 3 |
| Map Table | $801A | Bank00:$000A | 5 bytes (ptr, w, h, boundary) | 24 |
| CHR Tiles | $10010 | After PRG-ROM | 16 bytes per tile (NES 2bpp) | 1024 |

### Asset Extraction & Editing

- **data_extractor.py** - Extract authentic game data from ROM using real addresses
- **graphics_extractor.py** - Extract CHR-ROM graphics and palettes to PNG
- **data_structures.py** - Dragon Warrior game data definitions and validation
- Monster stats, item properties, spell data, shop inventories
- Authentic ROM addresses from Dragon Warrior assembly source analysis
- JSON output with cross-referenced asset relationships

### Interactive Editors

- **monster_editor.py** - Visual monster stats and abilities editor
- **item_editor.py** - Item properties, costs, and bonuses editor  
- **spell_editor.py** - Spell system and magic costs editor
- **shop_editor.py** - Shop inventories and inn pricing editor
- **dialog_editor.py** - Text and dialog content editor
- **map_editor.py** - Map terrain and layout editor
- **graphics_editor.py** - Visual graphics and palette editor
- Rich CLI interfaces with validation and real-time preview

### ROM Analysis

- **rom_analyzer.py** - Comprehensive ROM inspection and analysis
- Multi-format hex dumps with pattern analysis
- Text string detection and encoding analysis
- Data structure identification and mapping

### GitHub Integration

- **github_issues.py** - Automated issue creation and management
- Project board integration with GitHub Projects
- Bulk issue creation from YAML configuration
- Standard Dragon Warrior project issues template

### Testing Framework

- **test_framework.py** - Pytest-based comprehensive testing
- ROM validation and integrity checking
- Tool functionality testing
- Performance and memory usage testing
- Build system validation

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Core Documentation

- **[📖 Documentation Index](docs/INDEX.md)** - Complete navigation and overview of all documentation
- **[🎮 ROM Hacking Guide](docs/guides/ROM_HACKING_GUIDE.md)** - Complete guide to modifying Dragon Warrior
  - ROM structure and memory maps
  - Where to find and edit: monsters, spells, items, maps, dialogs, graphics
  - Modification workflow and testing
  - Advanced topics: text compression, bank switching, CHR editing

### User Guides

- **[🎮 ROM Hacking Guide](docs/guides/ROM_HACKING_GUIDE.md)** - Complete guide to modifying Dragon Warrior
- **[🚀 ROM Hacking Quick Start](docs/guides/ROM_HACKING_QUICKSTART.md)** - Get started modding in 10 minutes!
- **[📝 Modification Reference](docs/guides/MODIFICATION_REFERENCE.md)** - Quick lookup: "Change X" → "Edit file Y"
- **[🎨 CHR Graphics Workflow](docs/guides/CHR_GRAPHICS_WORKFLOW.md)** - Complete guide to editing sprites, tiles, and fonts
- **[🔧 Tools Documentation](docs/guides/TOOLS_DOCUMENTATION.md)** - Complete reference for all ROM hacking tools
- **[✅ Verification Checklist](docs/guides/VERIFICATION_CHECKLIST.md)** - Manual verification of extracted data and ROM modifications
- **[🎨 Advanced Editors Guide](docs/guides/ADVANCED_EDITORS_GUIDE.md)** - GUI editor usage and features
- **[🖼️ Sprite Sharing Guide](docs/guides/SPRITE_SHARING_GUIDE.md)** - Working with graphics and sprites
- **[🌐 Community Examples](docs/guides/COMMUNITY_EXAMPLES.md)** - Example ROM hacks and modifications
- **[🔍 Quick Reference](docs/guides/QUICK_REFERENCE.md)** - Fast lookup for common tasks
- **[❓ Troubleshooting](docs/guides/TROUBLESHOOTING.md)** - Common issues and solutions
- **[📸 Screenshot Workflow](docs/guides/SCREENSHOT_WORKFLOW.md)** - Capturing and documenting changes
- **[🎨 Enhanced Graphics](docs/guides/ENHANCED_GRAPHICS_README.md)** - Working with enhanced sprite sheets
- **[📦 Asset System](docs/guides/README_ASSET_SYSTEM.md)** - Understanding the asset management system

### Technical Documentation

- **[📐 Game Formulas and Constants](docs/technical/GAME_FORMULAS.md)** - Complete reference for all game calculations
- **[🏗️ Unified Editor Design](docs/technical/UNIFIED_EDITOR_DESIGN.md)** - Architecture of the integrated editor
- **[⚡ Optimization Techniques](docs/technical/OPTIMIZATION_TECHNIQUES.md)** - Performance optimization strategies
- **[🗺️ ROM Map](docs/datacrystal/ROM_MAP.md)** - DataCrystal format memory mapping

### Build System Documentation

- **[📋 Build Process Files](docs/build/BUILD_PROCESS_FILES.md)** - Complete list of build system files
- **[🔧 Build Verification](docs/build/BUILD_VERIFICATION.md)** - Testing and validation procedures
- **[📊 Binary Format Spec](docs/build/BINARY_FORMAT_SPEC.md)** - Binary file format specifications
- **[🔄 Binary Pipeline Tutorial](docs/build/BINARY_PIPELINE_TUTORIAL.md)** - Step-by-step build pipeline guide
- **[⚡ Optimization Guide](docs/build/OPTIMIZATION_GUIDE.md)** - Build optimization techniques
- **[📦 Asset First Build](docs/build/ASSET_FIRST_BUILD_IMPLEMENTATION.md)** - Asset-driven build process
- **[📄 Assets Not Used](docs/build/ASSETS_NOT_USED_IN_BUILD.md)** - Unused asset analysis
- **[📊 Build Process Analysis](docs/build/BUILD_PROCESS_DETAILED_ANALYSIS.md)** - Detailed build analysis
- **[📥 ROM Data Extraction](docs/build/ROM_DATA_EXTRACTION.md)** - Extraction process documentation
- **[💿 ROM Requirements](docs/build/ROM_REQUIREMENTS.md)** - ROM version and setup requirements

### Project & Implementation

- **[📊 Project Status](docs/project/PROJECT_STATUS.md)** - Current development status
- **[✅ Project Summary](docs/project/PROJECT_SUMMARY.md)** - Project overview and accomplishments
- **[🤝 Contributing](docs/project/CONTRIBUTING.md)** - How to contribute to the project
- **[📜 Code of Conduct](docs/project/CODE_OF_CONDUCT.md)** - Community guidelines
- **[🐛 Bug Fixes](docs/implementation/BUGFIX_MONSTER_SPRITES.md)** - Monster sprite allocation fixes
- **[📊 Implementation Summary](docs/implementation/IMPLEMENTATION_SUMMARY.md)** - Overall implementation notes
- **[🎨 Graphics Extraction](docs/implementation/GRAPHICS_EXTRACTION_COMPLETE.md)** - Graphics extraction completion
- **[🗂️ Item Extraction Fix](docs/implementation/ITEM_EXTRACTION_FIX_SUMMARY.md)** - Item extraction improvements
- **[🚀 Improvement Plan](docs/implementation/COMPREHENSIVE_IMPROVEMENT_PLAN.md)** - Future improvements

### Development Logs & Meta-Documentation

For logs about the **development process** of creating this project (rather than using it):

- **[📝 Development Logs Index](~docs/INDEX.md)** - Session logs, chat logs, and development history
  - [Session Logs](~docs/session-logs/) - Development session summaries
  - [Chat Logs](~docs/chat-logs/) - Detailed conversation transcripts
  - Design decisions and implementation notes

## 🤝 Contributing

This project welcomes contributions! See the documentation for:

- **Code Standards** - `.editorconfig` enforced formatting (tabs, CRLF, UTF-8)
- **Testing Requirements** - All tools must have comprehensive test coverage
- **Documentation Standards** - Markdown with DataCrystal compatibility
- **[Contributing Guide](docs/project/CONTRIBUTING.md)** - Detailed contribution guidelines
- **[Code of Conduct](docs/project/CODE_OF_CONDUCT.md)** - Community standards

### Development Workflow

1. Set up Python virtual environment with dependencies
2. Run existing tests: `python -m pytest tests/ -v`
3. Create feature branch with descriptive name
4. Implement changes with test coverage
5. Update documentation as needed
6. Commit with detailed messages following conventional commits
7. Update session logs in `~docs/session-logs/` (for significant work)

## 🏛️ Heritage and Attribution

This project builds upon excellent existing work:

### Original Disassembly

- **Source Files** - Complete 33,000+ line disassembly in `source_files/`
- **Ophis Assembler** - Included in `Ophis/` directory
- **Build Infrastructure** - Foundation build scripts and structure

### FFMQ Project Patterns

- **Project Structure** - Based on [FFMQ project](https://github.com/TheAnsarya/ffmq-info) proven patterns
- **Tool Design** - Python-based analysis and automation tools
- **Documentation Standards** - Comprehensive documentation framework
- **Testing Approach** - Pytest-based validation and quality assurance

## 🗺️ Roadmap

### Phase 1: Foundation (COMPLETE)

- ✅ Project structure and build system
- ✅ Python virtual environment and dependencies
- ✅ Basic ROM analysis tools
- ✅ Documentation framework
- ✅ Testing infrastructure
- ✅ Asset extraction and processing system
- ✅ ROM comparison and validation tools
- ✅ Comprehensive build reporting

### Phase 2: Analysis & Documentation (IN PROGRESS)

- 🔄 Complete ROM memory mapping
- 🔄 Data structure identification
- 🔄 Text encoding system analysis
- 🔄 Graphics format documentation
- 🔄 Music/audio system analysis

### Phase 3: Advanced Tools (PLANNED)

- ⏳ Visual data editors (character stats, items, monsters)
- ⏳ Graphics editing pipeline (CHR-ROM to PNG)
- ⏳ Text editing system with compression
- ⏳ Music extraction and editing tools
- ⏳ Advanced modding capabilities

### Phase 4: Distribution (FUTURE)

- ⏳ Package management system
- ⏳ Emulator integration for testing
- ⏳ Community mod sharing platform
- ⏳ Complete documentation publication

## 📋 License

This project respects all original copyrights and is intended for educational and preservation purposes. You must own a legal copy of Dragon Warrior to use these tools.

## 🙏 Acknowledgments

- **Original Disassembly Authors** - For the foundational 33,000+ line disassembly
- **FFMQ Project** - For proven patterns and project structure inspiration
- **NES Development Community** - For tools, documentation, and support
- **DataCrystal.org** - For documentation standards and hacking knowledge

