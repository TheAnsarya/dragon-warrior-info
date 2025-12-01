# Dragon Warrior CHR Graphics Workflow Guide

Complete guide to extracting, editing, and reinserting CHR graphics.

## Table of Contents

1. [Understanding CHR Graphics](#understanding-chr-graphics)
2. [Available Tools](#available-tools)
3. [Extraction Workflow](#extraction-workflow)
4. [Editing Graphics](#editing-graphics)
5. [Reinsertion Process](#reinsertion-process)
6. [Complete Example](#complete-example)
7. [Troubleshooting](#troubleshooting)

---

## Understanding CHR Graphics

### What is CHR?

CHR (Character ROM) contains all graphical tiles used by NES games:
- Sprites (characters, enemies, items)
- Background tiles (terrain, buildings)
- UI elements (text, menus)

### NES CHR Format

| Property | Value |
|----------|-------|
| Tile size | 8×8 pixels |
| Colors per tile | 4 (2-bit per pixel) |
| Bytes per tile | 16 bytes |
| Planes | 2 (bitplane format) |

### Bitplane Encoding

Each tile uses 16 bytes:
- Bytes 0-7: Bitplane 0 (low bits)
- Bytes 8-15: Bitplane 1 (high bits)

```
Pixel value = Bitplane0[bit] + (Bitplane1[bit] << 1)

Example:
Bitplane 0: 0b10110100  = pixel values 1,0,1,1,0,1,0,0
Bitplane 1: 0b11000010  = pixel values 2,2,0,0,0,0,2,0
Combined:   pixel values 3,2,1,1,0,1,2,0
```

### Dragon Warrior CHR Layout

| Bank | Offset | Tiles | Content |
|------|--------|-------|---------|
| Bank 0 | $0000-$0FFF | 0-255 | Sprites (hero, monsters, NPCs) |
| Bank 1 | $1000-$1FFF | 256-511 | Background (terrain, buildings) |

---

## Available Tools

### Extraction Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `extract_chr_tiles.py` | Extract all tiles | ROM file | PNG images |
| `chr_tile_extractor.py` | Advanced extraction | ROM file | PNG + metadata |

### Editing Tools

| Tool | Purpose |
|------|---------|
| `chr_editor.py` | Interactive tile editor |
| `organize_chr_tiles.py` | Organize tiles into sheets |
| External: YYCHR, Tile Layer Pro | Full-featured editors |

### Reinsertion Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `chr_reinserter.py` | PNG to CHR conversion | PNG images | CHR data |
| `generate_chr_from_pngs.py` | Batch PNG processing | PNG folder | CHR bank |
| `chr_validator.py` | Validate CHR data | CHR file | Validation report |

---

## Extraction Workflow

### Step 1: Extract All Tiles

```bash
# Extract all CHR tiles from ROM
python tools/extract_chr_tiles.py roms/Dragon_Warrior.nes

# Output: extracted_assets/chr_tiles/
#   ├── all_tiles.png      (complete tileset)
#   ├── tile_000.png       (individual tiles)
#   ├── tile_001.png
#   └── ...
```

### Step 2: Advanced Extraction

```bash
# Extract with metadata
python tools/extraction/chr_tile_extractor.py roms/Dragon_Warrior.nes

# Output includes:
#   - Individual tile PNGs
#   - Sprite sheets
#   - JSON metadata file
```

### Step 3: View Extracted Tiles

Open `docs/asset_catalog/chr_tiles.html` in a browser to see all tiles with IDs.

---

## Editing Graphics

### Method 1: Using chr_editor.py

Interactive terminal-based editor:

```bash
# Edit all tiles interactively
python tools/chr_editor.py extracted_assets/chr_tiles/tiles.chr

# Edit specific tile
python tools/chr_editor.py tiles.chr --tile 0x42

# Edit with specific palette
python tools/chr_editor.py tiles.chr --palette 2
```

### Editor Commands

```
Navigation:
  Arrow keys    Move cursor
  Tab           Next tile
  Shift+Tab     Previous tile
  G             Go to tile by ID

Editing:
  0-3           Set pixel color (0-3)
  F             Fill with current color
  C             Copy tile
  V             Paste tile
  H             Flip horizontal
  V             Flip vertical
  R             Rotate 90°

File:
  S             Save
  Q             Quit
  U             Undo
  Ctrl+R        Redo
```

### Method 2: External Editors (Recommended for Complex Edits)

#### YY-CHR
1. Open ROM in YY-CHR
2. Navigate to CHR offset (`$10010` for Dragon Warrior)
3. Edit tiles visually
4. Save changes

#### Tile Layer Pro
1. Open ROM
2. Set to 2bpp NES format
3. Navigate to CHR data
4. Edit and save

### Method 3: PNG Editing

1. Extract tiles to PNG
2. Edit in any image editor (Aseprite, GIMP, etc.)
3. Maintain 4-color palette constraint!
4. Save as indexed PNG
5. Use reinserter to convert back

---

## Reinsertion Process

### Step 1: Validate Your Graphics

```bash
# Validate PNG has correct format
python tools/chr_validator.py my_edited_tile.png

# Expected output:
# ✅ Image size: 8x8 (valid for 1 tile)
# ✅ Colors: 4 (valid for NES)
# ✅ Ready for conversion
```

### Step 2: Convert PNG to CHR

```bash
# Convert single tile
python tools/chr_reinserter.py my_tile.png -o my_tile.chr

# Convert tile sheet (e.g., 16 tiles wide, 8 tiles tall)
python tools/chr_reinserter.py tileset.png --sheet 16x8 -o tileset.chr
```

### Step 3: Update ROM/CHR-ROM

```bash
# Update specific tile in CHR-ROM
python tools/chr_reinserter.py my_tile.png --tile 42 --chr-rom source_files/chr_rom.bin

# Update range of tiles
python tools/chr_reinserter.py tileset.png --start-tile 0 --chr-rom source_files/chr_rom.bin
```

### Step 4: Rebuild ROM

```bash
# Rebuild with updated graphics
python dragon_warrior_build.py
```

---

## Complete Example

### Goal: Edit the Slime Monster Sprite

#### Step 1: Find the Tile

1. Open asset catalog: `docs/asset_catalog/chr_tiles.html`
2. Look for Slime in the sprite section
3. Note: Slime uses tiles **0x00-0x03** (2×2 sprite)

#### Step 2: Extract the Tiles

```bash
python tools/extract_chr_tiles.py roms/Dragon_Warrior.nes
```

#### Step 3: Edit the Tiles

Option A: Use chr_editor.py
```bash
python tools/chr_editor.py extracted_assets/chr_tiles/tiles.chr --tile 0
```

Option B: Edit PNG files
1. Open `extracted_assets/chr_tiles/tile_000.png`
2. Edit in image editor (keep 4 colors!)
3. Save as indexed PNG

#### Step 4: Validate Changes

```bash
python tools/chr_validator.py extracted_assets/chr_tiles/tile_000.png
```

#### Step 5: Reinsert Graphics

```bash
python tools/chr_reinserter.py tile_000.png --tile 0 --chr-rom source_files/chr_rom.bin
python tools/chr_reinserter.py tile_001.png --tile 1 --chr-rom source_files/chr_rom.bin
python tools/chr_reinserter.py tile_002.png --tile 2 --chr-rom source_files/chr_rom.bin
python tools/chr_reinserter.py tile_003.png --tile 3 --chr-rom source_files/chr_rom.bin
```

#### Step 6: Rebuild and Test

```bash
python dragon_warrior_build.py
# Load output/dragon_warrior_modified.nes in emulator
# Fight a Slime to see your changes!
```

---

## Palette Considerations

### NES Palette Constraints

- 4 sprite palettes (4 colors each)
- 4 background palettes (4 colors each)
- Color 0 in each palette is transparent (sprites) or shared (background)

### Dragon Warrior Default Palettes

```
Sprite Palette 0: $0F, $27, $30, $16  (Hero)
Sprite Palette 1: $0F, $16, $30, $12  (Monsters)
Sprite Palette 2: $0F, $29, $30, $19  (NPCs)
Sprite Palette 3: $0F, $30, $27, $17  (Effects)

Background Palette 0: $0F, $30, $10, $00  (Grass/Forest)
Background Palette 1: $0F, $30, $27, $07  (Castle)
Background Palette 2: $0F, $30, $19, $09  (Cave)
Background Palette 3: $0F, $30, $12, $02  (Water)
```

### Using Palettes in Editors

When editing, remember:
- Color index 0 = Background/Transparent
- Color index 1-3 = Visible colors
- Different sprites can use different palettes

---

## Integration with Universal Editor

The GraphicsEditorTab in Universal Editor provides visual editing:

1. Open Universal Editor: `python tools/universal_editor.py`
2. Go to **🎨 Graphics** tab
3. Load CHR data
4. Edit visually
5. Export changes

---

## Troubleshooting

### "Invalid color count"

**Problem:** Your PNG has more than 4 colors.

**Solution:**
1. Reduce to 4 colors (indexed palette)
2. Use image editor's "Posterize" or "Reduce Colors"
3. Re-export as indexed PNG

### "Tile appears corrupted"

**Problem:** Bitplane encoding issue.

**Solution:**
1. Verify file is exactly 16 bytes per tile
2. Check byte order (little-endian)
3. Use chr_validator.py to check format

### "Wrong tile position"

**Problem:** Tile inserted at wrong offset.

**Solution:**
1. Verify tile ID (0-511 for Dragon Warrior)
2. Check if using headerless or headered offset
3. Use `--tile ID` flag explicitly

### "Colors look wrong"

**Problem:** Palette mismatch.

**Solution:**
1. Check which palette the sprite uses
2. Edit palette in Universal Editor's Palette tab
3. Or modify tile colors to match expected palette

---

## Tool Reference

### extract_chr_tiles.py

```bash
python tools/extract_chr_tiles.py ROM_FILE [options]

Options:
  -o, --output DIR     Output directory
  --bank BANK          Extract specific bank (0 or 1)
  --start TILE         Start tile number
  --count COUNT        Number of tiles to extract
  --palette PALETTE    Palette to use (0-3)
```

### chr_reinserter.py

```bash
python tools/chr_reinserter.py INPUT_PNG [options]

Options:
  -o, --output FILE    Output CHR file
  --tile ID            Target tile ID
  --chr-rom FILE       CHR-ROM file to update
  --sheet WxH          Treat input as tile sheet
  --start-tile ID      Starting tile for sheet
```

### chr_validator.py

```bash
python tools/chr_validator.py INPUT_FILE [options]

Options:
  --strict             Strict validation mode
  --report FILE        Output validation report
```

### chr_editor.py

```bash
python tools/chr_editor.py CHR_FILE [options]

Options:
  --tile ID            Edit specific tile
  --palette ID         Use specific palette (0-7)
  --readonly           View-only mode
```

---

## Resources

### External Tools
- [YY-CHR](https://www.romhacking.net/utilities/119/) - Popular CHR editor
- [Tile Layer Pro](https://www.romhacking.net/utilities/108/) - Tile editor
- [NES Screen Tool](https://www.romhacking.net/utilities/802/) - Level design

### Documentation
- [NESDev Wiki - PPU](https://www.nesdev.org/wiki/PPU)
- [CHR Format](https://www.nesdev.org/wiki/CHR_ROM)
- [NES Palette](https://www.nesdev.org/wiki/PPU_palettes)

### Asset Catalog
- `docs/asset_catalog/chr_tiles.html` - All Dragon Warrior tiles
- `docs/asset_catalog/images/chr_tiles_sheet.png` - Complete tileset image
