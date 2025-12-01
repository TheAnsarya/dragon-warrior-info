# Dragon Warrior Build System - Troubleshooting Guide

This guide covers common errors and their solutions when using the Dragon Warrior build system.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [ROM-Related Issues](#rom-related-issues)
3. [Assembler Errors](#assembler-errors)
4. [Asset Pipeline Issues](#asset-pipeline-issues)
5. [Python Environment Issues](#python-environment-issues)
6. [File Permission Issues](#file-permission-issues)

---

## Quick Diagnostics

Run the built-in diagnostic tool to check your setup:

```bash
# From the project root:
python tools/build_errors.py

# Or from the build system menu:
# Select option 12: Run diagnostics
```

This checks:
- Python version (3.8+ required)
- Required directories exist
- Ophis assembler is present
- ROM file is available
- Required Python packages are installed

---

## ROM-Related Issues

### "ROM file not found"

**Problem:** The build system cannot find the Dragon Warrior ROM.

**Solution:**
1. Place your ROM in the `roms/` directory
2. Use the correct filename: `Dragon Warrior (U) (PRG1) [!].nes`
3. PRG1 is the recommended version (not PRG0)

### "Invalid ROM header"

**Problem:** The ROM file has a corrupted or missing iNES header.

**Solution:**
1. Ensure you have an unmodified ROM
2. File should be exactly 65,552 bytes (64KB + 16-byte header)
3. Try re-downloading the ROM
4. Verify the ROM with a NES emulator first

### "Wrong ROM version (PRG0)"

**Problem:** You're using the PRG0 revision instead of PRG1.

**Solution:**
1. PRG1 is required for this toolkit
2. Look for: `Dragon Warrior (U) (PRG1) [!].nes`
3. PRG0 has bugs that were fixed in PRG1
4. Check ROM databases for the correct version

---

## Assembler Errors

### "Assembler not found"

**Problem:** The Ophis assembler is not installed.

**Solution:**
1. Download Ophis from: https://michaelcmartin.github.io/Ophis/
2. Extract to the `Ophis/` directory in the project root
3. On Windows, ensure `Ophis/ophis.exe` exists
4. On Linux/Mac, ensure `ophis` is in your PATH

### "Undefined label"

**Problem:** An assembly label is used but not defined.

**Solution:**
1. Check spelling (labels are case-sensitive)
2. Ensure the file containing the definition is included
3. Look in `source_files/*.asm` for the label
4. Check for typos in `.include` statements

### "Syntax error"

**Problem:** Invalid assembly syntax.

**Common causes:**
- Missing colon after label definitions
- Wrong opcode names
- Invalid addressing modes
- Missing operands

**Solution:**
1. Check the line number in the error
2. Refer to 6502 instruction reference
3. Compare with original source files
4. Common valid opcodes: LDA, STA, LDX, STX, LDY, STY, ADC, SBC, etc.

### "Bank overflow"

**Problem:** The assembled code exceeds ROM space.

**Solution:**
1. Your modifications made the ROM too large
2. Remove unused code or data
3. Look for accidentally duplicated content
4. Consider bank switching techniques

---

## Asset Pipeline Issues

### "Asset not found"

**Problem:** Required asset files are missing.

**Solution:**
1. Run "Extract Assets" from the build menu first
2. Check that `assets/json/` directory exists
3. Verify JSON files are present:
   - `monsters.json`
   - `items.json`
   - `spells.json`
   - etc.
4. Re-extract if files appear corrupted

### "Invalid JSON"

**Problem:** A JSON file has syntax errors.

**Common issues:**
- Missing commas between items
- Trailing commas (not allowed in strict JSON)
- Unescaped quotes in strings
- Missing brackets

**Solution:**
1. Use a JSON validator (jsonlint.com or VS Code)
2. Check for:
   - Missing commas: `"a": 1 "b": 2` should be `"a": 1, "b": 2`
   - Trailing commas: `["a", "b",]` should be `["a", "b"]`
   - Unescaped quotes: `"He said "hi""` should be `"He said \"hi\""`
3. Restore from backup if available

### "Schema validation failed"

**Problem:** JSON data doesn't match expected format.

**Solution:**
1. Check all required fields are present
2. Verify data types match:
   - Strings need quotes: `"name": "Slime"`
   - Numbers don't: `"hp": 3`
   - Booleans are lowercase: `"active": true`
3. Compare with example files in `docs/examples/`

---

## Python Environment Issues

### "ModuleNotFoundError"

**Problem:** A required Python package is missing.

**Solution:**
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. For optional features:
   ```bash
   pip install Pillow numpy
   ```
3. Ensure you're using Python 3.8+
4. Activate your virtual environment if using one

### "Python version too old"

**Problem:** Python 3.7 or older is installed.

**Solution:**
1. Download Python 3.8+ from python.org
2. On Windows, check Python launcher:
   ```bash
   py -3.11 --version
   ```
3. Update your PATH to use newer Python

---

## File Permission Issues

### "Permission denied"

**Problem:** Cannot read or write files.

**Solution:**
1. Close any programs that might have files open
2. Check file permissions (right-click → Properties)
3. On Windows, uncheck "Read-only" attribute
4. Try running as administrator

### "File in use"

**Problem:** Another program has the file locked.

**Common culprits:**
- Text editors
- Emulators
- File explorers
- Antivirus software

**Solution:**
1. Close other applications
2. Wait a few seconds and retry
3. Use Process Explorer to find locking process

---

## Error Log Files

All errors are logged to: `logs/build_errors/`

Each error creates a JSON file with:
- Error category
- Detailed message
- File path and line number
- Suggested fixes
- Timestamp

Review these logs for debugging complex issues.

---

## Getting Help

If you still have issues:

1. **Check existing issues:** https://github.com/TheAnsarya/dragon-warrior-info/issues
2. **Create a new issue** with:
   - Error message (full text)
   - Steps to reproduce
   - Your operating system
   - Python version (`python --version`)
   - Contents of error log file

---

## Common Error Quick Reference

| Error | Quick Fix |
|-------|-----------|
| ROM not found | Put ROM in `roms/` directory |
| Assembler not found | Install Ophis in `Ophis/` |
| Undefined label | Check spelling, check includes |
| Invalid JSON | Use JSON validator |
| Module not found | `pip install -r requirements.txt` |
| Permission denied | Close other programs, check file permissions |
