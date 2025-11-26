# Binary Pipeline Tutorial

**Step-by-Step Guide to Using the Dragon Warrior Binary Intermediate Format**

*Version 1.0 - November 2024*

---

## Table of Contents

1. [Introduction](#introduction)
2. [Why Binary Intermediate Format?](#why-binary-intermediate-format)
3. [Pipeline Overview](#pipeline-overview)
4. [Step-by-Step Workflow](#step-by-step-workflow)
5. [Understanding .dwdata Files](#understanding-dwdata-files)
6. [Validation and Error Handling](#validation-and-error-handling)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The binary pipeline provides a **robust, validated workflow** for modifying Dragon Warrior ROM data. Instead of working directly with ROM or JSON files, you work with intermediate `.dwdata` binary files that include checksums and metadata.

### Benefits

✅ **Data Integrity**
- CRC32 checksums at every stage
- Automatic corruption detection
- Validation before ROM insertion

✅ **Better Workflow**
- Atomic operations (all-or-nothing)
- Faster processing (~7 seconds total)
- Clear error messages

✅ **Safety**
- Automatic ROM backups
- Reversible operations
- Version tracking

---

## Why Binary Intermediate Format?

### Traditional Workflow Problems

❌ **Direct ROM Editing**:
```
ROM → Edit → Save → Test
          ↑
        Easy to corrupt
        No validation
        Hard to debug
```

❌ **JSON-Only Workflow**:
```
ROM → JSON → Edit → ROM
          ↑
        Type errors
        Range violations
        Cross-reference issues
```

### Binary Pipeline Solution

✅ **Validated Pipeline**:
```
ROM → .dwdata → JSON/PNG → .dwdata → ROM
      ↓         ↓          ↓          ↓
      CRC32    Edit      Validate   CRC32
```

Each stage validates data before proceeding.

---

## Pipeline Overview

### The Four Tools

| Tool | Input | Output | Purpose |
|------|-------|--------|---------|
| `extract_to_binary.py` | ROM | `.dwdata` | Extract ROM data to binary |
| `binary_to_assets.py` | `.dwdata` | JSON/PNG | Convert to editable format |
| `assets_to_binary.py` | JSON/PNG | `.dwdata` | Package with validation |
| `binary_to_rom.py` | `.dwdata` | ROM | Insert into ROM with backup |

### Data Flow

```
┌─────────────┐
│ Dragon      │
│ Warrior ROM │
│ (40KB+8KB)  │
└──────┬──────┘
       │ extract_to_binary.py
       ▼
┌──────────────┐
│ monsters.    │
│ dwdata       │  Binary intermediate format
│ spells.dwdata│  • CRC32 checksums
│ items.dwdata │  • Metadata tracking
│ graphics.    │  • Version info
│ dwdata       │
└──────┬───────┘
       │ binary_to_assets.py
       ▼
┌──────────────┐
│ monsters.json│
│ spells.json  │  Human-editable formats
│ items.json   │  • JSON for data
│ chr_tiles.png│  • PNG for graphics
└──────┬───────┘
       │ ← EDIT HERE
       │
       │ assets_to_binary.py (with validation)
       ▼
┌──────────────┐
│ monsters.    │
│ dwdata       │  Validated binary
│ spells.dwdata│  • Range checks
│ items.dwdata │  • Type validation
│ graphics.    │  • Cross-references
│ dwdata       │
└──────┬───────┘
       │ binary_to_rom.py
       ▼
┌──────────────┐
│ Modified ROM │  Final output
│ + backup     │  • ROM backup created
│ + report     │  • Changes documented
└──────────────┘
```

---

## Step-by-Step Workflow

### Initial Setup

1. **Place ROM file**:
   ```powershell
   # Copy your ROM to the roms/ directory
   Copy-Item /path/to/dragon_warrior.nes roms/dragon_warrior.nes
   ```

2. **Verify ROM**:
   ```powershell
   # Check file size (should be 40,976 bytes)
   (Get-Item roms/dragon_warrior.nes).Length
   
   # Expected: 40976
   ```

### Stage 1: Extract ROM to Binary

```powershell
python tools/extract_to_binary.py
```

**What happens**:
1. Loads ROM file
2. Extracts monster data (624 bytes from 0x5C10)
3. Extracts spell data (40 bytes from 0x1D410)
4. Extracts item data (256 bytes from 0x1CF70)
5. Extracts graphics (8192 bytes from 0x10010)
6. Calculates CRC32 for each
7. Creates `.dwdata` files with headers

**Output**:
```
extracted_assets/binary/
├── monsters.dwdata     (656 bytes = 32 header + 624 data)
├── spells.dwdata       (72 bytes = 32 header + 40 data)
├── items.dwdata        (288 bytes = 32 header + 256 data)
└── graphics.dwdata     (8224 bytes = 32 header + 8192 data)
```

**Console output**:
```
==================================================
Dragon Warrior Binary Extractor
==================================================
✓ Loaded ROM: 40976 bytes

--- Extracting Data to Binary Format ---
✓ Extracted monsters (624 bytes, CRC: 0x1A2B3C4D)
✓ Extracted spells (40 bytes, CRC: 0x5E6F7A8B)
✓ Extracted items (256 bytes, CRC: 0x9C0D1E2F)
✓ Extracted graphics (8192 bytes, CRC: 0x3A4B5C6D)

==================================================
✓ Extraction complete: 4 binary files
==================================================
```

### Stage 2: Convert Binary to Assets

```powershell
python tools/binary_to_assets.py
```

**What happens**:
1. Loads `.dwdata` files
2. Validates CRC32 checksums
3. Unpacks binary data to structures
4. Converts to JSON/PNG formats
5. Saves human-editable files

**Output**:
```
extracted_assets/
├── json/
│   ├── monsters.json   (Pretty-printed, 2-space indent)
│   ├── spells.json
│   └── items.json
└── graphics/
    └── chr_tiles.png   (256×256, indexed color)
```

**Example monsters.json**:
```json
[
  {
    "id": 0,
    "name": "Slime",
    "hp": 3,
    "attack": 5,
    "defense": 2,
    "agility": 3,
    "spell": 0,
    "m_defense": 0,
    "xp": 1,
    "gold": 2
  },
  {
    "id": 1,
    "name": "Red Slime",
    "hp": 4,
    "attack": 7,
    "defense": 2,
    "agility": 4,
    "spell": 0,
    "m_defense": 0,
    "xp": 2,
    "gold": 3
  }
  ...
]
```

### Stage 3: Edit Assets

**Edit JSON files**:

Example - Double all monster XP:

```powershell
# Using Python
python -c @"
import json

with open('extracted_assets/json/monsters.json', 'r') as f:
    monsters = json.load(f)

for monster in monsters:
    monster['xp'] = min(monster['xp'] * 2, 65535)

with open('extracted_assets/json/monsters.json', 'w') as f:
    json.dump(monsters, f, indent=2)

print('✓ Doubled all monster XP')
"@
```

Example - Reduce spell MP costs:

```powershell
python -c @"
import json

with open('extracted_assets/json/spells.json', 'r') as f:
    spells = json.load(f)

for spell in spells:
    spell['mp_cost'] = max(1, spell['mp_cost'] // 2)

with open('extracted_assets/json/spells.json', 'w') as f:
    json.dump(spells, f, indent=2)

print('✓ Halved all spell MP costs')
"@
```

**Edit Graphics**:

1. Open `extracted_assets/graphics/chr_tiles.png` in GIMP/Aseprite
2. Modify tiles (keep 8×8 grid, 4 colors)
3. Save (same filename, PNG format)

### Stage 4: Package Assets to Binary

```powershell
python tools/assets_to_binary.py
```

**What happens**:
1. Loads JSON/PNG files
2. **VALIDATES all data**:
   - HP: 1-255 (no zero HP!)
   - Attack/Defense/Agility: 0-255
   - Spell: 0-9 (9 = no spell)
   - XP/Gold: 0-65535
   - Cross-references (spell IDs exist)
3. Packs into binary format
4. Calculates new CRC32
5. Creates validated `.dwdata` files

**Validation example**:

If you accidentally set HP to 0:
```json
{
  "id": 5,
  "name": "Ghost",
  "hp": 0,   // ❌ INVALID
  ...
}
```

Output:
```
❌ Validation failed for monster 5 (Ghost):
   HP must be 1-255 (got 0)

Aborting package creation.
```

**Successful output**:
```
==================================================
Dragon Warrior Asset Packager
==================================================

--- Packaging Monsters ---
✓ Validated 39 monsters
✓ Packaged monsters.dwdata (CRC: 0xNEWCRC32)

--- Packaging Spells ---
✓ Validated 10 spells
✓ Packaged spells.dwdata (CRC: 0xNEWCRC32)

--- Packaging Items ---
✓ Validated 32 items
✓ Packaged items.dwdata (CRC: 0xNEWCRC32)

==================================================
✓ Package complete: 3 binary files
==================================================
```

### Stage 5: Insert Binary into ROM

```powershell
python tools/binary_to_rom.py
```

**What happens**:
1. Loads `.dwdata` files
2. Validates CRC32 (ensures files not corrupted)
3. Loads original ROM
4. **Creates backup** (timestamped)
5. Inserts data at correct offsets
6. Saves modified ROM
7. Generates change report

**Output**:
```
==================================================
Dragon Warrior Binary Inserter
==================================================
✓ Loaded ROM: 40976 bytes
✓ Created backup: roms/dragon_warrior_backup_20241126_143022.nes

--- Inserting Binary Data ---
✓ Inserted monsters (624 bytes at 0x5C10, CRC: 0xVERIFIED)
✓ Inserted spells (40 bytes at 0x1D410, CRC: 0xVERIFIED)
✓ Inserted items (256 bytes at 0x1CF70, CRC: 0xVERIFIED)

✓ Saved: build/dragon_warrior_rebuilt.nes

--- Change Summary ---
Modified regions:
  0x5C10 - 0x5E80 (624 bytes) - Monster data
  0x1D410 - 0x1D438 (40 bytes) - Spell data
  0x1CF70 - 0x1D070 (256 bytes) - Item data

==================================================
✓ Build complete: build/dragon_warrior_rebuilt.nes
==================================================
```

**Files created**:
```
build/
├── dragon_warrior_rebuilt.nes      (Modified ROM)
└── reports/
    └── build_report_20241126.txt   (Detailed changes)

roms/
└── dragon_warrior_backup_20241126_143022.nes  (Backup)
```

---

## Understanding .dwdata Files

### File Structure

```
.dwdata format (32-byte header + data):

Offset  Size  Type      Description
------  ----  ----      -----------
0x00    4     char[4]   Magic: "DWDT"
0x04    1     uint8     Major version (1)
0x05    1     uint8     Minor version (0)
0x06    2     uint16    Reserved
0x08    4     uint32    Data type (1=monsters, 2=spells, etc.)
0x0C    4     uint32    CRC32 checksum of data
0x10    4     uint32    ROM offset (where data goes)
0x14    2     uint16    Data size in bytes
0x16    2     uint16    Reserved
0x18    8     uint64    Timestamp (Unix epoch)
0x20    ...   bytes     Raw data
```

### Data Types

| ID | Type | Description |
|----|------|-------------|
| 0x01 | Monsters | 39 monsters × 16 bytes |
| 0x02 | Spells | 10 spells × 4 bytes |
| 0x03 | Items | 32 items × 8 bytes |
| 0x04 | Maps | Variable size map data |
| 0x05 | Text | Dialog/text strings |
| 0x06 | Graphics | CHR-ROM tiles (8192 bytes) |

### Reading .dwdata Files

```python
import struct
import zlib

def read_dwdata(filename):
    """Read and validate .dwdata file"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Parse header
    header = struct.unpack('<4sBBHIIHHQ', data[:32])
    
    magic, ver_major, ver_minor, reserved1, data_type, \
        crc_stored, rom_offset, data_size, timestamp = header
    
    # Validate magic
    if magic != b'DWDT':
        raise ValueError("Invalid magic number")
    
    # Validate version
    if ver_major != 1 or ver_minor != 0:
        raise ValueError(f"Unsupported version {ver_major}.{ver_minor}")
    
    # Extract payload
    payload = data[32:32+data_size]
    
    # Validate CRC
    crc_calculated = zlib.crc32(payload)
    if crc_calculated != crc_stored:
        raise ValueError(f"CRC mismatch: {crc_calculated:08X} != {crc_stored:08X}")
    
    return {
        'data_type': data_type,
        'rom_offset': rom_offset,
        'data_size': data_size,
        'timestamp': timestamp,
        'payload': payload
    }

# Usage
info = read_dwdata('extracted_assets/binary/monsters.dwdata')
print(f"Data type: {info['data_type']}")
print(f"Size: {info['data_size']} bytes")
print(f"ROM offset: 0x{info['rom_offset']:X}")
```

---

## Validation and Error Handling

### Monster Validation

```python
def validate_monster(monster, index):
    """Validate monster data"""
    errors = []
    
    # HP check
    if not (1 <= monster.get('hp', 0) <= 255):
        errors.append(f"HP must be 1-255 (got {monster.get('hp')})")
    
    # Attack/Defense/Agility
    for stat in ['attack', 'defense', 'agility', 'm_defense']:
        value = monster.get(stat, 0)
        if not (0 <= value <= 255):
            errors.append(f"{stat} must be 0-255 (got {value})")
    
    # Spell ID
    spell = monster.get('spell', 0)
    if not (0 <= spell <= 9):
        errors.append(f"spell must be 0-9 (got {spell})")
    
    # XP/Gold
    for reward in ['xp', 'gold']:
        value = monster.get(reward, 0)
        if not (0 <= value <= 65535):
            errors.append(f"{reward} must be 0-65535 (got {value})")
    
    if errors:
        print(f"❌ Monster {index} ({monster.get('name', '?')}):")
        for error in errors:
            print(f"   {error}")
        return False
    
    return True
```

### Common Errors

**Error**: CRC mismatch
```
❌ CRC validation failed for monsters.dwdata
   Expected: 0x1A2B3C4D
   Got: 0x9E8F7D6C
```
**Solution**: File corrupted or modified. Re-run `assets_to_binary.py`

**Error**: Invalid HP
```
❌ Validation failed for monster 5 (Ghost):
   HP must be 1-255 (got 0)
```
**Solution**: Edit JSON, set HP to valid value (1-255)

**Error**: Spell ID out of range
```
❌ Validation failed for monster 12 (Druin):
   spell must be 0-9 (got 15)
```
**Solution**: Valid spell IDs are 0-9 (0 = no spell)

---

## Advanced Usage

### Batch Processing

Process multiple modifications:

```powershell
# Create processing script
$script = @"
import json

# Load all data
with open('extracted_assets/json/monsters.json', 'r') as f:
    monsters = json.load(f)

with open('extracted_assets/json/spells.json', 'r') as f:
    spells = json.load(f)

with open('extracted_assets/json/items.json', 'r') as f:
    items = json.load(f)

# Apply hard mode scaling
for monster in monsters:
    monster['hp'] = min(int(monster['hp'] * 2.0), 255)
    monster['attack'] = min(int(monster['attack'] * 1.5), 255)
    monster['xp'] = min(int(monster['xp'] * 1.5), 65535)
    monster['gold'] = int(monster['gold'] * 0.7)

# Reduce prices
for item in items:
    if item['buy_price'] > 0:
        item['buy_price'] = int(item['buy_price'] * 0.7)

# Buff spells
for spell in spells:
    spell['power'] = min(int(spell['power'] * 1.25), 255)

# Save all
with open('extracted_assets/json/monsters.json', 'w') as f:
    json.dump(monsters, f, indent=2)

with open('extracted_assets/json/spells.json', 'w') as f:
    json.dump(spells, f, indent=2)

with open('extracted_assets/json/items.json', 'w') as f:
    json.dump(items, f, indent=2)

print('✓ Applied hard mode scaling')
"@

# Run modifications
python -c $script

# Package and insert
python tools/assets_to_binary.py
python tools/binary_to_rom.py
```

### Version Control

Track changes using git:

```powershell
# Initialize repo
git init

# Add baseline
python tools/extract_to_binary.py
python tools/binary_to_assets.py
git add extracted_assets/json/*.json
git commit -m "Baseline: vanilla Dragon Warrior data"

# Make changes
# ... edit JSON files ...

# Commit changes
git add extracted_assets/json/*.json
git commit -m "Hard mode: 2x HP, 1.5x attack, reduced gold"

# View history
git log --oneline
```

### Automated Testing

Create test script:

```python
# test_modifications.py
import json

def test_no_zero_hp():
    """Ensure no monsters have 0 HP"""
    with open('extracted_assets/json/monsters.json', 'r') as f:
        monsters = json.load(f)
    
    for monster in monsters:
        assert monster['hp'] >= 1, f"{monster['name']} has invalid HP: {monster['hp']}"
    
    print("✓ All monsters have valid HP")

def test_xp_reasonable():
    """Ensure XP values are reasonable"""
    with open('extracted_assets/json/monsters.json', 'r') as f:
        monsters = json.load(f)
    
    for monster in monsters:
        assert 0 <= monster['xp'] <= 65535, f"{monster['name']} XP out of range"
        assert monster['xp'] > 0, f"{monster['name']} gives no XP"
    
    print("✓ All XP values reasonable")

if __name__ == '__main__':
    test_no_zero_hp()
    test_xp_reasonable()
    print("\n✓ All tests passed")
```

Run tests before building:

```powershell
python test_modifications.py
python tools/assets_to_binary.py
python tools/binary_to_rom.py
```

---

## Troubleshooting

### Pipeline Stuck?

**Check file permissions**:
```powershell
# Ensure files not read-only
Get-ChildItem extracted_assets -Recurse | ForEach-Object { $_.IsReadOnly = $false }
```

**Clear binary cache**:
```powershell
Remove-Item extracted_assets/binary/*.dwdata
python tools/extract_to_binary.py
```

### JSON Syntax Errors

**Common issue**: Trailing comma
```json
{
  "id": 0,
  "name": "Slime",
  "hp": 3,   // ❌ Trailing comma!
}
```

**Solution**: Remove trailing commas
```json
{
  "id": 0,
  "name": "Slime",
  "hp": 3
}
```

**Validate JSON**:
```powershell
python -m json.tool extracted_assets/json/monsters.json
```

### ROM Build Fails

**Check ROM size**:
```powershell
(Get-Item roms/dragon_warrior.nes).Length
# Should be: 40976
```

**Verify ROM hash**:
```powershell
Get-FileHash roms/dragon_warrior.nes -Algorithm MD5
# Should be: 6a0d2e06ff016f1b8c0b632fd6b79ac7 (PRG1)
```

**Check binary files exist**:
```powershell
Get-ChildItem extracted_assets/binary/*.dwdata
# Should show: monsters.dwdata, spells.dwdata, items.dwdata, graphics.dwdata
```

---

## Conclusion

The binary pipeline provides a **safe, validated, and reversible** workflow for Dragon Warrior ROM modifications.

**Key Takeaways**:

1. **Always use the full pipeline** (don't skip stages)
2. **Validate before building** (`assets_to_binary.py` catches errors)
3. **Check CRC32 checksums** (ensures data integrity)
4. **Keep backups** (`binary_to_rom.py` creates them automatically)
5. **Test in emulator** before distribution

**Happy Hacking!** 🐉⚔️

---

*Last Updated: November 2024*
*Dragon Warrior ROM Hacking Toolkit v1.0*
