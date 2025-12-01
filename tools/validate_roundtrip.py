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

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.binary_dir = project_root / 'assets' / 'binary'
        self.json_dir = project_root / 'assets' / 'json'
        self.dwdata_dir = project_root / 'extracted_assets' / 'binary'

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
        """Convert monsters JSON back to binary format."""
        monsters = json_data.get('monsters', [])
        result = bytearray()

        for monster in monsters:
            # Each monster is 16 bytes
            record = bytearray(16)

            # Pack monster data (format from original extraction)
            record[0] = monster.get('strength', 0) & 0xFF
            record[1] = monster.get('agility', 0) & 0xFF
            record[2] = monster.get('hp', 0) & 0xFF
            record[3] = monster.get('hurt_resist', 0) & 0xFF
            record[4] = monster.get('sleep_resist', 0) & 0xFF
            record[5] = monster.get('stopspell_resist', 0) & 0xFF
            record[6] = monster.get('attack_pattern', 0) & 0xFF
            record[7] = monster.get('sprite', 0) & 0xFF
            record[8] = monster.get('color', 0) & 0xFF
            record[9] = monster.get('run_factor', 0) & 0xFF

            # Experience (2 bytes, little-endian)
            exp = monster.get('experience', 0)
            record[10] = exp & 0xFF
            record[11] = (exp >> 8) & 0xFF

            # Gold (2 bytes, little-endian)
            gold = monster.get('gold', 0)
            record[12] = gold & 0xFF
            record[13] = (gold >> 8) & 0xFF

            # Reserved bytes
            record[14] = 0
            record[15] = 0

            result.extend(record)

        return bytes(result)

    def spell_json_to_binary(self, json_data: Dict) -> bytes:
        """Convert spells JSON back to binary format."""
        spells = json_data.get('spells', json_data.get('player_spells', []))
        result = bytearray()

        for spell in spells:
            # Each spell is 8 bytes
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
        """Convert items JSON back to binary format."""
        items = json_data.get('items', [])
        result = bytearray()

        for item in items:
            # Each item is 8 bytes
            record = bytearray(8)

            record[0] = item.get('type', 0) & 0xFF
            record[1] = item.get('flags', 0) & 0xFF

            price = item.get('price', 0)
            record[2] = price & 0xFF
            record[3] = (price >> 8) & 0xFF

            record[4] = item.get('effect', 0) & 0xFF
            record[5] = item.get('parameter', 0) & 0xFF
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
                    print(f"    Offset 0x{i:04X}: 0x{original[i]:02X} → 0x{rebuilt[i]:02X}")

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
        validations = [
            ('monsters', 'monsters.dwdata', 'monsters.json', self.monster_json_to_binary),
            ('spells', 'spells.dwdata', 'spells.json', self.spell_json_to_binary),
            ('items', 'items.dwdata', 'items.json', self.item_json_to_binary),
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

    validator = BinaryValidator(project_root)

    if args.asset:
        # Single asset validation
        validations = {
            'monsters': ('monsters.dwdata', 'monsters.json', validator.monster_json_to_binary),
            'spells': ('spells.dwdata', 'spells.json', validator.spell_json_to_binary),
            'items': ('items.dwdata', 'items.json', validator.item_json_to_binary),
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
