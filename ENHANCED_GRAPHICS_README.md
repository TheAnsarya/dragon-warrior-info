# Dragon Warrior Enhanced Graphics Extraction

This enhanced graphics extraction system focuses on extracting the text font and slime monster graphics from Dragon Warrior NES with proper colors and palettes for easy viewing and editing.

## What's New

✅ **Fixed PNG extraction** - No more blank black squares!  
✅ **Proper NES palettes** - Graphics now display with correct colors as seen in-game  
✅ **Font extraction** - Complete text font as viewable/editable sheet  
✅ **Slime monster focus** - Slime graphics with accurate blue/white/red color variants  
✅ **Based on disassembly** - Uses actual ROM structure analysis for accuracy  

## Quick Start

```bash
# Extract enhanced graphics
python tools/extraction/enhanced_graphics_extractor.py "roms/Dragon Warrior (U) (PRG0) [!].nes"

# Insert modified graphics back (experimental)
python tools/extraction/graphics_inserter.py "roms/Dragon Warrior (U) (PRG0) [!].nes" extracted_assets/enhanced
```

## Extracted Files

### Font Graphics
- `dragon_warrior_font_complete.png` - Complete font sheet (16x8 grid, 4x scale)
- `font_char_XX_Y.png` - Individual characters (e.g., `font_char_24_A.png` for letter A)
- `font_character_map.json` - Character to tile index mapping

### Slime Monster Graphics  
- `slime_blue_frame_XX_tile_YY.png` - Blue slime animation frames (8x scale)
- `slime_red_frame_XX_tile_YY.png` - Red slime variants
- `slime_metal_frame_XX_tile_YY.png` - Metal slime variants
- `slime_palettes.json` - Color palette data for all slime types

## Color Palettes

### Slime Palettes (from disassembly analysis)
- **Blue Slime**: Cyan-blue body, magenta details, white highlights
- **Red Slime**: Red-orange body, darker red details, white highlights  
- **Metal Slime**: Black body, silver details, white highlights

### Font Palette
- Black, dark gray, light gray, white (standard text colors)

## Technical Details

### NES Graphics Structure
- **CHR-ROM Location**: `0x8010` (32KB after PRG-ROM header)
- **Pattern Tables**: 2 tables, 256 tiles each (8x8 pixels, 2bpp)
- **Font Location**: First pattern table (tiles 0x00-0x7F)
- **Sprites Location**: Second pattern table (tiles 0x80-0xFF)

### Font Character Mapping
Based on Dragon Warrior disassembly analysis:
```
Uppercase: A=0x24, B=0x25, ..., Z=0x3D
Lowercase: a=0x04, b=0x05, ..., z=0x1D  
Numbers:   0=0x50, 1=0x51, ..., 9=0x59
Symbols:   '=0x40, .=0x47, ,=0x48, etc.
```

### Slime Graphics Data
From `SlimeSprts` data in disassembly:
```
Frame 0: Tile 0x55 (base slime shape)
Frame 1: Tile 0x53 (animation frame)
Frame 2: Tile 0x54 (animation frame)
```

## How to Edit Graphics

### Editing the Font
1. Open `dragon_warrior_font_complete.png` in your image editor
2. Each character is in an 8x8 pixel grid, scaled 4x (32x32 pixels on screen)
3. Use only 4 colors: black, dark gray, light gray, white
4. Edit characters in-place or extract individual character files
5. Use the inserter tool to patch back into ROM

### Editing Slime Graphics
1. Open any `slime_*_frame_*.png` file  
2. Each slime is 8x8 pixels, scaled 8x (64x64 pixels on screen)
3. Use the exact palette colors from `slime_palettes.json`
4. Maintain the slime's basic shape for game compatibility
5. Save and use inserter to patch ROM

### Palette Colors (RGB values)
```json
Blue Slime:  [(0,102,120), (160,20,100), (236,238,236), (152,150,152)]
Red Slime:   [(152,34,32), (136,20,176), (236,238,236), (152,150,152)]  
Metal Slime: [(84,84,84), (136,20,176), (236,238,236), (152,150,152)]
```

## ROM Patching

The graphics inserter tool can write modified graphics back to the ROM:

```bash
python tools/extraction/graphics_inserter.py original.nes extracted_assets/enhanced -o modified.nes
```

**⚠️ Warning**: Always backup your original ROM! Test modified ROMs in an emulator first.

## File Structure

```
extracted_assets/enhanced/
├── dragon_warrior_font_complete.png     # Complete font sheet
├── font_character_map.json              # Character mappings  
├── font_char_04_a.png                   # Individual characters
├── font_char_24_A.png
├── ...
├── slime_blue_frame_00_tile_55.png      # Slime animation frames
├── slime_red_frame_00_tile_55.png
├── slime_metal_frame_00_tile_55.png
├── ...
├── slime_palettes.json                  # Palette data
└── slime_all_variants_composite.png     # All slimes in one image
```

## Technical Notes

- Uses proper NES NTSC color palette for accurate colors
- 2bpp tile decoding matches NES PPU behavior  
- Palette indices match Dragon Warrior disassembly data
- Graphics are scaled up for easy editing and viewing
- JSON files provide all metadata needed for re-insertion

## Troubleshooting

**Q: Graphics still look wrong?**  
A: Make sure you're using the correct ROM version: "Dragon Warrior (U) (PRG0) [!].nes"

**Q: Can't see small details?**  
A: Characters are 8x8 pixels originally - use high zoom in your image editor

**Q: Colors don't match game?**  
A: Use the exact RGB values from the palette JSON files

**Q: Modified ROM doesn't work?**  
A: Ensure graphics maintain original dimensions and use only palette colors

## Based on Disassembly Analysis

This extraction is based on detailed analysis of the Dragon Warrior disassembly:
- Font character mappings from `Dragon_Warrior_Defines.asm`
- Slime sprite data from `SlimeSprts` in `Bank01.asm`  
- Color palettes from `BSlimePal`, `RSlimePal`, etc. in `Bank00.asm`
- CHR-ROM structure from header analysis

The result is accurate, properly colored graphics that match what you see in-game!