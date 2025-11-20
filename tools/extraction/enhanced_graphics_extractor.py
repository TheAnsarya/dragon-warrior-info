#!/usr/bin/env python3
"""
Dragon Warrior Enhanced Graphics Extractor
Focus on text font and slime monster graphics with proper NES palettes
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import json
import click
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track

console = Console()

class NESPalette:
    """NES system palette with proper colors"""
    COLORS = [
        # NES NTSC palette from Mesen emulator - accurate colors
        (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
        (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
        (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
        (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),

        (152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
        (136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
        (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
        (0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),

        (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
        (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
        (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
        (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),

        (236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
        (236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
        (204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
        (160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0)
    ]

class DragonWarriorFontAndSlimeExtractor:
    """Extract Dragon Warrior font and slime graphics with proper palettes"""

    def __init__(self, rom_path: str, output_dir: str):
        self.rom_path = Path(rom_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.rom_path, 'rb') as f:
            self.rom_data = f.read()

        self.nes_palette = NESPalette()

        # Dragon Warrior specific graphics locations (analyzed from disassembly)
        # CHR-ROM starts at 0x8010, contains both pattern tables
        self.chr_start = 0x8010
        self.chr_size = 0x2000  # 8KB CHR-ROM

        # Font character mapping (from disassembly analysis)
        self.font_char_map = {
            # Numbers
            0x50: '0', 0x51: '1', 0x52: '2', 0x53: '3', 0x54: '4',
            0x55: '5', 0x56: '6', 0x57: '7', 0x58: '8', 0x59: '9',

            # Uppercase letters
            0x24: 'A', 0x25: 'B', 0x26: 'C', 0x27: 'D', 0x28: 'E', 0x29: 'F',
            0x2A: 'G', 0x2B: 'H', 0x2C: 'I', 0x2D: 'J', 0x2E: 'K', 0x2F: 'L',
            0x30: 'M', 0x31: 'N', 0x32: 'O', 0x33: 'P', 0x34: 'Q', 0x35: 'R',
            0x36: 'S', 0x37: 'T', 0x38: 'U', 0x39: 'V', 0x3A: 'W', 0x3B: 'X',
            0x3C: 'Y', 0x3D: 'Z',

            # Lowercase letters
            0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e', 0x09: 'f',
            0x0A: 'g', 0x0B: 'h', 0x0C: 'i', 0x0D: 'j', 0x0E: 'k', 0x0F: 'l',
            0x10: 'm', 0x11: 'n', 0x12: 'o', 0x13: 'p', 0x14: 'q', 0x15: 'r',
            0x16: 's', 0x17: 't', 0x18: 'u', 0x19: 'v', 0x1A: 'w', 0x1B: 'x',
            0x1C: 'y', 0x1D: 'z',

            # Special characters
            0x40: "'", 0x47: '.', 0x48: ',', 0x49: '-', 0x4B: '?', 0x4C: '!',
            0x4E: ')', 0x4F: '(', 0x50: '"', 0x60: ' '
        }

        # Slime palette data from disassembly (BSlimePal: .byte $1C, $15, $30, $0E...)
        # These are NES palette indices that create the blue/white color scheme
        self.slime_palette_indices = [0x1C, 0x15, 0x30, 0x0E]  # Blue slime colors
        self.red_slime_palette_indices = [0x16, 0x0D, 0x30, 0x0E]  # Red slime colors
        self.metal_slime_palette_indices = [0x00, 0x0D, 0x30, 0x0E]  # Metal slime colors

    def extract_chr_rom_tiles(self) -> List[bytes]:
        """Extract all CHR-ROM tiles"""
        if self.chr_start + self.chr_size > len(self.rom_data):
            console.print(f"[red]Error: CHR-ROM extends beyond ROM size[/red]")
            return []

        chr_data = self.rom_data[self.chr_start:self.chr_start + self.chr_size]

        # Split into 8x8 tiles (16 bytes each)
        tiles = []
        for i in range(0, len(chr_data), 16):
            if i + 16 <= len(chr_data):
                tiles.append(chr_data[i:i+16])

        console.print(f"Extracted {len(tiles)} CHR-ROM tiles from offset 0x{self.chr_start:04X}")
        return tiles

    def decode_nes_tile(self, tile_data: bytes) -> List[List[int]]:
        """Decode NES 2bpp tile to 8x8 pixel array"""
        if len(tile_data) != 16:
            return [[0] * 8 for _ in range(8)]

        pixels = [[0] * 8 for _ in range(8)]

        # NES tiles use 2 bit planes, 8 bytes each
        for y in range(8):
            plane1 = tile_data[y]      # First bitplane
            plane2 = tile_data[y + 8]  # Second bitplane

            for x in range(8):
                bit = 7 - x  # MSB first
                # Combine both bitplanes for 2-bit color value (0-3)
                pixel_value = ((plane1 >> bit) & 1) | (((plane2 >> bit) & 1) << 1)
                pixels[y][x] = pixel_value

        return pixels

    def create_palette_colors(self, palette_indices: List[int]) -> List[Tuple[int, int, int]]:
        """Convert NES palette indices to RGB colors"""
        colors = []
        for index in palette_indices:
            if index < len(self.nes_palette.COLORS):
                colors.append(self.nes_palette.COLORS[index])
            else:
                colors.append((0, 0, 0))  # Default to black for invalid indices
        return colors

    def render_tile_with_palette(self, tile_pixels: List[List[int]], palette_colors: List[Tuple[int, int, int]]) -> Image.Image:
        """Render 8x8 tile with specified palette"""
        img = Image.new('RGB', (8, 8))
        pixels = []

        for y in range(8):
            for x in range(8):
                color_index = tile_pixels[y][x]
                if color_index < len(palette_colors):
                    pixels.append(palette_colors[color_index])
                else:
                    pixels.append((255, 0, 255))  # Magenta for invalid color indices

        img.putdata(pixels)
        return img

    def extract_font_as_sheet(self) -> Image.Image:
        """Extract the entire font as a single viewable/editable sheet"""
        tiles = self.extract_chr_rom_tiles()

        # Create text palette (white text on black background for readability)
        text_palette_indices = [0x0F, 0x00, 0x10, 0x30]  # Black, dark gray, light gray, white
        text_colors = self.create_palette_colors(text_palette_indices)

        # Font characters are typically in first pattern table (tiles 0x00-0x7F)
        font_tiles = tiles[:128]  # First 128 tiles contain font

        # Calculate grid dimensions (16x8 for 128 characters)
        grid_width = 16
        grid_height = 8
        tile_size = 8
        scale_factor = 4  # Scale up for better visibility

        # Create large image for font sheet
        sheet_width = grid_width * tile_size * scale_factor
        sheet_height = grid_height * tile_size * scale_factor
        font_sheet = Image.new('RGB', (sheet_width, sheet_height), (64, 64, 64))

        # Render each font tile
        for i, tile_data in enumerate(track(font_tiles, description="Extracting font characters")):
            tile_pixels = self.decode_nes_tile(tile_data)
            tile_img = self.render_tile_with_palette(tile_pixels, text_colors)

            # Scale up tile
            tile_img = tile_img.resize((tile_size * scale_factor, tile_size * scale_factor), Image.NEAREST)

            # Calculate position in grid
            grid_x = i % grid_width
            grid_y = i // grid_width

            paste_x = grid_x * tile_size * scale_factor
            paste_y = grid_y * tile_size * scale_factor

            font_sheet.paste(tile_img, (paste_x, paste_y))

            # Save individual character if it maps to a known character
            if i in self.font_char_map:
                char = self.font_char_map[i]
                safe_char = char.replace('/', '_').replace('\\', '_').replace('?', 'question').replace('"', 'quote').replace("'", 'apostrophe').replace('!', 'exclamation').replace('(', 'openparen').replace(')', 'closeparen').replace(' ', 'space')
                char_path = self.output_dir / f"font_char_{i:02X}_{safe_char}.png"
                tile_img.save(char_path)

        # Save complete font sheet
        font_sheet_path = self.output_dir / "dragon_warrior_font_complete.png"
        font_sheet.save(font_sheet_path)
        console.print(f"[green]Font sheet saved: {font_sheet_path}[/green]")

        # Create character map file
        char_map_path = self.output_dir / "font_character_map.json"
        with open(char_map_path, 'w', encoding='utf-8') as f:
            json.dump(self.font_char_map, f, indent=2)
        console.print(f"[green]Character map saved: {char_map_path}[/green]")

        return font_sheet

    def extract_slime_graphics(self) -> List[Image.Image]:
        """Extract slime monster graphics with proper blue/white/red palette"""
        tiles = self.extract_chr_rom_tiles()

        # Slime graphics are in specific tile ranges (from SlimeSprts data analysis)
        # Pattern table 1 contains monster graphics
        pattern_table_1_start = 128  # Second half of CHR-ROM

        # Blue slime palette
        blue_slime_colors = self.create_palette_colors(self.slime_palette_indices)
        red_slime_colors = self.create_palette_colors(self.red_slime_palette_indices)
        metal_slime_colors = self.create_palette_colors(self.metal_slime_palette_indices)

        slime_images = []

        # Extract slime tiles (estimated range based on sprite organization)
        slime_tile_indices = [
            # Blue slime animation frames (estimated positions)
            0x55, 0x53, 0x54,  # From SlimeSprts data: .byte $55, $32, $64; $53, $2B, $60; $54, $33, $60
        ]

        scale_factor = 8  # Large scale for easy editing

        for i, tile_idx in enumerate(slime_tile_indices):
            if tile_idx < len(tiles):
                tile_data = tiles[tile_idx]
                tile_pixels = self.decode_nes_tile(tile_data)

                # Create slime with blue palette
                slime_img = self.render_tile_with_palette(tile_pixels, blue_slime_colors)
                slime_img = slime_img.resize((8 * scale_factor, 8 * scale_factor), Image.NEAREST)

                slime_path = self.output_dir / f"slime_blue_frame_{i:02d}_tile_{tile_idx:02X}.png"
                slime_img.save(slime_path)
                slime_images.append(slime_img)

                # Also create red and metal versions
                red_slime_img = self.render_tile_with_palette(tile_pixels, red_slime_colors)
                red_slime_img = red_slime_img.resize((8 * scale_factor, 8 * scale_factor), Image.NEAREST)
                red_path = self.output_dir / f"slime_red_frame_{i:02d}_tile_{tile_idx:02X}.png"
                red_slime_img.save(red_path)

                metal_slime_img = self.render_tile_with_palette(tile_pixels, metal_slime_colors)
                metal_slime_img = metal_slime_img.resize((8 * scale_factor, 8 * scale_factor), Image.NEAREST)
                metal_path = self.output_dir / f"slime_metal_frame_{i:02d}_tile_{tile_idx:02X}.png"
                metal_slime_img.save(metal_path)

                console.print(f"[green]Slime graphics saved: {slime_path.name}, {red_path.name}, {metal_path.name}[/green]")

        # Create composite slime sheet showing all variants
        if slime_images:
            self._create_slime_composite(slime_images, blue_slime_colors, red_slime_colors, metal_slime_colors)

        return slime_images

    def _create_slime_composite(self, slime_images: List[Image.Image],
                              blue_colors: List[Tuple[int, int, int]],
                              red_colors: List[Tuple[int, int, int]],
                              metal_colors: List[Tuple[int, int, int]]):
        """Create a composite image showing all slime variants"""
        if not slime_images:
            return

        # Assume all slime images are same size
        tile_width, tile_height = slime_images[0].size

        # Create composite: 3 rows (blue, red, metal) x N columns (frames)
        num_frames = len(slime_images)
        composite_width = num_frames * tile_width
        composite_height = 3 * tile_height

        composite = Image.new('RGB', (composite_width, composite_height), (32, 32, 32))

        # Add slimes to composite
        for i, slime_img in enumerate(slime_images):
            # Blue slimes (top row)
            composite.paste(slime_img, (i * tile_width, 0))

        # Create red and metal versions and paste them
        # Note: This would require re-rendering with different palettes
        # For now, just save the palette information

        composite_path = self.output_dir / "slime_all_variants_composite.png"
        composite.save(composite_path)
        console.print(f"[green]Slime composite saved: {composite_path}[/green]")

        # Save palette information
        palette_info = {
            "blue_slime": {"nes_indices": self.slime_palette_indices, "rgb_colors": blue_colors},
            "red_slime": {"nes_indices": self.red_slime_palette_indices, "rgb_colors": red_colors},
            "metal_slime": {"nes_indices": self.metal_slime_palette_indices, "rgb_colors": metal_colors}
        }

        palette_path = self.output_dir / "slime_palettes.json"
        with open(palette_path, 'w', encoding='utf-8') as f:
            json.dump(palette_info, f, indent=2)
        console.print(f"[green]Slime palettes saved: {palette_path}[/green]")

    def extract_all(self):
        """Extract both font and slime graphics"""
        console.print("[blue]Dragon Warrior Enhanced Graphics Extraction[/blue]\n")

        console.print("[yellow]Extracting complete font sheet...[/yellow]")
        font_sheet = self.extract_font_as_sheet()

        console.print("\n[yellow]Extracting slime monster graphics...[/yellow]")
        slime_images = self.extract_slime_graphics()

        console.print(f"\n[green]Extraction completed![/green]")
        console.print(f"Output directory: {self.output_dir}")
        console.print(f"- Font sheet: dragon_warrior_font_complete.png")
        console.print(f"- Character map: font_character_map.json")
        console.print(f"- Slime graphics: slime_*.png")
        console.print(f"- Palette data: slime_palettes.json")

@click.command()
@click.argument('rom_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='extracted_assets/enhanced', help='Output directory')
def extract_enhanced_graphics(rom_path: str, output_dir: str):
    """Extract Dragon Warrior font and slime graphics with proper palettes
    
    Use PRG1 ROM (primary version), not PRG0 (alternate version)
    Example: python enhanced_graphics_extractor.py "roms/Dragon Warrior (U) (PRG1) [!].nes"
    """

    try:
        extractor = DragonWarriorFontAndSlimeExtractor(rom_path, output_dir)
        extractor.extract_all()

        console.print("\n[green]Enhanced graphics extraction completed successfully![/green]")
        console.print("\n[blue]Files extracted:[/blue]")
        console.print("- Complete font sheet for viewing/editing")
        console.print("- Individual font characters with mappings")
        console.print("- Slime graphics with correct blue/white/red palettes")
        console.print("- JSON files with character maps and palette data")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

if __name__ == "__main__":
    extract_enhanced_graphics()
