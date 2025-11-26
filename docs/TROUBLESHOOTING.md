# Troubleshooting Guide

**Solutions to Common Problems in Dragon Warrior ROM Hacking**

*Version 1.0 - November 2024*

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [ROM Problems](#rom-problems)
3. [Extraction Errors](#extraction-errors)
4. [Graphics Issues](#graphics-issues)
5. [Data Validation Failures](#data-validation-failures)
6. [Build Errors](#build-errors)
7. [Emulator Issues](#emulator-issues)
8. [Performance Problems](#performance-problems)
9. [Git and Version Control](#git-and-version-control)
10. [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Python Not Found

**Error**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:

1. **Install Python 3.8+**:
	 - Download from https://python.org
	 - ✅ Check "Add Python to PATH" during installation

2. **Verify installation**:
   ```powershell
   python --version
   # Should show: Python 3.8.x or higher
   ```

3. **If still not found**:
   ```powershell
   # Find Python installation
   where python
   
   # Add to PATH manually (PowerShell)
   $env:Path += ";C:\Python3\10"
   ```

### Pip Install Fails

**Error**:
```
ERROR: Could not find a version that satisfies the requirement pillow
```

**Solutions**:

1. **Update pip**:
   ```powershell
   python -m pip install --upgrade pip
   ```

2. **Use Python's pip module**:
   ```powershell
   python -m pip install pillow
   ```

3. **Check internet connection**:
	 - Ensure firewall allows pip
	 - Try different network

4. **Install from requirements.txt**:
   ```powershell
   pip install -r requirements.txt
   ```

### Pillow Installation Error (Windows)

**Error**:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solution**:

Install pre-built wheel:
```powershell
pip install --upgrade pip
pip install pillow
```

If still fails, use Anaconda:
```powershell
conda install pillow
```

---

## ROM Problems

### ROM Not Found

**Error**:
```
❌ ROM not found: roms/dragon_warrior.nes
```

**Solutions**:

1. **Check file path**:
   ```powershell
   Test-Path roms/dragon_warrior.nes
   # Should return: True
   ```

2. **Create roms directory**:
   ```powershell
   New-Item -ItemType Directory -Force -Path roms
   ```

3. **Copy ROM to correct location**:
   ```powershell
   Copy-Item "C:\path\to\your\rom.nes" roms/dragon_warrior.nes
   ```

### Wrong ROM Version

**Error**:
```
⚠ ROM hash mismatch
Expected: 6a0d2e06ff016f1b8c0b632fd6b79ac7
Got: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Solutions**:

1. **Check ROM version**:
   ```powershell
   # Calculate MD5 hash
   Get-FileHash roms/dragon_warrior.nes -Algorithm MD5
   ```

2. **Expected hashes**:
	 - **PRG1** (recommended): `6a0d2e06ff016f1b8c0b632fd6b79ac7`
	 - **PRG0**: `066d9435a488b107e0365e98878560a9`

3. **Verify file size**:
   ```powershell
   (Get-Item roms/dragon_warrior.nes).Length
   # Should be: 40976 bytes (40KB + 16B header)
   ```

4. **If wrong version**:
	 - Obtain correct ROM (PRG1 recommended)
	 - Toolkit works with both, but PRG1 is standard

### ROM Header Issues

**Error**:
```
Invalid NES header
```

**Solutions**:

1. **Check iNES header**:
   ```powershell
   # First 4 bytes should be: 4E 45 53 1A ("NES" + DOS EOF)
   Format-Hex roms/dragon_warrior.nes -Count 16
   ```

2. **Remove trainer** (if present):
	 Some ROMs have 512-byte trainer - remove it:
   ```python
   with open('roms/dragon_warrior.nes', 'rb') as f:
       data = f.read()
   
   # Check for trainer (byte 6, bit 2)
   has_trainer = (data[6] & 0x04) != 0
   
   if has_trainer:
       # Remove 512-byte trainer
       fixed = data[:16] + data[528:]
       with open('roms/dragon_warrior_fixed.nes', 'wb') as f:
           f.write(fixed)
   ```

---

## Extraction Errors

### Extraction Fails Silently

**Problem**: Tools run but create no output

**Solutions**:

1. **Check permissions**:
   ```powershell
   # Ensure directory is writable
   New-Item -ItemType Directory -Force -Path extracted_assets
   ```

2. **Run with verbose output**:
   ```powershell
   python tools/extract_all_data.py --verbose
   ```

3. **Check disk space**:
   ```powershell
   Get-PSDrive C | Select-Object Used,Free
   ```

### CRC32 Mismatch

**Error**:
```
❌ CRC validation failed for monsters.dwdata
Expected: 0x1A2B3C4D
Got: 0x9E8F7D6C
```

**Solutions**:

1. **File corrupted - re-extract**:
   ```powershell
   Remove-Item extracted_assets/binary/*.dwdata
   python tools/extract_to_binary.py
   ```

2. **If persistent**:
	 - Check ROM integrity
	 - Verify no antivirus interference
	 - Try different directory

3. **Bypass validation** (temporary):
   ```python
   # In binary_to_assets.py, comment out CRC check
   # NOT RECOMMENDED for production
   ```

### Missing Graphics

**Error**:
```
❌ CHR tiles not found: extracted_assets/graphics/chr_tiles.png
```

**Solutions**:

1. **Run full extraction**:
   ```powershell
   python tools/extract_all_data.py
   ```

2. **Check Pillow installed**:
   ```powershell
   python -c "from PIL import Image; print('OK')"
   ```

3. **Extract graphics specifically**:
   ```powershell
   python tools/organize_chr_tiles.py --extract
   ```

---

## Graphics Issues

### CHR Tiles Corrupted

**Problem**: Graphics look wrong or garbled

**Solutions**:

1. **Verify image dimensions**:
   ```python
   from PIL import Image
   img = Image.open('extracted_assets/graphics/chr_tiles.png')
   print(img.size)  # Should be: (256, 256)
   ```

2. **Check color mode**:
   ```python
   print(img.mode)  # Should be: RGB or P (indexed)
   ```

3. **Re-export from ROM**:
   ```powershell
   Remove-Item extracted_assets/graphics/chr_tiles.png
   python tools/organize_chr_tiles.py --extract
   ```

### Palette Wrong Colors

**Problem**: Sprites have incorrect colors

**Solutions**:

1. **Verify NES palette**:
	 - Must use standard NES 64-color palette
	 - Tools like YY-CHR export correct palettes

2. **Check palette index**:
   ```json
   {
     "id": 0,
     "name": "Slime",
     "palette_index": 0  // Must be 0-7 for sprites
   }
   ```

3. **Export palette swatches**:
   ```powershell
   python tools/palette_analyzer.py --export-swatches
   # Check output/palettes/sprite_palettes.png
   ```

### Tile Alignment Off

**Problem**: Sprites appear shifted or misaligned

**Solutions**:

1. **Verify 8×8 grid**:
	 - All edits must respect 8-pixel grid
	 - Use grid overlay in graphics editor

2. **Check image dimensions**:
	 - Must be exactly 256×256 (32×32 tiles)
	 - No cropping or resizing

3. **Re-export with correct settings**:
	 - Format: PNG
	 - Size: 256×256
	 - Grid: 8×8 pixels

---

## Data Validation Failures

### Invalid HP

**Error**:
```
❌ Validation failed for monster 5 (Ghost):
   HP must be 1-255 (got 0)
```

**Solutions**:

1. **Check JSON file**:
   ```json
   {
     "id": 5,
     "name": "Ghost",
     "hp": 1  // Must be 1-255, not 0
   }
   ```

2. **Common mistakes**:
	 - HP = 0 (invalid, use 1+)
	 - HP > 255 (invalid, max is 255)
	 - HP as string `"10"` (must be number)

### Spell ID Out of Range

**Error**:
```
❌ Monster 12: spell must be 0-9 (got 15)
```

**Solutions**:

1. **Valid spell IDs**:
   ```
   0 = No spell
   1 = HEAL
   2 = HURT
   3 = SLEEP
   4 = RADIANT
   5 = STOPSPELL
   6 = OUTSIDE
   7 = RETURN
   8 = REPEL
   9 = HEALMORE
   ```

2. **Fix JSON**:
   ```json
   {
     "spell": 0  // 0-9 only
   }
   ```

### XP/Gold Overflow

**Error**:
```
❌ Monster 38: xp must be 0-65535 (got 100000)
```

**Solutions**:

1. **Check max values**:
	 - XP: 0-65535 (16-bit unsigned)
	 - Gold: 0-65535 (16-bit unsigned)

2. **Cap values**:
   ```python
   monster['xp'] = min(monster['xp'], 65535)
   monster['gold'] = min(monster['gold'], 65535)
   ```

### JSON Syntax Error

**Error**:
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 15 column 5
```

**Solutions**:

1. **Validate JSON**:
   ```powershell
   python -m json.tool extracted_assets/json/monsters.json
   ```

2. **Common issues**:
	 - Trailing commas:
     ```json
     {
       "hp": 10,  // ❌ Last property has comma
     }
     ```
	 - Missing quotes:
     ```json
     {
       name: "Slime"  // ❌ Should be "name"
     }
     ```
	 - Comments (not allowed):
     ```json
     {
       "hp": 10  // ❌ JSON doesn't support comments
     }
     ```

3. **Use JSON editor**:
	 - VS Code with JSON extension
	 - JSONLint online validator

---

## Build Errors

### Binary Package Failed

**Error**:
```
❌ Package creation failed: Validation errors found
```

**Solutions**:

1. **Run validation first**:
   ```powershell
   python tools/validate_all.py
   ```

2. **Fix all validation errors**:
	 - Check console output for specific errors
	 - Edit JSON files to fix issues

3. **Re-run packaging**:
   ```powershell
   python tools/assets_to_binary.py
   ```

### ROM Insertion Failed

**Error**:
```
❌ Failed to insert monsters: File not found
```

**Solutions**:

1. **Verify binary files exist**:
   ```powershell
   Get-ChildItem extracted_assets/binary/*.dwdata
   ```

2. **Check ROM writable**:
   ```powershell
   Test-Path build/dragon_warrior_rebuilt.nes -PathType Leaf
   # If exists, check not read-only
   (Get-Item build/dragon_warrior_rebuilt.nes).IsReadOnly
   ```

3. **Create build directory**:
   ```powershell
   New-Item -ItemType Directory -Force -Path build
   ```

### Build Size Wrong

**Error**:
```
⚠ Output ROM size incorrect
Expected: 40976
Got: 40960
```

**Solutions**:

1. **Check CHR-ROM**:
	 - Should be 8192 bytes
	 - Verify graphics.dwdata size

2. **Verify all data inserted**:
   ```powershell
   python tools/rom_diff.py roms/dragon_warrior.nes build/dragon_warrior_rebuilt.nes
   ```

3. **Rebuild from scratch**:
   ```powershell
   Remove-Item build/dragon_warrior_rebuilt.nes
   python tools/binary_to_rom.py
   ```

---

## Emulator Issues

### ROM Crashes on Load

**Problem**: Emulator crashes or shows black screen

**Solutions**:

1. **Test with different emulators**:
	 - Try Mesen (most accurate)
	 - Try FCEUX
	 - Try Nestopia

2. **Check ROM size**:
   ```powershell
   (Get-Item build/dragon_warrior_rebuilt.nes).Length
   # Must be: 40976 bytes
   ```

3. **Verify header**:
   ```powershell
   Format-Hex build/dragon_warrior_rebuilt.nes -Count 16
   # First 4 bytes: 4E 45 53 1A
   ```

4. **Compare with original**:
   ```powershell
   python tools/rom_diff.py roms/dragon_warrior.nes build/dragon_warrior_rebuilt.nes --detailed
   ```

### Battle Crashes

**Problem**: Game crashes when entering battle

**Solutions**:

1. **Check monster stats**:
	 - HP must be 1-255
	 - All stats within valid ranges

2. **Verify sprite data**:
	 - CHR tiles not corrupted
	 - Sprite pointers valid

3. **Test specific monster**:
   ```powershell
   # Use emulator debugger
   # Set breakpoint at battle init
   # Check monster ID and stats
   ```

### Graphics Glitches

**Problem**: Sprites appear corrupted in-game

**Solutions**:

1. **Verify CHR-ROM**:
   ```powershell
   python tools/organize_chr_tiles.py --verify
   ```

2. **Check palette assignments**:
	 - Sprites use palettes 0-7
	 - Backgrounds use palettes 0-3

3. **Re-insert graphics**:
   ```powershell
   python tools/assets_to_binary.py
   python tools/binary_to_rom.py
   ```

---

## Performance Problems

### Slow Extraction

**Problem**: Extraction takes > 30 seconds

**Solutions**:

1. **Use binary pipeline** (faster):
   ```powershell
   python tools/extract_to_binary.py  # ~2 seconds
   python tools/binary_to_assets.py    # ~1 second
   ```

2. **Disable antivirus** (temporarily):
	 - Some AV scanners slow file I/O

3. **Check disk**:
	 - Use SSD if available
	 - Defragment HDD

4. **Benchmark performance**:
   ```powershell
   python tools/benchmark.py --iterations 3
   ```

### High Memory Usage

**Problem**: Python using > 500 MB RAM

**Solutions**:

1. **Use streaming**:
	 - Process data in chunks
	 - Don't load entire ROM to memory

2. **Close other programs**:
   ```powershell
   # Check memory usage
   Get-Process | Sort-Object WS -Descending | Select-Object -First 10
   ```

3. **Increase virtual memory**:
	 - System → Advanced → Performance → Virtual memory

---

## Git and Version Control

### Commit Fails

**Error**:
```
fatal: not a git repository
```

**Solutions**:

1. **Initialize git**:
   ```powershell
   git init
   ```

2. **Configure user**:
   ```powershell
   git config user.name "Your Name"
   git config user.email "your@email.com"
   ```

3. **Stage files**:
   ```powershell
   git add extracted_assets/json/*.json
   git commit -m "Initial commit"
   ```

### Merge Conflicts

**Problem**: Git shows merge conflicts

**Solutions**:

1. **View conflicts**:
   ```powershell
   git status
   git diff
   ```

2. **Resolve manually**:
	 - Open conflicted file
	 - Remove `<<<<<<<`, `=======`, `>>>>>>>` markers
	 - Keep desired changes

3. **Mark resolved**:
   ```powershell
   git add resolved_file.json
   git commit -m "Resolved merge conflict"
   ```

---

## Advanced Debugging

### Enable Debug Output

**Add to Python scripts**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Memory Profiling

```powershell
python -m memory_profiler tools/extract_all_data.py
```

### Performance Profiling

```powershell
python -m cProfile -o profile.stats tools/extract_all_data.py
python -m pstats profile.stats
```

### Hex Dump Comparison

```powershell
# Compare specific ROM regions
Format-Hex roms/dragon_warrior.nes -Offset 0x5C10 -Count 624
Format-Hex build/dragon_warrior_rebuilt.nes -Offset 0x5C10 -Count 624
```

### Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in
breakpoint()
```

---

## Getting Help

### Before Asking

1. ✅ Check this troubleshooting guide
2. ✅ Run validation: `python tools/validate_all.py`
3. ✅ Check file sizes and hashes
4. ✅ Try with clean ROM
5. ✅ Test in different emulator

### When Asking for Help

Include:

- **Error message** (full text)
- **Steps to reproduce**
- **ROM version** (PRG0/PRG1, MD5 hash)
- **Python version**: `python --version`
- **OS version**: `ver` (Windows)
- **Tool output** (copy/paste console output)

### Community Resources

- **ROM Hacking Discord servers**
- **DataCrystal Wiki**: https://datacrystal.romhacking.net/
- **GitHub Issues**: Project issue tracker

---

## Quick Reference

### Common Commands

```powershell
# Full extraction
python tools/extract_all_data.py

# Binary pipeline
python tools/extract_to_binary.py
python tools/binary_to_assets.py
python tools/assets_to_binary.py
python tools/binary_to_rom.py

# Validation
python tools/validate_all.py

# Verification
python tools/rom_diff.py roms/original.nes build/modified.nes
```

### File Locations

```
dragon-warrior-info/
├── roms/
│   └── dragon_warrior.nes          (40,976 bytes)
├── extracted_assets/
│   ├── json/
│   │   ├── monsters.json
│   │   ├── spells.json
│   │   └── items.json
│   ├── graphics/
│   │   └── chr_tiles.png           (256×256)
│   └── binary/
│       ├── monsters.dwdata
│       ├── spells.dwdata
│       └── items.dwdata
└── build/
    └── dragon_warrior_rebuilt.nes  (40,976 bytes)
```

---

*Last Updated: November 2024*
*Dragon Warrior ROM Hacking Toolkit v1.0*
