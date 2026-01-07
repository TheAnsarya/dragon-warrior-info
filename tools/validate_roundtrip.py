#!/usr/bin/env python3
"""
Dragon Warrior Binary Roundtrip Validator

Validates that JSON assets can be correctly converted back to binary format
that matches the original ROM extraction.

This ensures data integrity through the complete pipeline:
    ROM → binary → JSON → (edit) → JSON → binary (must match original if unedited)

Usage:
    python validate_roundtrip.py                    # Validate all assets
    python validate_roundtrip.py --asset monsters   # Validate single asset
    python validate_roundtrip.py --verbose          # Show detailed diffs

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import json
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a single asset validation."""
    asset_name: str
    passed: bool
    original_size: int
    rebuilt_size: int
    diff_count: int
    diff_positions: List[int]
    message: str


class BinaryValidator:
    """Validates binary roundtrip integrity."""

    def __init__(self, project_root: Path, use_roundtrip: bool = False):
        self.project_root = project_root
        self.binary_dir = project_root / 'assets' / 'binary'
        self.dwdata_dir = project_root / 'extracted_assets' / 'binary'

        # Use roundtrip JSON files if specified (produced by binary_to_json.py)
        if use_roundtrip:
            self.json_dir = project_root / 'assets' / 'json' / 'roundtrip'
        else:
            self.json_dir = project_root / 'assets' / 'json'

    def load_dwdata(self, filename: str) -> Optional[bytes]:
        """Load data section from .dwdata file."""
        path = self.dwdata_dir / filename
        if not path.exists():
            return None

        with open(path, 'rb') as f:
            data = f.read()

        # Skip 32-byte header
        if len(data) < 32:
            return None

        # Get data size from header
        data_size = struct.unpack_from('<I', data, 0x08)[0]
        return data[32:32 + data_size]

    def load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON asset file."""
        path = self.json_dir / filename
        if not path.exists():
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def monster_json_to_binary(self, json_data: Dict) -> bytes:
        """Convert monsters JSON back to binary format.

        The ROM format is 16 bytes per monster:
        Bytes 0-7 (used stats):
            0: Strength (attack power)
            1: Defense
            2: HP
            3: Spell pattern
            4: Agility
            5: Resistance (magic defense)
            6: Experience
            7: Gold
        Bytes 8-15 (unused but preserved):
            Stored in _raw_bytes_8_15 for exact roundtrip
        """
        result = bytearray()

        # Handle dict format with string keys ("0", "1", etc.)
        if isinstance(json_data, dict) and not json_data.get('monsters'):
            # Convert dict to sorted list by ID
            monsters = []
            for key in sorted(json_data.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                if key.isdigit():
                    monsters.append(json_data[key])
        else:
            monsters = json_data.get('monsters', [])

        for monster in monsters:
            # Each monster is 16 bytes
            record = bytearray(16)

            # Pack monster data matching ROM format (8 used bytes)
            record[0] = monster.get('strength', 0) & 0xFF
            record[1] = monster.get('defense', 0) & 0xFF
            record[2] = monster.get('hp', 0) & 0xFF
            record[3] = monster.get('spell_pattern', 0) & 0xFF
            record[4] = monster.get('agility', 0) & 0xFF
            record[5] = monster.get('resistance', 0) & 0xFF
            record[6] = monster.get('experience', 0) & 0xFF
            record[7] = monster.get('gold', 0) & 0xFF

            # Restore raw bytes 8-15 for exact roundtrip
            raw_bytes = monster.get('_raw_bytes_8_15', [0] * 8)
            for i, byte in enumerate(raw_bytes[:8]):
                record[8 + i] = byte & 0xFF

            result.extend(record)

        return bytes(result)

        return bytes(result)

    def spell_json_to_binary(self, json_data: Dict) -> bytes:
        """Convert spells JSON back to binary format.

        Uses raw bytes for exact roundtrip since spell offsets may need verification.
        Each spell is 8 bytes.
        """
        result = bytearray()

        # Handle dict format with string keys ("0", "1", etc.)
        if isinstance(json_data, dict) and not json_data.get('spells'):
            spells = []
            for key in sorted(json_data.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                if key.isdigit():
                    spells.append(json_data[key])
        else:
            spells = json_data.get('spells', json_data.get('player_spells', []))

        for spell in spells:
            # Check for raw bytes first (roundtrip format)
            raw_bytes = spell.get('_raw_bytes', None)
            if raw_bytes:
                record = bytearray(8)
                for i, byte in enumerate(raw_bytes[:8]):
                    record[i] = byte & 0xFF
            else:
                # Legacy format fallback
                record = bytearray(8)
                record[0] = spell.get('mp_cost', 0) & 0xFF
                record[1] = spell.get('power', 0) & 0xFF
                record[2] = spell.get('type', 0) & 0xFF
                record[3] = spell.get('level_learned', 0) & 0xFF
                record[4] = spell.get('target', 0) & 0xFF
                record[5] = spell.get('flags', 0) & 0xFF
                record[6] = 0
                record[7] = 0

            result.extend(record)

        return bytes(result)

    def item_json_to_binary(self, json_data: Dict) -> bytes:
        """Convert items JSON back to binary format.

        Uses raw bytes for exact roundtrip since item offsets may need verification.
        Each item is 8 bytes.
        """
        result = bytearray()

        # Handle dict format with string keys ("0", "1", etc.)
        if isinstance(json_data, dict) and not json_data.get('items'):
            items = []
            for key in sorted(json_data.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                if key.isdigit():
                    items.append(json_data[key])
        else:
            items = json_data.get('items', [])

        for item in items:
            # Check for raw bytes first (roundtrip format)
            raw_bytes = item.get('_raw_bytes', None)
            if raw_bytes:
                record = bytearray(8)
                for i, byte in enumerate(raw_bytes[:8]):
                    record[i] = byte & 0xFF
            else:
                # Legacy format fallback
                record = bytearray(8)
                item_type_map = {'weapon': 0, 'armor': 1, 'shield': 2, 'accessory': 3, 'consumable': 4, 'key': 5}
                item_type = item.get('type', item.get('item_type', 'consumable'))
                if isinstance(item_type, str):
                    item_type = item_type_map.get(item_type.lower(), 0)

                record[0] = item_type & 0xFF
                record[1] = item.get('flags', 0) & 0xFF

                price = item.get('price', item.get('buy_price', 0))
                record[2] = price & 0xFF
                record[3] = (price >> 8) & 0xFF

                record[4] = item.get('attack_power', item.get('effect', 0)) & 0xFF
                record[5] = item.get('defense_power', item.get('parameter', 0)) & 0xFF
                record[6] = 0
                record[7] = 0

            result.extend(record)

        return bytes(result)

    def compare_binary(
        self,
        original: bytes,
        rebuilt: bytes,
        verbose: bool = False
    ) -> Tuple[int, List[int]]:
        """Compare two binary blobs and return differences."""
        diff_positions = []

        min_len = min(len(original), len(rebuilt))
        max_len = max(len(original), len(rebuilt))

        for i in range(min_len):
            if original[i] != rebuilt[i]:
                diff_positions.append(i)
                if verbose:
                    print(f"    Offset 0x{i:04X}: 0x{original[i]:02X} -> 0x{rebuilt[i]:02X}")

        # Size difference counts as differences
        if len(original) != len(rebuilt):
            if verbose:
                print(f"    Size difference: {len(original)} vs {len(rebuilt)}")

        return len(diff_positions), diff_positions

    def validate_asset(
        self,
        asset_name: str,
        dwdata_file: str,
        json_file: str,
        converter_func,
        verbose: bool = False
    ) -> ValidationResult:
        """Validate a single asset's roundtrip integrity."""
        print(f"\n--- Validating {asset_name} ---")

        # Load original binary
        original = self.load_dwdata(dwdata_file)
        if original is None:
            return ValidationResult(
                asset_name=asset_name,
                passed=False,
                original_size=0,
                rebuilt_size=0,
                diff_count=0,
                diff_positions=[],
                message=f"Original binary not found: {dwdata_file}"
            )

        # Load JSON
        json_data = self.load_json(json_file)
        if json_data is None:
            return ValidationResult(
                asset_name=asset_name,
                passed=False,
                original_size=len(original),
                rebuilt_size=0,
                diff_count=0,
                diff_positions=[],
                message=f"JSON file not found: {json_file}"
            )

        # Convert JSON back to binary
        try:
            rebuilt = converter_func(json_data)
        except Exception as e:
            return ValidationResult(
                asset_name=asset_name,
                passed=False,
                original_size=len(original),
                rebuilt_size=0,
                diff_count=0,
                diff_positions=[],
                message=f"Conversion error: {e}"
            )

        # Compare
        diff_count, diff_positions = self.compare_binary(original, rebuilt, verbose)

        passed = (diff_count == 0) and (len(original) == len(rebuilt))
        message = "PASS" if passed else f"{diff_count} differences found"

        if passed:
            print(f"  ✓ PASS: {len(original)} bytes match exactly")
        else:
            print(f"  ✗ FAIL: {diff_count} byte differences")
            print(f"         Original: {len(original)} bytes")
            print(f"         Rebuilt:  {len(rebuilt)} bytes")

        return ValidationResult(
            asset_name=asset_name,
            passed=passed,
            original_size=len(original),
            rebuilt_size=len(rebuilt),
            diff_count=diff_count,
            diff_positions=diff_positions[:20],  # Limit stored positions
            message=message
        )

    def validate_all(self, verbose: bool = False) -> List[ValidationResult]:
        """Validate all assets."""
        results = []

        # Define validation targets
        # Use roundtrip JSON files for proper validation
        validations = [
            ('monsters', 'monsters.dwdata', 'monsters_roundtrip.json', self.monster_json_to_binary),
            ('spells', 'spells.dwdata', 'spells_roundtrip.json', self.spell_json_to_binary),
            ('items', 'items.dwdata', 'items_roundtrip.json', self.item_json_to_binary),
        ]

        for name, dwdata, json_file, converter in validations:
            result = self.validate_asset(name, dwdata, json_file, converter, verbose)
            results.append(result)

        return results


def write_validation_report(results: List[ValidationResult], output_path: Path):
    """Write validation report to file."""
    with open(output_path, 'w') as f:
        f.write("Dragon Warrior Binary Roundtrip Validation Report\n")
        f.write("=" * 60 + "\n\n")

        passed = sum(1 for r in results if r.passed)
        total = len(results)

        f.write(f"Summary: {passed}/{total} assets validated successfully\n\n")

        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            f.write(f"{status}: {result.asset_name}\n")
            f.write(f"  Original: {result.original_size} bytes\n")
            f.write(f"  Rebuilt:  {result.rebuilt_size} bytes\n")
            f.write(f"  Status:   {result.message}\n")
            if result.diff_positions:
                positions = ', '.join(f'0x{p:04X}' for p in result.diff_positions[:10])
                f.write(f"  Diff at:  {positions}...\n")
            f.write("\n")

    print(f"\nReport written: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Dragon Warrior binary roundtrip integrity'
    )
    parser.add_argument(
        '--asset', '-a',
        type=str,
        help='Validate only specified asset'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed differences'
    )
    parser.add_argument(
        '--roundtrip', '-R',
        action='store_true',
        help='Use roundtrip JSON files from assets/json/roundtrip/'
    )
    parser.add_argument(
        '--report', '-r',
        type=Path,
        help='Write validation report to file'
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print("=" * 60)
    print("Dragon Warrior Binary Roundtrip Validator")
    print("=" * 60)

    validator = BinaryValidator(project_root, use_roundtrip=args.roundtrip)

    if args.asset:
        # Single asset validation
        # Define validation targets
        # Use roundtrip JSON files for proper validation
        validations = {
            'monsters': ('monsters.dwdata', 'monsters_roundtrip.json', validator.monster_json_to_binary),
            'spells': ('spells.dwdata', 'spells_roundtrip.json', validator.spell_json_to_binary),
            'items': ('items.dwdata', 'items_roundtrip.json', validator.item_json_to_binary),
        }

        if args.asset not in validations:
            print(f"Unknown asset: {args.asset}")
            print(f"Available: {', '.join(validations.keys())}")
            return 1

        dwdata, json_file, converter = validations[args.asset]
        results = [validator.validate_asset(args.asset, dwdata, json_file, converter, args.verbose)]
    else:
        # Validate all
        results = validator.validate_all(args.verbose)

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for result in results:
        status = "✓" if result.passed else "✗"
        print(f"  {status} {result.asset_name}: {result.message}")

    print(f"\nResult: {passed}/{total} assets validated")

    # Write report if requested
    if args.report:
        write_validation_report(results, args.report)

    if passed == total:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n❌ Some validations failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
