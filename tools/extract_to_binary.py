#!/usr/bin/env python3
"""
Extract ROM Data to Binary Intermediate Format (.dwdata)

This script extracts data from Dragon Warrior (NES) ROM and converts it to
.dwdata binary intermediate format for the build pipeline.

Pipeline: ROM → .dwdata (this script) → JSON/PNG → .dwdata → ROM

Usage:
	python extract_to_binary.py
	python extract_to_binary.py --rom path/to/rom.nes
	python extract_to_binary.py --output-dir custom/output/

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import struct
import zlib
import time
from pathlib import Path
from typing import Dict, Tuple
import argparse

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

# ROM offsets (Dragon Warrior U PRG1)
MONSTER_OFFSET = 0x5e5b
MONSTER_SIZE = 39 * 16  # 39 monsters, 16 bytes each

SPELL_OFFSET = 0x5f3b
SPELL_SIZE = 10 * 8  # 10 spells, 8 bytes each

ITEM_OFFSET = 0x5f83
ITEM_SIZE = 32 * 8  # 32 items, 8 bytes each

CHR_OFFSET = 0x10010
CHR_SIZE = 0x4000  # 16KB CHR-ROM (1024 tiles)

# Default paths
DEFAULT_ROM = "roms/Dragon Warrior (U) (PRG1) [!].nes"
DEFAULT_OUTPUT_DIR = "extracted_assets/binary"


class DWDataBuilder:
	"""Build .dwdata binary files with proper headers and checksums"""

	def __init__(self):
		self.header = bytearray(32)

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
			data_type: Data type ID (0x01-0x06)
			data_size: Size of data section in bytes
			rom_offset: Original ROM offset
			data: Data section for CRC32 calculation

		Returns:
			32-byte header as bytes
		"""
		header = bytearray(32)

		# Magic number
		header[0:4] = MAGIC

		# Version
		header[4] = VERSION_MAJOR
		header[5] = VERSION_MINOR

		# Data type
		header[6] = data_type

		# Flags (reserved)
		header[7] = 0x00

		# Data size (little-endian)
		struct.pack_into('<I', header, 0x08, data_size)

		# ROM offset (little-endian)
		struct.pack_into('<I', header, 0x0c, rom_offset)

		# CRC32 checksum
		crc = zlib.crc32(data) & 0xffffffff
		struct.pack_into('<I', header, 0x10, crc)

		# Timestamp
		timestamp = int(time.time())
		struct.pack_into('<I', header, 0x14, timestamp)

		# Reserved bytes (8 bytes of 0x00)
		header[0x18:0x20] = b'\x00' * 8

		return bytes(header)

	def write_dwdata_file(
		self,
		output_path: str,
		data_type: int,
		rom_offset: int,
		data: bytes
	) -> Tuple[int, str]:
		"""
		Write complete .dwdata file

		Args:
			output_path: Path for output file
			data_type: Data type ID
			rom_offset: Original ROM offset
			data: Data section

		Returns:
			Tuple of (CRC32 checksum, hex string)
		"""
		# Build header
		header = self.build_header(data_type, len(data), rom_offset, data)

		# Write file
		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		with open(output_path, 'wb') as f:
			f.write(header)
			f.write(data)

		# Return checksum
		crc = struct.unpack_from('<I', header, 0x10)[0]
		return crc, f"{crc:08X}"


class ROMExtractor:
	"""Extract data from Dragon Warrior ROM"""

	def __init__(self, rom_path: str):
		"""
		Initialize extractor with ROM file

		Args:
			rom_path: Path to Dragon Warrior ROM
		"""
		self.rom_path = rom_path
		self.rom_data = None
		self.builder = DWDataBuilder()

	def load_rom(self) -> bool:
		"""
		Load and validate ROM file

		Returns:
			True if valid ROM loaded
		"""
		if not os.path.exists(self.rom_path):
			print(f"❌ ERROR: ROM file not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		# Validate ROM
		if len(self.rom_data) != 81936:
			print(f"❌ ERROR: Invalid ROM size: {len(self.rom_data)} (expected 81936)")
			return False

		if self.rom_data[0:4] != b'NES\x1A':
			print(f"❌ ERROR: Invalid NES header")
			return False

		print(f"✓ Loaded ROM: {self.rom_path}")
		print(f"  Size: {len(self.rom_data)} bytes")
		return True

	def extract_monsters(self, output_path: str) -> bool:
		"""
		Extract monster data to monsters.dwdata

		Args:
			output_path: Path for monsters.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Extracting Monster Data ---")

		# Extract data from ROM
		data = self.rom_data[MONSTER_OFFSET:MONSTER_OFFSET + MONSTER_SIZE]

		print(f"  ROM Offset: 0x{MONSTER_OFFSET:04X}")
		print(f"  Data Size: {len(data)} bytes ({len(data)//16} monsters)")

		# Write .dwdata file
		crc, crc_hex = self.builder.write_dwdata_file(
			output_path,
			TYPE_MONSTER,
			MONSTER_OFFSET,
			data
		)

		print(f"  CRC32: {crc_hex}")
		print(f"✓ Wrote: {output_path}")

		return True

	def extract_spells(self, output_path: str) -> bool:
		"""
		Extract spell data to spells.dwdata

		Args:
			output_path: Path for spells.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Extracting Spell Data ---")

		# Extract data from ROM
		data = self.rom_data[SPELL_OFFSET:SPELL_OFFSET + SPELL_SIZE]

		print(f"  ROM Offset: 0x{SPELL_OFFSET:04X}")
		print(f"  Data Size: {len(data)} bytes ({len(data)//8} spells)")

		# Write .dwdata file
		crc, crc_hex = self.builder.write_dwdata_file(
			output_path,
			TYPE_SPELL,
			SPELL_OFFSET,
			data
		)

		print(f"  CRC32: {crc_hex}")
		print(f"✓ Wrote: {output_path}")

		return True

	def extract_items(self, output_path: str) -> bool:
		"""
		Extract item data to items.dwdata

		Args:
			output_path: Path for items.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Extracting Item Data ---")

		# Extract data from ROM
		data = self.rom_data[ITEM_OFFSET:ITEM_OFFSET + ITEM_SIZE]

		print(f"  ROM Offset: 0x{ITEM_OFFSET:04X}")
		print(f"  Data Size: {len(data)} bytes ({len(data)//8} items)")

		# Write .dwdata file
		crc, crc_hex = self.builder.write_dwdata_file(
			output_path,
			TYPE_ITEM,
			ITEM_OFFSET,
			data
		)

		print(f"  CRC32: {crc_hex}")
		print(f"✓ Wrote: {output_path}")

		return True

	def extract_graphics(self, output_path: str) -> bool:
		"""
		Extract CHR-ROM graphics to graphics.dwdata

		Args:
			output_path: Path for graphics.dwdata

		Returns:
			True if successful
		"""
		print("\n--- Extracting Graphics Data ---")

		# Extract CHR-ROM data
		data = self.rom_data[CHR_OFFSET:CHR_OFFSET + CHR_SIZE]

		print(f"  ROM Offset: 0x{CHR_OFFSET:04X}")
		print(f"  Data Size: {len(data)} bytes ({len(data)//16} tiles)")

		# Write .dwdata file
		crc, crc_hex = self.builder.write_dwdata_file(
			output_path,
			TYPE_GRAPHICS,
			CHR_OFFSET,
			data
		)

		print(f"  CRC32: {crc_hex}")
		print(f"✓ Wrote: {output_path}")

		return True

	def extract_all(self, output_dir: str) -> Dict[str, bool]:
		"""
		Extract all data types to output directory

		Args:
			output_dir: Base directory for output files

		Returns:
			Dict mapping filenames to success status
		"""
		results = {}

		# Ensure output directory exists
		os.makedirs(output_dir, exist_ok=True)

		# Extract each data type
		results['monsters.dwdata'] = self.extract_monsters(
			os.path.join(output_dir, 'monsters.dwdata')
		)

		results['spells.dwdata'] = self.extract_spells(
			os.path.join(output_dir, 'spells.dwdata')
		)

		results['items.dwdata'] = self.extract_items(
			os.path.join(output_dir, 'items.dwdata')
		)

		results['graphics.dwdata'] = self.extract_graphics(
			os.path.join(output_dir, 'graphics.dwdata')
		)

		return results


def verify_dwdata_file(path: str) -> bool:
	"""
	Verify .dwdata file integrity

	Args:
		path: Path to .dwdata file

	Returns:
		True if file is valid
	"""
	try:
		with open(path, 'rb') as f:
			data = f.read()

		# Check minimum size
		if len(data) < 32:
			print(f"  ❌ File too small: {len(data)} bytes")
			return False

		# Check magic
		if data[0:4] != MAGIC:
			print(f"  ❌ Invalid magic: {data[0:4]}")
			return False

		# Check version
		if data[4] != VERSION_MAJOR or data[5] != VERSION_MINOR:
			print(f"  ❌ Version mismatch: {data[4]}.{data[5]}")
			return False

		# Get sizes
		data_size = struct.unpack_from('<I', data, 0x08)[0]
		stored_crc = struct.unpack_from('<I', data, 0x10)[0]

		# Verify file size
		if len(data) != 32 + data_size:
			print(f"  ❌ Size mismatch: {len(data)} != {32 + data_size}")
			return False

		# Verify checksum
		actual_data = data[32:32 + data_size]
		calc_crc = zlib.crc32(actual_data) & 0xffffffff

		if calc_crc != stored_crc:
			print(f"  ❌ CRC mismatch: {calc_crc:08X} != {stored_crc:08X}")
			return False

		print(f"  ✓ Valid: CRC32 {calc_crc:08X}")
		return True

	except Exception as e:
		print(f"  ❌ Error: {e}")
		return False


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Extract Dragon Warrior ROM data to .dwdata binary format',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python extract_to_binary.py
  python extract_to_binary.py --rom custom_rom.nes
  python extract_to_binary.py --output-dir custom/output/
  python extract_to_binary.py --verify
		"""
	)

	parser.add_argument(
		'--rom',
		default=DEFAULT_ROM,
		help=f'Path to Dragon Warrior ROM (default: {DEFAULT_ROM})'
	)

	parser.add_argument(
		'--output-dir',
		default=DEFAULT_OUTPUT_DIR,
		help=f'Output directory for .dwdata files (default: {DEFAULT_OUTPUT_DIR})'
	)

	parser.add_argument(
		'--verify',
		action='store_true',
		help='Verify existing .dwdata files instead of extracting'
	)

	args = parser.parse_args()

	print("=" * 60)
	print("Dragon Warrior ROM → Binary Extraction")
	print("=" * 60)

	# Verify mode
	if args.verify:
		print("\n--- Verification Mode ---")
		files = [
			'monsters.dwdata',
			'spells.dwdata',
			'items.dwdata',
			'graphics.dwdata'
		]

		all_valid = True
		for filename in files:
			path = os.path.join(args.output_dir, filename)
			print(f"\nVerifying: {filename}")
			if os.path.exists(path):
				valid = verify_dwdata_file(path)
				all_valid = all_valid and valid
			else:
				print(f"  ❌ File not found")
				all_valid = False

		print("\n" + "=" * 60)
		if all_valid:
			print("✅ All files valid")
			return 0
		else:
			print("❌ Some files invalid or missing")
			return 1

	# Extraction mode
	extractor = ROMExtractor(args.rom)

	if not extractor.load_rom():
		return 1

	results = extractor.extract_all(args.output_dir)

	# Summary
	print("\n" + "=" * 60)
	print("Extraction Summary")
	print("=" * 60)

	success_count = sum(1 for v in results.values() if v)
	total_count = len(results)

	for filename, success in results.items():
		status = "✓" if success else "✗"
		print(f"  {status} {filename}")

	print(f"\nCompleted: {success_count}/{total_count} files")

	if success_count == total_count:
		print("\n✅ All extractions successful!")
		print(f"\nNext step: python tools/binary_to_assets.py")
		return 0
	else:
		print("\n❌ Some extractions failed")
		return 1


if __name__ == '__main__':
	sys.exit(main())
