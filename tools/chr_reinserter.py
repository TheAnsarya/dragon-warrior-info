#!/usr/bin/env python3
"""
Dragon Warrior CHR Reinserter

Converts PNG graphics to NES 2bpp planar CHR format and updates the ROM/chr_rom.bin.

NES CHR Format:
- Each tile is 8x8 pixels, 4 colors (2-bit per pixel)
- 16 bytes per tile: 8 bytes for bitplane 0, 8 bytes for bitplane 1
- Pixel value = bit0 + (bit1 << 1)

Usage:
    # Convert a single PNG to CHR tile(s)
    python chr_reinserter.py input.png -o output.chr
    
    # Update specific tile in CHR-ROM
    python chr_reinserter.py input.png --tile 42 --chr-rom source_files/chr_rom.bin
    
    # Update all tiles from a tile sheet
    python chr_reinserter.py tileset.png --sheet 16x32 --chr-rom source_files/chr_rom.bin
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install pillow")
    sys.exit(1)


class PaletteValidator:
    """Validates images against NES palette constraints."""
    
    def __init__(self):
        # NES can only display 4 colors per palette (including transparency)
        self.max_colors = 4
    
    def get_unique_colors(self, img: Image.Image) -> List[Tuple[int, ...]]:
        """Get unique colors in an image."""
        if img.mode == 'P':
            # Paletted image - get actual palette colors used
            img = img.convert('RGB')
        elif img.mode == 'RGBA':
            # Convert transparent pixels to a marker color
            pixels = list(img.getdata())
            unique = set()
            for p in pixels:
                if p[3] < 128:  # Transparent
                    unique.add((0, 0, 0, 0))  # Mark as transparent
                else:
                    unique.add(p[:3])
            return list(unique)
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        return list(set(img.getdata()))
    
    def validate_tile_colors(self, img: Image.Image, tile_x: int, tile_y: int, 
                            tile_size: int = 8) -> Tuple[bool, str]:
        """
        Validate that an 8x8 tile region has at most 4 colors.
        
        Returns (is_valid, message).
        """
        left = tile_x * tile_size
        top = tile_y * tile_size
        right = left + tile_size
        bottom = top + tile_size
        
        if right > img.width or bottom > img.height:
            return False, f"Tile ({tile_x}, {tile_y}) is outside image bounds"
        
        tile = img.crop((left, top, right, bottom))
        colors = self.get_unique_colors(tile)
        
        if len(colors) > self.max_colors:
            return False, f"Tile ({tile_x}, {tile_y}) has {len(colors)} colors (max 4)"
        
        return True, f"Tile ({tile_x}, {tile_y}) OK: {len(colors)} colors"
    
    def validate_image(self, img: Image.Image) -> Tuple[bool, List[str]]:
        """
        Validate entire image as a tile sheet.
        
        Returns (all_valid, list of messages).
        """
        if img.width % 8 != 0 or img.height % 8 != 0:
            return False, [f"Image dimensions ({img.width}x{img.height}) must be multiples of 8"]
        
        tiles_x = img.width // 8
        tiles_y = img.height // 8
        
        messages = []
        all_valid = True
        
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                valid, msg = self.validate_tile_colors(img, tx, ty)
                if not valid:
                    all_valid = False
                    messages.append(msg)
        
        if all_valid:
            messages.append(f"✓ All {tiles_x * tiles_y} tiles are valid")
        
        return all_valid, messages


class CHREncoder:
    """Encodes images to NES CHR format."""
    
    def __init__(self, palette: Optional[List[Tuple[int, int, int]]] = None):
        """
        Initialize encoder with optional palette mapping.
        
        palette: 4 RGB tuples mapping colors to NES color indices 0-3.
                 If None, uses grayscale (black=0, dark=1, light=2, white=3)
        """
        self.palette = palette or [
            (0, 0, 0),         # Index 0: Transparent/black
            (85, 85, 85),      # Index 1: Dark gray
            (170, 170, 170),   # Index 2: Light gray
            (255, 255, 255),   # Index 3: White
        ]
    
    def color_distance(self, c1: Tuple[int, ...], c2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two RGB colors."""
        r1, g1, b1 = c1[:3]
        r2, g2, b2 = c2
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
    def map_color_to_index(self, color: Tuple[int, ...]) -> int:
        """Map an RGB color to the nearest palette index (0-3)."""
        # Handle transparent pixels
        if len(color) == 4 and color[3] < 128:
            return 0  # Transparent = index 0
        
        # Find closest palette color
        min_dist = float('inf')
        best_idx = 0
        
        for idx, pal_color in enumerate(self.palette):
            dist = self.color_distance(color, pal_color)
            if dist < min_dist:
                min_dist = dist
                best_idx = idx
        
        return best_idx
    
    def encode_tile(self, img: Image.Image, tile_x: int = 0, tile_y: int = 0) -> bytes:
        """
        Encode an 8x8 tile from an image to 16 bytes of CHR data.
        
        Returns 16 bytes: first 8 are bitplane 0, next 8 are bitplane 1.
        """
        # Extract 8x8 tile region
        left = tile_x * 8
        top = tile_y * 8
        tile_img = img.crop((left, top, left + 8, top + 8))
        
        if tile_img.mode == 'P':
            tile_img = tile_img.convert('RGBA')
        elif tile_img.mode == 'RGB':
            tile_img = tile_img.convert('RGB')
        
        pixels = list(tile_img.getdata())
        
        # Initialize bitplanes
        plane0 = bytearray(8)
        plane1 = bytearray(8)
        
        for y in range(8):
            for x in range(8):
                pixel_idx = y * 8 + x
                color = pixels[pixel_idx]
                palette_idx = self.map_color_to_index(color)
                
                # Split into bitplanes
                bit0 = palette_idx & 1
                bit1 = (palette_idx >> 1) & 1
                
                # Set bits (MSB = leftmost pixel)
                bit_pos = 7 - x
                if bit0:
                    plane0[y] |= (1 << bit_pos)
                if bit1:
                    plane1[y] |= (1 << bit_pos)
        
        return bytes(plane0 + plane1)
    
    def encode_image(self, img: Image.Image) -> bytes:
        """
        Encode an entire image as CHR tiles.
        
        Image dimensions must be multiples of 8.
        Returns all tiles concatenated.
        """
        if img.width % 8 != 0 or img.height % 8 != 0:
            raise ValueError(f"Image dimensions ({img.width}x{img.height}) must be multiples of 8")
        
        tiles_x = img.width // 8
        tiles_y = img.height // 8
        
        chr_data = bytearray()
        
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                tile_data = self.encode_tile(img, tx, ty)
                chr_data.extend(tile_data)
        
        return bytes(chr_data)


class CHRDecoder:
    """Decodes NES CHR format to images."""
    
    def __init__(self, palette: Optional[List[Tuple[int, int, int]]] = None):
        self.palette = palette or [
            (0, 0, 0),
            (85, 85, 85),
            (170, 170, 170),
            (255, 255, 255),
        ]
    
    def decode_tile(self, chr_data: bytes) -> Image.Image:
        """Decode 16 bytes of CHR data to an 8x8 PIL Image."""
        if len(chr_data) != 16:
            raise ValueError("CHR tile data must be exactly 16 bytes")
        
        img = Image.new('RGB', (8, 8))
        pixels = img.load()
        
        for y in range(8):
            plane0 = chr_data[y]
            plane1 = chr_data[y + 8]
            
            for x in range(8):
                bit_pos = 7 - x
                bit0 = (plane0 >> bit_pos) & 1
                bit1 = (plane1 >> bit_pos) & 1
                palette_idx = bit0 | (bit1 << 1)
                pixels[x, y] = self.palette[palette_idx]
        
        return img


class CHRReinserter:
    """Main tool for reinserting CHR graphics."""
    
    def __init__(self, chr_rom_path: Optional[str] = None):
        self.chr_rom_path = Path(chr_rom_path) if chr_rom_path else None
        self.chr_data = None
        
        if self.chr_rom_path and self.chr_rom_path.exists():
            with open(self.chr_rom_path, 'rb') as f:
                self.chr_data = bytearray(f.read())
            print(f"Loaded CHR-ROM: {self.chr_rom_path} ({len(self.chr_data)} bytes)")
    
    def convert_png_to_chr(self, png_path: str, output_path: Optional[str] = None) -> bytes:
        """
        Convert PNG to CHR format.
        
        If output_path is provided, saves to file.
        Returns CHR data bytes.
        """
        img = Image.open(png_path)
        print(f"Input image: {png_path} ({img.width}x{img.height}, {img.mode})")
        
        # Validate
        validator = PaletteValidator()
        valid, messages = validator.validate_image(img)
        for msg in messages:
            print(f"  {msg}")
        
        if not valid:
            raise ValueError("Image validation failed")
        
        # Encode
        encoder = CHREncoder()
        chr_data = encoder.encode_image(img)
        
        tiles = len(chr_data) // 16
        print(f"Encoded {tiles} tiles ({len(chr_data)} bytes)")
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(chr_data)
            print(f"Saved to: {output_path}")
        
        return chr_data
    
    def update_tile(self, png_path: str, tile_id: int):
        """Update a specific tile in CHR-ROM with PNG data."""
        if self.chr_data is None:
            raise ValueError("No CHR-ROM loaded")
        
        img = Image.open(png_path)
        
        if img.width != 8 or img.height != 8:
            # Assume first tile if larger image
            print(f"Note: Using first 8x8 tile from {img.width}x{img.height} image")
        
        encoder = CHREncoder()
        tile_data = encoder.encode_tile(img, 0, 0)
        
        offset = tile_id * 16
        if offset + 16 > len(self.chr_data):
            raise ValueError(f"Tile {tile_id} is beyond CHR-ROM size")
        
        # Replace tile data
        self.chr_data[offset:offset + 16] = tile_data
        print(f"Updated tile {tile_id} at offset 0x{offset:04X}")
    
    def update_tiles_from_sheet(self, png_path: str, start_tile: int = 0, 
                                 tiles_per_row: int = 16):
        """
        Update multiple tiles from a tile sheet PNG.
        
        Reads tiles left-to-right, top-to-bottom from the sheet.
        """
        if self.chr_data is None:
            raise ValueError("No CHR-ROM loaded")
        
        img = Image.open(png_path)
        
        if img.width % 8 != 0 or img.height % 8 != 0:
            raise ValueError(f"Image dimensions must be multiples of 8")
        
        tiles_x = img.width // 8
        tiles_y = img.height // 8
        total_tiles = tiles_x * tiles_y
        
        print(f"Updating {total_tiles} tiles starting at tile {start_tile}")
        
        encoder = CHREncoder()
        
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                tile_idx = ty * tiles_x + tx
                target_tile = start_tile + tile_idx
                offset = target_tile * 16
                
                if offset + 16 > len(self.chr_data):
                    print(f"Warning: Tile {target_tile} beyond CHR-ROM, stopping")
                    break
                
                tile_data = encoder.encode_tile(img, tx, ty)
                self.chr_data[offset:offset + 16] = tile_data
        
        print(f"Updated {min(total_tiles, (len(self.chr_data) - start_tile * 16) // 16)} tiles")
    
    def save_chr_rom(self, output_path: Optional[str] = None):
        """Save modified CHR-ROM."""
        if self.chr_data is None:
            raise ValueError("No CHR-ROM data to save")
        
        path = Path(output_path) if output_path else self.chr_rom_path
        if path is None:
            raise ValueError("No output path specified")
        
        with open(path, 'wb') as f:
            f.write(self.chr_data)
        
        print(f"Saved CHR-ROM: {path} ({len(self.chr_data)} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG graphics to NES CHR format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PNG to CHR file
  python chr_reinserter.py sprite.png -o sprite.chr
  
  # Update tile 42 in CHR-ROM
  python chr_reinserter.py tile.png --tile 42 --chr-rom source_files/chr_rom.bin
  
  # Update multiple tiles from a sheet starting at tile 0
  python chr_reinserter.py tileset.png --start-tile 0 --chr-rom source_files/chr_rom.bin
  
  # Just validate a PNG
  python chr_reinserter.py sprite.png --validate
        """
    )
    
    parser.add_argument('input', help='Input PNG file')
    parser.add_argument('-o', '--output', help='Output CHR file')
    parser.add_argument('--tile', type=int, help='Update specific tile ID in CHR-ROM')
    parser.add_argument('--start-tile', type=int, default=0,
                        help='Starting tile ID for sheet import')
    parser.add_argument('--chr-rom', help='CHR-ROM file to update')
    parser.add_argument('--validate', action='store_true', 
                        help='Only validate the image, do not convert')
    parser.add_argument('--save-as', help='Save modified CHR-ROM to different file')
    
    args = parser.parse_args()
    
    # Validate only mode
    if args.validate:
        img = Image.open(args.input)
        print(f"Validating: {args.input} ({img.width}x{img.height})")
        
        validator = PaletteValidator()
        valid, messages = validator.validate_image(img)
        for msg in messages:
            print(f"  {msg}")
        
        sys.exit(0 if valid else 1)
    
    # Initialize reinserter
    reinserter = CHRReinserter(args.chr_rom)
    
    # Handle different modes
    if args.tile is not None:
        # Update single tile
        if not args.chr_rom:
            parser.error("--tile requires --chr-rom")
        reinserter.update_tile(args.input, args.tile)
        reinserter.save_chr_rom(args.save_as)
    
    elif args.chr_rom:
        # Update tiles from sheet
        reinserter.update_tiles_from_sheet(args.input, args.start_tile)
        reinserter.save_chr_rom(args.save_as)
    
    elif args.output:
        # Simple PNG to CHR conversion
        reinserter.convert_png_to_chr(args.input, args.output)
    
    else:
        # Default: just convert and print info
        chr_data = reinserter.convert_png_to_chr(args.input)
        print(f"\nTo save, use: python chr_reinserter.py {args.input} -o output.chr")


if __name__ == "__main__":
    main()
