#!/usr/bin/env python3
"""
Dragon Warrior World Map Extractor
Extracts and visualizes the 120×120 overworld map from ROM

The overworld uses Run-Length Encoding (RLE):
- Each byte: upper nibble = tile type, lower nibble + 1 = repeat count
- Map is 120×120 tiles decoded from compressed row data
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
import json

# Tile type constants (upper nibble of RLE byte)
TILE_TYPES = {
	0x0: 'Grass',
	0x1: 'Desert',
	0x2: 'Hills',
	0x3: 'Mountain',
	0x4: 'Water',
	0x5: 'Rock Wall',
	0x6: 'Forest',
	0x7: 'Poison',
	0x8: 'Town',
	0x9: 'Tunnel',
	0xa: 'Castle',
	0xb: 'Bridge',
	0xc: 'Stairs',
	0xd: 'Unknown_D',
	0xe: 'Unknown_E',
	0xf: 'Unknown_F'
}

# NES palette colors for visualization
TILE_COLORS = {
	0x0: (34, 177, 76),      # Grass - Green
	0x1: (255, 217, 102),    # Desert - Sand
	0x2: (139, 90, 43),      # Hills - Brown
	0x3: (96, 96, 96),       # Mountain - Gray
	0x4: (0, 112, 221),      # Water - Blue
	0x5: (64, 64, 64),       # Rock Wall - Dark Gray
	0x6: (0, 100, 0),        # Forest - Dark Green
	0x7: (128, 0, 128),      # Poison - Purple
	0x8: (192, 192, 192),    # Town - Light Gray
	0x9: (139, 69, 19),      # Tunnel - Dark Brown
	0xa: (255, 215, 0),      # Castle - Gold
	0xb: (210, 180, 140),    # Bridge - Tan
	0xc: (255, 165, 0),      # Stairs - Orange
	0xd: (255, 0, 255),      # Unknown - Magenta
	0xe: (255, 0, 255),      # Unknown - Magenta
	0xf: (255, 0, 255)       # Unknown - Magenta
}

class WorldMapExtractor:
	"""Extract and decode Dragon Warrior overworld map"""

	def __init__(self, rom_path: str):
		"""Initialize extractor with ROM path"""
		self.rom_path = Path(rom_path)
		self.rom_data = None
		self.map_width = 120
		self.map_height = 120
		self.map_data = []  # 2D list of tile types

		# World map data location in ROM (Bank00)
		# WrldMapPtrTbl at $a653 (CPU) = 0x6663 (file offset)
		# Row data starts after pointer table
		self.world_map_start = 0x5d6d  # File offset for Row000 ($9d5d CPU - $8000 + $4010 Bank00)

	def load_rom(self):
		"""Load ROM file into memory"""
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM not found: {self.rom_path}")

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		print(f"✓ Loaded ROM: {len(self.rom_data)} bytes")

	def decode_rle_row(self, offset: int, tiles_needed: int) -> Tuple[List[int], int]:
		"""
		Decode RLE row data

		Args:
			offset: Starting offset in ROM data
			tiles_needed: Number of tiles to decode

		Returns:
			Tuple of (decoded tiles list, new offset)
		"""
		tiles = []
		current_offset = offset

		while len(tiles) < tiles_needed:
			if current_offset >= len(self.rom_data):
				print(f"⚠ Warning: Ran past end of ROM at offset 0x{current_offset:04X}")
				break

			byte = self.rom_data[current_offset]
			current_offset += 1

			tile_type = (byte >> 4) & 0x0f  # Upper nibble
			repeat_count = (byte & 0x0f) + 1  # Lower nibble + 1

			# Add tiles
			for _ in range(repeat_count):
				if len(tiles) < tiles_needed:
					tiles.append(tile_type)

		return tiles, current_offset

	def extract_world_map(self):
		"""Extract complete 120×120 world map"""
		print(f"\nExtracting {self.map_width}×{self.map_height} overworld map...")

		# Start reading from Row000
		current_offset = self.world_map_start

		for row in range(self.map_height):
			# Decode this row (120 tiles)
			tiles, current_offset = self.decode_rle_row(current_offset, self.map_width)
			self.map_data.append(tiles)

			if row % 20 == 0:
				print(f"  Decoded row {row}/{self.map_height}...")

		print(f"✓ Extracted {self.map_width}×{self.map_height} = {self.map_width * self.map_height} tiles")

		# Verify data
		self.verify_extraction()

	def verify_extraction(self):
		"""Verify extracted map data"""
		print("\nVerifying extraction...")

		# Count tile types
		tile_counts = {}
		for row in self.map_data:
			for tile in row:
				tile_counts[tile] = tile_counts.get(tile, 0) + 1

		print("\nTile type distribution:")
		for tile_type in sorted(tile_counts.keys()):
			count = tile_counts[tile_type]
			percentage = (count / (self.map_width * self.map_height)) * 100
			name = TILE_TYPES.get(tile_type, f'Unknown_{tile_type:X}')
			print(f"  {name:12s} ({tile_type:X}): {count:5d} tiles ({percentage:5.2f}%)")

	def save_to_json(self, output_path: str):
		"""Save map data to JSON"""
		output_file = Path(output_path)
		output_file.parent.mkdir(parents=True, exist_ok=True)

		# Convert to serializable format
		map_json = {
			'width': self.map_width,
			'height': self.map_height,
			'tiles': []
		}

		for y, row in enumerate(self.map_data):
			row_data = []
			for x, tile_type in enumerate(row):
				row_data.append({
					'x': x,
					'y': y,
					'type': tile_type,
					'name': TILE_TYPES.get(tile_type, f'Unknown_{tile_type:X}')
				})
			map_json['tiles'].append(row_data)

		with open(output_file, 'w') as f:
			json.dump(map_json, f, indent=2)

		print(f"\n✓ Saved map data: {output_file}")

	def render_to_png(self, output_path: str, tile_size: int = 4):
		"""
		Render map to PNG image

		Args:
			output_path: Output PNG file path
			tile_size: Size of each tile in pixels (default 4 for 480×480 image)
		"""
		output_file = Path(output_path)
		output_file.parent.mkdir(parents=True, exist_ok=True)

		# Create image
		img_width = self.map_width * tile_size
		img_height = self.map_height * tile_size
		img = Image.new('RGB', (img_width, img_height), (0, 0, 0))
		draw = ImageDraw.Draw(img)

		print(f"\nRendering {img_width}×{img_height} map image...")

		# Draw tiles
		for y, row in enumerate(self.map_data):
			for x, tile_type in enumerate(row):
				color = TILE_COLORS.get(tile_type, (255, 0, 255))  # Magenta for unknown

				x1 = x * tile_size
				y1 = y * tile_size
				x2 = x1 + tile_size
				y2 = y1 + tile_size

				draw.rectangle([x1, y1, x2, y2], fill=color)

			if y % 20 == 0:
				print(f"  Rendered row {y}/{self.map_height}...")

		# Save image
		img.save(output_file)
		print(f"✓ Saved map image: {output_file}")

		# Also create a larger version with grid
		self.render_large_with_grid(output_path.replace('.png', '_large.png'))

	def render_large_with_grid(self, output_path: str, tile_size: int = 8):
		"""
		Render large map with grid overlay

		Args:
			output_path: Output PNG file path
			tile_size: Size of each tile in pixels (default 8 for 960×960 image)
		"""
		output_file = Path(output_path)

		# Create image
		img_width = self.map_width * tile_size
		img_height = self.map_height * tile_size
		img = Image.new('RGB', (img_width, img_height), (0, 0, 0))
		draw = ImageDraw.Draw(img)

		print(f"\nRendering {img_width}×{img_height} large map with grid...")

		# Draw tiles
		for y, row in enumerate(self.map_data):
			for x, tile_type in enumerate(row):
				color = TILE_COLORS.get(tile_type, (255, 0, 255))

				x1 = x * tile_size
				y1 = y * tile_size
				x2 = x1 + tile_size
				y2 = y1 + tile_size

				draw.rectangle([x1, y1, x2, y2], fill=color)

		# Draw grid lines every 8 tiles (screen size)
		grid_color = (128, 128, 128)
		for i in range(0, self.map_width + 1, 8):
			x = i * tile_size
			draw.line([(x, 0), (x, img_height)], fill=grid_color, width=1)

		for i in range(0, self.map_height + 1, 8):
			y = i * tile_size
			draw.line([(0, y), (img_width, y)], fill=grid_color, width=1)

		# Save image
		img.save(output_file)
		print(f"✓ Saved large map: {output_file}")

	def create_legend(self, output_path: str):
		"""Create legend image showing tile types"""
		output_file = Path(output_path)
		output_file.parent.mkdir(parents=True, exist_ok=True)

		# Legend dimensions
		tile_size = 32
		label_width = 200
		row_height = 40

		# Count non-unknown tile types
		tile_types = [t for t in TILE_TYPES.keys() if t < 0xd]
		img_width = tile_size + label_width + 40
		img_height = len(tile_types) * row_height + 40

		# Create image
		img = Image.new('RGB', (img_width, img_height), (255, 255, 255))
		draw = ImageDraw.Draw(img)

		# Title
		draw.text((20, 10), "Dragon Warrior Overworld - Tile Legend", fill=(0, 0, 0))

		# Draw legend entries
		y_offset = 50
		for tile_type in tile_types:
			name = TILE_TYPES[tile_type]
			color = TILE_COLORS[tile_type]

			# Draw color swatch
			x1 = 20
			y1 = y_offset
			x2 = x1 + tile_size
			y2 = y1 + tile_size
			draw.rectangle([x1, y1, x2, y2], fill=color, outline=(0, 0, 0))

			# Draw label
			label_x = x2 + 10
			label_y = y1 + 8
			draw.text((label_x, label_y), f"0x{tile_type:X} - {name}", fill=(0, 0, 0))

			y_offset += row_height

		# Save legend
		img.save(output_file)
		print(f"✓ Saved legend: {output_file}")

def main():
	"""Main extraction routine"""
	# Paths
	rom_path = "roms/Dragon Warrior (U) (PRG1) [!].nes"
	output_dir = "extracted_assets/maps"

	print("=" * 70)
	print("Dragon Warrior World Map Extractor")
	print("=" * 70)

	try:
		# Create extractor
		extractor = WorldMapExtractor(rom_path)

		# Load ROM
		extractor.load_rom()

		# Extract map
		extractor.extract_world_map()

		# Save outputs
		extractor.save_to_json(f"{output_dir}/overworld_map.json")
		extractor.render_to_png(f"{output_dir}/overworld_map.png", tile_size=4)
		extractor.create_legend(f"{output_dir}/overworld_legend.png")

		print("\n" + "=" * 70)
		print("✓ EXTRACTION COMPLETE")
		print("=" * 70)
		print(f"\nOutput files:")
		print(f"  - {output_dir}/overworld_map.json")
		print(f"  - {output_dir}/overworld_map.png (480×480)")
		print(f"  - {output_dir}/overworld_map_large.png (960×960 with grid)")
		print(f"  - {output_dir}/overworld_legend.png")

		return 0

	except Exception as e:
		print(f"\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
		return 1

if __name__ == '__main__':
	sys.exit(main())
