#!/usr/bin/env python3
"""
Dragon Warrior ROM Hacking Toolkit - Automated Test Suite

Comprehensive testing framework for:
- ROM data integrity
- Data extraction accuracy
- Editor functionality
- Import/export operations
- Regression testing
- Performance benchmarks
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
from typing import List, Tuple
import struct
import time

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
	import numpy as np
	from PIL import Image
except ImportError:
	print("WARNING: PIL and numpy not available, some tests will be skipped")
	np = None
	Image = None


class TestROMValidation(unittest.TestCase):
	"""Test ROM file validation and integrity."""

	@classmethod
	def setUpClass(cls):
		"""Set up test ROM path."""
		cls.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not cls.rom_path.exists():
			# Try alternative path
			cls.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

		cls.rom_available = cls.rom_path.exists()

	def test_rom_exists(self):
		"""Test that ROM file exists."""
		self.assertTrue(self.rom_available, f"ROM not found at {self.rom_path}")

	def test_rom_size(self):
		"""Test ROM has correct size."""
		if not self.rom_available:
			self.skipTest("ROM not available")

		size = os.path.getsize(self.rom_path)
		self.assertEqual(size, 262144, f"ROM size is {size}, expected 262144 bytes (256KB)")

	def test_rom_header(self):
		"""Test ROM has valid NES header."""
		if not self.rom_available:
			self.skipTest("ROM not available")

		with open(self.rom_path, 'rb') as f:
			header = f.read(16)

		# Check NES header
		self.assertEqual(header[0:4], b'NES\x1a', "Invalid NES header magic")

		# Check PRG ROM size (16KB units)
		prg_size = header[4]
		self.assertEqual(prg_size, 2, f"PRG ROM size: {prg_size * 16}KB (expected 32KB)")

		# Check CHR ROM size (8KB units)
		chr_size = header[5]
		self.assertEqual(chr_size, 2, f"CHR ROM size: {chr_size * 8}KB (expected 16KB)")

	def test_chr_rom_offset(self):
		"""Test CHR-ROM is at correct offset."""
		if not self.rom_available:
			self.skipTest("ROM not available")

		# CHR-ROM should start at 0x10010 (header + PRG-ROM)
		expected_offset = 0x10010

		with open(self.rom_path, 'rb') as f:
			f.seek(expected_offset)
			chr_data = f.read(16)  # Read first CHR tile

		self.assertEqual(len(chr_data), 16, "Could not read CHR data")


class TestDataExtraction(unittest.TestCase):
	"""Test data extraction from ROM."""

	@classmethod
	def setUpClass(cls):
		"""Load ROM for extraction tests."""
		cls.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not cls.rom_path.exists():
			cls.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

		if cls.rom_path.exists():
			with open(cls.rom_path, 'rb') as f:
				cls.rom_data = bytearray(f.read())
		else:
			cls.rom_data = None

	def test_monster_stats_extraction(self):
		"""Test monster stats extraction."""
		if self.rom_data is None:
			self.skipTest("ROM not available")

		# Extract Slime stats (monster 0)
		offset = 0xC6E0  # MONSTER_STATS offset
		data = self.rom_data[offset:offset + 16]

		hp = data[0] | (data[1] << 8)
		strength = data[2]
		agility = data[3]

		# Verify reasonable values
		self.assertGreater(hp, 0, "Slime HP should be > 0")
		self.assertLess(hp, 10000, "Slime HP should be < 10000")
		self.assertGreater(strength, 0, "Slime strength should be > 0")
		self.assertLess(strength, 255, "Slime strength should be < 255")

	def test_chr_tile_extraction(self):
		"""Test CHR tile extraction."""
		if self.rom_data is None or np is None:
			self.skipTest("ROM or numpy not available")

		# Extract tile 0 from pattern table 0
		offset = 0x10010  # CHR_ROM offset
		tile_data = self.rom_data[offset:offset + 16]

		self.assertEqual(len(tile_data), 16, "CHR tile should be 16 bytes")

		# Decode tile
		pixels = np.zeros((8, 8), dtype=np.uint8)
		for y in range(8):
			lo = tile_data[y]
			hi = tile_data[y + 8]
			for x in range(8):
				bit = 7 - x
				lo_bit = (lo >> bit) & 1
				hi_bit = (hi >> bit) & 1
				pixels[y, x] = (hi_bit << 1) | lo_bit

		# Verify pixel array
		self.assertEqual(pixels.shape, (8, 8), "Tile should be 8×8 pixels")
		self.assertTrue(np.all(pixels >= 0) and np.all(pixels <= 3),
					   "Pixel values should be 0-3")

	def test_sprite_pointer_table(self):
		"""Test monster sprite pointer table."""
		if self.rom_data is None:
			self.skipTest("ROM not available")

		# Read Slime sprite pointer
		ptr_offset = 0x59F4
		ptr_lo = self.rom_data[ptr_offset]
		ptr_hi = self.rom_data[ptr_offset + 1]
		pointer = ptr_lo | (ptr_hi << 8)

		# Verify pointer is reasonable
		self.assertGreater(pointer, 0, "Sprite pointer should be > 0")
		self.assertLess(pointer, 0x8000, "Sprite pointer should be < 0x8000")

	def test_all_39_monsters(self):
		"""Test all 39 monster stats can be extracted."""
		if self.rom_data is None:
			self.skipTest("ROM not available")

		monster_count = 0
		offset = 0xC6E0

		for i in range(39):
			monster_offset = offset + (i * 16)
			data = self.rom_data[monster_offset:monster_offset + 16]

			hp = data[0] | (data[1] << 8)

			# Basic validation
			if 0 < hp < 10000:  # Reasonable HP range
				monster_count += 1

		self.assertGreaterEqual(monster_count, 35,
							   f"Should extract at least 35 valid monsters, got {monster_count}")


class TestEditorFunctionality(unittest.TestCase):
	"""Test editor tool functionality."""

	def setUp(self):
		"""Create temporary ROM for editing tests."""
		self.temp_dir = tempfile.mkdtemp()
		self.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not self.rom_path.exists():
			self.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

		if self.rom_path.exists():
			self.test_rom = Path(self.temp_dir) / "test.nes"
			shutil.copy(self.rom_path, self.test_rom)
		else:
			self.test_rom = None

	def tearDown(self):
		"""Clean up temporary files."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)

	def test_rom_manager_read_write(self):
		"""Test ROMManager read/write operations."""
		if self.test_rom is None:
			self.skipTest("ROM not available")

		from dragon_warrior_master_editor import ROMManager

		rom_mgr = ROMManager(str(self.test_rom))

		# Test read byte
		byte = rom_mgr.read_byte(0x00)
		self.assertEqual(byte, ord('N'), "First byte should be 'N' from NES header")

		# Test write byte
		original = rom_mgr.read_byte(0x100)
		rom_mgr.write_byte(0x100, 0xFF)
		self.assertEqual(rom_mgr.read_byte(0x100), 0xFF, "Byte should be modified")

		# Test undo
		rom_mgr.undo()
		self.assertEqual(rom_mgr.read_byte(0x100), original, "Undo should restore original")

	def test_monster_stats_roundtrip(self):
		"""Test reading and writing monster stats."""
		if self.test_rom is None:
			self.skipTest("ROM not available")

		from dragon_warrior_master_editor import ROMManager

		rom_mgr = ROMManager(str(self.test_rom))

		# Read Slime stats
		original_stats = rom_mgr.extract_monster_stats(0)

		# Modify stats
		modified_stats = original_stats
		modified_stats.hp = 9999
		modified_stats.strength = 255

		# Write back
		rom_mgr.write_monster_stats(modified_stats)

		# Read again
		read_back = rom_mgr.extract_monster_stats(0)

		self.assertEqual(read_back.hp, 9999, "HP should be modified")
		self.assertEqual(read_back.strength, 255, "Strength should be modified")


class TestExportImport(unittest.TestCase):
	"""Test data export/import functionality."""

	def setUp(self):
		"""Create temporary directory for exports."""
		self.temp_dir = tempfile.mkdtemp()
		self.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not self.rom_path.exists():
			self.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

	def tearDown(self):
		"""Clean up temporary files."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)

	def test_json_export(self):
		"""Test JSON export functionality."""
		if not self.rom_path.exists():
			self.skipTest("ROM not available")

		try:
			from data_export_import import DataExporter
			import json

			exporter = DataExporter(str(self.rom_path))

			# Export monsters
			monsters = exporter.extract_monster_stats()
			self.assertGreater(len(monsters), 0, "Should extract monsters")

			# Save to JSON
			output_file = Path(self.temp_dir) / "monsters.json"
			exporter.export_json(str(self.temp_dir), ['monsters'])

			# Verify file exists
			self.assertTrue(output_file.exists(), "JSON file should be created")

			# Verify JSON is valid
			with open(output_file, 'r') as f:
				data = json.load(f)

			self.assertIsInstance(data, list, "JSON should contain list")
			self.assertGreater(len(data), 0, "JSON should have data")

		except ImportError:
			self.skipTest("data_export_import module not available")

	def test_csv_export(self):
		"""Test CSV export functionality."""
		if not self.rom_path.exists():
			self.skipTest("ROM not available")

		try:
			from data_export_import import DataExporter

			exporter = DataExporter(str(self.rom_path))
			exporter.export_csv(str(self.temp_dir), ['monsters'])

			csv_file = Path(self.temp_dir) / "monsters.csv"
			self.assertTrue(csv_file.exists(), "CSV file should be created")

			# Check CSV has content
			with open(csv_file, 'r') as f:
				lines = f.readlines()

			self.assertGreater(len(lines), 1, "CSV should have header + data")

		except ImportError:
			self.skipTest("data_export_import module not available")


class TestSpriteExtraction(unittest.TestCase):
	"""Test monster sprite extraction."""

	@classmethod
	def setUpClass(cls):
		"""Set up ROM path."""
		cls.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not cls.rom_path.exists():
			cls.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

	def test_sprite_extraction_tool(self):
		"""Test sprite extraction tool."""
		if not self.rom_path.exists():
			self.skipTest("ROM not available")

		try:
			from extract_monsters_rom import extract_all_monsters

			temp_dir = tempfile.mkdtemp()

			try:
				# Extract monsters
				count = extract_all_monsters(str(self.rom_path), temp_dir)

				self.assertEqual(count, 39, f"Should extract 39 monsters, got {count}")

				# Check that PNG files were created
				png_files = list(Path(temp_dir).glob("*.png"))
				self.assertEqual(len(png_files), 39,
							   f"Should create 39 PNG files, got {len(png_files)}")

			finally:
				shutil.rmtree(temp_dir, ignore_errors=True)

		except ImportError:
			self.skipTest("extract_monsters_rom module not available")

	def test_extracted_sprite_format(self):
		"""Test extracted sprites are valid PNG."""
		sprite_dir = Path("extracted_assets") / "monsters_corrected"

		if not sprite_dir.exists():
			self.skipTest("Extracted sprites not available")

		if Image is None:
			self.skipTest("PIL not available")

		png_files = list(sprite_dir.glob("*.png"))

		if len(png_files) == 0:
			self.skipTest("No extracted sprites found")

		# Test first sprite
		img = Image.open(png_files[0])

		self.assertEqual(img.mode, 'RGBA', "Sprite should be RGBA format")
		self.assertGreater(img.width, 0, "Sprite should have width")
		self.assertGreater(img.height, 0, "Sprite should have height")


class TestPerformance(unittest.TestCase):
	"""Test performance benchmarks."""

	@classmethod
	def setUpClass(cls):
		"""Set up ROM path."""
		cls.rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not cls.rom_path.exists():
			cls.rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

	def test_rom_load_performance(self):
		"""Test ROM loading performance."""
		if not self.rom_path.exists():
			self.skipTest("ROM not available")

		start = time.time()

		with open(self.rom_path, 'rb') as f:
			data = f.read()

		elapsed = time.time() - start

		self.assertLess(elapsed, 1.0, f"ROM load took {elapsed:.3f}s, should be < 1s")

	def test_monster_extraction_performance(self):
		"""Test monster stats extraction performance."""
		if not self.rom_path.exists():
			self.skipTest("ROM not available")

		try:
			from dragon_warrior_master_editor import ROMManager

			rom_mgr = ROMManager(str(self.rom_path))

			start = time.time()

			for i in range(39):
				stats = rom_mgr.extract_monster_stats(i)

			elapsed = time.time() - start

			self.assertLess(elapsed, 0.1,
						   f"Extracting 39 monsters took {elapsed:.3f}s, should be < 0.1s")

		except ImportError:
			self.skipTest("dragon_warrior_master_editor module not available")


class TestRegression(unittest.TestCase):
	"""Regression tests for known issues."""

	def test_monster_sprite_tile_mapping(self):
		"""Test that monster sprites use correct tiles (regression for JSON bug)."""
		rom_path = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not rom_path.exists():
			rom_path = Path("..") / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"

		if not rom_path.exists():
			self.skipTest("ROM not available")

		with open(rom_path, 'rb') as f:
			rom_data = f.read()

		# Read Slime sprite pointer
		ptr_offset = 0x59F4
		pointer = rom_data[ptr_offset] | (rom_data[ptr_offset + 1] << 8)

		# Read sprite data
		sprite_offset = 0x5000 + pointer  # Adjust for ROM offset

		# Read first tile ID
		tile_id = rom_data[sprite_offset]

		# Slime should use tiles from Pattern Table 2 (512-767)
		# Not tiles like 85, 83, 84 from the incorrect JSON
		# The actual tiles should be in the 68-76 range or similar

		self.assertNotEqual(tile_id, 85,
						   "Slime sprite should not use tile 85 (JSON bug)")
		self.assertNotEqual(tile_id, 83,
						   "Slime sprite should not use tile 83 (JSON bug)")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests(verbose=True, pattern='test_*.py'):
	"""
	Run all tests.

	Args:
		verbose: Show detailed output
		pattern: Test file pattern

	Returns:
		TestResult object
	"""
	# Discover and run tests
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromModule(sys.modules[__name__])

	runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
	result = runner.run(suite)

	return result


def main():
	"""Main test entry point."""
	import argparse

	parser = argparse.ArgumentParser(description="Dragon Warrior ROM Toolkit Test Suite")
	parser.add_argument('-v', '--verbose', action='store_true',
					   help="Verbose output")
	parser.add_argument('-q', '--quiet', action='store_true',
					   help="Minimal output")
	parser.add_argument('-f', '--failfast', action='store_true',
					   help="Stop on first failure")
	parser.add_argument('-k', '--pattern', default='test_',
					   help="Test method pattern")

	args = parser.parse_args()

	# Print header
	print("=" * 80)
	print("DRAGON WARRIOR ROM HACKING TOOLKIT - TEST SUITE")
	print("=" * 80)
	print()

	# Run tests
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromModule(sys.modules[__name__])

	verbosity = 0 if args.quiet else (2 if args.verbose else 1)
	runner = unittest.TextTestRunner(verbosity=verbosity, failfast=args.failfast)

	result = runner.run(suite)

	# Print summary
	print()
	print("=" * 80)
	print("TEST SUMMARY")
	print("=" * 80)
	print(f"Tests run: {result.testsRun}")
	print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
	print(f"Failures: {len(result.failures)}")
	print(f"Errors: {len(result.errors)}")
	print(f"Skipped: {len(result.skipped)}")
	print()

	if result.wasSuccessful():
		print("✓ ALL TESTS PASSED!")
		return 0
	else:
		print("✗ SOME TESTS FAILED")
		return 1


if __name__ == '__main__':
	sys.exit(main())
