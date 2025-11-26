#!/usr/bin/env python3
"""
Reinsert Binary Data to ROM

This script reinserts .dwdata binary files into a Dragon Warrior ROM.

Pipeline: ROM → .dwdata → JSON/PNG → .dwdata → ROM (this script)

Usage:
    python binary_to_rom.py
    python binary_to_rom.py --rom output_rom.nes
    python binary_to_rom.py --binary-dir custom/binary/

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import struct
import zlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from datetime import datetime

# Constants
MAGIC = b'DWDT'

# Data type IDs
TYPE_MONSTER = 0x01
TYPE_SPELL = 0x02
TYPE_ITEM = 0x03
TYPE_MAP = 0x04
TYPE_TEXT = 0x05
TYPE_GRAPHICS = 0x06

TYPE_NAMES = {
    TYPE_MONSTER: "Monster",
    TYPE_SPELL: "Spell",
    TYPE_ITEM: "Item",
    TYPE_MAP: "Map",
    TYPE_TEXT: "Text",
    TYPE_GRAPHICS: "Graphics"
}

# Default paths
DEFAULT_ROM = "roms/Dragon Warrior (U) (PRG1) [!].nes"
DEFAULT_BINARY_DIR = "extracted_assets/binary"
DEFAULT_OUTPUT_ROM = "build/dragon_warrior_modified.nes"


class BinaryReader:
    """Read and validate .dwdata binary files"""

    def __init__(self, path: str):
        """
        Initialize reader

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
            True if valid
        """
        if not os.path.exists(self.path):
            print(f"  ❌ File not found: {self.path}")
            return False

        with open(self.path, 'rb') as f:
            self.data = f.read()

        # Validate
        if len(self.data) < 32:
            print(f"  ❌ File too small")
            return False

        if self.data[0:4] != MAGIC:
            print(f"  ❌ Invalid magic")
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
            print(f"     File may be corrupted!")
            return False

        return True

    def get_data_section(self) -> bytes:
        """Get data section"""
        return self.data[32:32 + self.header['data_size']]

    def get_type_name(self) -> str:
        """Get human-readable type name"""
        return TYPE_NAMES.get(self.header['data_type'], "Unknown")


class ROMModifier:
    """Reinsert binary data into ROM"""

    def __init__(self, rom_path: str, binary_dir: str):
        """
        Initialize modifier

        Args:
            rom_path: Path to ROM file
            binary_dir: Directory with .dwdata files
        """
        self.rom_path = rom_path
        self.binary_dir = binary_dir
        self.rom_data = None
        self.modifications = []

    def load_rom(self) -> bool:
        """
        Load ROM file

        Returns:
            True if loaded successfully
        """
        if not os.path.exists(self.rom_path):
            print(f"❌ ROM file not found: {self.rom_path}")
            return False

        with open(self.rom_path, 'rb') as f:
            self.rom_data = bytearray(f.read())

        # Validate ROM
        if len(self.rom_data) != 81936:
            print(f"❌ Invalid ROM size: {len(self.rom_data)}")
            return False

        if self.rom_data[0:4] != b'NES\x1A':
            print(f"❌ Invalid NES header")
            return False

        print(f"✓ Loaded ROM: {self.rom_path}")
        print(f"  Size: {len(self.rom_data)} bytes")

        return True

    def create_backup(self, backup_path: str) -> bool:
        """
        Create ROM backup

        Args:
            backup_path: Path for backup file

        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy(self.rom_path, backup_path)
            print(f"✓ Created backup: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False

    def reinsert_binary(self, dwdata_path: str) -> Tuple[bool, Dict]:
        """
        Reinsert one .dwdata file into ROM

        Args:
            dwdata_path: Path to .dwdata file

        Returns:
            Tuple of (success, info_dict)
        """
        # Load and validate binary
        reader = BinaryReader(dwdata_path)
        if not reader.load():
            return False, {}

        data = reader.get_data_section()
        rom_offset = reader.header['rom_offset']
        data_size = reader.header['data_size']
        data_type = reader.get_type_name()

        print(f"\n--- Reinserting {data_type} Data ---")
        print(f"  Source: {os.path.basename(dwdata_path)}")
        print(f"  ROM Offset: 0x{rom_offset:04X}")
        print(f"  Data Size: {data_size} bytes")
        print(f"  CRC32: {reader.header['crc32']:08X}")

        # Verify offset is valid
        if rom_offset + data_size > len(self.rom_data):
            print(f"  ❌ Offset out of bounds!")
            print(f"     ROM size: {len(self.rom_data)}")
            print(f"     Required: {rom_offset + data_size}")
            return False, {}

        # Store original data for comparison
        original_data = bytes(self.rom_data[rom_offset:rom_offset + data_size])

        # Count changes
        changes = sum(1 for i in range(data_size) if original_data[i] != data[i])
        change_percent = (changes / data_size) * 100 if data_size > 0 else 0

        # Reinsert data
        self.rom_data[rom_offset:rom_offset + data_size] = data

        # Build modification record
        mod_info = {
            'type': data_type,
            'offset': rom_offset,
            'size': data_size,
            'changes': changes,
            'percent': change_percent,
            'crc32': reader.header['crc32']
        }

        self.modifications.append(mod_info)

        print(f"  ✓ Reinserted {data_size} bytes")
        print(f"  ✓ Changed: {changes} bytes ({change_percent:.1f}%)")

        return True, mod_info

    def reinsert_all(self) -> Dict[str, Tuple[bool, Dict]]:
        """
        Reinsert all .dwdata files

        Returns:
            Dict mapping filenames to (success, info) tuples
        """
        files = [
            'monsters.dwdata',
            'spells.dwdata',
            'items.dwdata',
            'graphics.dwdata'
        ]

        results = {}

        for filename in files:
            path = os.path.join(self.binary_dir, filename)

            if os.path.exists(path):
                success, info = self.reinsert_binary(path)
                results[filename] = (success, info)
            else:
                print(f"\n⚠ Skipping {filename} (not found)")
                results[filename] = (False, {})

        return results

    def save_rom(self, output_path: str) -> bool:
        """
        Save modified ROM

        Args:
            output_path: Path for output ROM

        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(self.rom_data)

            print(f"\n✓ Saved modified ROM: {output_path}")
            print(f"  Size: {len(self.rom_data)} bytes")

            return True
        except Exception as e:
            print(f"\n❌ Failed to save ROM: {e}")
            return False

    def generate_report(self, output_path: str) -> bool:
        """
        Generate modification report

        Args:
            output_path: Path for report file

        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("Dragon Warrior ROM Modification Report\n")
                f.write("=" * 70 + "\n\n")

                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source ROM: {self.rom_path}\n")
                f.write(f"Binary Directory: {self.binary_dir}\n\n")

                f.write("-" * 70 + "\n")
                f.write("Modifications\n")
                f.write("-" * 70 + "\n\n")

                total_changes = 0

                for mod in self.modifications:
                    f.write(f"Type: {mod['type']}\n")
                    f.write(f"  ROM Offset: 0x{mod['offset']:04X}\n")
                    f.write(f"  Data Size: {mod['size']} bytes\n")
                    f.write(f"  Changes: {mod['changes']} bytes ({mod['percent']:.1f}%)\n")
                    f.write(f"  CRC32: {mod['crc32']:08X}\n")
                    f.write("\n")

                    total_changes += mod['changes']

                f.write("-" * 70 + "\n")
                f.write("Summary\n")
                f.write("-" * 70 + "\n\n")

                f.write(f"Total Modifications: {len(self.modifications)}\n")
                f.write(f"Total Bytes Changed: {total_changes}\n")
                f.write(f"ROM Size: {len(self.rom_data)} bytes\n")

                change_percent = (total_changes / len(self.rom_data)) * 100
                f.write(f"Overall Change: {change_percent:.2f}%\n")

                f.write("\n" + "=" * 70 + "\n")

            print(f"✓ Generated report: {output_path}")

            return True
        except Exception as e:
            print(f"❌ Failed to generate report: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Reinsert .dwdata binary files into Dragon Warrior ROM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python binary_to_rom.py
  python binary_to_rom.py --rom custom_rom.nes
  python binary_to_rom.py --output modified_rom.nes
  python binary_to_rom.py --no-backup
        """
    )

    parser.add_argument(
        '--rom',
        default=DEFAULT_ROM,
        help=f'Source ROM file (default: {DEFAULT_ROM})'
    )

    parser.add_argument(
        '--binary-dir',
        default=DEFAULT_BINARY_DIR,
        help=f'.dwdata files directory (default: {DEFAULT_BINARY_DIR})'
    )

    parser.add_argument(
        '--output',
        default=DEFAULT_OUTPUT_ROM,
        help=f'Output ROM file (default: {DEFAULT_OUTPUT_ROM})'
    )

    parser.add_argument(
        '--backup',
        default=None,
        help='Backup path (default: {rom}.backup)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )

    parser.add_argument(
        '--report',
        default='build/reports/modification_report.txt',
        help='Modification report path'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Binary → ROM Reinsertion")
    print("=" * 70)

    # Initialize modifier
    modifier = ROMModifier(args.rom, args.binary_dir)

    if not modifier.load_rom():
        return 1

    # Create backup
    if not args.no_backup:
        backup_path = args.backup or (args.rom + '.backup')
        if not modifier.create_backup(backup_path):
            print("\n⚠ Continuing without backup...")

    # Reinsert all binary files
    results = modifier.reinsert_all()

    # Count successes
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)

    # Summary
    print("\n" + "=" * 70)
    print("Reinsertion Summary")
    print("=" * 70)

    for filename, (success, info) in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")
        if success and info:
            print(f"      {info['changes']} bytes changed ({info['percent']:.1f}%)")

    print(f"\nCompleted: {success_count}/{total_count} files")

    if success_count == 0:
        print("\n❌ No files reinserted!")
        return 1

    # Save modified ROM
    if not modifier.save_rom(args.output):
        return 1

    # Generate report
    modifier.generate_report(args.report)

    # Final summary
    total_changes = sum(info.get('changes', 0) for _, info in results.values() if info)

    print("\n" + "=" * 70)
    print("✅ Reinsertion Complete!")
    print("=" * 70)
    print(f"Modified ROM: {args.output}")
    print(f"Total Changes: {total_changes} bytes")
    print(f"\nNext step: Test ROM in emulator!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
