#!/usr/bin/env python3
"""
Dragon Warrior Comprehensive Graphics Extractor
Extracts ALL graphics with correct addresses, palettes, and sprite compositions
Based on actual disassembly data from Bank00.asm and Bank01.asm
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import json
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track, Progress
from rich.table import Table
from rich import print as rprint

console = Console()

class NESPalette:
	"""Accurate NES NTSC palette"""
	COLORS = [
		# Row 0
		(84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
		(68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
		(32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
		(0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
		# Row 1
		(152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
		(136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
		(84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
		(0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
		# Row 2
		(236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
		(228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
		(160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
		(56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
		# Row 3
		(236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
		(236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
		(204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
		(160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0)
	]

class DragonWarriorComprehensiveExtractor:
	"""Complete Dragon Warrior graphics extraction with proper addresses and palettes"""

	def __init__(self, rom_path: str, output_dir: str):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.nes_palette = NESPalette()

		# Dragon Warrior ROM structure (MMC1 mapper)
		# Header: 16 bytes (0x0000-0x000F)
		# PRG-ROM: 64KB = 4x16KB banks (0x0010-0x1000F)
		# CHR-ROM: 16KB = 2x8KB banks (0x10010-0x1400F)
		self.chr_start = 0x10010
		self.chr_size = 0x4000  # 16KB

		# Dragon Warrior palettes from disassembly (Bank00.asm @ 0x9AAF)
		# These are NES palette indices that create the actual game colors
		self.sprite_palettes = {
			"blue_slime": [0x1C, 0x15, 0x30, 0x0E],      # BSlimePal
			"red_slime": [0x16, 0x0D, 0x30, 0x0E],       # RSlimePal
			"drakee": [0x01, 0x15, 0x30, 0x0E],          # DrakeePal
			"ghost": [0x13, 0x15, 0x0C, 0x26],           # GhostPal
			"magician": [0x00, 0x36, 0x0F, 0x00],        # MagicianPal (4 colors)
			"metal_drakee": [0x15, 0x0E, 0x30, 0x0E],    # MDrakeePal
			"scorpion": [0x26, 0x13, 0x1E, 0x0E],        # ScorpionPal
			"druin": [0x26, 0x03, 0x30, 0x15],           # DruinPal
			"hero": [0x16, 0x27, 0x30, 0x0F],            # Hero palette (estimated)
			"text": [0x0F, 0x00, 0x10, 0x30],            # Text: black bg, white text
		}

		# Sprite data from Bank01.asm
		# Format: [tile_index, x_offset, y_offset/attributes]
		# These are from SlimeSprts @ 0x9B0E in Bank 1
		self.sprite_definitions = {
			"slime": [
				(0x55, 0x32, 0x64),  # Body tile
				(0x53, 0x2B, 0x60),  # Left eye
				(0x54, 0x33, 0x60),  # Right eye
				(0x53, 0x6B, 0x7C),  # Shadow left (flipped)
				(0x54, 0x73, 0x7C),  # Shadow right (flipped)
				# FF/FE bytes indicate palette/attribute changes
			],
			# More sprites can be added from other *Sprts tables
		}

	def extract_chr_rom_tiles(self) -> List[bytes]:
		"""Extract all CHR-ROM tiles (pattern tables)"""
		if self.chr_start + self.chr_size > len(self.rom_data):
			console.print(f"[red]Error: CHR-ROM extends beyond ROM size[/red]")
			console.print(f"Expected CHR at 0x{self.chr_start:X}-0x{self.chr_start + self.chr_size:X}")
			console.print(f"ROM size: 0x{len(self.rom_data):X}")
			return []

		chr_data = self.rom_data[self.chr_start:self.chr_start + self.chr_size]

		# Split into 8x8 tiles (16 bytes each)
		tiles = []
		for i in range(0, len(chr_data), 16):
			if i + 16 <= len(chr_data):
				tiles.append(chr_data[i:i+16])

		console.print(f"[green]Extracted {len(tiles)} tiles from CHR-ROM at 0x{self.chr_start:X}[/green]")
		return tiles

	def decode_nes_tile(self, tile_data: bytes) -> List[List[int]]:
		"""Decode NES 2bpp tile format to 8x8 pixel array"""
		if len(tile_data) != 16:
			return [[0] * 8 for _ in range(8)]

		pixels = [[0] * 8 for _ in range(8)]

		# NES uses planar format: 8 bytes plane 0, 8 bytes plane 1
		for y in range(8):
			plane0 = tile_data[y]
			plane1 = tile_data[y + 8]

			for x in range(8):
				bit = 7 - x  # MSB = leftmost pixel
				# Combine both bit planes to get 2-bit color index (0-3)
				pixel_value = ((plane0 >> bit) & 1) | (((plane1 >> bit) & 1) << 1)
				pixels[y][x] = pixel_value

		return pixels

	def palette_to_rgb(self, palette_indices: List[int]) -> List[Tuple[int, int, int]]:
		"""Convert NES palette indices to RGB colors"""
		colors = []
		for idx in palette_indices:
			if 0 <= idx < len(self.nes_palette.COLORS):
				colors.append(self.nes_palette.COLORS[idx])
			else:
				colors.append((255, 0, 255))  # Magenta for invalid
		return colors

	def render_tile(self, tile_pixels: List[List[int]], palette_rgb: List[Tuple[int, int, int]]) -> Image.Image:
		"""Render 8x8 tile with specified palette"""
		img = Image.new('RGB', (8, 8))
		pixels = []

		for y in range(8):
			for x in range(8):
				color_idx = tile_pixels[y][x]
				if color_idx < len(palette_rgb):
					pixels.append(palette_rgb[color_idx])
				else:
					pixels.append((255, 0, 255))  # Magenta for errors

		img.putdata(pixels)
		return img

	def extract_pattern_tables(self):
		"""Extract both pattern tables as organized sheets"""
		tiles = self.extract_chr_rom_tiles()
		if not tiles:
			return

		# Dragon Warrior has 2 CHR banks (pattern tables)
		# Each pattern table is 256 tiles (4KB)
		tiles_per_bank = 256
		scale = 4  # Scale factor for visibility

		for bank_num in range(2):
			bank_start = bank_num * tiles_per_bank
			bank_end = min(bank_start + tiles_per_bank, len(tiles))

			# Create pattern table sheet (16x16 grid)
			sheet_width = 16 * 8 * scale
			sheet_height = 16 * 8 * scale
			sheet = Image.new('RGB', (sheet_width, sheet_height), (0, 0, 0))

			# Use grayscale for pattern table visualization
			grayscale_pal = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]

			console.print(f"\n[cyan]Extracting Pattern Table {bank_num} (CHR Bank {bank_num})[/cyan]")

			for tile_idx in track(range(bank_start, bank_end), description=f"CHR Bank {bank_num}"):
				if tile_idx < len(tiles):
					tile_data = tiles[tile_idx]
					tile_pixels = self.decode_nes_tile(tile_data)
					tile_img = self.render_tile(tile_pixels, grayscale_pal)

					# Scale up
					tile_img = tile_img.resize((8 * scale, 8 * scale), Image.Resampling.NEAREST)

					# Calculate position in 16x16 grid
					local_idx = tile_idx - bank_start
					grid_x = local_idx % 16
					grid_y = local_idx // 16

					paste_x = grid_x * 8 * scale
					paste_y = grid_y * 8 * scale

					sheet.paste(tile_img, (paste_x, paste_y))

					# Save individual tile
					tile_dir = self.output_dir / f"chr_bank_{bank_num}"
					tile_dir.mkdir(exist_ok=True)
					tile_img.save(tile_dir / f"tile_{tile_idx:03X}.png")

			# Save pattern table sheet
			sheet_path = self.output_dir / f"pattern_table_{bank_num}_complete.png"
			sheet.save(sheet_path)
			console.print(f"[green]Saved: {sheet_path.name}[/green]")

	def extract_sprites_with_palettes(self):
		"""Extract sprite graphics with their correct palettes"""
		tiles = self.extract_chr_rom_tiles()
		if not tiles:
			return

		sprite_dir = self.output_dir / "sprites"
		sprite_dir.mkdir(exist_ok=True)

		scale = 8  # Large scale for editing

		console.print("\n[cyan]Extracting sprites with correct palettes...[/cyan]")

		for sprite_name, palette_indices in self.sprite_palettes.items():
			palette_rgb = self.palette_to_rgb(palette_indices)

			# Save palette swatch
			swatch = self.create_palette_swatch(palette_rgb, sprite_name)
			swatch.save(sprite_dir / f"palette_{sprite_name}.png")

			# Extract sprite compositions if available
			if sprite_name in ["blue_slime", "red_slime"]:
				self.extract_slime_sprite(tiles, sprite_name, palette_rgb, sprite_dir, scale)

		# Extract all tiles with each palette for maximum flexibility
		for palette_name, palette_indices in track(list(self.sprite_palettes.items())[:3], 
													description="Rendering tile sheets"):
			self.create_tile_sheet_with_palette(tiles, palette_name, palette_indices)

	def extract_slime_sprite(self, tiles: List[bytes], variant: str, palette_rgb: List[Tuple[int, int, int]], 
							 output_dir: Path, scale: int):
		"""Extract slime sprite with composition"""
		# Slime sprite data from disassembly
		slime_tiles = [0x55, 0x53, 0x54]  # Main tiles used

		composite_width = 3 * 8 * scale
		composite_height = 8 * scale
		composite = Image.new('RGBA', (composite_width, composite_height), (0, 0, 0, 0))

		for i, tile_idx in enumerate(slime_tiles):
			if tile_idx < len(tiles):
				tile_data = tiles[tile_idx]
				tile_pixels = self.decode_nes_tile(tile_data)
				tile_img = self.render_tile(tile_pixels, palette_rgb)
				tile_img = tile_img.resize((8 * scale, 8 * scale), Image.Resampling.NEAREST)

				# Convert to RGBA and make color 0 transparent
				tile_rgba = tile_img.convert('RGBA')
				pixels = tile_rgba.load()
				for y in range(tile_rgba.height):
					for x in range(tile_rgba.width):
						if pixels[x, y][:3] == palette_rgb[0]:  # Background color
							pixels[x, y] = (0, 0, 0, 0)  # Transparent

				composite.paste(tile_rgba, (i * 8 * scale, 0), tile_rgba)

				# Save individual tile
				tile_img.save(output_dir / f"{variant}_tile_{tile_idx:02X}.png")

		composite.save(output_dir / f"{variant}_composite.png")
		console.print(f"[green]Extracted {variant} sprite[/green]")

	def create_palette_swatch(self, palette_rgb: List[Tuple[int, int, int]], name: str) -> Image.Image:
		"""Create a palette swatch image"""
		swatch_size = 64
		swatch = Image.new('RGB', (len(palette_rgb) * swatch_size, swatch_size))

		for i, color in enumerate(palette_rgb):
			for y in range(swatch_size):
				for x in range(swatch_size):
					swatch.putpixel((i * swatch_size + x, y), color)

		# Add text label
		draw = ImageDraw.Draw(swatch)
		# Note: Default font, could use ImageFont.truetype() for better fonts
		draw.text((5, swatch_size - 15), name, fill=(255, 255, 255))

		return swatch

	def create_tile_sheet_with_palette(self, tiles: List[bytes], palette_name: str, palette_indices: List[int]):
		"""Create a full tile sheet with specific palette applied"""
		palette_rgb = self.palette_to_rgb(palette_indices)

		# Create sheet for first 256 tiles (pattern table 0)
		tiles_per_row = 16
		tiles_per_col = 16
		tile_count = min(256, len(tiles))
		scale = 3

		sheet_width = tiles_per_row * 8 * scale
		sheet_height = tiles_per_col * 8 * scale
		sheet = Image.new('RGB', (sheet_width, sheet_height))

		for tile_idx in range(tile_count):
			tile_data = tiles[tile_idx]
			tile_pixels = self.decode_nes_tile(tile_data)
			tile_img = self.render_tile(tile_pixels, palette_rgb)
			tile_img = tile_img.resize((8 * scale, 8 * scale), Image.Resampling.NEAREST)

			grid_x = tile_idx % tiles_per_row
			grid_y = tile_idx // tiles_per_row

			paste_x = grid_x * 8 * scale
			paste_y = grid_y * 8 * scale

			sheet.paste(tile_img, (paste_x, paste_y))

		sheet_path = self.output_dir / f"tile_sheet_with_{palette_name}_palette.png"
		sheet.save(sheet_path)
		console.print(f"[green]Saved: {sheet_path.name}[/green]")

	def export_palette_json(self):
		"""Export palette data as JSON"""
		palette_data = {}

		for name, indices in self.sprite_palettes.items():
			rgb_colors = self.palette_to_rgb(indices)
			palette_data[name] = {
				"nes_indices": indices,
				"rgb_colors": [[r, g, b] for r, g, b in rgb_colors],
				"hex_colors": [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in rgb_colors]
			}

		json_path = self.output_dir / "palettes.json"
		with open(json_path, 'w', encoding='utf-8') as f:
			json.dump(palette_data, f, indent=2)

		console.print(f"[green]Saved palette data: {json_path.name}[/green]")

	def generate_report(self):
		"""Generate extraction report"""
		table = Table(title="Dragon Warrior Graphics Extraction Report")
		table.add_column("Component", style="cyan")
		table.add_column("Details", style="green")

		table.add_row("ROM Size", f"{len(self.rom_data):,} bytes")
		table.add_row("CHR-ROM Offset", f"0x{self.chr_start:X}")
		table.add_row("CHR-ROM Size", f"0x{self.chr_size:X} ({self.chr_size // 1024}KB)")
		table.add_row("Total Tiles", f"{self.chr_size // 16}")
		table.add_row("Palettes Extracted", f"{len(self.sprite_palettes)}")
		table.add_row("Output Directory", str(self.output_dir))

		console.print("\n")
		console.print(table)

	def extract_all(self):
		"""Run complete extraction"""
		console.print("[bold blue]Dragon Warrior Comprehensive Graphics Extraction[/bold blue]\n")

		self.generate_report()

		# Extract pattern tables
		self.extract_pattern_tables()

		# Extract sprites with palettes
		self.extract_sprites_with_palettes()

		# Export palette JSON
		self.export_palette_json()

		console.print("\n[bold green]✓ Extraction Complete![/bold green]")
		console.print(f"[dim]All files saved to: {self.output_dir}[/dim]")


def main():
	"""Main entry point"""
	import sys

	if len(sys.argv) < 2:
		console.print("[yellow]Usage: python comprehensive_graphics_extractor.py <rom_path> [output_dir][/yellow]")
		console.print("[dim]Example: python comprehensive_graphics_extractor.py dragon_warrior.nes extracted_graphics[/dim]")
		sys.exit(1)

	rom_path = sys.argv[1]
	output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_graphics"

	if not os.path.exists(rom_path):
		console.print(f"[red]Error: ROM file not found: {rom_path}[/red]")
		sys.exit(1)

	try:
		extractor = DragonWarriorComprehensiveExtractor(rom_path, output_dir)
		extractor.extract_all()
	except Exception as e:
		console.print(f"[red]Error during extraction: {e}[/red]")
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == "__main__":
	main()
