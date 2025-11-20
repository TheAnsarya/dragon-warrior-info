#!/usr/bin/env python3
"""
Dragon Warrior Graphics Inserter
Insert edited font and slime graphics back into ROM
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import click
from PIL import Image
from rich.console import Console

console = Console()

class DragonWarriorGraphicsInserter:
    """Insert edited graphics back into Dragon Warrior ROM"""

    def __init__(self, rom_path: str, output_rom_path: str):
        self.rom_path = Path(rom_path)
        self.output_rom_path = Path(output_rom_path)

        with open(self.rom_path, 'rb') as f:
            self.rom_data = bytearray(f.read())

        self.chr_start = 0x8010
        self.chr_size = 0x2000

        # Load character mapping
        self.char_to_tile = {}
        self.load_character_mapping()

    def load_character_mapping(self):
        """Load character to tile mapping from JSON"""
        char_map_path = Path("extracted_assets/enhanced/font_character_map.json")
        if char_map_path.exists():
            with open(char_map_path, 'r', encoding='utf-8') as f:
                tile_to_char = json.load(f)
                # Reverse the mapping
                self.char_to_tile = {char: int(tile, 16) for tile, char in tile_to_char.items()}
                console.print(f"[green]Loaded character mapping: {len(self.char_to_tile)} characters[/green]")

    def png_to_tile_data(self, png_path: Path, palette_colors: List[Tuple[int, int, int]]) -> bytes:
        """Convert PNG image back to NES tile data"""
        try:
            img = Image.open(png_path).convert('RGB')

            # If image is scaled up, scale it down to 8x8
            if img.size != (8, 8):
                img = img.resize((8, 8), Image.NEAREST)

            # Convert pixels back to palette indices
            pixels = list(img.getdata())
            tile_pixels = [[0] * 8 for _ in range(8)]

            for y in range(8):
                for x in range(8):
                    pixel_rgb = pixels[y * 8 + x]

                    # Find closest palette color
                    best_index = 0
                    best_distance = float('inf')

                    for i, palette_rgb in enumerate(palette_colors):
                        # Calculate color distance
                        distance = sum((a - b) ** 2 for a, b in zip(pixel_rgb, palette_rgb))
                        if distance < best_distance:
                            best_distance = distance
                            best_index = i

                    tile_pixels[y][x] = best_index

            # Convert back to NES tile format (2bpp)
            tile_data = bytearray(16)

            for y in range(8):
                plane1 = 0
                plane2 = 0

                for x in range(8):
                    bit = 7 - x
                    color_index = tile_pixels[y][x]

                    # Extract bit planes
                    if color_index & 1:
                        plane1 |= (1 << bit)
                    if color_index & 2:
                        plane2 |= (1 << bit)

                tile_data[y] = plane1
                tile_data[y + 8] = plane2

            return bytes(tile_data)

        except Exception as e:
            console.print(f"[red]Error converting {png_path}: {e}[/red]")
            return b'\x00' * 16

    def insert_font_character(self, char: str, png_path: Path):
        """Insert a single font character from PNG"""
        if char not in self.char_to_tile:
            console.print(f"[yellow]Warning: Character '{char}' not in mapping[/yellow]")
            return False

        tile_index = self.char_to_tile[char]

        # Default text palette colors (black, dark gray, light gray, white)
        text_palette = [(84, 84, 84), (152, 150, 152), (236, 238, 236), (236, 238, 236)]

        tile_data = self.png_to_tile_data(png_path, text_palette)

        # Calculate position in CHR-ROM
        tile_offset = self.chr_start + (tile_index * 16)

        if tile_offset + 16 <= len(self.rom_data):
            self.rom_data[tile_offset:tile_offset + 16] = tile_data
            console.print(f"[green]Inserted character '{char}' at tile {tile_index:02X}[/green]")
            return True
        else:
            console.print(f"[red]Error: Tile offset out of range for '{char}'[/red]")
            return False

    def insert_slime_graphics(self, slime_png_dir: Path):
        """Insert slime graphics from PNG files"""
        # Load slime palette data
        palette_path = Path("extracted_assets/enhanced/slime_palettes.json")
        if not palette_path.exists():
            console.print(f"[red]Error: Slime palette file not found[/red]")
            return False

        with open(palette_path, 'r', encoding='utf-8') as f:
            palette_data = json.load(f)

        blue_slime_colors = [tuple(color) for color in palette_data["blue_slime"]["rgb_colors"]]

        # Insert slime tiles (based on SlimeSprts data)
        slime_tiles = [0x55, 0x53, 0x54]

        for i, tile_index in enumerate(slime_tiles):
            png_file = slime_png_dir / f"slime_blue_frame_{i:02d}_tile_{tile_index:02X}.png"

            if png_file.exists():
                tile_data = self.png_to_tile_data(png_file, blue_slime_colors)
                tile_offset = self.chr_start + (tile_index * 16)

                if tile_offset + 16 <= len(self.rom_data):
                    self.rom_data[tile_offset:tile_offset + 16] = tile_data
                    console.print(f"[green]Inserted slime tile {tile_index:02X} from {png_file.name}[/green]")
                else:
                    console.print(f"[red]Error: Tile offset out of range for slime tile {tile_index:02X}[/red]")
            else:
                console.print(f"[yellow]Warning: Slime PNG not found: {png_file}[/yellow]")

    def save_rom(self):
        """Save the modified ROM"""
        self.output_rom_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_rom_path, 'wb') as f:
            f.write(self.rom_data)

        console.print(f"[green]Modified ROM saved: {self.output_rom_path}[/green]")

    def insert_all_from_directory(self, graphics_dir: Path):
        """Insert all graphics from a directory"""
        graphics_dir = Path(graphics_dir)

        if not graphics_dir.exists():
            console.print(f"[red]Error: Graphics directory not found: {graphics_dir}[/red]")
            return

        console.print(f"[blue]Inserting graphics from: {graphics_dir}[/blue]")

        # Insert font characters
        font_files = list(graphics_dir.glob("font_char_*.png"))
        inserted_chars = 0

        for font_file in font_files:
            # Extract character from filename (e.g., "font_char_24_A.png" -> "A")
            parts = font_file.stem.split('_')
            if len(parts) >= 4:
                char = parts[3]
                if self.insert_font_character(char, font_file):
                    inserted_chars += 1

        console.print(f"[green]Inserted {inserted_chars} font characters[/green]")

        # Insert slime graphics
        self.insert_slime_graphics(graphics_dir)

@click.command()
@click.argument('rom_path', type=click.Path(exists=True))
@click.argument('graphics_dir', type=click.Path(exists=True))
@click.option('--output', '-o', default='patched_dragon_warrior.nes', help='Output ROM file')
def insert_graphics(rom_path: str, graphics_dir: str, output: str):
    """Insert edited graphics back into Dragon Warrior ROM"""

    try:
        inserter = DragonWarriorGraphicsInserter(rom_path, output)
        inserter.insert_all_from_directory(graphics_dir)
        inserter.save_rom()

        console.print(f"\n[green]Graphics insertion completed![/green]")
        console.print(f"Original ROM: {rom_path}")
        console.print(f"Graphics from: {graphics_dir}")
        console.print(f"Output ROM: {output}")
        console.print("\n[yellow]Note: Test the ROM in an emulator to verify changes![/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

if __name__ == "__main__":
    insert_graphics()
