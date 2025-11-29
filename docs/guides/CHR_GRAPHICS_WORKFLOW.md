# CHR-ROM Graphics Editing Workflow Guide

**Complete Guide to Editing Dragon Warrior Graphics**

Version: 1.0  
Last Updated: November 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [CHR-ROM Basics](#chr-rom-basics)
3. [Required Tools](#required-tools)
4. [Extraction Workflow](#extraction-workflow)
5. [Editing Graphics](#editing-graphics)
6. [Conversion and Reinsertion](#conversion-and-reinsertion)
7. [Testing and Verification](#testing-and-verification)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Techniques](#advanced-techniques)

---

## Introduction

This guide covers the complete workflow for editing CHR-ROM graphics in Dragon Warrior (NES), from extraction through testing. You'll learn how to modify sprites, tiles, and other graphics using modern tools while respecting NES hardware constraints.

### What You Can Modify

- **Monster Sprites** - All 40 enemy graphics
- **Player Character** - Hero sprites (walking, facing directions)
- **Map Tiles** - Terrain, buildings, objects
- **Font Characters** - Text display characters
- **Menu Graphics** - Windows, cursors, icons
- **Battle Backgrounds** - Combat screen graphics

### Prerequisites

- Basic understanding of ROM structure
- Graphics editor (GIMP, Aseprite, Photoshop, etc.)
- Python 3.8+ for conversion scripts
- NES emulator for testing (Mesen recommended)

---

## CHR-ROM Basics

### What is CHR-ROM?

**CHR-ROM (Character ROM)** contains all graphical data for NES games. Dragon Warrior uses:

- **CHR Size:** 8 KB (8192 bytes)
- **Total Tiles:** 512 tiles (256 per pattern table)
- **Tile Size:** 8×8 pixels each
- **Pattern Tables:** 2 banks of 256 tiles

### NES Graphics Constraints

Understanding these limits is crucial for successful CHR editing:

#### Color Palette Restrictions

**4-Color Palettes:**

```
Each palette has 4 colors:
- Color 0: Transparent/Background (shared across all palettes)
- Color 1: First unique color
- Color 2: Second unique color
- Color 3: Third unique color
```

**Available Palettes:**

- **Background:** 4 palettes (16 colors total)
- **Sprites:** 4 palettes (16 colors total)
- **Total NES Colors:** 64 possible colors in master palette

#### Tile Structure

**Each 8×8 tile:**

```
- 2 bits per pixel (4 colors max)
- 16 bytes of data per tile
- Stored as 2 bitplanes
```

**Bitplane Format:**

```
Plane 0: Bits 0-7 (low bits of color index)
Plane 1: Bits 0-7 (high bits of color index)

Combined: Creates 2-bit color value (0-3) per pixel
```

### Sprite Composition

**Monster sprites** are built from multiple 8×8 tiles:

```
Example: Slime sprite
- Composed of 4-6 CHR tiles
- Each tile positioned with X/Y offsets
- Palette assigned per tile
- Sprite data in Bank01.asm
```

---

## Required Tools

### Graphics Editors

**Recommended:**

1. **GIMP** (Free, powerful)
   - Download: https://www.gimp.org/
   - Good for: Batch editing, advanced features
   - Palette support: Excellent

2. **Aseprite** (Paid, pixel art focused)
   - Download: https://www.aseprite.org/
   - Good for: Animation, sprite work
   - Palette support: Excellent

3. **Paint.NET** (Free, Windows)
   - Download: https://www.getpaint.net/
   - Good for: Simple edits
   - Palette support: Basic

**Avoid:**
- MS Paint (no palette support)
- Most online editors (poor NES color handling)

### NES-Specific Tools

**YY-CHR** (NES tile editor)

- **Platform:** Windows (Wine on Mac/Linux)
- **Download:** http://www.romhacking.net/utilities/119/
- **Purpose:** Direct CHR-ROM editing
- **Pros:** Real-time CHR viewing, palette editor
- **Cons:** Less flexible than modern editors

**Tile Molester** (Generic tile editor)

- **Platform:** Java (cross-platform)
- **Download:** http://www.romhacking.net/utilities/109/
- **Purpose:** View/edit raw tile data
- **Pros:** Many format support
- **Cons:** Steeper learning curve

### Emulators with Graphics Tools

**Mesen** (Recommended)

- **Download:** https://www.mesen.ca/
- **Features:**
  - CHR viewer/editor
  - Palette viewer
  - Sprite viewer
  - Real-time editing
  - Debugging tools

**FCEUX**

- **Download:** http://fceux.com/
- **Features:**
  - PPU viewer
  - CHR editor
  - Debugging

### Conversion Scripts

**Included in Project:**

```
tools/
├── extract_chr_tiles.py        # Extract CHR to PNG
├── chr_to_png.py               # CHR → PNG conversion
├── png_to_chr.py               # PNG → CHR conversion (TBD)
└── chr_validator.py            # Validate graphics (TBD)
```

**Note:** Some tools marked "TBD" are planned (see GitHub issues #4).

---

## Extraction Workflow

### Step 1: Extract CHR Data from ROM

**Using Python Script:**

```powershell
# Extract all 512 tiles to individual PNGs
python tools/extract_chr_tiles.py

# Output: extracted_assets/chr_tiles/tile_000.png through tile_511.png
```

**Output Structure:**

```
extracted_assets/
└── chr_tiles/
    ├── tile_000.png
    ├── tile_001.png
    ├── tile_002.png
    ...
    └── tile_511.png
```

**Each PNG:**
- 8×8 pixels
- Indexed color (4 colors)
- NES palette colors

### Step 2: Extract Organized Sprites

**Using Comprehensive Extractor:**

```powershell
python tools/extraction/comprehensive_graphics_extractor.py
```

**Output:**

```
extracted_assets/
└── chr_organized/
    ├── sprites_monsters_01_slimes.png
    ├── sprites_monsters_02_dragons.png
    ├── sprites_monsters_03_undead.png
    ├── sprites_monsters_04_humanoid.png
    ├── sprites_monsters_05_special.png
    ├── sprites_player_hero.png
    ├── tiles_terrain.png
    └── tiles_font.png
```

**These organized sheets** show complete sprites assembled from individual tiles.

### Step 3: Verify Extraction

**Check extraction quality:**

```powershell
python tools/verify_extractions.py
```

**Expected output:**

```
✓ All 512 tiles extracted successfully
✓ PNG dimensions correct (8×8)
✓ Color palettes valid
✓ No missing tiles
```

---

## Editing Graphics

### Method 1: Edit Individual Tiles (Advanced)

**Best for:** Precise tile-level changes, font editing, single tile fixes

**Workflow:**

1. Open `extracted_assets/chr_tiles/tile_XXX.png` in graphics editor

2. **Set up indexed color mode:**

```
GIMP: Image → Mode → Indexed
- Use 4-color palette
- Dithering: None
```

3. **Load NES palette:**

Create palette file with NES colors:

```
NES Palette (example for Slime):
Color 0: #000000 (Black - transparent)
Color 1: #008800 (Green)
Color 2: #00FF00 (Bright Green)
Color 3: #FFFFFF (White)
```

4. **Edit the tile:**

- Use pencil tool (no anti-aliasing!)
- Only use the 4 palette colors
- Keep 8×8 dimensions

5. **Save as PNG:**

```
File → Export As → PNG
- No interlacing
- No compression (or minimal)
```

### Method 2: Edit Organized Sprite Sheets (Recommended)

**Best for:** Monster redesigns, major graphics overhauls

**Workflow:**

1. Open organized sprite sheet:

```
extracted_assets/chr_organized/sprites_monsters_01_slimes.png
```

2. **Maintain structure:**

- Sprite sheets have multiple sprites tiled
- Each sprite is a collection of 8×8 tiles
- Don't change sheet dimensions
- Don't move sprite positions

3. **Edit sprites:**

```
Example: Make Slime blue instead of green
1. Select Slime sprite area
2. Change green pixels to blue
3. Keep black outlines and highlights
4. Use only 4 colors total per sprite
```

4. **Palette constraints:**

Each sprite region must use:
- Maximum 4 colors (including transparent)
- Colors from NES 64-color master palette

### NES Color Palette Reference

**Common NES Colors (Hex RGB):**

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| Black | #000000 | 0,0,0 | Outlines, background |
| White | #FFFFFF | 255,255,255 | Highlights |
| Dark Gray | #808080 | 128,128,128 | Shadows |
| Light Gray | #C0C0C0 | 192,192,192 | Mid-tones |
| Dark Green | #008800 | 0,136,0 | Slime body |
| Bright Green | #00FF00 | 0,255,0 | Slime highlights |
| Dark Blue | #0000AA | 0,0,170 | Water, blue slime |
| Light Blue | #00AAFF | 0,170,255 | Sky |
| Red | #FF0000 | 255,0,0 | Red slime, fire |
| Orange | #FF8800 | 255,136,0 | Flames |
| Brown | #884400 | 136,68,0 | Ground, wood |
| Yellow | #FFFF00 | 255,255,0 | Metal, gold |

**Full NES Palette:** See https://www.nesdev.org/wiki/PPU_palettes

**Palette Tools:**

- **GIMP:** Colors → Colormap
- **Aseprite:** Palette panel
- **Online:** NES Palette Generator

### Editing Best Practices

**DO:**

- ✓ Use indexed color mode
- ✓ Disable anti-aliasing
- ✓ Use pencil/pixel tools
- ✓ Stick to 4 colors per tile/sprite
- ✓ Keep 8×8 tile boundaries
- ✓ Test in emulator frequently

**DON'T:**

- ✗ Use gradients or blending
- ✗ Use more than 4 colors per sprite
- ✗ Change image dimensions
- ✗ Use transparency (except color 0)
- ✗ Apply filters/effects
- ✗ Save as JPEG (lossy compression)

---

## Conversion and Reinsertion

### Current Status

**⚠️ Important:** CHR reinsertion tools are **under development**.

See GitHub issue #4: "Build CHR Reinsertion Tool"

### Manual Reinsertion (Current Method)

**Using YY-CHR:**

1. Open `build/dragon_warrior_rebuilt.nes` in YY-CHR

2. Navigate to CHR-ROM section:

```
View → CHR-ROM
Pattern Table: Select 0 or 1
```

3. **Import edited tile:**

- Right-click tile slot
- Import → From File
- Select your PNG file
- Confirm import

4. **Save ROM:**

```
File → Save
```

5. **Verify in emulator**

### Planned Automated Workflow

**Future tool:** `tools/chr_reinserter.py`

```powershell
# Planned usage:
python tools/chr_reinserter.py --input extracted_assets/chr_organized/ --output build/

# Will:
# 1. Validate PNGs (palette, size, format)
# 2. Convert PNG → CHR format
# 3. Rebuild ROM with new graphics
# 4. Generate verification report
```

**See:** `docs/guides/MODIFICATION_REFERENCE.md` for code locations

### Sprite Data Modification

**Changing sprite composition:**

If you redesign a monster's sprite layout, update sprite data in `source_files/Bank01.asm`:

**Example: Slime sprite definition (line ~4048)**

```assembly
SlimeSprts:
L9B0E:  .byte $55, $32, $64     ; Tile ID, Attributes, X/Y
        .byte $53, $2B, $60     ; Second tile
        .byte $54, $33, $60     ; Third tile
        .byte $00               ; End marker
```

**Tile Attributes byte:**

```
Bits 0-1: Palette (0-3)
Bit 2: Priority (0=behind background, 1=in front)
Bit 3-4: Unused
Bit 5: Flip horizontal
Bit 6: Flip vertical
Bit 7: Unused
```

**Example: Change Slime's palette from 0 to 1:**

```assembly
; Original:
.byte $55, $32, $64
              ^^ Attributes = $32 (binary 00110010)
                 Palette bits = 10 (palette 2)

; Change to palette 1:
.byte $55, $31, $64
              ^^ Attributes = $31 (binary 00110001)
                 Palette bits = 01 (palette 1)
```

---

## Testing and Verification

### Visual Testing

**Step 1: Load in Emulator**

```powershell
# Mesen
mesen.exe build/dragon_warrior_rebuilt.nes

# FCEUX
fceux.exe build/dragon_warrior_rebuilt.nes
```

**Step 2: Navigate to Graphics**

- **Monsters:** Get into a battle
- **Map tiles:** Walk around overworld
- **Fonts:** Open menu, read text
- **Player:** Move character

**Step 3: Check for Issues**

- [ ] Graphics display correctly
- [ ] No glitched tiles
- [ ] Colors are correct
- [ ] No flickering
- [ ] Animations smooth (if applicable)

### Palette Testing

**Use emulator debugging tools:**

**Mesen:**

```
Tools → PPU Viewer
- View current palettes
- See which tiles use which palette
- Verify color assignments
```

**FCEUX:**

```
Tools → PPU Viewer
- Palette viewer
- CHR viewer with palette overlay
```

### CHR Integrity Check

**Planned tool:** `tools/chr_validator.py`

```powershell
# Planned usage:
python tools/chr_validator.py --rom build/dragon_warrior_rebuilt.nes

# Will check:
# - CHR size is exactly 8 KB
# - All tiles are valid
# - No corrupted data
# - Palette usage is correct
```

### Comparison Testing

**Before/After screenshots:**

1. **Before modification:**

```powershell
# Take screenshot in emulator
# Mesen: File → Save Screenshot
```

2. **After modification:**

```powershell
# Rebuild ROM
.\build_rom.ps1

# Load in emulator
# Take same screenshot
# Compare side-by-side
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Graphics Look Corrupted

**Symptoms:**
- Random pixels
- Wrong colors
- Garbled sprites

**Possible Causes:**

1. **Wrong file format**

```
Fix:
- Save as indexed PNG
- No compression
- 8×8 dimensions exactly
```

2. **Too many colors**

```
Fix:
- Reduce to 4 colors max per tile
- Use NES palette colors only
```

3. **Incorrect CHR offset**

```
Fix:
- Verify tile is inserted at correct position
- Check sprite data references correct tile ID
```

#### Issue 2: Colors Are Wrong

**Symptoms:**
- Sprite has wrong colors
- Colors change unexpectedly

**Possible Causes:**

1. **Wrong palette assignment**

```
Fix:
- Check sprite attributes byte
- Verify palette index (0-3)
- Update Bank01.asm sprite data
```

2. **Palette colors changed**

```
Fix:
- Reset palette to original NES colors
- Check palette definition in ROM
```

#### Issue 3: Sprite Doesn't Appear

**Symptoms:**
- Sprite is invisible
- Shows up as blank/black

**Possible Causes:**

1. **All pixels are color 0 (transparent)**

```
Fix:
- Color 0 is transparent
- Use colors 1-3 for visible pixels
```

2. **Sprite data points to empty tile**

```
Fix:
- Check sprite definition in Bank01.asm
- Verify tile IDs are correct
```

#### Issue 4: Graphics Are Offset/Misaligned

**Symptoms:**
- Sprites appear shifted
- Tiles don't line up

**Possible Causes:**

1. **Sprite X/Y offsets wrong**

```
Fix:
- Check sprite data in Bank01.asm
- Adjust X/Y offset bytes
```

2. **Tile boundaries not respected**

```
Fix:
- Graphics must align to 8×8 grid
- Check PNG dimensions
```

#### Issue 5: ROM Doesn't Build After Graphics Change

**Symptoms:**
- Build script fails
- Error messages

**Possible Causes:**

1. **CHR file missing or wrong size**

```
Fix:
- CHR must be exactly 8 KB (8192 bytes)
- Check file wasn't corrupted
```

2. **Invalid tile data**

```
Fix:
- Verify tiles are in correct format
- Re-extract from known good ROM
```

### Debug Tools

**Mesen Debug Features:**

```
Tools → Debugger
- Set breakpoints on CHR access
- Trace which code loads tiles
- Monitor palette writes

Tools → Event Viewer
- See when CHR is updated
- Track sprite rendering
```

**FCEUX Debug:**

```
Tools → PPU Viewer
- Live CHR view
- Palette editor
- OAM (sprite) viewer
```

---

## Advanced Techniques

### Palette Swapping

**Change monster colors without editing graphics:**

1. Find palette definition in ROM
2. Edit palette colors
3. All sprites using that palette change color

**Example: Make all slimes blue**

```assembly
; In Bank01.asm, find slime palette
SlimePalette:
    .byte $0F  ; Background (black)
    .byte $0A  ; Dark green  ← Change to $02 (dark blue)
    .byte $2A  ; Light green ← Change to $12 (light blue)
    .byte $30  ; White (keep)
```

### Animated Sprites

**NES sprites don't animate automatically, but you can:**

1. Create multiple versions of a sprite
2. Use different tiles for each frame
3. Modify sprite loading code to switch tiles

**Example: Walking animation**

```assembly
; Define animation frames
HeroWalkFrame1: .byte $10, $11, $12, $13  ; Tile IDs frame 1
HeroWalkFrame2: .byte $14, $15, $16, $17  ; Tile IDs frame 2

; Code switches between frames based on step counter
```

### Tile Reuse and Flipping

**Save tile slots using flips:**

```assembly
; Instead of separate left/right tiles:
; Use same tile with horizontal flip bit

.byte $55, $32, $64     ; Tile facing right
.byte $55, $72, $64     ; Same tile, flipped (bit 5 set)
                 ^^ Bit 5 (0x40) sets horizontal flip
```

**Flip bits:**
- Bit 5 (`$20`): Horizontal flip
- Bit 6 (`$40`): Vertical flip
- Both (`$60`): 180° rotation

### CHR Bank Switching

**Dragon Warrior uses MMC1 mapper:**

```assembly
; Switch CHR banks for different areas
; Bank 0: Town/castle graphics
; Bank 1: Cave/dungeon graphics

LDA #$00          ; Select CHR bank 0
STA $A000         ; MMC1 CHR control
```

**You can:**
- Have different graphics per area
- Double your total tile count
- Load battle vs. overworld graphics

### Compression and Space Optimization

**Techniques to fit more graphics:**

1. **Reuse tiles**

```
- Use flipping for symmetrical sprites
- Share common tiles (like outlines)
- Use palette swaps for variants
```

2. **Optimize tile usage**

```
- Remove unused tiles
- Combine similar tiles
- Use pattern table switching
```

3. **8×16 sprite mode** (advanced)

```
; Switch to tall sprite mode for larger characters
LDA #$20
STA $2000  ; PPUCTRL - set bit 5

; Sprites are now 8×16 instead of 8×8
; Double the height, but uses 2 consecutive tiles
```

---

## Quick Reference

### File Locations

| Asset Type | Location | Format |
|------------|----------|--------|
| CHR ROM | Original ROM offset 0x8010-0xA010 | Raw binary |
| Extracted Tiles | `extracted_assets/chr_tiles/` | PNG (8×8) |
| Organized Sprites | `extracted_assets/chr_organized/` | PNG sheets |
| Sprite Data | `source_files/Bank01.asm` line ~4000 | Assembly |
| Palettes | `source_files/Bank01.asm` | Assembly |

### Tool Quick Commands

```powershell
# Extract all tiles
python tools/extract_chr_tiles.py

# Extract organized sprites
python tools/extraction/comprehensive_graphics_extractor.py

# Verify extraction
python tools/verify_extractions.py

# Rebuild ROM
.\build_rom.ps1

# Enhanced build with report
.\build_enhanced.ps1 -Report
```

### NES Graphics Limits

| Limit | Value |
|-------|-------|
| Tile Size | 8×8 pixels |
| Colors per tile | 4 (including transparent) |
| Total tiles | 512 (2 banks × 256) |
| CHR Size | 8 KB |
| Background palettes | 4 |
| Sprite palettes | 4 |
| Colors per palette | 4 |
| Sprites on screen | 64 max |
| Sprites per scanline | 8 max |

### Hex Attribute Byte Calculator

```
Palette (bits 0-1):
  00 = Palette 0
  01 = Palette 1
  10 = Palette 2
  11 = Palette 3

Flip Horizontal (bit 5): Add $20
Flip Vertical (bit 6): Add $40

Examples:
  $00 = Palette 0, no flip
  $01 = Palette 1, no flip
  $20 = Palette 0, H-flip
  $21 = Palette 1, H-flip
  $40 = Palette 0, V-flip
  $60 = Palette 0, H+V flip (180°)
```

---

## Next Steps

### After Completing This Guide

1. **Practice with simple edits**
   - Change one monster's colors
   - Modify a few map tiles
   - Test thoroughly

2. **Explore advanced modifications**
   - Create new monsters from scratch
   - Design custom tilesets
   - Implement sprite animations

3. **Contribute improvements**
   - Share your graphics mods
   - Submit to community
   - Document your techniques

### Related Documentation

- [**ROM Hacking Guide**](ROM_HACKING_GUIDE.md) - Complete modding reference
- [**Modification Reference**](MODIFICATION_REFERENCE.md) - Quick lookup guide
- [**Game Formulas**](../technical/GAME_FORMULAS.md) - Technical specifications

### Future Enhancements

**Planned tools (see GitHub issues):**

- Issue #4: CHR Reinsertion Tool (automated PNG → ROM)
- Issue #5: Interactive Map Editor (visual tile editor)
- Issue #7: Music/Sound Effect Editor
- Issue #10: Video tutorials

---

## Credits

- **Original Game** - Chunsoft, Enix (1989)
- **CHR Format** - Nintendo Entertainment System PPU specification
- **Tools** - Community ROM hacking tools (YY-CHR, Tile Molester, etc.)
- **This Guide** - Compiled from NES dev documentation and project experience

---

**Happy Graphics Hacking! 🎨🐉**

For questions, issues, or contributions, see the main [README.md](../../README.md) and [CONTRIBUTING.md](../project/CONTRIBUTING.md).
