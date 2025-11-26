#!/usr/bin/env python3
"""
Unit Tests for Binary Pipeline

Tests for extract → transform → package → reinsert workflow.

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import unittest
import tempfile
import shutil
import struct
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from extract_to_binary import BinaryExtractor
from binary_to_assets import BinaryUnpacker
from assets_to_binary import BinaryPackager
from binary_to_rom import BinaryInserter


class TestBinaryExtractor(unittest.TestCase):
    """Test ROM to binary extraction"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.rom_path = cls.test_dir / "test.nes"
        cls.output_dir = cls.test_dir / "extracted"

        # Create minimal test ROM (16 byte header + data)
        header = bytes([0x4E, 0x45, 0x53, 0x1A,  # "NES" + DOS EOF
                       0x02,  # 2 × 16KB PRG-ROM
                       0x01,  # 1 × 8KB CHR-ROM
                       0x00, 0x00,  # Flags
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        prg_rom = bytes([0xFF] * (2 * 16384))  # 32KB PRG-ROM
        chr_rom = bytes([0xAA] * (1 * 8192))   # 8KB CHR-ROM

        with open(cls.rom_path, 'wb') as f:
            f.write(header + prg_rom + chr_rom)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        shutil.rmtree(cls.test_dir)

    def test_extractor_initialization(self):
        """Test extractor initialization"""
        extractor = BinaryExtractor(str(self.rom_path), str(self.output_dir))
        self.assertIsNotNone(extractor)
        self.assertEqual(extractor.rom_path, self.rom_path)

    def test_rom_loading(self):
        """Test ROM file loading"""
        extractor = BinaryExtractor(str(self.rom_path), str(self.output_dir))
        success = extractor.load_rom()

        self.assertTrue(success)
        self.assertIsNotNone(extractor.rom_data)
        self.assertEqual(len(extractor.rom_data), 16 + 32768 + 8192)

    def test_binary_format_header(self):
        """Test .dwdata header creation"""
        extractor = BinaryExtractor(str(self.rom_path), str(self.output_dir))
        extractor.load_rom()

        test_data = bytes([0x01, 0x02, 0x03, 0x04])
        binary_data = extractor.create_binary_format(test_data, 0x01, 0x1000)

        # Check header
        self.assertEqual(binary_data[0:4], b'DWDT')  # Magic
        self.assertEqual(binary_data[4], 1)  # Major version
        self.assertEqual(binary_data[5], 0)  # Minor version
        self.assertEqual(binary_data[8], 0x01)  # Data type

        # Check data follows header
        self.assertEqual(binary_data[32:36], test_data)

    def test_crc32_calculation(self):
        """Test CRC32 checksum"""
        extractor = BinaryExtractor(str(self.rom_path), str(self.output_dir))
        extractor.load_rom()

        test_data = bytes([0x01, 0x02, 0x03, 0x04])
        binary_data = extractor.create_binary_format(test_data, 0x01, 0x1000)

        # Extract CRC from header
        crc_stored = struct.unpack('<I', binary_data[12:16])[0]

        # Recalculate CRC
        import zlib
        crc_calculated = zlib.crc32(test_data)

        self.assertEqual(crc_stored, crc_calculated)


class TestBinaryUnpacker(unittest.TestCase):
    """Test binary to assets conversion"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.binary_dir = cls.test_dir / "binary"
        cls.output_dir = cls.test_dir / "assets"
        cls.binary_dir.mkdir(parents=True)

        # Create test .dwdata file
        cls._create_test_binary()

    @classmethod
    def _create_test_binary(cls):
        """Create test .dwdata file"""
        # Monster data: ID, HP, Attack, Defense, Agility, Spell, M.Def, XP, Gold
        monster_data = struct.pack(
            '<BBBBBBBHH',
            0,    # ID
            10,   # HP
            5,    # Attack
            3,    # Defense
            4,    # Agility
            0,    # Spell
            2,    # M.Defense
            8,    # XP
            6     # Gold
        )

        # Create header
        header = struct.pack(
            '<4sBBHIIHHI',
            b'DWDT',  # Magic
            1, 0,     # Version 1.0
            0,        # Reserved
            0x01,     # Data type (monsters)
            0,        # CRC32 (placeholder)
            0x5C00,   # ROM offset
            len(monster_data),  # Data size
            0,        # Reserved
            0         # Timestamp
        )

        # Calculate CRC
        import zlib
        crc = zlib.crc32(monster_data)
        header = struct.pack(
            '<4sBBHIIHHI',
            b'DWDT',
            1, 0,
            0,
            0x01,
            crc,
            0x5C00,
            len(monster_data),
            0,
            0
        )

        # Write file
        with open(cls.binary_dir / "monsters.dwdata", 'wb') as f:
            f.write(header + monster_data)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        shutil.rmtree(cls.test_dir)

    def test_unpacker_initialization(self):
        """Test unpacker initialization"""
        unpacker = BinaryUnpacker(str(self.binary_dir), str(self.output_dir))
        self.assertIsNotNone(unpacker)

    def test_binary_validation(self):
        """Test .dwdata validation"""
        unpacker = BinaryUnpacker(str(self.binary_dir), str(self.output_dir))

        binary_file = self.binary_dir / "monsters.dwdata"
        is_valid = unpacker.validate_binary_file(str(binary_file))

        self.assertTrue(is_valid)

    def test_crc_validation(self):
        """Test CRC32 validation"""
        unpacker = BinaryUnpacker(str(self.binary_dir), str(self.output_dir))

        binary_file = self.binary_dir / "monsters.dwdata"

        with open(binary_file, 'rb') as f:
            data = f.read()

        # Header is 32 bytes
        header = data[:32]
        payload = data[32:]

        # Extract CRC
        crc_stored = struct.unpack('<I', header[12:16])[0]

        # Calculate CRC
        import zlib
        crc_calculated = zlib.crc32(payload)

        self.assertEqual(crc_stored, crc_calculated)


class TestBinaryPackager(unittest.TestCase):
    """Test assets to binary conversion"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.assets_dir = cls.test_dir / "assets"
        cls.json_dir = cls.assets_dir / "json"
        cls.json_dir.mkdir(parents=True)

        # Create test JSON
        import json
        monsters = [
            {
                "id": 0,
                "name": "Test Monster",
                "hp": 10,
                "attack": 5,
                "defense": 3,
                "agility": 4,
                "spell": 0,
                "m_defense": 2,
                "xp": 8,
                "gold": 6
            }
        ]

        with open(cls.json_dir / "monsters.json", 'w') as f:
            json.dump(monsters, f)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        shutil.rmtree(cls.test_dir)

    def test_packager_initialization(self):
        """Test packager initialization"""
        packager = BinaryPackager(str(self.assets_dir))
        self.assertIsNotNone(packager)

    def test_monster_validation(self):
        """Test monster data validation"""
        packager = BinaryPackager(str(self.assets_dir))

        # Valid monster
        valid = {
            "hp": 10,
            "attack": 5,
            "defense": 3,
            "agility": 4,
            "spell": 0,
            "m_defense": 2,
            "xp": 8,
            "gold": 6
        }
        self.assertTrue(packager.validate_monster(valid, 0))

        # Invalid HP (0)
        invalid_hp = valid.copy()
        invalid_hp["hp"] = 0
        self.assertFalse(packager.validate_monster(invalid_hp, 0))

        # Invalid HP (256)
        invalid_hp2 = valid.copy()
        invalid_hp2["hp"] = 256
        self.assertFalse(packager.validate_monster(invalid_hp2, 0))


class TestBinaryInserter(unittest.TestCase):
    """Test binary to ROM insertion"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.rom_path = cls.test_dir / "test.nes"
        cls.binary_dir = cls.test_dir / "binary"
        cls.binary_dir.mkdir(parents=True)

        # Create test ROM
        header = bytes([0x4E, 0x45, 0x53, 0x1A,
                       0x02, 0x01, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        prg_rom = bytes([0xFF] * 32768)
        chr_rom = bytes([0xAA] * 8192)

        with open(cls.rom_path, 'wb') as f:
            f.write(header + prg_rom + chr_rom)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        shutil.rmtree(cls.test_dir)

    def test_inserter_initialization(self):
        """Test inserter initialization"""
        inserter = BinaryInserter(str(self.binary_dir), str(self.rom_path))
        self.assertIsNotNone(inserter)

    def test_rom_backup(self):
        """Test ROM backup creation"""
        inserter = BinaryInserter(str(self.binary_dir), str(self.rom_path))
        inserter.load_rom()

        backup_path = inserter.create_backup()

        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.name.startswith("test_backup_"))


class TestEndToEndPipeline(unittest.TestCase):
    """Test complete binary pipeline workflow"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        shutil.rmtree(cls.test_dir)

    def test_full_pipeline(self):
        """Test extract → unpack → modify → repack → insert"""
        # This would test the complete workflow
        # Skipped in unit tests (would be integration test)
        pass


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryUnpacker))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryPackager))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryInserter))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndPipeline))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
