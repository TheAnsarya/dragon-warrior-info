# Asset-First Build Implementation

## Overview

The asset-first build system allows editing Dragon Warrior assets through JSON files, which are then automatically converted to assembly and integrated into the final ROM. This is the **preferred workflow** for data editing, replacing the old extract→edit disassembly→reassemble approach.

## How It Works

```
JSON Assets → ASM Generation → ASM Swapping → Ophis Assembly → Final ROM
```

1. **Edit JSON** (`assets/json/*.json`) - Human-readable game data
2. **Generate ASM** (`asset_reinserter.py`) - Converts JSON to 6502 assembly
3. **Swap Sections** (Build script) - Temporarily replaces original ASM data
4. **Assemble** (Ophis) - Compiles modified ASM to binary
5. **Restore Original** - Keeps source files clean for version control

## Implementation Details

### The Challenge: Ophis Assembler Limitations

**Problem**: Ophis doesn't support conditional assembly directives:
- `.ifdef`, `.ifndef` - Conditional compilation
- `.define`, `.echo` - Macro definition and debug output
- `.else`, `.endif` - Conditional blocks

**Attempted Solutions**:
1. ❌ `.ifdef USE_GENERATED_ASSETS` - Ophis doesn't recognize directive
2. ❌ `.ifndef USE_GENERATED_ASSETS` - Still causes address shifts
3. ✅ **Simple comment markers** - Works perfectly!

**Why unknown directives fail**: Ophis silently ignores unknown directives but they still consume space in the source, shifting all subsequent addresses. This causes the monster table to appear at the wrong ROM offset even though assembly "succeeds".

### The Solution: ASM Swapping with Comment Markers

**Source File** (`source_files/Bank01.asm`):
```asm
; === GENERATED_MONSTER_DATA_START ===
EnStatTbl:
; Original monster data...
; === GENERATED_MONSTER_DATA_END ===
```

**Build Script** (`build_with_assets.ps1`):
```powershell
# 1. Backup original
Copy-Item Bank01.asm Bank01_backup_temp.asm

# 2. Read files
$bank01Content = Get-Content Bank01.asm -Raw
$generatedMonsters = Get-Content monster_data.asm -Raw

# 3. Escape $ signs for PowerShell regex
$escapedReplacement = $generatedMonsters -replace '\$', '$$$$'

# 4. Replace section between markers
$pattern = '(?s); === GENERATED_MONSTER_DATA_START ===.*?; === GENERATED_MONSTER_DATA_END ==='
$fullReplacement = "; === GENERATED_MONSTER_DATA_START ===`r`n" + $escapedReplacement + "`r`n; === GENERATED_MONSTER_DATA_END ==="
$newBank01Content = [regex]::Replace($bank01Content, $pattern, $fullReplacement)

# 5. Write modified file
[System.IO.File]::WriteAllText('Bank01.asm', $newBank01Content)

# 6. Assemble Bank01
& Ophis Bank01.asm build/bank01.bin

# 7. Restore original
Copy-Item Bank01_backup_temp.asm Bank01.asm
Remove-Item Bank01_backup_temp.asm
```

### PowerShell Regex Gotcha: Dollar Signs

**Problem**: PowerShell treats `$` in replacement strings as variable/backreference markers.

```powershell
# WRONG - $ gets interpreted as backreference
$replacement = ".byte $05, $03, $63"  # Becomes ".byte , , "

# CORRECT - Escape $ as $$$$
$replacement = $text -replace '\$', '$$$$'  # Becomes ".byte $05, $03, $63"
```

**Why `$$$$`?** PowerShell regex replacement needs `$$` to produce a literal `$`. Since the replacement string itself is processed, you need to escape the escape: `$$$$` → `$$` → `$`.

## Current Integration Status

### ✅ Fully Implemented
- **Monster Data** (`monsters_verified.json` → `EnStatTbl` in Bank01.asm)
  - HP, Attack, Defense, Agility, etc.
  - Experience and Gold rewards
  - All 39 enemies fully supported

### ⚠️ Partial Implementation
- **Item Data** (`items_corrected.json`)
  - ASM generation exists but not integrated into build
  - Requires markers in Bank00 or Bank01
  
- **Spell Data** (`spells.json`)
  - ASM generation exists but not integrated
  - Requires markers in appropriate bank

### ❌ Not Yet Implemented
- **Graphics** (PNG → CHR-ROM conversion)
- **Maps** (Tiled JSON → ROM map data)
- **Text** (String tables)

## Usage Examples

### Example 1: Increase Slime HP

**Before** (ROM has Slime HP = 3):
```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 3,
    ...
  }
}
```

**Edit**:
```json
{
  "0": {
    "id": 0,
    "name": "Slime",
    "hp": 99,
    ...
  }
}
```

**Build**:
```powershell
.\build_with_assets.ps1
```

**Result**: ROM at offset `0x5E5D` now contains `0x63` (99) instead of `0x03` (3).

### Example 2: Modify Multiple Monsters

```json
{
  "0": { "name": "Slime", "hp": 99, "strength": 10 },
  "1": { "name": "Red Slime", "hp": 50, "gold": 100 },
  "2": { "name": "Drakee", "experience": 500 }
}
```

All changes appear in the final ROM automatically.

## File Offset Calculations

**ROM Structure**:
```
Offset     | Content           | Size
-----------|-------------------|-------
0x0000     | iNES Header       | 16 bytes (0x10)
0x0010     | PRG Bank 00       | 16KB (0x4000)
0x4010     | PRG Bank 01       | 16KB (0x4000)
0x8010     | PRG Bank 02       | 16KB (0x4000)
0xC010     | PRG Bank 03       | 16KB (0x4000)
0x10010    | CHR-ROM           | 16KB (0x4000)
-----------|-------------------|-------
Total:     | 80KB + 16 header  | 0x14010 (81936 bytes)
```

**Monster Table Location**:
- **Bank01.asm label**: `L9E4B` (bank-local address `0x9E4B`)
- **Bank01.bin offset**: `0x1E4D` (file offset, -0x8000 from label)
- **Final ROM offset**: `0x5E5D` (0x10 header + 0x4000 Bank00 + 0x1E4D)

**Address Calculation Formula**:
```
ROM offset = iNES_Header_Size + Sum(Previous_Banks) + Bank_Offset
ROM offset = 0x10 + 0x4000 + 0x1E4D = 0x5E5D
```

## Testing the Pipeline

### Verify Monster Data Integration

```powershell
# 1. Modify JSON
$json = Get-Content "assets\json\monsters_verified.json" -Raw | ConvertFrom-Json
$json.'0'.hp = 99  # Change Slime HP to 99
$json | ConvertTo-Json -Depth 100 | Set-Content "assets\json\monsters_verified.json"

# 2. Build ROM
.\build_with_assets.ps1

# 3. Verify ROM (Python)
python -c "f = open('build/dragon_warrior_rebuilt.nes', 'rb'); f.seek(0x5E5D); print(f'HP: {f.read(1)[0]}'); f.close()"
# Expected output: HP: 99

# 4. Revert changes
$json.'0'.hp = 3
$json | ConvertTo-Json -Depth 100 | Set-Content "assets\json\monsters_verified.json"
```

### Verify Build Consistency

```powershell
# Build twice and compare
.\build_with_assets.ps1
Copy-Item build\dragon_warrior_rebuilt.nes build\test1.nes

.\build_with_assets.ps1
Copy-Item build\dragon_warrior_rebuilt.nes build\test2.nes

# Should be identical
fc /b build\test1.nes build\test2.nes
# Expected: FC: no differences encountered
```

## Advantages Over Disassembly Editing

### Asset-First Workflow (NEW)
```
✅ Edit JSON (human-readable)
✅ Automatic conversion to ASM
✅ Source files stay clean
✅ Version control friendly
✅ Build script handles complexity
```

### Old Disassembly Workflow
```
❌ Edit ASM directly (hex values, no context)
❌ Manual offset calculations
❌ Easy to introduce errors
❌ Hard to track what changed
❌ No round-trip guarantee
```

## Troubleshooting

### Build succeeds but ROM has wrong data

**Symptom**: Build reports success but values don't change in ROM.

**Causes**:
1. **Wrong offset** - Use ROM offset, not bank-local address
   - Monster table: `0x5E5D` (not `0x9E4D`)
2. **Cached files** - Delete `build/` directory and rebuild
3. **JSON format** - Ensure proper indentation and types (numbers not strings)

**Solution**:
```powershell
# Clean build
Remove-Item build\* -Recurse -Force
.\build_with_assets.ps1

# Verify at CORRECT offset
python -c "with open('build/dragon_warrior_rebuilt.nes', 'rb') as f: f.seek(0x5E5D); print(f'HP: {f.read(1)[0]}')"
```

### Size change too large

**Symptom**: Build reports "Size change: 663491 bytes" instead of ~200 bytes.

**Cause**: PowerShell regex not escaping `$` properly.

**Solution**: Check `$escapedReplacement = $generatedMonsters -replace '\$', '$$$$'` exists.

### Address shifts after assembly

**Symptom**: Monster table appears at wrong offset, ROM has garbage data.

**Cause**: Ophis-incompatible directives (`.ifdef`, `.ifndef`, etc.) in ASM source.

**Solution**: Use simple comment markers only:
```asm
; === SECTION_START ===
; Data here
; === SECTION_END ===
```

## Next Steps

### Short Term
1. Add item data integration markers to Bank00
2. Add spell data integration markers
3. Test with multiple asset types simultaneously

### Medium Term
1. Implement graphics conversion (PNG → CHR-ROM)
2. Add map data integration (Tiled → ROM)
3. Create unified asset editor GUI

### Long Term
1. Support for text table editing
2. Automated ROM testing (compare gameplay)
3. Community contribution system for asset libraries

## Technical Notes

### Why Not Switch Assemblers?

**ca65** (from cc65 suite) supports full conditional assembly, but:
- Different syntax from Ophis (`.segment` vs `.org`, etc.)
- Would require rewriting all 5 ASM files (~10,000 lines)
- Break compatibility with existing disassembly
- Ophis is simpler for ROM hacking (direct `.org` mapping)

The ASM swapping solution is **simpler and more maintainable** than migrating assemblers.

### Performance Considerations

**Build Time**:
- JSON → ASM generation: ~1 second
- ASM swapping: <0.1 seconds
- Ophis assembly: ~2 seconds
- Total: ~3-4 seconds (acceptable for iterative development)

**Future Optimization**:
- Cache generated ASM if JSON unchanged
- Parallel bank assembly
- Incremental builds (only changed banks)

### Version Control Best Practices

**Commit Strategy**:
```
✅ Commit: JSON asset files
✅ Commit: Source ASM files (original data)
✅ Commit: Build scripts

❌ Don't commit: Generated ASM files
❌ Don't commit: build/ directory
❌ Don't commit: Backup files (*_backup_temp.*)
```

**`.gitignore`**:
```
source_files/generated/*.asm
source_files/*_backup_temp.*
build/
*.nes
```

## References

- **Ophis Documentation**: https://github.com/michaelcmartin/Ophis
- **Dragon Warrior ROM Map**: `docs/ROM_MAP.md`
- **Asset Reinserter**: `tools/asset_reinserter.py`
- **Build Script**: `build_with_assets.ps1`

---

**Status**: ✅ **Monster Data Fully Working** (December 2024)

**Tested**: Slime HP modification (3 → 99 → 3) verified in final ROM.
