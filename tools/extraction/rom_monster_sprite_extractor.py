#!/usr/bin/env python3
"""
Dragon Warrior ROM-Based Monster Sprite Extractor
Reads sprite data directly from ROM using EnSpritesPtrTbl pointer table
Extracts ALL 39 monsters with complete multi-tile compositions
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

class NESPalette:
	"""Accurate NES NTSC palette"""
	COLORS = [
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

# All 39 Dragon Warrior monsters with their palettes from Bank00.asm
MONSTER_DATA = [
	{"id": 0, "name": "Slime", "palette": [0x1C, 0x15, 0x30, 0x0E]},
	{"id": 1, "name": "Red Slime", "palette": [0x16, 0x0D, 0x30, 0x0E]},
	{"id": 2, "name": "Drakee", "palette": [0x01, 0x15, 0x30, 0x0E]},
	{"id": 3, "name": "Ghost", "palette": [0x13, 0x15, 0x0C, 0x26]},
	{"id": 4, "name": "Magician", "palette": [0x00, 0x36, 0x0F, 0x00]},
	{"id": 5, "name": "Magidrakee", "palette": [0x01, 0x15, 0x30, 0x0E]},
	{"id": 6, "name": "Scorpion", "palette": [0x26, 0x13, 0x1E, 0x0E]},
	{"id": 7, "name": "Druin", "palette": [0x26, 0x03, 0x30, 0x15]},
	{"id": 8, "name": "Poltergeist", "palette": [0x13, 0x15, 0x0C, 0x26]},
	{"id": 9, "name": "Droll", "palette": [0x05, 0x15, 0x30, 0x0E]},
	{"id": 10, "name": "Drakeema", "palette": [0x01, 0x15, 0x30, 0x0E]},
	{"id": 11, "name": "Skeleton", "palette": [0x00, 0x30, 0x0E, 0x0E]},
	{"id": 12, "name": "Warlock", "palette": [0x00, 0x36, 0x0F, 0x00]},
	{"id": 13, "name": "Metal Scorpion", "palette": [0x00, 0x10, 0x30, 0x0E]},
	{"id": 14, "name": "Wolf", "palette": [0x16, 0x27, 0x30, 0x0E]},
	{"id": 15, "name": "Wraith", "palette": [0x00, 0x30, 0x0E, 0x0E]},
	{"id": 16, "name": "Metal Slime", "palette": [0x15, 0x0E, 0x30, 0x0E]},
	{"id": 17, "name": "Specter", "palette": [0x13, 0x15, 0x0C, 0x26]},
	{"id": 18, "name": "Wolflord", "palette": [0x16, 0x27, 0x30, 0x0E]},
	{"id": 19, "name": "Druinlord", "palette": [0x26, 0x03, 0x30, 0x15]},
	{"id": 20, "name": "Drollmagi", "palette": [0x05, 0x15, 0x30, 0x0E]},
	{"id": 21, "name": "Wyvern", "palette": [0x06, 0x16, 0x30, 0x0E]},
	{"id": 22, "name": "Rouge Scorpion", "palette": [0x16, 0x06, 0x30, 0x0E]},
	{"id": 23, "name": "Wraith Knight", "palette": [0x00, 0x11, 0x30, 0x0E]},
	{"id": 24, "name": "Golem", "palette": [0x00, 0x0A, 0x2A, 0x1A]},
	{"id": 25, "name": "Goldman", "palette": [0x00, 0x18, 0x30, 0x0E]},
	{"id": 26, "name": "Knight", "palette": [0x16, 0x06, 0x30, 0x0E]},
	{"id": 27, "name": "Magiwyvern", "palette": [0x06, 0x16, 0x30, 0x0E]},
	{"id": 28, "name": "Demon Knight", "palette": [0x16, 0x06, 0x30, 0x0E]},
	{"id": 29, "name": "Werewolf", "palette": [0x16, 0x27, 0x30, 0x0E]},
	{"id": 30, "name": "Green Dragon", "palette": [0x0A, 0x1A, 0x30, 0x0E]},
	{"id": 31, "name": "Starwyvern", "palette": [0x06, 0x16, 0x30, 0x0E]},
	{"id": 32, "name": "Wizard", "palette": [0x00, 0x36, 0x0F, 0x00]},
	{"id": 33, "name": "Axe Knight", "palette": [0x16, 0x27, 0x18, 0x0E]},
	{"id": 34, "name": "Blue Dragon", "palette": [0x01, 0x11, 0x30, 0x0E]},
	{"id": 35, "name": "Stoneman", "palette": [0x00, 0x0A, 0x2A, 0x1A]},
	{"id": 36, "name": "Armored Knight", "palette": [0x00, 0x10, 0x30, 0x0E]},
	{"id": 37, "name": "Red Dragon", "palette": [0x16, 0x06, 0x30, 0x0E]},
	{"id": 38, "name": "Dragonlord", "palette": [0x16, 0x06, 0x30, 0x0E]},
]

class ROMMonsterSpriteExtractor:
	"""Extract all Dragon Warrior monster sprites directly from ROM"""

	def __init__(self, rom_path: str, output_dir: str):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir) / "monsters"
		self.output_dir.mkdir(parents=True, exist_ok=True)

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.nes_palette = NESPalette()
		
		# ROM structure for MMC1 mapper
		self.header_size = 16
		self.prg_rom_start = self.header_size
		self.prg_rom_size = 0x10000  # 64KB (4 banks of 16KB each)
		self.chr_rom_start = self.header_size + self.prg_rom_size
		self.chr_rom_size = 0x4000  # 16KB
		
		# PRG-ROM bank layout (MMC1):
		# Bank 0: file 0x000010-0x00400F, CPU 0x8000-0xBFFF (fixed)
		# Bank 1: file 0x004010-0x00800F, CPU 0xC000-0xFFFF (switchable)
		# Bank 2: file 0x008010-0x00C00F, CPU 0xC000-0xFFFF (switchable)
		# Bank 3: file 0x00C010-0x01000F, CPU 0xC000-0xFFFF (switchable)
		
		# EnSpritesPtrTbl is at CPU 0x99E4 (in Bank00)
		# File offset = 0x10 + (0x99E4 - 0x8000) = 0x59F4
		self.sprite_ptr_table_offset = self.header_size + 0x59E4
		
		# Bank01.asm uses .org $8000 but represents the switchable bank
		# Pointers with "-$8000" are offsets into Bank01 data
		# Bank01 file offset = 0x4010
		self.bank01_file_offset = self.header_size + 0x4000
		
		self.chr_tiles = self.extract_chr_tiles()

	def extract_chr_tiles(self) -> List[bytes]:
		"""Extract CHR-ROM tiles"""
		chr_data = self.rom_data[self.chr_rom_start:self.chr_rom_start + self.chr_rom_size]
		tiles = []
		for i in range(0, len(chr_data), 16):
			if i + 16 <= len(chr_data):
				tiles.append(chr_data[i:i+16])
		return tiles

	def read_word_le(self, offset: int) -> int:
		"""Read little-endian 16-bit word from ROM"""
		return self.rom_data[offset] | (self.rom_data[offset + 1] << 8)

	def cpu_to_file_offset(self, cpu_addr: int, in_bank01: bool = True) -> int:
		"""Convert NES CPU address to ROM file offset"""
		if in_bank01:
			# Bank01 is mapped to 0x8000-0xBFFF in CPU space
			# File offset = header + (CPU_addr - 0x8000) + bank_offset
			if 0x8000 <= cpu_addr <= 0xBFFF:
				return self.header_size + (cpu_addr - 0x8000)
			else:
				# Must be in Bank00 (0x8000-0xBFFF can be Bank00 or Bank01 depending on mapping)
				# For Bank00: CPU 0x8000 = file 0x10
				return self.header_size + (cpu_addr - 0x8000)
		else:
			# For addresses in other banks
			return self.header_size + (cpu_addr - 0x8000)

	def read_sprite_data(self, sprite_ptr_offset: int) -> List[Tuple[int, int, int]]:
		"""Read sprite data from ROM using pointer
		
		Returns list of (tile, attr_byte, x_pos) tuples
		Sprite data format: TTTTTTTT VHYYYYYY XXXXXXPP
		"""
		# Read pointer (little-endian word)
		ptr_value = self.read_word_le(sprite_ptr_offset)
		
		# Debug logging for troublesome monsters
		debug_ids = [3, 8, 17]  # Ghost, Poltergeist, Specter
		monster_id = (sprite_ptr_offset - self.sprite_ptr_table_offset) // 2
		if monster_id in debug_ids:
			console.print(f"[dim]Debug monster {monster_id}: ptr_offset=0x{sprite_ptr_offset:06X}, ptr_value=0x{ptr_value:04X}[/dim]")
		
		# The pointers in EnSpritesPtrTbl have two formats:
		# 1. Values < 0x8000: These are offsets into Bank01 (the .asm uses "-$8000")
		#    Example: SlimeSprts -$8000 ;($1B0E) → pointer stores 0x1B0E
		#    File location: Bank01_base + offset = 0x4010 + 0x1B0E = 0x5B1E
		# 
		# 2. Values >= 0x8000: These are CPU addresses in Bank00  
		#    Example: SkelSprts ;($9A3E) → pointer stores 0x9A3E
		#    File location: header + (CPU_addr - 0x8000) = 0x10 + 0x1A3E = 0x1A4E
		
		if ptr_value < 0x8000:
			# It's an offset into Bank01 (switchable bank at 0xC000-0xFFFF)
			# Bank01 file offset is 0x4010
			file_offset = self.bank01_file_offset + ptr_value
		else:
			# It's a CPU address in Bank00 (fixed bank at 0x8000-0xBFFF)
			file_offset = self.header_size + (ptr_value - 0x8000)
		
		if file_offset >= len(self.rom_data):
			console.print(f"[yellow]Warning: sprite file offset {file_offset:06X} outside ROM[/yellow]")
			return []
		
		# Debug logging
		if monster_id in debug_ids:
			console.print(f"[dim]  file_offset=0x{file_offset:06X}, first_byte=0x{self.rom_data[file_offset]:02X}[/dim]")
		
		# Read sprite entries until we hit $00 terminator
		sprites = []
		offset = file_offset
		max_sprites = 50  # Safety limit
		
		while offset < len(self.rom_data) and len(sprites) < max_sprites:
			tile = self.rom_data[offset]
			
			# Check for terminator
			if tile == 0x00:
				break
			
			attr_byte = self.rom_data[offset + 1]
			x_pos = self.rom_data[offset + 2]
			
			sprites.append((tile, attr_byte, x_pos))
			offset += 3
		
		return sprites
	
	def _read_sprite_data_at_offset(self, file_offset: int) -> List[Tuple[int, int, int]]:
		"""Read sprite data directly from a file offset (for fallback/debug)"""
		sprites = []
		offset = file_offset
		max_sprites = 50
		
		while offset < len(self.rom_data) and len(sprites) < max_sprites:
			tile = self.rom_data[offset]
			if tile == 0x00:
				break
			attr_byte = self.rom_data[offset + 1]
			x_pos = self.rom_data[offset + 2]
			sprites.append((tile, attr_byte, x_pos))
			offset += 3
		
		return sprites

	def decode_tile(self, tile_data: bytes) -> List[List[int]]:
		"""Decode NES 2bpp tile"""
		pixels = [[0] * 8 for _ in range(8)]
		for y in range(8):
			plane0 = tile_data[y]
			plane1 = tile_data[y + 8]
			for x in range(8):
				bit = 7 - x
				pixels[y][x] = ((plane0 >> bit) & 1) | (((plane1 >> bit) & 1) << 1)
		return pixels

	def palette_to_rgb(self, palette_indices: List[int]) -> List[Tuple[int, int, int]]:
		"""Convert NES palette indices to RGB"""
		return [self.nes_palette.COLORS[idx] if idx < len(self.nes_palette.COLORS)
				else (255, 0, 255) for idx in palette_indices]

	def render_tile(self, tile_idx: int, palette_rgb: List[Tuple], h_flip: bool = False,
					v_flip: bool = False) -> Image.Image:
		"""Render a single 8x8 tile with palette and flipping"""
		if tile_idx >= len(self.chr_tiles):
			# Return blank tile
			img = Image.new('RGB', (8, 8), palette_rgb[0])
			return img

		tile_pixels = self.decode_tile(self.chr_tiles[tile_idx])

		# Apply flipping
		if h_flip:
			tile_pixels = [row[::-1] for row in tile_pixels]
		if v_flip:
			tile_pixels = tile_pixels[::-1]

		# Render
		img = Image.new('RGB', (8, 8))
		pixels = []
		for y in range(8):
			for x in range(8):
				color_idx = tile_pixels[y][x]
				pixels.append(palette_rgb[color_idx] if color_idx < len(palette_rgb)
							 else (255, 0, 255))
		img.putdata(pixels)
		return img

	def parse_sprite_byte(self, byte: int) -> dict:
		"""Parse sprite attribute byte
		
		Format: VHPPPPPP (for Dragon Warrior - differs from standard NES)
		V = V flip
		H = H flip  
		PPPPPP = Y offset (6 bits)
		"""
		return {
			'y_offset': byte & 0x3F,  # Lower 6 bits
			'h_flip': bool(byte & 0x40),  # Bit 6
			'v_flip': bool(byte & 0x80),  # Bit 7
		}

	def render_monster_sprite(self, monster: dict, sprite_data: List[Tuple[int, int, int]],
							  scale: int = 4) -> Optional[Image.Image]:
		"""Render complete monster sprite from tile data"""
		if not sprite_data:
			return None
			
		palette_rgb = self.palette_to_rgb(monster['palette'])

		# Calculate bounding box from sprite positions
		min_x = min(x for _, _, x in sprite_data)
		max_x = max(x for _, _, x in sprite_data)
		min_y = min(self.parse_sprite_byte(y)['y_offset'] for _, y, _ in sprite_data)
		max_y = max(self.parse_sprite_byte(y)['y_offset'] for _, y, _ in sprite_data)

		# Create canvas with padding
		width = (max_x - min_x + 16) * scale
		height = (max_y - min_y + 16) * scale

		# Create transparent canvas
		img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

		# Render each sprite tile
		for tile_idx, attr_byte, x_pos in sprite_data:
			attrs = self.parse_sprite_byte(attr_byte)
			y_pos = attrs['y_offset']

			# Render tile
			tile_img = self.render_tile(tile_idx, palette_rgb,
										attrs['h_flip'], attrs['v_flip'])

			# Convert to RGBA and make background transparent
			tile_rgba = tile_img.convert('RGBA')
			pixels = tile_rgba.load()
			for py in range(8):
				for px in range(8):
					if pixels[px, py][:3] == palette_rgb[0]:  # Background color
						pixels[px, py] = (0, 0, 0, 0)

			# Scale up
			tile_rgba = tile_rgba.resize((8 * scale, 8 * scale), Image.Resampling.NEAREST)

			# Paste onto canvas
			paste_x = (x_pos - min_x) * scale
			paste_y = (y_pos - min_y) * scale
			img.paste(tile_rgba, (paste_x, paste_y), tile_rgba)

		return img

	def extract_all_monsters(self):
		"""Extract all 39 monsters from ROM"""
		console.print("[cyan]Extracting all 39 Dragon Warrior monsters from ROM...[/cyan]\n")
		
		# Show ROM structure info
		table = Table(title="ROM Structure Analysis")
		table.add_column("Component", style="cyan")
		table.add_column("File Offset", style="green")
		table.add_column("CPU Address", style="yellow")
		table.add_column("Size", style="magenta")
		
		table.add_row("iNES Header", f"0x{0:06X}", "N/A", "16 bytes")
		table.add_row("PRG-ROM", f"0x{self.prg_rom_start:06X}", "0x8000-0xFFFF", f"{self.prg_rom_size} bytes")
		table.add_row("CHR-ROM", f"0x{self.chr_rom_start:06X}", "N/A (CHR)", f"{self.chr_rom_size} bytes")
		table.add_row("EnSpritesPtrTbl", f"0x{self.sprite_ptr_table_offset:06X}", "0x99E4", "78 bytes (39 ptrs)")
		
		console.print(table)
		console.print()

		metadata = []
		success_count = 0
		ghost_sprite_data = None  # Cache for fallback
		
		for i, monster in enumerate(track(MONSTER_DATA, description="Extracting monsters")):
			# Calculate pointer offset for this monster
			ptr_offset = self.sprite_ptr_table_offset + (i * 2)
			
			# Read sprite data from ROM
			sprite_data = self.read_sprite_data(ptr_offset)
			
			# Special case: Specter (#17) has a buggy pointer in both PRG0 and PRG1
			# It points to 0x9BAA (Bank00) but sprite data doesn't exist there
			# Should use GhstSprts like Ghost (#3) and Poltergeist (#8)
			if not sprite_data and monster['name'] in ['Ghost', 'Poltergeist', 'Specter']:
				if ghost_sprite_data is None and monster['name'] == 'Ghost':
					console.print(f"[yellow]Warning: No sprite data for {monster['name']}[/yellow]")
					continue
				elif ghost_sprite_data is not None:
					# Use cached ghost sprite data
					sprite_data = ghost_sprite_data
					console.print(f"[dim]Using Ghost sprite data for {monster['name']} (ROM pointer bug workaround)[/dim]")
				elif monster['name'] == 'Ghost':
					# Try reading from the known good location (0x5BBA)
					fallback_offset = 0x5BBA
					sprite_data = self._read_sprite_data_at_offset(fallback_offset)
					if sprite_data:
						ghost_sprite_data = sprite_data
						console.print(f"[dim]Using fallback location for Ghost sprites[/dim]")
			
			# Cache Ghost sprite data for Poltergeist and Specter
			if monster['name'] == 'Ghost' and sprite_data and ghost_sprite_data is None:
				ghost_sprite_data = sprite_data
			
			if not sprite_data:
				console.print(f"[yellow]Warning: No sprite data for {monster['name']}[/yellow]")
				continue
			
			# Create monster directory
			monster_dir = self.output_dir / f"{monster['id']:02d}_{monster['name'].lower().replace(' ', '_')}"
			monster_dir.mkdir(exist_ok=True)

			# Render palette swatch
			palette_rgb = self.palette_to_rgb(monster['palette'])
			swatch = self.create_palette_swatch(palette_rgb, monster['name'])
			swatch.save(monster_dir / "palette.png")

			# Render sprite
			sprite_img = self.render_monster_sprite(monster, sprite_data, scale=6)
			if sprite_img:
				sprite_img.save(monster_dir / "sprite.png")

			# Save metadata
			monster_meta = {
				"id": monster['id'],
				"name": monster['name'],
				"palette_nes": monster['palette'],
				"palette_rgb": [[r, g, b] for r, g, b in palette_rgb],
				"sprite_tiles": len(sprite_data),
				"sprite_data": [{"tile": t, "attr": a, "x": x} for t, a, x in sprite_data],
				"rom_pointer_offset": f"0x{ptr_offset:06X}",
			}
			metadata.append(monster_meta)

			with open(monster_dir / "metadata.json", 'w') as f:
				json.dump(monster_meta, f, indent=2)
			
			success_count += 1

		# Save complete monster database
		with open(self.output_dir / "monsters_database.json", 'w') as f:
			json.dump(metadata, f, indent=2)

		console.print(f"\n[green]✓ Successfully extracted {success_count}/39 monsters to {self.output_dir}[/green]")
		
		# Show statistics
		stats = Table(title="Extraction Statistics")
		stats.add_column("Metric", style="cyan")
		stats.add_column("Value", style="green")
		
		stats.add_row("Total Monsters", str(len(MONSTER_DATA)))
		stats.add_row("Successfully Extracted", str(success_count))
		stats.add_row("Total Sprite Tiles", str(sum(m['sprite_tiles'] for m in metadata)))
		stats.add_row("Average Tiles per Monster", f"{sum(m['sprite_tiles'] for m in metadata) / len(metadata):.1f}")
		
		console.print()
		console.print(stats)

	def create_palette_swatch(self, palette_rgb: List[Tuple], name: str) -> Image.Image:
		"""Create palette swatch with color codes"""
		swatch_size = 64
		swatch = Image.new('RGB', (len(palette_rgb) * swatch_size, swatch_size))
		for i, color in enumerate(palette_rgb):
			for y in range(swatch_size):
				for x in range(swatch_size):
					swatch.putpixel((i * swatch_size + x, y), color)
		return swatch


def main():
	import sys
	if len(sys.argv) < 2:
		console.print("[yellow]Usage: python rom_monster_sprite_extractor.py <rom_path> [output_dir][/yellow]")
		sys.exit(1)

	rom_path = sys.argv[1]
	output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_assets/graphics_comprehensive"

	extractor = ROMMonsterSpriteExtractor(rom_path, output_dir)
	extractor.extract_all_monsters()


if __name__ == "__main__":
	main()
