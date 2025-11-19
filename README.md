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

### Asset Extraction & Editing Pipeline

```bash
# Extract all assets using the complete pipeline
python dragon_warrior_build.py --rom dragon_warrior.nes extract

# Run the interactive asset pipeline
python tools/asset_pipeline.py dragon_warrior.nes

# Extract specific data types
python tools/extraction/data_extractor.py dragon_warrior.nes
python tools/extraction/graphics_extractor.py dragon_warrior.nes

# Edit assets with interactive editors
python tools/editors/monster_editor.py extracted_assets/json/monsters.json
python tools/editors/item_editor.py extracted_assets/json/items.json
```

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

### ✅ Completed Foundation

- **Project Structure** - Based on proven FFMQ patterns
- **Build System** - PowerShell scripts with Ophis assembler integration
- **Python Environment** - Virtual environment with comprehensive dependencies
- **Documentation Framework** - Structured docs with DataCrystal compatibility
- **ROM Analysis Tools** - Hex dump, pattern analysis, string extraction
- **Asset Extraction** - Basic graphics, text, and data extraction
- **Testing Framework** - Pytest-based validation and testing
- **GitHub Integration** - Issues management and project automation

### 🔄 In Active Development

- **Detailed ROM Mapping** - Complete memory layout documentation
- **Graphics Tools** - CHR-ROM extraction and PNG conversion
- **Text System** - Character encoding and dialog extraction
- **Data Editors** - Character stats, items, monsters
- **Music Tools** - Audio extraction and analysis

### ⏳ Planned Features

- **Visual Editors** - GUI tools for data modification
- **Advanced Modding** - Complex ROM modifications
- **Emulator Integration** - Testing and debugging support
- **Distribution System** - Package management and releases

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

### Build System

- **dragon_warrior_build.py** - Complete master build system
- **tools/asset_pipeline.py** - Unified asset extraction, editing, and reinsertion
- **tools/asset_reinserter.py** - Generate assembly code for ROM reintegration
- Complete authentic ROM data extraction (not sample data)
- Interactive visual editors for all asset types
- Assembly generation with proper Dragon Warrior data structures

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

- **[Documentation Index](docs/INDEX.md)** - Complete navigation and overview
- **[ROM Map](docs/datacrystal/ROM_MAP.md)** - DataCrystal format memory mapping
- **[Quick Start](docs/guides/QUICK_START.md)** - Get started in 5 minutes *(planned)*
- **[Developer Guide](docs/guides/DEVELOPER_ONBOARDING.md)** - Contributing information *(planned)*

## 🤝 Contributing

This project welcomes contributions! See the documentation for:

- **Code Standards** - `.editorconfig` enforced formatting (tabs, CRLF, UTF-8)
- **Testing Requirements** - All tools must have comprehensive test coverage
- **Documentation Standards** - Markdown with DataCrystal compatibility
- **Session Logging** - All development work is logged in `~docs/session-logs/`

### Development Workflow

1. Set up Python virtual environment with dependencies
2. Run existing tests: `python -m pytest tests/ -v`
3. Create feature branch with descriptive name
4. Implement changes with test coverage
5. Update documentation as needed
6. Commit with detailed messages following conventional commits
7. Update session logs in `~docs/session-logs/`

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
