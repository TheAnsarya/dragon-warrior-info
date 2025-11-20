#!/usr/bin/env python3
"""
Dragon Warrior Graphics Extractor
Extract graphics, palettes, and maps to PNG files with JSON metadata
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import json
import click
from PIL import Image, ImageDraw
from rich.console import Console
from rich.progress import track

from data_structures import (
	GameData, GraphicsData, Palette, Color, MapData, MapTile, TerrainType,
	DW_MONSTERS, DW_ITEMS, DW_SPELLS, DW_MAPS
)

console = Console()

class NESPalette:
	"""NES system palette"""
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

class DragonWarriorGraphicsExtractor:
	"""Extract and convert Dragon Warrior graphics to PNG"""

	def __init__(self, rom_path: str, output_dir: str):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.graphics_dir = self.output_dir / "graphics"
		self.palettes_dir = self.output_dir / "palettes"
		self.maps_dir = self.output_dir / "maps"
		self.json_dir = self.output_dir / "json"

		# Create directories
		for dir_path in [self.graphics_dir, self.palettes_dir, self.maps_dir, self.json_dir]:
			dir_path.mkdir(parents=True, exist_ok=True)

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.nes_palette = NESPalette()

	def extract_chr_rom(self) -> List[bytes]:
		"""Extract CHR-ROM data (graphics)"""
		# Dragon Warrior CHR-ROM starts at 0x8010 (after PRG-ROM)
		chr_start = 0x8010
		chr_size = 0x2000	# 8KB CHR-ROM

		if chr_start + chr_size <= len(self.rom_data):
			chr_data = self.rom_data[chr_start:chr_start + chr_size]

			# Split into 8x8 tiles (16 bytes each)
			tiles = []
			for i in range(0, len(chr_data), 16):
				if i + 16 <= len(chr_data):
					tiles.append(chr_data[i:i+16])

			return tiles

		return []

	def decode_tile(self, tile_data: bytes) -> List[List[int]]:
		"""Decode NES 8x8 tile to 2D pixel array"""
		if len(tile_data) != 16:
			return [[0] * 8 for _ in range(8)]

		pixels = [[0] * 8 for _ in range(8)]

		# NES tiles use 2 bit planes
		for y in range(8):
			plane1 = tile_data[y]
			plane2 = tile_data[y + 8]

			for x in range(8):
				bit = 7 - x
				pixel_value = ((plane1 >> bit) & 1) | (((plane2 >> bit) & 1) << 1)
				pixels[y][x] = pixel_value

		return pixels

	def extract_palettes(self) -> Dict[int, Palette]:
		"""Extract game palettes"""
		palettes = {}

		# Dragon Warrior palette data locations (approximate)
		palette_locations = [
			(0x5000, "Overworld"),
			(0x5004, "Dungeon"),
			(0x5008, "Town"),
			(0x500C, "Battle"),
			(0x5010, "Menu"),
			(0x5014, "Character"),
			(0x5018, "Monster"),
			(0x501C, "Dialog")
		]

		for i, (offset, name) in enumerate(palette_locations):
			if offset + 4 <= len(self.rom_data):
				palette_bytes = self.rom_data[offset:offset + 4]
				colors = []

				for byte_val in palette_bytes:
					if byte_val < len(self.nes_palette.COLORS):
						r, g, b = self.nes_palette.COLORS[byte_val]
						colors.append(Color(r, g, b))
					else:
						colors.append(Color(0, 0, 0))	# Default black

				palette = Palette(name=name, colors=colors)
				palettes[i] = palette

		return palettes

	def render_tile_to_image(self, tile_pixels: List[List[int]], palette: Palette) -> Image.Image:
		"""Render 8x8 tile to PIL Image"""
		img = Image.new('RGB', (8, 8))
		pixels = []

		for y in range(8):
			for x in range(8):
				color_index = tile_pixels[y][x]
				if color_index < len(palette.colors):
					color = palette.colors[color_index]
					pixels.append((color.r, color.g, color.b))
				else:
					pixels.append((0, 0, 0))

		img.putdata(pixels)
		return img

	def extract_graphics_set(self, tiles: List[bytes], palette: Palette, name: str) -> List[GraphicsData]:
		"""Extract a set of graphics tiles"""
		graphics_data = []

		for i, tile_data in enumerate(track(tiles, description=f"Processing {name} tiles")):
			tile_pixels = self.decode_tile(tile_data)

			graphics = GraphicsData(
				id=i,
				name=f"{name}_tile_{i:03d}",
				width=8,
				height=8,
				tile_data=list(tile_data),
				palette_id=0	# Default palette
			)

			graphics_data.append(graphics)

			# Render to PNG
			img = self.render_tile_to_image(tile_pixels, palette)
			# Scale up 8x for visibility
			img = img.resize((64, 64), Image.NEAREST)

			png_path = self.graphics_dir / f"{name}_tile_{i:03d}.png"
			img.save(png_path)

		return graphics_data

	def extract_sprite_graphics(self, tiles: List[bytes], palettes: Dict[int, Palette]) -> Dict[int, GraphicsData]:
		"""Extract sprite graphics (characters, monsters, items)"""
		graphics = {}
		default_palette = list(palettes.values())[0] if palettes else Palette("default", [Color(0,0,0)] * 4)

		# Character sprites (approximate tile ranges)
		sprite_ranges = {
			"hero": (0x00, 0x10),
			"monsters": (0x10, 0x50),
			"npcs": (0x50, 0x70),
			"items": (0x70, 0x80),
			"ui": (0x80, 0x90)
		}

		sprite_id = 0
		for sprite_type, (start_tile, end_tile) in sprite_ranges.items():
			for tile_idx in range(start_tile, min(end_tile, len(tiles))):
				if tile_idx < len(tiles):
					tile_data = tiles[tile_idx]
					tile_pixels = self.decode_tile(tile_data)

					graphics_data = GraphicsData(
						id=sprite_id,
						name=f"{sprite_type}_{tile_idx:03d}",
						width=8,
						height=8,
						tile_data=list(tile_data),
						palette_id=0
					)

					graphics[sprite_id] = graphics_data

					# Render sprite
					img = self.render_tile_to_image(tile_pixels, default_palette)
					img = img.resize((64, 64), Image.NEAREST)

					png_path = self.graphics_dir / f"{sprite_type}_{tile_idx:03d}.png"
					img.save(png_path)

					sprite_id += 1

		return graphics

	def extract_map_data(self) -> Dict[int, MapData]:
		"""Extract map data (simplified)"""
		maps = {}

		# Dragon Warrior overworld map (approximate location and size)
		overworld_data = {
			'id': 0,
			'name': 'Overworld',
			'width': 120,
			'height': 120,
			'data_offset': 0x6000	# Approximate
		}

		# Create simplified overworld map
		tiles = []
		for y in range(overworld_data['height']):
			row = []
			for x in range(overworld_data['width']):
				# Simplified terrain generation (would be read from ROM)
				terrain = TerrainType.GRASS
				if x == 0 or y == 0 or x == overworld_data['width']-1 or y == overworld_data['height']-1:
					terrain = TerrainType.WATER
				elif (x + y) % 10 == 0:
					terrain = TerrainType.FOREST

				tile = MapTile(
					tile_id=(y * overworld_data['width'] + x) % 256,
					terrain_type=terrain,
					walkable=terrain != TerrainType.WATER,
					encounter_rate=15 if terrain == TerrainType.GRASS else 0
				)
				row.append(tile)
			tiles.append(row)

		map_data = MapData(
			id=overworld_data['id'],
			name=overworld_data['name'],
			width=overworld_data['width'],
			height=overworld_data['height'],
			tiles=tiles,
			encounters=list(range(20)),	# Monster group IDs
			music_id=0,
			palette_id=0
		)

		maps[0] = map_data

		return maps

	def render_map_to_png(self, map_data: MapData, palette: Palette) -> Image.Image:
		"""Render map to PNG image"""
		# Scale for visibility
		tile_size = 4
		img_width = map_data.width * tile_size
		img_height = map_data.height * tile_size

		img = Image.new('RGB', (img_width, img_height), (0, 0, 0))
		draw = ImageDraw.Draw(img)

		# Terrain colors
		terrain_colors = {
			TerrainType.GRASS: (34, 139, 34),
			TerrainType.WATER: (0, 100, 200),
			TerrainType.MOUNTAIN: (139, 69, 19),
			TerrainType.FOREST: (0, 100, 0),
			TerrainType.SWAMP: (85, 107, 47),
			TerrainType.DESERT: (238, 203, 173),
			TerrainType.TOWN: (160, 160, 160),
			TerrainType.CASTLE: (128, 128, 128),
			TerrainType.CAVE: (64, 64, 64),
			TerrainType.SHRINE: (255, 215, 0)
		}

		for y in range(map_data.height):
			for x in range(map_data.width):
				if y < len(map_data.tiles) and x < len(map_data.tiles[y]):
					tile = map_data.tiles[y][x]
					color = terrain_colors.get(tile.terrain_type, (0, 0, 0))

					x1 = x * tile_size
					y1 = y * tile_size
					x2 = x1 + tile_size
					y2 = y1 + tile_size

					draw.rectangle([x1, y1, x2, y2], fill=color)

		return img

	def save_palette_image(self, palette: Palette, filename: str):
		"""Save palette as PNG swatch"""
		swatch_size = 64
		img = Image.new('RGB', (swatch_size * 4, swatch_size))

		for i, color in enumerate(palette.colors):
			x1 = i * swatch_size
			x2 = x1 + swatch_size

			pixels = [(color.r, color.g, color.b)] * (swatch_size * swatch_size)
			color_img = Image.new('RGB', (swatch_size, swatch_size))
			color_img.putdata(pixels)

			img.paste(color_img, (x1, 0))

		img.save(self.palettes_dir / filename)

	def extract_all_graphics(self) -> GameData:
		"""Extract all graphics and data"""
		console.print("[blue]Extracting Dragon Warrior graphics...[/blue]\n")

		# Extract CHR-ROM tiles
		tiles = self.extract_chr_rom()
		console.print(f"Extracted {len(tiles)} CHR-ROM tiles")

		# Extract palettes
		palettes = self.extract_palettes()
		console.print(f"Extracted {len(palettes)} palettes")

		# Save palette swatches
		for palette_id, palette in palettes.items():
			filename = f"palette_{palette_id:02d}_{palette.name.lower()}.png"
			self.save_palette_image(palette, filename)

		# Extract sprite graphics
		default_palette = list(palettes.values())[0] if palettes else Palette("default", [Color(255,255,255), Color(170,170,170), Color(85,85,85), Color(0,0,0)])
		graphics = self.extract_sprite_graphics(tiles, palettes)
		console.print(f"Extracted {len(graphics)} sprite graphics")

		# Extract maps
		maps = self.extract_map_data()
		console.print(f"Extracted {len(maps)} maps")

		# Render maps to PNG
		for map_id, map_data in maps.items():
			map_img = self.render_map_to_png(map_data, default_palette)
			map_img.save(self.maps_dir / f"map_{map_id:02d}_{map_data.name.lower()}.png")

		# Create game data structure with placeholder data
		game_data = GameData(
			monsters={},	# Will be populated by data extractor
			items={},	 # Will be populated by data extractor
			spells={},	# Will be populated by data extractor
			shops={},	 # Will be populated by data extractor
			dialogs={},	 # Will be populated by data extractor
			maps=maps,
			npcs={},		# Will be populated by data extractor
			graphics=graphics,
			palettes=palettes
		)

		# Save JSON data
		game_data.save_json(self.json_dir / "graphics_data.json")

		# Save individual JSON files
		self._save_individual_json_files(palettes, graphics, maps)

		console.print(f"\n[green]Graphics extraction complete![/green]")
		console.print(f"	 Graphics: {self.graphics_dir}")
		console.print(f"	 Palettes: {self.palettes_dir}")
		console.print(f"	 Maps: {self.maps_dir}")
		console.print(f"	 JSON: {self.json_dir}")

		return game_data

	def _save_individual_json_files(self, palettes: Dict[int, Palette], graphics: Dict[int, GraphicsData], maps: Dict[int, MapData]):
		"""Save individual JSON files for each data type"""

		# Palettes
		palettes_data = {str(k): v.to_dict() for k, v in palettes.items()}
		with open(self.json_dir / "palettes.json", 'w', encoding='utf-8') as f:
			json.dump(palettes_data, f, indent=2)

		# Graphics
		graphics_data = {str(k): v.to_dict() for k, v in graphics.items()}
		with open(self.json_dir / "graphics.json", 'w', encoding='utf-8') as f:
			json.dump(graphics_data, f, indent=2)

		# Maps
		maps_data = {str(k): v.to_dict() for k, v in maps.items()}
		with open(self.json_dir / "maps.json", 'w', encoding='utf-8') as f:
			json.dump(maps_data, f, indent=2)

@click.command()
@click.argument('rom_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='assets', help='Output directory')
def extract_graphics(rom_path: str, output_dir: str):
	"""Extract Dragon Warrior graphics to PNG and JSON"""

	try:
		extractor = DragonWarriorGraphicsExtractor(rom_path, output_dir)
		game_data = extractor.extract_all_graphics()

		console.print("\n[green]Graphics extraction completed successfully![/green]")

	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")
		raise

if __name__ == "__main__":
	extract_graphics()
