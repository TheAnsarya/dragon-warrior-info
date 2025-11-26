#!/usr/bin/env python3
"""
Transform Binary Intermediate Format to Editable Assets

This script transforms .dwdata binary files to human-editable JSON/PNG assets.

Pipeline: ROM → .dwdata → JSON/PNG (this script) → .dwdata → ROM

Usage:
	python binary_to_assets.py
	python binary_to_assets.py --binary-dir custom/binary/
	python binary_to_assets.py --output-dir custom/output/

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import struct
import zlib
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse

try:
	from PIL import Image
except ImportError:
	print("WARNING: PIL not available, graphics export disabled")
	Image = None

# Constants
MAGIC = b'DWDT'

# Data type IDs
TYPE_MONSTER = 0x01
TYPE_SPELL = 0x02
TYPE_ITEM = 0x03
TYPE_MAP = 0x04
TYPE_TEXT = 0x05
TYPE_GRAPHICS = 0x06

# Monster names (39 total)
MONSTER_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician",
	"Magidrakee", "Scorpion", "Druin", "Poltergeist", "Droll",
	"Drakeema", "Skeleton", "Warlock", "Metal Scorpion", "Wolf",
	"Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord",
	"Drollmagi", "Wyvern", "Rouge Scorpion", "Wraith Knight", "Golem",
	"Goldman", "Knight", "Magiwyvern", "Demon Knight", "Werewolf",
	"Green Dragon", "Starwyvern", "Wizard", "Axe Knight", "Blue Dragon",
	"Stoneman", "Armored Knight", "Red Dragon", "Dragonlord"
]

# Spell names (10 total)
SPELL_NAMES = [
	"HEAL", "HURT", "SLEEP", "RADIANT", "STOPSPELL",
	"OUTSIDE", "RETURN", "REPEL", "HEALMORE", "HURTMORE"
]

# Item names (32 total)
ITEM_NAMES = [
	"Herb", "Torch", "Magic Key", "Wings", "Dragon's Scale",
	"Fairy Water", "Warrior's Ring", "Cursed Belt", "Silver Harp",
	"Death Necklace", "Stones of Sunlight", "Staff of Rain", "Rainbow Drop",
	"Gwaelin's Love", "Erdrick's Token", "(Unused 15)", "(Unused 16)", "(Unused 17)",
	"Bamboo Pole", "Club", "Copper Sword", "Hand Axe", "Broad Sword",
	"Flame Sword", "Erdrick's Sword", "Clothes", "Leather Armor", "Chain Mail",
	"Half Plate", "Full Plate", "Magic Armor", "Erdrick's Armor"
]

# Default paths
DEFAULT_BINARY_DIR = "extracted_assets/binary"
DEFAULT_JSON_DIR = "extracted_assets/json"
DEFAULT_GRAPHICS_DIR = "extracted_assets/graphics"

# NES palette (64 colors)
NES_PALETTE = [
	0x666666, 0x002A88, 0x1412A7, 0x3B00A4, 0x5C007E,
	0x6E0040, 0x6C0600, 0x561D00, 0x333500, 0x0B4800,
	0x005200, 0x004F08, 0x00404D, 0x000000, 0x000000,
	0x000000, 0xADADAD, 0x155FD9, 0x4240FF, 0x7527FE,
	0xA01ACC, 0xB71E7B, 0xB53120, 0x994E00, 0x6B6D00,
	0x388700, 0x0C9300, 0x008F32, 0x007C8D, 0x000000,
	0x000000, 0x000000, 0xFFFEFF, 0x64B0FF, 0x9290FF,
	0xC676FF, 0xF36AFF, 0xFE6ECC, 0xFE8170, 0xEA9E22,
	0xBCBE00, 0x88D800, 0x5CE430, 0x45E082, 0x48CDDE,
	0x4F4F4F, 0x000000, 0x000000, 0xFFFEFF, 0xC0DFFF,
	0xD3D2FF, 0xE8C8FF, 0xFBC2FF, 0xFEC4EA, 0xFECCC5,
	0xF7D8A5, 0xE4E594, 0xCFEF96, 0xBDF4AB, 0xB3F3CC,
	0xB5EBF2, 0xB8B8B8, 0x000000, 0x000000
]


class BinaryReader:
	"""Read and validate .dwdata binary files"""

	def __init__(self, path: str):
		"""
		Initialize reader with .dwdata file

		Args:
			path: Path to .dwdata file
		"""
		self.path = path
		self.data = None
		self.header = {}

	def load(self) -> bool:
		"""
		Load and validate .dwdata file

		Returns:
			True if valid file loaded
		"""
		if not os.path.exists(self.path):
			print(f"  ❌ File not found: {self.path}")
			return False

		with open(self.path, 'rb') as f:
			self.data = f.read()

		# Validate header
		if len(self.data) < 32:
			print(f"  ❌ File too small: {len(self.data)} bytes")
			return False

		if self.data[0:4] != MAGIC:
			print(f"  ❌ Invalid magic: {self.data[0:4]}")
			return False

		# Parse header
		self.header = {
			'magic': self.data[0:4].decode('ascii'),
			'version_major': self.data[4],
			'version_minor': self.data[5],
			'data_type': self.data[6],
			'flags': self.data[7],
			'data_size': struct.unpack_from('<I', self.data, 0x08)[0],
			'rom_offset': struct.unpack_from('<I', self.data, 0x0C)[0],
			'crc32': struct.unpack_from('<I', self.data, 0x10)[0],
			'timestamp': struct.unpack_from('<I', self.data, 0x14)[0]
		}

		# Verify checksum
		data_section = self.data[32:32 + self.header['data_size']]
		calc_crc = zlib.crc32(data_section) & 0xFFFFFFFF

		if calc_crc != self.header['crc32']:
			print(f"  ❌ CRC mismatch: {calc_crc:08X} != {self.header['crc32']:08X}")
			return False

		return True

	def get_data_section(self) -> bytes:
		"""Get data section (after 32-byte header)"""
		return self.data[32:32 + self.header['data_size']]


class AssetTransformer:
	"""Transform .dwdata binary to JSON/PNG assets"""

	def __init__(self, binary_dir: str, json_dir: str, graphics_dir: str):
		"""
		Initialize transformer

		Args:
			binary_dir: Directory containing .dwdata files
			json_dir: Output directory for JSON files
			graphics_dir: Output directory for PNG files
		"""
		self.binary_dir = binary_dir
		self.json_dir = json_dir
		self.graphics_dir = graphics_dir

	def transform_monsters(self) -> bool:
		"""
		Transform monsters.dwdata → monsters.json

		Returns:
			True if successful
		"""
		print("\n--- Transforming Monster Data ---")

		# Load binary file
		reader = BinaryReader(os.path.join(self.binary_dir, 'monsters.dwdata'))
		if not reader.load():
			return False

		data = reader.get_data_section()

		# Parse monsters
		monsters = []
		for i in range(39):
			offset = i * 16
			entry = data[offset:offset + 16]

			monster = {
				"id": i,
				"name": MONSTER_NAMES[i],
				"attack": entry[0],
				"defense": entry[1],
				"hp": entry[2],
				"spell": entry[3],
				"agility": entry[4],
				"m_defense": entry[5],
				"xp": struct.unpack_from('<H', entry, 6)[0],
				"gold": struct.unpack_from('<H', entry, 8)[0]
			}
			monsters.append(monster)

		# Build output JSON
		output = {
			"format_version": "1.0",
			"source_file": "monsters.dwdata",
			"crc32": f"{reader.header['crc32']:08X}",
			"rom_offset": f"0x{reader.header['rom_offset']:04X}",
			"description": "Monster stats for 39 enemies in Dragon Warrior",
			"monsters": monsters
		}

		# Write JSON
		output_path = os.path.join(self.json_dir, 'monsters.json')
		os.makedirs(self.json_dir, exist_ok=True)

		with open(output_path, 'w') as f:
			json.dump(output, f, indent=2)

		print(f"  ✓ Transformed {len(monsters)} monsters")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def transform_spells(self) -> bool:
		"""
		Transform spells.dwdata → spells.json

		Returns:
			True if successful
		"""
		print("\n--- Transforming Spell Data ---")

		# Load binary file
		reader = BinaryReader(os.path.join(self.binary_dir, 'spells.dwdata'))
		if not reader.load():
			return False

		data = reader.get_data_section()

		# Parse spells
		spells = []
		for i in range(10):
			offset = i * 8
			entry = data[offset:offset + 8]

			spell = {
				"id": i,
				"name": SPELL_NAMES[i],
				"mp_cost": entry[0],
				"power": entry[1],
				"effect_type": entry[2],
				"range": entry[3],
				"animation": entry[4]
			}
			spells.append(spell)

		# Build output JSON
		output = {
			"format_version": "1.0",
			"source_file": "spells.dwdata",
			"crc32": f"{reader.header['crc32']:08X}",
			"rom_offset": f"0x{reader.header['rom_offset']:04X}",
			"description": "Spell data for 10 spells in Dragon Warrior",
			"effect_types": {
				"0": "Damage",
				"1": "Heal",
				"2": "Status",
				"3": "Field",
				"4": "Utility"
			},
			"range_types": {
				"0": "Self",
				"1": "Enemy",
				"2": "All",
				"3": "Radius"
			},
			"spells": spells
		}

		# Write JSON
		output_path = os.path.join(self.json_dir, 'spells.json')
		os.makedirs(self.json_dir, exist_ok=True)

		with open(output_path, 'w') as f:
			json.dump(output, f, indent=2)

		print(f"  ✓ Transformed {len(spells)} spells")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def transform_items(self) -> bool:
		"""
		Transform items.dwdata → items.json

		Returns:
			True if successful
		"""
		print("\n--- Transforming Item Data ---")

		# Load binary file
		reader = BinaryReader(os.path.join(self.binary_dir, 'items.dwdata'))
		if not reader.load():
			return False

		data = reader.get_data_section()

		# Parse items
		items = []
		for i in range(32):
			offset = i * 8
			entry = data[offset:offset + 8]

			# Parse values
			buy_price = struct.unpack_from('<H', entry, 0)[0]
			sell_price = struct.unpack_from('<H', entry, 2)[0]
			attack_bonus = struct.unpack_from('<b', entry, 4)[0]  # signed
			defense_bonus = struct.unpack_from('<b', entry, 5)[0]  # signed
			item_type = entry[6]
			flags = entry[7]

			item = {
				"id": i,
				"name": ITEM_NAMES[i],
				"buy_price": buy_price,
				"sell_price": sell_price,
				"attack_power": attack_bonus,  # Field renamed from attack_bonus for accuracy
				"defense_bonus": defense_bonus,
				"type": item_type,
				"flags": {
					"equippable": bool(flags & 0x01),
					"cursed": bool(flags & 0x02),
					"important": bool(flags & 0x04),
					"quest_item": bool(flags & 0x08)
				}
			}
			items.append(item)

		# Build output JSON
		output = {
			"format_version": "1.0",
			"source_file": "items.dwdata",
			"crc32": f"{reader.header['crc32']:08X}",
			"rom_offset": f"0x{reader.header['rom_offset']:04X}",
			"description": "Item and equipment data for 32 items in Dragon Warrior",
			"item_types": {
				"0": "Tool",
				"1": "Weapon",
				"2": "Armor",
				"3": "Shield",
				"4": "Key Item"
			},
			"items": items
		}

		# Write JSON
		output_path = os.path.join(self.json_dir, 'items.json')
		os.makedirs(self.json_dir, exist_ok=True)

		with open(output_path, 'w') as f:
			json.dump(output, f, indent=2)

		print(f"  ✓ Transformed {len(items)} items")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def transform_graphics(self) -> bool:
		"""
		Transform graphics.dwdata → CHR tiles PNG + JSON

		Returns:
			True if successful
		"""
		print("\n--- Transforming Graphics Data ---")

		if Image is None:
			print("  ⚠ PIL not available, skipping graphics export")
			return False

		# Load binary file
		reader = BinaryReader(os.path.join(self.binary_dir, 'graphics.dwdata'))
		if not reader.load():
			return False

		data = reader.get_data_section()

		# Decode CHR tiles
		tiles = []
		tile_count = len(data) // 16

		for i in range(tile_count):
			offset = i * 16
			tile_data = data[offset:offset + 16]

			# Decode 2bpp NES tile
			tile_pixels = self._decode_chr_tile(tile_data)
			tiles.append(tile_pixels)

		# Create tile sheet image (32 tiles wide)
		tiles_wide = 32
		tiles_high = (tile_count + tiles_wide - 1) // tiles_wide

		img_width = tiles_wide * 8
		img_height = tiles_high * 8

		img = Image.new('RGB', (img_width, img_height))

		for tile_idx, tile_pixels in enumerate(tiles):
			tile_x = (tile_idx % tiles_wide) * 8
			tile_y = (tile_idx // tiles_wide) * 8

			for y in range(8):
				for x in range(8):
					pixel_value = tile_pixels[y * 8 + x]
					# Use grayscale for now (0=black, 1=dark, 2=light, 3=white)
					color_value = pixel_value * 85  # 0, 85, 170, 255
					color = (color_value, color_value, color_value)
					img.putpixel((tile_x + x, tile_y + y), color)

		# Save PNG
		output_path = os.path.join(self.graphics_dir, 'chr_tiles.png')
		os.makedirs(self.graphics_dir, exist_ok=True)
		img.save(output_path)

		# Save metadata JSON
		metadata = {
			"format_version": "1.0",
			"source_file": "graphics.dwdata",
			"crc32": f"{reader.header['crc32']:08X}",
			"rom_offset": f"0x{reader.header['rom_offset']:04X}",
			"tile_count": tile_count,
			"image_width": img_width,
			"image_height": img_height,
			"tiles_per_row": tiles_wide,
			"description": "CHR-ROM tiles (1024 tiles, 8x8 each, 2bpp NES format)"
		}

		metadata_path = os.path.join(self.graphics_dir, 'chr_tiles.json')
		with open(metadata_path, 'w') as f:
			json.dump(metadata, f, indent=2)

		print(f"  ✓ Decoded {tile_count} CHR tiles")
		print(f"  ✓ Wrote: {output_path}")
		print(f"  ✓ Wrote: {metadata_path}")

		return True

	def _decode_chr_tile(self, tile_data: bytes) -> List[int]:
		"""
		Decode NES 2bpp CHR tile to pixel values

		Args:
			tile_data: 16 bytes (8 low + 8 high bitplanes)

		Returns:
			List of 64 pixel values (0-3)
		"""
		pixels = []

		for y in range(8):
			low_byte = tile_data[y]
			high_byte = tile_data[y + 8]

			for x in range(7, -1, -1):  # MSB first
				low_bit = (low_byte >> x) & 1
				high_bit = (high_byte >> x) & 1
				pixel_value = (high_bit << 1) | low_bit
				pixels.append(pixel_value)

		return pixels

	def transform_all(self) -> Dict[str, bool]:
		"""
		Transform all .dwdata files to JSON/PNG

		Returns:
			Dict mapping filenames to success status
		"""
		results = {}

		results['monsters.json'] = self.transform_monsters()
		results['spells.json'] = self.transform_spells()
		results['items.json'] = self.transform_items()
		results['chr_tiles.png'] = self.transform_graphics()

		return results


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Transform .dwdata binary to JSON/PNG editable assets',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python binary_to_assets.py
  python binary_to_assets.py --binary-dir custom/binary/
  python binary_to_assets.py --output-dir custom/output/
		"""
	)

	parser.add_argument(
		'--binary-dir',
		default=DEFAULT_BINARY_DIR,
		help=f'Directory with .dwdata files (default: {DEFAULT_BINARY_DIR})'
	)

	parser.add_argument(
		'--json-dir',
		default=DEFAULT_JSON_DIR,
		help=f'Output directory for JSON (default: {DEFAULT_JSON_DIR})'
	)

	parser.add_argument(
		'--graphics-dir',
		default=DEFAULT_GRAPHICS_DIR,
		help=f'Output directory for PNG (default: {DEFAULT_GRAPHICS_DIR})'
	)

	args = parser.parse_args()

	print("=" * 60)
	print("Binary → JSON/PNG Transformation")
	print("=" * 60)

	transformer = AssetTransformer(args.binary_dir, args.json_dir, args.graphics_dir)
	results = transformer.transform_all()

	# Summary
	print("\n" + "=" * 60)
	print("Transformation Summary")
	print("=" * 60)

	success_count = sum(1 for v in results.values() if v)
	total_count = len(results)

	for filename, success in results.items():
		status = "✓" if success else "✗"
		print(f"  {status} {filename}")

	print(f"\nCompleted: {success_count}/{total_count} files")

	if success_count == total_count:
		print("\n✅ All transformations successful!")
		print(f"\nNext step: Edit JSON/PNG files, then run:")
		print(f"  python tools/assets_to_binary.py")
		return 0
	else:
		print("\n⚠ Some transformations skipped or failed")
		return 1


if __name__ == '__main__':
	sys.exit(main())
