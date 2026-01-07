#!/usr/bin/env python3
"""
Dragon Warrior CHR Tile Organizer

Reorganizes 1024 individual CHR tiles into purposeful grouped sprite sheets:
- Hero sprites (all animations)
- Monsters (all enemy sprites)
- NPCs (townspeople, guards, royalty)
- Items & Equipment (weapons, armor, treasures)
- UI Elements (menus, borders, cursors)
- Font & Text (all characters)
- Overworld Terrain (grass, mountains, water, trees)
- Town Buildings (walls, doors, roofs)
- Dungeon Tiles (stone walls, floors, stairs)
- Castle Interior (special areas)

Based on Dragon Warrior (NES) - Graphics Data.wikitext documentation.
"""

import struct
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict
import json

# NES Color Palette (standard NTSC approximation)
NES_PALETTE = [
	(84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136), (68, 0, 100), (92, 0, 48),
	(84, 4, 0), (60, 24, 0), (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
	(0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228), (136, 20, 176), (160, 20, 100),
	(152, 34, 32), (120, 60, 0), (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
	(0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236), (228, 84, 236), (236, 88, 180),
	(236, 106, 100), (212, 136, 32), (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
	(56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
	(236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236), (236, 174, 236), (236, 174, 212),
	(236, 180, 176), (228, 196, 144), (204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
	(160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0),
]

# Dragon Warrior Palette Definitions (based on wiki documentation)
PALETTES = {
	'overworld': [0x0f, 0x30, 0x10, 0x00],      # Black, White, Light Gray, Dark Gray
	'dungeon': [0x0f, 0x00, 0x10, 0x30],        # Black, Dark Gray, Light Gray, White
	'town': [0x0f, 0x16, 0x27, 0x30],           # Black, Brown, Orange, White
	'battle': [0x0f, 0x00, 0x10, 0x30],         # Black, Dark Gray, Light Gray, White
	'menu': [0x0f, 0x00, 0x10, 0x30],           # Black, Dark Gray, Light Gray, White
	'character': [0x0f, 0x16, 0x27, 0x30],      # Black, Brown, Orange, White
	'monster': [0x0f, 0x05, 0x15, 0x30],        # Black, Purple, Pink, White
	'dialog': [0x0f, 0x00, 0x10, 0x30],         # Black, Dark Gray, Light Gray, White
}

class CHRTileOrganizer:
	"""Organize CHR tiles into purposeful sprite sheets"""

	def __init__(self, rom_path: str, output_dir: str):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)

		# CHR-ROM starts at 0x10010 (after 16-byte header + 64KB PRG-ROM)
		self.chr_offset = 0x10010
		self.chr_size = 0x4000  # 16KB CHR-ROM

		# Extract all tiles from ROM
		self.tiles = self.extract_chr_tiles()

	def extract_chr_tiles(self) -> List[bytes]:
		"""Extract all 1024 tiles from CHR-ROM"""
		with open(self.rom_path, 'rb') as f:
			f.seek(self.chr_offset)
			chr_data = f.read(self.chr_size)

		tiles = []
		for i in range(0, len(chr_data), 16):
			tile_data = chr_data[i:i+16]
			if len(tile_data) == 16:
				tiles.append(tile_data)

		print(f"Extracted {len(tiles)} tiles from CHR-ROM")
		return tiles

	def decode_tile(self, tile_data: bytes) -> List[List[int]]:
		"""Decode NES 2bpp tile format to 8x8 pixel array"""
		pixels = [[0] * 8 for _ in range(8)]

		for row in range(8):
			low_byte = tile_data[row]
			high_byte = tile_data[row + 8]

			for col in range(8):
				bit_pos = 7 - col
				low_bit = (low_byte >> bit_pos) & 1
				high_bit = (high_byte >> bit_pos) & 1
				pixels[row][col] = (high_bit << 1) | low_bit

		return pixels

	def render_tile(self, tile_pixels: List[List[int]], palette_name: str, scale: int = 4) -> Image.Image:
		"""Render an 8x8 tile with specified palette and scale"""
		palette = PALETTES.get(palette_name, PALETTES['menu'])
		rgb_palette = [NES_PALETTE[idx] for idx in palette]

		img = Image.new('RGB', (8, 8))
		pixels_data = img.load()

		for y in range(8):
			for x in range(8):
				color_idx = tile_pixels[y][x]
				pixels_data[x, y] = rgb_palette[color_idx]

		# Scale up for visibility
		if scale > 1:
			img = img.resize((8 * scale, 8 * scale), Image.Resampling.NEAREST)

		return img

	def create_sprite_sheet(self, tile_ranges: List[Tuple[int, int]],
						   palette_name: str, output_name: str,
						   tiles_per_row: int = 16, scale: int = 2,
						   description: str = "") -> Dict:
		"""Create a sprite sheet from tile ranges"""

		# Collect all tiles for this sheet
		all_tiles = []
		for start, end in tile_ranges:
			for tile_idx in range(start, end + 1):
				if tile_idx < len(self.tiles):
					all_tiles.append((tile_idx, self.tiles[tile_idx]))

		if not all_tiles:
			print(f"Warning: No tiles found for {output_name}")
			return {}

		# Calculate sheet dimensions
		total_tiles = len(all_tiles)
		rows = (total_tiles + tiles_per_row - 1) // tiles_per_row

		sheet_width = tiles_per_row * 8 * scale
		sheet_height = rows * 8 * scale

		# Create sprite sheet
		sheet = Image.new('RGB', (sheet_width, sheet_height), (0, 0, 0))

		for idx, (tile_idx, tile_data) in enumerate(all_tiles):
			tile_pixels = self.decode_tile(tile_data)
			tile_img = self.render_tile(tile_pixels, palette_name, scale)

			grid_x = (idx % tiles_per_row) * 8 * scale
			grid_y = (idx // tiles_per_row) * 8 * scale

			sheet.paste(tile_img, (grid_x, grid_y))

		# Save sprite sheet
		output_path = self.output_dir / f"{output_name}.png"
		sheet.save(output_path)
		print(f"Created: {output_name}.png ({total_tiles} tiles, {sheet_width}x{sheet_height})")

		# Return metadata
		return {
			'name': output_name,
			'description': description,
			'palette': palette_name,
			'tile_count': total_tiles,
			'tile_ranges': tile_ranges,
			'dimensions': {'width': sheet_width, 'height': sheet_height},
			'tiles_per_row': tiles_per_row,
			'scale': scale
		}

	def organize_all_tiles(self):
		"""Create all organized sprite sheets based on Dragon Warrior tile organization"""

		metadata = {
			'rom': str(self.rom_path),
			'chr_offset': f"0x{self.chr_offset:X}",
			'chr_size': self.chr_size,
			'total_tiles': len(self.tiles),
			'sprite_sheets': []
		}

		print("\n=== CHR Bank 0 (Sprites) ===\n")

		# Hero sprites (tiles 0x00-0x0f, 16 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x00, 0x0f)],
			'character',
			'hero_sprites',
			tiles_per_row=8,
			scale=4,
			description="Hero character sprites: 4 directions × 2 frames × 2 weapon states"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Monster Sprites (tiles 0x00-0x3f, 64 tiles)
		# NOTE: These 64 tile slots contain 252 unique tiles across 19 sprite definitions
		# used by 39 monsters. Extensive sprite sharing occurs (e.g., SlimeSprts shared
		# by Slime, Red Slime, Metal Slime). See extracted_assets/reports/monster_sprite_allocation.md
		sheet_info = self.create_sprite_sheet(
			[(0x00, 0x3f)],
			'monster',
			'monster_sprites',
			tiles_per_row=16,
			scale=3,
			description="Monster sprites: 252 tiles in 19 definitions for 39 monsters (sprite sharing)"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# NPC sprites (tiles 0x50-0x6f, 32 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x50, 0x6f)],
			'character',
			'npc_sprites',
			tiles_per_row=8,
			scale=4,
			description="NPCs: townspeople, guards, king, princess, merchants"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Items & Equipment (tiles 0x70-0x7f, 16 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x70, 0x7f)],
			'menu',
			'items_equipment',
			tiles_per_row=8,
			scale=4,
			description="Weapons, armor, items, treasure chests"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# UI Elements (tiles 0x80-0x8f, 16 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x80, 0x8f)],
			'menu',
			'ui_elements',
			tiles_per_row=8,
			scale=4,
			description="Menu cursors, borders, text boxes, UI decorations"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Font & Text (tiles 0x90-0xff, 112 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x90, 0xff)],
			'dialog',
			'font_text',
			tiles_per_row=16,
			scale=3,
			description="Text characters, numbers, symbols, punctuation"
		)
		metadata['sprite_sheets'].append(sheet_info)

		print("\n=== CHR Bank 1 (Background Tiles) ===\n")

		# Overworld Terrain (tiles 0x100-0x13f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x100, 0x13f)],
			'overworld',
			'overworld_terrain',
			tiles_per_row=16,
			scale=3,
			description="Overworld: grass, trees, mountains, water, bridges"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Town Buildings (tiles 0x140-0x17f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x140, 0x17f)],
			'town',
			'town_buildings',
			tiles_per_row=16,
			scale=3,
			description="Town tiles: buildings, roads, doors, roofs, walls"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Dungeon Tiles (tiles 0x180-0x1bf, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x180, 0x1bf)],
			'dungeon',
			'dungeon_tiles',
			tiles_per_row=16,
			scale=3,
			description="Dungeon: stone walls, floors, stairs, cave features"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Castle Interior (tiles 0x1c0-0x1ff, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x1c0, 0x1ff)],
			'battle',
			'castle_interior',
			tiles_per_row=16,
			scale=3,
			description="Castle interiors, throne room, special areas"
		)
		metadata['sprite_sheets'].append(sheet_info)

		print("\n=== CHR Bank 2 (Battle Backgrounds) ===\n")

		# Battle Background Set 1 (tiles 0x200-0x23f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x200, 0x23f)],
			'battle',
			'battle_background_1',
			tiles_per_row=16,
			scale=3,
			description="Battle backgrounds: grass/field patterns"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Battle Background Set 2 (tiles 0x240-0x27f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x240, 0x27f)],
			'battle',
			'battle_background_2',
			tiles_per_row=16,
			scale=3,
			description="Battle backgrounds: dungeon/cave patterns"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Battle Background Set 3 (tiles 0x280-0x2bf, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x280, 0x2bf)],
			'battle',
			'battle_background_3',
			tiles_per_row=16,
			scale=3,
			description="Battle backgrounds: castle/throne room patterns"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Battle Background Set 4 (tiles 0x2c0-0x2ff, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x2c0, 0x2ff)],
			'battle',
			'battle_background_4',
			tiles_per_row=16,
			scale=3,
			description="Battle backgrounds: special area patterns"
		)
		metadata['sprite_sheets'].append(sheet_info)

		print("\n=== CHR Bank 3 (Extended Graphics) ===\n")

		# Extended Graphics Set 1 (tiles 0x300-0x33f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x300, 0x33f)],
			'menu',
			'extended_graphics_1',
			tiles_per_row=16,
			scale=3,
			description="Extended graphics: additional UI and special elements"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Extended Graphics Set 2 (tiles 0x340-0x37f, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x340, 0x37f)],
			'menu',
			'extended_graphics_2',
			tiles_per_row=16,
			scale=3,
			description="Extended graphics: title screen and credits"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Extended Graphics Set 3 (tiles 0x380-0x3bf, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x380, 0x3bf)],
			'menu',
			'extended_graphics_3',
			tiles_per_row=16,
			scale=3,
			description="Extended graphics: special effects and animations"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Extended Graphics Set 4 (tiles 0x3c0-0x3ff, 64 tiles)
		sheet_info = self.create_sprite_sheet(
			[(0x3c0, 0x3ff)],
			'menu',
			'extended_graphics_4',
			tiles_per_row=16,
			scale=3,
			description="Extended graphics: miscellaneous tiles"
		)
		metadata['sprite_sheets'].append(sheet_info)

		# Save metadata
		metadata_path = self.output_dir / 'sprite_sheets_metadata.json'
		with open(metadata_path, 'w', encoding='utf-8') as f:
			json.dump(metadata, f, indent=2)

		print(f"\n✓ Created {len(metadata['sprite_sheets'])} organized sprite sheets")
		print(f"✓ Saved metadata: sprite_sheets_metadata.json")

		return metadata

def main():
	"""Main execution"""
	import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

	# Default paths
	rom_path = Path(__file__).parent.parent / 'roms' / 'Dragon Warrior (U) (PRG1) [!].nes'
	output_dir = Path(__file__).parent.parent / 'extracted_assets' / 'chr_organized'

	# Allow command-line override
	if len(sys.argv) > 1:
		rom_path = Path(sys.argv[1])
	if len(sys.argv) > 2:
		output_dir = Path(sys.argv[2])

	if not rom_path.exists():
		print(f"Error: ROM not found at {rom_path}")
		print("Usage: python organize_chr_tiles.py [rom_path] [output_dir]")
		return 1

	print("=" * 70)
	print("Dragon Warrior CHR Tile Organizer")
	print("=" * 70)
	print(f"ROM: {rom_path}")
	print(f"Output: {output_dir}")
	print()

	organizer = CHRTileOrganizer(str(rom_path), str(output_dir))
	metadata = organizer.organize_all_tiles()

	print("\n" + "=" * 70)
	print("Sprite Sheet Summary:")
	print("=" * 70)
	for sheet in metadata['sprite_sheets']:
		print(f"  {sheet['name']:30s} - {sheet['tile_count']:3d} tiles - {sheet['description']}")

	print("\n✓ All sprite sheets created successfully!")
	print(f"✓ Output directory: {output_dir}")

	return 0

if __name__ == '__main__':
	exit(main())
