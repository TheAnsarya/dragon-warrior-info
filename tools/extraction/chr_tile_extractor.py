#!/usr/bin/env python3
"""
Dragon Warrior CHR-ROM Tile Extractor

Extracts all tiles from the CHR-ROM and organizes them into meaningful categories:
- Background tiles (terrain, castle walls, dungeon tiles, etc.)
- Character sprites (hero, NPCs, enemies)
- Text font characters
- UI elements

CHR-ROM Structure:
- Pattern Table 0: $0000-$0FFF (4KB) - Background tiles and sprites
- Pattern Table 1: $1000-$1FFF (4KB) - Text font and UI elements

Each tile is 8x8 pixels, 2 bits per pixel (4 colors)
Tile format: 16 bytes per tile
- Bytes 0-7: Low bit plane
- Bytes 8-15: High bit plane
"""

import os
import sys
from pathlib import Path
from PIL import Image
import json

# NES color palette (approximate NTSC colors)
NES_PALETTE = [
    (84, 84, 84),     # 0x00 - Dark gray
    (0, 30, 116),     # 0x01 - Dark blue
    (8, 16, 144),     # 0x02 - Purple-blue
    (48, 0, 136),     # 0x03 - Purple
    (68, 0, 100),     # 0x04 - Dark magenta
    (92, 0, 48),      # 0x05 - Dark red
    (84, 4, 0),       # 0x06 - Brown
    (60, 24, 0),      # 0x07 - Dark orange
    (32, 42, 0),      # 0x08 - Dark yellow
    (8, 58, 0),       # 0x09 - Dark green
    (0, 64, 0),       # 0x0A - Green
    (0, 60, 0),       # 0x0B - Green-teal
    (0, 50, 60),      # 0x0C - Teal
    (0, 0, 0),        # 0x0D - Black
    (0, 0, 0),        # 0x0E - Black
    (0, 0, 0),        # 0x0F - Black

    (152, 150, 152),  # 0x10 - Light gray
    (8, 76, 196),     # 0x11 - Blue
    (48, 50, 236),    # 0x12 - Light purple-blue
    (92, 30, 228),    # 0x13 - Light purple
    (136, 20, 176),   # 0x14 - Magenta
    (160, 20, 100),   # 0x15 - Pink-red
    (152, 34, 32),    # 0x16 - Red
    (120, 60, 0),     # 0x17 - Orange
    (84, 90, 0),      # 0x18 - Yellow-orange
    (40, 114, 0),     # 0x19 - Yellow-green
    (8, 124, 0),      # 0x1A - Light green
    (0, 118, 40),     # 0x1B - Green-cyan
    (0, 102, 120),    # 0x1C - Cyan
    (0, 0, 0),        # 0x1D - Black
    (0, 0, 0),        # 0x1E - Black
    (0, 0, 0),        # 0x1F - Black

    (236, 238, 236),  # 0x20 - White
    (76, 154, 236),   # 0x21 - Sky blue
    (120, 124, 236),  # 0x22 - Light blue
    (176, 98, 236),   # 0x23 - Light purple
    (228, 84, 236),   # 0x24 - Pink
    (236, 88, 180),   # 0x25 - Light pink
    (236, 106, 100),  # 0x26 - Salmon
    (212, 136, 32),   # 0x27 - Light orange
    (160, 170, 0),    # 0x28 - Yellow
    (116, 196, 0),    # 0x29 - Light yellow-green
    (76, 208, 32),    # 0x2A - Lime green
    (56, 204, 108),   # 0x2B - Cyan-green
    (56, 180, 204),   # 0x2C - Light cyan
    (60, 60, 60),     # 0x2D - Dark gray
    (0, 0, 0),        # 0x2E - Black
    (0, 0, 0),        # 0x2F - Black

    (236, 238, 236),  # 0x30 - White
    (168, 204, 236),  # 0x31 - Pale blue
    (188, 188, 236),  # 0x32 - Pale purple
    (212, 178, 236),  # 0x33 - Pale pink-purple
    (236, 174, 236),  # 0x34 - Pale pink
    (236, 174, 212),  # 0x35 - Very pale pink
    (236, 180, 176),  # 0x36 - Pale salmon
    (228, 196, 144),  # 0x37 - Pale orange
    (204, 210, 120),  # 0x38 - Pale yellow
    (180, 222, 120),  # 0x39 - Pale yellow-green
    (168, 226, 144),  # 0x3A - Pale green
    (152, 226, 180),  # 0x3B - Pale cyan-green
    (160, 214, 228),  # 0x3C - Pale cyan
    (160, 162, 160),  # 0x3D - Gray
    (0, 0, 0),        # 0x3E - Black
    (0, 0, 0),        # 0x3F - Black
]

# Dragon Warrior palettes (from earlier extraction)
DW_PALETTES = {
    'background': [0x0F, 0x29, 0x1A, 0x09],  # Black, light yellow-green, light green, dark green
    'sprite0': [0x0F, 0x36, 0x17, 0x0F],     # Black, pale salmon, orange, black
    'sprite1': [0x0F, 0x30, 0x27, 0x17],     # Black, white, light orange, orange
}

class CHRExtractor:
    def __init__(self, rom_path, chr_offset=0x10010, chr_size=0x4000):
        """Initialize CHR extractor with ROM path and CHR-ROM location."""
        self.rom_path = Path(rom_path)
        self.chr_offset = chr_offset
        self.chr_size = chr_size

        # Read ROM
        with open(self.rom_path, 'rb') as f:
            f.seek(chr_offset)
            self.chr_data = f.read(chr_size)

        # Calculate tile count (16 bytes per tile)
        self.tile_count = len(self.chr_data) // 16
        print(f"Loaded CHR-ROM: {len(self.chr_data)} bytes, {self.tile_count} tiles")

    def decode_tile(self, tile_index, palette_indices):
        """
        Decode a single 8x8 tile from CHR-ROM.

        Args:
            tile_index: Tile number (0-511)
            palette_indices: List of 4 NES palette indices for colors 0-3

        Returns:
            PIL Image of the tile
        """
        offset = tile_index * 16
        if offset + 16 > len(self.chr_data):
            raise ValueError(f"Tile {tile_index} out of range")

        # Get tile data
        tile_data = self.chr_data[offset:offset+16]
        low_plane = tile_data[0:8]
        high_plane = tile_data[8:16]

        # Create 8x8 image
        img = Image.new('RGB', (8, 8))
        pixels = img.load()

        # Decode each pixel
        for y in range(8):
            for x in range(8):
                # Get bit from each plane
                bit_pos = 7 - x
                low_bit = (low_plane[y] >> bit_pos) & 1
                high_bit = (high_plane[y] >> bit_pos) & 1

                # Combine to get palette index (0-3)
                color_index = (high_bit << 1) | low_bit

                # Get NES palette color
                nes_color = palette_indices[color_index]
                rgb = NES_PALETTE[nes_color]

                pixels[x, y] = rgb

        return img

    def extract_tile_range(self, start_tile, end_tile, palette_name, output_dir, category_name):
        """Extract a range of tiles and save as individual images."""
        output_path = Path(output_dir) / category_name
        output_path.mkdir(parents=True, exist_ok=True)

        palette = DW_PALETTES.get(palette_name, DW_PALETTES['background'])

        tiles_extracted = []
        for tile_idx in range(start_tile, end_tile + 1):
            try:
                tile_img = self.decode_tile(tile_idx, palette)

                # Save individual tile
                tile_file = output_path / f"tile_{tile_idx:03X}.png"
                tile_img.save(tile_file)

                tiles_extracted.append({
                    'index': tile_idx,
                    'hex': f"0x{tile_idx:03X}",
                    'file': f"tile_{tile_idx:03X}.png"
                })
            except Exception as e:
                print(f"Error extracting tile {tile_idx:03X}: {e}")

        # Save metadata
        metadata = {
            'category': category_name,
            'palette': palette_name,
            'palette_colors': [f"0x{c:02X}" for c in palette],
            'tile_range': {
                'start': start_tile,
                'end': end_tile,
                'start_hex': f"0x{start_tile:03X}",
                'end_hex': f"0x{end_tile:03X}"
            },
            'tiles': tiles_extracted,
            'total_tiles': len(tiles_extracted)
        }

        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Extracted {len(tiles_extracted)} tiles to {output_path}")
        return metadata

    def create_tile_sheet(self, start_tile, end_tile, palette_name, output_file, tiles_per_row=16):
        """Create a tile sheet showing multiple tiles in a grid."""
        palette = DW_PALETTES.get(palette_name, DW_PALETTES['background'])

        tile_count = end_tile - start_tile + 1
        rows = (tile_count + tiles_per_row - 1) // tiles_per_row

        # Create sheet image (8px tiles + 1px borders)
        sheet_width = tiles_per_row * 9 + 1
        sheet_height = rows * 9 + 1
        sheet = Image.new('RGB', (sheet_width, sheet_height), color=(0, 0, 0))

        for idx, tile_idx in enumerate(range(start_tile, end_tile + 1)):
            try:
                tile_img = self.decode_tile(tile_idx, palette)

                # Calculate position
                row = idx // tiles_per_row
                col = idx % tiles_per_row
                x = col * 9 + 1
                y = row * 9 + 1

                # Paste tile
                sheet.paste(tile_img, (x, y))
            except Exception as e:
                print(f"Error in tile sheet for tile {tile_idx:03X}: {e}")

        sheet.save(output_file)
        print(f"Created tile sheet: {output_file} ({tile_count} tiles)")
        return sheet

    def extract_all_tiles(self, output_dir):
        """Extract all tiles organized by category."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        categories = [
            # Pattern Table 0 (0x000-0x0FF)
            {'name': 'background', 'start': 0x00, 'end': 0xFF, 'palette': 'background',
             'description': 'Background tiles: terrain, walls, objects'},

            # Pattern Table 1 (0x100-0x1FF)
            {'name': 'font_and_ui', 'start': 0x100, 'end': 0x1FF, 'palette': 'background',
             'description': 'Text font, numbers, UI elements'},
        ]

        extraction_report = {
            'rom': str(self.rom_path),
            'chr_offset': f"0x{self.chr_offset:X}",
            'chr_size': self.chr_size,
            'total_tiles': self.tile_count,
            'categories': []
        }

        for cat in categories:
            print(f"\nExtracting {cat['name']}: tiles ${cat['start']:03X}-${cat['end']:03X}")

            # Extract individual tiles
            metadata = self.extract_tile_range(
                cat['start'], cat['end'],
                cat['palette'], output_dir, cat['name']
            )

            # Create tile sheet
            sheet_file = output_path / f"{cat['name']}_sheet.png"
            self.create_tile_sheet(
                cat['start'], cat['end'],
                cat['palette'], sheet_file
            )

            metadata['description'] = cat['description']
            metadata['sheet'] = str(sheet_file.name)
            extraction_report['categories'].append(metadata)

        # Save overall report
        report_file = output_path / 'extraction_report.json'
        with open(report_file, 'w') as f:
            json.dump(extraction_report, f, indent=2)

        print(f"\n✅ CHR extraction complete!")
        print(f"Report: {report_file}")
        return extraction_report


def main():
    # Paths
    rom_path = Path(__file__).parent.parent.parent / 'roms' / 'Dragon Warrior (U) (PRG0) [!].nes'
    output_dir = Path(__file__).parent.parent.parent / 'extracted_assets' / 'chr_tiles'

    if not rom_path.exists():
        print(f"❌ ROM not found: {rom_path}")
        sys.exit(1)

    # Extract all tiles
    extractor = CHRExtractor(rom_path)
    extractor.extract_all_tiles(output_dir)

    print(f"\n📁 Output directory: {output_dir}")


if __name__ == '__main__':
    main()
