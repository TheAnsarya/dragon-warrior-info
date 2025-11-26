#!/usr/bin/env python3
"""
Package Editable Assets to Binary Intermediate Format

This script packages edited JSON/PNG assets back to .dwdata binary format.

Pipeline: ROM → .dwdata → JSON/PNG → .dwdata (this script) → ROM

Usage:
	python assets_to_binary.py
	python assets_to_binary.py --json-dir custom/json/
	python assets_to_binary.py --output-dir custom/binary/

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import struct
import zlib
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse

try:
	from PIL import Image
except ImportError:
	print("WARNING: PIL not available, graphics import disabled")
	Image = None

# Constants
MAGIC = b'DWDT'
VERSION_MAJOR = 1
VERSION_MINOR = 0

# Data type IDs
TYPE_MONSTER = 0x01
TYPE_SPELL = 0x02
TYPE_ITEM = 0x03
TYPE_MAP = 0x04
TYPE_TEXT = 0x05
TYPE_GRAPHICS = 0x06

# ROM offsets (from original extraction)
MONSTER_OFFSET = 0x5E5B
SPELL_OFFSET = 0x5F3B
ITEM_OFFSET = 0x5F83
CHR_OFFSET = 0x10010

# Default paths
DEFAULT_JSON_DIR = "extracted_assets/json"
DEFAULT_GRAPHICS_DIR = "extracted_assets/graphics"
DEFAULT_OUTPUT_DIR = "extracted_assets/binary"


class ValidationError(Exception):
	"""Raised when asset validation fails"""
	pass


class AssetValidator:
	"""Validate JSON/PNG assets before packaging"""

	@staticmethod
	def validate_monsters(monsters: List[Dict]) -> None:
		"""
		Validate monster data

		Args:
			monsters: List of monster dicts

		Raises:
			ValidationError: If validation fails
		"""
		if len(monsters) != 39:
			raise ValidationError(f"Must have 39 monsters, got {len(monsters)}")

		for i, monster in enumerate(monsters):
			# Required fields
			required = ['id', 'name', 'attack', 'defense', 'hp', 'spell', 'agility', 'm_defense', 'xp', 'gold']
			for field in required:
				if field not in monster:
					raise ValidationError(f"Monster {i}: Missing field '{field}'")

			# Validate ID
			if monster['id'] != i:
				raise ValidationError(f"Monster {i}: ID mismatch (expected {i}, got {monster['id']})")

			# Validate HP (must be 1-255)
			if not (1 <= monster['hp'] <= 255):
				raise ValidationError(f"Monster {i} ({monster['name']}): HP must be 1-255, got {monster['hp']}")

			# Validate stats (0-255)
			for stat in ['attack', 'defense', 'agility', 'm_defense']:
				value = monster[stat]
				if not (0 <= value <= 255):
					raise ValidationError(f"Monster {i}: {stat} must be 0-255, got {value}")

			# Validate spell ID (0-9)
			if not (0 <= monster['spell'] <= 9):
				raise ValidationError(f"Monster {i}: spell must be 0-9, got {monster['spell']}")

			# Validate XP and Gold (0-65535)
			for stat in ['xp', 'gold']:
				value = monster[stat]
				if not (0 <= value <= 65535):
					raise ValidationError(f"Monster {i}: {stat} must be 0-65535, got {value}")

	@staticmethod
	def validate_spells(spells: List[Dict]) -> None:
		"""
		Validate spell data

		Args:
			spells: List of spell dicts

		Raises:
			ValidationError: If validation fails
		"""
		if len(spells) != 10:
			raise ValidationError(f"Must have 10 spells, got {len(spells)}")

		for i, spell in enumerate(spells):
			# Required fields
			required = ['id', 'name', 'mp_cost', 'power', 'effect_type', 'range', 'animation']
			for field in required:
				if field not in spell:
					raise ValidationError(f"Spell {i}: Missing field '{field}'")

			# Validate ID
			if spell['id'] != i:
				raise ValidationError(f"Spell {i}: ID mismatch")

			# Validate ranges
			for field, max_val in [('mp_cost', 255), ('power', 255), ('effect_type', 15), ('range', 15), ('animation', 15)]:
				value = spell[field]
				if not (0 <= value <= max_val):
					raise ValidationError(f"Spell {i}: {field} must be 0-{max_val}, got {value}")

	@staticmethod
	def validate_items(items: List[Dict]) -> None:
		"""
		Validate item data

		Args:
			items: List of item dicts

		Raises:
			ValidationError: If validation fails
		"""
		if len(items) != 32:
			raise ValidationError(f"Must have 32 items, got {len(items)}")

		for i, item in enumerate(items):
			# Required fields
			required = ['id', 'name', 'buy_price', 'sell_price', 'attack_bonus', 'defense_bonus', 'type', 'flags']
			for field in required:
				if field not in item:
					raise ValidationError(f"Item {i}: Missing field '{field}'")

			# Validate ID
			if item['id'] != i:
				raise ValidationError(f"Item {i}: ID mismatch")

			# Validate prices (0-65535)
			for field in ['buy_price', 'sell_price']:
				value = item[field]
				if not (0 <= value <= 65535):
					raise ValidationError(f"Item {i}: {field} must be 0-65535, got {value}")

			# Validate bonuses (-128 to 127)
			for field in ['attack_bonus', 'defense_bonus']:
				value = item[field]
				if not (-128 <= value <= 127):
					raise ValidationError(f"Item {i}: {field} must be -128 to 127, got {value}")

			# Validate type (0-15)
			if not (0 <= item['type'] <= 15):
				raise ValidationError(f"Item {i}: type must be 0-15, got {item['type']}")

			# Validate flags structure
			if not isinstance(item['flags'], dict):
				raise ValidationError(f"Item {i}: flags must be a dict")


class BinaryPackager:
	"""Package JSON/PNG assets to .dwdata binary files"""

	def __init__(self, json_dir: str, graphics_dir: str, output_dir: str):
		"""
		Initialize packager

		Args:
			json_dir: Directory with JSON files
			graphics_dir: Directory with PNG files
			output_dir: Output directory for .dwdata files
		"""
		self.json_dir = json_dir
		self.graphics_dir = graphics_dir
		self.output_dir = output_dir
		self.validator = AssetValidator()

	def build_header(
		self,
		data_type: int,
		data_size: int,
		rom_offset: int,
		data: bytes
	) -> bytes:
		"""
		Build 32-byte .dwdata header

		Args:
			data_type: Data type ID
			data_size: Size of data section
			rom_offset: Original ROM offset
			data: Data section for CRC32

		Returns:
			32-byte header
		"""
		header = bytearray(32)

		header[0:4] = MAGIC
		header[4] = VERSION_MAJOR
		header[5] = VERSION_MINOR
		header[6] = data_type
		header[7] = 0x00

		struct.pack_into('<I', header, 0x08, data_size)
		struct.pack_into('<I', header, 0x0C, rom_offset)

		crc = zlib.crc32(data) & 0xFFFFFFFF
		struct.pack_into('<I', header, 0x10, crc)

		timestamp = int(time.time())
		struct.pack_into('<I', header, 0x14, timestamp)

		header[0x18:0x20] = b'\x00' * 8

		return bytes(header)

	def package_monsters(self) -> bool:
		"""
		Package monsters.json → monsters.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Packaging Monster Data ---")

		# Load JSON
		json_path = os.path.join(self.json_dir, 'monsters.json')

		if not os.path.exists(json_path):
			print(f"  ❌ File not found: {json_path}")
			return False

		with open(json_path, 'r') as f:
			data = json.load(f)

		monsters = data['monsters']

		# Validate
		try:
			self.validator.validate_monsters(monsters)
			print(f"  ✓ Validated {len(monsters)} monsters")
		except ValidationError as e:
			print(f"  ❌ Validation failed: {e}")
			return False

		# Build binary data
		binary_data = bytearray(39 * 16)

		for monster in monsters:
			offset = monster['id'] * 16

			binary_data[offset + 0] = monster['attack']
			binary_data[offset + 1] = monster['defense']
			binary_data[offset + 2] = monster['hp']
			binary_data[offset + 3] = monster['spell']
			binary_data[offset + 4] = monster['agility']
			binary_data[offset + 5] = monster['m_defense']

			struct.pack_into('<H', binary_data, offset + 6, monster['xp'])
			struct.pack_into('<H', binary_data, offset + 8, monster['gold'])

			# Bytes 10-15 remain 0x00 (unused)

		# Build header and write file
		header = self.build_header(TYPE_MONSTER, len(binary_data), MONSTER_OFFSET, binary_data)

		output_path = os.path.join(self.output_dir, 'monsters.dwdata')
		os.makedirs(self.output_dir, exist_ok=True)

		with open(output_path, 'wb') as f:
			f.write(header)
			f.write(binary_data)

		crc = struct.unpack_from('<I', header, 0x10)[0]
		print(f"  ✓ Packaged {len(monsters)} monsters")
		print(f"  ✓ CRC32: {crc:08X}")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def package_spells(self) -> bool:
		"""
		Package spells.json → spells.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Packaging Spell Data ---")

		# Load JSON
		json_path = os.path.join(self.json_dir, 'spells.json')

		if not os.path.exists(json_path):
			print(f"  ❌ File not found: {json_path}")
			return False

		with open(json_path, 'r') as f:
			data = json.load(f)

		spells = data['spells']

		# Validate
		try:
			self.validator.validate_spells(spells)
			print(f"  ✓ Validated {len(spells)} spells")
		except ValidationError as e:
			print(f"  ❌ Validation failed: {e}")
			return False

		# Build binary data
		binary_data = bytearray(10 * 8)

		for spell in spells:
			offset = spell['id'] * 8

			binary_data[offset + 0] = spell['mp_cost']
			binary_data[offset + 1] = spell['power']
			binary_data[offset + 2] = spell['effect_type']
			binary_data[offset + 3] = spell['range']
			binary_data[offset + 4] = spell['animation']
			binary_data[offset + 5] = 0x00  # Reserved
			binary_data[offset + 6] = 0x00  # Reserved
			binary_data[offset + 7] = 0x00  # Reserved

		# Build header and write file
		header = self.build_header(TYPE_SPELL, len(binary_data), SPELL_OFFSET, binary_data)

		output_path = os.path.join(self.output_dir, 'spells.dwdata')
		os.makedirs(self.output_dir, exist_ok=True)

		with open(output_path, 'wb') as f:
			f.write(header)
			f.write(binary_data)

		crc = struct.unpack_from('<I', header, 0x10)[0]
		print(f"  ✓ Packaged {len(spells)} spells")
		print(f"  ✓ CRC32: {crc:08X}")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def package_items(self) -> bool:
		"""
		Package items.json → items.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Packaging Item Data ---")

		# Load JSON
		json_path = os.path.join(self.json_dir, 'items.json')

		if not os.path.exists(json_path):
			print(f"  ❌ File not found: {json_path}")
			return False

		with open(json_path, 'r') as f:
			data = json.load(f)

		items = data['items']

		# Validate
		try:
			self.validator.validate_items(items)
			print(f"  ✓ Validated {len(items)} items")
		except ValidationError as e:
			print(f"  ❌ Validation failed: {e}")
			return False

		# Build binary data
		binary_data = bytearray(32 * 8)

		for item in items:
			offset = item['id'] * 8

			struct.pack_into('<H', binary_data, offset + 0, item['buy_price'])
			struct.pack_into('<H', binary_data, offset + 2, item['sell_price'])
			struct.pack_into('<b', binary_data, offset + 4, item['attack_bonus'])
			struct.pack_into('<b', binary_data, offset + 5, item['defense_bonus'])

			binary_data[offset + 6] = item['type']

			# Pack flags bitfield
			flags = 0
			if item['flags'].get('equippable', False):
				flags |= 0x01
			if item['flags'].get('cursed', False):
				flags |= 0x02
			if item['flags'].get('important', False):
				flags |= 0x04
			if item['flags'].get('quest_item', False):
				flags |= 0x08

			binary_data[offset + 7] = flags

		# Build header and write file
		header = self.build_header(TYPE_ITEM, len(binary_data), ITEM_OFFSET, binary_data)

		output_path = os.path.join(self.output_dir, 'items.dwdata')
		os.makedirs(self.output_dir, exist_ok=True)

		with open(output_path, 'wb') as f:
			f.write(header)
			f.write(binary_data)

		crc = struct.unpack_from('<I', header, 0x10)[0]
		print(f"  ✓ Packaged {len(items)} items")
		print(f"  ✓ CRC32: {crc:08X}")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def package_graphics(self) -> bool:
		"""
		Package chr_tiles.png → graphics.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Packaging Graphics Data ---")

		if Image is None:
			print("  ⚠ PIL not available, skipping graphics packaging")
			return False

		# Load PNG
		png_path = os.path.join(self.graphics_dir, 'chr_tiles.png')

		if not os.path.exists(png_path):
			print(f"  ⚠ File not found: {png_path}")
			return False

		img = Image.open(png_path)

		# Validate dimensions (must be 256x256 for 1024 tiles)
		width, height = img.size
		tiles_wide = width // 8
		tiles_high = height // 8
		tile_count = tiles_wide * tiles_high

		if tile_count != 1024:
			print(f"  ⚠ Expected 1024 tiles, got {tile_count}")
			print(f"    Image size: {width}x{height}")
			print(f"    Skipping graphics packaging")
			return False

		# Encode tiles to NES 2bpp format
		binary_data = bytearray(1024 * 16)

		for tile_idx in range(1024):
			tile_x = (tile_idx % tiles_wide) * 8
			tile_y = (tile_idx // tiles_wide) * 8

			# Extract 8x8 pixels
			pixels = []
			for y in range(8):
				for x in range(8):
					pixel = img.getpixel((tile_x + x, tile_y + y))

					# Convert to grayscale if RGB
					if isinstance(pixel, tuple):
						gray = (pixel[0] + pixel[1] + pixel[2]) // 3
					else:
						gray = pixel

					# Map to 2-bit value (0-3)
					value = gray // 64  # 0-255 → 0-3
					pixels.append(value)

			# Encode to 2bpp
			tile_data = self._encode_chr_tile(pixels)

			# Write to binary
			offset = tile_idx * 16
			binary_data[offset:offset + 16] = tile_data

		# Build header and write file
		header = self.build_header(TYPE_GRAPHICS, len(binary_data), CHR_OFFSET, binary_data)

		output_path = os.path.join(self.output_dir, 'graphics.dwdata')
		os.makedirs(self.output_dir, exist_ok=True)

		with open(output_path, 'wb') as f:
			f.write(header)
			f.write(binary_data)

		crc = struct.unpack_from('<I', header, 0x10)[0]
		print(f"  ✓ Encoded {tile_count} CHR tiles")
		print(f"  ✓ CRC32: {crc:08X}")
		print(f"  ✓ Wrote: {output_path}")

		return True

	def _encode_chr_tile(self, pixels: List[int]) -> bytes:
		"""
		Encode 64 pixels to NES 2bpp CHR tile

		Args:
			pixels: List of 64 pixel values (0-3)

		Returns:
			16 bytes (8 low + 8 high bitplanes)
		"""
		tile_data = bytearray(16)

		for y in range(8):
			low_byte = 0
			high_byte = 0

			for x in range(8):
				pixel_idx = y * 8 + x
				pixel_value = pixels[pixel_idx]

				low_bit = pixel_value & 1
				high_bit = (pixel_value >> 1) & 1

				low_byte |= (low_bit << (7 - x))
				high_byte |= (high_bit << (7 - x))

			tile_data[y] = low_byte
			tile_data[y + 8] = high_byte

		return bytes(tile_data)

	def package_all(self) -> Dict[str, bool]:
		"""
		Package all JSON/PNG files to .dwdata

		Returns:
			Dict mapping filenames to success status
		"""
		results = {}

		results['monsters.dwdata'] = self.package_monsters()
		results['spells.dwdata'] = self.package_spells()
		results['items.dwdata'] = self.package_items()
		results['graphics.dwdata'] = self.package_graphics()

		return results


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Package JSON/PNG assets to .dwdata binary format',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python assets_to_binary.py
  python assets_to_binary.py --json-dir custom/json/
  python assets_to_binary.py --output-dir custom/binary/
		"""
	)

	parser.add_argument(
		'--json-dir',
		default=DEFAULT_JSON_DIR,
		help=f'Directory with JSON files (default: {DEFAULT_JSON_DIR})'
	)

	parser.add_argument(
		'--graphics-dir',
		default=DEFAULT_GRAPHICS_DIR,
		help=f'Directory with PNG files (default: {DEFAULT_GRAPHICS_DIR})'
	)

	parser.add_argument(
		'--output-dir',
		default=DEFAULT_OUTPUT_DIR,
		help=f'Output directory for .dwdata (default: {DEFAULT_OUTPUT_DIR})'
	)

	args = parser.parse_args()

	print("=" * 60)
	print("JSON/PNG → Binary Packaging")
	print("=" * 60)

	packager = BinaryPackager(args.json_dir, args.graphics_dir, args.output_dir)
	results = packager.package_all()

	# Summary
	print("\n" + "=" * 60)
	print("Packaging Summary")
	print("=" * 60)

	success_count = sum(1 for v in results.values() if v)
	total_count = len(results)

	for filename, success in results.items():
		status = "✓" if success else "✗"
		print(f"  {status} {filename}")

	print(f"\nCompleted: {success_count}/{total_count} files")

	if success_count == total_count:
		print("\n✅ All packaging successful!")
		print(f"\nNext step: python tools/binary_to_rom.py")
		return 0
	else:
		print("\n⚠ Some packages skipped or failed")
		return 1


if __name__ == '__main__':
	sys.exit(main())
