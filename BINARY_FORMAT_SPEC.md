# Dragon Warrior Binary Intermediate Format Specification

**Version:** 1.0  
**Created:** 2024-11-25  
**Purpose:** Define .dwdata binary format for ROM hacking pipeline intermediate representation

---

## Table of Contents

1. [Overview](#overview)
2. [Design Rationale](#design-rationale)
3. [File Format Structure](#file-format-structure)
4. [Monster Data Format (.dwdata)](#monster-data-format-dwdata)
5. [Spell Data Format (.dwdata)](#spell-data-format-dwdata)
6. [Item Data Format (.dwdata)](#item-data-format-dwdata)
7. [Map Data Format (.dwdata)](#map-data-format-dwdata)
8. [Text Data Format (.dwdata)](#text-data-format-dwdata)
9. [Graphics Data Format (.dwdata)](#graphics-data-format-dwdata)
10. [Transformation Pipeline](#transformation-pipeline)
11. [Checksum & Validation](#checksum--validation)
12. [Implementation Reference](#implementation-reference)

---

## Overview

### Purpose

The `.dwdata` (Dragon Warrior Data) format is an intermediate binary representation designed for the ROM hacking build pipeline. It sits between raw ROM data and human-editable assets (JSON, PNG).

**Pipeline Flow:**
```
ROM (binary) → .dwdata (binary) → JSON/PNG (editable) → .dwdata (binary) → ROM (binary)
```

### Benefits

1. **Byte-Perfect Accuracy:** Binary format ensures no precision loss
2. **Validation Layer:** Checksums detect corruption at each stage
3. **ROM Independence:** .dwdata files work with any compatible ROM version
4. **Modular Pipeline:** Each transformation step is independent and testable
5. **Debugging:** Binary inspection easier than hex dumps
6. **Version Control:** Binary diffs track changes precisely

---

## Design Rationale

### Why Not Direct ROM → JSON?

**Problem with Direct Approach:**
- ROM offsets are fragile (change with ROM version)
- No intermediate validation
- Hard to debug extraction errors
- Difficult to verify reinsertion accuracy

**Solution with Binary Intermediate:**
```
ROM → Binary (.dwdata)
  ↓ Extraction validates offsets
  ↓ Checksum computed
  ↓
Binary → JSON/PNG
  ↓ Data transformation validated
  ↓ Checksum verified
  ↓
User edits JSON/PNG
  ↓
JSON/PNG → Binary (.dwdata)
  ↓ Schema validation
  ↓ Range checking
  ↓ New checksum
  ↓
Binary → ROM
  ↓ Offset validation
  ↓ Checksum verified
  ↓
Modified ROM output
```

### Why Custom Format vs Existing?

**Considered Alternatives:**
- **JSON:** Not byte-perfect, precision loss on numbers
- **MessagePack:** Too generic, no domain validation
- **Protocol Buffers:** Overkill, requires schema compiler
- **SQLite:** Too heavy, unnecessary overhead

**Custom Format Advantages:**
- Game-specific validation rules
- Optimized for NES 8-bit/16-bit data
- Simple binary structure (no parsing overhead)
- Header includes metadata for validation
- Checksums ensure integrity

---

## File Format Structure

### Header (32 bytes)

All `.dwdata` files start with a standard 32-byte header:

```
Offset | Size | Type     | Description
-------|------|----------|----------------------------------
0x00   | 4    | char[4]  | Magic: "DWDT" (Dragon Warrior Data)
0x04   | 1    | uint8    | Major version (1)
0x05   | 1    | uint8    | Minor version (0)
0x06   | 1    | uint8    | Data type ID (see table below)
0x07   | 1    | uint8    | Flags (reserved, 0x00)
0x08   | 4    | uint32   | Data section size (bytes)
0x0C   | 4    | uint32   | ROM source offset (original ROM address)
0x10   | 4    | uint32   | CRC32 checksum of data section
0x14   | 4    | uint32   | Timestamp (Unix epoch, creation time)
0x18   | 8    | uint64   | Reserved (future use, 0x00)
```

**Data Type IDs:**
| ID | Type | Description |
|----|------|-------------|
| 0x01 | Monster | Monster stat data (39 * 16 bytes) |
| 0x02 | Spell | Spell data (10 * 8 bytes) |
| 0x03 | Item | Item/equipment data (32 * 8 bytes) |
| 0x04 | Map | Interior map tile data |
| 0x05 | Text | Text/dialog data with encoding |
| 0x06 | Graphics | CHR tile/sprite data |

### Data Section

Immediately follows header (offset 0x20). Format depends on data type.

### Endianness

**Little-endian** for all multi-byte values (NES 6502 CPU is little-endian).

Example:
- Value: 0x1234
- Stored as: `34 12` (low byte first)

---

## Monster Data Format (.dwdata)

### Specification

**File:** `monsters.dwdata`  
**Data Type ID:** 0x01  
**Total Size:** 32 bytes (header) + 624 bytes (data) = 656 bytes

### Header Example

```
Offset | Hex Values           | Description
-------|----------------------|-------------------------
0x00   | 44 57 44 54          | Magic: "DWDT"
0x04   | 01                   | Major version: 1
0x05   | 00                   | Minor version: 0
0x06   | 01                   | Data type: Monster
0x07   | 00                   | Flags: none
0x08   | 70 02 00 00          | Data size: 0x270 (624 bytes)
0x0C   | 5B 5E 00 00          | ROM offset: 0x5E5B
0x10   | [CRC32 checksum]     | CRC32 of 624-byte data
0x14   | [Timestamp]          | Creation time
0x18   | 00 00 00 00 00 00 00 00 | Reserved
```

### Data Section (624 bytes)

**Format:** 39 monsters × 16 bytes per monster

**Monster Entry (16 bytes):**
```
Offset | Size | Type   | Description | Range
-------|------|--------|-------------|--------
0x00   | 1    | uint8  | Attack      | 0-255
0x01   | 1    | uint8  | Defense     | 0-255
0x02   | 1    | uint8  | HP          | 1-255
0x03   | 1    | uint8  | Spell ID    | 0-9 (0=none)
0x04   | 1    | uint8  | Agility     | 0-255
0x05   | 1    | uint8  | M.Defense   | 0-255
0x06   | 2    | uint16 | Experience  | 0-65535
0x08   | 2    | uint16 | Gold        | 0-65535
0x0A   | 6    | byte[6]| Unused      | 0x00 (reserved)
```

**Example:** Slime (Monster ID 0)
```
Offset | Hex | Value | Field
-------|-----|-------|--------
0x20   | 05  | 5     | Attack
0x21   | 02  | 2     | Defense
0x22   | 03  | 3     | HP
0x23   | 00  | 0     | Spell (none)
0x24   | 03  | 3     | Agility
0x25   | 00  | 0     | M.Defense
0x26   | 01 00 | 1   | Experience (little-endian)
0x28   | 02 00 | 2   | Gold (little-endian)
0x2A   | 00 00 00 00 00 00 | Unused
```

### Validation Rules

- HP > 0 (no zero-HP monsters)
- All stats 0-255 (8-bit unsigned)
- Spell ID 0-9 (must reference valid spell)
- Experience/Gold 0-65535 (16-bit unsigned)
- Unused bytes must be 0x00

---

## Spell Data Format (.dwdata)

### Specification

**File:** `spells.dwdata`  
**Data Type ID:** 0x02  
**Total Size:** 32 bytes (header) + 80 bytes (data) = 112 bytes

### Data Section (80 bytes)

**Format:** 10 spells × 8 bytes per spell

**Spell Entry (8 bytes):**
```
Offset | Size | Type   | Description | Range
-------|------|--------|-------------|--------
0x00   | 1    | uint8  | MP Cost     | 0-255
0x01   | 1    | uint8  | Power       | 0-255
0x02   | 1    | uint8  | Effect Type | 0-15 (enum)
0x03   | 1    | uint8  | Range       | 0-15 (enum)
0x04   | 1    | uint8  | Animation   | 0-15
0x05   | 3    | byte[3]| Reserved    | 0x00
```

**Effect Type Enum:**
| Value | Type | Description |
|-------|------|-------------|
| 0x00 | Damage | Direct damage spell |
| 0x01 | Heal | HP restoration |
| 0x02 | Status | Status effect (sleep, etc.) |
| 0x03 | Field | Field effect (light, repel) |
| 0x04 | Utility | Utility (warp, exit) |

**Range Enum:**
| Value | Type | Description |
|-------|------|-------------|
| 0x00 | Self | Affects caster only |
| 0x01 | Enemy | Single enemy target |
| 0x02 | All | All enemies |
| 0x03 | Radius | Area effect |

**Example:** HEAL (Spell ID 0)
```
Offset | Hex | Value | Field
-------|-----|-------|--------
0x20   | 04  | 4     | MP Cost
0x21   | 1E  | 30    | Power (~30 HP)
0x22   | 01  | 1     | Effect: Heal
0x23   | 00  | 0     | Range: Self
0x24   | 00  | 0     | Animation
0x25   | 00 00 00 | Unused
```

---

## Item Data Format (.dwdata)

### Specification

**File:** `items.dwdata`  
**Data Type ID:** 0x03  
**Total Size:** 32 bytes (header) + 256 bytes (data) = 288 bytes

### Data Section (256 bytes)

**Format:** 32 items × 8 bytes per item

**Item Entry (8 bytes):**
```
Offset | Size | Type   | Description | Range
-------|------|--------|-------------|--------
0x00   | 2    | uint16 | Buy Price   | 0-65535
0x02   | 2    | uint16 | Sell Price  | 0-65535
0x04   | 1    | int8   | Attack Bonus| -128 to 127
0x05   | 1    | int8   | Def Bonus   | -128 to 127
0x06   | 1    | uint8  | Type        | 0-15 (enum)
0x07   | 1    | uint8  | Flags       | Bitfield
```

**Type Enum:**
| Value | Type | Description |
|-------|------|-------------|
| 0x00 | Tool | Consumable item |
| 0x01 | Weapon | Equippable weapon |
| 0x02 | Armor | Equippable body armor |
| 0x03 | Shield | Equippable shield |
| 0x04 | Key Item | Quest item |

**Flags Bitfield:**
```
Bit 0: Equippable (1=yes, 0=no)
Bit 1: Cursed (1=yes, 0=no)
Bit 2: Important (1=cannot sell/drop, 0=normal)
Bit 3: Quest Item (1=yes, 0=no)
Bit 4-7: Reserved (0)
```

**Example:** Herb (Item ID 0)
```
Offset | Hex | Value | Field
-------|-----|-------|--------
0x20   | 18 00 | 24  | Buy Price
0x22   | 0C 00 | 12  | Sell Price
0x24   | 00  | 0     | Attack Bonus
0x25   | 00  | 0     | Defense Bonus
0x26   | 00  | 0     | Type: Tool
0x27   | 00  | 0     | Flags: none
```

---

## Map Data Format (.dwdata)

### Specification

**File:** `maps.dwdata` (all 22 locations in one file)  
**Data Type ID:** 0x04  
**Total Size:** Variable (depends on map sizes)

### File Structure

```
Header (32 bytes)
Map Directory (22 * 16 bytes = 352 bytes)
Map Data Sections (variable)
```

### Map Directory Entry (16 bytes)

```
Offset | Size | Type   | Description
-------|------|--------|----------------------------------
0x00   | 1    | uint8  | Map ID (0-21)
0x01   | 1    | uint8  | Width (tiles)
0x02   | 1    | uint8  | Height (tiles)
0x03   | 1    | uint8  | Palette ID
0x04   | 4    | uint32 | Data offset (from file start)
0x08   | 4    | uint32 | Data size (bytes)
0x0C   | 4    | uint32 | CRC32 of map data
```

### Map Data Section (per location)

**Format:** Tile grid + NPC data

**Tile Grid:**
```
Width × Height bytes
Each byte = Tile ID (0x00-0xFF)
```

**NPC Data (after tile grid):**
```
Offset | Size | Type   | Description
-------|------|--------|----------------------------------
0x00   | 1    | uint8  | NPC count
0x01   | N*4  | NPC[]  | NPC entries (4 bytes each)
```

**NPC Entry (4 bytes):**
```
Offset | Size | Type   | Description
-------|------|--------|----------------------------------
0x00   | 1    | uint8  | X position
0x01   | 1    | uint8  | Y position
0x02   | 1    | uint8  | Sprite ID
0x03   | 1    | uint8  | Dialog ID
```

**Example:** Tantegel Throne Room (Map ID 0)
```
Map Directory Entry:
0x20   | 00  | Map ID: 0
0x21   | 20  | Width: 32 tiles
0x22   | 20  | Height: 32 tiles
0x23   | 02  | Palette: Town
0x24   | 70 01 00 00 | Data offset: 0x170
0x28   | 00 04 00 00 | Data size: 1024 bytes
0x2C   | [CRC32]     | Checksum

Map Data (at offset 0x170):
Tiles: 32×32 = 1024 bytes of tile IDs
NPCs:
  Count: 0x02 (2 NPCs)
  NPC 1: X=16, Y=8, Sprite=King, Dialog=0
  NPC 2: X=18, Y=10, Sprite=Princess, Dialog=1
```

---

## Text Data Format (.dwdata)

### Specification

**File:** `text.dwdata`  
**Data Type ID:** 0x05  
**Total Size:** Variable (depends on text length)

### File Structure

```
Header (32 bytes)
String Table (N * 8 bytes)
String Data (variable)
```

### String Table Entry (8 bytes)

```
Offset | Size | Type   | Description
-------|------|--------|----------------------------------
0x00   | 2    | uint16 | String ID
0x02   | 2    | uint16 | String length (bytes)
0x04   | 4    | uint32 | Data offset (from file start)
```

### String Data

**Format:** NES text encoding (see `ENCODING.md`)

```
Byte 0x00-0x7F: Character codes
Byte 0x80-0x8F: Word substitutions
Byte 0xF0-0xFF: Control codes
  0xFC: Player name insertion
  0xFD: Wait for button press
  0xFE: Line break
  0xFF: String terminator
```

**Example:** King Lorik Dialog
```
String Table Entry:
0x20   | 00 00 | String ID: 0
0x22   | 2A 00 | Length: 42 bytes
0x24   | 00 01 00 00 | Offset: 0x100

String Data (at offset 0x100):
57 65 6C 63 6F 6D 65 20 74 6F 20 54 61 6E 74 65 67 65 6C FE
42 72 61 76 65 20 FC 2C 20 74 68 6F 75 20 61 72 74 20 77 65 6C 63 6F 6D 65 FF

Decoded:
"Welcome to Tantegel.\n"
"Brave {HERO}, thou art welcome."
```

---

## Graphics Data Format (.dwdata)

### Specification

**File:** `graphics.dwdata` (CHR-ROM tiles)  
**Data Type ID:** 0x06  
**Total Size:** 32 bytes (header) + 16,384 bytes (data) = 16,416 bytes

### Data Section (16,384 bytes)

**Format:** 1024 tiles × 16 bytes per tile (NES 2bpp format)

**CHR Tile Entry (16 bytes):**
```
Byte 0-7: Low bitplane (8×8 pixels, low bit)
Byte 8-15: High bitplane (8×8 pixels, high bit)

2 bits per pixel → 4 colors (palette indices 0-3)
```

**Example:** Tile 0x00 (Slime sprite, partial)
```
Offset | Hex                          | Description
-------|------------------------------|-------------
0x20   | 00 18 24 42 42 24 18 00      | Low bitplane
0x28   | 18 24 5A 99 99 5A 24 18      | High bitplane

Pixel calculation:
  Pixel[y][x] = (high_bit << 1) | low_bit
```

### Palette Data (optional extension)

**Appended after tile data:** 8 palettes × 4 colors × 1 byte = 32 bytes

**Palette Entry (4 bytes):**
```
Offset | Size | Type   | Description
-------|------|--------|----------------------------------
0x00   | 1    | uint8  | Color 0 (background, NES palette index)
0x01   | 1    | uint8  | Color 1 (NES palette index 0x00-0x3F)
0x02   | 1    | uint8  | Color 2 (NES palette index 0x00-0x3F)
0x03   | 1    | uint8  | Color 3 (NES palette index 0x00-0x3F)
```

---

## Transformation Pipeline

### Stage 1: ROM → Binary Extraction

**Script:** `tools/extract_to_binary.py`

```python
def extract_monsters_binary(rom_path, output_path):
    """
    Extract monster data from ROM to .dwdata binary
    
    Args:
        rom_path: Path to Dragon Warrior ROM
        output_path: Path for monsters.dwdata output
    """
    # 1. Read ROM file
    with open(rom_path, 'rb') as f:
        rom_data = f.read()
    
    # 2. Verify ROM size and header
    assert len(rom_data) == 81936, "Invalid ROM size"
    assert rom_data[0:4] == b'NES\x1A', "Invalid NES header"
    
    # 3. Extract monster data (offset 0x5E5B, 39*16=624 bytes)
    monster_offset = 0x5E5B
    monster_size = 39 * 16
    monster_data = rom_data[monster_offset:monster_offset + monster_size]
    
    # 4. Build .dwdata header
    header = bytearray(32)
    header[0:4] = b'DWDT'              # Magic
    header[4] = 1                       # Major version
    header[5] = 0                       # Minor version
    header[6] = 0x01                    # Data type: Monster
    header[7] = 0x00                    # Flags
    struct.pack_into('<I', header, 0x08, monster_size)  # Data size
    struct.pack_into('<I', header, 0x0C, monster_offset) # ROM offset
    
    # 5. Calculate CRC32 checksum
    crc = zlib.crc32(monster_data) & 0xFFFFFFFF
    struct.pack_into('<I', header, 0x10, crc)
    
    # 6. Add timestamp
    timestamp = int(time.time())
    struct.pack_into('<I', header, 0x14, timestamp)
    
    # 7. Write .dwdata file
    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(monster_data)
    
    print(f"✓ Extracted {len(monster_data)} bytes to {output_path}")
    print(f"  CRC32: {crc:08X}")
    return crc
```

### Stage 2: Binary → JSON Transformation

**Script:** `tools/binary_to_assets.py`

```python
def binary_to_monsters_json(dwdata_path, json_path):
    """
    Transform monsters.dwdata → monsters.json
    
    Args:
        dwdata_path: Path to monsters.dwdata
        json_path: Path for monsters.json output
    """
    # 1. Read .dwdata file
    with open(dwdata_path, 'rb') as f:
        data = f.read()
    
    # 2. Parse and validate header
    assert data[0:4] == b'DWDT', "Invalid magic"
    assert data[6] == 0x01, "Not monster data"
    
    data_size = struct.unpack_from('<I', data, 0x08)[0]
    stored_crc = struct.unpack_from('<I', data, 0x10)[0]
    
    # 3. Extract data section
    monster_data = data[32:32+data_size]
    
    # 4. Verify checksum
    calc_crc = zlib.crc32(monster_data) & 0xFFFFFFFF
    assert calc_crc == stored_crc, f"CRC mismatch: {calc_crc:08X} != {stored_crc:08X}"
    
    # 5. Parse monster entries
    monsters = []
    for i in range(39):
        offset = i * 16
        entry = monster_data[offset:offset+16]
        
        monster = {
            "id": i,
            "name": MONSTER_NAMES[i],  # From constants
            "attack": entry[0],
            "defense": entry[1],
            "hp": entry[2],
            "spell": entry[3],
            "agility": entry[4],
            "m_defense": entry[5],
            "xp": struct.unpack_from('<H', entry, 6)[0],
            "gold": struct.unpack_from('<H', entry, 8)[0]
        }
        monsters.append(monster)
    
    # 6. Write JSON with metadata
    output = {
        "format_version": "1.0",
        "source_file": os.path.basename(dwdata_path),
        "crc32": f"{calc_crc:08X}",
        "monsters": monsters
    }
    
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Transformed {len(monsters)} monsters to {json_path}")
```

### Stage 3: JSON → Binary Packaging

**Script:** `tools/assets_to_binary.py`

```python
def monsters_json_to_binary(json_path, dwdata_path):
    """
    Package edited monsters.json → monsters.dwdata
    
    Args:
        json_path: Path to monsters.json
        dwdata_path: Path for monsters.dwdata output
    """
    # 1. Load and validate JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    monsters = data['monsters']
    assert len(monsters) == 39, "Must have 39 monsters"
    
    # 2. Validate each monster
    for monster in monsters:
        assert 1 <= monster['hp'] <= 255, f"Invalid HP: {monster['hp']}"
        assert 0 <= monster['attack'] <= 255, "Invalid attack"
        assert 0 <= monster['spell'] <= 9, "Invalid spell ID"
        # ... more validation
    
    # 3. Build binary data
    monster_data = bytearray(39 * 16)
    for i, monster in enumerate(monsters):
        offset = i * 16
        monster_data[offset + 0] = monster['attack']
        monster_data[offset + 1] = monster['defense']
        monster_data[offset + 2] = monster['hp']
        monster_data[offset + 3] = monster['spell']
        monster_data[offset + 4] = monster['agility']
        monster_data[offset + 5] = monster['m_defense']
        struct.pack_into('<H', monster_data, offset + 6, monster['xp'])
        struct.pack_into('<H', monster_data, offset + 8, monster['gold'])
        # Bytes 10-15 remain 0x00 (unused)
    
    # 4. Build header (same as extraction)
    header = build_dwdata_header(0x01, len(monster_data), 0x5E5B, monster_data)
    
    # 5. Write .dwdata file
    with open(dwdata_path, 'wb') as f:
        f.write(header)
        f.write(monster_data)
    
    print(f"✓ Packaged {len(monsters)} monsters to {dwdata_path}")
```

### Stage 4: Binary → ROM Reinsertion

**Script:** `tools/binary_to_rom.py`

```python
def reinsert_monsters_binary(dwdata_path, rom_path):
    """
    Reinsert monsters.dwdata → ROM at offset 0x5E5B
    
    Args:
        dwdata_path: Path to monsters.dwdata
        rom_path: Path to ROM file (will be modified)
    """
    # 1. Read .dwdata file and validate
    with open(dwdata_path, 'rb') as f:
        dwdata = f.read()
    
    assert dwdata[0:4] == b'DWDT', "Invalid .dwdata file"
    assert dwdata[6] == 0x01, "Not monster data"
    
    data_size = struct.unpack_from('<I', dwdata, 0x08)[0]
    rom_offset = struct.unpack_from('<I', dwdata, 0x0C)[0]
    stored_crc = struct.unpack_from('<I', dwdata, 0x10)[0]
    
    # 2. Extract and verify data
    monster_data = dwdata[32:32+data_size]
    calc_crc = zlib.crc32(monster_data) & 0xFFFFFFFF
    assert calc_crc == stored_crc, "CRC mismatch - data corrupted!"
    
    # 3. Read ROM and create backup
    with open(rom_path, 'rb') as f:
        rom_data = bytearray(f.read())
    
    backup_path = rom_path + '.backup'
    with open(backup_path, 'wb') as f:
        f.write(rom_data)
    
    # 4. Verify target offset
    assert rom_offset + data_size <= len(rom_data), "Offset out of bounds"
    
    # 5. Store original data for comparison
    original = rom_data[rom_offset:rom_offset+data_size]
    
    # 6. Reinsert data
    rom_data[rom_offset:rom_offset+data_size] = monster_data
    
    # 7. Write modified ROM
    with open(rom_path, 'wb') as f:
        f.write(rom_data)
    
    # 8. Generate modification report
    changes = sum(1 for i in range(data_size) if original[i] != monster_data[i])
    print(f"✓ Reinserted {data_size} bytes at offset 0x{rom_offset:04X}")
    print(f"  Changed: {changes} bytes ({100*changes/data_size:.1f}%)")
    
    return changes
```

---

## Checksum & Validation

### CRC32 Checksum

**Algorithm:** Standard IEEE CRC32 (polynomial 0xEDB88320)

**Python Implementation:**
```python
import zlib

def calculate_crc32(data: bytes) -> int:
    """Calculate CRC32 checksum (IEEE)"""
    return zlib.crc32(data) & 0xFFFFFFFF
```

**Usage:**
- Computed on data section only (not header)
- Stored in header at offset 0x10
- Verified before every transformation
- Mismatch = abort operation with error

### Validation Stages

**1. File Format Validation**
```python
def validate_dwdata_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    # Check magic
    assert data[0:4] == b'DWDT', "Invalid magic"
    
    # Check version
    assert data[4] == 1, "Unsupported version"
    
    # Check data type
    data_type = data[6]
    assert data_type in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06], "Invalid type"
    
    # Verify sizes
    data_size = struct.unpack_from('<I', data, 0x08)[0]
    assert len(data) >= 32 + data_size, "File truncated"
    
    # Verify checksum
    stored_crc = struct.unpack_from('<I', data, 0x10)[0]
    actual_data = data[32:32+data_size]
    calc_crc = zlib.crc32(actual_data) & 0xFFFFFFFF
    assert calc_crc == stored_crc, f"CRC mismatch: {calc_crc:08X} != {stored_crc:08X}"
    
    return True
```

**2. Data Range Validation**
```python
def validate_monster_data(monsters):
    for i, m in enumerate(monsters):
        assert 1 <= m['hp'] <= 255, f"Monster {i}: HP out of range"
        assert 0 <= m['attack'] <= 255, f"Monster {i}: Attack out of range"
        assert 0 <= m['spell'] <= 9, f"Monster {i}: Invalid spell ID"
        # ... more checks
```

**3. Cross-Reference Validation**
```python
def validate_cross_references(monsters, spells):
    for m in monsters:
        spell_id = m['spell']
        if spell_id > 0:
            assert spell_id - 1 < len(spells), f"Monster references non-existent spell {spell_id}"
```

### Error Handling

**CRC Mismatch:**
```
❌ ERROR: CRC32 checksum mismatch in monsters.dwdata
   Expected: A3F2C1D5
   Actual:   B4E3D2C6
   
   File may be corrupted. Restore from backup or re-extract from ROM.
```

**Data Corruption:**
```
❌ ERROR: Invalid data in monsters.dwdata
   Monster 12 (Warlock): HP = 0 (must be 1-255)
   
   Fix data in JSON and re-package to binary.
```

---

## Implementation Reference

### Directory Structure

```
extracted_assets/
├── binary/                 # .dwdata binary files
│   ├── monsters.dwdata
│   ├── spells.dwdata
│   ├── items.dwdata
│   ├── maps.dwdata
│   ├── text.dwdata
│   └── graphics.dwdata
├── json/                   # JSON editable files
│   ├── monsters.json
│   ├── spells.json
│   └── items.json
├── maps/                   # Map JSON files
│   ├── tantegel_throne.json
│   └── ... (22 files)
├── text/                   # Text JSON files
│   └── dialogs.json
└── graphics/               # PNG sprite sheets
    ├── monster_sprites.png
    └── ... (18 files)
```

### Build Pipeline Integration

**Modified Build Script:**
```powershell
# build.ps1
param(
    [switch]$UseBinaryPipeline
)

if ($UseBinaryPipeline) {
    Write-Host "=== Binary Pipeline Build ===" -ForegroundColor Cyan
    
    # Stage 1: ROM → Binary
    Write-Host "Extracting ROM data to binary..." -ForegroundColor Yellow
    python tools/extract_to_binary.py
    
    # Stage 2: Binary → JSON/PNG
    Write-Host "Transforming binary to editable assets..." -ForegroundColor Yellow
    python tools/binary_to_assets.py
    
    # Stage 3: User edits JSON/PNG (manual step)
    # (Editor would be used here)
    
    # Stage 4: JSON/PNG → Binary
    Write-Host "Packaging edited assets to binary..." -ForegroundColor Yellow
    python tools/assets_to_binary.py
    
    # Stage 5: Binary → ROM
    Write-Host "Reinserting binary data to ROM..." -ForegroundColor Yellow
    python tools/binary_to_rom.py
    
    Write-Host "✓ Build complete!" -ForegroundColor Green
}
else {
    # Original build process (direct JSON → ROM)
    Write-Host "=== Standard Build ===" -ForegroundColor Cyan
    python dragon_warrior_build.py
}
```

### Validation Report

**Example Output:**
```
Dragon Warrior Binary Pipeline Validation Report
=================================================

File: monsters.dwdata
Magic: DWDT ✓
Version: 1.0 ✓
Data Type: Monster (0x01) ✓
Data Size: 624 bytes ✓
ROM Offset: 0x5E5B ✓
CRC32: A3F2C1D5 ✓ (verified)
Timestamp: 2024-11-25 18:30:45 ✓

Data Validation:
  Monster Count: 39 ✓
  HP Range: 3-165 ✓
  Attack Range: 5-180 ✓
  Defense Range: 2-165 ✓
  Spell IDs: 0-9 ✓
  XP Range: 1-16500 ✓
  Gold Range: 2-255 ✓

Cross-References:
  Spell ID 0 (none): 16 monsters ✓
  Spell ID 1-9: Referenced in spell table ✓

Status: ✅ ALL CHECKS PASSED
```

---

**End of Binary Format Specification**
