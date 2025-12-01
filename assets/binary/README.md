# Binary Asset Directory

This directory contains intermediate binary files extracted from the Dragon Warrior ROM.

## Pipeline Architecture

```text
ROM → extract_to_binary.py → .dwdata → binary_to_assets.py → .json
                                                                 ↓
                                              (edit with Universal Editor)
                                                                 ↓
                       .dwdata (rebuilt) ← assets_to_binary.py ← .json (edited)
                                                                 ↓
                                       validate_roundtrip.py (verify match)
                                                                 ↓
                                            source_files/generated/*.asm
```

## Existing Tools

| Tool | Purpose |
|------|---------|
| `extract_to_binary.py` | ROM → .dwdata (7 asset types) |
| `binary_to_assets.py` | .dwdata → JSON/PNG |
| `validate_roundtrip.py` | Verify JSON→binary matches original |

## Binary File Formats

The `.dwdata` format includes a 32-byte header with:

- Magic number (`DWDT`)
- Version (1.0)
- Data type ID
- Data size
- ROM offset
- CRC32 checksum
- Timestamp

| File | Type ID | Description | Size |
|------|---------|-------------|------|
| `monsters.dwdata` | 0x01 | Monster stat table | ~624 bytes |
| `spells.dwdata` | 0x02 | Spell data table | ~80 bytes |
| `items.dwdata` | 0x03 | Item data table | ~256 bytes |
| `graphics.dwdata` | 0x06 | CHR-ROM tiles | 16KB |
| `music_pointers.dwdata` | 0x07 | Music track pointers | 54 bytes |
| `sfx_pointers.dwdata` | 0x08 | SFX pointers | 44 bytes |
| `note_table.dwdata` | 0x07 | Note frequency table | 146 bytes |

## Usage

### Extract from ROM

```powershell
python tools/extract_to_binary.py --rom roms/dragon_warrior.nes
```

### Convert to JSON

```powershell
python tools/binary_to_assets.py
```

### Validate roundtrip

```powershell
python tools/validate_roundtrip.py --verbose
```

### Verify extracted files

```powershell
python tools/extract_to_binary.py --verify
```

## Output Locations

- **Binary files:** `extracted_assets/binary/*.dwdata`
- **JSON assets:** `extracted_assets/json/*.json`
- **Graphics:** `extracted_assets/graphics/*.png`

## Benefits

1. **Verification** - CRC32 checksums ensure data integrity
2. **Debugging** - Binary diffs easier to analyze
3. **Preservation** - Original binary preserved with header metadata
4. **Timestamps** - Track when extractions were made
5. **Roundtrip Testing** - Validate JSON→binary conversion matches original

---

Supports Issue #18 (Binary Extraction Pipeline)

